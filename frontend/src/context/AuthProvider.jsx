import { useEffect, useMemo, useState } from "react";
import { AuthContext } from "./authContext";
import * as authService from "../services/authService";

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    authService
      .getSession()
      .then((account) => active && setUser(account))
      .catch(() => {})
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      async register(data) {
        const account = await authService.register(data);
        setUser(account);
        return account;
      },
      async login(data) {
        const account = await authService.login(data);
        setUser(account);
        return account;
      },
      async logout() {
        await authService.logout();
        setUser(null);
      },
      async updateAccount(changes) {
        const account = await authService.updateAccount(changes);
        setUser(account);
        return account;
      },
    }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
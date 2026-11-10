import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

function Loading() {
  return (
    <div className="center-screen" role="status">
      Loading…
    </div>
  );
}

// Protected pages: logged-out users are sent to /login and returned afterwards.
export function RequireAuth() {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <Loading />;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return <Outlet />;
}

// Sign up / Sign in: signed-in students go straight to the dashboard.
export function PublicOnly() {
  const { user, loading } = useAuth();
  if (loading) return <Loading />;
  if (user) return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}
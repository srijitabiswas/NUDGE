import { useEffect, useRef, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { APP_ROUTES } from "../routeConfig";
import Logo from "../components/Logo";
import Icon from "../components/Icon";
import Footer from "../components/Footer";
import { useAuth } from "../hooks/useAuth";
import { useTasks } from "../hooks/useTasks";

export default function AppLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const menuRef = useRef(null);
  const [navOpen, setNavOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const { unread } = useTasks();
  const { user, logout } = useAuth();
  const studentName = user?.name || "Student";
  const firstName = studentName.split(" ")[0];

  useEffect(() => {
    function onKey(e) {
      if (e.key === "Escape") {
        setNavOpen(false);
        setMenuOpen(false);
      }
    }
    function onPointer(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false);
    }
    document.addEventListener("keydown", onKey);
    document.addEventListener("mousedown", onPointer);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("mousedown", onPointer);
    };
  }, []);

  const current = APP_ROUTES.find((r) => r.path === location.pathname);
  const title =
    location.pathname === "/dashboard"
      ? `Welcome back, ${firstName}`
      : current
        ? current.label
        : "NUDGE";

  async function handleSignOut() {
    setMenuOpen(false);
    await logout();
    navigate("/", { replace: true });
  }

  return (
    <div className="app-shell">
      <a href="#main-content" className="skip-link">Skip to main content</a>

      <div className={`scrim ${navOpen ? "open" : ""}`} onClick={() => setNavOpen(false)} />

      <aside className={`sidebar on-dark ${navOpen ? "open" : ""}`} id="sidebar" aria-label="Sidebar">
        <div className="sidebar-brand">
          <Logo to="/dashboard" />
        </div>
        <nav aria-label="Workspace">
          <ul className="sidebar-nav">
            {APP_ROUTES.map((r) => (
              <li key={r.path}>
                <NavLink
                  to={r.path}
                  className={({ isActive }) => `side-link ${isActive ? "active" : ""}`}
                  onClick={() => setNavOpen(false)}
                >
                  <Icon name={r.icon} />
                  <span>{r.navLabel}</span>
                  {r.path === "/notifications" && unread > 0 && (
                    <span className="nav-badge" aria-label={`${unread} unread`}>{unread}</span>
                  )}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      <div className="app-main">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="icon-btn mobile-only"
              aria-label="Open navigation"
              aria-expanded={navOpen}
              aria-controls="sidebar"
              onClick={() => setNavOpen(true)}
            >
              <Icon name="menu" />
            </button>
            <p className="topbar-title">{title}</p>
          </div>

          <div className="topbar-right">
            <NavLink
              to="/notifications"
              className="icon-btn bell-btn"
              aria-label={`Notifications${unread ? `, ${unread} unread` : ""}`}
            >
              <Icon name="bell" />
              {unread > 0 && <span className="bell-dot" aria-hidden="true" />}
            </NavLink>

            <div className="profile-menu" ref={menuRef}>
              <button
                className="profile-btn"
                aria-label={`Account menu for ${studentName}`}
                aria-haspopup="menu"
                aria-expanded={menuOpen}
                onClick={() => setMenuOpen((v) => !v)}
              >
                <span className="avatar" aria-hidden="true">{studentName.charAt(0).toUpperCase()}</span>
              </button>

              {menuOpen && (
                <div className="menu-pop" role="menu">
                  <div className="menu-head">
                    <strong>{studentName}</strong>
                  </div>
                  <NavLink to="/profile" className="menu-item" role="menuitem" onClick={() => setMenuOpen(false)}>
                    <Icon name="user" size={18} /> Profile
                  </NavLink>
                  <NavLink to="/settings" className="menu-item" role="menuitem" onClick={() => setMenuOpen(false)}>
                    <Icon name="settings" size={18} /> Settings
                  </NavLink>
                  <button className="menu-item" role="menuitem" onClick={handleSignOut}>
                    <Icon name="logout" size={18} /> Sign out
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        <main id="main-content" tabIndex={-1} className="app-content">
          <Outlet />
        </main>

        <Footer variant="app" />
      </div>
    </div>
  );
}
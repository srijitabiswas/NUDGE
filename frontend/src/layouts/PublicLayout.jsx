import { useEffect, useState } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
import Logo from "../components/Logo";
import Icon from "../components/Icon";
import Footer from "../components/Footer";

export default function PublicLayout() {
  const { hash, pathname } = useLocation();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (hash) document.getElementById(hash.slice(1))?.scrollIntoView();
    else window.scrollTo(0, 0);
  }, [hash, pathname]);

  const close = () => setOpen(false);

  return (
    <div className="public-shell">
      <a href="#main-content" className="skip-link">Skip to main content</a>

      <header className="site-header on-dark">
        <div className="container site-header-inner">
          <Logo />

          <button
            className="icon-btn menu-toggle"
            aria-label="Toggle menu"
            aria-expanded={open}
            aria-controls="site-menu"
            onClick={() => setOpen((v) => !v)}
          >
            <Icon name={open ? "close" : "menu"} />
          </button>

          <div id="site-menu" className={`site-collapsible ${open ? "open" : ""}`}>
            <nav className="site-nav" aria-label="Main">
              <Link className="nav-link" to="/" onClick={close}>Home</Link>
              <Link className="nav-link" to="/#features" onClick={close}>Features</Link>
              <Link className="nav-link" to="/#how-it-works" onClick={close}>How it works</Link>
            </nav>
            <div className="site-actions">
              <Link to="/login" className="btn btn-secondary btn-sm" onClick={close}>Sign in</Link>
              <Link to="/signup" className="btn btn-primary btn-sm" onClick={close}>Sign up</Link>
            </div>
          </div>
        </div>
      </header>

      <main id="main-content" tabIndex={-1} className="public-main">
        <Outlet />
      </main>

      <Footer />
    </div>
  );
}
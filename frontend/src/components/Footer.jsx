import { Link } from "react-router-dom";
import Logo from "./Logo";

export default function Footer({ variant = "public" }) {
  const year = new Date().getFullYear();

  if (variant === "app") {
    return (
      <footer className="site-footer site-footer-app">
        <div className="footer-bottom">
          <span>© {year} NUDGE. From Messages to Actions.</span>
          <span className="row">
            <Link to="/settings">Settings</Link>
            <Link to="/profile">Profile</Link>
          </span>
        </div>
      </footer>
    );
  }

  return (
    <footer className="site-footer">
      <div className="container">
        <div className="footer-grid">
          <div>
            <Logo />
            <p style={{ marginTop: "var(--space-3)", maxWidth: 360 }}>
              NUDGE turns scattered messages, notices and screenshots into tasks, deadlines and
              priorities, so students never miss what matters.
            </p>
          </div>
          <div>
            <h3>Product</h3>
            <ul className="footer-links">
              <li><Link to="/#features">Features</Link></li>
              <li><Link to="/#how-it-works">How it works</Link></li>
            </ul>
          </div>
          <div>
            <h3>Account</h3>
            <ul className="footer-links">
              <li><Link to="/login">Sign in</Link></li>
              <li><Link to="/signup">Sign up</Link></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <span>© {year} NUDGE. Intelligent Student Life Management Platform.</span>
          <span>B.Tech CSE final year project</span>
        </div>
      </div>
    </footer>
  );
}
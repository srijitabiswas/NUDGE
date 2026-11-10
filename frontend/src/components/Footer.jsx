import { Link } from "react-router-dom";
import Logo from "./Logo";
import { CONTACT_EMAIL } from "../config";

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
    <footer className="site-footer site-footer-public on-dark">
      <div className="container">
        <div className="footer-grid">
          <div>
            <Logo />
            <p className="footer-blurb">
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
          <span>© {year} NUDGE. All rights reserved.</span>
          <span className="row">
            <Link to="/privacy">Privacy</Link>
            <Link to="/terms">Terms</Link>
            {CONTACT_EMAIL && <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>}
          </span>
        </div>
      </div>
    </footer>
  );
}
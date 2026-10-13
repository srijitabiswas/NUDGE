import { Link } from "react-router-dom";

export default function Logo({ to = "/" }) {
  return (
    <Link to={to} className="logo" aria-label="NUDGE home">
      <span className="logo-mark" aria-hidden="true">N</span>
      <span>NUDGE</span>
    </Link>
  );
}
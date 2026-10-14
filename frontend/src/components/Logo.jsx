import { Link } from "react-router-dom";
import logoImg from "../assets/nudge-logo.png";

export default function Logo({ to = "/" }) {
  return (
    <Link to={to} className="logo" aria-label="NUDGE home">
      <img src={logoImg} alt="" className="logo-img" width="40" height="40" />
      <span>NUDGE</span>
    </Link>
  );
}
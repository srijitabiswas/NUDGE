import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function NotFoundPage() {
  const { user } = useAuth();
  return (
    <div className="container center-screen stack">
      <h1>Page not found</h1>
      <p className="muted">The page you are looking for doesn't exist or has moved.</p>
      <div className="row">
        <Link className="btn btn-primary" to={user ? "/dashboard" : "/"}>
          {user ? "Back to dashboard" : "Back to home"}
        </Link>
      </div>
    </div>
  );
}
import { Link } from "react-router-dom";
import { PUBLIC_ROUTES, APP_ROUTES } from "../routeConfig";

export default function PlaceholderPage({ title }) {
  const all = [...PUBLIC_ROUTES, ...APP_ROUTES];
  return (
    <main style={{ maxWidth: 640, margin: "48px auto", padding: "0 20px" }}>
      <h1>{title}</h1>
      <p>This page is coming in a later step.</p>
      <ul>
        {all.map((r) => (
          <li key={r.path}>
            <Link to={r.path}>{r.label}</Link> <code>{r.path}</code>
          </li>
        ))}
      </ul>
    </main>
  );
}
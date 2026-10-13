import { Routes, Route } from "react-router-dom";
import { PUBLIC_ROUTES, APP_ROUTES } from "./routeConfig";
import DashboardPage from "./pages/DashboardPage";
import PlaceholderPage from "./pages/PlaceholderPage";

const ALL = [...PUBLIC_ROUTES, ...APP_ROUTES];

export default function App() {
  return (
    <Routes>
      {ALL.filter((r) => r.path !== "/dashboard").map((r) => (
        <Route key={r.path} path={r.path} element={<PlaceholderPage title={r.label} />} />
      ))}
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="*" element={<PlaceholderPage title="Page not found" />} />
    </Routes>
  );
}
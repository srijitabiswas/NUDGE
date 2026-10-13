import { Routes, Route } from "react-router-dom";
import { APP_ROUTES } from "./routeConfig";
import PublicLayout from "./layouts/PublicLayout";
import AppLayout from "./layouts/AppLayout";
import { RequireAuth, PublicOnly } from "./components/RouteGuards";
import DashboardPage from "./pages/DashboardPage";
import PlaceholderPage from "./pages/PlaceholderPage";
import SignUpPage from "./pages/SignUpPage";
import LoginPage from "./pages/LoginPage";
import ProfileSetupPage from "./pages/ProfileSetupPage";
import ProfilePage from "./pages/ProfilePage";
import SettingsPage from "./pages/SettingsPage";
import TasksPage from "./pages/TasksPage";
import AcademicsPage from "./pages/AcademicsPage";
import AddInformationPage from "./pages/AddInformationPage";
import CalendarPage from "./pages/CalendarPage";
import AnalyticsPage from "./pages/AnalyticsPage";

export default function App() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route path="/" element={<PlaceholderPage title="Landing page" />} />
        <Route element={<PublicOnly />}>
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="/login" element={<LoginPage />} />
        </Route>
        <Route path="*" element={<PlaceholderPage title="Page not found" />} />
      </Route>

      <Route element={<RequireAuth />}>
        <Route path="/profile-setup" element={<ProfileSetupPage />} />
        <Route element={<AppLayout />}>
          {APP_ROUTES.filter((r) => !["/dashboard", "/tasks","/add-information",  "/academics", "/profile", "/settings", "/calendar", "/analytics"].includes(r.path)).map((r) => (
  <Route key={r.path} path={r.path} element={<PlaceholderPage title={r.label} />} />
))}
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/tasks" element={<TasksPage />} />
          <Route path="/add-information" element={<AddInformationPage />} />
          <Route path="/academics" element={<AcademicsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/calendar" element={<CalendarPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
        </Route>
      </Route>
    </Routes>
  );
}
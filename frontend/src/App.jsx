import { useEffect } from "react";
import { Route, Routes, useLocation } from "react-router-dom";
import PublicLayout from "./layouts/PublicLayout";
import AppLayout from "./layouts/AppLayout";
import { RequireAuth, PublicOnly } from "./components/RouteGuards";
import LandingPage from "./pages/LandingPage";
import NotFoundPage from "./pages/NotFoundPage";
import LegalPage from "./pages/LegalPage";
import SignUpPage from "./pages/SignUpPage";
import LoginPage from "./pages/LoginPage";
import ProfileSetupPage from "./pages/ProfileSetupPage";
import DashboardPage from "./pages/DashboardPage";
import TasksPage from "./pages/TasksPage";
import AcademicsPage from "./pages/AcademicsPage";
import CalendarPage from "./pages/CalendarPage";
import AddInformationPage from "./pages/AddInformationPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import NotificationsPage from "./pages/NotificationsPage";
import ProfilePage from "./pages/ProfilePage";
import SettingsPage from "./pages/SettingsPage";

const TITLES = {
  "/": "NUDGE | From Messages to Actions",
  "/signup": "Sign up",
  "/login": "Log in",
  "/privacy": "Privacy Policy",
  "/terms": "Terms of Use",
  "/profile-setup": "Set up your profile",
  "/dashboard": "Dashboard",
  "/tasks": "My Tasks",
  "/academics": "Assignments and Exams",
  "/calendar": "Calendar",
  "/add-information": "Add Information",
  "/analytics": "Priorities and Analytics",
  "/notifications": "Notifications",
  "/profile": "Student Profile",
  "/settings": "Settings",
};

// Keeps the browser tab title in step with the current page.
function PageTitle() {
  const { pathname } = useLocation();
  useEffect(() => {
    const t = TITLES[pathname];
    document.title = !t ? "Page not found | NUDGE" : pathname === "/" ? t : `${t} | NUDGE`;
  }, [pathname]);
  return null;
}

export default function App() {
  return (
    <>
    <PageTitle />
    <Routes>
      <Route element={<PublicLayout />}>
        <Route path="/" element={<LandingPage />} />
        <Route path="/privacy" element={<LegalPage kind="privacy" />} />
        <Route path="/terms" element={<LegalPage kind="terms" />} />
        <Route element={<PublicOnly />}>
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="/login" element={<LoginPage />} />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Route>

      <Route element={<RequireAuth />}>
        <Route path="/profile-setup" element={<ProfileSetupPage />} />
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/tasks" element={<TasksPage />} />
          <Route path="/academics" element={<AcademicsPage />} />
          <Route path="/calendar" element={<CalendarPage />} />
          <Route path="/add-information" element={<AddInformationPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Route>
    </Routes>
    </>
  );
}
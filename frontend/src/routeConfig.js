// Single source of truth for every route in the app.
export const PUBLIC_ROUTES = [
  { path: "/", label: "Landing page" },
  { path: "/signup", label: "Sign up" },
  { path: "/login", label: "Sign in" },
];

// Order here is the sidebar order.
export const APP_ROUTES = [
  { path: "/dashboard", label: "Dashboard", navLabel: "Dashboard", icon: "dashboard" },
  { path: "/tasks", label: "My Tasks", navLabel: "My Tasks", icon: "tasks" },
  { path: "/academics", label: "Assignments & Exams", navLabel: "Academics", icon: "academics" },
  { path: "/calendar", label: "Calendar", navLabel: "Calendar", icon: "calendar" },
  { path: "/add-information", label: "Add Information", navLabel: "Add Information", icon: "add" },
  { path: "/analytics", label: "Priorities & Analytics", navLabel: "Analytics", icon: "analytics" },
  { path: "/notifications", label: "Notifications", navLabel: "Notifications", icon: "bell" },
  { path: "/profile", label: "Student Profile", navLabel: "Profile", icon: "user" },
  { path: "/settings", label: "Settings", navLabel: "Settings", icon: "settings" },
];
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "@fontsource/fraunces/600.css";
import "@fontsource/fraunces/700.css";
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "./index.css";
import "./styles/ui.css";
import "./styles/layout.css";
import App from "./App.jsx";
import "./styles/theme.css";
import "./styles/shell.css";
import "./styles/public.css";
import "./styles/pages.css";
import "./styles/landing.css";
import AuthProvider from "./context/AuthProvider.jsx";
import TaskProvider from "./context/TaskProvider.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <TaskProvider>
          <App />
        </TaskProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
);
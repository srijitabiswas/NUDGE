import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button, Callout, Card, Field } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { USING_DEMO_AUTH } from "../services/authService";
import { validateLogin } from "../utils/validation";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [values, setValues] = useState({ email: "", password: "" });
  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function setField(key, value) {
    setValues((v) => ({ ...v, [key]: value }));
    setErrors((e) => ({ ...e, [key]: "" }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitError("");
    const found = validateLogin(values);
    setErrors(found);
    const first = Object.keys(found)[0];
    if (first) {
      document.getElementById(`login-${first}`)?.focus();
      return;
    }
    setSubmitting(true);
    try {
      await login(values);
      navigate(location.state?.from || "/dashboard", { replace: true });
    } catch (err) {
      setSubmitError(err.message || "Could not sign in.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-wrap">
      <Card>
        <h1 className="auth-title">Welcome back</h1>
        <p className="muted">Sign in to see your tasks and deadlines.</p>

        {USING_DEMO_AUTH && (
          <Callout tone="warning">
            Demo mode: no backend yet. Your password is not checked. Only accounts created in this browser can sign in.
          </Callout>
        )}

        <form className="stack" onSubmit={handleSubmit} noValidate style={{ marginTop: "var(--space-4)" }}>
          <Field id="login-email" label="Email" type="email" autoComplete="email" required
            value={values.email} onChange={(e) => setField("email", e.target.value)} error={errors.email} />
          <Field id="login-password" label="Password" type="password" autoComplete="current-password" required
            value={values.password} onChange={(e) => setField("password", e.target.value)} error={errors.password} />

          {submitError && <Callout tone="danger">{submitError}</Callout>}

          <Button type="submit" size="lg" disabled={submitting}>
            {submitting ? "Signing in…" : "Sign in"}
          </Button>
        </form>

        <p className="auth-switch">
          New to NUDGE? <Link to="/signup">Create an account</Link>
        </p>
      </Card>
    </div>
  );
}
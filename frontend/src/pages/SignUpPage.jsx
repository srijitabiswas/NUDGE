import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button, Callout, Card, Field } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { USING_DEMO_AUTH } from "../services/authService";
import { validateSignUp } from "../utils/validation";
import AuthAside from "../components/AuthAside";

export default function SignUpPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [values, setValues] = useState({ name: "", email: "", password: "", confirm: "" });
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
    const found = validateSignUp(values);
    setErrors(found);
    const first = Object.keys(found)[0];
    if (first) {
      document.getElementById(`signup-${first}`)?.focus();
      return;
    }
    setSubmitting(true);
    try {
      await register(values);
      navigate("/profile-setup", { replace: true });
    } catch (err) {
      setSubmitError(err.message || "Could not create the account.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-wrap">
            <AuthAside mode="signup" />
      <Card>
        <h1 className="auth-title">Create your account</h1>
        <p className="muted">Set up NUDGE in a minute. You can add your academic details next.</p>

        {USING_DEMO_AUTH && (
          <Callout tone="warning">
            Demo mode: no backend yet. Your password is not stored or checked, and this account exists only in this browser.
          </Callout>
        )}

        <form className="stack" onSubmit={handleSubmit} noValidate style={{ marginTop: "var(--space-4)" }}>
          <Field id="signup-name" label="Full name" autoComplete="name" required
            value={values.name} onChange={(e) => setField("name", e.target.value)} error={errors.name} />
          <Field id="signup-email" label="Email" type="email" autoComplete="email" required
            value={values.email} onChange={(e) => setField("email", e.target.value)} error={errors.email} />
          <Field id="signup-password" label="Password" type="password" autoComplete="new-password" required
            hint="At least 8 characters, with a letter and a number."
            value={values.password} onChange={(e) => setField("password", e.target.value)} error={errors.password} />
          <Field id="signup-confirm" label="Confirm password" type="password" autoComplete="new-password" required
            value={values.confirm} onChange={(e) => setField("confirm", e.target.value)} error={errors.confirm} />

          {submitError && <Callout tone="danger">{submitError}</Callout>}

          <Button type="submit" size="lg" disabled={submitting}>
            {submitting ? "Creating account…" : "Create account"}
          </Button>
        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </Card>
    </div>
  );
}
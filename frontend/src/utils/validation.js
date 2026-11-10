const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateName(value) {
  const v = value.trim();
  if (!v) return "Name is required.";
  if (v.length < 2) return "Name must be at least 2 characters.";
  return "";
}

export function validateEmail(value) {
  const v = value.trim();
  if (!v) return "Email is required.";
  if (!EMAIL_RE.test(v)) return "Enter a valid email address.";
  return "";
}

export function validatePassword(value) {
  if (!value) return "Password is required.";
  if (value.length < 8) return "Password must be at least 8 characters.";
  if (!/[A-Za-z]/.test(value) || !/\d/.test(value)) return "Use at least one letter and one number.";
  return "";
}

function clean(errors) {
  return Object.fromEntries(Object.entries(errors).filter(([, msg]) => msg));
}

export function validateSignUp({ name, email, password, confirm }) {
  return clean({
    name: validateName(name),
    email: validateEmail(email),
    password: validatePassword(password),
    confirm: password !== confirm ? "Passwords do not match." : "",
  });
}

export function validateLogin({ email, password }) {
  return clean({
    email: validateEmail(email),
    password: password ? "" : "Password is required.",
  });
}
// Authentication service. The ONLY place that talks to the auth backend.
//
// IMPORTANT: no auth backend exists yet, so USING_DEMO_AUTH = true runs a DEMO mode:
//  - Passwords are never stored or checked. This is NOT secure.
//  - Accounts and the session live only in this browser's localStorage.
// When the backend interface is agreed, set USING_DEMO_AUTH = false and implement
// the real calls in each function below.

export const USING_DEMO_AUTH = true;

const ACCOUNTS_KEY = "nudge.demo.accounts";
const SESSION_KEY = "nudge.demo.session";

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function notConnected() {
  throw new Error("The authentication service is not connected yet.");
}

function read(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function write(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* storage unavailable: demo session will not persist */
  }
}

function newId() {
  return crypto.randomUUID ? crypto.randomUUID() : `u${Date.now()}`;
}

const normalizeEmail = (email) => email.trim().toLowerCase();

// Returns the signed-in account, or null.
export async function getSession() {
  if (!USING_DEMO_AUTH) notConnected();
  const session = read(SESSION_KEY, null);
  if (!session) return null;
  return read(ACCOUNTS_KEY, []).find((a) => a.id === session.id) || null;
}

// Demo mode ignores the password on purpose (never stored, never checked).
export async function register({ name, email }) {
  if (!USING_DEMO_AUTH) notConnected();
  await wait(300);
  const accounts = read(ACCOUNTS_KEY, []);
  const key = normalizeEmail(email);
  if (accounts.some((a) => a.email === key)) {
    throw new Error("An account with this email already exists.");
  }
  const account = {
    id: newId(),
    name: name.trim(),
    email: key,
    profile: { completed: false },
    createdAt: new Date().toISOString(),
  };
  write(ACCOUNTS_KEY, [...accounts, account]);
  write(SESSION_KEY, { id: account.id });
  return account;
}

export async function login({ email }) {
  if (!USING_DEMO_AUTH) notConnected();
  await wait(300);
  const account = read(ACCOUNTS_KEY, []).find((a) => a.email === normalizeEmail(email));
  if (!account) throw new Error("No account found for this email. Sign up first (demo mode).");
  write(SESSION_KEY, { id: account.id });
  return account;
}

export async function logout() {
  if (!USING_DEMO_AUTH) notConnected();
  try {
    localStorage.removeItem(SESSION_KEY);
  } catch {
    /* ignore */
  }
}

// changes: { name?, profile? }. The profile object is merged into the saved profile.
export async function updateAccount(changes) {
  if (!USING_DEMO_AUTH) notConnected();
  await wait(200);
  const session = read(SESSION_KEY, null);
  if (!session) throw new Error("You are not signed in.");
  const accounts = read(ACCOUNTS_KEY, []);
  const index = accounts.findIndex((a) => a.id === session.id);
  if (index === -1) throw new Error("Account not found.");
  const current = accounts[index];
  const updated = {
    ...current,
    ...(changes.name !== undefined ? { name: changes.name.trim() } : {}),
    profile: { ...current.profile, ...(changes.profile || {}) },
  };
  accounts[index] = updated;
  write(ACCOUNTS_KEY, accounts);
  return updated;
}
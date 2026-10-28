// Single entry point for HTTP calls to the backend.
// No endpoints are defined here on purpose: they will be added in services/*.js once the
// backend contract is agreed. Set VITE_API_BASE_URL in frontend/.env (for example
// VITE_API_BASE_URL=http://localhost:8000) before switching a service off sample data.

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(message, status, details) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

export const apiConfigured = () => BASE_URL !== "";

// request("/some/path", { method: "POST", body: { ... } }) -> parsed JSON (or null for 204)
export async function request(path, { method = "GET", body, headers = {}, signal } = {}) {
  if (!apiConfigured()) throw new ApiError("The API address is not configured yet.", 0);

  let res;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      method,
      credentials: "include",
      signal,
      headers: { Accept: "application/json", ...(body ? { "Content-Type": "application/json" } : {}), ...headers },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (err) {
    if (err.name === "AbortError") throw err;
    throw new ApiError("Could not reach the server. Check your connection and try again.", 0);
  }

  if (res.status === 204) return null;
  let data = null;
  try {
    data = await res.json();
  } catch {
    /* response had no JSON body */
  }
  if (!res.ok) {
    throw new ApiError(data?.message || data?.detail || `Request failed (${res.status}).`, res.status, data);
  }
  return data;
}
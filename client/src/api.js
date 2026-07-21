const API_URL = import.meta.env.VITE_API_URL || "/api";

export const TOKEN_KEY = "atomic_token";

function token() {
  return localStorage.getItem(TOKEN_KEY);
}

async function request(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const authToken = token();
  if (authToken) headers.Authorization = `Bearer ${authToken}`;

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error || "Something went wrong");
  return body;
}

export function signUp(username, email, password) {
  return request("/auth/signup", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });
}

export function logIn(email, password) {
  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function createPlaidLinkToken() {
  return request("/plaid/link-token", { method: "POST" });
}

export function createSandboxPublicToken() {
  return request("/plaid/sandbox-token", { method: "POST" });
}

export function exchangePlaidToken(publicToken) {
  return request("/plaid/exchange", {
    method: "POST",
    body: JSON.stringify({ public_token: publicToken }),
  });
}

export function syncPlaidTransactions() {
  return request("/plaid/sync", { method: "POST" });
}

export function getDashboard() {
  return request("/dashboard");
}

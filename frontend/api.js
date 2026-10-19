// Shared API helpers: backend address, access token storage and authorized requests.

const API_URL = "http://localhost:8000";
const TOKEN_STORAGE_KEY = "lagoa-token";

function getToken() {
  try { return localStorage.getItem(TOKEN_STORAGE_KEY); } catch { return null; }
}

function setToken(token) {
  try { localStorage.setItem(TOKEN_STORAGE_KEY, token); } catch {}
}

function clearToken() {
  try { localStorage.removeItem(TOKEN_STORAGE_KEY); } catch {}
}

function goToLogin() {
  clearToken();
  window.location.replace("login.html");
}

// fetch() to the backend with the access token attached. A 401 means the
// token is missing or expired, so the user is sent back to the login page.
async function apiFetch(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.body) headers["Content-Type"] = "application/json";

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (res.status === 401) {
    goToLogin();
    throw new Error("Not authenticated");
  }
  return res;
}

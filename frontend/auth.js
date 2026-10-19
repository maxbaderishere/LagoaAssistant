// Login and registration page.

const form = document.getElementById("authForm");
const loginInput = document.getElementById("login");
const passwordInput = document.getElementById("password");
const passwordHint = document.getElementById("passwordHint");
const errorBox = document.getElementById("authError");
const submitBtn = document.getElementById("authSubmit");
const switchBtn = document.getElementById("switchBtn");

const MODES = {
  login: {
    title: "signInTitle", sub: "signInSub", submit: "submitSignIn",
    switchText: "noAccount", switchBtn: "signUp", other: "register",
    path: "/auth/login", autocomplete: "current-password",
  },
  register: {
    title: "signUpTitle", sub: "signUpSub", submit: "submitSignUp",
    switchText: "haveAccount", switchBtn: "signIn", other: "login",
    path: "/auth/register", autocomplete: "new-password",
  },
};

let mode = "login";

// Sets a translation key on an element so a language switch re-translates it.
function setText(id, key) {
  const el = document.getElementById(id);
  el.dataset.i18n = key;
  el.textContent = t(key);
}

function setMode(newMode) {
  mode = newMode;
  const m = MODES[mode];
  setText("authTitle", m.title);
  setText("authSub", m.sub);
  setText("authSubmit", m.submit);
  setText("switchText", m.switchText);
  setText("switchBtn", m.switchBtn);
  passwordInput.autocomplete = m.autocomplete;
  passwordHint.hidden = mode !== "register";
  document.querySelectorAll("[data-mode]").forEach(tab => {
    tab.setAttribute("aria-selected", String(tab.dataset.mode === mode));
  });
  hideError();
}

function showError(key) {
  errorBox.dataset.i18n = key;
  errorBox.textContent = t(key);
  errorBox.hidden = false;
}

function hideError() {
  errorBox.hidden = true;
}

function validate(login, password) {
  if (login.length < 3 || login.length > 64) return "loginLength";
  if (mode === "register" && password.length < 8) return "passwordLength";
  if (!password) return "passwordLength";
  return null;
}

const ERROR_BY_STATUS = { 401: "invalidCredentials", 409: "loginTaken", 422: "invalidInput" };

async function submit() {
  const login = loginInput.value.trim();
  const password = passwordInput.value;
  const problem = validate(login, password);
  if (problem) {
    showError(problem);
    return;
  }

  hideError();
  submitBtn.disabled = true;
  try {
    const res = await fetch(`${API_URL}${MODES[mode].path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ login, password }),
    });
    if (!res.ok) {
      showError(ERROR_BY_STATUS[res.status] ?? "authFailed");
      return;
    }
    const data = await res.json();
    setToken(data.access_token);
    window.location.replace("index.html");
  } catch (e) {
    console.error(e);
    showError("networkError");
  } finally {
    submitBtn.disabled = false;
  }
}

// Already signed in with a valid token: go straight to the chat.
async function skipIfSignedIn() {
  const token = getToken();
  if (!token) return;
  try {
    const res = await fetch(`${API_URL}/auth/me`, { headers: { Authorization: `Bearer ${token}` } });
    if (res.ok) window.location.replace("index.html");
    else clearToken();
  } catch {}
}

form.addEventListener("submit", e => {
  e.preventDefault();
  submit();
});
switchBtn.addEventListener("click", () => setMode(MODES[mode].other));
document.querySelectorAll("[data-mode]").forEach(tab => {
  tab.addEventListener("click", () => setMode(tab.dataset.mode));
});
initLanguageMenus();
applyTranslations();
setMode("login");
loginInput.focus();
skipIfSignedIn();

// Interface translations. Static text in index.html is marked with data-i18n
// attributes; dynamic text in app.js goes through t().

const TRANSLATIONS = {
  ru: {
    chats: "Чаты",
    beta: "Бета",
    newChat: "Новый чат",
    newConversation: "Новый разговор",
    connecting: "Подключение к API…",
    apiConnected: "API подключено",
    apiUnavailable: "API недоступно",
    requestFailed: "Ошибка запроса",
    openMenu: "Открыть меню",
    modelLabel: "Модель",
    conversation: "Переписка",
    greetingNight: "Доброй ночи",
    greetingMorning: "Доброе утро",
    greetingDay: "Добрый день",
    greetingEvening: "Добрый вечер",
    welcomeSub: "О чём подумаем сегодня?",
    tripTitle: "Спланировать поездку",
    tripSub: "Маршрут на выходные без суеты",
    tripPrompt: "Помоги спланировать поездку на выходные без суеты: куда поехать и что посмотреть?",
    letterTitle: "Написать письмо",
    letterSub: "Вежливо, но твёрдо",
    letterPrompt: "Помоги написать вежливое, но твёрдое письмо. Сначала спроси, кому и о чём.",
    explainTitle: "Объяснить сложное",
    explainSub: "Простыми словами и с примерами",
    explainPrompt: "Объясни простыми словами и с примерами, как работает интернет.",
    codeTitle: "Помочь с кодом",
    codeSub: "Найти ошибку и объяснить её",
    codePrompt: "Помоги разобраться с ошибкой в моём коде на Python. Сначала спроси, что за ошибка.",
    disclaimer: "Lagoa может ошибаться. Проверяйте важное.",
    messageLabel: "Сообщение для Lagoa",
    placeholder: "Спросите Lagoa о чём угодно",
    hint: "Enter — отправить, Shift+Enter — новая строка",
    send: "Отправить",
    copy: "Копировать",
    copied: "Скопировано",
    copyFailed: "Не удалось скопировать",
    thinking: "Lagoa думает…",
    serverError: "Сервер вернул ошибку {status}. Подробности — в терминале с uvicorn.",
    networkError: "Не удалось связаться с API. Запущен ли сервер на localhost:8000?",
    language: "Язык интерфейса",
    signIn: "Вход",
    signUp: "Регистрация",
    signInTitle: "С возвращением",
    signInSub: "Войдите, чтобы продолжить разговор",
    signUpTitle: "Добро пожаловать",
    signUpSub: "Создайте аккаунт, и Lagoa запомнит ваши разговоры",
    loginLabel: "Логин или email",
    passwordLabel: "Пароль",
    passwordHint: "Не короче 8 символов",
    submitSignIn: "Войти",
    submitSignUp: "Создать аккаунт",
    noAccount: "Нет аккаунта?",
    haveAccount: "Уже есть аккаунт?",
    loginLength: "Логин должен быть от 3 до 64 символов",
    passwordLength: "Пароль должен быть не короче 8 символов",
    invalidCredentials: "Неверный логин или пароль",
    loginTaken: "Этот логин уже занят",
    invalidInput: "Проверьте логин и пароль: логин от 3 символов, пароль от 8",
    authFailed: "Не получилось войти. Попробуйте ещё раз",
    logout: "Выйти",
    today: "Сегодня",
    yesterday: "Вчера",
    thisWeek: "На этой неделе",
    earlier: "Ранее",
    chatActions: "Действия с чатом",
    rename: "Переименовать",
    delete: "Удалить",
    deleteTitle: "Удалить чат?",
    deleteText: "Все сообщения будут удалены без возможности восстановления:",
    cancel: "Отмена",
  },
  en: {
    chats: "Chats",
    beta: "Beta",
    newChat: "New chat",
    newConversation: "New conversation",
    connecting: "Connecting to the API…",
    apiConnected: "API connected",
    apiUnavailable: "API unavailable",
    requestFailed: "Request failed",
    openMenu: "Open menu",
    modelLabel: "Model",
    conversation: "Conversation",
    greetingNight: "Good night",
    greetingMorning: "Good morning",
    greetingDay: "Good afternoon",
    greetingEvening: "Good evening",
    welcomeSub: "What shall we think about today?",
    tripTitle: "Plan a trip",
    tripSub: "A relaxed weekend route",
    tripPrompt: "Help me plan a relaxed weekend trip: where to go and what to see?",
    letterTitle: "Write a letter",
    letterSub: "Polite but firm",
    letterPrompt: "Help me write a polite but firm letter. First ask who it's for and what it's about.",
    explainTitle: "Explain something hard",
    explainSub: "In plain words, with examples",
    explainPrompt: "Explain in plain words, with examples, how the internet works.",
    codeTitle: "Help with code",
    codeSub: "Find a bug and explain it",
    codePrompt: "Help me figure out a bug in my Python code. First ask what the error is.",
    disclaimer: "Lagoa can make mistakes. Double-check what matters.",
    messageLabel: "Message to Lagoa",
    placeholder: "Ask Lagoa anything",
    hint: "Enter to send, Shift+Enter for a new line",
    send: "Send",
    copy: "Copy",
    copied: "Copied",
    copyFailed: "Couldn't copy",
    thinking: "Lagoa is thinking…",
    serverError: "The server returned error {status}. See the uvicorn terminal for details.",
    networkError: "Couldn't reach the API. Is the server running on localhost:8000?",
    language: "Interface language",
    signIn: "Sign in",
    signUp: "Sign up",
    signInTitle: "Welcome back",
    signInSub: "Sign in to pick up the conversation",
    signUpTitle: "Welcome",
    signUpSub: "Create an account and Lagoa will remember your conversations",
    loginLabel: "Login or email",
    passwordLabel: "Password",
    passwordHint: "At least 8 characters",
    submitSignIn: "Sign in",
    submitSignUp: "Create account",
    noAccount: "No account yet?",
    haveAccount: "Already have an account?",
    loginLength: "Login must be 3 to 64 characters long",
    passwordLength: "Password must be at least 8 characters long",
    invalidCredentials: "Wrong login or password",
    loginTaken: "This login is already taken",
    invalidInput: "Check your login and password: login 3+ characters, password 8+",
    authFailed: "Couldn't sign in. Please try again",
    logout: "Sign out",
    today: "Today",
    yesterday: "Yesterday",
    thisWeek: "This week",
    earlier: "Earlier",
    chatActions: "Chat actions",
    rename: "Rename",
    delete: "Delete",
    deleteTitle: "Delete chat?",
    deleteText: "All messages will be permanently deleted:",
    cancel: "Cancel",
  },
};

const LANG_STORAGE_KEY = "lagoa-lang";

function detectLanguage() {
  try {
    const saved = localStorage.getItem(LANG_STORAGE_KEY);
    if (saved in TRANSLATIONS) return saved;
  } catch {}
  return navigator.language.toLowerCase().startsWith("ru") ? "ru" : "en";
}

let currentLang = detectLanguage();

// Returns the translation for key, with {name} placeholders filled from params.
function t(key, params = {}) {
  const text = TRANSLATIONS[currentLang][key] ?? TRANSLATIONS.ru[key] ?? key;
  return text.replace(/\{(\w+)\}/g, (_, name) => params[name] ?? `{${name}}`);
}

// Fills every element marked with data-i18n* attributes inside root.
function applyTranslations(root = document) {
  root.querySelectorAll("[data-i18n]").forEach(el => { el.textContent = t(el.dataset.i18n); });
  root.querySelectorAll("[data-i18n-placeholder]").forEach(el => { el.placeholder = t(el.dataset.i18nPlaceholder); });
  root.querySelectorAll("[data-i18n-title]").forEach(el => { el.title = t(el.dataset.i18nTitle); });
  root.querySelectorAll("[data-i18n-aria-label]").forEach(el => { el.setAttribute("aria-label", t(el.dataset.i18nAriaLabel)); });
  root.querySelectorAll("[data-i18n-prompt]").forEach(el => { el.dataset.prompt = t(el.dataset.i18nPrompt); });
  document.documentElement.lang = currentLang;
  document.querySelectorAll("[data-lang]").forEach(btn => {
    btn.setAttribute("aria-pressed", String(btn.dataset.lang === currentLang));
  });
}

function setLanguage(lang) {
  if (!(lang in TRANSLATIONS)) return;
  currentLang = lang;
  try { localStorage.setItem(LANG_STORAGE_KEY, lang); } catch {}
  applyTranslations();
}

// Interface translations. Static text in index.html is marked with data-i18n
// attributes; dynamic text in app.js goes through t().

const MODEL_NAME = "Gemini";

const TRANSLATIONS = {
  ru: {
    chats: "Чаты",
    beta: "Бета",
    newChat: "Новый чат",
    soon: "· скоро",
    newChatSoon: "Несколько чатов появятся в следующих версиях",
    yourDialog: "Ваш диалог",
    newConversation: "Новый разговор",
    connecting: "Подключение к API…",
    apiConnected: "{model} · API подключено",
    apiUnavailable: "API недоступно",
    requestFailed: "Ошибка запроса",
    openMenu: "Открыть меню",
    model: "Модель: {model}",
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
    disclaimer: "Lagoa работает на {model} и может ошибаться. Проверяйте важное.",
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
  },
  en: {
    chats: "Chats",
    beta: "Beta",
    newChat: "New chat",
    soon: "· soon",
    newChatSoon: "Multiple chats are coming in a future version",
    yourDialog: "Your conversation",
    newConversation: "New conversation",
    connecting: "Connecting to the API…",
    apiConnected: "{model} · API connected",
    apiUnavailable: "API unavailable",
    requestFailed: "Request failed",
    openMenu: "Open menu",
    model: "Model: {model}",
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
    disclaimer: "Lagoa runs on {model} and can make mistakes. Double-check what matters.",
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
  return text.replace(/\{(\w+)\}/g, (_, name) => params[name] ?? (name === "model" ? MODEL_NAME : `{${name}}`));
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

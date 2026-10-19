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
    ollamaProvider: "Ollama · работает без интернета",
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
    stop: "Остановить ответ",
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
    ollamaProvider: "Ollama · works offline",
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
    stop: "Stop answering",
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
  pt: {
    chats: "Conversas",
    beta: "Beta",
    newChat: "Nova conversa",
    newConversation: "Nova conversa",
    connecting: "Conectando à API…",
    apiConnected: "API conectada",
    apiUnavailable: "API indisponível",
    requestFailed: "Erro na solicitação",
    openMenu: "Abrir menu",
    modelLabel: "Modelo",
    ollamaProvider: "Ollama · funciona sem internet",
    conversation: "Conversa",
    greetingNight: "Boa noite",
    greetingMorning: "Bom dia",
    greetingDay: "Boa tarde",
    greetingEvening: "Boa noite",
    welcomeSub: "Sobre o que vamos pensar hoje?",
    tripTitle: "Planejar uma viagem",
    tripSub: "Um roteiro tranquilo de fim de semana",
    tripPrompt: "Me ajude a planejar uma viagem tranquila de fim de semana: para onde ir e o que ver?",
    letterTitle: "Escrever uma carta",
    letterSub: "Educada, mas firme",
    letterPrompt: "Me ajude a escrever uma carta educada, mas firme. Primeiro pergunte para quem e sobre o quê.",
    explainTitle: "Explicar algo difícil",
    explainSub: "Em palavras simples e com exemplos",
    explainPrompt: "Explique em palavras simples e com exemplos como a internet funciona.",
    codeTitle: "Ajudar com código",
    codeSub: "Encontrar um erro e explicá-lo",
    codePrompt: "Me ajude a entender um erro no meu código Python. Primeiro pergunte qual é o erro.",
    disclaimer: "A Lagoa pode cometer erros. Confira o que for importante.",
    messageLabel: "Mensagem para a Lagoa",
    placeholder: "Pergunte qualquer coisa à Lagoa",
    hint: "Enter para enviar, Shift+Enter para nova linha",
    send: "Enviar",
    stop: "Parar resposta",
    copy: "Copiar",
    copied: "Copiado",
    copyFailed: "Não foi possível copiar",
    thinking: "A Lagoa está pensando…",
    serverError: "O servidor retornou o erro {status}. Veja os detalhes no terminal do uvicorn.",
    networkError: "Não foi possível conectar à API. O servidor está rodando em localhost:8000?",
    language: "Idioma da interface",
    signIn: "Entrar",
    signUp: "Cadastrar",
    signInTitle: "Que bom te ver de novo",
    signInSub: "Entre para continuar a conversa",
    signUpTitle: "Boas-vindas",
    signUpSub: "Crie uma conta e a Lagoa vai lembrar das suas conversas",
    loginLabel: "Login ou e-mail",
    passwordLabel: "Senha",
    passwordHint: "Pelo menos 8 caracteres",
    submitSignIn: "Entrar",
    submitSignUp: "Criar conta",
    noAccount: "Ainda não tem conta?",
    haveAccount: "Já tem uma conta?",
    loginLength: "O login deve ter de 3 a 64 caracteres",
    passwordLength: "A senha deve ter pelo menos 8 caracteres",
    invalidCredentials: "Login ou senha incorretos",
    loginTaken: "Este login já está em uso",
    invalidInput: "Confira o login e a senha: login com 3+ caracteres, senha com 8+",
    authFailed: "Não foi possível entrar. Tente novamente",
    logout: "Sair",
    today: "Hoje",
    yesterday: "Ontem",
    thisWeek: "Esta semana",
    earlier: "Antes",
    chatActions: "Ações da conversa",
    rename: "Renomear",
    delete: "Excluir",
    deleteTitle: "Excluir conversa?",
    deleteText: "Todas as mensagens serão excluídas permanentemente:",
    cancel: "Cancelar",
  },
  es: {
    chats: "Chats",
    beta: "Beta",
    newChat: "Nuevo chat",
    newConversation: "Nueva conversación",
    connecting: "Conectando con la API…",
    apiConnected: "API conectada",
    apiUnavailable: "API no disponible",
    requestFailed: "Error en la solicitud",
    openMenu: "Abrir menú",
    modelLabel: "Modelo",
    ollamaProvider: "Ollama · funciona sin internet",
    conversation: "Conversación",
    greetingNight: "Buenas noches",
    greetingMorning: "Buenos días",
    greetingDay: "Buenas tardes",
    greetingEvening: "Buenas noches",
    welcomeSub: "¿En qué pensamos hoy?",
    tripTitle: "Planear un viaje",
    tripSub: "Una ruta de fin de semana sin prisas",
    tripPrompt: "Ayúdame a planear un viaje de fin de semana sin prisas: ¿adónde ir y qué ver?",
    letterTitle: "Escribir una carta",
    letterSub: "Educada, pero firme",
    letterPrompt: "Ayúdame a escribir una carta educada, pero firme. Primero pregunta para quién es y de qué trata.",
    explainTitle: "Explicar algo difícil",
    explainSub: "Con palabras sencillas y ejemplos",
    explainPrompt: "Explica con palabras sencillas y ejemplos cómo funciona internet.",
    codeTitle: "Ayuda con código",
    codeSub: "Encontrar un error y explicarlo",
    codePrompt: "Ayúdame a entender un error en mi código de Python. Primero pregunta cuál es el error.",
    disclaimer: "Lagoa puede cometer errores. Comprueba lo importante.",
    messageLabel: "Mensaje para Lagoa",
    placeholder: "Pregúntale a Lagoa lo que quieras",
    hint: "Enter para enviar, Shift+Enter para nueva línea",
    send: "Enviar",
    stop: "Detener respuesta",
    copy: "Copiar",
    copied: "Copiado",
    copyFailed: "No se pudo copiar",
    thinking: "Lagoa está pensando…",
    serverError: "El servidor devolvió el error {status}. Mira los detalles en la terminal de uvicorn.",
    networkError: "No se pudo conectar con la API. ¿Está el servidor en marcha en localhost:8000?",
    language: "Idioma de la interfaz",
    signIn: "Iniciar sesión",
    signUp: "Registrarse",
    signInTitle: "Hola de nuevo",
    signInSub: "Inicia sesión para seguir la conversación",
    signUpTitle: "Te damos la bienvenida",
    signUpSub: "Crea una cuenta y Lagoa recordará tus conversaciones",
    loginLabel: "Usuario o correo",
    passwordLabel: "Contraseña",
    passwordHint: "Al menos 8 caracteres",
    submitSignIn: "Entrar",
    submitSignUp: "Crear cuenta",
    noAccount: "¿Aún no tienes cuenta?",
    haveAccount: "¿Ya tienes cuenta?",
    loginLength: "El usuario debe tener entre 3 y 64 caracteres",
    passwordLength: "La contraseña debe tener al menos 8 caracteres",
    invalidCredentials: "Usuario o contraseña incorrectos",
    loginTaken: "Este usuario ya está en uso",
    invalidInput: "Revisa el usuario y la contraseña: usuario de 3+ caracteres, contraseña de 8+",
    authFailed: "No se pudo iniciar sesión. Inténtalo de nuevo",
    logout: "Cerrar sesión",
    today: "Hoy",
    yesterday: "Ayer",
    thisWeek: "Esta semana",
    earlier: "Antes",
    chatActions: "Acciones del chat",
    rename: "Renombrar",
    delete: "Eliminar",
    deleteTitle: "¿Eliminar el chat?",
    deleteText: "Todos los mensajes se eliminarán de forma permanente:",
    cancel: "Cancelar",
  },
};

// Languages in the language menu: code shown on the button and the name in that language.
const LANGUAGES = [
  { code: "ru", label: "RU", name: "Русский" },
  { code: "en", label: "EN", name: "English" },
  { code: "pt", label: "PT", name: "Português" },
  { code: "es", label: "ES", name: "Español" },
];

const LANG_STORAGE_KEY = "lagoa-lang";

function detectLanguage() {
  try {
    const saved = localStorage.getItem(LANG_STORAGE_KEY);
    if (saved in TRANSLATIONS) return saved;
  } catch {}
  // "pt-BR" -> "pt"; languages without a translation fall back to English.
  const browserLang = navigator.language.toLowerCase().split("-")[0];
  return browserLang in TRANSLATIONS ? browserLang : "en";
}

let currentLang = detectLanguage();

// Returns the translation for key, with {name} placeholders filled from params.
function t(key, params = {}) {
  const text = TRANSLATIONS[currentLang][key] ?? TRANSLATIONS.en[key] ?? key;
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
  const label = LANGUAGES.find(l => l.code === currentLang)?.label ?? currentLang.toUpperCase();
  document.querySelectorAll(".lang-current").forEach(el => { el.textContent = label; });
  document.querySelectorAll("[data-lang]").forEach(btn => {
    btn.setAttribute("aria-checked", String(btn.dataset.lang === currentLang));
  });
}

// Switches the interface language and tells the page, so it can redraw
// text it builds itself (like the chat list), via a "languagechange" event.
function setLanguage(lang) {
  if (!(lang in TRANSLATIONS)) return;
  currentLang = lang;
  try { localStorage.setItem(LANG_STORAGE_KEY, lang); } catch {}
  applyTranslations();
  document.dispatchEvent(new CustomEvent("languagechange", { detail: lang }));
}

// ---------- language menu ----------

const LANG_CHECK_ICON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>';

// Builds every .lang-picker on the page: a globe button that opens a menu of languages.
function initLanguageMenus() {
  document.querySelectorAll(".lang-picker").forEach(picker => {
    const button = picker.querySelector(".lang-btn");
    const menu = picker.querySelector(".lang-menu");
    menu.replaceChildren(...LANGUAGES.map(lang => {
      const item = document.createElement("button");
      item.type = "button";
      item.setAttribute("role", "menuitemradio");
      item.dataset.lang = lang.code;
      item.innerHTML = `<span class="lang-name"></span><span class="lang-code"></span>${LANG_CHECK_ICON}`;
      item.querySelector(".lang-name").textContent = lang.name;
      item.querySelector(".lang-code").textContent = lang.label;
      item.addEventListener("click", () => {
        setLanguage(lang.code);
        close(true);
      });
      return item;
    }));

    const open = () => {
      menu.hidden = false;
      button.setAttribute("aria-expanded", "true");
      (menu.querySelector('[aria-checked="true"]') ?? menu.firstElementChild).focus();
    };
    const close = (returnFocus = false) => {
      if (menu.hidden) return;
      menu.hidden = true;
      button.setAttribute("aria-expanded", "false");
      if (returnFocus) button.focus();
    };

    button.addEventListener("click", () => (menu.hidden ? open() : close()));
    menu.addEventListener("keydown", e => {
      const items = [...menu.querySelectorAll("[data-lang]")];
      const index = items.indexOf(document.activeElement);
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        const step = e.key === "ArrowDown" ? 1 : -1;
        items[(index + step + items.length) % items.length].focus();
      } else if (e.key === "Escape" || e.key === "Tab") {
        close(e.key === "Escape");
      }
    });
    document.addEventListener("click", e => {
      if (!picker.contains(e.target)) close();
    });
  });
}

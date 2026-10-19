// Without a token there is nothing to show: go to the login page first.
if (!getToken()) goToLogin();

const BOT_ICON = '<svg width="20" height="20" viewBox="0 0 32 32" fill="none" aria-hidden="true"><path d="M5 14c2.6-2.4 5.2-2.4 7.8 0s5.2 2.4 7.8 0 3.9-1.6 5.6-.7" stroke="#E8956B" stroke-width="2.4" stroke-linecap="round"/><path d="M7 20.5c2.4-1.9 4.6-1.9 7 0s4.6 1.9 7 0" stroke="#7FB3A8" stroke-width="2.2" stroke-linecap="round"/></svg>';
const COPY_ICON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a1 1 0 0 1 1-1h10"/></svg>';
const MORE_ICON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="5" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/></svg>';
const EDIT_ICON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>';
const TRASH_ICON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>';

const welcome = document.getElementById("welcome");
const welcomeSlot = document.getElementById("welcomeSlot");
const scroll = document.getElementById("scroll");
const messages = document.getElementById("messages");
const dock = document.getElementById("dock");
const dockSlot = document.getElementById("dockSlot");
const chatTitle = document.getElementById("chatTitle");
const chatList = document.getElementById("chatList");
const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");
const deleteDialog = document.getElementById("deleteDialog");

welcomeSlot.appendChild(document.getElementById("composerTpl").content.cloneNode(true));
const form = document.getElementById("composer");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");

// All chats of the user, most recently active first.
let chats = [];
// Chat shown on screen; null means a new chat that isn't created until the first message.
let currentChatId = null;

// ---------- helpers ----------

// key is a translation key; it stays on the element so a language switch re-translates it.
function setStatus(ok, key) {
  statusDot.className = "status-dot " + (ok ? "ok" : "fail");
  statusText.dataset.i18n = key;
  statusText.textContent = t(key);
}

// ---------- welcome screen ----------
//
// The greeting, subtitle and input hints come from the phrase sets in
// greetings.js. A random mix is picked once per day, part of the day and
// language and cached in the browser, so it doesn't change every time a new
// chat is opened. Changes fade out and in.

// The version in the key drops greetings cached by older versions, such as
// ones written by a model before the phrase sets.
const GREETING_CACHE_PREFIX = "lagoa-greeting:v2:";
const HINTS_PER_GREETING = 6;
const HINT_INTERVAL_MS = 5000;
const FADE_MS = 300;

const greetingEl = document.getElementById("greeting");
const welcomeSubEl = document.querySelector(".welcome-sub");

let greetingKey = null;
let hints = [];
let hintIndex = 0;

function dayPeriod(hour = new Date().getHours()) {
  if (hour < 5 || hour >= 23) return "night";
  if (hour < 12) return "morning";
  if (hour < 18) return "day";
  return "evening";
}

function currentGreetingKey() {
  const now = new Date();
  const date = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`;
  return `${GREETING_CACHE_PREFIX}${date}:${dayPeriod()}:${currentLang}`;
}

// Built-in texts from the translations, for a language without phrase sets.
function setGreeting() {
  const key = { night: "greetingNight", morning: "greetingMorning", day: "greetingDay", evening: "greetingEvening" }[dayPeriod()];
  greetingEl.dataset.i18n = key;
  greetingEl.textContent = t(key);
  welcomeSubEl.dataset.i18n = "welcomeSub";
  welcomeSubEl.textContent = t("welcomeSub");
  input.dataset.i18nPlaceholder = "placeholder";
  input.placeholder = t("placeholder");
  hints = [];
}

function fadeText(el, text) {
  if (el.textContent === text) return;
  el.classList.add("is-fading");
  setTimeout(() => {
    el.textContent = text;
    el.classList.remove("is-fading");
  }, FADE_MS);
}

function randomItem(items) {
  return items[Math.floor(Math.random() * items.length)];
}

function randomSample(items, count) {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy.slice(0, count);
}

function pickGreeting(lang, period) {
  const set = GREETINGS[lang];
  return {
    title: randomItem(set.titles[period]),
    subtitle: randomItem(set.subtitles),
    hints: randomSample(set.hints, HINTS_PER_GREETING),
  };
}

function applyGreeting(data) {
  // These texts replace the translated ones, so a language switch mustn't
  // overwrite them; it picks a greeting in the new language instead.
  delete greetingEl.dataset.i18n;
  delete welcomeSubEl.dataset.i18n;
  delete input.dataset.i18nPlaceholder;
  fadeText(greetingEl, data.title);
  fadeText(welcomeSubEl, data.subtitle);
  hints = data.hints;
  hintIndex = -1;
  showNextHint();
}

function readCachedGreeting(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function cacheGreeting(key, data) {
  try {
    // Greetings from earlier parts of the day are no longer needed; other
    // languages for the current one are kept for switching back.
    const period = key.slice(0, key.lastIndexOf(":") + 1);
    Object.keys(localStorage)
      .filter(k => k.startsWith("lagoa-greeting:") && !k.startsWith(period))
      .forEach(k => localStorage.removeItem(k));
    localStorage.setItem(key, JSON.stringify(data));
  } catch {}
}

// Shows the greeting for the current part of the day, picking a new one if it isn't cached yet.
function updateGreeting() {
  const key = currentGreetingKey();
  if (key === greetingKey) return;
  greetingKey = key;
  if (!(currentLang in GREETINGS)) {
    setGreeting();
    return;
  }
  let data = readCachedGreeting(key);
  if (!data) {
    data = pickGreeting(currentLang, dayPeriod());
    cacheGreeting(key, data);
  }
  applyGreeting(data);
}

// Swaps the input placeholder to the next hint with a fade out and in.
function showNextHint() {
  if (!hints.length) return;
  hintIndex = (hintIndex + 1) % hints.length;
  input.classList.add("hint-fading");
  setTimeout(() => {
    input.placeholder = hints[hintIndex];
    input.classList.remove("hint-fading");
  }, FADE_MS);
}

setInterval(() => {
  // Only while the hint is visible: an empty input, not mid-typing.
  if (!input.value) showNextHint();
}, HINT_INTERVAL_MS);

function showChat() {
  welcome.hidden = true;
  scroll.hidden = false;
  dock.hidden = false;
  dockSlot.appendChild(form);
}

function showWelcome() {
  welcome.hidden = false;
  scroll.hidden = true;
  dock.hidden = true;
  welcomeSlot.appendChild(form);
}

function scrollToBottom() {
  scroll.scrollTop = scroll.scrollHeight;
}

function closeDrawer() {
  document.body.classList.remove("menu-open");
}

function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Минимальный markdown: блоки кода, инлайн-код, заголовки, списки, жирный, курсив.
function renderMarkdown(text) {
  const blocks = [];
  text = text.replace(/```[^\n]*\n([\s\S]*?)```/g, (_, code) => {
    blocks.push("<pre><code>" + escapeHtml(code.replace(/\n$/, "")) + "</code></pre>");
    return "\u0000" + (blocks.length - 1) + "\u0000";
  });

  const inline = s => escapeHtml(s)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*\s][^*]*?)\*/g, "$1<em>$2</em>");

  const out = [];
  let list = null;
  let para = [];
  const flushPara = () => { if (para.length) { out.push("<p>" + para.join("<br>") + "</p>"); para = []; } };
  const flushList = () => { if (list) { out.push(`<${list.tag}>${list.items.join("")}</${list.tag}>`); list = null; } };

  for (const line of text.split("\n")) {
    const block = line.match(/^\u0000(\d+)\u0000$/);
    const heading = line.match(/^#{1,6}\s+(.*)$/);
    const ul = line.match(/^\s*[-*]\s+(.*)$/);
    const ol = line.match(/^\s*\d+[.)]\s+(.*)$/);

    if (block) { flushPara(); flushList(); out.push(blocks[+block[1]]); }
    else if (heading) { flushPara(); flushList(); out.push("<h4>" + inline(heading[1]) + "</h4>"); }
    else if (ul || ol) {
      flushPara();
      const tag = ul ? "ul" : "ol";
      if (!list || list.tag !== tag) { flushList(); list = { tag, items: [] }; }
      list.items.push("<li>" + inline((ul || ol)[1]) + "</li>");
    }
    else if (!line.trim()) { flushPara(); flushList(); }
    else { flushList(); para.push(inline(line)); }
  }
  flushPara(); flushList();
  return out.join("");
}

// ---------- messages ----------

function addUserMessage(text) {
  const el = document.createElement("div");
  el.className = "msg-user";
  el.textContent = text;
  messages.appendChild(el);
  scrollToBottom();
}

function botShell() {
  const el = document.createElement("article");
  el.className = "msg-bot";
  el.innerHTML = `<div class="avatar">${BOT_ICON}</div><div class="bot-body"></div>`;
  messages.appendChild(el);
  return el;
}

function fillBotMessage(el, text) {
  const body = el.querySelector(".bot-body");
  body.innerHTML = `
    <div class="bot-name">Lagoa</div>
    <div class="bot-text">${renderMarkdown(text)}</div>
    <div class="bot-actions"><button type="button">${COPY_ICON}<span data-i18n="copy">${t("copy")}</span></button></div>`;
  const copyBtn = body.querySelector(".bot-actions button");
  copyBtn.addEventListener("click", async () => {
    const label = copyBtn.querySelector("span");
    try {
      await navigator.clipboard.writeText(text);
      label.textContent = t("copied");
    } catch {
      label.textContent = t("copyFailed");
    }
    setTimeout(() => { label.textContent = t("copy"); }, 1500);
  });
}

function addBotMessage(text) {
  const el = botShell();
  fillBotMessage(el, text);
  scrollToBottom();
  return el;
}

// ---------- quick replies ----------

function clearQuickReplies() {
  messages.querySelectorAll(".quick-replies").forEach(el => el.remove());
}

// Asks for short replies to the chat's last answer and shows them as buttons
// under it. The answer is already on screen; the buttons appear when ready.
async function loadQuickReplies(chatId, botEl) {
  try {
    const res = await apiFetch(`/chats/${chatId}/suggestions`);
    if (!res.ok) return;
    const { suggestions } = await res.json();
    // Skip if the user has switched chats or already sent another message.
    if (!suggestions.length || currentChatId !== chatId || messages.lastElementChild !== botEl) return;
    clearQuickReplies();
    const box = document.createElement("div");
    box.className = "quick-replies";
    for (const text of suggestions) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = text;
      btn.addEventListener("click", () => submitPrompt(text));
      box.appendChild(btn);
    }
    botEl.querySelector(".bot-body").appendChild(box);
    const nearBottom = scroll.scrollHeight - scroll.scrollTop - scroll.clientHeight < 120;
    if (nearBottom) scrollToBottom();
  } catch (e) {
    console.error(e);
  }
}

function addThinking() {
  const el = document.createElement("div");
  el.className = "thinking";
  el.innerHTML = `<div class="avatar">${BOT_ICON}</div><div class="dots" aria-hidden="true"><span></span><span></span><span></span></div><span data-i18n="thinking">${t("thinking")}</span>`;
  messages.appendChild(el);
  scrollToBottom();
  return el;
}

function addError(text) {
  const el = botShell();
  el.querySelector(".bot-body").innerHTML = `<div class="bot-name">Lagoa</div><div class="msg-error"></div>`;
  el.querySelector(".msg-error").textContent = text;
  scrollToBottom();
}

// ---------- model picker ----------

const MODEL_STORAGE_KEY = "lagoa-model";
const PROVIDER_NAMES = { groq: "Groq", gemini: "Google Gemini" };
const CHECK_ICON = '<svg class="model-option-check" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>';

const modelPicker = document.getElementById("modelPicker");
const modelBtn = document.getElementById("modelBtn");
const modelName = document.getElementById("modelName");
const modelMenu = document.getElementById("modelMenu");

let models = [];
let selectedModelId = null;

function selectModel(id) {
  const model = models.find(m => m.id === id);
  if (!model) return;
  selectedModelId = id;
  modelName.textContent = model.name;
  modelBtn.setAttribute("aria-label", `${t("modelLabel")}: ${model.name}`);
  modelMenu.querySelectorAll(".model-option").forEach(li => {
    li.setAttribute("aria-selected", String(li.dataset.id === id));
  });
  try { localStorage.setItem(MODEL_STORAGE_KEY, id); } catch {}
}

function renderModelMenu() {
  modelMenu.replaceChildren(...models.map(m => {
    const li = document.createElement("li");
    li.className = "model-option";
    li.setAttribute("role", "option");
    li.tabIndex = -1;
    li.dataset.id = m.id;
    li.innerHTML = `<span class="model-option-text"><span class="model-option-name"></span><span class="model-option-provider"></span></span>${CHECK_ICON}`;
    li.querySelector(".model-option-name").textContent = m.name;
    li.querySelector(".model-option-provider").textContent = m.provider === "ollama" ? t("ollamaProvider") : PROVIDER_NAMES[m.provider] ?? m.provider;
    li.addEventListener("click", () => {
      selectModel(m.id);
      closeModelMenu(true);
    });
    return li;
  }));
}

function openModelMenu() {
  modelMenu.hidden = false;
  modelBtn.setAttribute("aria-expanded", "true");
  const current = modelMenu.querySelector('[aria-selected="true"]') ?? modelMenu.firstElementChild;
  current?.focus();
}

function closeModelMenu(returnFocus = false) {
  if (modelMenu.hidden) return;
  modelMenu.hidden = true;
  modelBtn.setAttribute("aria-expanded", "false");
  if (returnFocus) modelBtn.focus();
}

modelBtn.addEventListener("click", () => {
  if (modelMenu.hidden) openModelMenu();
  else closeModelMenu();
});

modelMenu.addEventListener("keydown", e => {
  const options = [...modelMenu.querySelectorAll(".model-option")];
  const index = options.indexOf(document.activeElement);
  if (e.key === "ArrowDown" || e.key === "ArrowUp") {
    e.preventDefault();
    const step = e.key === "ArrowDown" ? 1 : -1;
    options[(index + step + options.length) % options.length].focus();
  } else if ((e.key === "Enter" || e.key === " ") && index >= 0) {
    e.preventDefault();
    options[index].click();
  } else if (e.key === "Escape" || e.key === "Tab") {
    closeModelMenu(e.key === "Escape");
  }
});

// Loads the available models; the last picked one is remembered in the browser.
async function loadModels() {
  try {
    const res = await apiFetch("/models");
    if (!res.ok) return;
    const data = await res.json();
    models = data.models;
    if (models.length === 0) return;
    let saved = null;
    try { saved = localStorage.getItem(MODEL_STORAGE_KEY); } catch {}
    renderModelMenu();
    selectModel(models.some(m => m.id === saved) ? saved : data.default);
    modelPicker.hidden = false;
  } catch (e) {
    console.error(e);
  }
}

// ---------- chat list ----------

function chatTitleText(chat) {
  return chat?.title ?? t("newConversation");
}

// Groups chats by how long ago they were active: today, yesterday, this week, earlier.
function groupKey(chat) {
  const startOfToday = new Date();
  startOfToday.setHours(0, 0, 0, 0);
  const day = 24 * 60 * 60 * 1000;
  const updated = new Date(chat.updated_at).getTime();
  if (updated >= startOfToday.getTime()) return "today";
  if (updated >= startOfToday.getTime() - day) return "yesterday";
  if (updated >= startOfToday.getTime() - 6 * day) return "thisWeek";
  return "earlier";
}

function renderChatList() {
  chatList.replaceChildren();
  let lastGroup = null;
  for (const chat of chats) {
    const group = groupKey(chat);
    if (group !== lastGroup) {
      const label = document.createElement("div");
      label.className = "chat-list-label";
      label.dataset.i18n = group;
      label.textContent = t(group);
      chatList.appendChild(label);
      lastGroup = group;
    }
    chatList.appendChild(renderChatItem(chat));
  }
  updateTitle();
}

function renderChatItem(chat) {
  const item = document.createElement("div");
  item.className = "chat-item";
  item.dataset.id = chat.id;
  if (chat.id === currentChatId) item.setAttribute("aria-current", "true");
  item.innerHTML = `
    <button type="button" class="chat-link"></button>
    <button type="button" class="chat-more" aria-haspopup="menu" aria-expanded="false" data-i18n-aria-label="chatActions" aria-label="${t("chatActions")}">${MORE_ICON}</button>
    <div class="chat-menu" role="menu" hidden>
      <button type="button" role="menuitem" data-action="rename">${EDIT_ICON}<span data-i18n="rename">${t("rename")}</span></button>
      <button type="button" role="menuitem" data-action="delete" class="danger">${TRASH_ICON}<span data-i18n="delete">${t("delete")}</span></button>
    </div>`;
  const link = item.querySelector(".chat-link");
  link.textContent = chatTitleText(chat);
  link.title = chatTitleText(chat);
  link.addEventListener("click", () => openChat(chat.id));

  const moreBtn = item.querySelector(".chat-more");
  moreBtn.addEventListener("click", e => {
    e.stopPropagation();
    toggleChatMenu(item);
  });
  item.querySelector('[data-action="rename"]').addEventListener("click", () => {
    closeChatMenus();
    startRename(item, chat);
  });
  item.querySelector('[data-action="delete"]').addEventListener("click", () => {
    closeChatMenus();
    confirmDelete(chat);
  });
  return item;
}

function closeChatMenus() {
  chatList.querySelectorAll(".chat-menu:not([hidden])").forEach(menu => {
    menu.hidden = true;
    menu.closest(".chat-item").querySelector(".chat-more").setAttribute("aria-expanded", "false");
  });
}

function toggleChatMenu(item) {
  const menu = item.querySelector(".chat-menu");
  const wasOpen = !menu.hidden;
  closeChatMenus();
  if (wasOpen) return;
  const moreBtn = item.querySelector(".chat-more");
  menu.hidden = false;
  moreBtn.setAttribute("aria-expanded", "true");
  // The list scrolls and would clip an absolutely positioned menu, so the
  // menu is fixed to the viewport and placed under the button.
  const rect = moreBtn.getBoundingClientRect();
  const left = Math.max(8, rect.right - menu.offsetWidth);
  const top = rect.bottom + 4 + menu.offsetHeight > window.innerHeight
    ? rect.top - 4 - menu.offsetHeight
    : rect.bottom + 4;
  menu.style.left = `${left}px`;
  menu.style.top = `${top}px`;
  menu.querySelector("button").focus();
}

function updateTitle() {
  const chat = chats.find(c => c.id === currentChatId);
  if (chat) {
    delete chatTitle.dataset.i18n;
    chatTitle.textContent = chatTitleText(chat);
  } else {
    chatTitle.dataset.i18n = "newChat";
    chatTitle.textContent = t("newChat");
  }
}

// Puts a chat at the top of the list with its latest data from the server.
function upsertChat(chat) {
  chats = [chat, ...chats.filter(c => c.id !== chat.id)];
  renderChatList();
}

async function loadChats() {
  const res = await apiFetch("/chats");
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  chats = await res.json();
  renderChatList();
}

// ---------- rename and delete ----------

function startRename(item, chat) {
  const link = item.querySelector(".chat-link");
  const field = document.createElement("input");
  field.className = "chat-rename";
  field.value = chat.title ?? "";
  field.maxLength = 100;
  field.setAttribute("aria-label", t("rename"));
  link.replaceWith(field);
  item.classList.add("renaming");
  field.focus();
  field.select();

  let done = false;
  const finish = async save => {
    if (done) return;
    done = true;
    const title = field.value.trim();
    if (!save || !title || title === chat.title) {
      renderChatList();
      return;
    }
    try {
      const res = await apiFetch(`/chats/${chat.id}`, {
        method: "PATCH",
        body: JSON.stringify({ title }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const updated = await res.json();
      chats = chats.map(c => c.id === updated.id ? updated : c);
    } catch (e) {
      console.error(e);
      setStatus(false, "requestFailed");
    }
    renderChatList();
  };
  field.addEventListener("keydown", e => {
    if (e.key === "Enter") { e.preventDefault(); finish(true); }
    if (e.key === "Escape") { e.preventDefault(); finish(false); }
  });
  field.addEventListener("blur", () => finish(true));
}

// Chat waiting for confirmation in the delete dialog.
let chatToDelete = null;

function confirmDelete(chat) {
  chatToDelete = chat;
  document.getElementById("deleteChatName").textContent = chatTitleText(chat);
  deleteDialog.showModal();
  document.getElementById("deleteCancel").focus();
}

async function deleteConfirmedChat() {
  const chat = chatToDelete;
  chatToDelete = null;
  deleteDialog.close();
  if (!chat) return;
  try {
    const res = await apiFetch(`/chats/${chat.id}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    chats = chats.filter(c => c.id !== chat.id);
    if (chat.id === currentChatId) startNewChat();
    else renderChatList();
  } catch (e) {
    console.error(e);
    setStatus(false, "requestFailed");
  }
}

document.getElementById("deleteConfirm").addEventListener("click", deleteConfirmedChat);
document.getElementById("deleteCancel").addEventListener("click", () => {
  chatToDelete = null;
  deleteDialog.close();
});

// ---------- navigation ----------

function setHash(chatId) {
  const hash = chatId ? `#chat-${chatId}` : "";
  if (location.hash !== hash) history.replaceState(null, "", hash || location.pathname);
}

function startNewChat() {
  currentChatId = null;
  setHash(null);
  messages.replaceChildren();
  showWelcome();
  // The part of the day may have changed since the page was opened.
  updateGreeting();
  renderChatList();
  closeDrawer();
  input.focus();
}

async function openChat(chatId) {
  currentChatId = chatId;
  setHash(chatId);
  renderChatList();
  closeDrawer();
  messages.replaceChildren();
  showChat();
  try {
    const res = await apiFetch(`/chats/${chatId}/messages`);
    if (res.status === 404) {
      chats = chats.filter(c => c.id !== chatId);
      startNewChat();
      return;
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const items = await res.json();
    if (currentChatId !== chatId) return;
    if (items.length === 0) {
      showWelcome();
      return;
    }
    let lastBot = null;
    for (const item of items) {
      addUserMessage(item.promt);
      lastBot = addBotMessage(item.response);
    }
    scrollToBottom();
    loadQuickReplies(chatId, lastBot);
    input.focus();
  } catch (e) {
    console.error(e);
    setStatus(false, "requestFailed");
  }
}

// ---------- sending ----------

async function sendPrompt(prompt) {
  clearQuickReplies();
  showChat();
  addUserMessage(prompt);
  const thinking = addThinking();
  sendBtn.disabled = true;

  try {
    // A new chat is created on the server only when its first message is sent.
    if (currentChatId === null) {
      const res = await apiFetch("/chats", { method: "POST" });
      if (!res.ok) throw new Error(t("serverError", { status: res.status }));
      const chat = await res.json();
      currentChatId = chat.id;
      setHash(chat.id);
      upsertChat(chat);
    }
    const chatId = currentChatId;
    const res = await apiFetch(`/chats/${chatId}/messages`, {
      method: "POST",
      body: JSON.stringify({ prompt, model: selectedModelId }),
    });
    if (!res.ok) throw new Error(t("serverError", { status: res.status }));
    const data = await res.json();
    upsertChat(data.chat);
    thinking.remove();
    // The user may have switched to another chat while waiting for the answer.
    if (currentChatId === chatId) loadQuickReplies(chatId, addBotMessage(data.answer ?? ""));
    setStatus(true, "apiConnected");
  } catch (e) {
    thinking.remove();
    addError(e instanceof TypeError ? t("networkError") : e.message);
    setStatus(false, "requestFailed");
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

// ---------- events ----------

function autoResize() {
  input.style.height = "auto";
  input.style.height = input.scrollHeight + "px";
}

function submitPrompt(text) {
  const prompt = text.trim();
  if (!prompt || sendBtn.disabled) return;
  input.value = "";
  autoResize();
  sendPrompt(prompt);
}

input.addEventListener("input", autoResize);
input.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    submitPrompt(input.value);
  }
});
form.addEventListener("submit", e => {
  e.preventDefault();
  submitPrompt(input.value);
});

document.querySelectorAll(".suggestion").forEach(btn => {
  btn.addEventListener("click", () => submitPrompt(btn.dataset.prompt));
});

// The chat list builds its own labels, so it's redrawn in the new language.
document.addEventListener("languagechange", () => {
  renderChatList();
  greetingKey = null;
  updateGreeting();
});

document.getElementById("newChatBtn").addEventListener("click", startNewChat);
document.getElementById("newChatMobileBtn").addEventListener("click", startNewChat);
document.getElementById("logoutBtn").addEventListener("click", goToLogin);

document.getElementById("menuBtn").addEventListener("click", () => document.body.classList.add("menu-open"));
document.getElementById("backdrop").addEventListener("click", closeDrawer);

document.addEventListener("click", e => {
  if (!modelPicker.contains(e.target)) closeModelMenu();
  if (!e.target.closest(".chat-item")) closeChatMenus();
});
document.addEventListener("keydown", e => {
  if (e.key === "Escape") closeChatMenus();
});
chatList.addEventListener("scroll", closeChatMenus);
window.addEventListener("resize", closeChatMenus);

// Opens the chat named in the address (#chat-12), or a new chat if there is none.
function openChatFromHash() {
  const id = Number(location.hash.match(/^#chat-(\d+)$/)?.[1]);
  if (chats.some(c => c.id === id)) {
    if (id !== currentChatId) openChat(id);
  } else {
    startNewChat();
  }
}

window.addEventListener("hashchange", openChatFromHash);

async function init() {
  initLanguageMenus();
  applyTranslations();
  loadUser();
  updateGreeting();
  loadModels();
  try {
    await loadChats();
    setStatus(true, "apiConnected");
  } catch (e) {
    console.error(e);
    setStatus(false, "apiUnavailable");
  }
  openChatFromHash();
}

async function loadUser() {
  try {
    const res = await apiFetch("/auth/me");
    if (!res.ok) return;
    const user = await res.json();
    document.getElementById("userName").textContent = user.login;
    document.getElementById("userAvatar").textContent = user.login.charAt(0);
  } catch (e) {
    console.error(e);
  }
}

init();

const API_URL = "http://localhost:8000";

const BOT_ICON = '<svg width="20" height="20" viewBox="0 0 32 32" fill="none" aria-hidden="true"><path d="M5 14c2.6-2.4 5.2-2.4 7.8 0s5.2 2.4 7.8 0 3.9-1.6 5.6-.7" stroke="#E8956B" stroke-width="2.4" stroke-linecap="round"/><path d="M7 20.5c2.4-1.9 4.6-1.9 7 0s4.6 1.9 7 0" stroke="#7FB3A8" stroke-width="2.2" stroke-linecap="round"/></svg>';
const COPY_ICON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a1 1 0 0 1 1-1h10"/></svg>';

const welcome = document.getElementById("welcome");
const welcomeSlot = document.getElementById("welcomeSlot");
const scroll = document.getElementById("scroll");
const messages = document.getElementById("messages");
const dock = document.getElementById("dock");
const dockSlot = document.getElementById("dockSlot");
const chatTitle = document.getElementById("chatTitle");
const chatItem = document.getElementById("chatItem");
const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");

welcomeSlot.appendChild(document.getElementById("composerTpl").content.cloneNode(true));
const form = document.getElementById("composer");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");

let isChatMode = false;
let titleSet = false;

// ---------- helpers ----------

// key is a translation key; it stays on the element so a language switch re-translates it.
function setStatus(ok, key) {
  statusDot.className = "status-dot " + (ok ? "ok" : "fail");
  statusText.dataset.i18n = key;
  statusText.textContent = t(key);
}

function setGreeting() {
  const h = new Date().getHours();
  const key = h < 5 ? "greetingNight" : h < 12 ? "greetingMorning" : h < 18 ? "greetingDay" : "greetingEvening";
  const greeting = document.getElementById("greeting");
  greeting.dataset.i18n = key;
  greeting.textContent = t(key);
}

function setTitle(firstPrompt) {
  if (titleSet) return;
  titleSet = true;
  const oneLine = firstPrompt.replace(/\s+/g, " ").trim();
  const title = oneLine.length > 48 ? oneLine.slice(0, 48) + "…" : oneLine;
  chatTitle.textContent = title;
  delete chatItem.dataset.i18n;
  chatItem.textContent = title;
}

function showChat() {
  if (isChatMode) return;
  isChatMode = true;
  welcome.hidden = true;
  scroll.hidden = false;
  dock.hidden = false;
  input.rows = 2;
  dockSlot.appendChild(form);
}

function showWelcome() {
  welcome.hidden = false;
  scroll.hidden = true;
  dock.hidden = true;
}

function scrollToBottom() {
  scroll.scrollTop = scroll.scrollHeight;
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
  fillBotMessage(botShell(), text);
  scrollToBottom();
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

// ---------- API ----------

async function loadHistory() {
  try {
    const res = await fetch(`${API_URL}/requests`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const items = await res.json();
    setStatus(true, "apiConnected");
    if (items.length === 0) {
      showWelcome();
      return;
    }
    showChat();
    setTitle(items[0].promt);
    for (const item of items) {
      addUserMessage(item.promt);
      addBotMessage(item.response);
    }
    scrollToBottom();
  } catch (e) {
    console.error(e);
    setStatus(false, "apiUnavailable");
    showWelcome();
  }
}

async function sendPrompt(prompt) {
  showChat();
  setTitle(prompt);
  addUserMessage(prompt);
  const thinking = addThinking();
  sendBtn.disabled = true;

  try {
    const res = await fetch(`${API_URL}/requests`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    if (!res.ok) throw new Error(t("serverError", { status: res.status }));
    const data = await res.json();
    thinking.remove();
    addBotMessage(data.answer ?? "");
    setStatus(true, "apiConnected");
  } catch (e) {
    thinking.remove();
    addError(e instanceof TypeError
      ? t("networkError")
      : e.message);
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

document.querySelectorAll("[data-lang]").forEach(btn => {
  btn.addEventListener("click", () => setLanguage(btn.dataset.lang));
});

document.getElementById("menuBtn").addEventListener("click", () => document.body.classList.add("menu-open"));
document.getElementById("backdrop").addEventListener("click", () => document.body.classList.remove("menu-open"));

applyTranslations();
setGreeting();
input.focus();
loadHistory();

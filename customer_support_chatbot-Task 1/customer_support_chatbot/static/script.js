const messages = document.getElementById("messages");
const form = document.getElementById("form");
const input = document.getElementById("text");
const quick = document.getElementById("quick");
const sendBtn = form.querySelector("button");

const botIcon =
  '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 14v-2a9 9 0 0 1 18 0v2"/><path d="M21 15a2 2 0 0 1-2 2h-1v-5h1a2 2 0 0 1 2 2z"/><path d="M3 15a2 2 0 0 0 2 2h1v-5H5a2 2 0 0 0-2 2z"/></svg>';

function timeNow() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function scrollDown() {
  messages.scrollTop = messages.scrollHeight;
}

function addMessage(text, who) {
  const row = document.createElement("div");
  row.className = "row " + who;

  if (who === "bot") {
    const mini = document.createElement("div");
    mini.className = "mini";
    mini.innerHTML = botIcon;
    row.appendChild(mini);
  }

  const col = document.createElement("div");
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  const time = document.createElement("div");
  time.className = "time";
  time.textContent = timeNow();
  col.appendChild(bubble);
  col.appendChild(time);
  row.appendChild(col);

  messages.appendChild(row);
  scrollDown();
}

function showTyping() {
  const row = document.createElement("div");
  row.className = "row bot";
  row.id = "typing";
  row.innerHTML = '<div class="mini">' + botIcon + '</div><div class="bubble typing"><i></i><i></i><i></i></div>';
  messages.appendChild(row);
  scrollDown();
}

function hideTyping() {
  const t = document.getElementById("typing");
  if (t) t.remove();
}

function send(text) {
  text = text.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";
  quick.style.display = "none";
  sendBtn.disabled = true;
  showTyping();

  const wait = new Promise((r) => setTimeout(r, 600));
  const request = fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text }),
  }).then((r) => r.json());

  Promise.all([request, wait])
    .then(([data]) => {
      hideTyping();
      addMessage(data.reply || data.error, "bot");
    })
    .catch(() => {
      hideTyping();
      addMessage("Sorry, I could not reach the server. Please try again.", "bot");
    })
    .finally(() => {
      sendBtn.disabled = false;
      input.focus();
    });
}

function welcome() {
  addMessage("Hello! Welcome to customer support. How can I help you today?", "bot");
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  send(input.value);
});

document.querySelectorAll("[data-q]").forEach((btn) => {
  btn.addEventListener("click", () => {
    send(btn.dataset.q);
    document.getElementById("chat").scrollIntoView({ behavior: "smooth", block: "center" });
  });
});

document.getElementById("clear").addEventListener("click", () => {
  fetch("/reset", { method: "POST" });
  messages.innerHTML = "";
  quick.style.display = "flex";
  welcome();
});

welcome();

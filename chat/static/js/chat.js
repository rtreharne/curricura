function getCSRFToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function appendBubble({ text, sender = "ai" }) {
  const bubble = document.createElement("div");
  const classes = {
    ai: "max-w-[60%] bg-gray-100 text-gray-800 px-4 py-3 rounded-xl shadow-sm",
    user: "flex justify-end"
  };

  if (sender === "user") {
    bubble.className = classes.user;
    bubble.innerHTML = `
      <div class="max-w-[60%] bg-indigo-600 text-white px-4 py-3 rounded-xl shadow-sm text-right">
        ${text}
      </div>`;
  } else {
    bubble.className = classes.ai;
    bubble.innerText = text;
  }

  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function appendThinkingPlaceholder() {
  const existing = document.getElementById("ai-thinking-placeholder");
  if (existing) existing.remove();

  const loader = document.createElement("div");
  loader.id = "ai-thinking-placeholder";
  loader.className = "w-full flex mb-4";
  loader.innerHTML = `
    <div class="bg-gray-100 text-gray-600 px-4 py-3 rounded-xl shadow-sm w-3/5 animate-pulse flex items-center space-x-2">
      <svg class="w-5 h-5 text-indigo-500 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
      </svg>
      <span>Thinking...</span>
    </div>`;
  chatWindow.appendChild(loader);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

document.addEventListener("DOMContentLoaded", function () {
  const chatWindow = document.getElementById("chatWindow");
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");

  // Autofocus input
  chatInput.focus();

  // Show welcome message after brief loader
  const initialMessage = document.getElementById("initialInstruction")?.dataset?.message;
  if (initialMessage) {
    setTimeout(() => {
      const aiThinking = document.getElementById("ai-thinking-placeholder");
      if (aiThinking) aiThinking.remove();
      appendBubble({ text: initialMessage, sender: "ai" });
    }, 1000);
  } else {
    const aiThinking = document.getElementById("ai-thinking-placeholder");
    if (aiThinking) aiThinking.remove();
  }

  chatForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const userText = chatInput.value.trim();
    if (!userText) return;

    appendBubble({ text: userText, sender: "user" });
    chatInput.value = "";

    appendThinkingPlaceholder();

    try {
      const response = await fetch("/chat/ai_chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({ query: userText })
      });

      const data = await response.json();

      const aiThinking = document.getElementById("ai-thinking-placeholder");
      if (aiThinking) aiThinking.remove();

      appendBubble({ text: data.answer, sender: "ai" });

    } catch (error) {
      const aiThinking = document.getElementById("ai-thinking-placeholder");
      if (aiThinking) aiThinking.remove();

      appendBubble({ text: "⚠️ Error: Unable to get response from AI.", sender: "ai" });
    }
  });
});

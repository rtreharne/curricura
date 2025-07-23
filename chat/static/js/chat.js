function getCSRFToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function convertTimestampToSeconds(timestamp) {
  const parts = timestamp.split(":").map(Number);
  if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
  if (parts.length === 2) return parts[0] * 60 + parts[1];
  return parseInt(parts[0], 10) || 0;
}

function formatDate(dateString) {
  if (!dateString) return "";
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch (e) {
    return dateString;
  }
}

function buildSourceCard(src) {
  const type = src.type || "Source";
  const link = src.link || "";
  const timestamp = src.timestamp || "";
  const filename = src.filename || "";
  const courseName = src.course || "";
  const date = src.date || "";
  const textSnippet =
    (src.text || "").slice(0, 180) +
    ((src.text || "").length > 180 ? "..." : "");

  const badgeClass =
    type === "Transcript"
      ? "bg-indigo-100 text-indigo-700"
      : type === "Canvas"
      ? "bg-green-100 text-green-700"
      : "bg-yellow-100 text-yellow-700";

  let href = "";
  if (link) {
    href =
      link +
      (type === "Transcript" && timestamp
        ? `&t=${convertTimestampToSeconds(timestamp)}`
        : "");
  }

  const card = href ? document.createElement("a") : document.createElement("div");
  card.className =
    "block border border-gray-200 rounded-2xl p-4 bg-white shadow-sm text-sm hover:shadow-md transition hover:bg-gray-50";
  if (href) {
    card.href = href;
    card.target = "_blank";
  }

  let footerHTML = "";
  if (type === "Transcript") {
    footerHTML = `
      <div class="text-xs text-gray-400 mt-4 flex justify-between">
        <span>
          ${link ? `<span class="text-indigo-600 hover:underline">View Transcript</span>` : ""}
          ${timestamp ? ` @ ${timestamp}` : ""}
        </span>
        ${date ? `<span class="text-gray-500">📅 ${formatDate(date)}</span>` : ""}
      </div>`;
  } else if (type === "Canvas") {
    footerHTML = `
      <div class="text-xs text-gray-400 mt-4 flex justify-between">
        <span>${filename ? `📄 ${filename}` : ""}</span>
      </div>`;
  }

  card.innerHTML = `
    <div class="flex justify-between items-start text-xs text-gray-500 mb-2">
      <span class="font-medium text-gray-800">${courseName || ""}</span>
      <span class="px-2 py-0.5 rounded-full ${badgeClass} text-xs">${type}</span>
    </div>
    <p class="text-gray-700 leading-relaxed">“${textSnippet}”</p>
    ${footerHTML}
  `;

  return card;
}

function appendBubble({ text, sender = "ai", sources = [] }) {
  const wrapper = document.createElement("div");
  wrapper.className = sender === "user" ? "flex justify-end" : "flex flex-col";

  if (sender === "user") {
    wrapper.innerHTML = `
      <div class="max-w-[80%] bg-indigo-600 text-white px-4 py-3 rounded-xl shadow-sm text-right">
        ${text}
      </div>`;
  } else {
    const aiBubble = document.createElement("div");
    aiBubble.className =
      "max-w-[80%] bg-gray-100 text-gray-800 px-4 py-3 rounded-xl shadow-sm whitespace-pre-wrap";
    aiBubble.innerText = text;
    wrapper.appendChild(aiBubble);

    if (sources.length > 0) {
      const toggleBtn = document.createElement("button");
      toggleBtn.className =
        "mt-2 max-w-[80%] px-3 py-1.5 bg-gray-200 text-gray-700 text-xs font-medium rounded-xl shadow hover:bg-gray-300 transition";
      toggleBtn.innerHTML = `
        <svg class="w-4 h-4 mr-1 inline" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"></path>
        </svg>
        Show Sources
      `;

      const sourceContainer = document.createElement("div");
      sourceContainer.className = "mt-3 max-w-[80%] space-y-4 hidden";

      toggleBtn.addEventListener("click", () => {
        const isHidden = sourceContainer.classList.contains("hidden");
        if (isHidden) {
          sourceContainer.classList.remove("hidden");
          toggleBtn.innerHTML = `
            <svg class="w-4 h-4 mr-1 inline" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M20 12H4"></path>
            </svg>
            Hide Sources
          `;
        } else {
          sourceContainer.classList.add("hidden");
          toggleBtn.innerHTML = `
            <svg class="w-4 h-4 mr-1 inline" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"></path>
            </svg>
            Show Sources
          `;
        }
      });

      sources.forEach((src) => {
        const card = buildSourceCard(src);
        sourceContainer.appendChild(card);
      });

      wrapper.appendChild(toggleBtn);
      wrapper.appendChild(sourceContainer);
    }
  }

  chatWindow.appendChild(wrapper);
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
  window.chatWindow = document.getElementById("chatWindow");
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");

  chatInput.focus();

  const initialMessage =
    document.getElementById("initialInstruction")?.dataset?.message;
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

    // Check toggle state
    const expansive = document.getElementById("expansiveToggle")?.checked || false;

    try {
      const response = await fetch("/chat/ai_chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({
        query: userText,
        expansive: expansive,
        course_id: window.courseId || null,
      }),

      });

      const data = await response.json();

      // Remove "Thinking..." placeholder
      const aiThinking = document.getElementById("ai-thinking-placeholder");
      if (aiThinking) aiThinking.remove();

      // Append AI answer
      appendBubble({
        text: data.answer,
        sender: "ai",
        sources: data.sources || [],
      });

    } catch (error) {
      const aiThinking = document.getElementById("ai-thinking-placeholder");
      if (aiThinking) aiThinking.remove();

      appendBubble({
        text: "⚠️ Error: Unable to get response from AI.",
        sender: "ai",
      });
    }
  });

});

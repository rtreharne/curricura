document.addEventListener("DOMContentLoaded", function () {
  // Smooth scroll if on homepage
  if (window.location.pathname === "/" || window.location.pathname === "/index.html") {
    document.querySelectorAll(".scroll-link").forEach(link => {
      link.addEventListener("click", function (e) {
        const href = this.getAttribute("href");
        if (href && href.startsWith("/#")) {
          e.preventDefault();
          const targetId = href.split("#")[1];
          const targetEl = document.getElementById(targetId);
          if (targetEl) {
            window.scrollTo({
              top: targetEl.offsetTop - 60,
              behavior: "smooth"
            });
          }
        }
      });
    });
  }

  // Mobile menu toggle
  const btn = document.getElementById("mobile-menu-button");
  const menu = document.getElementById("mobile-menu");
  if (btn && menu) {
    btn.addEventListener("click", () => {
      menu.classList.toggle("hidden");
    });
  }

  // Chat: scroll to bottom smoothly
  const chatWindow = document.getElementById("chatWindow");
  if (chatWindow) {
    chatWindow.scrollTo({
      top: chatWindow.scrollHeight,
      behavior: "smooth"
    });
  }
});

window.addEventListener("DOMContentLoaded", () => {
  const chatWindow = document.getElementById("chatWindow");
  const placeholder = document.getElementById("ai-thinking-placeholder");

  if (placeholder) {
    setTimeout(() => {
      placeholder.outerHTML = `
        <div class="w-full flex mb-4">
          <div class="bg-gray-100 text-gray-800 px-4 py-3 rounded-xl shadow w-3/5">
            Here's a list of assessments related to parasitology across Years 1–4. Would you like links to past questions or marking schemes?
          </div>
        </div>
      `;

      // Scroll smoothly to the bottom
      chatWindow.scrollTo({
        top: chatWindow.scrollHeight,
        behavior: "smooth"
      });

    }, 2000); // 2 seconds delay
  }
});

// Matches the dictionary's courtesy lock, not server-side authentication.
(() => {
  "use strict";
  const DIGEST = "05331485ce6bb8b1f8f233be48788c8bb5355cfa1e79362754cd82cbdcb293d9";
  const KEY = "tangliengim.translator.access.v1";
  const form = document.querySelector("#accessForm");
  const password = document.querySelector("#passwordInput");
  const error = document.querySelector("#accessError");
  const button = document.querySelector("#enterTranslatorButton");
  let opening = false;
  // tools/build_site.py replaces the next line with content hashes, so a deployed
  // page reuses cached scripts until they change. An unbuilt checkout keeps the
  // timestamp fallback so local editing always loads fresh code.
  const ASSET_VERSIONS = {};

  async function open() {
    if (opening) return;
    opening = true;
    button.disabled = true;
    try {
      for (const source of ["/shared/web-hangul-ime.js", "/shared/web-ime-core.js", "/shared/web-phonetic-output.js", "/shared/web-audio-player.js", "translate.js"]) {
        await new Promise((resolve, reject) => {
          const script = document.createElement("script");
          script.src = `${source}?v=${ASSET_VERSIONS[source] || Date.now()}`;
          script.onload = resolve;
          script.onerror = reject;
          document.body.append(script);
        });
      }
      document.querySelector("#lockScreen").hidden = true;
      document.querySelector("#translatorRoot").hidden = false;
      document.querySelector("#englishText").focus();
      window.dispatchEvent(new Event("resize"));
    } catch {
      error.textContent = "The translator could not be opened. Please reload and try again.";
      error.hidden = false;
    }
  }

  form.addEventListener("submit", async event => {
    event.preventDefault();
    button.disabled = true;
    error.hidden = true;
    try {
      const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(password.value));
      const digest = Array.from(new Uint8Array(bytes), byte => byte.toString(16).padStart(2, "0")).join("");
      password.value = "";
      if (digest !== DIGEST) {
        password.setAttribute("aria-invalid", "true");
        error.textContent = "That password is not correct.";
        error.hidden = false;
        button.disabled = false;
        password.focus();
        return;
      }
      try { localStorage.setItem(KEY, DIGEST); } catch { /* Unlock without persistence. */ }
      await open();
    } catch {
      error.textContent = "Unable to check the password. Please reload and try again.";
      error.hidden = false;
      button.disabled = false;
    }
  });
  password.addEventListener("input", () => { password.removeAttribute("aria-invalid"); error.hidden = true; });
  document.querySelector("#lockTranslatorButton").addEventListener("click", () => {
    try { localStorage.removeItem(KEY); } catch { /* Reload still locks this page. */ }
    location.reload();
  });
  try { if (localStorage.getItem(KEY) === DIGEST) open(); } catch { /* Keep the password form available. */ }
})();

// The Dictionary and Translator share this client-side courtesy lock. It is not
// secure server-side authentication. Unlocking either tool unlocks both.
window.TliAccessGate = (() => {
  "use strict";
  const DIGEST = "05331485ce6bb8b1f8f233be48788c8bb5355cfa1e79362754cd82cbdcb293d9";
  const KEY = "tangliengim.tools.access.v1";
  // Visitors who unlocked one tool before the locks were merged stay unlocked.
  const OLD_KEYS = ["tangliengim.dictionary.access.v1", "tangliengim.translator.access.v1"];
  const text = window.TliSiteLanguage?.text || (value => value);

  const isUnlocked = () => {
    try {
      return [KEY, ...OLD_KEYS].some(key => localStorage.getItem(key) === DIGEST);
    } catch {
      return false;
    }
  };

  const remember = () => {
    try {
      localStorage.setItem(KEY, DIGEST);
    } catch {
      // Access still works for this page when browser storage is unavailable.
    }
  };

  // Locking either tool locks both.
  const lock = () => {
    try {
      [KEY, ...OLD_KEYS].forEach(key => localStorage.removeItem(key));
    } catch {
      // Reloading still restores the lock screen when storage is unavailable.
    }
    location.reload();
  };

  const digestOf = async password => {
    const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(password));
    return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, "0")).join("");
  };

  // open() shows the tool and rejects if it can't; failureMessage is then shown on the lock screen.
  const start = ({ open, failureMessage }) => {
    const form = document.querySelector("#accessForm");
    const password = document.querySelector("#passwordInput");
    const error = document.querySelector("#accessError");
    const button = document.querySelector("#enterToolButton");
    let opening = false;

    const showError = message => {
      error.textContent = text(message);
      error.hidden = false;
      button.disabled = false;
      password.focus();
    };

    const openTool = async () => {
      if (opening) return;
      opening = true;
      button.disabled = true;
      error.hidden = true;
      try {
        await open();
      } catch (problem) {
        console.error(problem);
        opening = false;
        showError(failureMessage);
      }
    };

    form.addEventListener("submit", async event => {
      event.preventDefault();
      button.disabled = true;
      error.hidden = true;
      password.removeAttribute("aria-invalid");
      let digest;
      try {
        digest = await digestOf(password.value);
      } catch {
        showError("Unable to check the password. Please reload and try again.");
        return;
      }
      password.value = "";
      if (digest !== DIGEST) {
        password.setAttribute("aria-invalid", "true");
        showError("That password is not correct.");
        return;
      }
      remember();
      await openTool();
    });

    password.addEventListener("input", () => {
      password.removeAttribute("aria-invalid");
      error.hidden = true;
    });

    if (isUnlocked()) openTool();
  };

  return { start, lock };
})();

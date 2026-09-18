// This is a client-side courtesy lock, not secure server-side authentication.
const ACCESS_STORAGE_KEY = "tangliengim.dictionary.access.v1";
const ACCESS_DIGEST = "05331485ce6bb8b1f8f233be48788c8bb5355cfa1e79362754cd82cbdcb293d9";
const APP_SCRIPTS = [
  "/shared/web-hangul-ime.js",
  "/shared/web-ime-core.js",
  "/shared/web-audio-player.js",
  "app.js",
];

const lockScreen = document.querySelector("#lockScreen");
const accessForm = document.querySelector("#accessForm");
const passwordInput = document.querySelector("#passwordInput");
const accessError = document.querySelector("#accessError");
const enterButton = document.querySelector("#enterDictionaryButton");
const dictionaryRoot = document.querySelector("#dictionaryRoot");
let dictionaryLoading = false;

function savedAccessIsValid() {
  try {
    return localStorage.getItem(ACCESS_STORAGE_KEY) === ACCESS_DIGEST;
  } catch (_error) {
    return false;
  }
}

function rememberAccess() {
  try {
    localStorage.setItem(ACCESS_STORAGE_KEY, ACCESS_DIGEST);
  } catch (_error) {
    // Access still works for this page when browser storage is unavailable.
  }
}

function forgetAccess() {
  try {
    localStorage.removeItem(ACCESS_STORAGE_KEY);
  } catch (_error) {
    // Reloading still restores the locked screen when storage is unavailable.
  }
}

async function passwordDigest(password) {
  const bytes = new TextEncoder().encode(password);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

function loadScript(source) {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    const separator = source.includes("?") ? "&" : "?";
    script.src = `${source}${separator}v=${Date.now()}`;
    script.onload = resolve;
    script.onerror = () => reject(new Error(`Unable to load ${source}`));
    document.body.append(script);
  });
}

async function openDictionary() {
  if (dictionaryLoading) return;
  dictionaryLoading = true;
  enterButton.disabled = true;
  accessError.hidden = true;

  try {
    const response = await fetch("dictionary-view.html", { cache: "no-cache" });
    if (!response.ok) throw new Error(`Dictionary view returned ${response.status}`);
    dictionaryRoot.innerHTML = await response.text();
    dictionaryRoot.hidden = false;
    lockScreen.hidden = true;
    document.body.classList.remove("dictionary-locked");
    document.querySelector("#lockDictionaryButton").addEventListener("click", () => {
      forgetAccess();
      window.location.reload();
    });
    for (const source of APP_SCRIPTS) await loadScript(source);
  } catch (error) {
    console.error(error);
    dictionaryRoot.replaceChildren();
    dictionaryRoot.hidden = true;
    lockScreen.hidden = false;
    document.body.classList.add("dictionary-locked");
    accessError.textContent = "The dictionary could not be opened. Please try again.";
    accessError.hidden = false;
    enterButton.disabled = false;
    dictionaryLoading = false;
    passwordInput.focus();
  }
}

accessForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  enterButton.disabled = true;
  accessError.hidden = true;
  passwordInput.removeAttribute("aria-invalid");

  const digest = await passwordDigest(passwordInput.value);
  if (digest !== ACCESS_DIGEST) {
    passwordInput.value = "";
    passwordInput.setAttribute("aria-invalid", "true");
    accessError.textContent = "That password is not correct.";
    accessError.hidden = false;
    enterButton.disabled = false;
    passwordInput.focus();
    return;
  }

  rememberAccess();
  passwordInput.value = "";
  await openDictionary();
});

passwordInput.addEventListener("input", () => {
  passwordInput.removeAttribute("aria-invalid");
  accessError.hidden = true;
});

if (savedAccessIsValid()) openDictionary();

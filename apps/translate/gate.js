// Opens the Translator once the shared lock (shared/web-access-gate.js) lets the visitor in.
(() => {
  "use strict";
  const APP_SCRIPTS = [
    "/shared/web-hangul-ime.js",
    "/shared/web-ime-core.js",
    "/shared/web-phonetic-output.js",
    "/shared/web-audio-player.js",
    "translate.js",
  ];
  // tools/build_site.py replaces the next line with content hashes, so a deployed
  // page reuses cached scripts until they change. An unbuilt checkout keeps the
  // timestamp fallback so local editing always loads fresh code.
  const ASSET_VERSIONS = {};

  function loadScript(source) {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = `${source}?v=${ASSET_VERSIONS[source] || Date.now()}`;
      script.onload = resolve;
      script.onerror = () => reject(new Error(`Unable to load ${source}`));
      document.body.append(script);
    });
  }

  async function openTranslator() {
    for (const source of APP_SCRIPTS) await loadScript(source);
    document.querySelector("#lockScreen").hidden = true;
    document.body.classList.remove("access-locked");
    document.querySelector("#translatorRoot").hidden = false;
    document.querySelector("#englishText").focus();
    window.dispatchEvent(new Event("resize"));
  }

  document.querySelector("#lockTranslatorButton").addEventListener("click", TliAccessGate.lock);
  TliAccessGate.start({
    open: openTranslator,
    failureMessage: "The translator could not be opened. Please try again.",
  });
})();

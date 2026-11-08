// Opens the Dictionary once the shared lock (shared/web-access-gate.js) lets the visitor in.
(() => {
  "use strict";
  const APP_SCRIPTS = [
    "/shared/web-hangul-ime.js",
    "/shared/web-ime-core.js",
    "/shared/web-audio-player.js",
    "app.js",
  ];
  // tools/build_site.py replaces the next line with content hashes, so a deployed
  // page reuses cached scripts until they change. An unbuilt checkout keeps the
  // timestamp fallback so local editing always loads fresh code.
  const ASSET_VERSIONS = {};

  function loadScript(source) {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      const separator = source.includes("?") ? "&" : "?";
      script.src = `${source}${separator}v=${ASSET_VERSIONS[source] || Date.now()}`;
      script.onload = resolve;
      script.onerror = () => reject(new Error(`Unable to load ${source}`));
      document.body.append(script);
    });
  }

  const lockScreen = document.querySelector("#lockScreen");
  const dictionaryRoot = document.querySelector("#dictionaryRoot");

  async function openDictionary() {
    try {
      const response = await fetch("dictionary-view.html", { cache: "no-cache" });
      if (!response.ok) throw new Error(`Dictionary view returned ${response.status}`);
      dictionaryRoot.innerHTML = await response.text();
      window.TliSiteLanguage?.apply(dictionaryRoot);
      dictionaryRoot.hidden = false;
      lockScreen.hidden = true;
      document.body.classList.remove("access-locked");
      document.querySelector("#lockDictionaryButton").addEventListener("click", TliAccessGate.lock);
      for (const source of APP_SCRIPTS) await loadScript(source);
    } catch (error) {
      dictionaryRoot.replaceChildren();
      dictionaryRoot.hidden = true;
      lockScreen.hidden = false;
      document.body.classList.add("access-locked");
      throw error;
    }
  }

  TliAccessGate.start({
    open: openDictionary,
    failureMessage: "The dictionary could not be opened. Please try again.",
  });
})();

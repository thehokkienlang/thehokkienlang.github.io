"use strict";
(() => {
  // The launcher watches this lease, not Edge's short-lived delegation process.
  async function heartbeat() {
    try {
      await fetch("/desktop-api/editor-heartbeat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: "{}",
        cache: "no-store",
        signal: AbortSignal.timeout(4000),
      });
    } catch (_) {
      // A server restart temporarily interrupts requests; the next beat retries.
    }
  }
  heartbeat();
  setInterval(heartbeat, 10000);
  window.addEventListener("pageshow", heartbeat);
  document.addEventListener("visibilitychange", heartbeat);
})();

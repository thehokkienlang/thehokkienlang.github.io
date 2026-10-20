"use strict";
(() => {
  const instance = "__DESKTOP_INSTANCE__";
  const token = "__EDITOR_TOKEN__";
  const draftKey = "tangliengim-restart:" + location.pathname;
  let hooks, reloading = false, restarting = false, checking = false;

  function preserveDraft() {
    sessionStorage.setItem(draftKey, JSON.stringify(hooks.capture()));
  }
  async function checkInstance() {
    if (reloading) return true;
    if (!hooks || checking) return false;
    checking = true;
    try {
      const response = await fetch("/desktop-api/session", { cache: "no-store", signal: AbortSignal.timeout(2500) });
      if (!response.ok) return false;
      const status = await response.json();
      if (!status.instance || status.instance === instance) return false;
      preserveDraft();
      reloading = true;
      const url = new URL(location.href);
      url.searchParams.delete("job");
      url.searchParams.delete("publish");
      history.replaceState(null, "", url);
      location.reload();
      return true;
    } catch (error) {
      if (error.name !== "TimeoutError" && error.name !== "TypeError") hooks.notify(error.message);
      return false;
    } finally { checking = false; }
  }
  window.TangliengimDesktopRestart = {
    isReloading: () => reloading,
    async attach(options) {
      hooks = options;
      const draft = sessionStorage.getItem(draftKey);
      if (draft) {
        await options.restore(JSON.parse(draft));
        sessionStorage.removeItem(draftKey);
      }
      setInterval(checkInstance, 2000);
    },
    async restart() {
      if (!hooks) throw new Error("The editor is still loading. Please try restarting again in a moment.");
      if (restarting) throw new Error("A restart is already in progress.");
      const reason = hooks.canRestart?.();
      if (reason) throw new Error(reason);
      preserveDraft();
      restarting = true;
      try {
        const response = await fetch("/desktop-api/editor/restart", {
          method: "POST", headers: { "Content-Type": "application/json", "X-Tangliengim-Editor": token },
          body: "{}", signal: AbortSignal.timeout(5000),
        });
        const result = await response.json();
        if (!response.ok || !result.ok) throw new Error(result.error || "Could not restart.");
        hooks.notify("Restarting...");
        const deadline = Date.now() + 45000;
        while (Date.now() < deadline) {
          if (await checkInstance()) return;
          await new Promise(resolve => setTimeout(resolve, 400));
        }
        throw new Error("The restart has not finished. Your input is retained in this window.");
      } finally { restarting = false; }
    },
  };
})();

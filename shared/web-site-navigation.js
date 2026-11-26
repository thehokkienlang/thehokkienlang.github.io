(() => {
  const hoverPointer = window.matchMedia("(hover: hover) and (pointer: fine)");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const FOOTER_LABELS = {
    en: {controls: "Footer controls", top: "Back to top"},
    "zh-Hant": {controls: "頁尾功能", top: "返回頁首"},
    "zh-Hans": {controls: "页尾功能", top: "返回页首"},
  };
  const HANGUL_ON_LABELS = {
    en: "Hangul key on",
    "zh-Hant": "諺文鍵盤已開啟",
    "zh-Hans": "谚文键盘已开启",
  };

  function language() {
    return ["zh-Hant", "zh-Hans"].includes(document.documentElement.lang)
      ? document.documentElement.lang : "en";
  }

  function prepareDropdowns(root = document) {
    root.querySelectorAll('nav[aria-label="Main navigation"], .site-footer-controls').forEach(nav => {
    const dropdowns = [...nav.querySelectorAll(".site-nav-dropdown")];
    const closeOthers = current => dropdowns.forEach(dropdown => {
      if (dropdown !== current) dropdown.open = false;
    });

    dropdowns.forEach(dropdown => {
      const trigger = dropdown.querySelector("summary");
      let closeTimer;
      dropdown.addEventListener("pointerenter", event => {
        if (event.pointerType !== "mouse" || !hoverPointer.matches) return;
        clearTimeout(closeTimer);
        closeOthers(dropdown);
        dropdown.open = true;
      });
      dropdown.addEventListener("pointerleave", event => {
        if (event.pointerType !== "mouse" || !hoverPointer.matches) return;
        clearTimeout(closeTimer);
        // Allow the pointer to cross the small gap between the label and panel.
        closeTimer = setTimeout(() => {
          if (!dropdown.matches(":focus-within")) dropdown.open = false;
        }, 180);
      });
      dropdown.addEventListener("toggle", () => {
        if (dropdown.open) closeOthers(dropdown);
      });
      trigger.addEventListener("keydown", event => {
        if (event.key !== "ArrowDown" && event.key !== "ArrowUp") return;
        event.preventDefault();
        closeOthers(dropdown);
        dropdown.open = true;
        const links = dropdown.querySelectorAll("a");
        const target = event.key === "ArrowDown" ? links[0] : links[links.length - 1];
        target?.focus();
      });
      dropdown.addEventListener("keydown", event => {
        if (event.key !== "Escape" || !dropdown.open) return;
        event.preventDefault();
        event.stopPropagation();
        dropdown.open = false;
        trigger.focus();
      });
      dropdown.addEventListener("click", event => {
        if (event.target.closest("a")) dropdown.open = false;
      });
    });

    document.addEventListener("pointerdown", event => {
      dropdowns.forEach(dropdown => {
        if (!dropdown.contains(event.target)) dropdown.open = false;
      });
    });
    document.addEventListener("focusin", event => {
      dropdowns.forEach(dropdown => {
        if (!dropdown.contains(event.target)) dropdown.open = false;
      });
    });
  });
  }

  function mountHeaderSearch(root = document) {
    root.querySelectorAll(".site-header-search:not([data-search-mounted])").forEach(form => {
      if (!window.TliSearchBox) return;
      window.TliSearchBox.mount(form, {deferKeyboard: true});
      form.dataset.searchMounted = "true";
      const toggle = form.querySelector(".hangul-keyboard-toggle");
      const hint = document.createElement("span");
      hint.className = "site-header-keyboard-hint";
      hint.setAttribute("role", "status");
      hint.setAttribute("aria-live", "polite");
      hint.textContent = HANGUL_ON_LABELS[language()];
      form.append(hint);
      let hintTimer;
      toggle.addEventListener("click", () => {
        clearTimeout(hintTimer);
        if (toggle.getAttribute("aria-pressed") !== "true") {
          hint.classList.remove("is-visible");
          return;
        }
        hint.classList.add("is-visible");
        hintTimer = setTimeout(() => hint.classList.remove("is-visible"), 1800);
      });
    });
  }

  function mountFooters(root = document) {
    root.querySelectorAll(".site-footer:not([data-controls-mounted])").forEach(footer => {
      const headerNav = document.querySelector('nav[aria-label="Main navigation"]');
      const languageMenu = headerNav?.querySelector(":scope > .site-language-dropdown");
      if (!languageMenu) return;

      const meta = document.createElement("div");
      meta.className = "site-footer-meta";
      meta.append(...footer.childNodes);

      const controls = document.createElement("nav");
      controls.className = "site-footer-controls";
      controls.setAttribute("aria-label", FOOTER_LABELS[language()].controls);

      const theme = document.createElement("button");
      theme.type = "button";
      theme.className = "site-theme-toggle site-footer-control";

      const footerLanguage = languageMenu.cloneNode(true);
      footerLanguage.classList.add("site-footer-language");
      footerLanguage.removeAttribute("name");
      footerLanguage.querySelector(".site-sandhi")?.remove();
      footerLanguage.querySelectorAll("[data-language-choice]").forEach(link => {
        link.addEventListener("click", () => {
          const input = document.querySelector(location.pathname.startsWith("/dictionary/") ? "#searchInput" : "#imeText");
          if (!input) return;
          const destination = new URL(link.href);
          destination.searchParams.set(location.pathname.startsWith("/dictionary/") ? "q" : "text", input.value);
          link.href = destination.pathname + destination.search + destination.hash;
        });
      });

      controls.append(theme, footerLanguage);
      footer.replaceChildren(controls, meta);
      footer.dataset.controlsMounted = "true";
      window.TliTheme?.mount?.();
      prepareDropdowns(footer);
    });
  }

  function mountBackToTop() {
    if (document.querySelector(".site-back-to-top")) return;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "site-back-to-top";
    button.hidden = true;
    button.innerHTML = '<span aria-hidden="true">↑</span><span>' + FOOTER_LABELS[language()].top + "</span>";
    button.setAttribute("aria-label", FOOTER_LABELS[language()].top);
    button.addEventListener("click", () => window.scrollTo({
      top: 0,
      behavior: reducedMotion.matches ? "auto" : "smooth",
    }));
    document.body.append(button);

    let scheduled = false;
    const update = () => {
      scheduled = false;
      button.hidden = window.scrollY < 480;
    };
    window.addEventListener("scroll", () => {
      if (scheduled) return;
      scheduled = true;
      window.requestAnimationFrame(update);
    }, {passive: true});
    update();
  }

  function mount(root = document) {
    prepareDropdowns(root);
    mountHeaderSearch(root);
    mountFooters(root);
    mountBackToTop();
  }

  window.TliSiteNavigation = {mount, mountFooters};
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => mount());
  else mount();
})();

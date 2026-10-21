(() => {
  const hoverPointer = window.matchMedia("(hover: hover) and (pointer: fine)");
  document.querySelectorAll('nav[aria-label="Main navigation"]').forEach(nav => {
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
})();

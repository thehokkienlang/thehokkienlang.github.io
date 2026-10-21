(() => {
  document.querySelectorAll('nav[aria-label="Main navigation"]').forEach(nav => {
    const dropdowns = [...nav.querySelectorAll(".site-nav-dropdown")];
    const closeOthers = current => dropdowns.forEach(dropdown => {
      if (dropdown !== current) dropdown.open = false;
    });

    dropdowns.forEach(dropdown => {
      const trigger = dropdown.querySelector("summary");
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

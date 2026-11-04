(() => {
  "use strict";
  const readings = "rt, .tli-rt, .entry-headword-reading";
  const annotations = `${readings}, rp`;
  const elementAt = node => node?.nodeType === Node.ELEMENT_NODE ? node : node?.parentElement;
  const readingAt = node => elementAt(node)?.closest(readings);

  // Set the selection mode before the browser starts a mouse drag or long press.
  document.addEventListener("pointerdown", event => {
    if (event.button !== 0) return;
    document.documentElement.classList.toggle("selecting-ruby", Boolean(readingAt(event.target)));
  }, true);

  document.addEventListener("selectionchange", () => {
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed) return;
    const reading = readingAt(selection.anchorNode);
    document.documentElement.classList.toggle("selecting-ruby",
      Boolean(reading && reading === readingAt(selection.focusNode)));
  });

  document.addEventListener("copy", event => {
    if (event.defaultPrevented || !event.clipboardData) return;
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed || !selection.rangeCount) return;
    // Inputs and editable IME controls keep their own clipboard behaviour.
    if (elementAt(selection.anchorNode)?.closest("input, textarea, [contenteditable]:not([contenteditable=false])")) return;
    const reading = readingAt(selection.anchorNode);
    if (reading && reading === readingAt(selection.focusNode)) return;
    const fragment = selection.getRangeAt(0).cloneContents();
    if (!fragment.querySelector(annotations)) return;
    fragment.querySelectorAll(annotations).forEach(node => node.remove());
    const container = document.createElement("div");
    container.append(fragment);
    // Keep paragraph and explicit line breaks in the plain-text clipboard.
    container.querySelectorAll("br").forEach(node => node.replaceWith("\n"));
    container.querySelectorAll("p, div, li, h1, h2, h3, h4, h5, h6, tr, [style]").forEach(node => {
      if (node.matches("[style]") && !node.matches("p, div, li, h1, h2, h3, h4, h5, h6, tr") && node.style.display !== "block") return;
      node.append("\n");
    });
    event.clipboardData.setData("text/plain", container.textContent.replace(/\n{3,}/g, "\n\n").trim());
    event.preventDefault();
  });
})();

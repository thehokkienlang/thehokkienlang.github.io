(() => {
  "use strict";
  const readings = "rt, .tli-rt, .entry-headword-reading";
  const annotations = `${readings}, rp`;
  const elementAt = node => node?.nodeType === Node.ELEMENT_NODE ? node : node?.parentElement;
  const readingAt = node => elementAt(node)?.closest(readings);

  const selectReading = reading => {
    const selection = window.getSelection();
    if (!selection) return;
    const range = document.createRange();
    range.selectNodeContents(reading);
    selection.removeAllRanges();
    selection.addRange(range);
  };

  // Set the selection mode before the browser starts a mouse drag or long press.
  document.addEventListener("pointerdown", event => {
    if (event.button !== 0) return;
    const reading = readingAt(event.target);
    document.documentElement.classList.toggle("selecting-ruby", Boolean(reading));
    if (!reading) return;
    event.stopPropagation();
    selectReading(reading);
  }, true);

  document.addEventListener("click", event => {
    const reading = readingAt(event.target);
    if (!reading) return;
    event.preventDefault();
    event.stopPropagation();
    selectReading(reading);
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
    // Lyric and Lomari lines are block spans (classes since audit B4; inline styles before).
    container.querySelectorAll("p, div, li, h1, h2, h3, h4, h5, h6, tr, .lyric-line, .lyric-lomari, [style]").forEach(node => {
      if (node.matches("[style]") && !node.matches("p, div, li, h1, h2, h3, h4, h5, h6, tr, .lyric-line, .lyric-lomari")
          && node.style.display !== "block") return;
      node.append("\n");
    });
    event.clipboardData.setData("text/plain", container.textContent.replace(/\n{3,}/g, "\n\n").trim());
    event.preventDefault();
  });
})();

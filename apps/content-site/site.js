(() => {
  const toneRenderer = window.TangliengimImeCore;
  if (toneRenderer) {
    document.querySelectorAll(".title-reading").forEach(title => {
      title.querySelectorAll(".hanri-title:not(.bopomofo-title) > rt").forEach(reading => {
        reading.replaceChildren(toneRenderer.renderInlineUpperToneReading(reading.textContent));
      });
      const walker = document.createTreeWalker(title, NodeFilter.SHOW_TEXT, {
        acceptNode: node => node.parentElement.closest("rt, rp, .hangul-tone")
          ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT,
      });
      const textNodes = [];
      while (walker.nextNode()) textNodes.push(walker.currentNode);
      textNodes.forEach(node => node.replaceWith(toneRenderer.renderToneMarkedReading(node.textContent)));
    });
  }
  const article = document.querySelector(".imported-content");
  if (!article) return;
  const lookup = document.querySelector("#lookup-link");
  const ime = document.querySelector("#ime-link");
  document.addEventListener("selectionchange", () => {
    const selection = window.getSelection();
    if (!selection || !selection.rangeCount || selection.isCollapsed || !article.contains(selection.anchorNode) || !article.contains(selection.focusNode)) return;
    const fragment = selection.getRangeAt(0).cloneContents();
    fragment.querySelectorAll("rt, rp").forEach(node => node.remove());
    const text = fragment.textContent.trim().slice(0, 12000);
    if (!text) return;
    lookup.href = "/dictionary/?q=" + encodeURIComponent(text);
    ime.href = "/ime/?text=" + encodeURIComponent(text);
  });
  article.querySelectorAll("table").forEach(table => {
    if (table.parentElement.matches(".wp-block-table")) return;
    const wrapper = document.createElement("div");
    wrapper.className = "table-scroll";
    table.before(wrapper);
    wrapper.append(table);
  });
})();

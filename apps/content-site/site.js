(() => {
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

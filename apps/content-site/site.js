(() => {
  const picks = document.querySelector("[data-home-song-picks]");
  const pool = document.querySelector("[data-home-song-pool]");
  if (picks && pool) {
    const songs = [...pool.content.querySelectorAll("a")];
    for (let index = songs.length - 1; index > 0; index--) {
      const other = Math.floor(Math.random() * (index + 1));
      [songs[index], songs[other]] = [songs[other], songs[index]];
    }
    picks.replaceChildren(...songs.slice(0, 3).map(song => song.cloneNode(true)));
  }
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
  if (document.body.dataset.siteSection === "learn") {
    const headings = [...article.querySelectorAll("h2")];
    if (headings.length > 2) {
      const contents = document.createElement("details");
      contents.className = "article-contents";
      const summary = document.createElement("summary");
      summary.textContent = {"zh-Hant": "本頁內容", "zh-Hans": "本页内容"}[document.documentElement.lang] || "On this page";
      const list = document.createElement("ol");
      headings.forEach((heading, index) => {
        if (!heading.id) {
          let id = `article-section-${index + 1}`;
          while (document.getElementById(id)) id += "-section";
          heading.id = id;
        }
        const label = heading.cloneNode(true);
        label.querySelectorAll("rt, rp").forEach(node => node.remove());
        const link = document.createElement("a");
        link.href = "#" + encodeURIComponent(heading.id);
        link.textContent = label.textContent.trim();
        const item = document.createElement("li");
        item.append(link);
        list.append(item);
      });
      contents.append(summary, list);
      article.before(contents);
    }
  }
  const lookup = document.querySelector("#lookup-link");
  const ime = document.querySelector("#ime-link");
  document.addEventListener("selectionchange", () => {
    const selection = window.getSelection();
    if (!selection || !selection.rangeCount || selection.isCollapsed || !article.contains(selection.anchorNode) || !article.contains(selection.focusNode)) return;
    const fragment = selection.getRangeAt(0).cloneContents();
    fragment.querySelectorAll("rt, rp").forEach(node => node.remove());
    const text = fragment.textContent.trim().slice(0, 12000);
    if (!text) return;
    const languageHref = window.TliSiteLanguage?.href || (value => value);
    lookup.href = languageHref("/dictionary/?q=" + encodeURIComponent(text));
    ime.href = languageHref("/ime/?text=" + encodeURIComponent(text));
  });
  article.querySelectorAll("table").forEach(table => {
    if (table.parentElement.matches(".wp-block-table")) return;
    const wrapper = document.createElement("div");
    wrapper.className = "table-scroll";
    table.before(wrapper);
    wrapper.append(table);
  });
})();

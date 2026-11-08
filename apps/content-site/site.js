(() => {
  const removeRubyHyphens = reading => {
    const walker = document.createTreeWalker(reading, NodeFilter.SHOW_TEXT);
    const textNodes = [];
    while (walker.nextNode()) textNodes.push(walker.currentNode);
    textNodes.forEach(node => {
      node.textContent = node.textContent.replace(/-/gu, "");
    });
  };

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
  // WebKit can place positioned rt boxes below their base; use ordinary boxes for display.
  [...document.querySelectorAll('.title-reading ruby, .imported-content ruby')].reverse().forEach(ruby => {
    const annotation = document.createElement("span");
    for (const { name, value } of ruby.attributes) annotation.setAttribute(name, value);
    annotation.classList.add("tli-ruby");
    const base = document.createElement("span");
    base.className = "tli-ruby-base";
    const readings = [];
    for (const child of [...ruby.childNodes]) {
      if (child.nodeName === "RT") {
        const reading = document.createElement("span");
        for (const { name, value } of child.attributes) reading.setAttribute(name, value);
        reading.classList.add("tli-rt");
        reading.append(...child.childNodes);
        removeRubyHyphens(reading);
        readings.push(reading);
      } else if (child.nodeName !== "RP") {
        base.append(child);
      }
    }
    const toneOnly = readings.length > 0 && readings.every(reading =>
      /^[\sˆˋˊˉˇˍˎˏˬꞈ`]+$/u.test(reading.textContent));
    if (readings.length > 0) annotation.classList.add(toneOnly ? "tli-tone-ruby" : "tli-reading-ruby");
    if (ruby.closest('.imported-content') && readings.some(reading => /[\u3105-\u312f\u31a0-\u31bf]/u.test(reading.textContent))) {
      annotation.classList.add('tli-bopomofo-reading');
    }
    annotation.append(base, ...readings);
    ruby.replaceWith(annotation);
  });
  const updateWrappedTitles = () => {
    document.querySelectorAll("h1.title-reading").forEach(title => {
      title.classList.remove("title-reading-wrapped");
      const units = [...title.children].filter(unit => getComputedStyle(unit).position !== "absolute");
      if (units.length < 2) return;
      const tops = units.map(unit => unit.getBoundingClientRect().top);
      title.classList.toggle("title-reading-wrapped", Math.max(...tops) - Math.min(...tops) > 3);
    });
  };
  let titleWrapFrame = 0;
  const scheduleTitleWrapUpdate = () => {
    cancelAnimationFrame(titleWrapFrame);
    titleWrapFrame = requestAnimationFrame(updateWrappedTitles);
  };
  scheduleTitleWrapUpdate();
  document.fonts?.ready.then(scheduleTitleWrapUpdate);
  window.addEventListener("resize", scheduleTitleWrapUpdate, { passive: true });
  document.querySelectorAll(".song-entry-lomari, .home-songbook small").forEach(node => {
    node.textContent = node.textContent.normalize("NFC");
  });
  // Keep catalogue entries as full links; only homepage picks use base-text links.
  document.querySelectorAll("[data-home-song-picks] > a").forEach(original => {
    const href = original.getAttribute("href");
    const item = document.createElement("div");
    for (const { name, value } of original.attributes) {
      if (name !== "href") item.setAttribute(name, value);
    }
    if (!item.classList.contains("song-entry")) item.classList.add("home-songbook-item");
    item.append(...original.childNodes);
    const title = item.querySelector(".song-entry-title, .home-song-title");
    const walker = document.createTreeWalker(title, NodeFilter.SHOW_TEXT, {
      acceptNode: node => node.parentElement.closest("rt, rp, .tli-rt, .tone-mark, a") || !node.textContent.trim()
        ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT,
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(node => {
      const link = document.createElement("a");
      link.className = "song-base-link";
      link.href = href;
      node.replaceWith(link);
      link.append(node);
    });
    original.replaceWith(item);
  });
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
        label.querySelectorAll("rt, rp, .tli-rt, .tone-mark").forEach(node => node.remove());
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
    fragment.querySelectorAll("rt, rp, .tli-rt, .tone-mark").forEach(node => node.remove());
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

  // Songs page filter (audit A9). Matching ignores case, Lomari diacritics, TLI tone
  // marks, spaces and hyphens; Hangul is compared syllable by syllable, never as Korean.
  const filter = document.querySelector("[data-song-filter]");
  if (filter) {
    const fold = value => String(value || "").normalize("NFKD")
      .replace(/[̀-ͯ]/gu, "").replace(/[ˆˋˊˉˇˍˎˏˬꞈ`\s\-’'‘]/gu, "").toLowerCase().normalize("NFC");
    const input = filter.querySelector(".song-filter-input");
    const chips = [...filter.querySelectorAll("[data-song-filter-category]")];
    const summary = filter.querySelector(".song-filter-summary");
    const empty = filter.querySelector(".song-filter-empty");
    const catalogue = document.querySelector(".song-catalogue");
    const sections = [...catalogue.querySelectorAll(".song-category")];
    const rows = sections.flatMap(section => [...section.querySelectorAll("li[data-song-search]")]
      .map(row => ({ row, section, text: fold(row.dataset.songSearch) })));
    let category = "";
    const apply = () => {
      const query = fold(input.value);
      let shown = 0;
      rows.forEach(item => {
        const visible = (!category || item.section.dataset.songCategory === category) && (!query || item.text.includes(query));
        item.row.hidden = !visible;
        if (visible) shown += 1;
      });
      sections.forEach(section => {
        const count = section.querySelectorAll("li[data-song-search]:not([hidden])").length;
        section.hidden = count === 0;
        const badge = section.querySelector(".song-category-heading > span");
        if (badge) badge.textContent = String(count).padStart(2, "0");
      });
      const filtering = Boolean(query || category);
      catalogue.classList.toggle("is-filtering", filtering);
      empty.hidden = shown > 0;
      summary.textContent = filtering && shown ? filter.dataset.countTemplate.replace("{n}", shown) : "";
    };
    input.addEventListener("input", apply);
    chips.forEach(chip => chip.addEventListener("click", () => {
      category = chip.dataset.songFilterCategory;
      chips.forEach(other => other.setAttribute("aria-pressed", String(other === chip)));
      apply();
    }));
  }
})();

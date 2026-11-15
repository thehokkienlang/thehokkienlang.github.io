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
  const renderTitleTones = scope => {
    const toneRenderer = window.TangliengimImeCore;
    if (!toneRenderer) return;
    scope.querySelectorAll(".title-reading").forEach(title => {
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
  };
  renderTitleTones(document);
  // WebKit can place positioned rt boxes below their base; use ordinary boxes for display.
  const normalizeRuby = scope => [...scope.querySelectorAll('ruby')].reverse().forEach(ruby => {
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
    // A final tone mark widens the reading but barely registers, so the Hangul looks left of centre.
    if (!toneOnly && !ruby.closest(".title-reading")) readings.forEach(reading => {
      const syllables = reading.textContent.match(/[가-힣ᄀ-ᅟꥠ-꥿]/gu) || [];
      if (syllables.length >= 2 && /[ˆˋˊˉˇˍˎˏˬꞈ`]\s*$/u.test(reading.textContent)) reading.classList.add("tli-rt-tone-end");
    });
    if (ruby.closest('.imported-content') && readings.some(reading => /[\u3105-\u312f\u31a0-\u31bf]/u.test(reading.textContent))) {
      annotation.classList.add('tli-bopomofo-reading');
    }
    annotation.append(base, ...readings);
    ruby.replaceWith(annotation);
  });
  normalizeRuby(document);
  // For markup drawn after load (search results): the same tone marks and ruby as the page's own.
  window.TliSiteDisplay = { decorate: scope => { renderTitleTones(scope); normalizeRuby(scope); } };
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

  // Side-by-side language columns become tabs on phones, where they would otherwise stack.
  document.querySelectorAll(".song-language-compare").forEach(compare => {
    const columns = [...compare.children].filter(column => column.matches(".wp-block-column"));
    if (columns.length < 2) return;
    const tabs = document.createElement("div");
    tabs.className = "song-version-tablist song-language-tabs";
    const buttons = columns.map(column => {
      const button = document.createElement("button");
      button.type = "button";
      button.append(...[...(column.querySelector("h4")?.childNodes || [])].map(node => node.cloneNode(true)));
      button.addEventListener("click", () => show(columns.indexOf(column)));
      tabs.append(button);
      return button;
    });
    const show = selected => columns.forEach((column, index) => {
      column.classList.toggle("is-tab-hidden", index !== selected);
      buttons[index].setAttribute("aria-pressed", String(index === selected));
    });
    compare.before(tabs);
    show(0);
  });

  // Homepage Listen buttons play the dictionary clips embedded by the build.
  let listenPlayer = null;
  let listening = null;
  const stopListening = () => {
    listening?.classList.remove("is-playing");
    listening = null;
  };
  document.querySelectorAll("[data-tli-audio]").forEach(button => button.addEventListener("click", async () => {
    listenPlayer ||= window.TangliengimWebAudio.createPlayer();
    if (listening === button) {
      listenPlayer.stop();
      stopListening();
      return;
    }
    stopListening();
    listening = button;
    button.classList.add("is-playing");
    try {
      await listenPlayer.play(JSON.parse(button.dataset.tliAudio));
    } catch (error) {
      console.error(error);
    } finally {
      if (listening === button) stopListening();
    }
  }));

  // A video in a tab you leave must stop, or its sound keeps playing out of sight.
  const stopVideos = panel => panel.querySelectorAll("iframe").forEach(frame => {
    const source = frame.src;
    if (source.includes("enablejsapi=1")) {
      frame.contentWindow?.postMessage(JSON.stringify({ event: "command", func: "pauseVideo", args: "" }), new URL(source).origin);
    } else {
      frame.src = source;
    }
  });
  document.querySelectorAll("[data-song-version-tabs]").forEach(tabs => {
    const buttons = [...tabs.querySelectorAll('[role="tab"]')];
    const panels = [...tabs.querySelectorAll('[role="tabpanel"]')];
    const activate = (button, updateHash = true) => {
      buttons.forEach(item => {
        const selected = item === button;
        item.setAttribute("aria-selected", String(selected));
        item.tabIndex = selected ? 0 : -1;
      });
      panels.forEach(panel => {
        const shown = panel.id === button.getAttribute("aria-controls");
        if (panel.hidden === !shown) return;
        panel.hidden = !shown;
        if (shown) panel.dispatchEvent(new Event("song-version-shown"));
        else stopVideos(panel);
      });
      if (updateHash) history.replaceState(null, "", `#version-${button.dataset.songVersionKey}`);
    };
    buttons.forEach((button, index) => {
      button.addEventListener("click", () => activate(button));
      button.addEventListener("keydown", event => {
        if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
        event.preventDefault();
        const next = event.key === "Home" ? 0 : event.key === "End" ? buttons.length - 1
          : (index + (event.key === "ArrowRight" ? 1 : -1) + buttons.length) % buttons.length;
        buttons[next].focus();
        activate(buttons[next]);
      });
    });
    const requested = location.hash.match(/^#version-(.+)$/)?.[1];
    const initial = buttons.find(button => button.dataset.songVersionKey === requested);
    if (initial) activate(initial, false);
  });

  // Songs page filter (audit A9). The box, the song data and the matching rule are shared with
  // every other search (shared/web-search-box.js, web-song-search.js, web-site-search-variants.js).
  // Hangul is compared syllable by syllable, never as Korean.
  const filter = document.querySelector("[data-song-filter]");
  if (filter && window.TliSearchBox && window.TliSongSearch) {
    const chips = [...filter.querySelectorAll("[data-song-filter-category]")];
    const summary = filter.querySelector(".song-filter-summary");
    const empty = filter.querySelector(".song-filter-empty");
    const catalogue = document.querySelector(".song-catalogue");
    const sections = [...catalogue.querySelectorAll(".song-category")];
    const rows = sections.flatMap(section => [...section.querySelectorAll("li[data-song-route]")].map(row => ({
      row, section, route: row.dataset.songRoute,
      mandarinMatch: row.querySelector(".song-entry-mandarin-match"),
      match: row.querySelector(".song-entry-match"),
      matchMain: row.querySelector(".song-entry-match-main"),
      matchLomari: row.querySelector(".song-entry-match-lomari"),
    })));
    let matcher = null;
    let category = new URL(location.href).searchParams.get("category") || "";
    if (!chips.some(chip => chip.dataset.songFilterCategory === category)) category = "";
    const showCategory = () => chips.forEach(chip => chip.setAttribute("aria-pressed", String(chip.dataset.songFilterCategory === category)));
    const apply = () => {
      if (!matcher) return;
      const query = box.value();
      const results = new Map(matcher.search(query, { category }).map(result => [result.song.route, result]));
      rows.forEach(item => {
        const result = results.get(item.route);
        item.row.hidden = !result;
        if (item.mandarinMatch) {
          item.mandarinMatch.hidden = !result?.mandarinMatch;
          if (result?.mandarinMatch) item.mandarinMatch.textContent = `(${result.song.mandarinTitle})`;
        }
        const lyricMatch = result?.lineMatch;
        if (item.match) item.match.hidden = !lyricMatch;
        if (lyricMatch) {
          if (lyricMatch.mainHtml) {
            item.matchMain.innerHTML = lyricMatch.mainHtml;
            normalizeRuby(item.matchMain);
          } else {
            item.matchMain.textContent = lyricMatch.main;
          }
          item.matchLomari.textContent = lyricMatch.lomari;
        }
      });
      sections.forEach(section => {
        const count = section.querySelectorAll("li[data-song-route]:not([hidden])").length;
        section.hidden = count === 0;
        const badge = section.querySelector(".song-category-heading > span");
        if (badge) badge.textContent = String(count).padStart(2, "0");
      });
      const shown = results.size;
      const filtering = Boolean(query || category);
      catalogue.classList.toggle("is-filtering", filtering);
      empty.hidden = shown > 0;
      summary.textContent = filtering && shown ? filter.dataset.countTemplate.replace("{n}", shown) : "";
    };
    const box = window.TliSearchBox.mount(document.querySelector(".songs-subheader [data-tli-search]"), { queryParam: "q", onChange: apply });
    chips.forEach(chip => chip.addEventListener("click", () => {
      category = chip.dataset.songFilterCategory;
      showCategory();
      const url = new URL(location.href);
      if (category) url.searchParams.set("category", category); else url.searchParams.delete("category");
      history.replaceState(history.state, "", url);
      apply();
    }));
    showCategory();
    Promise.all([window.TliSongSearch.loadIndex(), window.TliSiteSearchVariants.loadHanriFold()])
      .then(([index, hanriFold]) => { matcher = window.TliSongSearch.createMatcher(index, hanriFold); apply(); })
      .catch(error => console.error("Song search could not load", error));
  }
  // A song page's search box (in the Songs sub-header): a dropdown of matching songs, from the same
  // index and by the same rule as the /songs/ filter.
  const headerSearch = document.querySelector("#songSearchInput")?.closest("[data-tli-search]");
  if (headerSearch && window.TliSearchBox && window.TliSongSearch) {
    const language = document.documentElement.lang || "en";
    const limit = 8;
    let matcher = null;
    let categories = {};
    const songHref = (song, line) => {
      const base = song.urls[language] || song.urls.en;
      return line && line.anchor > 0 ? `${base}#line-${line.anchor}` : base;
    };
    window.TliSearchBox.mount(headerSearch, {
      results: "dropdown",
      dropdown: {
        prepare: async () => {
          const [index, hanriFold] = await Promise.all([window.TliSongSearch.loadIndex(), window.TliSiteSearchVariants.loadHanriFold()]);
          categories = index.categories;
          matcher = window.TliSongSearch.createMatcher(index, hanriFold);
        },
        search: query => {
          const all = matcher ? matcher.search(query) : [];
          return { items: all.slice(0, limit), total: all.length };
        },
        render: ({ song, lineMatch }) => {
          const link = document.createElement("a");
          link.className = "tli-search-song";
          link.href = songHref(song, lineMatch);
          const title = document.createElement("span");
          title.className = "tli-search-song-title title-reading";
          title.innerHTML = song.label;
          const category = document.createElement("small");
          category.className = "tli-search-song-category";
          category.textContent = (categories[song.category] || {})[language] || (categories[song.category] || {}).en || "";
          link.append(title, category);
          if (lineMatch) {
            const snippet = document.createElement("span");
            snippet.className = "tli-search-song-line";
            const main = document.createElement("span");
            main.textContent = lineMatch.main;
            const lomari = document.createElement("small");
            lomari.textContent = lineMatch.lomari;
            snippet.append(main, lomari);
            link.append(snippet);
          }
          window.TliSiteDisplay.decorate(link);
          return link;
        },
      },
    });
  }

  // #line-N (from a search result): scroll to that lyric line and flash it.
  const lineTarget = /^#line-(\d+)$/.exec(location.hash);
  if (lineTarget && document.body.dataset.siteSection === "songs") {
    const scope = document.querySelector('[role="tabpanel"]') || article;
    const showLine = () => {
      const line = scope.querySelectorAll("p:has(> .lyric-line)")[Number(lineTarget[1]) - 1];
      if (!line) return;
      line.scrollIntoView({ block: "center" });
      line.classList.add("is-search-target");
      setTimeout(() => line.classList.remove("is-search-target"), 2600);
    };
    showLine();
    document.fonts?.ready.then(showLine);
  }
})();

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

  // Songs page filter (audit A9). Matching ignores case, Lomari diacritics, TLI tone
  // marks, spaces and hyphens; Hangul is compared syllable by syllable, never as Korean.
  const filter = document.querySelector("[data-song-filter]");
  if (filter) {
    const language = document.documentElement.lang;
    const labels = language === "zh-Hant"
      ? { filter: "篩選歌曲", keyboard: "啟用諺文鍵盤", candidates: "漢字候選詞" }
      : language === "zh-Hans"
        ? { filter: "筛选歌曲", keyboard: "启用谚文键盘", candidates: "汉字候选词" }
        : { filter: "Filter songs", keyboard: "Enable Hangul keyboard", candidates: "Hanri candidates" };
    let hanriFold = {};
    try { hanriFold = JSON.parse(filter.dataset.songHanriFold || "{}"); } catch {}
    const fold = value => [...String(value || "").normalize("NFKD")
      .replace(/[̀-ͯ]/gu, "").replace(/[ˆˋˊˉˇˍˎˏˬꞈ`\s\-’'‘]/gu, "").toLowerCase().normalize("NFC")]
      .map(char => hanriFold[char] || char).join("");
    const input = filter.querySelector(".song-filter-input");
    input.id ||= "songFilterInput";
    const heading = document.createElement("div");
    heading.className = "song-filter-heading";
    const label = document.createElement("label");
    label.htmlFor = input.id;
    label.textContent = labels.filter;
    const toggle = document.createElement("button");
    toggle.className = "hangul-keyboard-toggle";
    toggle.type = "button";
    toggle.setAttribute("aria-pressed", "false");
    toggle.innerHTML = `<span class="toggle-label">${labels.keyboard}</span><span class="toggle-switch" aria-hidden="true"><span class="toggle-knob"></span></span>`;
    heading.append(label, toggle);
    const inputWrap = document.createElement("div");
    inputWrap.className = "song-filter-input-wrap";
    const candidates = document.createElement("div");
    candidates.id = "songFilterCandidates";
    candidates.className = "hanri-candidate-menu";
    candidates.setAttribute("role", "listbox");
    candidates.setAttribute("aria-label", labels.candidates);
    candidates.hidden = true;
    input.before(heading, inputWrap);
    inputWrap.append(input, candidates);
    const chips = [...filter.querySelectorAll("[data-song-filter-category]")];
    const summary = filter.querySelector(".song-filter-summary");
    const empty = filter.querySelector(".song-filter-empty");
    const catalogue = document.querySelector(".song-catalogue");
    const sections = [...catalogue.querySelectorAll(".song-category")];
    const rows = sections.flatMap(section => [...section.querySelectorAll("li[data-song-search]")]
      .map(row => {
        let sourceLines = [];
        try { sourceLines = JSON.parse(row.dataset.songLines || "[]"); } catch {}
        const lines = sourceLines.map(([main, lomari, search, mainHtml]) => ({
          main, mainHtml, lomari, text: fold(search),
        }));
        const titleText = fold(row.dataset.songSearch);
        return {
          row, section, titleText, lines,
          text: [titleText, ...lines.map(line => line.text)].join(" "),
          match: row.querySelector(".song-entry-match"),
          matchMain: row.querySelector(".song-entry-match-main"),
          matchLomari: row.querySelector(".song-entry-match-lomari"),
        };
      }));
    let category = "";
    const apply = () => {
      const query = fold(input.value);
      let shown = 0;
      rows.forEach(item => {
        const visible = (!category || item.section.dataset.songCategory === category) && (!query || item.text.includes(query));
        item.row.hidden = !visible;
        const lyricMatch = visible && query ? item.lines.find(line => line.text.includes(query)) : null;
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

    const loadScript = src => new Promise((resolve, reject) => {
      const existing = [...document.scripts].find(script => new URL(script.src, location.href).pathname === src);
      if (existing) {
        if (existing.dataset.loaded === "true" || existing.readyState === "complete") resolve();
        else {
          existing.addEventListener("load", resolve, { once: true });
          existing.addEventListener("error", reject, { once: true });
        }
        return;
      }
      const script = document.createElement("script");
      script.src = src;
      script.addEventListener("load", () => { script.dataset.loaded = "true"; resolve(); }, { once: true });
      script.addEventListener("error", reject, { once: true });
      document.head.append(script);
    });
    const setupIme = async () => {
      if (!window.TangliengimHangulIme) await loadScript("/shared/web-hangul-ime.js");
      if (!window.TangliengimImeCore) await loadScript("/shared/web-ime-core.js");
      const imeCore = window.TangliengimImeCore;
      let enabled = false;
      const popup = imeCore.createCandidatePopupPositioner({
        control: input,
        container: candidates,
        boundary: inputWrap,
        placement: "below",
      });
      const controller = imeCore.createTextImeController({
        control: input,
        candidateContainer: candidates,
        entries: [],
        enabled: () => enabled,
        onUpdate: apply,
        onCandidatesChanged: popup.schedule,
        enterBehavior: "none",
      });
      toggle.addEventListener("click", () => {
        enabled = !enabled;
        toggle.setAttribute("aria-pressed", String(enabled));
        input.classList.toggle("hangul-ime-active", enabled);
        controller.setEnabled();
        input.focus();
      });
      const response = await fetch("/public/data/hokkien-hanri-dict.json", { cache: "no-cache" });
      if (!response.ok) throw new Error(`Dictionary request failed: ${response.status}`);
      const data = await response.json();
      const entries = data.entries || [];
      controller.setEntries(entries, imeCore.createDictionaryIndex(entries));
    };
    setupIme().catch(error => console.error("Songs TLI IME could not load", error));
  }
})();

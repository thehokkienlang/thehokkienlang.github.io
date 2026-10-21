(() => {
  const requested = new URLSearchParams(location.search).get("lang");
  const language = location.pathname.startsWith("/zh-hant/") ? "zh-Hant"
    : location.pathname.startsWith("/zh-hans/") ? "zh-Hans"
    : ["zh-Hant", "zh-Hans"].includes(requested) ? requested : "en";
  const simplified = language === "zh-Hans";
  const messages = {
    "Dictionary": ["詞典", "词典"], "IME Pad": ["輸入法", "输入法"],
    "Open IME": ["開啟輸入法", "打开输入法"], "Songs": ["歌曲", "歌曲"],
    "Original WordPress page": ["原 WordPress 頁面", "原 WordPress 页面"],
    "Skip to content": ["跳至內容", "跳至内容"], "Search": ["搜尋", "搜索"],
    "Enable Hangul keyboard": ["啟用諺文鍵盤", "启用谚文键盘"],
    "Browse:": ["分類：", "分类："], "Food": ["飲食", "饮食"], "Place names": ["地名", "地名"],
    "Password": ["密碼", "密码"], "Enter dictionary": ["進入詞典", "进入词典"],
    "Lock dictionary": ["鎖定詞典", "锁定词典"],
    "This dictionary is currently available to invited visitors.": ["本詞典目前僅供受邀訪客使用。", "本词典目前仅供受邀访客使用。"],
    "That password is not correct.": ["密碼不正確。", "密码不正确。"],
    "The dictionary could not be opened. Please try again.": ["無法開啟詞典，請重試。", "无法打开词典，请重试。"],
    "This website is still under construction. Entries, translations, and features are being actively refined.": ["本網站仍在建置中，詞條、翻譯與功能將持續完善。", "本网站仍在建设中，词条、翻译与功能将持续完善。"],
    "Search Hanri, Hangul, Lomari, or English...": ["搜尋漢字、諺文、羅馬字或英文…", "搜索汉字、谚文、罗马字或英文…"],
    "Type 漢字, 한글, Lomari, or English...": ["輸入漢字、諺文、羅馬字或英文…", "输入汉字、谚文、罗马字或英文…"],
    "Clear search": ["清除搜尋", "清除搜索"], "Clear text": ["清除文字", "清除文字"],
    "Hanri + Hangul": ["漢字＋諺文", "汉字＋谚文"], "Type here...": ["在此輸入…", "在此输入…"],
    "Sandhi:": ["變調：", "变调："], "Taipei": ["臺北", "台北"], "Singapore": ["新加坡", "新加坡"],
    "Keyboard guide": ["鍵盤初學", "键盘初学"], "Lomari mode": ["羅馬字提示", "罗马字提示"],
    "Lomari": ["羅馬字", "罗马字"], "English": ["英文", "英文"],
    "Listen": ["聆聽", "收听"], "Copy": ["複製", "复制"], "Stop": ["停止", "停止"],
    "Copy text": ["複製文字", "复制文字"], "Play audio": ["播放語音", "播放语音"], "Stop audio": ["停止語音", "停止语音"],
    "Loading dictionary...": ["正在載入詞典…", "正在加载词典…"], "Loading entries...": ["正在載入詞條…", "正在加载词条…"],
    "No matching entries yet": ["找不到相符詞條", "找不到匹配词条"],
    "Try Hanri, Tangliengim Hangul, Lomari, or English meanings.": ["試試漢字、東寧音諺文、羅馬字或英文釋義。", "试试汉字、东宁音谚文、罗马字或英文释义。"],
    "Dictionary failed to load": ["詞典載入失敗", "词典加载失败"],
    "The dictionary could not load. Please refresh and try again.": ["無法載入詞典，請重新整理後再試。", "无法加载词典，请刷新后重试。"],
    "Reading copied": ["已複製讀音", "已复制读音"], "Text copied": ["已複製文字", "已复制文字"],
    "Could not copy reading": ["無法複製讀音", "无法复制读音"], "Could not play audio": ["無法播放語音", "无法播放语音"],
    "No audio for this reading": ["此讀音暫無語音", "此读音暂无语音"],
    "Copied": ["已複製", "已复制"], "Could not copy": ["無法複製", "无法复制"],
    "No text to play": ["尚無可播放的文字", "尚无可播放的文字"],
    "Dictionary candidates unavailable; Hangul typing still works": ["無法載入詞典候選，仍可輸入諺文", "无法加载词典候选，仍可输入谚文"],
    "Listen to": ["聆聽", "收听"], "No audio for": ["暫無語音：", "暂无语音："],
  };
  const text = value => {
    if (language === "en") return value;
    if (messages[value]) return messages[value][simplified ? 1 : 0];
    let match;
    if ((match = /^(\d+) active TSV entries$/.exec(value))) return `${match[1]} ${simplified ? "个有效词条" : "個有效詞條"}`;
    if ((match = /^(Hanri|Hangul|Mixed) · (\d+) readings?$/.exec(value))) return `${(simplified ? {Hanri: "汉字", Hangul: "谚文", Mixed: "混写"} : {Hanri: "漢字", Hangul: "諺文", Mixed: "混寫"})[match[1]]} · ${match[2]} ${simplified ? "种读音" : "種讀音"}`;
    if ((match = /^(.*?)(\d+) results?(?: · showing (\d+)-(\d+))?$/.exec(value))) return `${match[1]}${match[2]} ${simplified ? "个结果" : "個結果"}${match[3] ? ` · ${match[3]}–${match[4]}` : ""}`;
    if ((match = /^\+(\d+) more readings$/.exec(value))) return `+${match[1]} ${simplified ? "种读音" : "種讀音"}`;
    if ((match = /^No entries in (.*) match this search\.$/.exec(value))) return `${text(match[1])}：${simplified ? "找不到匹配词条" : "找不到相符詞條"}`;
    return value;
  };
  const href = value => {
    const url = new URL(value, location.href);
    if (url.origin !== location.origin || !/^\/(?:dictionary|ime|songs|read\/literature)\//.test(url.pathname)) return value;
    if (language === "en") url.searchParams.delete("lang");
    else url.searchParams.set("lang", language);
    return url.pathname + url.search + url.hash;
  };
  document.documentElement.lang = language;
  document.querySelectorAll('nav[aria-label="Main navigation"]').forEach(nav => {
    const variant = nav.querySelector(`template[data-navigation-language="${language}"]`);
    if (variant) nav.replaceChildren(variant.content.cloneNode(true));
    nav.querySelectorAll("[data-language-choice]").forEach(link => {
      const target = new URL(link.href);
      if (target.pathname === location.pathname) {
        for (const [key, value] of new URLSearchParams(location.search)) {
          if (key !== "lang") target.searchParams.set(key, value);
        }
        target.hash = location.hash;
        link.href = target.pathname + target.search + target.hash;
        link.addEventListener("click", () => {
          const input = document.querySelector(location.pathname.startsWith("/dictionary/") ? "#searchInput" : "#imeText");
          if (!input) return;
          const destination = new URL(link.href);
          destination.searchParams.set(location.pathname.startsWith("/dictionary/") ? "q" : "text", input.value);
          link.href = destination.pathname + destination.search + destination.hash;
        });
      }
    });
  });
  const apply = (root = document) => {
    root.querySelectorAll("[data-site-text]").forEach(node => { node.textContent = text(node.dataset.siteText); });
    const labels = {
      ".site-app-header h1": location.pathname.startsWith("/dictionary/") ? "Dictionary" : "IME Pad",
      ".search-label": "Search", ".toggle-label": "Enable Hangul keyboard", ".category-title": "Browse:",
      "label[for=passwordInput]": "Password", "#enterDictionaryButton": "Enter dictionary",
      "#lockDictionaryButton": "Lock dictionary", ".lock-note": "This dictionary is currently available to invited visitors.",
      ".construction-notice": "This website is still under construction. Entries, translations, and features are being actively refined.",
      ".pad-label": "Hanri + Hangul", ".sandhi-label": "Sandhi:", "#taipeiButton": "Taipei", "#singaporeButton": "Singapore",
      "#keyboardGuideButton > span:first-child": "Keyboard guide", "#keyboardGuideOptions > span": "Lomari mode",
      "#dataStatus": "Loading dictionary...", "#resultSummary": "Loading entries...",
    };
    for (const [selector, label] of Object.entries(labels)) root.querySelectorAll(selector).forEach(node => { node.textContent = text(label); });
    for (const [selector, attribute, label] of [
      ["#searchInput", "placeholder", "Type 漢字, 한글, Lomari, or English..."],
      ["#imeText", "placeholder", "Type here..."], ["#clearButton", "aria-label", location.pathname.startsWith("/dictionary/") ? "Clear search" : "Clear text"],
      ["#copyButton", "title", "Copy text"], ["#copyButton", "aria-label", "Copy text"],
      ["#audioButton", "title", "Listen"], ["#audioButton", "aria-label", "Play audio"],
    ]) root.querySelectorAll(selector).forEach(node => { node.setAttribute(attribute, text(label)); });
    root.querySelectorAll('a[href^="/"]').forEach(link => {
      if (!link.closest("nav") && !link.matches("[data-language-choice]")) link.setAttribute("href", href(link.getAttribute("href")));
    });
    const brand = root.querySelector(".site-brand");
    if (brand) brand.href = language === "en" ? "/" : language === "zh-Hant" ? "/zh-hant/" : "/zh-hans/";
  };
  window.TliSiteLanguage = {language, text, href, apply};
  apply();
})();

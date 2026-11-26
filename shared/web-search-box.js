(function (root) {
  'use strict';
  // The one search box. The markup comes from search_box_html() in tools/build_content.py; this
  // attaches to it: the Hangul keyboard switch, the × clear button, the Hanri candidate menu and
  // the TLI input controller, plus ?q= in the address bar. Each page decides what to do with the
  // query through options.onChange.

  const KEYBOARD_ON_LABELS = {
    en: 'Hangul key on',
    'zh-Hant': '諺文鍵盤已開啟',
    'zh-Hans': '谚文键盘已开启',
  };

  const KEYBOARD_PREFERENCE_KEY = 'tli-search-hangul';
  const mountedKeyboards = new Map();
  let storage;
  let preferredKeyboard = false;
  try {
    storage = root.localStorage;
    preferredKeyboard = storage?.getItem(KEYBOARD_PREFERENCE_KEY) === 'on';
  }
  catch { /* Use the page default when storage is unavailable. */ }

  function syncKeyboardPreference(enabled) {
    preferredKeyboard = enabled;
    for (const [box, apply] of mountedKeyboards) {
      if (box.isConnected === false) mountedKeyboards.delete(box);
      else apply(enabled);
    }
  }

  function saveKeyboardPreference(enabled) {
    try { storage?.setItem(KEYBOARD_PREFERENCE_KEY, enabled ? 'on' : 'off'); }
    catch { /* The choice still applies to this page. */ }
    syncKeyboardPreference(enabled);
  }

  root.addEventListener?.('storage', event => {
    if (event.storageArea === storage && (event.key === KEYBOARD_PREFERENCE_KEY || event.key === null)) {
      syncKeyboardPreference(event.newValue === 'on');
    }
  });

  const loadScript = src => new Promise((resolve, reject) => {
    const existing = [...document.scripts].find(script => script.src && new URL(script.src, location.href).pathname === src);
    if (existing) {
      if (existing.dataset.loaded === 'true' || existing.readyState === 'complete') resolve();
      else {
        existing.addEventListener('load', resolve, {once: true});
        existing.addEventListener('error', reject, {once: true});
      }
      return;
    }
    const script = document.createElement('script');
    script.src = src;
    script.addEventListener('load', () => { script.dataset.loaded = 'true'; resolve(); }, {once: true});
    script.addEventListener('error', reject, {once: true});
    document.head.append(script);
  });

  async function loadEntries(options) {
    // `entries` may be an array, or a promise of one or of {entries, index} (a page that loads the
    // dictionary itself and has its own lookup index).
    if (options.entries) {
      const loaded = await options.entries;
      return Array.isArray(loaded)
        ? {entries: loaded, index: options.dictionaryIndex || null}
        : {entries: loaded.entries || [], index: loaded.index || null};
    }
    const response = await fetch(options.dictionaryUrl || '/public/data/hokkien-hanri-dict.json', {cache: 'no-cache'});
    if (!response.ok) throw new Error(`Dictionary request failed: ${response.status}`);
    const data = await response.json();
    return {entries: data.entries || [], index: null};
  }

  function mount(host, options = {}) {
    const box = host.matches('[data-tli-search]') ? host : host.querySelector('[data-tli-search]');
    if (!box) throw new Error('TliSearchBox.mount needs the markup from search_box_html().');
    if (options.keyboardMode && !['switch', 'modes'].includes(options.keyboardMode)) {
      throw new Error(`Unknown keyboard mode "${options.keyboardMode}".`);
    }
    const input = box.querySelector('.tli-search-input');
    const clearButton = box.querySelector('.tli-search-clear');
    const toggle = box.querySelector('.hangul-keyboard-toggle');
    const candidates = box.querySelector('.hanri-candidate-menu');
    const wrap = box.querySelector('.tli-search-input-wrap');
    const keyboardHint = toggle?.hasAttribute('aria-label') ? document.createElement('span') : null;
    if (keyboardHint) {
      keyboardHint.className = 'tli-keyboard-on-hint';
      keyboardHint.setAttribute('role', 'status');
      keyboardHint.setAttribute('aria-live', 'polite');
      keyboardHint.textContent = KEYBOARD_ON_LABELS[document.documentElement.lang] || KEYBOARD_ON_LABELS.en;
      // Keep the bubble inside its compact pill so its position follows that exact control.
      // Compact pills have an aria-label, so this status text does not alter their accessible name.
      toggle.append(keyboardHint);
    }
    let keyboardHintTimer;
    // Show the labels in the page's language (a song page is switched to it after it is built).
    const table = JSON.parse(box.dataset.labels || '{}')[document.documentElement.lang];
    if (table) {
      box.querySelector('label').textContent = table.label;
      input.placeholder = table.placeholder;
      clearButton.setAttribute('aria-label', table.clear);
      if (toggle) {
        toggle.querySelector('.toggle-label').textContent = table.keyboard;
        if (toggle.hasAttribute('aria-label')) { toggle.setAttribute('aria-label', table.keyboard); toggle.setAttribute('title', table.keyboard); }
      }
      candidates.setAttribute('aria-label', table.candidates);
      if (table.more) { box.dataset.moreLabel = table.more; box.dataset.emptyLabel = table.empty; }
      box.querySelector('.tli-search-dropdown')?.setAttribute('aria-label', table.label);
    }
    const list = options.results === 'dropdown' ? box.querySelector('.tli-search-dropdown') : null;
    if (options.results === 'dropdown' && !list) throw new Error('results: "dropdown" needs search_box_html(results="dropdown").');
    let lastQuery = null;
    let controller = null;
    let active = -1;
    let prepared = null;
    let refreshToken = 0;

    // The results dropdown: options.dropdown = {limit, prepare(), search(query) -> {items, total},
    // render(item) -> an <a href>}. The page supplies the data and how an item looks; the box
    // supplies the list, ↑/↓/Enter/Esc, and a last "See all N results" row.
    const prepare = () => (prepared ||= Promise.resolve(options.dropdown.prepare?.()));
    const rows = () => list ? [...list.querySelectorAll('[role="option"]')] : [];
    const setActive = index => {
      const all = rows();
      active = all.length ? (index + all.length) % all.length : -1;
      all.forEach((row, i) => {
        row.setAttribute('aria-selected', String(i === active));
        row.classList.toggle('is-active', i === active);
      });
      if (active >= 0) {
        input.setAttribute('aria-activedescendant', all[active].id);
        all[active].scrollIntoView({block: 'nearest'});
      } else input.removeAttribute('aria-activedescendant');
    };
    const closeList = () => {
      if (!list) return;
      list.hidden = true;
      input.setAttribute('aria-expanded', 'false');
      setActive(-1);
    };
    const moreUrl = query => {
      const url = new URL(box.dataset.moreHref || '/songs/', location.href);
      url.searchParams.set(options.queryParam || 'q', query);
      const path = url.pathname + url.search;
      // A page shown in another language keeps that language (TliSiteLanguage.href adds ?lang=).
      return root.TliSiteLanguage ? root.TliSiteLanguage.href(path) : path;
    };
    const refreshList = async () => {
      if (!list) return;
      const query = input.value;
      const token = ++refreshToken;
      if (!query.trim()) { closeList(); return; }
      try { await prepare(); } catch { return; }
      if (token !== refreshToken) return;
      const {items, total} = await options.dropdown.search(query);
      if (token !== refreshToken) return;
      const nodes = items.map((item, i) => {
        const node = options.dropdown.render(item);
        node.setAttribute('role', 'option');
        node.id = `${input.id}-option-${i}`;
        return node;
      });
      if (!nodes.length) {
        const message = document.createElement('div');
        message.className = 'tli-search-empty';
        message.textContent = box.dataset.emptyLabel || '';
        list.replaceChildren(message);
      } else {
        if (total > nodes.length) {
          const more = document.createElement('a');
          more.className = 'tli-search-more';
          more.href = moreUrl(query);
          more.setAttribute('role', 'option');
          more.id = `${input.id}-option-more`;
          more.textContent = (box.dataset.moreLabel || '').replace('{n}', total);
          nodes.push(more);
        }
        list.replaceChildren(...nodes);
      }
      list.hidden = false;
      input.setAttribute('aria-expanded', 'true');
      active = -1;
    };
    if (list) {
      // The song index is fetched the first time the box is used, not when the page loads.
      input.addEventListener('focus', () => { prepare().catch(() => {}); });
      input.addEventListener('keydown', event => {
        if (event.defaultPrevented || event.isComposing) return;
        // While the Hanri candidate menu is open its keys belong to the keyboard.
        if (!candidates.hidden) return;
        const open = !list.hidden;
        if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
          if (!open) return;
          event.preventDefault();
          setActive(active < 0 ? (event.key === 'ArrowDown' ? 0 : -1) : active + (event.key === 'ArrowDown' ? 1 : -1));
        } else if (event.key === 'Enter') {
          if (!input.value.trim()) return;
          event.preventDefault();
          const target = open && active >= 0 ? rows()[active] : null;
          location.href = target ? target.href : moreUrl(input.value);
        } else if (event.key === 'Escape' && open) {
          event.preventDefault();
          closeList();
        }
      });
      document.addEventListener('pointerdown', event => { if (!box.contains(event.target)) closeList(); });
      box.addEventListener('focusout', event => { if (!box.contains(event.relatedTarget)) closeList(); });
    }

    const writeUrl = () => {
      if (!options.queryParam) return;
      const url = new URL(location.href);
      if (input.value) url.searchParams.set(options.queryParam, input.value);
      else url.searchParams.delete(options.queryParam);
      history.replaceState(history.state, '', url);
    };
    const changed = () => {
      clearButton.hidden = !input.value;
      if (input.value === lastQuery) return;
      lastQuery = input.value;
      writeUrl();
      options.onChange?.(input.value);
      refreshList();
    };
    input.addEventListener('input', changed);
    clearButton.addEventListener('click', () => {
      input.value = '';
      controller?.syncComposerFromControl?.();
      changed();
      input.focus();
    });

    // The Hangul keyboard: an on/off switch or, with keyboardMode "modes", a choice named "lomari"
    // (off) or "hanri-hangul" (on) that the page hears of through onModeChange (the dictionary
    // ranks its results by it).
    let enabled = false;
    const setEnabled = (value) => {
      if (value === enabled) return;
      enabled = value;
      if (!enabled) {
        clearTimeout(keyboardHintTimer);
        keyboardHint?.classList.remove('is-visible');
      }
      toggle?.setAttribute('aria-pressed', String(enabled));
      input.classList.toggle('hangul-ime-active', enabled);
      controller?.setEnabled();
      if (enabled && document.activeElement === input) start();
      if (options.keyboardMode === 'modes') options.onModeChange?.(enabled ? 'hanri-hangul' : 'lomari');
    };
    toggle?.addEventListener('click', () => {
      saveKeyboardPreference(!enabled);
      clearTimeout(keyboardHintTimer);
      keyboardHint?.classList.remove('is-visible');
      if (enabled && keyboardHint) {
        keyboardHint.classList.add('is-visible');
        keyboardHintTimer = setTimeout(() => keyboardHint.classList.remove('is-visible'), 1800);
      }
      input.focus();
    });

    const api = {
      input,
      box,
      candidates,
      value: () => input.value,
      setValue(query) {
        input.value = query;
        controller?.syncComposerFromControl?.();
        changed();
      },
      clear() { api.setValue(''); },
      focus() { input.focus(); },
      mode: () => (enabled ? 'hanri-hangul' : 'lomari'),
      setMode(mode) { saveKeyboardPreference(mode === 'hanri-hangul'); },
      renderCandidates() { controller?.renderCandidates?.(); },
      get controller() { return controller; },
      // Resolves to the IME controller once the keyboard is ready; the box works as a plain search
      // box before then. Reading it starts the keyboard if it has not started yet.
      get ready() { return startKeyboard(); },
    };

    if (options.queryParam) {
      const initial = new URL(location.href).searchParams.get(options.queryParam);
      if (initial) input.value = initial.slice(0, 12000);
    }
    clearButton.hidden = !input.value;

    // The keyboard and its dictionary (several MB) load straight away on a search page, but a
    // dropdown box (song pages) waits until the visitor first uses it, so a page nobody searches
    // from stays light.
    let keyboard = null;
    const startKeyboard = () => (keyboard ||= loadKeyboard());
    const loadKeyboard = async () => {
      if (!root.TangliengimHangulIme) await loadScript('/shared/web-hangul-ime.js');
      if (!root.TangliengimImeCore) await loadScript('/shared/web-ime-core.js');
      const imeCore = root.TangliengimImeCore;
      const popup = imeCore.createCandidatePopupPositioner({
        control: input, container: candidates, boundary: wrap, placement: 'below',
      });
      controller = imeCore.createTextImeController({
        control: input,
        candidateContainer: candidates,
        entries: [],
        enabled: () => enabled,
        onUpdate: changed,
        onCandidatesChanged: popup.schedule,
        enterBehavior: 'none',
      });
      if (input.value) controller.syncComposerFromControl?.();
      if (enabled) controller.setEnabled();
      const {entries, index} = await loadEntries(options);
      await controller.preferences?.ready;
      controller.setEntries(entries, index || imeCore.createDictionaryIndex(entries));
      return controller;
    };
    const start = () => startKeyboard().catch(error => console.error('The search keyboard could not load', error));
    mountedKeyboards.set(box, setEnabled);
    setEnabled(preferredKeyboard);
    if (options.deferKeyboard) {
      input.addEventListener('focus', () => { if (enabled) start(); });
      toggle?.addEventListener('click', () => { if (enabled) start(); });
    } else if (list && !input.value) {
      input.addEventListener('focus', start, {once: true});
      toggle?.addEventListener('click', start, {once: true});
    } else start();

    // A page opened with ?q= filters straight away.
    if (input.value) changed();
    return api;
  }

  root.TliSearchBox = {mount};
})(typeof window !== 'undefined' ? window : globalThis);

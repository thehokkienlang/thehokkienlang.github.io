(function (root) {
  'use strict';
  // The one search box. The markup comes from search_box_html() in tools/build_content.py; this
  // attaches to it: the Hangul keyboard switch, the × clear button, the Hanri candidate menu and
  // the TLI input controller, plus ?q= in the address bar. Each page decides what to do with the
  // query through options.onChange.

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
    if (options.entries) return {entries: options.entries, index: options.dictionaryIndex || null};
    const response = await fetch(options.dictionaryUrl || '/public/data/hokkien-hanri-dict.json', {cache: 'no-cache'});
    if (!response.ok) throw new Error(`Dictionary request failed: ${response.status}`);
    const data = await response.json();
    return {entries: data.entries || [], index: null};
  }

  function mount(host, options = {}) {
    const box = host.matches('[data-tli-search]') ? host : host.querySelector('[data-tli-search]');
    if (!box) throw new Error('TliSearchBox.mount needs the markup from search_box_html().');
    if (options.keyboardMode && options.keyboardMode !== 'switch') {
      throw new Error(`Keyboard mode "${options.keyboardMode}" is not available yet.`);
    }
    const input = box.querySelector('.tli-search-input');
    const clearButton = box.querySelector('.tli-search-clear');
    const toggle = box.querySelector('.hangul-keyboard-toggle');
    const candidates = box.querySelector('.hanri-candidate-menu');
    const wrap = box.querySelector('.tli-search-input-wrap');
    let lastQuery = null;
    let controller = null;

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
    };
    input.addEventListener('input', changed);
    clearButton.addEventListener('click', () => {
      input.value = '';
      controller?.syncComposerFromControl?.();
      changed();
      input.focus();
    });

    const api = {
      input,
      box,
      value: () => input.value,
      setValue(query) {
        input.value = query;
        controller?.syncComposerFromControl?.();
        changed();
      },
      clear() { api.setValue(''); },
      focus() { input.focus(); },
      // Resolves once the keyboard is ready; the box works as a plain search box before then.
      ready: null,
    };

    if (options.queryParam) {
      const initial = new URL(location.href).searchParams.get(options.queryParam);
      if (initial) input.value = initial;
    }
    clearButton.hidden = !input.value;

    api.ready = (async () => {
      if (!root.TangliengimHangulIme) await loadScript('/shared/web-hangul-ime.js');
      if (!root.TangliengimImeCore) await loadScript('/shared/web-ime-core.js');
      const imeCore = root.TangliengimImeCore;
      let enabled = false;
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
      toggle.addEventListener('click', () => {
        enabled = !enabled;
        toggle.setAttribute('aria-pressed', String(enabled));
        input.classList.toggle('hangul-ime-active', enabled);
        controller.setEnabled();
        input.focus();
      });
      const {entries, index} = await loadEntries(options);
      controller.setEntries(entries, index || imeCore.createDictionaryIndex(entries));
    })();
    api.ready.catch(error => console.error('The search keyboard could not load', error));

    // A page opened with ?q= filters straight away.
    if (input.value) changed();
    return api;
  }

  root.TliSearchBox = {mount};
})(typeof window !== 'undefined' ? window : globalThis);

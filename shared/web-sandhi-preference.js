(function (root) {
  'use strict';
  // The site-wide sandhi preference: Taipei or Singapore. It changes how tone sandhi sounds and is
  // marked for the reader; it never changes stored readings, which stay Taipei (docs/sandhi-toggle-plan.md).
  //
  // Stored per visitor in localStorage ('tli-sandhi'), read inside try/catch so a blocked store falls
  // back to the default. It is not put in the URL, so a shared link doesn't force a dialect on the
  // person opening it. Visitors without a saved choice default to Taipei.

  const STORAGE_KEY = 'tli-sandhi';
  const MODES = Object.freeze(['taipei', 'singapore']);
  const CHANGE_EVENT = 'tli-sandhi-change';

  // The labels, in the three site languages. The header menu is written by tools/build_content.py
  // from its own copy; tests/check_sandhi_preference.cjs checks the two agree.
  const LABELS = Object.freeze({
    en: {sandhi: 'Tone pattern', change: '', term: 'tone sandhi', taipei: 'Taipei', singapore: 'Singapore',
      note: 'Changes how tone sandhi is marked.'},
    'zh-Hant': {sandhi: '聲調形式', change: '', term: '變調', taipei: '臺北', singapore: '新加坡',
      note: '調整變調的標示方式。'},
    'zh-Hans': {sandhi: '声调形式', change: '', term: '变调', taipei: '台北', singapore: '新加坡',
      note: '调整变调的标示方式。'},
  });

  function browserStorage() {
    try { return root.localStorage; } catch (_error) { return null; }
  }

  // storage and target are injectable so the rules can be tested without a browser.
  function createPreference({storage = browserStorage(), target = root} = {}) {
    const listeners = new Set();
    let chosen = null; // a mode picked in this page, kept even when the store refuses to save it

    function stored() {
      try {
        const value = storage?.getItem(STORAGE_KEY);
        return MODES.includes(value) ? value : null;
      } catch (_error) { return null; }
    }
    const get = () => chosen || stored() || 'taipei';
    let known = get(); // the mode this page last showed, to tell a real change from a repeat

    function announce(mode) {
      listeners.forEach(listener => { try { listener(mode); } catch (error) { root.console?.error?.(error); } });
      try { target?.dispatchEvent?.(new root.CustomEvent(CHANGE_EVENT, {detail: {mode}})); } catch (_error) { /* no DOM */ }
    }

    function set(mode) {
      if (!MODES.includes(mode)) return get();
      chosen = mode;
      try { storage?.setItem(STORAGE_KEY, mode); } catch (_error) { /* kept in memory for this page */ }
      if (mode !== known) {
        known = mode;
        announce(mode);
      }
      return mode;
    }

    // Called with the new mode whenever it changes (here, or in another tab).
    function onChange(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    }

    // Another tab changed the stored choice.
    function receiveStorageEvent(event) {
      if (event && event.key !== STORAGE_KEY && event.key !== null) return;
      chosen = null;
      const after = get();
      if (after !== known) {
        known = after;
        announce(after);
      }
    }

    return {get, set, onChange, receiveStorageEvent};
  }

  const api = {STORAGE_KEY, MODES, CHANGE_EVENT, LABELS, createPreference};

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
    return;
  }

  // In a page: one shared instance, and every [data-sandhi-choice] control reads and writes it.
  const preference = createPreference();
  root.TliSandhiPreference = {...api, ...preference};
  root.addEventListener?.('storage', event => preference.receiveStorageEvent(event));

  // <html data-sandhi="taipei|singapore">: lets CSS show the Taipei or the Singapore version of a
  // figure ([data-sandhi-show]) with no script of its own.
  function markRoot() {
    try { root.document.documentElement.dataset.sandhi = preference.get(); } catch (_error) { /* no DOM */ }
  }
  markRoot();

  function syncControls() {
    markRoot();
    if (!root.document?.querySelectorAll) return;
    const mode = preference.get();
    root.document.querySelectorAll('[data-sandhi-choice]').forEach(button => {
      const active = button.dataset.sandhiChoice === mode;
      button.setAttribute('aria-pressed', String(active));
      button.classList.toggle('active', active);
    });
    root.document.querySelectorAll('select[data-sandhi-select]').forEach(select => { select.value = mode; });
  }
  root.TliSandhiPreference.syncControls = syncControls;
  preference.onChange(syncControls);
  root.document?.addEventListener('click', event => {
    const button = event.target.closest?.('[data-sandhi-choice]');
    if (button) preference.set(button.dataset.sandhiChoice);
  });
  root.document?.addEventListener('change', event => {
    const select = event.target.closest?.('select[data-sandhi-select]');
    if (select) preference.set(select.value);
  });
  // While text is selected, a Lomari vowel with a coloured tone shows its plain text (CSS:
  // .tli-text-selected in shared/web-site-navigation.css), so the selection highlight looks normal.
  root.document?.addEventListener('selectionchange', () => {
    let selected = false;
    try { const selection = root.getSelection?.(); selected = Boolean(selection && !selection.isCollapsed); } catch (_error) { /* none */ }
    root.document.documentElement.classList.toggle('tli-text-selected', selected);
  });
  if (root.document?.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', syncControls);
  else syncControls();
})(typeof window !== 'undefined' ? window : globalThis);

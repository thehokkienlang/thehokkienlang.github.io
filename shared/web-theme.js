(function (root) {
  'use strict';
  // Dark or light colours for the whole site. Dark is the default; a toggle in the header (beside
  // the search icon) switches between the two, and the choice is kept per visitor in localStorage
  // ('tli-theme', read inside try/catch). <html data-theme="dark|light"> carries the theme in use,
  // and shared/web-dark-theme.css draws dark mode from it. This script is loaded in <head> without
  // defer, so the page is never drawn in the wrong colours first.

  const STORAGE_KEY = 'tli-theme';
  const THEMES = Object.freeze(['dark', 'light']);
  const DEFAULT = 'dark';
  // Each label says what pressing the toggle does.
  const LABELS = Object.freeze({
    en: {toLight: 'Switch to light mode', toDark: 'Switch to dark mode'},
    'zh-Hant': {toLight: '切換為淺色模式', toDark: '切換為深色模式'},
    'zh-Hans': {toLight: '切换为浅色模式', toDark: '切换为深色模式'},
  });
  // Sun (shown in dark mode: press for light) and moon (shown in light mode: press for dark).
  const SUN = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.6M12 18.9v2.6M2.5 12h2.6M18.9 12h2.6M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>';
  const MOON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.2 14.6A8.4 8.4 0 0 1 9.4 3.8a8.4 8.4 0 1 0 10.8 10.8z"/></svg>';

  function stored() {
    try {
      const value = root.localStorage?.getItem(STORAGE_KEY);
      return THEMES.includes(value) ? value : DEFAULT; // an older 'auto' choice reads as the default
    } catch (_error) { return DEFAULT; }
  }
  let theme = stored();

  function language() {
    const lang = root.document?.documentElement.lang;
    return lang === 'zh-Hant' || lang === 'zh-Hans' ? lang : 'en';
  }

  function apply() {
    const doc = root.document;
    const html = doc?.documentElement;
    if (!html) return;
    html.dataset.theme = theme;
    html.style.colorScheme = theme;
    const words = LABELS[language()];
    doc.querySelectorAll?.('.site-theme-toggle').forEach(button => {
      const label = theme === 'dark' ? words.toLight : words.toDark;
      button.innerHTML = theme === 'dark' ? SUN : MOON;
      button.setAttribute('aria-label', label);
      button.title = label;
      button.setAttribute('aria-pressed', String(theme === 'dark'));
    });
  }

  function set(next) {
    if (!THEMES.includes(next)) return;
    theme = next;
    try { root.localStorage?.setItem(STORAGE_KEY, next); } catch (_error) { /* kept for this page */ }
    apply();
  }
  const toggle = () => set(theme === 'dark' ? 'light' : 'dark');

  // The toggle goes in the header, right after the search icon. The header's navigation is
  // replaced when the page language is applied (shared/web-site-language.js), which calls mount().
  function mount() {
    const doc = root.document;
    doc?.querySelectorAll?.('.site-search-link').forEach(search => {
      if (search.nextElementSibling?.classList.contains('site-theme-toggle')) return;
      const button = doc.createElement('button');
      button.type = 'button';
      button.className = 'site-theme-toggle';
      search.after(button);
    });
    apply();
  }

  root.TliTheme = {STORAGE_KEY, THEMES, DEFAULT, get: () => theme, set, toggle, mount};
  apply();
  root.addEventListener?.('storage', event => {
    if (event.key !== STORAGE_KEY && event.key !== null) return;
    theme = stored();
    apply();
  });
  root.document?.addEventListener('click', event => {
    if (event.target.closest?.('.site-theme-toggle')) toggle();
  });
  if (root.document?.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', mount);
  else mount();
})(window);

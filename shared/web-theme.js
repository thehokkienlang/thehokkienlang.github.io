(function (root) {
  'use strict';
  // Dark or light colours for the whole site. Follow the browser until the visitor picks a theme.
  // Manual choices are kept per visitor in localStorage ('tli-theme', read inside try/catch).
  // <html data-theme="dark|light"> carries the theme in use,
  // and shared/web-dark-theme.css draws dark mode from it. This script is loaded in <head> without
  // defer, so the page is never drawn in the wrong colours first.

  const STORAGE_KEY = 'tli-theme';
  const THEMES = Object.freeze(['dark', 'light']);
  const browserTheme = root.matchMedia?.('(prefers-color-scheme: dark)');
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
      return THEMES.includes(value) ? value : null;
    } catch (_error) { return null; }
  }
  let choice = stored();
  const get = () => choice ?? (browserTheme?.matches ? 'dark' : 'light');

  function language() {
    const lang = root.document?.documentElement.lang;
    return lang === 'zh-Hant' || lang === 'zh-Hans' ? lang : 'en';
  }

  function apply() {
    const doc = root.document;
    const html = doc?.documentElement;
    if (!html) return;
    const theme = get();
    html.dataset.theme = theme;
    html.style.colorScheme = theme;
    const words = LABELS[language()];
    doc.querySelectorAll?.('.site-theme-toggle').forEach(button => {
      const label = theme === 'dark' ? words.toLight : words.toDark;
      button.innerHTML = (theme === 'dark' ? SUN : MOON)
        + (button.classList.contains('site-footer-control') ? `<span>${label}</span>` : '');
      button.setAttribute('aria-label', label);
      button.title = label;
      button.setAttribute('aria-pressed', String(theme === 'dark'));
    });
  }

  function set(next) {
    if (!THEMES.includes(next)) return;
    choice = next;
    try { root.localStorage?.setItem(STORAGE_KEY, next); } catch (_error) { /* kept for this page */ }
    apply();
  }
  const toggle = () => set(get() === 'dark' ? 'light' : 'dark');

  // The toggle goes after the header search field, or before the language menu on /search/ where
  // the redundant header search is intentionally absent. The header's navigation is replaced when
  // the page language is applied (shared/web-site-language.js), which calls mount().
  function mount() {
    const doc = root.document;
    doc?.querySelectorAll?.('nav[aria-label="Main navigation"]').forEach(nav => {
      if (nav.querySelector(':scope > .site-theme-toggle')) return;
      const search = nav.querySelector(':scope > .site-header-search');
      const languageMenu = nav.querySelector(':scope > .site-language-dropdown');
      const button = doc.createElement('button');
      button.type = 'button';
      button.className = 'site-theme-toggle';
      if (search) search.after(button);
      else if (languageMenu) languageMenu.before(button);
      else nav.append(button);
    });
    apply();
  }

  root.TliTheme = {STORAGE_KEY, THEMES, get, set, toggle, mount};
  apply();
  const browserThemeChanged = () => { if (choice === null) apply(); };
  if (browserTheme?.addEventListener) browserTheme.addEventListener('change', browserThemeChanged);
  else browserTheme?.addListener?.(browserThemeChanged);
  root.addEventListener?.('storage', event => {
    if (event.key !== STORAGE_KEY && event.key !== null) return;
    choice = stored();
    apply();
  });
  root.document?.addEventListener('click', event => {
    if (event.target.closest?.('.site-theme-toggle')) toggle();
  });
  if (root.document?.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', mount);
  else mount();
})(window);

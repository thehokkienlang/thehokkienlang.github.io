(function (root) {
  'use strict';
  // Light or dark colours for the whole site. A visitor picks Auto (follow the device), Light or
  // Dark in the header menu; the choice is kept in localStorage ('tli-theme', read inside
  // try/catch). <html data-theme="light|dark"> carries the theme in use, and
  // shared/web-dark-theme.css draws dark mode from it. This script is loaded in <head> without
  // defer, so the page is never drawn in the wrong colours first.

  const STORAGE_KEY = 'tli-theme';
  const CHOICES = Object.freeze(['auto', 'light', 'dark']);
  const LABELS = Object.freeze({
    en: {theme: 'Theme', auto: 'Auto', light: 'Light', dark: 'Dark'},
    'zh-Hant': {theme: '外觀', auto: '自動', light: '淺色', dark: '深色'},
    'zh-Hans': {theme: '外观', auto: '自动', light: '浅色', dark: '深色'},
  });

  function stored() {
    try {
      const value = root.localStorage?.getItem(STORAGE_KEY);
      return CHOICES.includes(value) ? value : 'auto';
    } catch (_error) { return 'auto'; }
  }
  let choice = stored();
  const media = root.matchMedia ? root.matchMedia('(prefers-color-scheme: dark)') : null;
  const effective = () => choice === 'auto' ? (media?.matches ? 'dark' : 'light') : choice;

  function apply() {
    const html = root.document?.documentElement;
    if (!html) return;
    const theme = effective();
    html.dataset.theme = theme;
    html.style.colorScheme = theme;
    root.document.querySelectorAll?.('[data-theme-choice]').forEach(button => {
      const active = button.dataset.themeChoice === choice;
      button.setAttribute('aria-pressed', String(active));
      button.classList.toggle('active', active);
    });
  }

  function set(next) {
    if (!CHOICES.includes(next)) return;
    choice = next;
    try { root.localStorage?.setItem(STORAGE_KEY, next); } catch (_error) { /* kept for this page */ }
    apply();
  }

  // The setting in the header's language menu, beside Sandhi, in the page's language. The menu is
  // replaced when the page language is applied (shared/web-site-language.js), which calls mount().
  function mount() {
    const doc = root.document;
    // Only the language menu's panel, which holds the Sandhi setting.
    doc?.querySelectorAll?.('.site-nav-panel:has(.site-sandhi)').forEach(panel => {
      if (panel.querySelector('.site-theme')) return;
      const lang = doc.documentElement.lang === 'zh-Hant' || doc.documentElement.lang === 'zh-Hans'
        ? doc.documentElement.lang : 'en';
      const words = LABELS[lang];
      const group = doc.createElement('div');
      group.className = 'site-sandhi site-theme';
      group.setAttribute('role', 'group');
      group.setAttribute('aria-label', words.theme);
      const label = doc.createElement('span');
      label.className = 'site-sandhi-label';
      label.textContent = words.theme;
      const choices = doc.createElement('span');
      choices.className = 'site-sandhi-choices';
      for (const value of CHOICES) {
        const button = doc.createElement('button');
        button.type = 'button';
        button.className = 'site-sandhi-choice';
        button.dataset.themeChoice = value;
        button.textContent = words[value];
        choices.append(button);
      }
      group.append(label, choices);
      const sandhi = panel.querySelector('.site-sandhi:not(.site-theme)');
      sandhi.after(group);
    });
    apply();
  }

  root.TliTheme = {STORAGE_KEY, CHOICES, get: () => choice, effective, set, mount};
  apply();
  media?.addEventListener?.('change', () => { if (choice === 'auto') apply(); });
  root.addEventListener?.('storage', event => {
    if (event.key !== STORAGE_KEY && event.key !== null) return;
    choice = stored();
    apply();
  });
  root.document?.addEventListener('click', event => {
    const button = event.target.closest?.('[data-theme-choice]');
    if (button) set(button.dataset.themeChoice);
  });
  if (root.document?.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', mount);
  else mount();
})(window);

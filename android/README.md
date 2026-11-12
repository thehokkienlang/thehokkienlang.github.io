# TLI Keyboard for Android

A system keyboard that types Tangliengim (TLI) in any app. It is not part of the
website build; nothing here is published by GitHub Pages.

## How it works

- `keyboard/` is the keyboard's page (keys, candidate strip). It runs in a WebView
  inside the keyboard and reuses the website's IME code unchanged.
- At build time Gradle copies `shared/web-hangul-ime.js`, `shared/web-ime-core.js`,
  the menu styles, `assets/fonts/*.woff2` and `public/data/hokkien-hanri-dict.json`
  from the repository into the APK, laid out like the site root. There is no second
  copy of the engine or the dictionary.
- `TliKeyboardService` passes the page's output to the focused app. The app has no
  INTERNET permission.

## Build

Needs JDK 17 and the Android SDK (platform 34, build-tools 34). `local.properties`
(not in git) holds `sdk.dir`.

```
python tools/build_site.py          # from the repository root: generates the dictionary JSON
gradle -p android assembleDebug     # APK in android/app/build/outputs/apk/debug/
```

To work on the keyboard page in a desktop browser, copy `keyboard/` into `_site/`
after a site build and open `/keyboard/index.html` on the local server; output is
logged to the console instead of being typed.

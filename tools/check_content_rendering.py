"""Optional Playwright regression checks for mobile ruby, tones and song layout."""

import argparse
import json
from pathlib import Path


MEASURE = """() => {
  const issues = [];
  const toneSpacing = [...document.querySelectorAll('.song-entry-title .hangul-tone')].flatMap(node => {
    const range = document.createRange();
    range.selectNodeContents(node.firstChild);
    const extra = node.getBoundingClientRect().width - range.getBoundingClientRect().width;
    return extra > 0.25 ? [{base: node.firstChild.textContent, extra}] : [];
  });
  for (const ruby of document.querySelectorAll('.song-entry-title ruby, .song-entry-title .tli-ruby, .song-entry-title .hangul-tone')) {
    const reading = ruby.querySelector(':scope > rt, :scope > .tli-rt, :scope > .tone-mark');
    const base = ruby.querySelector(':scope > .tli-ruby-base') || ruby.firstChild;
    if (!reading || !base) continue;
    const range = document.createRange();
    range.selectNodeContents(base);
    const baseBox = range.getBoundingClientRect();
    const readingBox = reading.getBoundingClientRect();
    if (readingBox.bottom > baseBox.top + 4) {
      issues.push({base: base.textContent, reading: reading.textContent,
        baseY: baseBox.top, readingBottom: readingBox.bottom});
    }
  }
  return {issues: issues.slice(0, 4), issueCount: issues.length, toneSpacing, overflow: document.documentElement.scrollWidth > innerWidth,
    entries: document.querySelectorAll('.song-entry').length,
    marks: document.querySelectorAll('.hangul-tone').length,
    composedLomari: [...document.querySelectorAll('.song-entry-lomari')]
      .every(node => node.textContent === node.textContent.normalize('NFC'))};
}"""


def main():
    from playwright.sync_api import sync_playwright

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8043")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--diagnose", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as playwright:
        for engine_name in ("webkit", "chromium"):
            browser = getattr(playwright, engine_name).launch()
            try:
                for width in (390, 1280):
                    context = browser.new_context(viewport={"width": width, "height": 844},
                                                  device_scale_factor=1, is_mobile=width == 390)
                    page = context.new_page()
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.goto(args.url.rstrip("/") + "/songs/", wait_until="networkidle")
                    page.evaluate("document.fonts.ready")
                    result = page.evaluate(MEASURE)
                    result.update(engine=engine_name, width=width, errors=errors)
                    page.locator('.song-category').first.screenshot(path=str(args.output / f"{engine_name}-{width}.png"))
                    results.append(result)
                    context.close()
                context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
                context.route("https://**/*", lambda route: route.abort())
                page = context.new_page()
                for route in ("/songs/곻愛릐一擺/", "/read/stories/the-egg/"):
                    page.goto(args.url.rstrip("/") + route, wait_until="domcontentloaded")
                    page.wait_for_selector(".tli-ruby")
                    page.evaluate("document.fonts.ready")
                    remaining = page.locator('.imported-content ruby[style*="position"]').count()
                    if not args.diagnose:
                        assert remaining == 0, f"Positioned native ruby remains in {engine_name}: {route}"
                page.goto(args.url.rstrip("/") + "/zh-hant/", wait_until="domcontentloaded")
                page.wait_for_selector(".home-song-title .tli-ruby, .home-song-title .hangul-tone")
                page.evaluate("document.fonts.ready")
                page.locator(".home-songbook").screenshot(path=str(args.output / f"{engine_name}-home-songbook.png"))
                if not args.diagnose:
                    assert page.locator(".home-song-title").count() == 3
                    assert page.locator(".home-song-title ruby").count() == 0
                    assert "瀏覽歌單" in page.locator(".home-feature-songs").inner_text()
                context.close()
            finally:
                browser.close()
    print(json.dumps(results, ensure_ascii=False, indent=2))
    (args.output / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    if not args.diagnose:
        assert all(not row["issues"] and not row["toneSpacing"] and not row["overflow"] and not row["errors"] and
                   row["entries"] == 70 and row["composedLomari"] for row in results), "Content rendering regression"


if __name__ == "__main__":
    main()

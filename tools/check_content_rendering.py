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
                    context.route("https://**/*", lambda route: route.abort())
                    page = context.new_page()
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.goto(args.url.rstrip("/") + "/songs/", wait_until="networkidle")
                    page.evaluate("document.fonts.ready")
                    result = page.evaluate(MEASURE)
                    result.update(engine=engine_name, width=width, errors=errors)
                    page.locator('.song-category').first.screenshot(path=str(args.output / f"{engine_name}-{width}.png"))
                    results.append(result)
                    for language, homepage in (("en", "/"), ("zh-hant", "/zh-hant/"), ("zh-hans", "/zh-hans/")):
                        page.goto(args.url.rstrip("/") + homepage, wait_until="domcontentloaded")
                        student = page.locator('.imported-content ul.wp-block-list .tli-rt').filter(has_text="학솅")
                        student.wait_for()
                        page.evaluate("document.fonts.ready")
                        offset = student.evaluate("""node => {
                            const style = getComputedStyle(node);
                            const size = parseFloat(style.fontSize);
                            const parentSize = parseFloat(getComputedStyle(node.parentElement).fontSize);
                            return {actual: parseFloat(style.top), expected: -0.85 * (size + 1) + 1,
                                size, expectedSize: parentSize * 0.6 - 1};
                        }""")
                        if not args.diagnose:
                            expected_label = {"zh-hant": "歌單精選", "zh-hans": "歌单精选"}.get(language)
                            if expected_label:
                                assert page.locator('.home-songbook-label').inner_text() == expected_label
                            assert abs(offset["actual"] - offset["expected"]) < 0.1, (
                                f"Student ruby offset ignored after DOM conversion: {engine_name}/{width}/{language}: {offset}")
                            assert abs(offset["size"] - offset["expectedSize"]) < 0.1, offset
                            for prefix in ("한", "당"):
                                readings = page.locator('.imported-content > p .tli-rt').filter(has_text=prefix)
                                assert readings.count() > 0, f"Missing homepage reading: {language}/{prefix}"
                                for reading in readings.all():
                                    top = reading.evaluate("node => parseFloat(getComputedStyle(node).top)")
                                    assert abs(top - offset["actual"]) < 0.1, f"Homepage ruby offsets differ: {language}/{prefix}"
                                    size = reading.evaluate("node => parseFloat(getComputedStyle(node).fontSize)")
                                    assert abs(size - offset["size"]) < 0.1, f"Homepage ruby sizes differ: {language}/{prefix}"
                        student.locator("xpath=ancestor::ul[1]").screenshot(
                            path=str(args.output / f"{engine_name}-{width}-{language}-student.png"))
                    for language, story in (("en", "/read/stories/the-egg/"), ("zh-hant", "/zh-hant/read/stories/the-egg/"), ("zh-hans", "/zh-hans/read/stories/the-egg/")):
                        page.goto(args.url.rstrip("/") + story, wait_until="domcontentloaded")
                        title = page.locator('h1.title-reading')
                        title.locator('.tli-rt').wait_for()
                        if not args.diagnose:
                            assert title.locator('.tli-ruby-base').inner_text() == '卵'
                            assert title.locator('.tli-rt').inner_text() == '능ˉ'
                            assert page.locator('.story-subtitle').inner_text() == ('The Egg' if language == 'en' else '蛋')
                            assert '2352652016' in page.locator('iframe[src*="w.soundcloud.com"]').get_attribute('src')
                        paragraphs = page.locator('p[style*="text-indent:2em"]')
                        paragraphs.first.locator(".tli-ruby").first.wait_for()
                        page.evaluate("document.fonts.ready")
                        page.screenshot(path=str(args.output / f"{engine_name}-{width}-{language}-egg-header.png"))
                        spacing = paragraphs.nth(1).evaluate("""paragraph => {
                            const ruby = paragraph.querySelector('.tli-ruby');
                            const reading = paragraph.querySelector('.tli-rt:not([style*="120%"] )');
                            const style = getComputedStyle(reading);
                            return {indent: getComputedStyle(ruby).textIndent,
                                extraWidth: ruby.getBoundingClientRect().width - ruby.querySelector('.tli-ruby-base').getBoundingClientRect().width,
                                paragraphIndent: getComputedStyle(paragraph).textIndent,
                                top: parseFloat(style.top), expectedTop: -1.1 * parseFloat(style.fontSize) + 4};
                        }""")
                        if not args.diagnose:
                            assert spacing["indent"] == "0px" and abs(spacing["extraWidth"]) < 0.25, spacing
                            assert spacing["paragraphIndent"] == "48px", spacing
                            assert abs(spacing["top"] - spacing["expectedTop"]) < 0.1, spacing
                        paragraphs.nth(1).screenshot(path=str(args.output / f"{engine_name}-{width}-{language}-egg.png"))
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

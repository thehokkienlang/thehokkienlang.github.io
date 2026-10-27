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
    const pronunciation = ruby.classList.contains('tli-reading-ruby');
    const baseBox = pronunciation ? ruby.getBoundingClientRect() : range.getBoundingClientRect();
    const readingBox = reading.getBoundingClientRect();
    const allowedOverlap = pronunciation ? 0.15 * parseFloat(getComputedStyle(reading).fontSize) + 0.25 : 4;
    if (readingBox.bottom > baseBox.top + allowedOverlap) {
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

RUBY_GEOMETRY = """node => {
  const reading = node.querySelector(':scope > .tli-rt, :scope > .entry-headword-reading');
  const base = node.querySelector(':scope > .tli-ruby-base, :scope > .entry-headword-base');
  const style = getComputedStyle(reading);
  const size = parseFloat(style.fontSize);
  const box = node.getBoundingClientRect();
  return {ratio: size / parseFloat(getComputedStyle(node).fontSize),
    bottom: parseFloat(style.bottom), expectedBottom: box.height - 0.15 * size,
    extraWidth: box.width - base.getBoundingClientRect().width};
}"""


def check_ruby(locator):
    for geometry in locator.evaluate_all(f"nodes => nodes.map({RUBY_GEOMETRY})"):
        assert abs(geometry['ratio'] - 0.5) < 0.002, geometry
        assert abs(geometry['bottom'] - geometry['expectedBottom']) < 0.15, geometry
        assert abs(geometry['extraWidth']) < 0.25, geometry


def check_scaling(page, origin, screenshot):
    samples = []
    for size in (16, 20, 24, 32, 48, 64):
        samples.append(f'''<p style="font-size:{size}px;line-height:2.2">
          <ruby style="position:relative">學生<rt style="position:absolute;top:-99px;left:19px;font-size:57%">학솅ˆ</rt></ruby>
          <span class="title-reading"><ruby class="hanri-title">學生<rt>학솅ˆ</rt></ruby></span>
          <span class="entry-headword-ruby"><span class="entry-headword-base">學生</span><span class="entry-headword-reading">학솅ˆ</span></span>
        </p>''')
    page.set_content(f'''<html><head><link rel="stylesheet" href="{origin}/assets/content-site/site.css">
      <link rel="stylesheet" href="{origin}/shared/web-title-reading.css"></head>
      <body><main class="imported-content">{''.join(samples)}
      <p><ruby style="position:relative">가<rt style="font-size:120%;position:absolute;top:-1.15em;left:0.2em">ꞈ</rt></ruby></p>
      </main><script src="{origin}/assets/content-site/site.js"></script></body></html>''')
    page.wait_for_selector('.tli-reading-ruby')
    page.evaluate('document.fonts.ready')
    check_ruby(page.locator('.tli-reading-ruby, .entry-headword-ruby'))
    assert page.locator('.tli-tone-ruby').count() == 1
    tone = page.locator('.tli-tone-ruby > .tli-rt').evaluate('node => parseFloat(getComputedStyle(node).fontSize) / parseFloat(getComputedStyle(node.parentElement).fontSize)')
    assert abs(tone - 1.2) < 0.002, tone
    page.screenshot(path=str(screenshot), full_page=True)


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
                        if not args.diagnose:
                            expected_label = {"zh-hant": "歌單精選", "zh-hans": "歌单精选"}.get(language)
                            if expected_label:
                                assert page.locator('.home-songbook-label').inner_text() == expected_label
                            check_ruby(page.locator('.tli-reading-ruby:not(.bopomofo-title)'))
                            for prefix in ("한", "당"):
                                readings = page.locator('.imported-content > p .tli-rt').filter(has_text=prefix)
                                assert readings.count() > 0, f"Missing homepage reading: {language}/{prefix}"
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
                            return {indent: getComputedStyle(ruby).textIndent,
                                extraWidth: ruby.getBoundingClientRect().width - ruby.querySelector('.tli-ruby-base').getBoundingClientRect().width,
                                paragraphIndent: getComputedStyle(paragraph).textIndent};
                        }""")
                        if not args.diagnose:
                            assert spacing["indent"] == "0px" and abs(spacing["extraWidth"]) < 0.25, spacing
                            assert spacing["paragraphIndent"] == "48px", spacing
                            check_ruby(page.locator('.tli-reading-ruby:not(.bopomofo-title)'))
                        paragraphs.nth(1).screenshot(path=str(args.output / f"{engine_name}-{width}-{language}-egg.png"))
                        footnotes = page.locator('table').filter(has=page.locator('a#_ftn1')).first
                        colon_positions = footnotes.locator('td:first-child').evaluate_all("""cells => cells.map(cell => {
                            const walker = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT);
                            let node;
                            while (node = walker.nextNode()) {
                                const index = node.textContent.indexOf(':');
                                if (index < 0) continue;
                                const range = document.createRange();
                                range.setStart(node, index); range.setEnd(node, index + 1);
                                const colon = range.getBoundingClientRect();
                                const label = cell.querySelector('i').getBoundingClientRect();
                                return colon.top < label.bottom && colon.bottom > label.top;
                            }
                            return false;
                        })""")
                        if not args.diagnose:
                            assert colon_positions and all(colon_positions), f"Wrapped footnote colon: {engine_name}/{width}/{language}"
                        footnotes.screenshot(path=str(args.output / f"{engine_name}-{width}-{language}-egg-footnotes.png"))
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
                check_scaling(page, args.url.rstrip('/'), args.output / f'{engine_name}-scaling.png')
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

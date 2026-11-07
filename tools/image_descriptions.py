"""Alt text for the content images, and a text version of the sandhi diagram (audit A7).

The imported WordPress pages carry their images with empty or missing alt text.
The build fills in these descriptions so the source pages stay untouched.
Descriptions say what each image shows; they add no new linguistic claims.
The text version transcribes the Taipei sandhi diagram exactly as drawn.
"""

from __future__ import annotations

import html
import re

_SANDHI_DIAGRAM = {
    "en": "Diagram of the Taipei tone sandhi pattern. A text version follows.",
    "zh-Hant": "台北變調規則圖。下方附有文字版。",
    "zh-Hans": "台北变调规则图。下方附有文字版。",
}
_HIGH_TO_MID = {
    "en": "In tone sandhi, the High tone (東) becomes the Mid tone (洞).",
    "zh-Hant": "變調時，高調（東）變為中調（洞）。",
    "zh-Hans": "变调时，高调（东）变为中调（洞）。",
}

# Image file name (as published under /assets/content/wordpress/) -> alt text per language.
ALT_TEXT = {
    "ffbe2a8272c7-taipei-sandhi.png": _SANDHI_DIAGRAM,
    "eb5dcc7d8d80-taipei-sandhi-sc.png": _SANDHI_DIAGRAM,
    "74a429b6c640-high-to-mid-sandhi.png": _HIGH_TO_MID,
    "206b70dff342-high-to-mid-sandhi-sc.png": _HIGH_TO_MID,
    "7422c04d94d8-consonants-illustration_v2.png": {
        "en": "Illustration of the consonant letters ㄱ, ㄷ and ㄴ",
        "zh-Hant": "子音字母 ㄱ、ㄷ、ㄴ 的插圖",
        "zh-Hans": "辅音字母 ㄱ、ㄷ、ㄴ 的插图",
    },
    "458d8131d783-vowels-illustration.png": {
        "en": "Illustration of the vowel letters ㅏ, ㅗ and ㅓ",
        "zh-Hant": "母音字母 ㅏ、ㅗ、ㅓ 的插圖",
        "zh-Hans": "元音字母 ㅏ、ㅗ、ㅓ 的插图",
    },
    "850da4c77295-hn_hangul_jamo_au_bold.png": {
        "en": "The vowel letter ᅷ (au)",
        "zh-Hant": "母音字母 ᅷ（au）",
        "zh-Hans": "元音字母 ᅷ（au）",
    },
    "93a22602bb73-hn_hangul_jamo_iau_bold.png": {
        "en": "The vowel letter ᆤ (iau)",
        "zh-Hant": "母音字母 ᆤ（iau）",
        "zh-Hans": "元音字母 ᆤ（iau）",
    },
    "49dd7a39f410-korean-keyboard.png": {
        "en": "Windows input menu listing Korean (Microsoft IME), Korean (Microsoft Old Hangul) and Japanese (Microsoft IME)",
        "zh-Hant": "Windows 輸入法選單，列出 Korean（Microsoft IME）、Korean（Microsoft Old Hangul）和 Japanese（Microsoft IME）",
        "zh-Hans": "Windows 输入法菜单，列出 Korean（Microsoft IME）、Korean（Microsoft Old Hangul）和 Japanese（Microsoft IME）",
    },
    "763d64878260-eca784eb8da9.png": {
        "en": "Pixel-art avatar wearing a party hat",
        "zh-Hant": "戴著派對帽的像素風頭像",
        "zh-Hans": "戴着派对帽的像素风头像",
    },
    "a544aeacfa20-the-egg.png": {
        "en": "Illustration of an egg",
        "zh-Hant": "一顆蛋的插圖",
        "zh-Hans": "一颗蛋的插图",
    },
}

# Text version of the Taipei sandhi diagram: (tone, example, tone before another syllable).
_SANDHI_ROWS = {
    "en": (("High", "東", "Mid"), ("Mid", "洞", "Low"), ("Rising", "同", "Low"), ("Low", "棟", "Falling"),
           ("Falling", "黨", "High"), ("High checked", "獨", "Low checked"), ("Low checked", "督", "High checked")),
    "zh-Hant": (("高調", "東", "中調"), ("中調", "洞", "低調"), ("升調", "同", "低調"), ("低調", "棟", "降調"),
                ("降調", "黨", "高調"), ("高入調", "獨", "低入調"), ("低入調", "督", "高入調")),
    "zh-Hans": (("高调", "东", "中调"), ("中调", "洞", "低调"), ("升调", "同", "低调"), ("低调", "栋", "降调"),
                ("降调", "党", "高调"), ("高入调", "独", "低入调"), ("低入调", "督", "高入调")),
}
_SANDHI_LABELS = {
    "en": ("Text version of the diagram", "Tone (example)", "Before another syllable",
           "Checked syllables end in -ㄱ, -ㄷ, -ㅂ or -ㅎ."),
    "zh-Hant": ("圖表文字版", "本調（例字）", "後接其他音節時", "入聲字以 -ㄱ、-ㄷ、-ㅂ 或 -ㅎ 結尾。"),
    "zh-Hans": ("图表文字版", "本调（例字）", "后接其他音节时", "入声字以 -ㄱ、-ㄷ、-ㅂ 或 -ㅎ 结尾。"),
}
TEXT_VERSIONS = {"ffbe2a8272c7-taipei-sandhi.png", "eb5dcc7d8d80-taipei-sandhi-sc.png"}

IMG = re.compile(r"<img\b[^>]*>", re.I)
SRC = re.compile(r'\bsrc="([^"]+)"', re.I)
ALT = re.compile(r'\salt="([^"]*)"', re.I)


def sandhi_text_version(language: str) -> str:
    summary, tone_header, sandhi_header, note = _SANDHI_LABELS[language]
    rows = "".join(f"<tr><td>{html.escape(tone)}（{example}）</td><td>{html.escape(after)}</td></tr>"
                   if language != "en" else
                   f"<tr><td>{html.escape(tone)} ({example})</td><td>{html.escape(after)}</td></tr>"
                   for tone, example, after in _SANDHI_ROWS[language])
    return ('<details class="diagram-text-version"><summary>' + html.escape(summary) + "</summary>"
            f"<table><thead><tr><th>{html.escape(tone_header)}</th><th>{html.escape(sandhi_header)}</th></tr></thead>"
            f"<tbody>{rows}</tbody></table><p>{html.escape(note)}</p></details>")


def describe_images(body: str, language: str) -> str:
    """Fill empty or missing alt text and add the sandhi diagram's text version."""
    pending_text_version = False

    def image(match: re.Match) -> str:
        nonlocal pending_text_version
        tag = match.group(0)
        source = SRC.search(tag)
        name = source.group(1).split("?")[0].rsplit("/", 1)[-1] if source else ""
        descriptions = ALT_TEXT.get(name)
        if not descriptions:
            return tag
        if name in TEXT_VERSIONS:
            pending_text_version = True
        existing = ALT.search(tag)
        if existing and existing.group(1).strip():
            return tag
        alt = html.escape(descriptions[language], quote=True)
        if existing:
            return tag[:existing.start()] + f' alt="{alt}"' + tag[existing.end():]
        return re.sub(r"<img\b", f'<img alt="{alt}"', tag, count=1, flags=re.I)

    pieces = []
    position = 0
    for match in IMG.finditer(body):
        if match.start() < position:  # already copied with an inserted text version
            continue
        pieces.append(body[position:match.start()])
        pieces.append(image(match))
        position = match.end()
        if pending_text_version:
            # Put the text version after the figure that holds the diagram (or after the image).
            close = body.find("</figure>", position)
            next_image = IMG.search(body, position)
            end = close + len("</figure>") if close != -1 and (next_image is None or close < next_image.start()) else position
            pieces.append(body[position:end] + sandhi_text_version(language))
            position = end
            pending_text_version = False
    pieces.append(body[position:])
    return "".join(pieces)

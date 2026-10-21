"""Public language routes and shared navigation labels."""

from urllib.parse import urlencode

LANGUAGES = ("en", "zh-Hant", "zh-Hans")
PREFIXES = {"en": "", "zh-Hant": "/zh-hant", "zh-Hans": "/zh-hans"}
LANGUAGE_NAMES = {"en": "English", "zh-Hant": "繁體中文", "zh-Hans": "简体中文"}
LABELS = {
    "en": ("Home", "Learn", "Songs", "Read", "Dictionary", "IME", "About", "Introduction", "Spelling", "Tone sandhi", "Romanisation", "The Egg", "Tale of the Lychee Mirror", "Literature", "Stories", "Original WordPress page", "Open IME", "Skip to content", "Learn Tangliengim", "Read in Hokkien"),
    "zh-Hant": ("主頁", "學習", "歌曲", "閱讀", "詞典", "輸入法", "關於", "使用說明", "拼寫原則", "變調規則", "羅馬字", "卵", "荔鏡記", "文學", "故事", "原 WordPress 頁面", "開啟輸入法", "跳至內容", "學習東寧音", "閱讀閩南語"),
    "zh-Hans": ("主页", "学习", "歌曲", "阅读", "词典", "输入法", "关于", "使用说明", "拼写规范", "变调规则", "罗马字", "卵（繁體中文）", "荔镜记", "文学", "故事", "原 WordPress 页面", "打开输入法", "跳至内容", "学习东宁音", "阅读闽南语"),
}
LOCAL_PATHS = ("/", "/about/", "/learn/", "/learn/introduction/", "/learn/spelling/", "/learn/tone-sandhi/", "/learn/romanisation/", "/songs/", "/read/")
CHINESE_PAGES = (
    (6645, "zh-Hant", "pages", "home", "/", "主頁"),
    (9433, "zh-Hant", "pages", "about", "/about/", "關於我"),
    (581, "zh-Hant", "guides", "introduction", "/learn/introduction/", "東寧音使用說明"),
    (9613, "zh-Hant", "guides", "spelling", "/learn/spelling/", "東寧音拼寫原則"),
    (8873, "zh-Hant", "guides", "tone-sandhi", "/learn/tone-sandhi/", "閩南語的變調規則"),
    (10853, "zh-Hant", "guides", "romanisation", "/learn/romanisation/", "東寧音羅馬字"),
    (7647, "zh-Hant", "stories", "the-egg", "/read/stories/the-egg/", "卵"),
    (8952, "zh-Hans", "pages", "home", "/", "主页"),
    (10885, "zh-Hans", "pages", "about", "/about/", "关于我"),
    (3478, "zh-Hans", "guides", "introduction", "/learn/introduction/", "东宁音使用说明"),
    (9635, "zh-Hans", "guides", "spelling", "/learn/spelling/", "东宁音拼写规范"),
    (8935, "zh-Hans", "guides", "tone-sandhi", "/learn/tone-sandhi/", "闽南语的变调规则"),
    (10869, "zh-Hans", "guides", "romanisation", "/learn/romanisation/", "东宁音罗马字"),
)


def language_for_route(route):
    return next((lang for lang, prefix in PREFIXES.items() if prefix and route.startswith(prefix + "/")), "en")


def base_route(route):
    return route[len(PREFIXES[language_for_route(route)]):]


def language_url(route, language):
    base = base_route(route)
    if base in LOCAL_PATHS:
        return PREFIXES[language] + base
    if base == "/read/stories/the-egg/":
        return None if language == "zh-Hans" else PREFIXES[language] + base
    return base + ("?" + urlencode({"lang": language}) if language != "en" else "")


def text(key, language):
    return LABELS[language][LABELS["en"].index(key)]

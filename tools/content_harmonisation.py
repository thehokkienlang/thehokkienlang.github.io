"""Source-preserving mixed-script audit and reviewed v3.2 spelling edits."""

from __future__ import annotations

import hashlib
import html
import re
import unicodedata
from dataclasses import dataclass, field
from html.parser import HTMLParser

from song_title_readings import FirstHeading, phonetics

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
BLOCKS = {"p", "h1", "h2", "h3", "h4", "li", "td", "th", "figcaption"}
UPPER = str.maketrans({"ꞈ": "ˆ", "ˎ": "`", "ˏ": "ˊ", "ˍ": "ˉ", "ˋ": "`"})
TONES = "ˆ`ˋˊˉꞈˎˏˍ12345"
BOUNDARIES = set(".,;:!?，。；：！？()（）\"“”‘[]【】/…—")
HANGUL = re.compile(r"[\u1100-\u11ff\u3130-\u318f\ua960-\ua97f\uac00-\ud7a3\ud7b0-\ud7ff]")

# These are contextual readings, not citation-tone replacements.
HANRI = {
    "뽀": ("無", "4.3.1/30"), "뿌": ("無", "4.3.1/30"),
    "우": ("有", "4.3.1/37"), "에": ("會", "4.3.1/36"),
    "뾔": ("𣍐", "4.3.1/31"), "음": ("毋", "4.3.1/38"),
    "시": ("是", "4.3.1/32"), "야": ("也", "4.3.1/34"),
    "됴": ("就", "4.3.1/22"), "둏": ("著", "4.4/49-50"),
    "렁": ("攏", "4.3.1/26"), "렣": ("咧", "4.3.1/27"),
    "듸": ("佇", "4.3.1/24"), "허": ("予", "4.3.1/45"),
    "캏": ("較", "4.3.1/44"), "죄": ("㩼", "4.5/62"),
    "똬": ("偌", "user:2026-10-25"), "껑": ("慐", "4.5/54"),
    "빼": ("䆀", "4.1/dictionary"), "빧": ("捌", "4.1/dictionary"),
    "심": ("心", "4.1/dictionary"), "래": ("來", "4.1/dictionary"),
    "킁": ("囥", "4.1/dictionary"), "ᄁᅷ": ("𠢕", "4.1/dictionary"),
    "ᄃᅷ": ("兜", "4.1/dictionary"),
    "도": ("就", "4.3.1/22-regional-to"),
}
RETAIN = {
    "꽈", "꽌", "꾼", "란", "릐", "린", "이", "인", "쟈", "햐", "제", "헤",
    "가", "감", "곻", "매", "애", "뻐", "샹",
}
# Whole-word exceptions prevent a native homophone rule from altering a loan or refrain.
PROTECTED = {
    "안니": "user-retained", "간나": "user-retained", "에당": "unassigned-native",
    "다버": "user-retained-review", "자뻐": "user-retained", "간다": "user-retained-review",
    "오로": "user-retained-review", "샇샇": "user-retained-review",
    "오도빼": "foreign-transcription", "유치엔": "foreign-transcription",
    "수구": "foreign-transcription", "미니": "foreign-transcription",
    "시아껳": "foreign-transcription", "덱시": "foreign-transcription",
    "힏ᄅힻ": "foreign-name", "젝뻐띠": "foreign-transcription",
    "거브ᄄힻ": "foreign-transcription", "사ᄍힻᆫ": "foreign-transcription",
    "남ᄈힻ트띠": "foreign-transcription", "남ᄈힻ흐어": "foreign-transcription",
    "트떼닝": "foreign-transcription", "게쭈ᄋힻ디": "foreign-transcription",
    "챻챻챻": "dance-name", "챻챻": "dance-name", "퓨퓨": "sound-symbolism",
    "애애요": "interjection", "애요": "interjection", "이얗헿더": "sung-refrain",
    "렁덩친덩챵": "sung-refrain", "왛핳하": "sung-refrain",
}
WORDS = {"칟토": ("𨑨迌", "4.1/dictionary"), "운쟝": ("運將", "user-approved-example"),
         "냐냐": ("爾爾", "4.5/55"), "일아": ("嬰仔", "user:2026-10-25"),
         "안좔": ("按怎", "user:2026-10-25"), "뽀내": ("無奈", "user:2026-10-25"),
         "뽀대뽀지": ("無代無誌", "user:2026-10-25")}


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def bare(value):
    return unicodedata.normalize("NFC", value.rstrip(TONES))


@dataclass
class Node:
    tag: str
    start: int
    end: int
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)
    data: str = ""

    def visible(self):
        if self.tag in {"rt", "rp", "script", "style"}:
            return ""
        return html.unescape(self.data) if self.tag == "#text" else "".join(child.visible() for child in self.children)


class SourceHTML(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.lines = [0] + [match.end() for match in re.finditer("\n", source)]
        self.root = Node("#root", 0, len(source))
        self.stack = [self.root]
        self.feed(source)

    def source_offset(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        start = self.source_offset()
        node = Node(tag, start, start + len(self.get_starttag_text()), dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1, 0, -1):
            if self.stack[index].tag == tag:
                self.stack[index].end = self.source.index(">", self.source_offset()) + 1
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(Node("#text", self.source_offset(), self.source_offset()+len(data), data=data))

    def handle_entityref(self, name):
        self.handle_data("&"+name+";")

    def handle_charref(self, name):
        self.handle_data("&#"+name+";")


@dataclass
class Atom:
    base: str
    reading: str
    start: int
    end: int
    block: Node
    kind: str
    neutral: bool = False
    protected: str = ""


def atoms_for(record):
    source = record["body"]
    tree = SourceHTML(source)
    heading = FirstHeading(source) if record["type"] == "songs" else None
    atoms = []

    def walk(node, block=None):
        if heading and heading.start is not None and heading.start <= node.start < heading.end:
            return
        if node.tag in {"rt", "rp", "script", "style", "iframe"}:
            return
        if node.tag in BLOCKS:
            block = node
        if node.tag == "br":
            atoms.append(Atom("\n", "", node.start, node.end, block, "boundary"))
            return
        if node.tag == "ruby":
            base = node.visible()
            readings = [child for child in node.children if child.tag == "rt"]
            annotation = "".join("".join(child.visible() for child in rt.children) for rt in readings).strip()
            if HANGUL.search(base) and annotation and all(char in TONES for char in annotation):
                atoms.append(Atom(bare(base), base+annotation.translate(UPPER), node.start, node.end, block, "hangul"))
            else:
                atoms.append(Atom(base, annotation, node.start, node.end, block, "ruby"))
            return
        if node.tag == "#text":
            decoded = html.unescape(node.data)
            if decoded != node.data:
                kind = "hangul" if HANGUL.fullmatch(decoded) else "text"
                atoms.append(Atom(bare(decoded), decoded.translate(UPPER) if kind == "hangul" else "",
                                  node.start, node.end, block, kind))
                return
            index = 0
            while index < len(node.data):
                unit = phonetics().hangul_reading_unit_at(node.data, index)
                if unit:
                    reading, end = unit
                    atoms.append(Atom(bare(reading), reading.translate(UPPER), node.start+index, node.start+end, block, "hangul"))
                    index = end
                else:
                    atoms.append(Atom(node.data[index], "", node.start+index, node.start+index+1, block, "text"))
                    index += 1
            return
        for child in node.children:
            walk(child, block)

    walk(tree.root)
    active, previous_block = False, None
    for atom in atoms:
        if atom.block is not previous_block:
            active = False
        for char in atom.base:
            if char in "’'ʼ":
                active = True
            elif char.isspace() or char in BOUNDARIES:
                active = False
        atom.neutral = active
        previous_block = atom.block
    return atoms


def word_at(atoms, index, word):
    value = ""
    for end in range(index, min(len(atoms), index+len(word)+1)):
        atom = atoms[end]
        if atom.kind != "hangul" or atom.neutral or atom.block is not atoms[index].block:
            return None
        value += atom.base
        if value == word:
            return end+1
        if not word.startswith(value):
            return None
    return None


def reading_ruby(hanri, reading, connected):
    reading = reading.translate(UPPER)
    if connected:
        reading += "-"
    left = "0.25em" if any(char in TONES for char in reading) else "0.4em"
    base = '<span style=";font-family: Noto Sans SC">㩼</span>' if hanri == "㩼" else html.escape(hanri)
    return ('<ruby style="position: relative;white-space: nowrap">'+base+
            '<rt style="font-size: 57%;position: absolute;top: -1.2em;left: '+left+'">'+html.escape(reading)+"</rt></ruby>")


def propose(record):
    atoms = atoms_for(record)
    # Teaching/reference material and Teochew lyrics are not Hokkien mixed prose.
    if record["type"] not in {"songs", "stories"} or record["route"] == "/songs/月下煮茶/" or record.get("titleRuby"):
        return [], []
    for index, atom in enumerate(atoms):
        if atom.kind != "hangul" or atom.neutral:
            continue
        for word, reason in sorted(PROTECTED.items(), key=lambda item: -len(item[0])):
            if end := word_at(atoms, index, word):
                for member in atoms[index:end]:
                    member.protected = reason
                break
    assigned = {}
    for index, atom in enumerate(atoms):
        if atom.kind != "hangul" or atom.neutral or atom.protected:
            continue
        if atom.block is None or atom.block.tag in {"td", "th", "figcaption"}:
            atom.protected = "transcription/reference"
            continue
        for word, (hanri, rule) in WORDS.items():
            if end := word_at(atoms, index, word):
                members = atoms[index:end]
                if len(members) == len(hanri):
                    assigned.update({index+offset: (character, rule) for offset, character in enumerate(hanri)})
                break
        if index in assigned:
            continue
        previous = "".join(item.base for item in atoms[max(0,index-4):index] if item.block is atom.block)
        following = "".join(item.base for item in atoms[index+1:index+5] if item.block is atom.block)
        if atom.base == "가" and (
                following.startswith("人拼輸贏") or following.startswith("란 有孝") or
                previous.endswith("定定") or (previous.endswith("來") and following.startswith("꽈 見面")) or
                ("Good morning" in atom.block.visible() and following.startswith("릐"))):
            assigned[index] = ("共", "4.2.2/13-relational")
        elif atom.base == "마":
            if previous.endswith("這"):
                atom.protected = "unassigned-native/這마"
            else:
                assigned[index] = ("嘛", "4.3.1/28")
        elif atom.base == "위":
            if following.startswith("什物"):
                assigned[index] = ("為", "4.1/semantic-purpose")
            elif previous.endswith("欲"):
                assigned[index] = ("對", "user:2026-10-25-destination")
            else:
                assigned[index] = ("𨘗", "4.5/57")
        elif atom.base == "뒤" and (following.startswith("少年") or following.startswith("底來")):
            assigned[index] = ("𨘗", "4.5/57-source-reading-tui")
        elif atom.base == "매" and previous.endswith("看"):
            assigned[index] = ("覓", "4.1/semantic-try")
        elif atom.base == "짇" and following.startswith(("一切", "細粒子", "烏暗", "繁華", "４８年", "兩世人", "規个")):
            assigned[index] = ("這", "4.3.1/42-bound-demonstrative")
        elif atom.base == "힏" and following.startswith("縛"):
            assigned[index] = ("彼", "4.3.1/43-bound-demonstrative")
        elif atom.base == "키" and previous.endswith("想"):
            assigned[index] = ("起", "4.1/dictionary")
        elif atom.base == "궤" and previous.endswith("行"):
            assigned[index] = ("過", "4.1/dictionary")
        elif atom.base == "솅" and previous.endswith("生"):
            assigned[index] = ("性", "C.4.2/nominaliser")
        elif atom.base == "갛" and previous.endswith("落魄 "):
            assigned[index] = ("徦", "4.5/53")
        elif atom.base == "능" and atom.block.tag in {"h1", "h2", "h3"}:
            assigned[index] = ("卵", "4.1/dictionary")
        elif atom.base == "촿":
            assigned[index] = ("掣", "user:2026-10-25")
        elif atom.base == "쉬":
            assigned[index] = ("媠", "user:2026-10-25")
        elif atom.base == "캉" and previous.endswith("好"):
            assigned[index] = ("康", "user:2026-10-25")
        elif atom.base == "완" and following.startswith("來"):
            assigned[index] = ("彎", "user:2026-10-25")
        elif atom.base == "왇" and following.startswith("去"):
            assigned[index] = ("斡", "user:2026-10-25")
        elif atom.base == "핳" and following.startswith("徦"):
            assigned[index] = ("哈", "user:2026-10-25")
        elif atom.base == "벻" and following.startswith("上天"):
            assigned[index] = ("𬦰", "user:2026-10-25")
        elif atom.base == "니" and previous.endswith("똬"):
            assigned[index] = ("邇", "user:2026-10-25")
        elif atom.base in {"아", "옿", "앟", "엏", "왛"}:
            atom.protected = "phonetic-interjection"
        elif atom.base == "텧":
            atom.protected = "user-retained-review"
        elif atom.base == "당":
            atom.protected = "user-retained-review/capability"
        elif atom.base in HANRI:
            assigned[index] = HANRI[atom.base]
    edits, retained = [], []
    for index, atom in enumerate(atoms):
        if atom.kind != "hangul" or atom.neutral:
            continue
        if index not in assigned or atom.protected:
            reason = atom.protected or ("4.2-explicit-Hangul" if atom.base in RETAIN else "needs-review")
            context = "".join(item.base for item in atoms[max(0,index-10):index+11] if item.block is atom.block)
            retained.append({"base": atom.base, "reason": reason, "context": context})
            continue
        hanri, rule = assigned[index]
        following = atoms[index+1] if index+1 < len(atoms) else None
        connected = bool(following and following.block is atom.block and following.base and
                         (HANGUL.search(following.base[0]) or phonetics().is_cjk_char(following.base[0])))
        edits.append({"start": atom.start, "end": atom.end, "before": record["body"][atom.start:atom.end],
                      "after": reading_ruby(hanri, atom.reading, connected), "base": atom.base, "hanri": hanri,
                      "reading": atom.reading, "rule": rule})
    # The alternate verse omits the pronoun's reading; its parallel verse supplies gùn.
    if record.get("id") == "song-727":
        for atom in atoms:
            if atom.kind == "text" and atom.base == "阮" and not atom.neutral:
                edits.append({"start": atom.start, "end": atom.end, "before": "阮",
                              "after": '<ruby style="position: relative">꾼<rt style="font-size: 120%;position: absolute;top: -1.15em;left: 0.2em;z-index: -1">ˎ</rt></ruby>',
                              "base": "阮", "hanri": "꾼", "reading": "꾼`",
                              "rule": "4.2.1/2-user-retained-sung-reading-parallel-verse"})
    return sorted(edits, key=lambda item: item["start"]), retained


def apply_edits(body, edits):
    previous = len(body)
    for edit in sorted(edits, key=lambda item: item["start"], reverse=True):
        start, end = edit["start"], edit["end"]
        if not 0 <= start <= end <= previous or body[start:end] != edit["before"]:
            raise ValueError("Stale or overlapping content edit")
        body = body[:start]+edit["after"]+body[end:]
        previous = start
    return body


def restore_body(body, entry):
    if digest(body) != entry["afterSha256"]:
        raise ValueError("Edited body differs from reviewed v3.2 audit")
    shift = 0
    inverse = []
    for edit in sorted(entry["edits"], key=lambda item: item["start"]):
        start = edit["start"] + shift
        inverse.append({"start": start, "end": start+len(edit["after"]), "before": edit["after"], "after": edit["before"]})
        shift += len(edit["after"])-len(edit["before"])
    original = apply_edits(body, inverse)
    if digest(original) != entry["beforeSha256"]:
        raise ValueError("v3.1 source could not be recovered from reviewed v3.2 edits")
    return original

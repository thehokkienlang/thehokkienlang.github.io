"""Local-only content, reference, validation, and Git services for the website CMS."""
from __future__ import annotations

import hashlib
import html as html_lib
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from assign_dictionary_entry_ids import _atomic_write
from dictionary_editor_service import EditorError, MAIN, read_table, table_bytes
from dictionary_ranking import PRIORITY_COLUMNS, load_priority, read_records
from dictionary_references import CATEGORY_COLUMNS, load_categories
from lyric_timing import blank_timing, reconcile_timing, song_lines, timing_path, validate_timing
from song_editor_import import fragment_source, legacy_lyrics, legacy_suffix, title_segments
from song_title_readings import song_sort_reading, song_title
from simplified_lookup import simplified_headword

REDIRECT_COLUMNS = ("kind", "source", "source_reading", "target_entry_id", "reason", "sources", "date")
GENERATED_PREFIXES = ("_site/", "public/data/")
CONTENT_ROOT = "content"


class WebsiteEditorError(EditorError):
    def __init__(self, message, *, code="validation", details=None):
        super().__init__(message, code=code, details=details)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(repo: Path, *arguments: str, timeout=180, check=True) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(key, None)
    env["GIT_TERMINAL_PROMPT"] = "0"
    result = subprocess.run(
        ["git", "-C", str(repo), *arguments], cwd=repo, env=env,
        stdin=subprocess.DEVNULL, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if check and result.returncode:
        raise WebsiteEditorError((result.stderr or result.stdout).strip() or "Git operation failed.", code="git")
    return result


class WebsiteEditorService:
    def __init__(self, repo: Path):
        self.repo = Path(repo).resolve()
        self.content = self.repo / CONTENT_ROOT
        self.data = self.repo / "data"
        self._song_converter = None
        self._song_converter_stamp = None

    def _tone_marker(self):
        path = self.repo / "desktop" / "hokkien_tone_marker_gui.py"
        dictionary = self.data / MAIN
        stamp = (path.stat().st_mtime_ns, dictionary.stat().st_mtime_ns)
        if self._song_converter is None or self._song_converter_stamp != stamp:
            import importlib.util
            name = "tangliengim_song_editor_tone_marker"
            previous = os.environ.get("HOKKIEN_HANRI_DICT_PATH")
            os.environ["HOKKIEN_HANRI_DICT_PATH"] = str(dictionary)
            try:
                spec = importlib.util.spec_from_file_location(name, path)
                if spec is None or spec.loader is None:
                    raise WebsiteEditorError("The shared TLI renderer could not be loaded.")
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                spec.loader.exec_module(module)
            finally:
                if previous is None:
                    os.environ.pop("HOKKIEN_HANRI_DICT_PATH", None)
                else:
                    os.environ["HOKKIEN_HANRI_DICT_PATH"] = previous
            self._song_converter = module
            self._song_converter_stamp = stamp
        return self._song_converter

    def _inside(self, root: Path, relative: str, *, suffix=None) -> Path:
        if not isinstance(relative, str) or not relative or "\0" in relative:
            raise WebsiteEditorError("Invalid repository path.")
        rel = Path(relative.replace("\\", "/"))
        if rel.is_absolute() or ".." in rel.parts:
            raise WebsiteEditorError("The editor may only access repository source files.", code="forbidden")
        target = (self.repo / rel).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError as error:
            raise WebsiteEditorError("The editor may only access approved source files.", code="forbidden") from error
        if suffix and target.suffix.lower() != suffix:
            raise WebsiteEditorError("Unsupported source-file type.")
        return target

    def page_path(self, relative: str) -> Path:
        target = self._inside(self.content, relative, suffix=".json")
        if target.name == "song-categories.json":
            raise WebsiteEditorError("Song categories use their structured editor.", code="forbidden")
        return target

    @staticmethod
    def _load_json(path: Path) -> tuple[bytes, dict]:
        raw = path.read_bytes()
        try:
            record = json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as error:
            raise WebsiteEditorError(f"{path.name} is not valid UTF-8 JSON: {error}") from error
        if not isinstance(record, dict):
            raise WebsiteEditorError(f"{path.name} must contain one JSON object.")
        return raw, record

    def pages(self) -> list[dict]:
        pages = []
        for path in sorted(self.content.rglob("*.json")):
            if path.name == "song-categories.json":
                continue
            try:
                raw, record = self._load_json(path)
            except WebsiteEditorError:
                continue
            relative = path.relative_to(self.repo).as_posix()
            search_text = record.get('title', path.stem)
            if record.get('type') == 'songs':
                from song_title_readings import song_sort_reading
                search_text += ' ' + record.get('originalTitle', '') + ' ' + song_sort_reading(record)
            version = record.get("songVersion") if isinstance(record.get("songVersion"), dict) else {}
            version_label = str(version.get("label") or "").strip()
            display_title = record.get("title", path.stem) + (f" — {version_label}" if version_label else "")
            pages.append({
                "file": relative, "revision": digest(raw), "id": record.get("id", path.stem),
                "title": display_title, "route": record.get("route", ""),
                "type": record.get("type", path.parent.name), "language": record.get("language", "en"),
                "archived": bool(record.get("archived")),
                "searchText": search_text,
            })
        return pages

    def page(self, relative: str) -> dict:
        path = self.page_path(relative)
        if not path.is_file():
            raise WebsiteEditorError("This page no longer exists. Reload the page list.", code="stale")
        raw, record = self._load_json(path)
        return {"ok": True, "file": path.relative_to(self.repo).as_posix(), "revision": digest(raw), "page": record}

    @staticmethod
    def validate_page_fields(title, body):
        if not isinstance(title, str) or not title.strip():
            raise WebsiteEditorError("Page title is required.")
        if not isinstance(body, str):
            raise WebsiteEditorError("Page content must be text.")
        if any(char in title for char in "\t\r\n\0") or "\0" in body:
            raise WebsiteEditorError("Remove control characters from the page fields.")
        if len(body.encode("utf-8")) > 2_000_000:
            raise WebsiteEditorError("This page is too large for the local editor.")
        return unicodedata.normalize("NFC", title.strip()), unicodedata.normalize("NFC", body)

    def save_page(self, relative: str, revision: str, title: str, body: str) -> dict:
        path = self.page_path(relative)
        raw, record = self._load_json(path)
        if revision != digest(raw):
            raise WebsiteEditorError(
                "This page changed outside the editor. Reload it before saving; your draft is still in the form.",
                code="stale",
            )
        title, body = self.validate_page_fields(title, body)
        record["title"] = title
        record["body"] = body
        relative_path = path.relative_to(self.repo).as_posix()
        rewritten, home_changed = self._sync_lomari(relative_path, record)
        output = (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        if output != raw:
            _atomic_write(path, output)
        message = f"Saved {title} locally." + self._lomari_note(rewritten, home_changed)
        return {"ok": True, "revision": digest(output), "message": message, "page": record,
                "lomariRewritten": rewritten, "changedPaths": [relative_path] + home_changed}

    def _sync_lomari(self, relative: str, record: dict) -> tuple[int, list[str]]:
        """Regenerate Lomari from the Hokkien text (audit B7): the page's own lines, and for a song
        its button on the home page. Lines waiting in docs/lomari-review.json are left alone."""
        import lomari_sync

        songs = lomari_sync.song_records(self.repo)
        if record.get("type") == "songs":
            for link in (record.get("sourceUrl"), record.get("route")):
                if link:
                    songs[lomari_sync.unquote(link).rstrip("/").lower()] = record
        under_review = lomari_sync.review_keys(self.repo)
        rewritten = 0
        if relative not in lomari_sync.EXCLUDED:
            record["body"], rewritten = lomari_sync.sync_body(relative, record["body"], songs, under_review)
        home_changed = []
        home = self.repo / lomari_sync.HOME
        if record.get("type") == "songs" and relative != lomari_sync.HOME and home.is_file():
            home_raw, home_record = self._load_json(home)
            home_record["body"], count = lomari_sync.sync_body(
                lomari_sync.HOME, home_record["body"], songs, under_review)
            if count:
                _atomic_write(home, (json.dumps(home_record, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
                home_changed.append(lomari_sync.HOME)
        return rewritten, home_changed

    @staticmethod
    def _lomari_note(rewritten: int, home_changed: list[str]) -> str:
        notes = []
        if rewritten:
            notes.append(f"{rewritten} Lomari line{'s' if rewritten != 1 else ''} regenerated from the Hangul")
        if home_changed:
            notes.append("the home-page song button updated")
        text = "; ".join(notes)
        return f" {text[:1].upper()}{text[1:]}." if notes else ""

    def entries(self) -> tuple[list[dict], dict[str, dict]]:
        records = read_records(self.data / MAIN)
        compact = [{"entry_id": row["entry_id"], "hanri": row["hanri"],
                    "reading": row["corrected"] or row["reading"], "english": row["english"]}
                   for row in records]
        return compact, {row["entry_id"]: row for row in records}

    def lyric_timing(self, relative):
        opened = self.page(relative)
        record = opened['page']
        try:
            video, lines = song_lines(record)
            path = timing_path(self.repo, record)
            self._inside(self.data, path.relative_to(self.repo).as_posix(), suffix='.json')
            raw = path.read_bytes() if path.exists() else b''
            warning = ''
            stored = json.loads(raw) if raw else None
            try:
                data = validate_timing(record, stored) if raw else blank_timing(record)
            except ValueError:
                data = reconcile_timing(record, stored)
                warning = 'The lyrics, recording, or stored timing structure changed. Existing times were preserved; review affected sentences before saving.'
        except (ValueError, json.JSONDecodeError) as error:
            raise WebsiteEditorError(str(error)) from error
        return {'ok': True, 'file': opened['file'], 'sourceRevision': opened['revision'], 'warning': warning,
                'revision': digest(raw), 'title': record['title'], 'videoId': video, 'timing': data,
                'lines': [{key: line[key] for key in ('id', 'label', 'html')} for line in lines]}

    def save_lyric_timing(self, relative, source_revision, revision, data, base=None, labels=None, overwrite_revision=None):
        opened = self.lyric_timing(relative)
        if opened['sourceRevision'] != source_revision:
            if not isinstance(labels, list) or labels != [line['label'] for line in opened['lines']]:
                raise WebsiteEditorError('Lyric text or order changed outside this window. Your draft remains on screen; save a backup before reloading.', code='stale')
            if data.get('videoId') != opened['videoId'] or len(data.get('cues', [])) != len(opened['timing']['cues']):
                raise WebsiteEditorError('The recording or lyric count changed. Your draft remains on screen.', code='stale')
            data = {**data, 'cues': [{**cue, 'fingerprint': current['fingerprint']} for cue, current in zip(data['cues'], opened['timing']['cues'])]}
        if opened['revision'] != revision:
            if not isinstance(base, dict) or opened['warning']:
                raise WebsiteEditorError('Timings changed outside this window. Your draft remains on screen.', code='stale')
            current = opened['timing']
            if len(base.get('cues', [])) != len(data['cues']) or len(current['cues']) != len(data['cues']):
                raise WebsiteEditorError('The lyric count changed. Your draft remains on screen.', code='stale')
            merged = []
            conflict = False
            for prior, mine, theirs in zip(base['cues'], data['cues'], current['cues']):
                if prior.get('id') != mine.get('id') or mine.get('id') != theirs.get('id'):
                    raise WebsiteEditorError('Lyric order changed. Your draft remains on screen.', code='stale')
                combined = dict(theirs)
                for key in ('start', 'end'):
                    mine_changed = mine.get(key) != prior.get(key)
                    theirs_changed = theirs.get(key) != prior.get(key)
                    conflict |= mine_changed and theirs_changed and mine.get(key) != theirs.get(key)
                    if mine_changed:
                        combined[key] = mine.get(key)
                merged.append(combined)
            conflict |= data.get('status') != base.get('status') and current.get('status') != base.get('status') and data.get('status') != current.get('status')
            if conflict and overwrite_revision != opened['revision']:
                return {'ok': False, 'conflict': True, 'revision': opened['revision'], 'error': 'Some of the same timings changed on disk. Overwrite those conflicting changes with your draft?'}
            data = {**data, 'cues': merged, 'status': data['status'] if data['status'] != base.get('status') else current['status']}
        record = self.page(relative)['page']
        try:
            clean = validate_timing(record, data)
        except ValueError as error:
            raise WebsiteEditorError(str(error)) from error
        path = timing_path(self.repo, record)
        path.parent.mkdir(parents=True, exist_ok=True)
        output = (json.dumps(clean, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        _atomic_write(path, output)
        return {'ok': True, 'revision': digest(output), 'sourceRevision': opened['sourceRevision'], 'lines': opened['lines'], 'timing': clean,
                'message': 'Lyric timings saved locally. Nothing was committed or pushed.'}

    @staticmethod
    def _json_bytes(value) -> bytes:
        return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    def _song_support_files(self):
        return (
            self.content / "song-categories.json",
            self.repo / "migration" / "song-urls.json",
            self.repo / "migration" / "wordpress-map.json",
        )

    def _song_categories(self):
        path, _, _ = self._song_support_files()
        raw, categories = path.read_bytes(), json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(categories, list):
            raise WebsiteEditorError("Song categories are not valid JSON data.")
        return raw, categories

    def song_editor_snapshot(self):
        category_raw, categories = self._song_categories()
        _, urls_path, manifest_path = self._song_support_files()
        songs = []
        for path in sorted((self.content / "songs").glob("*.json")):
            try:
                raw, record = self._load_json(path)
            except WebsiteEditorError:
                continue
            if record.get("type") != "songs":
                continue
            try:
                title_reading = song_sort_reading(record)
            except (KeyError, TypeError, ValueError):
                title_reading = ""
            editor_source = record.get("songEditor")
            version = record.get("songVersion") if isinstance(record.get("songVersion"), dict) else {}
            version_label = str(version.get("label") or "").strip()
            display_title = record.get("title", path.stem) + (f" — {version_label}" if version_label else "")
            songs.append({
                "file": path.relative_to(self.repo).as_posix(),
                "revision": digest(raw),
                "title": display_title,
                "route": record.get("route", ""),
                "editable": isinstance(editor_source, dict),
                "searchText": " ".join(filter(None, (
                    record.get("title", path.stem), record.get("route", ""),
                    record.get("originalTitle", ""), title_reading,
                    record.get("mandarinAlternativeTitle", ""),
                    record.get("mandarinAlternativeTitleSimplified", ""),
                    editor_source.get("titleSource", "") if isinstance(editor_source, dict) else "",
                ))),
            })
        labels = [{"id": row.get("id", ""), "label": row.get("labels", {}).get("en", row.get("id", ""))}
                  for row in categories]
        return {
            "ok": True,
            "songs": songs,
            "categories": labels,
            "categoryRevision": digest(category_raw),
            "urlRevision": digest(urls_path.read_bytes()),
            "manifestRevision": digest(manifest_path.read_bytes()),
        }

    def _resolve_hyphenated_readings(self, lyrics, *, from_page=False):
        """Give hyphenated readings in a non-final position a citation tone.

        A published page writes a joined syllable with the tone actually sung and a hyphen
        ([起키ˆ-] is khî, [有우-] is u). from_page=True (a song imported from its page) finds
        the citation tone that renders that same tone, preferring the dictionary's reading.
        Song Editor sources saved before this ([在재ˉ-]) already hold a citation tone; for them a
        reading is replaced only when exactly one dictionary reading renders the same ruby and
        Lomari. Anything unresolved stays as written. Returns the new lyrics and the count.
        """
        converter = self._tone_marker()
        index = converter.load_hanri_reading_index()
        digits = converter.normalize_tone_symbols_to_digits
        probe = "[相쇼5]"
        cache = {}

        def surface(hanri, reading):
            key = (hanri, reading)
            if key not in cache:
                result = converter.convert_hangul_to_html(f"[{hanri}{reading}]{probe}", "song")
                ruby = re.search(re.escape(hanri) + r"<rt[^>]*>([^<]*)</rt>", result["html"])
                cache[key] = ruby and (digits(ruby.group(1).rstrip("-")), " ".join(result["lomari"].split()))
            return cache[key]

        def sung_tone_match(hanri, reading):
            """A citation that renders the page's sung tone; the dictionary's reading first."""
            wanted = digits(reading.rstrip("-"))
            rendered = lambda value: (surface(hanri, value) or (None,))[0] == wanted
            dictionary = sorted({str(entry.get("reading") or "") for entry in index.get(hanri, [])} - {""})
            matches = [value for value in dictionary if rendered(value)]
            if matches:
                # Several dictionary readings can sandhi to the same sung tone (若 나4/나5 both give
                # na); they render identically here, so the first is as good as any.
                return matches[0]
            base = re.sub(r"[1-5]$", "", wanted)
            # Every match renders this same sung tone here, so any of them is output-identical.
            return next((value for value in [base + tone for tone in "12345"] + [base] if rendered(value)), None)

        def resolve(match):
            parsed = converter.split_hanri_hangul_bracket(match.group(1))
            # On a page every reading is the sung tone; a saved source only hyphenates them.
            if not parsed or not (from_page or parsed[1].endswith("-")):
                return match.group(0)
            # Only where a Hokkien syllable follows on the line, the position the probe models.
            # Elsewhere (line end, punctuation, a Zhuyin word) the hyphen also joins the Lomari
            # to what follows, so it is kept.
            rest = match.string[match.end():]
            following = rest[:rest.find("]") + 1] if rest.startswith("[") else rest[:1]
            # Syllables, or TLI's archaic jamo spellings such as ᄐᅷ.
            if not re.search("[가-힣ᄀ-ᇿꥠ-꥿ힰ-퟿]", following):
                return match.group(0)
            hanri, reading = parsed
            if from_page:
                found = sung_tone_match(hanri, reading)
            else:
                target = surface(hanri, reading)
                readings = {str(entry.get("reading") or "") for entry in index.get(hanri, [])}
                matches = sorted(value for value in readings if value and surface(hanri, value) == target)
                found = matches[0] if target and len(matches) == 1 else None
            if not found:
                return match.group(0)
            if found == reading:
                return match.group(0)
            counter[0] += 1
            return f"[{hanri}{found}]"

        stops = ",.!?:;，。！？：；、’'“”()「」『』…‧~"

        def sung_hangul(text):
            """Typed Hangul on a page also shows the sung tone (릐ꞈ is lî). Where the song pass
            will apply sandhi (a syllable follows), write the citation tone that sandhis to it."""
            out, index = [], 0
            while index < len(text):
                if text[index] == "[":
                    close = text.find("]", index + 1)
                    if close >= 0:
                        out.append(text[index:close + 1])
                        index = close + 1
                        continue
                unit = converter.hangul_reading_unit_at(text, index)
                if unit is None:
                    out.append(text[index])
                    index += 1
                    continue
                reading, end = unit
                sung = digits(reading)
                follows = end < len(text) and not text[end].isspace() and text[end] not in stops
                if follows and re.search(r"[1-5]$", sung):
                    base = sung[:-1]
                    citation = next((base + tone for tone in "12345"
                                     if digits(converter.citation_to_sandhi_reading(base + tone) or base + tone) == sung), None)
                    if citation and citation != sung:
                        reading = citation
                        counter[0] += 1
                out.append(reading)
                index = end
            return "".join(out)

        counter = [0]
        resolved = []
        for item in lyrics:
            if isinstance(item, dict) and item.get("kind") == "line":
                text = str(item.get("text", ""))
                if from_page or "-]" in text:
                    text = re.sub(r"\[([^\]]+)\]", resolve, text)
                if from_page:
                    text = sung_hangul(text)
                if text != item.get("text"):
                    item = {**item, "text": text}
            resolved.append(item)
        return resolved, counter[0]

    def song_editor_song(self, relative):
        path = self._inside(self.content / "songs", relative, suffix=".json")
        if not path.is_file():
            raise WebsiteEditorError("This song no longer exists. Reload the song list.", code="stale")
        raw, record = self._load_json(path)
        draft = record.get("songEditor")
        imported = not isinstance(draft, dict) or draft.get("version") != 1
        if imported:
            draft, _suffix = self._import_legacy_song(record)
        else:
            draft = dict(draft)
        draft["mandarinTitle"] = self._song_mandarin_title(record)
        draft["mandarinSimplifiedTitle"] = self._song_mandarin_simplified_title(record)
        draft["mandarinAlternativeTitle"] = self._song_mandarin_alternative_title(record)
        draft["mandarinAlternativeSimplifiedTitle"] = self._song_mandarin_alternative_simplified_title(record)
        if not draft.get("titleTliRuby") and draft.get("titleAnnotationSystem", "tli") == "tli":
            title_ruby = self._tli_title_ruby_from_source(draft.get("titleSource", ""))
            if not title_ruby:
                try:
                    title_html, _ = song_title(record)
                    recovered_source = fragment_source(title_html)
                    title_ruby = self._tli_title_ruby_from_source(recovered_source)
                    if title_ruby:
                        draft["titleSource"] = recovered_source
                except (KeyError, TypeError, ValueError):
                    pass
            draft["titleTliRuby"] = title_ruby
        draft["lyrics"], converted = self._resolve_hyphenated_readings(draft.get("lyrics") or [], from_page=imported)
        return {
            "ok": True,
            "convertedReadings": converted,
            "file": path.relative_to(self.repo).as_posix(),
            "revision": digest(raw),
            "route": record.get("route", ""),
            "draft": draft,
            "imported": imported,
        }

    def _import_legacy_song(self, record):
        body = str(record.get("body") or "")
        lyrics = legacy_lyrics(body)
        if not lyrics:
            raise WebsiteEditorError("No editable lyric lines could be recovered from this existing song.")
        try:
            title_html, _ = song_title(record)
            title_source = fragment_source(title_html)
            legacy_title = {
                "title": str(record.get("title") or "").strip(),
                "source": title_source,
                "segments": title_segments(title_html),
            }
        except (KeyError, TypeError, ValueError):
            title_source = str(record.get("title") or "").strip()
            legacy_title = None
        video = re.search(r"youtube(?:-nocookie)?\.com/embed/([A-Za-z0-9_-]{11})", body)
        if not video:
            raise WebsiteEditorError("The existing song's YouTube video could not be recovered.")
        _, categories = self._song_categories()
        route = record.get("route", "")
        version = record.get("songVersion") if isinstance(record.get("songVersion"), dict) else {}
        category_route = version.get("groupRoute") or route
        category = next((row.get("id", "") for row in categories if category_route in row.get("routes", [])), "")
        if not category and categories:
            category = categories[0].get("id", "")
        draft = {
            "version": 1,
            "title": str(record.get("title") or "").strip(),
            "mandarinTitle": self._song_mandarin_title(record),
            "mandarinSimplifiedTitle": self._song_mandarin_simplified_title(record),
            "mandarinAlternativeTitle": self._song_mandarin_alternative_title(record),
            "mandarinAlternativeSimplifiedTitle": self._song_mandarin_alternative_simplified_title(record),
            "titleSource": title_source,
            "videoUrl": f"https://www.youtube.com/watch?v={video.group(1)}",
            "category": category,
            "lyrics": lyrics,
        }
        if legacy_title:
            draft["legacyTitle"] = legacy_title
        return draft, legacy_suffix(body)

    @staticmethod
    def _song_mandarin_title(record):
        value = str(record.get("originalTitle") or record.get("title") or "").strip()
        return re.sub(r"\s+諺文(?:/中文)?歌詞\s*$", "", value).strip()

    @classmethod
    def _song_mandarin_simplified_title(cls, record):
        stored = str(record.get("mandarinTitleSimplified") or "").strip()
        if stored:
            return stored
        traditional = cls._song_mandarin_title(record)
        return simplified_headword(traditional) or traditional

    @staticmethod
    def _song_mandarin_alternative_title(record):
        editor = record.get("songEditor") if isinstance(record.get("songEditor"), dict) else {}
        return str(record.get("mandarinAlternativeTitle") or editor.get("mandarinAlternativeTitle") or "").strip()

    @classmethod
    def _song_mandarin_alternative_simplified_title(cls, record):
        editor = record.get("songEditor") if isinstance(record.get("songEditor"), dict) else {}
        stored = str(record.get("mandarinAlternativeTitleSimplified")
                     or editor.get("mandarinAlternativeSimplifiedTitle") or "").strip()
        if stored:
            return stored
        traditional = cls._song_mandarin_alternative_title(record)
        return simplified_headword(traditional) or traditional

    def simplify_song_title(self, title):
        traditional = self._plain(title, "Mandarin title", required=True)
        return {"ok": True, "title": simplified_headword(traditional) or traditional}

    @staticmethod
    def _youtube_id(value):
        text = str(value or "").strip()
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", text):
            return text
        try:
            parsed = urlsplit(text)
        except ValueError:
            return None
        host = parsed.netloc.lower().removeprefix("www.")
        candidate = ""
        if host == "youtu.be":
            candidate = parsed.path.strip("/").split("/", 1)[0]
        elif host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
            if parsed.path == "/watch":
                candidate = parse_qs(parsed.query).get("v", [""])[0]
            else:
                parts = parsed.path.strip("/").split("/")
                if len(parts) >= 2 and parts[0] in {"embed", "shorts", "live"}:
                    candidate = parts[1]
        return candidate if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate) else None

    def _normalize_song_draft(self, draft, *, existing_route=""):
        if not isinstance(draft, dict):
            raise WebsiteEditorError("Song data must be an object.")
        title = self._plain(draft.get("title"), "Song title", required=True)
        if len(title) > 160 or any(char in title for char in "/\\?#"):
            raise WebsiteEditorError("Song title is too long or contains a route separator.")
        mandarin_title = self._plain(draft.get("mandarinTitle"), "Mandarin title", required=True)
        if len(mandarin_title) > 160:
            raise WebsiteEditorError("Mandarin title is too long.")
        mandarin_simplified_title = self._plain(
            draft.get("mandarinSimplifiedTitle"), "Simplified Mandarin title", required=True)
        if len(mandarin_simplified_title) > 160:
            raise WebsiteEditorError("Simplified Mandarin title is too long.")
        alternative_title = self._plain(draft.get("mandarinAlternativeTitle", ""), "Alternative Mandarin title")
        alternative_simplified_title = self._plain(
            draft.get("mandarinAlternativeSimplifiedTitle", ""), "Alternative Simplified Mandarin title")
        if len(alternative_title) > 160 or len(alternative_simplified_title) > 160:
            raise WebsiteEditorError("An alternative Mandarin title is too long.")
        if bool(alternative_title) != bool(alternative_simplified_title):
            raise WebsiteEditorError("Fill both alternative Mandarin title fields, or leave both blank.")
        title_system = self._plain(draft.get("titleAnnotationSystem", "tli"), "Title annotation")
        if title_system not in {"tli", "zhuyin"}:
            raise WebsiteEditorError("Choose TLI or Zhuyin for the title annotation.")
        title_source = self._plain(
            draft.get("titleSource") or (title if title_system == "zhuyin" else ""),
            "TLI title", required=True)
        if len(title_source) > 500:
            raise WebsiteEditorError("TLI title is too long.")
        title_tli_ruby = self._plain(
            draft.get("titleTliRuby") or self._tli_title_ruby_from_source(title_source),
            "TLI title ruby", required=title_system == "tli" and any(self._tone_marker().is_cjk_char(char)
                                                                      for char in title))
        if len(title_tli_ruby) > 500:
            raise WebsiteEditorError("The TLI title ruby is too long.")
        if title_system == "tli" and title_tli_ruby:
            title_source = self._tli_title_source(title, title_tli_ruby, title_source)
        title_zhuyin = self._plain(draft.get("titleZhuyin", ""), "Zhuyin title reading",
                                   required=title_system == "zhuyin")
        title_pinyin = self._plain(draft.get("titlePinyin", ""), "Title Pinyin",
                                  required=title_system == "zhuyin")
        if len(title_zhuyin) > 500 or len(title_pinyin) > 500:
            raise WebsiteEditorError("A title reading is too long.")
        if title_system == "zhuyin":
            self._zhuyin_title_segments(title, title_zhuyin)
        video_url = self._plain(draft.get("videoUrl"), "YouTube link", required=True)
        video_id = self._youtube_id(video_url)
        if not video_id:
            raise WebsiteEditorError("Enter a valid YouTube video link or video ID.")
        _, categories = self._song_categories()
        category = self._plain(draft.get("category"), "Song category", required=True)
        if category not in {row.get("id") for row in categories}:
            raise WebsiteEditorError("Choose an existing song category.")
        raw_lyrics = draft.get("lyrics")
        if not isinstance(raw_lyrics, list) or len(raw_lyrics) > 600:
            raise WebsiteEditorError("Lyrics must be a list of at most 600 rows.")
        lyrics = []
        for item in raw_lyrics:
            if not isinstance(item, dict):
                raise WebsiteEditorError("Each lyric row must be structured data.")
            if item.get("kind") == "break":
                if lyrics and lyrics[-1].get("kind") != "break":
                    lyrics.append({"kind": "break"})
                continue
            text = self._plain(item.get("text"), "Lyric line", required=True)
            if len(text) > 1200:
                raise WebsiteEditorError("A lyric line is too long.")
            line = {"kind": "line", "text": text, "grey": bool(item.get("grey"))}
            if "pinyin" in item and "lomari" in item:
                raise WebsiteEditorError("Choose either Mandarin Pinyin or custom Lomari for one lyric line.")
            if "pinyin" in item:
                pinyin = self._plain(item.get("pinyin", ""), "Mandarin Pinyin", required=True)
                if len(pinyin) > 1600:
                    raise WebsiteEditorError("A Mandarin Pinyin line is too long.")
                line["pinyin"] = pinyin
            elif "lomari" in item:
                lomari = self._plain(item.get("lomari", ""), "Custom Lomari", required=True)
                if len(lomari) > 1600:
                    raise WebsiteEditorError("A custom Lomari line is too long.")
                line["lomari"] = lomari
            lyrics.append(line)
        while lyrics and lyrics[-1].get("kind") == "break":
            lyrics.pop()
        if not any(item.get("kind") == "line" for item in lyrics):
            raise WebsiteEditorError("Add at least one lyric line.")
        legacy_title = self._normalize_legacy_title(draft.get("legacyTitle"), title, title_source)
        route_title = re.sub(r"\s+", "", title)
        route = existing_route or f"/songs/{route_title}/"
        clean = {
            "version": 1,
            "title": title,
            "mandarinTitle": mandarin_title,
            "mandarinSimplifiedTitle": mandarin_simplified_title,
            "mandarinAlternativeTitle": alternative_title,
            "mandarinAlternativeSimplifiedTitle": alternative_simplified_title,
            "titleAnnotationSystem": title_system,
            "titleSource": title_source,
            "titleTliRuby": title_tli_ruby,
            "titleZhuyin": title_zhuyin,
            "titlePinyin": title_pinyin,
            "videoUrl": f"https://www.youtube.com/watch?v={video_id}",
            "category": category,
            "lyrics": lyrics,
        }
        if legacy_title:
            clean["legacyTitle"] = legacy_title
        return clean, route, video_id

    @staticmethod
    def _zhuyin_title_segments(title, reading):
        if any(char.isspace() for char in title):
            raise WebsiteEditorError("A Zhuyin-annotated title cannot contain spaces.")
        readings = reading.split()
        if len(readings) != len(title):
            raise WebsiteEditorError("Enter one spaced Zhuyin reading for each title character.")
        if any(not re.search(r"[㄀-ㄯㆠ-ㆿ]", value) for value in readings):
            raise WebsiteEditorError("Each Zhuyin title reading must contain Bopomofo.")
        return [{"base": base, "reading": value, "system": "bopomofo"}
                for base, value in zip(title, readings)]

    def _tli_title_segments(self, title, reading):
        converter = self._tone_marker()
        bases = [char for char in title if converter.is_cjk_char(char)]
        readings = reading.split()
        if len(readings) != len(bases):
            raise WebsiteEditorError("Enter one spaced Hangul ruby reading for each Hanri title character.")
        segments = []
        for base, value in zip(bases, readings):
            unit = converter.hangul_reading_unit_at(value, 0)
            if not unit or unit[1] != len(value):
                raise WebsiteEditorError("Each TLI title ruby reading must contain exactly one Hangul syllable.")
            segments.append({"base": base, "reading": value, "system": "hangul"})
        return segments

    def _tli_title_source(self, title, reading, fallback):
        segments = iter(self._tli_title_segments(title, reading))
        converter = self._tone_marker()
        if not any(converter.is_cjk_char(char) for char in title):
            return fallback
        output = []
        for char in title:
            if converter.is_cjk_char(char):
                segment = next(segments)
                output.append(f'[{char}{segment["reading"]}]')
            else:
                output.append(char)
        return "".join(output)

    def _tli_title_ruby_from_source(self, source):
        converter = self._tone_marker()
        readings = []
        for match in re.finditer(r"\[([^\]]+)\]", str(source or "")):
            parsed = converter.split_hanri_hangul_bracket(match.group(1))
            if not parsed:
                continue
            hanri, reading = parsed
            units = []
            index = 0
            while index < len(reading):
                unit = converter.hangul_reading_unit_at(reading, index)
                if not unit:
                    return ""
                units.append(unit[0])
                index = unit[1]
            if len(units) != len(hanri):
                return ""
            readings.extend(units)
        return " ".join(readings)

    @staticmethod
    def _normalize_legacy_title(value, title, title_source):
        if not isinstance(value, dict) or value.get("title") != title or value.get("source") != title_source:
            return None
        raw_segments = value.get("segments")
        if not isinstance(raw_segments, list) or not raw_segments or len(raw_segments) > 200:
            return None
        segments = []
        for segment in raw_segments:
            if not isinstance(segment, dict):
                return None
            if set(segment) == {"text"}:
                text = str(segment["text"])
                if len(text) > 500 or any(char in text for char in "\0\r\n"):
                    return None
                segments.append({"text": text})
                continue
            if set(segment) != {"base", "reading", "system"}:
                return None
            base, reading, system = str(segment["base"]), str(segment["reading"]), segment["system"]
            if not base or len(base) > 200 or len(reading) > 500 or system not in {"hangul", "bopomofo"}:
                return None
            if any(char in base + reading for char in "\0\r\n"):
                return None
            segments.append({"base": base, "reading": reading, "system": system})
        return {"title": title, "source": title_source, "segments": segments}

    @staticmethod
    def _render_legacy_title(value):
        result = []
        for segment in value["segments"]:
            if "text" in segment:
                result.append(html_lib.escape(segment["text"]))
                continue
            css = "hanri-title" + (" bopomofo-title" if segment["system"] == "bopomofo" else "")
            result.append(
                f'<ruby class="{css}">{html_lib.escape(segment["base"])}'
                f'<rt>{html_lib.escape(segment["reading"])}</rt></ruby>'
            )
        return "".join(result)

    @staticmethod
    def _youtube_embed(video_id):
        safe = html_lib.escape(video_id, quote=True)
        return (
            '<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube '
            'wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper">\n'
            '<span class="embed-youtube" style="text-align:center; display: block;">'
            f'<iframe loading="lazy" class="youtube-player" width="640" height="360" '
            f'src="https://www.youtube.com/embed/{safe}?version=3&amp;rel=1&amp;showsearch=0&amp;showinfo=1'
            '&amp;iv_load_policy=1&amp;fs=1&amp;hl=en&amp;autohide=2&amp;wmode=transparent" '
            'allowfullscreen="true" style="border:0;" sandbox="allow-scripts allow-same-origin '
            'allow-popups allow-presentation allow-popups-to-escape-sandbox"></iframe></span>\n'
            '</div></figure>'
        )

    @staticmethod
    def _render_mandarin_lyric_line(item):
        return (
            '<p style="font-family:Sans-serif, Noto Sans">\n'
            '  <span class="lyric-line">\n'
            f'    {html_lib.escape(item["text"])}\n'
            '  </span>\n'
            '  <span class="lyric-lomari">\n'
            f'    {html_lib.escape(item["pinyin"])}\n'
            '  </span>\n'
            '</p>'
        )

    @staticmethod
    def _apply_manual_lomari(markup, lomari):
        pattern = re.compile(
            r'(<span class="lyric-lomari)(">\s*)(.*?)(\s*</span>)',
            re.S,
        )
        replacement = lambda match: (
            match.group(1) + ' lyric-lomari-manual' + match.group(2)
            + html_lib.escape(lomari) + match.group(4)
        )
        updated, count = pattern.subn(replacement, markup, count=1)
        if count != 1:
            raise WebsiteEditorError("The custom Lomari line could not be applied.")
        return updated

    def render_song_draft(self, draft, *, existing_route=""):
        clean, route, video_id = self._normalize_song_draft(draft, existing_route=existing_route)
        converter = self._tone_marker()
        try:
            if clean["titleAnnotationSystem"] == "zhuyin":
                title_html = self._render_legacy_title({
                    "segments": self._zhuyin_title_segments(clean["title"], clean["titleZhuyin"]),
                })
            elif clean.get("legacyTitle") and not clean.get("titleTliRuby"):
                title_html = self._render_legacy_title(clean["legacyTitle"])
            else:
                title_html = converter.convert_hangul_to_html(clean["titleSource"], "title")["html"]
                visible_title = converter.visible_source_for_lomari_next_line(clean["titleSource"])
                comparable = lambda value: re.sub(r"[\s’']+", "", unicodedata.normalize("NFC", value))
                # A title in Latin letters (Maybe Maybe, Aphrodite) is spelled in Hangul for
                # its TLI title, so the two can only be compared when the title is in TLI.
                written_in_tli = re.search(r"[㐀-鿿\U00020000-\U0003134f가-힣]", clean["title"])
                if written_in_tli and comparable(visible_title) != comparable(clean["title"]):
                    raise WebsiteEditorError("The visible TLI title must match the song title.")
            blocks = []
            for item in clean["lyrics"]:
                if item["kind"] == "break":
                    blocks.append("<br>")
                elif item.get("pinyin"):
                    blocks.append(self._render_mandarin_lyric_line(item))
                else:
                    markup = converter.convert_hangul_to_html(
                        item["text"], "song", song_grey=item["grey"])["html"]
                    if item.get("lomari"):
                        markup = self._apply_manual_lomari(markup, item["lomari"])
                    blocks.append(markup)
        except WebsiteEditorError:
            raise
        except Exception as error:
            raise WebsiteEditorError(f"TLI rendering failed: {error}") from error
        content_blocks = [
            self._youtube_embed(video_id),
            '<h3 class="wp-block-heading">漢諺混寫 Hanri-Hangul mixed script</h3>',
            *blocks,
        ]
        preview_body = "\n\n\n".join(content_blocks) + "\n"
        body = f'<h2 class="wp-block-heading">{title_html}</h2>\n\n\n' + preview_body
        return {"ok": True, "draft": clean, "route": route, "videoId": video_id,
                "titleHtml": title_html, "previewBody": preview_body, "body": body}

    def _next_song_identity(self):
        values = []
        for path in (self.content / "songs").glob("song-*.json"):
            match = re.fullmatch(r"song-(\d+)\.json", path.name)
            if match:
                values.append(int(match.group(1)))
        identity = max(values, default=0) + 1
        while (self.content / "songs" / f"song-{identity}.json").exists():
            identity += 1
        return identity

    def save_song(self, relative, revision, category_revision, url_revision, manifest_revision, draft):
        existing = None
        path = None
        existing_route = ""
        if relative:
            path = self._inside(self.content / "songs", relative, suffix=".json")
            raw, existing = self._load_json(path)
            if digest(raw) != revision:
                raise WebsiteEditorError("This song changed outside the editor. Reload before saving.", code="stale")
            existing_route = existing.get("route", "")
        suffix = ""
        if existing is not None:
            if isinstance(existing.get("songEditor"), dict):
                suffix = str(existing.get("songEditorLegacySuffix") or "")
            else:
                _imported, suffix = self._import_legacy_song(existing)
        rendered = self.render_song_draft(draft, existing_route=existing_route)
        clean, route, body = rendered["draft"], rendered["route"], rendered["body"]
        if suffix:
            body = body.rstrip() + "\n\n" + suffix.lstrip()
        category_path, urls_path, manifest_path = self._song_support_files()
        category_raw, url_raw, manifest_raw = (category_path.read_bytes(), urls_path.read_bytes(), manifest_path.read_bytes())
        if (digest(category_raw) != category_revision or digest(url_raw) != url_revision or
                digest(manifest_raw) != manifest_revision):
            raise WebsiteEditorError("Song categories or route data changed outside this window. Reload first.", code="stale")
        categories, urls, manifest = (json.loads(category_raw), json.loads(url_raw), json.loads(manifest_raw))
        for other in (self.content / "songs").glob("*.json"):
            if path and other.resolve() == path.resolve():
                continue
            try:
                other_record = json.loads(other.read_text(encoding="utf-8"))
            except (UnicodeError, json.JSONDecodeError):
                continue
            if other_record.get("route") == route:
                raise WebsiteEditorError("Another song already uses this title and website route.")

        is_new = existing is None
        if is_new:
            source_id = self._next_song_identity()
            identity = f"song-{source_id}"
            path = self.content / "songs" / f"{identity}.json"
            source_url = "https://thehokkienlang.github.io" + route
            record = {"id": identity, "type": "songs", "language": "en", "sourceId": source_id,
                      "sourceUrl": source_url}
        else:
            record = dict(existing)
            source_id = record["sourceId"]
            source_url = record["sourceUrl"]
        existing_original_title = str((existing or {}).get("originalTitle") or "")
        original_suffix_match = re.search(r"(\s+諺文(?:/中文)?歌詞\s*)$", existing_original_title)
        original_suffix = original_suffix_match.group(1) if original_suffix_match else " 諺文歌詞"
        record.update({
            "title": clean["title"],
            "originalTitle": clean["mandarinTitle"] + original_suffix,
            "mandarinTitleSimplified": clean["mandarinSimplifiedTitle"],
            "route": route,
            "sourceModified": datetime.now().astimezone().isoformat(timespec="seconds"),
            "orthography": {"target": "3.2", "review": "structured-song-editor"},
            "body": body,
            "songEditor": clean,
        })
        if clean["mandarinAlternativeTitle"]:
            record["mandarinAlternativeTitle"] = clean["mandarinAlternativeTitle"]
            record["mandarinAlternativeTitleSimplified"] = clean["mandarinAlternativeSimplifiedTitle"]
        else:
            record.pop("mandarinAlternativeTitle", None)
            record.pop("mandarinAlternativeTitleSimplified", None)
        if clean["titleAnnotationSystem"] == "zhuyin":
            record["titleRuby"] = self._zhuyin_title_segments(clean["title"], clean["titleZhuyin"])
            record["titleRomanisation"] = clean["titlePinyin"]
        else:
            record.pop("titleRuby", None)
            record.pop("titleRomanisation", None)
        if suffix:
            record["songEditorLegacySuffix"] = suffix
        rewritten, home_changed = self._sync_lomari(path.relative_to(self.repo).as_posix(), record)
        body = record["body"]
        record["sourceSha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()

        version = record.get("songVersion") if isinstance(record.get("songVersion"), dict) else {}
        grouped_variant = bool(version.get("groupRoute") and route != version.get("groupRoute"))
        if not grouped_variant:
            for category in categories:
                category["routes"] = [value for value in category.get("routes", []) if value != route]
            target_category = next(row for row in categories if row.get("id") == clean["category"])
            target_category.setdefault("routes", []).append(route)
        if is_new:
            urls.append({"old_url": source_url, "new_url": route, "display_title": clean["title"]})
            manifest.setdefault("records", []).append({
                "sourceUrl": source_url, "sourceId": source_id, "route": route,
                "file": path.relative_to(self.repo).as_posix(),
            })
        elif not grouped_variant and not any(row.get("file") == path.relative_to(self.repo).as_posix() for row in manifest.get("records", [])):
            raise WebsiteEditorError("The song is missing from the website content manifest.")

        outputs = {
            path: self._json_bytes(record),
            category_path: self._json_bytes(categories),
            urls_path: self._json_bytes(urls),
            manifest_path: self._json_bytes(manifest),
        }
        changed = []
        for target, output in outputs.items():
            before = target.read_bytes() if target.exists() else b""
            if before != output:
                _atomic_write(target, output)
                changed.append(target.relative_to(self.repo).as_posix())
        return {
            "ok": True,
            "file": path.relative_to(self.repo).as_posix(),
            "revision": digest(outputs[path]),
            "categoryRevision": digest(outputs[category_path]),
            "urlRevision": digest(outputs[urls_path]),
            "manifestRevision": digest(outputs[manifest_path]),
            "route": route,
            "draft": clean,
            "body": body,
            "changedPaths": changed + home_changed,
            "publishPaths": [target.relative_to(self.repo).as_posix() for target in outputs] + home_changed,
            "lomariRewritten": rewritten,
            "message": f'Saved {clean["title"]} locally.{self._lomari_note(rewritten, home_changed)} Nothing was pushed yet.',
        }

    def table_snapshot(self) -> dict:
        entries, by_id = self.entries()
        categories_path = self.data / "dictionary_categories.tsv"
        category_raw = categories_path.read_bytes()
        category_header, category_rows = read_table(category_raw)
        labels, memberships = load_categories(categories_path, list(by_id.values()))
        priorities_path = self.data / "dictionary_priority.tsv"
        priority_raw = priorities_path.read_bytes()
        priority_header, priorities = read_table(priority_raw)
        load_priority(priorities_path, list(by_id.values()))
        redirects_path = self.data / "dictionary_redirects.tsv"
        redirect_raw = redirects_path.read_bytes()
        redirect_header, redirects = read_table(redirect_raw)
        return {
            "ok": True, "entries": entries,
            "categories": {
                "revision": digest(category_raw),
                "labels": [{"category": key, "label": value,
                            "count": sum(key in values for values in memberships.values())}
                           for key, value in labels.items()],
                "memberships": [{**row, "reading": by_id[row["entry_id"]]["corrected"] or by_id[row["entry_id"]]["reading"]}
                                for row in category_rows],
                "columns": category_header,
            },
            "priorities": {"revision": digest(priority_raw), "rows": priorities, "columns": priority_header},
            "references": {"revision": digest(redirect_raw), "rows": redirects, "columns": redirect_header},
        }

    @staticmethod
    def _plain(value, field, *, required=False):
        if not isinstance(value, str) or any(char in value for char in "\t\r\n\0"):
            raise WebsiteEditorError(f"{field}: use plain text without tabs or line breaks.")
        value = unicodedata.normalize("NFC", value.strip())
        if required and not value:
            raise WebsiteEditorError(f"{field} is required.")
        return value

    def _replace_table(self, name: str, revision: str, columns, rows: list[dict], validate):
        path = self.data / name
        before = path.read_bytes()
        if revision != digest(before):
            raise WebsiteEditorError(
                f"{name} changed outside the editor. Reload before saving; your edits remain on screen.", code="stale")
        output = table_bytes(columns, rows)
        with tempfile.TemporaryDirectory(prefix="tli-cms-") as folder:
            candidate = Path(folder) / name
            candidate.write_bytes(output)
            validate(candidate)
        if output != before:
            _atomic_write(path, output)
        return {"ok": True, "revision": digest(output), "message": f"Saved {name} locally."}

    def save_categories(self, revision: str, labels, memberships) -> dict:
        entries, by_id = self.entries()
        if not isinstance(labels, list) or not isinstance(memberships, list):
            raise WebsiteEditorError("Category data must be a list.")
        label_map = {}
        for row in labels:
            key = self._plain(row.get("category"), "Category key", required=True)
            label = self._plain(row.get("label"), "Category label", required=True)
            if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", key):
                raise WebsiteEditorError("Category keys use lowercase letters, numbers, hyphens, and underscores.")
            if key in label_map and label_map[key] != label:
                raise WebsiteEditorError(f"Conflicting labels for category {key}.")
            label_map[key] = label
        seen, rows = set(), []
        used_categories = set()
        for member in memberships:
            key = self._plain(member.get("category"), "Category", required=True)
            identity = self._plain(member.get("entry_id"), "Entry ID", required=True)
            if key not in label_map or identity not in by_id:
                raise WebsiteEditorError("A category membership refers to a missing category or entry.")
            if (key, identity) in seen:
                continue
            seen.add((key, identity))
            used_categories.add(key)
            rows.append({"category": key, "label": label_map[key],
                         "entry": by_id[identity]["hanri"], "entry_id": identity})
        unused = sorted(set(label_map) - used_categories)
        if unused:
            raise WebsiteEditorError(
                "Each category needs at least one entry before it can be saved: " + ", ".join(unused))
        rows.sort(key=lambda row: (row["category"], row["entry_id"]))
        return self._replace_table("dictionary_categories.tsv", revision, CATEGORY_COLUMNS, rows,
                                   lambda path: load_categories(path, list(by_id.values())))

    def save_priorities(self, revision: str, rows) -> dict:
        entries, by_id = self.entries()
        if not isinstance(rows, list):
            raise WebsiteEditorError("Priority data must be a list.")
        output = []
        for row in rows:
            identity = self._plain(row.get("entry_id"), "Entry ID", required=True)
            if identity not in by_id:
                raise WebsiteEditorError(f"Unknown active entry: {identity}")
            rank = str(row.get("rank", "")).strip()
            if not rank.isascii() or not rank.isdigit() or int(rank) < 1:
                raise WebsiteEditorError("Static priority rank must be a positive integer.")
            output.append({"lookup_key": self._plain(row.get("lookup_key"), "Lookup key", required=True),
                           "entry": by_id[identity]["hanri"], "entry_id": identity, "rank": rank})
        output.sort(key=lambda row: (row["lookup_key"], int(row["rank"]), row["entry_id"]))
        return self._replace_table("dictionary_priority.tsv", revision, PRIORITY_COLUMNS, output,
                                   lambda path: load_priority(path, list(by_id.values())))

    def save_references(self, revision: str, rows) -> dict:
        _, by_id = self.entries()
        if not isinstance(rows, list):
            raise WebsiteEditorError("Reference data must be a list.")
        output = []
        for row in rows:
            normalized = {column: self._plain(row.get(column), column, required=column in {"kind", "source", "target_entry_id"})
                          for column in REDIRECT_COLUMNS}
            if normalized["kind"] not in {"headword", "reading"}:
                raise WebsiteEditorError("Reference kind must be headword or reading.")
            if normalized["target_entry_id"] not in by_id:
                raise WebsiteEditorError(f"Unknown active target entry: {normalized['target_entry_id']}")
            output.append(normalized)
        return self._replace_table("dictionary_redirects.tsv", revision, REDIRECT_COLUMNS, output,
                                   lambda path: self._validate_references(path, by_id))

    @staticmethod
    def _validate_references(path: Path, by_id: dict):
        header, rows = read_table(path.read_bytes())
        if tuple(header) != REDIRECT_COLUMNS:
            raise WebsiteEditorError("Reference table has the wrong columns.")
        seen = set()
        for row in rows:
            key = (row["kind"], row["source"], row["source_reading"])
            if key in seen:
                raise WebsiteEditorError("Duplicate dictionary reference: " + " / ".join(key))
            seen.add(key)
            if row["target_entry_id"] not in by_id:
                raise WebsiteEditorError("Reference points to an inactive entry.")

    def _status_records(self):
        raw = git(self.repo, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout
        tokens = raw.split("\0")
        records, index = [], 0
        while index < len(tokens) and tokens[index]:
            token = tokens[index]
            status, path = token[:2], token[3:]
            index += 1
            if status[0] in "RC" and index < len(tokens) and tokens[index]:
                old = tokens[index]
                index += 1
            else:
                old = ""
            records.append((status, path.replace("\\", "/"), old.replace("\\", "/")))
        return records

    def changes(self) -> dict:
        files = []
        for status, relative, old in self._status_records():
            target = self._inside(self.repo, relative)
            generated = relative.startswith(GENERATED_PREFIXES)
            if status == "??":
                if target.is_file() and target.stat().st_size <= 250_000:
                    content = target.read_text(encoding="utf-8", errors="replace")
                    patch = f"--- /dev/null\n+++ b/{relative}\n" + "\n".join("+" + line for line in content.splitlines())
                else:
                    patch = "Untracked binary or large file."
            else:
                patch = git(self.repo, "diff", "--no-ext-diff", "--unified=3", "HEAD", "--", relative,
                            check=False).stdout
            files.append({"status": status, "path": relative, "oldPath": old, "generated": generated,
                          "diff": patch[-300_000:]})
        branch = git(self.repo, "status", "--short", "--branch").stdout.splitlines()
        return {"ok": True, "files": files, "branch": branch[0] if branch else "",
                "fingerprint": self.working_fingerprint()}

    def working_fingerprint(self) -> str:
        state = hashlib.sha256()
        for status, relative, old in self._status_records():
            state.update(f"{status}\0{relative}\0{old}\0".encode("utf-8"))
            target = self._inside(self.repo, relative)
            if target.is_file():
                state.update(hashlib.sha256(target.read_bytes()).digest())
        return state.hexdigest()

    def summary(self) -> dict:
        pages = self.pages()
        entries, _ = self.entries()
        changes = self.changes()
        return {"ok": True, "pages": len(pages), "songs": sum(page["type"] == "songs" for page in pages),
                "entries": len(entries), "changes": len(changes["files"]), "branch": changes["branch"],
                "generatedProtected": list(GENERATED_PREFIXES)}

    def commit(self, message: str, paths: list[str], validated_fingerprint: str) -> dict:
        message = self._plain(message, "Commit message", required=True)
        current = self.changes()
        if validated_fingerprint != current["fingerprint"]:
            raise WebsiteEditorError("Files changed since validation. Validate the current changes before committing.", code="stale")
        allowed = {item["path"] for item in current["files"]}
        if not isinstance(paths, list) or not paths:
            raise WebsiteEditorError("Select at least one reviewed file to commit.")
        selected = []
        for relative in paths:
            self._inside(self.repo, relative)
            if relative not in allowed:
                raise WebsiteEditorError(f"{relative} is no longer an uncommitted change. Reload Changes.", code="stale")
            selected.append(relative)
        staged = {path for path in git(self.repo, "diff", "--cached", "--name-only", "-z").stdout.split("\0") if path}
        unrelated = sorted(staged - set(selected))
        if unrelated:
            raise WebsiteEditorError(
                "Git already has staged files that are not selected here. Commit or unstage them first: "
                + ", ".join(unrelated), code="git")
        git(self.repo, "add", "--", *selected)
        if not git(self.repo, "diff", "--cached", "--quiet", check=False).returncode:
            raise WebsiteEditorError("The selected files have no commit-ready changes.")
        git(self.repo, "commit", "-m", message, timeout=300)
        commit = git(self.repo, "rev-parse", "HEAD").stdout.strip()
        return {"ok": True, "commit": commit, "message": f"Committed {len(selected)} reviewed files locally."}

    def push(self) -> dict:
        branch = git(self.repo, "branch", "--show-current").stdout.strip()
        if not branch:
            raise WebsiteEditorError("The repository is not on a branch. Open it in GitHub Desktop first.", code="git")
        git(self.repo, "push", "origin", branch, timeout=300)
        commit = git(self.repo, "rev-parse", "HEAD").stdout.strip()
        return {"ok": True, "commit": commit, "message": f"Pushed {branch} to GitHub using existing Git authentication."}

    def validation_command(self, kind: str) -> list[str]:
        python = str(Path(sys.executable).with_name("python.exe") if Path(sys.executable).name.lower() == "pythonw.exe" else sys.executable)
        commands = {
            "dictionary": [python, "-X", "utf8", "tools/validate_dictionary_tsv.py"],
            "site": [python, "-X", "utf8", "tools/check_release.py"],
            "source": [python, "-X", "utf8", "tools/check_release.py", "--source-only"],
        }
        if kind not in commands:
            raise WebsiteEditorError("Unknown validation suite.")
        return commands[kind]

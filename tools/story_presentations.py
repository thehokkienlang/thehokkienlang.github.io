"""Shared story presentation without altering archived or audited source bodies."""

import html
import re
from html.parser import HTMLParser

from simplified_lookup import simplified_headword
from song_title_readings import song_title

EGG_ROUTE = '/read/stories/the-egg/'


class SoundCloudPlayer(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.lines = [0] + [match.end() for match in re.finditer('\n', source)]
        self.players = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        src = dict(attrs).get('src', '')
        if tag == 'iframe' and src.startswith('https://w.soundcloud.com/player/'):
            line, column = self.getpos()
            start = self.lines[line - 1] + column
            self.players.append((start, self.get_starttag_text(), src))


def soundcloud_source(body):
    players = SoundCloudPlayer(body).players
    if len(players) != 1:
        raise ValueError('The Egg must have exactly one SoundCloud player')
    return players[0][2]


def shared_soundcloud(body, src):
    players = SoundCloudPlayer(body).players
    if len(players) != 1:
        raise ValueError('The Egg must have exactly one SoundCloud player')
    start, tag, _ = players[0]
    replacement, count = re.subn(r'\bsrc=("[^"]*"|\x27[^\x27]*\x27)',
                                lambda _: 'src="' + html.escape(src, quote=True) + '"', tag)
    if count != 1:
        raise ValueError('SoundCloud iframe has no unique source attribute')
    return body[:start] + replacement + body[start + len(tag):]


class SimplifiedHTML(HTMLParser):
    """Simplify Mandarin notes while preserving Hokkien paragraphs and ruby."""
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.parts = []
        self.protected = []

    def handle_starttag(self, tag, attrs):
        self.parts.append(self.get_starttag_text())
        attributes = dict(attrs)
        hokkien_paragraph = tag == 'p' and re.search(
            r'(?:^|;)\s*text-indent\s*:\s*2em\s*(?:;|$)', attributes.get('style', ''), re.I)
        hokkien_language = attributes.get('lang', '').lower().split('-')[0] == 'nan'
        if tag in {'script', 'style', 'ruby', 'rt', 'rp', 'code', 'pre'} or hokkien_paragraph or hokkien_language:
            self.protected.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.parts.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        self.parts.append(f'</{tag}>')
        if self.protected and self.protected[-1] == tag:
            self.protected.pop()

    def handle_data(self, data):
        if self.protected:
            self.parts.append(data)
            return
        # Mainland Simplified retains 著 in the publishing sense (著作/原著).
        simplified = simplified_headword(data) or data
        self.parts.append(simplified.replace('原着', '原著'))

    def handle_entityref(self, name):
        self.parts.append(f'&{name};')

    def handle_charref(self, name):
        self.parts.append(f'&#{name};')

    def handle_comment(self, data):
        self.parts.append(f'<!--{data}-->')


def simplified_egg(traditional):
    parser = SimplifiedHTML()
    parser.feed(traditional['body'])
    parser.close()
    return {**traditional, 'language': 'zh-Hans', 'route': '/zh-hans' + EGG_ROUTE,
            'body': ''.join(parser.parts),
            'derivedFrom': {'route': traditional['route'], 'language': 'zh-Hant',
                            'conversion': 'tw2s-mandarin-text'}}


def egg_presentation(record, player_source):
    heading, body = song_title({**record, 'title': '卵'})
    subtitle = 'The Egg' if record['language'] == 'en' else '蛋'
    body = f'<h2 class="story-subtitle">{subtitle}</h2>' + shared_soundcloud(body, player_source)
    return heading, body

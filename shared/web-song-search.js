(function (root) {
  'use strict';
  // Song search: one index and one matcher, used by the /songs/ filter and (next) the song-page
  // search box. The index is public/data/song-search-index.json, written by the build; matching
  // follows the shared rule in web-site-search-variants.js.

  let indexRequest = null;
  function loadIndex(url) {
    indexRequest ||= fetch(url || '/public/data/song-search-index.json', {cache: 'no-cache'}).then(response => {
      if (!response.ok) throw new Error(`Song search index request failed: ${response.status}`);
      return response.json();
    });
    return indexRequest;
  }

  const RANK = Object.freeze({all: 0, title: 0, titleStart: 1, titleContains: 2, mandarin: 3, lyrics: 4});

  // index: the parsed song-search-index.json; hanriFold: from TliSiteSearchVariants.loadHanriFold().
  function createMatcher(index, hanriFold) {
    const {normalise} = root.TliSiteSearchVariants;
    const prepared = index.songs.map(song => {
      const lines = song.lines.map(([main, lomari, search, mainHtml]) => ({main, lomari, mainHtml, text: normalise(search, hanriFold)}));
      const titleText = normalise(song.search, hanriFold);
      const mandarinText = normalise(song.mandarinSearch, hanriFold);
      return {song, lines, titleText, mandarinText, text: [titleText, mandarinText, ...lines.map(line => line.text)].join(' ')};
    });
    return {
      // Songs matching `query` (everything when it is empty). Title matches come before lyric
      // matches, closest first: the whole title, then a title that starts with the query, then
      // one that contains it, then the Mandarin title, then lyrics. Songs of equal rank keep index
      // order. Each result gives its `rank`, whether the match is in the Mandarin title only, and
      // the first matching lyric line.
      search(query, {category = ''} = {}) {
        const needle = normalise(query, hanriFold);
        const results = [];
        prepared.forEach((item, order) => {
          if (category && item.song.category !== category) return;
          if (needle && !item.text.includes(needle)) return;
          const rank = !needle ? RANK.all
            : item.titleText === needle ? RANK.title
              : item.titleText.startsWith(needle) ? RANK.titleStart
                : item.titleText.includes(needle) ? RANK.titleContains
                  : item.mandarinText.includes(needle) ? RANK.mandarin
                    : RANK.lyrics;
          results.push({
            song: item.song,
            rank,
            order,
            mandarinMatch: Boolean(needle && item.mandarinText.includes(needle) && !item.titleText.includes(needle)),
            lineMatch: needle ? item.lines.find(line => line.text.includes(needle)) || null : null,
          });
        });
        return results.sort((a, b) => a.rank - b.rank || a.order - b.order);
      },
    };
  }

  root.TliSongSearch = {loadIndex, createMatcher};
})(typeof window !== 'undefined' ? window : globalThis);

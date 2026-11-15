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
      // Songs matching `query` (everything when it is empty), in index order. Each result says
      // whether the match is in the Mandarin title only, and gives the first matching lyric line.
      search(query, {category = ''} = {}) {
        const needle = normalise(query, hanriFold);
        const results = [];
        for (const item of prepared) {
          if (category && item.song.category !== category) continue;
          if (needle && !item.text.includes(needle)) continue;
          results.push({
            song: item.song,
            mandarinMatch: Boolean(needle && item.mandarinText.includes(needle) && !item.titleText.includes(needle)),
            lineMatch: needle ? item.lines.find(line => line.text.includes(needle)) || null : null,
          });
        }
        return results;
      },
    };
  }

  root.TliSongSearch = {loadIndex, createMatcher};
})(typeof window !== 'undefined' ? window : globalThis);

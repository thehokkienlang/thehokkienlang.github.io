// Load the generated dictionary JSON plus its sidecars as one logical document.
// Mirrors tools/dictionary_data.py: hokkien-hanri-dict.json holds entries and
// metadata, -runtime.json the audio/Lomari maps, -indexes.json the build-only
// lookup indexes.
const fs = require('node:fs');
const path = require('node:path');

const SIDECARS = ['runtime', 'indexes'];

function sidecarPath(corePath, part) {
  const parsed = path.parse(corePath);
  return path.join(parsed.dir, `${parsed.name}-${part}${parsed.ext}`);
}

function loadDictionaryData(corePath, parts = SIDECARS) {
  const data = JSON.parse(fs.readFileSync(corePath, 'utf8'));
  for (const part of parts) {
    if (part in data) continue; // a combined file written before the split
    const file = sidecarPath(corePath, part);
    const sidecar = JSON.parse(fs.readFileSync(file, 'utf8'));
    if (sidecar.sourceSha256 !== data.sourceSha256) {
      throw new Error(`${path.basename(file)} was built from a different TSV than ${path.basename(corePath)}; rebuild it`);
    }
    data[part] = sidecar[part];
  }
  return data;
}

module.exports = { SIDECARS, sidecarPath, loadDictionaryData };

"""Paths and loader for the generated dictionary JSON and its two sidecars.

The build writes the complete dictionary document as three files so browsers
only download what they use:

- ``hokkien-hanri-dict.json``: entries, categories and metadata (published;
  every app loads it).
- ``hokkien-hanri-dict-runtime.json``: the audio and Lomari maps (published;
  only the IME and translator load it).
- ``hokkien-hanri-dict-indexes.json``: lookup indexes (build-only; checks read
  it, the site build never publishes it).

``load_dictionary_data`` reassembles the complete logical document, so checks
and baselines see exactly the same data as before the split.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

SIDECARS = ("runtime", "indexes")
PUBLISHED_SIDECARS = ("runtime",)


def sidecar_path(core_path: Path | str, part: str) -> Path:
    core_path = Path(core_path)
    return core_path.with_name(f"{core_path.stem}-{part}{core_path.suffix}")


def split_dictionary_data(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return the core document and one small document per sidecar."""
    stamp = {"schemaVersion": data["schemaVersion"], "sourceSha256": data["sourceSha256"]}
    files = {"core": {key: value for key, value in data.items() if key not in SIDECARS}}
    for part in SIDECARS:
        files[part] = {**stamp, part: data[part]}
    return files


def load_dictionary_data(core_path: Path | str, parts: Iterable[str] = SIDECARS) -> dict[str, Any]:
    """Load the core file and merge the requested sidecars into it."""
    core_path = Path(core_path)
    data = json.loads(core_path.read_text(encoding="utf-8"))
    for part in parts:
        if part in data:  # a combined file written before the split
            continue
        path = sidecar_path(core_path, part)
        sidecar = json.loads(path.read_text(encoding="utf-8"))
        if sidecar.get("sourceSha256") != data.get("sourceSha256"):
            raise ValueError(f"{path.name} was built from a different TSV than {core_path.name}; rebuild it")
        data[part] = sidecar[part]
    return data

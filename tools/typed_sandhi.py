"""Typed sandhi tone 4 for the editors (docs/sandhi-toggle-plan.md, step 7).

A Singapore speaker types tone 4 where Taipei has 1 on an open syllable that is joined to the next
one (정4래5 for 정1래5). Stored readings keep Taipei sandhi digits, so the editors read that typed 4 as
1. The rule itself lives in the pronunciation engine (desktop/tangliengim_engine.py); this module
loads the engine by path, once and only when it is needed, so the editors need no sys.path change.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ENGINE_PATH = Path(__file__).resolve().parents[1] / "desktop" / "tangliengim_engine.py"
_engine = None


def typed_sandhi_to_taipei(text: str) -> str:
    """The text with every typed non-final open tone 4 read as tone 1; a digit stays a digit."""
    global _engine
    if _engine is None:
        spec = importlib.util.spec_from_file_location("tangliengim_engine_for_typed_sandhi", ENGINE_PATH)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load the pronunciation engine from {ENGINE_PATH}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _engine = module
    return _engine.typed_sandhi_to_taipei(text)

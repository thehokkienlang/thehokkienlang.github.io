"""Double-click launcher for the private Tangliengim editor hub."""

from pathlib import Path

from tangliengim_web_shell import run_desktop_shell


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    run_desktop_shell(
        repository,
        repository / "desktop" / "Hokkien Tangliengim IME Pad.py",
        editor=True,
        start_path="/editors/",
    )

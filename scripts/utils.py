#!/usr/bin/env python3
import datetime
import pathlib


def today():
    """Return (DATE, DAY_NAME, DAY_NUMBER) for today."""
    d = datetime.date.today()
    return d.isoformat(), d.strftime("%A, %B %d %Y"), d.timetuple().tm_yday


def setup_dir(path: str) -> pathlib.Path:
    """Create directory and return as pathlib.Path."""
    p = pathlib.Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def extract_field(raw: str, tag: str, default: str = "") -> str:
    """Extract a tagged single-line field from LLM output.

    Handles whitespace variations and case differences so fragile
    startswith() checks don't silently fall back to the default.
    """
    prefix = tag.lower().rstrip(":") + ":"
    for line in raw.split("\n"):
        stripped = line.strip()
        if stripped.lower().startswith(prefix):
            value = stripped[len(prefix):].strip()
            if value:
                return value
    return default


def write_tmp(filename: str, content: str) -> None:
    """Write to /tmp safely; ignores errors so the main script doesn't fail."""
    try:
        pathlib.Path(f"/tmp/{filename}").write_text(content, encoding="utf-8")
    except OSError:
        pass

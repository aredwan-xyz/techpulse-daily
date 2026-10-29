#!/usr/bin/env python3
"""Generate in isolation; copy validated output only after the full issue succeeds.

GitHub publishes the resulting paths together in one commit. An exception exits
nonzero before the commit step, leaving the previous remote issue untouched.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from ai_client import check_configuration
from update_index import FEEDS, archive_path, publish_issue, validate_issue
from utils import today


def run_daily(root, date, run=subprocess.run):
    root = root.resolve()
    # A completed date is immutable on rerun: no paid calls or duplicate output.
    status_path = root / "STATUS.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        if status.get("status") == "complete" and status.get("published_date") == date:
            validate_issue(root, date)
            if "**Feeds:** 9/9 published" not in (root / archive_path(date)).read_text(encoding="utf-8"):
                raise ValueError("Completed status has no complete archive")
            print(f"{date} already published; no changes")
            return False
    check_configuration()
    with tempfile.TemporaryDirectory(prefix="techpulse-") as temp:
        stage = Path(temp)
        for name in ("feeds", "archive", "assets"):
            if (root / name).exists():
                shutil.copytree(root / name, stage / name)
        shutil.copy2(root / "README.md", stage / "README.md")
        # Existing same-date partial outputs may not satisfy this generation.
        for feed in FEEDS:
            (stage / f"feeds/{feed}/{date}.md").unlink(missing_ok=True)
        env = dict(os.environ, TECHPULSE_DATE=date)
        for _, _, script in FEEDS.values():
            run([sys.executable, str(root / "scripts" / script)],
                cwd=stage, env=env, check=True, timeout=600)
        publish_issue(stage, date)
        paths = [f"feeds/{feed}/{date}.md" for feed in FEEDS]
        paths += [archive_path(date).as_posix(), "INDEX.md", "STATS.md", "README.md", "STATUS.json"]
        for relative in paths:
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(stage / relative, destination)
    return True


if __name__ == "__main__":
    try:
        run_daily(Path(__file__).resolve().parents[1], today()[0])
    except Exception as error:
        print(f"Daily issue not published: {error}", file=sys.stderr)
        sys.exit(1)

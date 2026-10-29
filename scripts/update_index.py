#!/usr/bin/env python3
"""Build navigation only from validated complete issues. No import-time writes."""

import datetime
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

from utils import today

FEEDS = {
    "news": ("📰", "Tech News Digest", "fetch_news.py"),
    "trending": ("🔥", "GitHub Repository Snapshot", "fetch_trending.py"),
    "research": ("🤖", "AI Research", "fetch_arxiv.py"),
    "challenges": ("💡", "Coding Challenge", "generate_challenge.py"),
    "tools": ("🛠️", "Tool Spotlight", "generate_tool.py"),
    "prompts": ("🎯", "Prompt of the Day", "generate_prompt.py"),
    "security": ("🔐", "Security Pulse", "fetch_security.py"),
    "market": ("📊", "Hiring Thread Notes", "fetch_market.py"),
    "learning": ("📚", "Learning Pick", "generate_learning.py"),
}


def archive_path(date):
    day = datetime.date.fromisoformat(date)
    return Path(f"archive/{day:%Y/%m}/{date}.md")


def body(content):
    sections = content.split("\n---\n", 1)
    content = sections[-1]
    return content.split("*← [Back to Index]", 1)[0].strip()


def validate_feed(path, date, feed):
    text = path.read_text(encoding="utf-8")
    label = datetime.date.fromisoformat(date).strftime("%A, %B %d %Y")
    if not text.startswith("# ") or (label not in text and date not in text):
        raise ValueError(f"{path}: missing heading or matching publication date")
    content = body(text)
    if len(content.strip()) < 120:
        raise ValueError(f"{path}: empty or insufficient body")
    required = {
        "challenges": ("PROBLEM:", "SOLUTION_PYTHON:", "SOLUTION_JS:"),
        "prompts": ("THE_PROMPT:", "WHEN_TO_USE:"),
        "learning": ("RESOURCE_TITLE:", "RESOURCE_URL:", "WHAT_YOULL_LEARN:"),
    }
    if any(field not in content for field in required.get(feed, ())):
        raise ValueError(f"{path}: missing required generated fields")
    if re.search(r"not yet published|could not read feed|api unavailable|TODO|lorem ipsum", text, re.I):
        raise ValueError(f"{path}: placeholder or unavailable source")
    if re.search(r"<(?:script|iframe|object|embed)\b|javascript:", text, re.I):
        raise ValueError(f"{path}: unsafe markup")
    fences = re.findall(r"^\s*(```+|~~~+)", text, re.M)
    if len(fences) % 2:
        raise ValueError(f"{path}: unterminated code fence")
    if feed not in ("challenges", "prompts"):
        urls = re.findall(r"https?://[^\s<>\]\)]+", content)
        sources = [url for url in urls if urlsplit(url).hostname
                   and not url.startswith("https://github.com/aredwan-xyz/")
                   and urlsplit(url).hostname not in ("img.shields.io", "localhost", "127.0.0.1")]
        if not sources:
            raise ValueError(f"{path}: missing external source URL")
    return text


def validate_issue(root, date):
    return {feed: validate_feed(root / f"feeds/{feed}/{date}.md", date, feed)
            for feed in FEEDS}


def complete_dates(root):
    # A legacy placeholder archive is not a completed publication.
    dates = []
    for path in sorted((root / "archive").glob("*/*/*.md"), reverse=True):
        try:
            if "**Feeds:** 9/9 published" not in path.read_text(encoding="utf-8"):
                continue
            validate_issue(root, path.stem)
        except (ValueError, OSError):
            continue
        dates.append(path.stem)
    return dates


def _rebase_links(content, feed):
    def replace(match):
        url = match.group(1)
        if urlsplit(url).scheme or url.startswith(("#", "//")):
            return match.group(0)
        target = os.path.normpath(os.path.join("feeds", feed, url))
        return "](" + os.path.relpath(target, "archive/2000/01") + ")"
    return re.sub(r"\]\(([^\s)]+)\)", replace, content)


def build_daily_archive(root, date, feeds):
    day = datetime.date.fromisoformat(date)
    sections = [f"## {FEEDS[feed][0]} {FEEDS[feed][1]}\n\n{_rebase_links(body(text), feed)}"
                for feed, text in feeds.items()]
    path = root / archive_path(date)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = (f"# TechPulse Daily Digest — {day:%A, %B %d %Y}\n\n"
            f"**Date:** {date}\n**Feeds:** 9/9 published\n\n"
            "> AI-assisted summaries and generated exercises; verify facts with linked sources.\n\n---\n\n"
            + "\n\n---\n\n".join(sections)
            + "\n\n---\n\n[Back to Index](../../../INDEX.md) · [Raw feeds](../../../feeds/)\n")
    path.write_text(text, encoding="utf-8")


def rebuild_navigation(root):
    dates = complete_dates(root)
    latest = dates[0] if dates else None
    status = f"Last successful complete digest: **{latest}**" if latest else "No complete digest has passed validation."
    table = "| Feed | Latest complete issue |\n|---|---|\n"
    for feed, (emoji, title, _) in FEEDS.items():
        link = f"[Read](feeds/{feed}/{latest}.md)" if latest else "Not available"
        table += f"| {emoji} {title} | {link} |\n"
    issues = "\n".join(f"- [{date}]({archive_path(date).as_posix()})" for date in dates[:30])
    (root / "INDEX.md").write_text(
        f"# TechPulse — Complete Issues\n\n{status}\n\n{table}\n"
        f"## Recent complete issues\n\n{issues or 'None yet.'}\n\n"
        "Historical files remain in [archive](archive/) and may be incomplete.\n\n[README](README.md)\n",
        encoding="utf-8",
    )
    counts = {feed: len(list((root / f"feeds/{feed}").glob("????-??-??.md"))) for feed in FEEDS}
    (root / "STATS.md").write_text(
        "# TechPulse — Content inventory\n\n" + status + "\n\n"
        + f"Complete validated issues: {len(dates)}\n\n"
        + "| Feed | Stored files (includes unvalidated legacy content) |\n|---|---:|\n"
        + "".join(f"| {FEEDS[f][1]} | {n} |\n" for f, n in counts.items())
        + "\nThese are file counts, not commits, users, or publication-success metrics.\n",
        encoding="utf-8",
    )
    readme = root / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        section = f"<!-- AUTO-UPDATED DAILY — DO NOT EDIT MANUALLY -->\n{status}\n\n{table}\n"
        text, count = re.subn(
            r"<!-- AUTO-UPDATED DAILY — DO NOT EDIT MANUALLY -->.*?(?=\n---)",
            lambda _: section, text, flags=re.S,
        )
        if count != 1:
            raise ValueError("README publication marker missing or duplicated")
        readme.write_text(text, encoding="utf-8")


def publish_issue(root, date):
    feeds = validate_issue(root, date)
    build_daily_archive(root, date, feeds)
    rebuild_navigation(root)
    (root / "STATUS.json").write_text(json.dumps({
        "status": "complete", "published_date": date,
        "feeds_published": len(feeds), "feeds_expected": len(FEEDS),
        "archive": archive_path(date).as_posix(),
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    # Navigation repair is safe even when today's generators have failed.
    rebuild_navigation(Path.cwd())

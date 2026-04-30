#!/usr/bin/env python3
"""
update_index.py
Compiles all today's feeds into a single daily archive file,
updates the master INDEX.md, and updates STATS.md.
"""

import datetime
import pathlib
import glob

DATE = datetime.date.today().isoformat()
DAY_NAME = datetime.date.today().strftime("%A, %B %d %Y")
YEAR = datetime.date.today().strftime("%Y")
MONTH = datetime.date.today().strftime("%m")

ARCHIVE_DIR = pathlib.Path(f"archive/{YEAR}/{MONTH}")
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_FILE = ARCHIVE_DIR / f"{DATE}.md"

FEEDS = {
    "news":       ("📰", "Tech News Digest", "feeds/news"),
    "trending":   ("🔥", "GitHub Trending",  "feeds/trending"),
    "research":   ("🤖", "AI Research",       "feeds/research"),
    "challenges": ("💡", "Coding Challenge",  "feeds/challenges"),
    "tools":      ("🛠️",  "Tool Spotlight",    "feeds/tools"),
    "prompts":    ("🎯", "Prompt of the Day", "feeds/prompts"),
    "security":   ("🔐", "Security Pulse",    "feeds/security"),
    "market":     ("📊", "Market Pulse",      "feeds/market"),
    "learning":   ("📚", "Learning Pick",     "feeds/learning"),
}


def _extract_body(content: str) -> str:
    """Strip the file header (everything up to and including the first ---) and footer nav."""
    lines = content.split("\n")
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip() == "---":
            body_start = i + 1
            break

    body_lines = []
    for line in lines[body_start:]:
        if "← [Back to Index]" in line:
            break
        body_lines.append(line)

    # Trim trailing blank lines
    while body_lines and not body_lines[-1].strip():
        body_lines.pop()

    return "\n".join(body_lines)


def build_daily_archive():
    """Compile today's content into one archive file."""
    sections = []

    for key, (emoji, title, feed_dir) in FEEDS.items():
        feed_file = pathlib.Path(feed_dir) / f"{DATE}.md"
        if feed_file.exists():
            try:
                content = feed_file.read_text(encoding="utf-8")
                body = _extract_body(content)
                sections.append(f"## {emoji} {title}\n\n{body}")
            except OSError as e:
                print(f"⚠️  Could not read {feed_file}: {e}")
                sections.append(f"## {emoji} {title}\n\n*Could not read feed file.*")
        else:
            sections.append(f"## {emoji} {title}\n\n*Not yet published today.*")

    separator = "\n\n---\n\n"
    sections_body = separator.join(sections)
    published_count = sum(1 for s in sections if "Not yet published" not in s and "Could not read" not in s)

    archive_content = (
        f"# 🗓️ DevPulse Daily Archive — {DAY_NAME}\n\n"
        f"> *Complete daily digest · [DevPulse](https://github.com/aredwan-xyz/devpulse-daily)*\n\n"
        f"**Date:** {DATE}\n"
        f"**Feeds:** {published_count}/9 published\n\n"
        f"---\n\n"
        f"{sections_body}\n\n"
        f"---\n\n"
        f"*[← Back to Index](../../INDEX.md) · [View Raw Feeds](../../feeds/) · [Full Archive](../)*\n"
    )
    ARCHIVE_FILE.write_text(archive_content, encoding="utf-8")
    print(f"✅ Daily archive written: {ARCHIVE_FILE}")


def count_files_in_feed(feed_dir: str) -> int:
    """Count published markdown files in a feed directory."""
    files = glob.glob(f"{feed_dir}/*.md")
    return len([f for f in files if "README" not in f])


def _build_archive_table() -> tuple[str, int]:
    """Scan the archive directory and return (markdown_table, total_count)."""
    archive_base = pathlib.Path("archive")
    rows = []
    total = 0

    if archive_base.exists():
        for year_dir in sorted(archive_base.iterdir()):
            if not year_dir.is_dir():
                continue
            for month_dir in sorted(year_dir.iterdir()):
                if not month_dir.is_dir():
                    continue
                count = count_files_in_feed(str(month_dir))
                total += count
                try:
                    month_name = datetime.datetime.strptime(month_dir.name, "%m").strftime("%B")
                except ValueError:
                    month_name = month_dir.name
                rows.append(
                    f"| {year_dir.name} | [{month_name}]({month_dir}/) | {count} issues |"
                )

    table = "\n".join(rows) if rows else "| — | — | — |"
    return table, total


def _get_days_active() -> int:
    """Derive days active from the oldest archive file instead of a hardcoded date."""
    all_archives = sorted(glob.glob("archive/**/*.md", recursive=True))
    for path in all_archives:
        stem = pathlib.Path(path).stem
        try:
            start = datetime.datetime.strptime(stem, "%Y-%m-%d")
            return max(1, (datetime.datetime.now() - start).days + 1)
        except ValueError:
            continue
    return 1


def update_index():
    """Update the master INDEX.md with all published dates."""
    archive_files = sorted(
        glob.glob("archive/**/*.md", recursive=True),
        reverse=True
    )

    recent_dates = []
    for af in archive_files[:30]:  # Last 30 days
        date_str = pathlib.Path(af).stem
        try:
            d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            recent_dates.append((date_str, d.strftime("%A, %b %d"), af))
        except ValueError:
            continue

    recent_table = "\n".join([
        f"| [{date_str}]({af}) | {day_name} | [📰]("
        f"feeds/news/{date_str}.md) [🔥](feeds/trending/{date_str}.md) "
        f"[🤖](feeds/research/{date_str}.md) [💡](feeds/challenges/{date_str}.md) "
        f"[🛠️](feeds/tools/{date_str}.md) [🎯](feeds/prompts/{date_str}.md) "
        f"[🔐](feeds/security/{date_str}.md) [📊](feeds/market/{date_str}.md) "
        f"[📚](feeds/learning/{date_str}.md) |"
        for date_str, day_name, af in recent_dates
    ]) or "| No entries yet | — | — |"

    archive_table, _ = _build_archive_table()

    index_content = f"""# 🗂️ DevPulse Daily — Master Index

> *Auto-updated daily · [Back to README](README.md)*

**Last updated:** {DATE}

---

## 📅 Recent Issues (Last 30 Days)

| Date | Day | Feeds |
|---|---|---|
{recent_table}

---

## 📁 Browse by Feed

| Feed | Latest | Archive |
|---|---|---|
| 📰 Tech News | [Today](feeds/news/{DATE}.md) | [All Issues](feeds/news/) |
| 🔥 GitHub Trending | [Today](feeds/trending/{DATE}.md) | [All Issues](feeds/trending/) |
| 🤖 AI Research | [Today](feeds/research/{DATE}.md) | [All Issues](feeds/research/) |
| 💡 Coding Challenges | [Today](feeds/challenges/{DATE}.md) | [All Issues](feeds/challenges/) |
| 🛠️ Tool Spotlights | [Today](feeds/tools/{DATE}.md) | [All Issues](feeds/tools/) |
| 🎯 Prompts | [Today](feeds/prompts/{DATE}.md) | [All Issues](feeds/prompts/) |
| 🔐 Security | [Today](feeds/security/{DATE}.md) | [All Issues](feeds/security/) |
| 📊 Market Pulse | [Today](feeds/market/{DATE}.md) | [All Issues](feeds/market/) |
| 📚 Learning | [Today](feeds/learning/{DATE}.md) | [All Issues](feeds/learning/) |

---

## 📂 Full Archive

| Year | Month | Issues |
|---|---|---|
{archive_table}

---

*← [Back to README](README.md)*
"""
    pathlib.Path("INDEX.md").write_text(index_content, encoding="utf-8")
    print("✅ INDEX.md updated")


def update_stats():
    """Update STATS.md with current repo statistics."""
    total_news = count_files_in_feed("feeds/news")
    total_trending = count_files_in_feed("feeds/trending")
    total_research = count_files_in_feed("feeds/research")
    total_challenges = count_files_in_feed("feeds/challenges")
    total_tools = count_files_in_feed("feeds/tools")
    total_prompts = count_files_in_feed("feeds/prompts")
    total_security = count_files_in_feed("feeds/security")
    total_market = count_files_in_feed("feeds/market")
    total_learning = count_files_in_feed("feeds/learning")

    _, total_archives = _build_archive_table()

    total_commits = (
        total_news + total_trending + total_research + total_challenges +
        total_tools + total_prompts + total_security + total_market +
        total_learning + total_archives
    )

    days_active = _get_days_active()

    stats_content = f"""# 📈 DevPulse Daily — Stats

> *Auto-updated with every daily index run*

**Last updated:** {DATE}

---

## 🔢 Totals

| Metric | Count |
|---|---|
| 📅 Days active | {days_active} |
| 📝 Total commits (content) | ~{total_commits * 10} |
| 📰 News digests | {total_news} |
| 🔥 Trending snapshots | {total_trending} |
| 🤖 Research papers summarized | {total_research} |
| 💡 Coding challenges | {total_challenges} |
| 🛠️ Tool spotlights | {total_tools} |
| 🎯 Prompts published | {total_prompts} |
| 🔐 Security bulletins | {total_security} |
| 📊 Market pulses | {total_market} |
| 📚 Learning picks | {total_learning} |
| 🗓️ Daily archives | {total_archives} |

---

## 📊 Milestones

- [ ] Day 1: First digest published
- [ ] Day 7: One full week
- [ ] Day 30: First month
- [ ] 100 papers summarized
- [ ] 100 challenges published
- [ ] 500 prompts curated
- [ ] 1,000 GitHub stars
- [ ] 365 days: One full year

---

*← [Back to README](README.md) · [Master Index](INDEX.md)*
"""
    pathlib.Path("STATS.md").write_text(stats_content, encoding="utf-8")
    print("✅ STATS.md updated")


if __name__ == "__main__":
    print("🗓️ Building daily archive...")
    build_daily_archive()

    print("📋 Updating master index...")
    update_index()

    print("📈 Updating stats...")
    update_stats()

    print("✅ All done!")

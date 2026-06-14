#!/usr/bin/env python3
"""
fetch_news.py
Fetches top AI & dev tech news from HackerNews API + NewsAPI,
then uses Claude to generate a curated digest.
"""

import sys
import json
import pathlib
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ai_client import generate
from utils import today, setup_dir

DATE, DAY_NAME, DAY_NUMBER = today()
OUTPUT_DIR = setup_dir("feeds/news")
OUTPUT_FILE = OUTPUT_DIR / f"{DATE}.md"


def fetch_hackernews_top(n: int = 20) -> list[dict]:
    """Fetch top stories from Hacker News API."""
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    with urllib.request.urlopen(url, timeout=15) as r:
        story_ids = json.loads(r.read())[:n]

    stories = []
    skipped = 0
    for sid in story_ids:
        try:
            with urllib.request.urlopen(
                f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=10
            ) as r:
                story = json.loads(r.read())
                if story and story.get("type") == "story":
                    stories.append({
                        "title": story.get("title", ""),
                        "url": story.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                        "score": story.get("score", 0),
                        "comments": story.get("descendants", 0),
                    })
        except Exception as e:
            skipped += 1
            print(f"   Skipped story {sid}: {e}")

    if skipped:
        print(f"   Skipped {skipped}/{n} stories due to fetch errors")

    return sorted(stories, key=lambda x: x["score"], reverse=True)[:10]


def generate_digest(stories: list[dict]) -> str:
    """Generate a curated digest using the configured free AI provider."""
    stories_text = "\n".join([
        f"- [{s['title']}]({s['url']}) — {s['score']} points, {s['comments']} comments"
        for s in stories
    ])

    return generate(
        system="""You are a tech editor writing a daily digest for software engineers and AI builders.
        Write in a direct, insightful voice. No fluff. Pick the 5 most important stories and explain
        WHY each one matters — not just what it is. Focus on AI, software engineering, and developer tools.

        Format each story as:
        ### [Emoji] [Story Title](URL)
        > **Why it matters:** [2-3 sentences on the real significance]

        End with a 1-sentence "Editor's Take" on the day's theme.""",
        user=f"Today is {DAY_NAME}. Here are the top HackerNews stories:\n\n{stories_text}\n\nGenerate today's digest.",
        max_tokens=1500,
    )


def write_file(digest: str, stories: list[dict]):
    content = f"""# 📰 Tech News Digest — {DAY_NAME}

> *Curated daily by [TechPulse Daily Digest](https://github.com/aredwan-xyz/devpulse-daily) · Powered by AI*

---

{digest}

---

## 🔗 All Stories Today

| Title | Score | Comments |
|---|---|---|
{chr(10).join([f"| [{s['title']}]({s['url']}) | ⬆ {s['score']} | 💬 {s['comments']} |" for s in stories])}

---

*← [Back to Index](../../INDEX.md) · [Yesterday's News](.) · [Full Archive](../../archive/)*
"""
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"✅ News digest written: {OUTPUT_FILE}")


if __name__ == "__main__":
    print("📰 Fetching tech news...")
    stories = fetch_hackernews_top(20)
    print(f"   Found {len(stories)} stories")

    print("🤖 Generating digest...")
    digest = generate_digest(stories)

    write_file(digest, stories)
    print("✅ Done!")

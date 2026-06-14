#!/usr/bin/env python3
"""
fetch_trending.py
Scrapes GitHub trending page and archives today's hot repos with AI summaries.
"""

import sys
import json
import pathlib
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ai_client import generate
from utils import today, setup_dir

DATE, DAY_NAME, DAY_NUMBER = today()
OUTPUT_DIR = setup_dir("feeds/trending")
OUTPUT_FILE = OUTPUT_DIR / f"{DATE}.md"


def fetch_trending_repos(language: str = "", since: str = "daily") -> list[dict]:
    """
    Fetch trending repos via the unofficial GitHub trending API.
    Falls back to GitHub search API if unavailable.
    """
    try:
        url = f"https://gh-trending-api.herokuapp.com/repositories?language={language}&since={since}"
        req = urllib.request.Request(url, headers={"User-Agent": "TechPulse-Bot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            repos = json.loads(r.read())[:10]
            return [
                {
                    "name": repo.get("name", ""),
                    "author": repo.get("author", ""),
                    "url": repo.get("url", ""),
                    "description": repo.get("description", "") or "No description",
                    "language": repo.get("language", "") or "Unknown",
                    "stars": repo.get("stars", 0),
                    "stars_today": repo.get("currentPeriodStars", 0),
                    "forks": repo.get("forks", 0),
                }
                for repo in repos
            ]
    except Exception as e:
        print(f"   Primary trending API unavailable ({e}), falling back to GitHub Search API...")

    # Fallback: GitHub Search API — last 30 days of activity
    import datetime
    cutoff = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    url = f"https://api.github.com/search/repositories?q=created:>{cutoff}&sort=stars&order=desc&per_page=10"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "TechPulse-Bot/1.0",
            "Accept": "application/vnd.github.v3+json",
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())

    return [
        {
            "name": repo["name"],
            "author": repo["owner"]["login"],
            "url": repo["html_url"],
            "description": repo.get("description", "") or "No description",
            "language": repo.get("language", "") or "Unknown",
            "stars": repo["stargazers_count"],
            "stars_today": 0,
            "forks": repo["forks_count"],
        }
        for repo in data.get("items", [])[:10]
    ]


def generate_insights(repos: list[dict]) -> str:
    """Generate insights on today's trending repos."""
    repos_text = "\n".join([
        f"- {r['author']}/{r['name']} ({r['language']}, ⭐{r['stars']:,}): {r['description']}"
        for r in repos
    ])

    return generate(
        system="""You are a developer trends analyst. Look at today's trending GitHub repos and:
        1. Identify the dominant theme/pattern (1 sentence)
        2. Call out the single most interesting project and why (2 sentences)
        3. Give a 1-sentence forward-looking observation about what this suggests

        Be sharp, opinionated, and specific. No generic observations.""",
        user=f"Today's trending GitHub repos ({DATE}):\n{repos_text}\n\nGive your analyst take.",
        max_tokens=600,
    )


def write_file(repos: list[dict], insights: str):
    def desc_cell(description: str) -> str:
        if len(description) > 60:
            return description[:57] + "..."
        return description

    table_rows = "\n".join([
        f"| [{r['author']}/{r['name']}]({r['url']}) | {r['language']} | "
        f"⭐ {r['stars']:,} | +{r['stars_today']:,} today | {desc_cell(r['description'])} |"
        for r in repos
    ])

    content = f"""# 🔥 GitHub Trending — {DAY_NAME}

> *Daily snapshot by [TechPulse Daily Digest](https://github.com/aredwan-xyz/devpulse-daily)*

## 🧠 Analyst Take

{insights}

---

## 📊 Today's Top 10

| Repository | Language | Total Stars | Today | Description |
|---|---|---|---|---|
{table_rows}

---

## 🗂️ Quick Links

{chr(10).join([f"- [{r['author']}/{r['name']}]({r['url']}) — {r['description'][:80]}" for r in repos])}

---

*← [Back to Index](../../INDEX.md) · [Full Trending Archive](.) · [Compare Yesterday](.)*
"""
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"✅ Trending snapshot written: {OUTPUT_FILE}")


if __name__ == "__main__":
    print("🔥 Fetching GitHub trending repos...")
    repos = fetch_trending_repos()
    print(f"   Found {len(repos)} trending repos")

    print("🤖 Generating insights...")
    insights = generate_insights(repos)

    write_file(repos, insights)
    print("✅ Done!")

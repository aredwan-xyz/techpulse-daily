#!/usr/bin/env python3
"""
fetch_market.py
Generates a market & jobs pulse using Claude's knowledge of the tech job market,
supplemented by HackerNews "Who's Hiring" data when available.
"""

import sys
import json
import pathlib
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ai_client import generate
from utils import today, setup_dir

DATE, DAY_NAME, DAY_NUMBER = today()
MONTH_NAME = __import__("datetime").date.today().strftime("%B %Y")
OUTPUT_DIR = setup_dir("feeds/market")
OUTPUT_FILE = OUTPUT_DIR / f"{DATE}.md"


def fetch_hn_hiring_snippet() -> str:
    """Try to get a snippet from HN 'Who is Hiring' thread."""
    url = "https://hn.algolia.com/api/v1/search?query=Ask+HN+Who+is+Hiring&tags=story&hitsPerPage=3"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DevPulse-Bot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        hits = data.get("hits", [])
        if hits:
            return f"Latest HN thread: {hits[0].get('title', '')} ({hits[0].get('url', '')})"
    except Exception as e:
        print(f"   HN Algolia API unavailable: {e}")
    return ""


def generate_market_pulse(hn_context: str) -> str:
    """Generate market intelligence using Gemini."""
    return generate(
        system=f"""You are a tech job market analyst writing a daily market pulse for developers.
        Today is {DAY_NAME}.

        Generate an insightful market pulse covering:

        ## 🔥 Hottest Skills Right Now
        [Top 5 most in-demand skills in AI/dev job market with brief context]

        ## 💰 Salary Signals
        [3 data points on current compensation trends for AI/ML/Full-stack roles]

        ## 🚀 Roles in High Demand
        [Top 3 specific job titles with the most open positions and why]

        ## 📉 What's Cooling Off
        [1-2 skills or roles losing steam — be honest]

        ## 🌍 Remote Landscape
        [Current state of remote work in tech — any changes?]

        ## 💡 Career Move of the Week
        [One specific, actionable career tip for developers right now]

        ## 📊 Quick Stats
        | Metric | Signal |
        |---|---|
        | AI Engineering roles | 📈 High demand |
        | [Other role] | [Signal] |
        | [Other metric] | [Signal] |

        Be specific with numbers and trends where possible. Avoid generic statements.""",
        user=f"Generate the market pulse for {DATE}. Context: {hn_context or 'Standard weekday'}",
        max_tokens=1500,
    )


def generate_learning_pick() -> str:
    """Generate a curated learning resource pick using Gemini."""
    resource_types = [
        "a free online course or tutorial",
        "a must-read technical blog post or article",
        "a YouTube talk or conference presentation",
        "a GitHub repo to study for learning",
        "a book (free or paid) worth reading",
        "an interactive playground or tool to practice",
        "a podcast episode worth listening to",
    ]
    resource_type = resource_types[DAY_NUMBER % len(resource_types)]

    return generate(
        system=f"""You are a developer educator recommending {resource_type} for today.

        Format:
        **Resource:** [Title and URL if known]
        **Why today:** [Why this is worth your time right now — 2 sentences]
        **What you'll learn:** [3 bullet points of concrete takeaways]
        **Time investment:** [Realistic estimate]
        **Best for:** [Who gets the most value]""",
        user=f"Recommend {resource_type} for {DATE} in the AI/dev space.",
        max_tokens=600,
    )


def write_file(market_pulse: str, learning_pick: str):
    content = f"""# 📊 Market Pulse — {DAY_NAME}

> *Daily market intelligence by [DevPulse](https://github.com/aredwan-xyz/devpulse-daily)*

---

{market_pulse}

---

## 📚 Today's Learning Pick

{learning_pick}

---

## 🔗 Job Search Resources

- [HN Who's Hiring](https://news.ycombinator.com/jobs) — Best tech jobs, no recruiter spam
- [Wellfound (AngelList)](https://wellfound.com/jobs) — Startup roles
- [Remote OK](https://remoteok.com/) — Remote-first positions
- [Levels.fyi](https://levels.fyi/) — Salary transparency
- [LinkedIn AI Jobs](https://linkedin.com/jobs) — Filter by AI/ML

---

*← [Back to Index](../../INDEX.md) · [All Market Pulses](.) · [Yesterday](.)*
"""
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"✅ Market pulse written: {OUTPUT_FILE}")


if __name__ == "__main__":
    print("📊 Fetching HN hiring context...")
    hn_context = fetch_hn_hiring_snippet()

    print("🤖 Generating market pulse with Claude...")
    market_pulse = generate_market_pulse(hn_context)

    print("📚 Generating learning pick...")
    learning_pick = generate_learning_pick()

    write_file(market_pulse, learning_pick)
    print("✅ Done!")

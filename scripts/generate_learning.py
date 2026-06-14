#!/usr/bin/env python3
"""
generate_learning.py
Generates a curated daily learning pick — rotating through
courses, talks, articles, repos, books, and interactive tools.
"""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ai_client import generate
from utils import today, setup_dir, extract_field

DATE, DAY_NAME, DAY_NUMBER = today()
OUTPUT_DIR = setup_dir("feeds/learning")
OUTPUT_FILE = OUTPUT_DIR / f"{DATE}.md"

RESOURCE_TYPES = [
    ("Free Course", "🎓", "a free online course with certificate"),
    ("Deep-Dive Article", "📖", "a long-form technical article or blog post"),
    ("Conference Talk", "🎤", "a recorded conference talk or keynote"),
    ("GitHub Repo to Study", "💻", "an open-source repo worth cloning and reading"),
    ("Book", "📚", "a technical book worth reading"),
    ("Interactive Tool", "🎮", "an interactive playground or hands-on learning tool"),
    ("Podcast Episode", "🎙️", "a podcast episode worth listening to"),
]

RTYPE_NAME, RTYPE_EMOJI, RTYPE_DESC = RESOURCE_TYPES[DAY_NUMBER % len(RESOURCE_TYPES)]

TOPIC_ROTATION = [
    "Multi-agent AI systems",
    "System design at scale",
    "LLM fine-tuning and RLHF",
    "RAG (Retrieval Augmented Generation)",
    "Rust for systems programming",
    "TypeScript advanced patterns",
    "Database internals",
    "Distributed systems",
    "AI-native UX design",
    "DevOps and platform engineering",
    "Security engineering",
    "Data engineering with DuckDB/Polars",
    "WebAssembly",
    "Edge computing",
]

TOPIC = TOPIC_ROTATION[DAY_NUMBER % len(TOPIC_ROTATION)]


def generate_learning_pick() -> dict:
    """Generate a curated learning pick using Gemini."""
    raw = generate(
        system=f"""You are a developer educator recommending the best {RTYPE_DESC} on the topic of {TOPIC}.

        Today: {DAY_NAME}

        Format EXACTLY as:

        RESOURCE_TITLE: [Title of the resource]
        RESOURCE_URL: [URL — use a real, well-known resource]
        RESOURCE_SOURCE: [Platform/Publisher]

        WHY_NOW:
        [Why this is particularly relevant RIGHT NOW — 2 sentences]

        WHAT_YOULL_LEARN:
        - [Specific skill or concept 1]
        - [Specific skill or concept 2]
        - [Specific skill or concept 3]
        - [Specific skill or concept 4]

        WHO_ITS_FOR:
        [2 sentences on who gets the most value from this]

        TIME_INVESTMENT: [Realistic time estimate]

        BEST_QUOTE_OR_HIGHLIGHT:
        [A key insight, quote, or the most valuable single takeaway from this resource]

        NEXT_STEP:
        [What to do immediately after finishing this resource]""",
        user=f"Recommend a {RTYPE_DESC} on {TOPIC} for {DATE}.",
        max_tokens=1500,
    )

    title = extract_field(raw, "RESOURCE_TITLE", default="Learning Pick")
    return {"raw": raw, "title": title}


def write_file(pick: dict):
    raw = pick["raw"]

    content = f"""# {RTYPE_EMOJI} Learning Pick — {DAY_NAME}

> *Daily learning curation by [TechPulse Daily Digest](https://github.com/aredwan-xyz/devpulse-daily)*

**Resource type:** {RTYPE_EMOJI} {RTYPE_NAME}
**Topic:** {TOPIC}
**Day #{DAY_NUMBER}**

---

{raw}

---

## 📅 Recent Learning Picks

Browse all picks in the [learning archive](.) — organized by type and topic.

| Type | Recent Pick |
|---|---|
| 🎓 Courses | [Browse](.) |
| 📖 Articles | [Browse](.) |
| 🎤 Talks | [Browse](.) |
| 💻 Repos | [Browse](.) |
| 📚 Books | [Browse](.) |

---

*← [Back to Index](../../INDEX.md) · [All Learning Picks](.) · [Yesterday's Pick](.)*
"""
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"✅ Learning pick written: {OUTPUT_FILE}")


if __name__ == "__main__":
    print(f"📚 Generating {RTYPE_NAME} pick on {TOPIC}...")
    pick = generate_learning_pick()
    write_file(pick)
    print("✅ Done!")

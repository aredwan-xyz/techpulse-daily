#!/usr/bin/env python3
"""
generate_tool.py
Curates a daily developer tool spotlight — rotating through
categories with Claude-generated write-ups and real examples.
"""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ai_client import generate
from utils import today, setup_dir, write_tmp

DATE, DAY_NAME, DAY_NUMBER = today()
OUTPUT_DIR = setup_dir("feeds/tools")
OUTPUT_FILE = OUTPUT_DIR / f"{DATE}.md"

# Curated list of tool categories to rotate through
TOOL_POOL = [
    # AI & LLM Tools
    {"name": "LiteLLM", "url": "https://github.com/BerriAI/litellm", "category": "AI/LLM", "emoji": "🤖"},
    {"name": "Instructor", "url": "https://github.com/jxnl/instructor", "category": "AI/LLM", "emoji": "🤖"},
    {"name": "DSPy", "url": "https://github.com/stanfordnlp/dspy", "category": "AI/LLM", "emoji": "🤖"},
    {"name": "Mirascope", "url": "https://github.com/Mirascope/mirascope", "category": "AI/LLM", "emoji": "🤖"},
    {"name": "Outlines", "url": "https://github.com/dottxt-ai/outlines", "category": "AI/LLM", "emoji": "🤖"},
    # Dev Productivity
    {"name": "Rye", "url": "https://github.com/astral-sh/rye", "category": "Dev Tools", "emoji": "🛠️"},
    {"name": "uv", "url": "https://github.com/astral-sh/uv", "category": "Dev Tools", "emoji": "🛠️"},
    {"name": "Ruff", "url": "https://github.com/astral-sh/ruff", "category": "Dev Tools", "emoji": "🛠️"},
    {"name": "Mise", "url": "https://github.com/jdx/mise", "category": "Dev Tools", "emoji": "🛠️"},
    {"name": "Just", "url": "https://github.com/casey/just", "category": "Dev Tools", "emoji": "🛠️"},
    # Databases & Storage
    {"name": "DuckDB", "url": "https://github.com/duckdb/duckdb", "category": "Databases", "emoji": "🗄️"},
    {"name": "Litestream", "url": "https://github.com/benbjohnson/litestream", "category": "Databases", "emoji": "🗄️"},
    {"name": "Drizzle ORM", "url": "https://github.com/drizzle-team/drizzle-orm", "category": "Databases", "emoji": "🗄️"},
    # Observability
    {"name": "OpenTelemetry", "url": "https://opentelemetry.io/", "category": "Observability", "emoji": "📊"},
    {"name": "Signoz", "url": "https://github.com/SigNoz/signoz", "category": "Observability", "emoji": "📊"},
    # API & Backend
    {"name": "Hono", "url": "https://github.com/honojs/hono", "category": "Backend", "emoji": "⚡"},
    {"name": "Encore", "url": "https://github.com/encoredev/encore", "category": "Backend", "emoji": "⚡"},
    {"name": "Loco", "url": "https://github.com/loco-rs/loco", "category": "Backend", "emoji": "⚡"},
    # Testing
    {"name": "Playwright", "url": "https://github.com/microsoft/playwright", "category": "Testing", "emoji": "🧪"},
    {"name": "Hypothesis", "url": "https://github.com/HypothesisWorks/hypothesis", "category": "Testing", "emoji": "🧪"},
    # CLI Tools
    {"name": "Atuin", "url": "https://github.com/atuinsh/atuin", "category": "CLI", "emoji": "💻"},
    {"name": "Zellij", "url": "https://github.com/zellij-org/zellij", "category": "CLI", "emoji": "💻"},
    {"name": "Starship", "url": "https://github.com/starship/starship", "category": "CLI", "emoji": "💻"},
]

tool = TOOL_POOL[DAY_NUMBER % len(TOOL_POOL)]


def generate_tool_spotlight(tool: dict) -> str:
    """Generate an engaging tool spotlight using Gemini."""
    return generate(
        system="""You are a developer advocate writing a daily tool spotlight.
        Write an engaging, honest write-up that helps developers decide if this tool is worth trying.

        Format EXACTLY as:

        ## What Is It?
        [1-2 sentence plain English description]

        ## The Problem It Solves
        [What were developers doing before this? What pain does it fix? 2-3 sentences]

        ## Why It's Worth 10 Minutes of Your Time
        [3 concrete reasons with specifics, no fluff]

        ## Quick Start
        ```bash
        [The fastest possible getting-started commands]
        ```

        ## Real-World Example
        [A short, realistic code snippet showing the core value]

        ## Who Should Use It
        ✅ Perfect for: [specific use cases]
        ⏩ Skip if: [when it's not the right fit]

        ## The Honest Take
        [1-2 sentences — what's great, what's not, bottom line]""",
        user=f"Write a spotlight for {tool['name']} ({tool['url']}) in category {tool['category']}.",
        max_tokens=1200,
    )


def write_file(tool: dict, spotlight: str):
    write_tmp("tool_name.txt", tool["name"])

    content = f"""# {tool['emoji']} Tool Spotlight — {DAY_NAME}

> *Daily tool discovery by [TechPulse Daily Digest](https://github.com/aredwan-xyz/devpulse-daily)*

---

# {tool['name']}

**Category:** {tool['category']}
**Link:** [{tool['url']}]({tool['url']})

[![Repo](https://img.shields.io/badge/View_on_GitHub-181717?style=flat-square&logo=github)](
{tool['url']})

---

{spotlight}

---

## 🗂️ Browse Tools by Category

| Category | Browse |
|---|---|
| 🤖 AI & LLM | [View all](.) |
| 🛠️ Dev Productivity | [View all](.) |
| 🗄️ Databases | [View all](.) |
| ⚡ Backend | [View all](.) |
| 🧪 Testing | [View all](.) |
| 💻 CLI | [View all](.) |

---

*← [Back to Index](../../INDEX.md) · [All Tools](.) · [Yesterday's Tool](.)*
"""
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"✅ Tool spotlight written: {OUTPUT_FILE}")


if __name__ == "__main__":
    print(f"🛠️ Generating spotlight for {tool['name']}...")
    spotlight = generate_tool_spotlight(tool)
    write_file(tool, spotlight)
    print("✅ Done!")

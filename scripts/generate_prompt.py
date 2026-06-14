#!/usr/bin/env python3
"""
generate_prompt.py
Generates a high-quality, battle-tested LLM prompt with
category rotation, use case, and live example output.
"""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ai_client import generate
from utils import today, setup_dir, extract_field

DATE, DAY_NAME, DAY_NUMBER = today()
OUTPUT_DIR = setup_dir("feeds/prompts")
OUTPUT_FILE = OUTPUT_DIR / f"{DATE}.md"

CATEGORIES = [
    ("Code Review", "🔍", "Get a senior engineer's code review"),
    ("System Design", "🏗️", "Design scalable systems with AI guidance"),
    ("Debugging", "🐛", "Diagnose and fix complex bugs"),
    ("Documentation", "📝", "Write clear technical documentation"),
    ("Data Analysis", "📊", "Extract insights from data with AI"),
    ("Email Writing", "✉️", "Write professional technical emails"),
    ("Technical Interviews", "💼", "Prep for technical interviews"),
    ("Architecture Decision", "⚖️", "Evaluate technical trade-offs"),
    ("Performance Optimization", "⚡", "Find and fix performance bottlenecks"),
    ("Security Audit", "🔐", "Audit code for security vulnerabilities"),
    ("API Design", "🔗", "Design clean, consistent APIs"),
    ("Refactoring", "♻️", "Refactor code for clarity and maintainability"),
    ("Test Writing", "🧪", "Generate comprehensive test suites"),
    ("Product Spec", "📋", "Write clear product requirements"),
]

CATEGORY_NAME, CATEGORY_EMOJI, CATEGORY_DESC = CATEGORIES[DAY_NUMBER % len(CATEGORIES)]


def generate_prompt_of_day() -> dict:
    """Generate a battle-tested prompt using Gemini."""
    raw = generate(
        system=f"""You are a prompt engineering expert. Create a powerful, reusable prompt for:

Category: {CATEGORY_NAME} {CATEGORY_EMOJI}
Use case: {CATEGORY_DESC}

Your output must follow this EXACT format:

PROMPT_TITLE: [Short punchy title]

THE_PROMPT:
[The actual prompt template. Use {{PLACEHOLDER}} for variables the user fills in.
Make it specific, structured, and reliably produce great output.
Should be 100-300 words.]

WHEN_TO_USE:
[2-3 sentences on the ideal use case]

EXAMPLE_INPUT:
[A realistic example of what a user would fill in for the placeholders]

EXAMPLE_OUTPUT_SUMMARY:
[What kind of output this prompt reliably produces — 2-3 sentences]

PRO_TIPS:
- [Tip 1 to get better results]
- [Tip 2]
- [Tip 3]

WORKS_WITH: Claude · GPT-4 · Gemini""",
        user=f"Create prompt #{DAY_NUMBER} for {DATE}. Make it immediately useful.",
        max_tokens=2000,
    )

    title = extract_field(raw, "PROMPT_TITLE", default=f"{CATEGORY_NAME} Prompt")
    return {"raw": raw, "title": title}


def write_file(prompt_data: dict):
    raw = prompt_data["raw"]

    content = f"""# 🎯 Prompt of the Day — {DAY_NAME}

> *Daily prompt by [TechPulse Daily Digest](https://github.com/aredwan-xyz/devpulse-daily)*

**Category:** {CATEGORY_EMOJI} {CATEGORY_NAME}
**Prompt #{DAY_NUMBER}**
**Works with:** Claude · GPT-4 · Gemini · All major LLMs

---

{raw}

---

## 📋 How to Use

1. Copy **THE_PROMPT** above
2. Replace all `{{PLACEHOLDER}}` variables with your specifics
3. Paste into any LLM chat interface
4. Iterate with follow-up questions

---

## 🗂️ Browse All Prompts by Category

| Category | Count |
|---|---|
| 🔍 Code Review | [Browse](.) |
| 🏗️ System Design | [Browse](.) |
| 🐛 Debugging | [Browse](.) |
| 📝 Documentation | [Browse](.) |
| ⚡ Performance | [Browse](.) |

---

*← [Back to Index](../../INDEX.md) · [All Prompts](.) · [Yesterday's Prompt](.)*
"""
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"✅ Prompt written: {OUTPUT_FILE}")


if __name__ == "__main__":
    print(f"🎯 Generating {CATEGORY_NAME} prompt...")
    prompt_data = generate_prompt_of_day()
    write_file(prompt_data)
    print("✅ Done!")

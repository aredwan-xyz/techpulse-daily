#!/usr/bin/env python3
"""
generate_challenge.py
Generates a fresh daily coding challenge using Claude,
with difficulty rotation and multi-language solutions.
"""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ai_client import generate
from utils import today, setup_dir, extract_field, write_tmp

DATE, DAY_NAME, DAY_NUMBER = today()
OUTPUT_DIR = setup_dir("feeds/challenges")
OUTPUT_FILE = OUTPUT_DIR / f"{DATE}.md"

# Rotate difficulty and topic categories
DIFFICULTIES = ["Easy", "Medium", "Medium", "Hard", "Medium", "Easy", "Hard"]
DIFFICULTY = DIFFICULTIES[DAY_NUMBER % len(DIFFICULTIES)]

TOPICS = [
    "Arrays & Strings",
    "Hash Maps & Sets",
    "Two Pointers",
    "Sliding Window",
    "Binary Search",
    "Linked Lists",
    "Trees & Graphs",
    "Dynamic Programming",
    "Recursion & Backtracking",
    "Sorting & Searching",
    "Stack & Queue",
    "Greedy Algorithms",
    "Bit Manipulation",
    "AI/ML Coding (NumPy/Pandas)",
]
TOPIC = TOPICS[DAY_NUMBER % len(TOPICS)]


def generate_challenge() -> dict:
    """Generate a unique coding challenge using Gemini."""
    raw = generate(
        system=f"""You are an expert coding interview coach creating daily challenges.

Today: {DAY_NAME}
Difficulty: {DIFFICULTY}
Topic: {TOPIC}

Generate a UNIQUE challenge (not a well-known LeetCode problem). Format your response EXACTLY as:

TITLE: [Challenge title]
DIFFICULTY: {DIFFICULTY}
TOPIC: {TOPIC}
ESTIMATED_TIME: [X minutes]

PROBLEM:
[Clear problem statement with context]

EXAMPLES:
Input: [example input]
Output: [example output]
Explanation: [why]

Input: [second example]
Output: [second example output]

CONSTRAINTS:
- [constraint 1]
- [constraint 2]

HINT:
[One helpful hint without giving away the solution]

SOLUTION_PYTHON:
```python
[Clean, well-commented Python solution with time/space complexity]
```

SOLUTION_JS:
```javascript
[Clean JavaScript solution]
```

TIME_COMPLEXITY: O(?)
SPACE_COMPLEXITY: O(?)

EXPLANATION:
[3-4 sentences explaining the approach and why it's optimal]

FOLLOW_UP:
[One follow-up question to make it harder]""",
        user=f"Generate challenge #{DAY_NUMBER} for {DATE}. Make it unique and practical.",
        max_tokens=2500,
    )

    title = extract_field(raw, "TITLE", default=f"Challenge #{DAY_NUMBER}")
    return {"raw": raw, "title": title}


def write_file(challenge: dict):
    write_tmp("challenge_title.txt", challenge["title"])

    raw = challenge["raw"]

    content = f"""# 💡 Coding Challenge #{DAY_NUMBER} — {DAY_NAME}

> *Daily challenge by [TechPulse Daily Digest](https://github.com/aredwan-xyz/devpulse-daily)*

**Difficulty:** {"🟢" if "Easy" in raw else "🟡" if "Medium" in raw else "🔴"} {DIFFICULTY}
**Topic:** {TOPIC}
**Streak:** Day {DAY_NUMBER} of the year

---

{raw}

---

## 💬 Discuss

Found a better solution? Have a question?
→ [Open a Discussion](https://github.com/aredwan-xyz/devpulse-daily/discussions)

---

*← [Back to Index](../../INDEX.md) · [All Challenges](.) · [Yesterday's Challenge](.)*
"""
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"✅ Challenge written: {OUTPUT_FILE}")
    print(f"   Title: {challenge['title']}")


if __name__ == "__main__":
    print(f"💡 Generating {DIFFICULTY} challenge on {TOPIC}...")
    challenge = generate_challenge()
    write_file(challenge)
    print("✅ Done!")

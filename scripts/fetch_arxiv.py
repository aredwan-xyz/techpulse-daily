#!/usr/bin/env python3
"""
fetch_arxiv.py
Fetches the most impactful recent AI/ML paper from arXiv
and uses Claude to explain it in plain English.
"""

import sys
import pathlib
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ai_client import generate
from utils import today, setup_dir

DATE, DAY_NAME, DAY_NUMBER = today()
OUTPUT_DIR = setup_dir("feeds/research")
OUTPUT_FILE = OUTPUT_DIR / f"{DATE}.md"

# Search categories to rotate through (gives variety)
CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.NE"]
CATEGORY = CATEGORIES[DAY_NUMBER % len(CATEGORIES)]


def fetch_arxiv_papers(category: str, max_results: int = 5) -> list[dict]:
    """Fetch recent papers from arXiv API."""
    query = urllib.request.quote(f"cat:{category}")
    url = (
        f"https://export.arxiv.org/api/query?"
        f"search_query={query}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    )

    req = urllib.request.Request(url, headers={"User-Agent": "DevPulse-Bot/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        xml_data = r.read()

    root = ET.fromstring(xml_data)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    papers = []

    for entry in root.findall("atom:entry", ns):
        id_el = entry.find("atom:id", ns)
        title_el = entry.find("atom:title", ns)
        summary_el = entry.find("atom:summary", ns)
        published_el = entry.find("atom:published", ns)

        if None in (id_el, title_el, summary_el, published_el):
            continue
        if not all(el.text for el in (id_el, title_el, summary_el, published_el)):
            continue

        paper_id = id_el.text.split("/")[-1]
        title = title_el.text.strip().replace("\n", " ")
        summary = summary_el.text.strip().replace("\n", " ")
        authors = [
            a.find("atom:name", ns).text
            for a in entry.findall("atom:author", ns)
            if a.find("atom:name", ns) is not None
            and a.find("atom:name", ns).text
        ]
        published = published_el.text[:10]

        papers.append({
            "id": paper_id,
            "title": title,
            "abstract": summary[:800],
            "authors": authors[:4],
            "published": published,
            "url": f"https://arxiv.org/abs/{paper_id}",
            "pdf_url": f"https://arxiv.org/pdf/{paper_id}",
        })

    return papers


def explain_paper(paper: dict) -> str:
    """Explain a paper in plain English using Gemini."""
    return generate(
        system="""You are a science communicator who makes AI research accessible to working developers.

        Given a paper abstract, write:

        ## 🎯 The Core Idea (2 sentences)
        What did they do, in plain English?

        ## 🔍 The Problem They Solved (2 sentences)
        What was broken or unknown before this paper?

        ## 💡 The Key Innovation (2-3 sentences)
        What's the novel approach or insight?

        ## 🛠️ Why Developers Should Care (2 sentences)
        Concrete impact on how we build AI systems.

        ## ⚡ TL;DR
        One sentence a non-expert could repeat at dinner.

        Be concrete, avoid jargon, use analogies where helpful.""",
        user=f"Paper: {paper['title']}\n\nAbstract: {paper['abstract']}",
        max_tokens=1200,
    )


def write_file(paper: dict, explanation: str):
    authors_str = ", ".join(paper["authors"])
    if len(paper["authors"]) >= 4:
        authors_str += " et al."

    content = f"""# 🤖 AI Research — {DAY_NAME}

> *Daily paper summary by [DevPulse](https://github.com/aredwan-xyz/devpulse-daily) · Category: `{CATEGORY}`*

---

## 📄 {paper['title']}

**Authors:** {authors_str}
**Published:** {paper['published']}
**arXiv ID:** [{paper['id']}]({paper['url']})

[![Read Paper](https://img.shields.io/badge/Read_Paper-arXiv-B31B1B?style=flat-square&logo=arxiv)](
{paper['url']})
[![PDF](https://img.shields.io/badge/Download_PDF-B31B1B?style=flat-square&logo=adobe)](
{paper['pdf_url']})

---

{explanation}

---

## 📝 Original Abstract

> {paper['abstract']}...

---

*← [Back to Index](../../INDEX.md) · [All Research](.) · [Yesterday's Paper](.)*
"""
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"✅ Research summary written: {OUTPUT_FILE}")


if __name__ == "__main__":
    print(f"🤖 Fetching arXiv papers (category: {CATEGORY})...")
    papers = fetch_arxiv_papers(CATEGORY, max_results=5)

    if not papers:
        print("❌ No papers found")
        sys.exit(1)

    paper = papers[0]  # Take the most recent
    print(f"   Selected: {paper['title'][:70]}...")

    print("🧠 Explaining with Claude...")
    explanation = explain_paper(paper)

    write_file(paper, explanation)
    print("✅ Done!")

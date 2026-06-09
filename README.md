<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,40:0f1b2d,80:0d2137,100:0d1117&height=200&section=header&text=DevPulse%20Daily&fontSize=62&fontColor=38bdf8&animation=fadeIn&fontAlignY=38&desc=🤖%20AI-powered%20daily%20intelligence%20feed%20for%20developers&descSize=18&descColor=8b949e&descAlignY=58" />

[![Stars](https://img.shields.io/github/stars/aredwan-xyz/devpulse-daily?style=for-the-badge&color=38bdf8&logo=github)](https://github.com/aredwan-xyz/devpulse-daily/stargazers)
[![Daily Commits](https://img.shields.io/badge/commits-10%2Fday-brightgreen?style=for-the-badge&logo=git&logoColor=white)](#)
[![Powered by Gemini](https://img.shields.io/badge/Powered%20by-Gemini%20AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=16&duration=2500&pause=800&color=38BDF8&center=true&vCenter=true&width=700&lines=📰+AI+%26+tech+news+summarized+daily;🔥+GitHub+trending+repos+archived+forever;🤖+AI+research+papers+explained+in+plain+English;💡+New+coding+challenge+every+single+day;🎯+Battle-tested+LLM+prompts%2C+fresh+daily)](https://github.com/aredwan-xyz/devpulse-daily)

**10 meaningful commits. Every. Single. Day.**  
*Star this repo to stay on the pulse of AI & dev — automatically.*

</div>

---

## 🧠 What Is DevPulse Daily?

DevPulse is a **self-updating knowledge feed** powered by AI and GitHub Actions.

Every day at 6 AM UTC, 10 automated jobs run — each one fetching real data, generating AI-curated summaries, and committing a new piece of content to this repo. The result: a growing, searchable archive of everything that matters in AI and software development.

> **No noise. No paywalls. No newsletters to ignore.**  
> Just the signal, committed to GitHub where you already live.

---

## 📦 What Gets Published Every Day

| # | Feed | What It Contains | Commit Time (UTC) |
|---|---|---|---|
| 1 | 📰 **Tech News Digest** | Top 5 AI & dev stories, AI-summarized | 06:00 |
| 2 | 🔥 **GitHub Trending** | Today's 10 hottest repos with descriptions | 06:15 |
| 3 | 🤖 **AI Research** | Top arXiv paper explained in plain English | 07:00 |
| 4 | 💡 **Coding Challenge** | Problem + optimal solution + explanation | 07:15 |
| 5 | 🛠️ **Tool Spotlight** | One dev tool worth knowing about | 08:00 |
| 6 | 🎯 **Prompt of the Day** | Battle-tested LLM prompt with example output | 08:15 |
| 7 | 🔐 **Security Pulse** | Critical CVEs + advisories summarized | 09:00 |
| 8 | 📊 **Market Pulse** | Trending tech skills & AI job market signal | 09:15 |
| 9 | 📚 **Learning Pick** | Best tutorial, talk, or article of the day | 10:00 |
| 10 | 🗓️ **Daily Index** | Master index updated with today's links | 10:15 |

---

## 📁 Repository Structure

```
devpulse-daily/
├── .github/
│   └── workflows/
│       └── daily-pulse.yml      ← The engine. Runs 10x/day.
│
├── feeds/                       ← Daily content, organized by type
│   ├── news/                    ← 📰 Tech news digests
│   ├── trending/                ← 🔥 GitHub trending snapshots
│   ├── research/                ← 🤖 AI paper summaries
│   ├── challenges/              ← 💡 Coding challenges + solutions
│   ├── tools/                   ← 🛠️ Tool spotlights
│   ├── prompts/                 ← 🎯 LLM prompts
│   ├── security/                ← 🔐 Security bulletins
│   ├── market/                  ← 📊 Market & jobs pulse
│   └── learning/                ← 📚 Learning picks
│
├── archive/                     ← Complete daily digests by date
│   └── YYYY/MM/YYYY-MM-DD.md   ← Full day's content in one file
│
├── scripts/                     ← Python scripts powering the feeds
│   ├── ai_client.py             ← Multi-provider AI (Gemini → Groq → GitHub Models)
│   ├── utils.py                 ← Shared helpers (date, dirs, parsing)
│   ├── fetch_news.py            ← HackerNews + NewsAPI digest
│   ├── fetch_trending.py        ← GitHub trending repos
│   ├── fetch_arxiv.py           ← arXiv AI/ML paper summaries
│   ├── fetch_security.py        ← NVD CVEs + security advisories
│   ├── fetch_market.py          ← AI job & skills trends
│   ├── generate_challenge.py    ← Daily coding challenge
│   ├── generate_prompt.py       ← LLM prompt of the day
│   ├── generate_tool.py         ← Developer tool spotlight
│   ├── generate_learning.py     ← Curated learning pick
│   └── update_index.py          ← Daily archive + INDEX.md + STATS.md
│
├── INDEX.md                     ← 🗂️ Auto-updated master index
├── STATS.md                     ← 📈 Repo stats and milestones
└── README.md                    ← You are here
```

---

## 🔥 Today's Digest

<!-- AUTO-UPDATED DAILY — DO NOT EDIT MANUALLY -->
> *Last updated: 2026-06-09 · [Full archive](archive/)*

| Feed | Today's Issue |
|---|---|
| 📰 Tech News | [Read →](feeds/news/2026-06-09.md) |
| 🔥 GitHub Trending | [Read →](feeds/trending/2026-06-09.md) |
| 🤖 AI Research | [Read →](feeds/research/2026-06-09.md) |
| 💡 Coding Challenge | [Read →](feeds/challenges/2026-06-09.md) |
| 🛠️ Tool Spotlight | [Read →](feeds/tools/2026-06-09.md) |
| 🎯 Prompt of the Day | [Read →](feeds/prompts/2026-06-09.md) |
| 🔐 Security Pulse | [Read →](feeds/security/2026-06-09.md) |
| 📊 Market Pulse | [Read →](feeds/market/2026-06-09.md) |
| 📚 Learning Pick | [Read →](feeds/learning/2026-06-09.md) |
---

## ⚙️ How It Works

```
┌─────────────────────────────────────────────────────────┐
│                  GitHub Actions (Cron)                   │
│              Runs 10 jobs across the day                 │
└──────────────┬──────────────────────────────────────────┘
               │
     ┌─────────▼──────────┐
     │   Python Scripts    │
     │  (fetch + generate) │
     └─────────┬───────────┘
               │
     ┌─────────▼────────────────────────────────────────┐
     │              AI Provider (auto-fallback)          │
     │  1. Google Gemini 2.0 Flash  (primary)           │
     │  2. Google Gemini 2.0 Flash Lite  (fallback)     │
     │  3. Groq Llama 3.3 70B  (if GROQ_API_KEY set)   │
     │  4. GitHub Models gpt-4o-mini  (always available) │
     └─────────┬─────────────────────────────────────────┘
               │
     ┌─────────▼──────────┐
     │   Markdown Files    │
     │   Committed to Git  │
     └─────────────────────┘
```

**Data sources used every day:**
- GitHub API — trending repos
- arXiv API — AI/ML research papers
- HackerNews Firebase API — top tech stories
- NVD API — security CVEs and advisories
- NewsAPI — tech news (optional, enhances quality)
- Algolia HN Search — market and jobs signal

---

## 📊 Archive Stats

<!-- AUTO-UPDATED -->
| Metric | Count |
|---|---|
| 📅 Days active | 0 |
| 📝 Total entries | 0 |
| 🔥 Trending repos archived | 0 |
| 🤖 Papers summarized | 0 |
| 💡 Challenges published | 0 |
| 🎯 Prompts curated | 0 |

---

## 🚀 Deploy Your Own

Fork this repo, then configure secrets in **Settings → Secrets and variables → Actions**:

| Secret | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Recommended | Free at [aistudio.google.com](https://aistudio.google.com/apikey) — 1,500 req/day. Use **"Create API key in new project"** to get free-tier access. |
| `GROQ_API_KEY` | Optional | Free at [console.groq.com](https://console.groq.com) — 14,400 req/day. Used as fallback if Gemini quota is hit. |
| `NEWS_API_KEY` | Optional | Free at [newsapi.org](https://newsapi.org) — enhances the news feed quality. |

> **No extra setup for GitHub Models.** The workflow automatically uses your repo's built-in `GITHUB_TOKEN` as a final fallback — no secret needed.

Then go to **Actions → 🤖 DevPulse Daily Feed → Run workflow** to trigger the first run.

---

## 🌟 Why Star This?

- 📌 **Bookmark via star** — your GitHub stars are a reading list. Make this one of them.
- 🔔 **Watch the repo** — get notified when big AI developments drop
- 🍴 **Fork it** — run your own version in 5 minutes
- 🤝 **Contribute** — add a new feed category via PR

---

## 📬 Maintained By

<div align="center">

**[Abid Redwan](https://github.com/aredwan-xyz)** · Interactive Media Designer & AI Engineer  
[aredwan.com](http://aredwan.com) · [CodeBeez Technology](https://github.com/aredwan-xyz)

[![Follow](https://img.shields.io/github/followers/aredwan-xyz?style=social)](https://github.com/aredwan-xyz)

</div>

---

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0d2137,100:0d1117&height=120&section=footer" />

<div align="center">
  <sub>⚡ Auto-updated daily by Gemini AI · Built by Abid Redwan · Star to subscribe</sub>
</div>

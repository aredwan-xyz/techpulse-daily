# Contributing to TechPulse Daily Digest

Thank you for your interest in contributing!

## How to Contribute

### Reporting Issues
- Use [GitHub Issues](../../issues) to report bugs or suggest new feed types.
- Include a clear description and steps to reproduce for bugs.

### Suggesting New Feeds
Open an issue with the label `enhancement` describing:
- What data source you'd like added
- What value it provides to developers
- Any relevant API or scraping approach

### Pull Requests
1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature-name`
3. Make your changes and test locally
4. Commit with a clear message
5. Open a pull request against `main`

### Local Setup
```bash
git clone https://github.com/aredwan-xyz/devpulse-daily.git
cd devpulse-daily
pip install -r requirements.txt
cp .env.example .env  # add your API keys
python scripts/fetch_tech_news.py
```

### Required Secrets (for GitHub Actions)
| Secret | Purpose |
|--------|---------|
| `GEMINI_API_KEY` | Primary AI provider |
| `GROQ_API_KEY` | Fallback AI provider |
| `GH_TOKEN` | GitHub API & commit access |

## Code Style
- Follow existing script patterns in `/scripts`
- Use `ai_client.py` for all AI calls (supports multi-provider fallback)
- Keep scripts self-contained and idempotent

## License
By contributing, you agree your contributions will be licensed under the [MIT License](../LICENSE).

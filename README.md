# TechPulse Daily Digest

AI-assisted developer reading: news, repository snapshots, research, exercises,
tools, prompts, security notes, hiring-thread notes and learning suggestions.

**Status: reliability remediation in progress.** Historical archives can be
incomplete. A scheduled run or index commit alone does not establish publication.
The latest successfully validated complete issue is shown below.

## Latest complete digest

<!-- AUTO-UPDATED DAILY — DO NOT EDIT MANUALLY -->
No complete digest has passed validation.

| Feed | Latest complete issue |
|---|---|
| 📰 Tech News Digest | Not available |
| 🔥 GitHub Repository Snapshot | Not available |
| 🤖 AI Research | Not available |
| 💡 Coding Challenge | Not available |
| 🛠️ Tool Spotlight | Not available |
| 🎯 Prompt of the Day | Not available |
| 🔐 Security Pulse | Not available |
| 📊 Hiring Thread Notes | Not available |
| 📚 Learning Pick | Not available |


---

## Publishing contract

One daily workflow generates all nine feeds in a temporary directory, validates
them, builds the archive and navigation, and publishes one commit. If any source,
provider or validation step fails, the workflow fails and the previous public
issue stays in place. A completed date is immutable on rerun.

`STATUS.json` is written only with a complete publication. Its `published_date`
is the last successful issue date, not the last time the scheduler ran. A stale
date should be investigated in [Actions](https://github.com/aredwan-xyz/techpulse-daily/actions).
Enable failed-workflow notifications in your GitHub notification settings.

Validation catches missing/empty outputs, placeholders, malformed code fences,
unsafe markup and missing source URLs. It does **not** prove factual accuracy,
resource availability, coding-solution correctness or exhaustive CVE coverage.
Check linked primary sources before acting. Challenges and prompts are generated
exercises, not benchmarked or “battle-tested” assets. Hiring notes summarize a
limited HN source, not a comprehensive market or salary survey.

## Run your own

```bash
git clone https://github.com/aredwan-xyz/techpulse-daily.git
cd techpulse-daily
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

For GitHub Actions, add `GEMINI_API_KEY` as a repository secret. Optionally add
`GROQ_API_KEY` for an independent fallback. Store keys in Actions secrets, never
in code or repository variables. Model IDs belong in variables:

| Variable | Default |
|---|---|
| `GEMINI_MODEL` | `gemini-3.8-flash` |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |

The default Gemini model is listed as stable in the
[official model catalog](https://ai.google.dev/gemini-api/docs/models)
(checked October 28, 2026). Check access, quotas, billing and the
[deprecation schedule](https://ai.google.dev/gemini-api/docs/deprecations)
before enabling the schedule. Paid usage and all API limits depend on your
provider project; no fixed free quota or zero-cost guarantee is assumed.
GitHub Models is not used.

The schedule requests a run at 10:17 UTC; GitHub can delay scheduled execution.
Use **Actions → TechPulse Daily Digest → Run workflow** on `main` to publish
manually. Pull requests run offline regression tests and cannot publish content.

Locally, provide the selected provider key in your shell environment and run
`python scripts/run_daily.py`. This updates local validated publication paths;
review the changes before committing. It does not load a `.env` automatically.
`TECHPULSE_DATE=YYYY-MM-DD` freezes the issue date for every subprocess; otherwise
the runner chooses the UTC date once at startup. Provider calls use a 60-second
timeout and at most three attempts for transient errors before falling back.

## Repository layout

- `scripts/run_daily.py`: staging and publication orchestration
- `scripts/ai_client.py`: configurable Gemini and optional Groq adapters
- `scripts/update_index.py`: complete-issue validation and navigation
- `feeds/`: individual Markdown feeds (legacy entries are preserved)
- `archive/`: daily bundles; older bundles may be incomplete
- `INDEX.md`: validated complete issues only
- `STATUS.json`: last successful publication, once one exists
- `tests/`: offline failure and publication regression tests

Run `python scripts/update_index.py` to rebuild navigation from existing complete
issues without generating content or promoting a partial day.

## Release verification

Before claiming unattended operation: verify a complete generated artifact,
exercise a provider outage and a source outage, confirm no public update on
failure, rerun a completed date without duplicate output, then observe seven
complete scheduled cycles. Those production checks require configured provider
accounts and are not established by the offline test suite alone.

Maintained by [Abid Redwan](https://github.com/aredwan-xyz). [MIT License](LICENSE).

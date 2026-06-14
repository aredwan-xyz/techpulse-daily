#!/usr/bin/env python3
"""
fetch_security.py
Fetches recent CVEs from NVD (National Vulnerability Database)
and generates developer-readable security bulletins.
"""

import sys
import json
import pathlib
import urllib.request
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ai_client import generate
from utils import today, setup_dir

DATE, DAY_NAME, DAY_NUMBER = today()
OUTPUT_DIR = setup_dir("feeds/security")
OUTPUT_FILE = OUTPUT_DIR / f"{DATE}.md"

# Fetch CVEs from the last 2 days to ensure we catch recent ones
DAYS_BACK = 2


def fetch_recent_cves(limit: int = 10) -> tuple[list[dict], bool]:
    """Fetch recent CVEs from NVD API v2.

    Returns (cves, api_available). If the API is unreachable, api_available
    is False and cves is empty — callers must distinguish this from a
    genuinely quiet day (api_available=True, cves=[]).
    """
    import datetime
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=DAYS_BACK)

    # NVD API v2 requires ISO 8601 with UTC timezone designator
    start_str = urllib.parse.quote(start_date.strftime("%Y-%m-%dT%H:%M:%S.000") + " UTC+00:00")
    end_str = urllib.parse.quote(end_date.strftime("%Y-%m-%dT%H:%M:%S.000") + " UTC+00:00")

    url = (
        f"https://services.nvd.nist.gov/rest/json/cves/2.0?"
        f"pubStartDate={start_str}&pubEndDate={end_str}"
        f"&cvssV3Severity=HIGH&resultsPerPage={limit}"
    )

    req = urllib.request.Request(url, headers={"User-Agent": "TechPulse-Bot/1.0"})

    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
    except Exception as e:
        print(f"⚠️  NVD API error: {e}")
        return [], False

    cves = []
    for item in data.get("vulnerabilities", []):
        cve = item.get("cve", {})
        cve_id = cve.get("id", "Unknown")

        descriptions = cve.get("descriptions", [])
        description = next(
            (d["value"] for d in descriptions if d.get("lang") == "en"),
            "No description available"
        )

        metrics = cve.get("metrics", {})
        cvss_data = metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {})
        score = cvss_data.get("baseScore", 0)
        severity = cvss_data.get("baseSeverity", "UNKNOWN")

        cves.append({
            "id": cve_id,
            "description": description[:400],
            "score": score,
            "severity": severity,
            "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
            "published": cve.get("published", DATE)[:10],
        })

    return sorted(cves, key=lambda x: x["score"], reverse=True)[:5], True


def generate_security_bulletin(cves: list[dict], api_available: bool) -> str:
    """Explain CVEs in developer-friendly language using Gemini."""
    if not api_available:
        cves_text = (
            "⚠️ The NVD API was unavailable today. "
            "Check https://nvd.nist.gov/ directly for recent vulnerabilities."
        )
    elif not cves:
        cves_text = "No HIGH/CRITICAL CVEs published in the last 48 hours. Relatively quiet security day."
    else:
        cves_text = "\n".join([
            f"- {c['id']} (CVSS {c['score']}, {c['severity']}): {c['description'][:200]}"
            for c in cves
        ])

    return generate(
        system="""You are a security engineer writing a daily briefing for developers.

        For each CVE, explain:
        1. What software/library is affected (in plain English)
        2. What an attacker could do if they exploited it
        3. The one-line action developers should take (patch, workaround, or monitor)

        Format as:
        ### [CVE-ID] — [Affected Software] (CVSS X.X)
        **Impact:** [plain English impact]
        **Action:** [what to do right now]

        If the NVD API was unavailable, acknowledge it and give general security advice instead.

        End with a "Security Mindset" tip — one actionable security habit for developers.""",
        user=f"Today's CVEs ({DATE}):\n{cves_text}\n\nGenerate developer-friendly bulletin.",
        max_tokens=1000,
    )


def write_file(cves: list[dict], bulletin: str, api_available: bool):
    severity_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}

    if not api_available:
        cve_table = "| ⚠️ NVD API unavailable | — | — | — |"
    elif cves:
        cve_table = "\n".join([
            f"| [{c['id']}]({c['url']}) | {severity_emoji.get(c['severity'], '⚪')} {c['severity']} | "
            f"CVSS {c['score']} | {c['published']} |"
            for c in cves
        ])
    else:
        cve_table = "| No critical CVEs today | 🟢 Quiet | — | — |"

    content = f"""# 🔐 Security Pulse — {DAY_NAME}

> *Daily security bulletin by [TechPulse Daily Digest](https://github.com/aredwan-xyz/devpulse-daily)*
> *Data source: [NIST NVD](https://nvd.nist.gov/) · Filtered to HIGH/CRITICAL severity*

---

## ⚠️ Today's CVE Summary

| CVE ID | Severity | CVSS Score | Published |
|---|---|---|---|
{cve_table}

---

## 📋 Developer Briefing

{bulletin}

---

## 🛡️ Security Resources

- [CISA Known Exploited Vulnerabilities](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
- [NVD Full Database](https://nvd.nist.gov/vuln/search)
- [Snyk Vulnerability DB](https://security.snyk.io/)
- [OSV (Open Source Vulns)](https://osv.dev/)

---

*← [Back to Index](../../INDEX.md) · [All Security Bulletins](.) · [Yesterday](.)*
"""
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"✅ Security bulletin written: {OUTPUT_FILE}")


if __name__ == "__main__":
    print("🔐 Fetching recent CVEs from NVD...")
    cves, api_available = fetch_recent_cves()

    if not api_available:
        print("⚠️  NVD API unavailable — generating advisory bulletin")
    else:
        print(f"   Found {len(cves)} HIGH/CRITICAL CVEs")

    print("🤖 Generating developer bulletin...")
    bulletin = generate_security_bulletin(cves, api_available)

    write_file(cves, bulletin, api_available)
    print("✅ Done!")

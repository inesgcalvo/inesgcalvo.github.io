#!/usr/bin/env python3
"""Refresh the citation counts shown on publications.html.

Every peer-reviewed entry carries a marker like

    <span class="cited-by" data-doi="10.7554/eLife.65712">26 citations</span>

This script asks Crossref how many works reference each of those DOIs
(`is-referenced-by-count`), rewrites the span contents, and stamps the
"last checked" date at the bottom of the list.

Only the standard library is used, so the GitHub Action needs no
dependency install. Run it by hand the same way the workflow does:

    python3 scripts/update_citations.py

Exit codes: 0 if the file is up to date (whether or not it changed),
1 if a DOI could not be looked up — the file is left untouched in that
case, so a Crossref outage never blanks the numbers already published.
"""

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "publications.html"

# Crossref asks for a contact address so they can get in touch about a
# misbehaving script instead of silently blocking it.
USER_AGENT = (
    "inesgcalvo.github.io citation updater "
    "(+https://github.com/inesgcalvo/inesgcalvo.github.io; "
    "mailto:ines@vetmonitor.ai)"
)
TIMEOUT = 30

CITED_BY_RE = re.compile(
    r'(<span class="cited-by" data-doi="(?P<doi>[^"]+)">)(?P<body>[^<]*)(</span>)'
)
UPDATED_RE = re.compile(
    r'(<time class="metrics-updated" datetime=")(?P<iso>[^"]*)(">)(?P<label>[^<]*)(</time>)'
)


def fetch_count(doi):
    """Return how many works Crossref knows to cite this DOI."""
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        payload = json.load(response)
    return int(payload["message"]["is-referenced-by-count"])


def phrase(count):
    return "1 citation" if count == 1 else f"{count} citations"


def main():
    html = PAGE.read_text(encoding="utf-8")

    dois = [match.group("doi") for match in CITED_BY_RE.finditer(html)]
    if not dois:
        print(f"No .cited-by markers found in {PAGE.name} — nothing to update.")
        return 0

    counts = {}
    for doi in dois:
        try:
            counts[doi] = fetch_count(doi)
        except (urllib.error.URLError, KeyError, ValueError, TimeoutError) as error:
            print(f"error: could not read the citation count for {doi}: {error}")
            print("Leaving the published numbers untouched.")
            return 1
        print(f"{doi}: {counts[doi]}")

    def rewrite(match):
        return match.group(1) + phrase(counts[match.group("doi")]) + match.group(4)

    updated = CITED_BY_RE.sub(rewrite, html)

    today = datetime.now(timezone.utc).date()
    stamp = today.strftime("%-d %B %Y")
    updated = UPDATED_RE.sub(
        lambda m: m.group(1) + today.isoformat() + m.group(3) + stamp + m.group(5),
        updated,
    )

    if updated == html:
        print("Citation counts are already up to date.")
        return 0

    PAGE.write_text(updated, encoding="utf-8")
    print(f"Updated {PAGE.name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

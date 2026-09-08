#!/usr/bin/env python3
"""Generate reliable, self-contained GitHub profile metric cards.

The cards are generated during GitHub Actions runs and published with the
profile's existing output branch, so the README does not depend on a public
third-party stats API at render time.
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from html import escape
from pathlib import Path
from typing import Any

USERNAME = os.environ.get("GH_USERNAME", "Ankit-DataScientist-Git")
TOKEN = os.environ.get("GH_TOKEN", "")
OUT = Path("dist")
OUT.mkdir(parents=True, exist_ok=True)


def github_get(path: str) -> Any:
    request = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "github-profile-cards",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def svg_shell(width: int, height: int, title: str, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">
  <title>{escape(title)}</title>
  <rect width="100%" height="100%" rx="14" fill="#0A101F" stroke="#1F2937"/>
  {body}
</svg>\n'''


def text(x: int, y: int, value: str, size: int, fill: str = "#F8FAFC", weight: int = 400) -> str:
    return f'<text x="{x}" y="{y}" fill="{fill}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="{size}px" font-weight="{weight}">{escape(value)}</text>'


def get_repos() -> list[dict[str, Any]]:
    repos: list[dict[str, Any]] = []
    page = 1
    while page <= 10:
        query = urllib.parse.urlencode({"per_page": 100, "page": page, "type": "owner", "sort": "updated"})
        batch = github_get(f"/users/{urllib.parse.quote(USERNAME)}/repos?{query}")
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return [r for r in repos if not r.get("fork") and not r.get("archived")]


def main() -> None:
    user = github_get(f"/users/{urllib.parse.quote(USERNAME)}")
    repos = get_repos()

    stars = sum(int(repo.get("stargazers_count", 0) or 0) for repo in repos)
    forks = sum(int(repo.get("forks_count", 0) or 0) for repo in repos)
    languages: dict[str, int] = {}

    for repo in repos[:100]:
        try:
            lang = github_get(f"/repos/{urllib.parse.quote(repo['full_name'], safe='/')}/languages")
        except Exception:
            continue
        for name, amount in lang.items():
            languages[name] = languages.get(name, 0) + int(amount)

    top_languages = sorted(languages.items(), key=lambda item: item[1], reverse=True)[:6]
    total_bytes = sum(v for _, v in top_languages) or 1

    body = []
    body.append(text(28, 38, "PROFILE METRICS", 13, "#22D3EE", 700))
    body.append(text(28, 70, f"{USERNAME} · GitHub activity snapshot", 18, "#F8FAFC", 700))

    metrics = [
        ("Public repos", str(user.get("public_repos", 0)), "#22D3EE"),
        ("Followers", str(user.get("followers", 0)), "#A78BFA"),
        ("Stars earned", str(stars), "#10B981"),
        ("Forks", str(forks), "#F59E0B"),
    ]
    x_positions = [28, 205, 382, 559]
    for (label, value, accent), x in zip(metrics, x_positions):
        body.append(f'<rect x="{x}" y="96" width="154" height="82" rx="12" fill="#111827" stroke="#263244"/>')
        body.append(text(x + 14, 122, label.upper(), 10, "#94A3B8", 700))
        body.append(text(x + 14, 157, value, 28, accent, 700))

    body.append(text(28, 212, "TOP LANGUAGES", 12, "#22D3EE", 700))
    bar_x, bar_y, bar_w = 28, 232, 685
    cursor = bar_x
    palette = ["#A78BFA", "#22D3EE", "#10B981", "#F59E0B", "#818CF8", "#64748B"]
    for idx, (name, amount) in enumerate(top_languages):
        width = max(8, int(bar_w * amount / total_bytes))
        body.append(f'<rect x="{cursor}" y="{bar_y}" width="{width}" height="10" fill="{palette[idx % len(palette)]}"/>')
        cursor += width

    legend_y = 274
    for idx, (name, amount) in enumerate(top_languages):
        share = (amount / total_bytes) * 100
        col = idx % 3
        row = idx // 3
        x = 28 + col * 230
        y = legend_y + row * 30
        body.append(f'<circle cx="{x + 5}" cy="{y - 4}" r="5" fill="{palette[idx % len(palette)]}"/>')
        body.append(text(x + 18, y, f"{name}  {share:.1f}%", 12, "#CBD5E1", 600))

    (OUT / "profile-stats.svg").write_text(svg_shell(740, 340, "GitHub profile metrics", "\n  ".join(body)), encoding="utf-8")


if __name__ == "__main__":
    main()

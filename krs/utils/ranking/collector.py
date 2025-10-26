"""Collect metrics for ranking snapshots."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import requests

from .schema import normalise_timestamp

GITHUB_API = "https://api.github.com"


@dataclass(frozen=True)
class ToolSource:
    name: str
    repo: str
    category: str
    cncf_status: str = "unlisted"
    mcp_support: bool = False
    capabilities: Sequence[str] = field(default_factory=list)


class GitHubAPI:
    def __init__(self, token: Optional[str] = None, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "krs-ranking-collector",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.session.headers.update(headers)

    def get_repo(self, full_name: str) -> Dict[str, Any]:
        resp = self.session.get(f"{GITHUB_API}/repos/{full_name}")
        resp.raise_for_status()
        return resp.json()

    def get_issue_velocity(self, full_name: str, since: datetime) -> float:
        since_str = since.strftime("%Y-%m-%d")
        base = f"repo:{full_name} is:issue created:>={since_str}"
        open_count = self._issue_count(f"{base} state:open")
        closed_count = self._issue_count(f"{base} state:closed")
        total = open_count + closed_count
        return round(closed_count / total, 4) if total else 0.0

    def get_recent_stars(self, full_name: str, since: datetime) -> int:
        resp = self.session.get(
            f"{GITHUB_API}/repos/{full_name}/stargazers",
            params={"per_page": 100},
            headers={"Accept": "application/vnd.github.star+json"},
        )
        if resp.status_code == 404:
            return 0
        resp.raise_for_status()
        count = 0
        for item in resp.json():
            ts = item.get("starred_at")
            if not ts:
                continue
            when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if when >= since:
                count += 1
        return count

    def _issue_count(self, query: str) -> int:
        resp = self.session.get(f"{GITHUB_API}/search/issues", params={"q": query, "per_page": 1})
        resp.raise_for_status()
        return int(resp.json().get("total_count", 0))


class RankingCollector:
    def __init__(self, *, github: Optional[GitHubAPI] = None, now: Optional[datetime] = None):
        self.github = github or GitHubAPI(token=self._token())
        self.now = now or datetime.now(timezone.utc)

    def collect_snapshot(self, sources: Sequence[ToolSource]) -> Dict[str, Any]:
        generated = normalise_timestamp(self.now)
        since_30d = self.now - timedelta(days=30)
        tools: List[Dict[str, Any]] = []

        for entry in sources:
            repo_data = self.github.get_repo(entry.repo)
            last_commit = repo_data.get("pushed_at") or repo_data.get("updated_at")
            if last_commit:
                last_commit_dt = datetime.fromisoformat(last_commit.replace("Z", "+00:00"))
            else:
                last_commit_dt = self.now - timedelta(days=365)
            issue_velocity = self.github.get_issue_velocity(entry.repo, since_30d)
            trend = self.github.get_recent_stars(entry.repo, since_30d)

            tools.append(
                {
                    "name": entry.name.lower(),
                    "repo": entry.repo,
                    "category": entry.category,
                    "stars": int(repo_data.get("stargazers_count", 0)),
                    "forks": int(repo_data.get("forks_count", 0)),
                    "open_issues": int(repo_data.get("open_issues_count", 0)),
                    "last_commit_at": normalise_timestamp(last_commit_dt.astimezone(timezone.utc)),
                    "issue_velocity_30d": issue_velocity,
                    "trend_30d_stars": int(trend),
                    "cncf_status": entry.cncf_status,
                    "mcp_support": bool(entry.mcp_support),
                    "capabilities": list(entry.capabilities),
                    "score_inputs": {
                        "popularity": 0.0,
                        "recency": 0.0,
                        "growth": 0.0,
                        "issue_velocity": issue_velocity,
                        "cncf": self._cncf(entry.cncf_status),
                    },
                }
            )

        return {
            "metadata": {
                "generated_at": generated,
                "source_repos": sorted({src.repo for src in sources}),
                "version": "1.0",
            },
            "tools": tools,
        }

    def write_snapshot(self, snapshot: Dict[str, Any], directory: Path) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        stamp = snapshot["metadata"]["generated_at"].replace(":", "").replace("-", "")
        path = directory / f"snapshot-{stamp}.json"
        with path.open("w", encoding="utf-8") as fh:
            json.dump(snapshot, fh, indent=2, sort_keys=True)
        return path

    @staticmethod
    def _cncf(status: str) -> float:
        value = (status or "").lower()
        if value in {"graduated", "incubating"}:
            return 1.0
        if value == "sandbox":
            return 0.5
        return 0.0

    @staticmethod
    def _token() -> Optional[str]:
        from os import getenv

        return getenv("GITHUB_TOKEN")


__all__ = ["RankingCollector", "ToolSource", "GitHubAPI"]

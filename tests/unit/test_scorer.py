from datetime import datetime, timezone, timedelta
from pathlib import Path

from krs.utils.ranking.scorer import RankingScorer, ScoreWeights


def build_snapshot(now, overrides=None):
    overrides = overrides or []
    base_tool = {
        "repo": "owner/repo-a",
        "category": "logging",
        "stars": 10,
        "forks": 3,
        "open_issues": 5,
        "last_commit_at": now,
        "issue_velocity_30d": 0.5,
        "trend_30d_stars": 5,
        "cncf_status": "sandbox",
        "mcp_support": False,
        "capabilities": [],
        "score_inputs": {
            "popularity": 0.0,
            "recency": 0.0,
            "growth": 0.0,
            "issue_velocity": 0.5,
            "cncf": 0.5,
        },
    }
    tools = []
    for idx, extra in enumerate(overrides):
        entry = dict(base_tool)
        entry.update(extra)
        entry["name"] = extra.get("name", f"tool-{idx}")
        entry["last_commit_at"] = extra.get("last_commit_at", now)
        tools.append(entry)

    return {
        "metadata": {
            "generated_at": now,
            "source_repos": [tool["repo"] for tool in tools],
            "version": "1.0",
        },
        "tools": tools,
    }


def test_scorer_orders_by_popularity_when_weighted():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    snapshot = build_snapshot(
        now,
        [
            {"name": "alpha", "stars": 500, "forks": 80},
            {"name": "beta", "stars": 50, "forks": 10},
        ],
    )
    scorer = RankingScorer(weights=ScoreWeights(popularity=1.0, recency=0, issue_velocity=0, growth=0, cncf_status=0))
    outputs = scorer.build_outputs(snapshot, data_dir=Path("krs/data/tool_rankings"), dry_run=True)
    category = outputs.canonical["categories"][0]
    assert category["tools"][0]["name"] == "alpha"
    assert category["tools"][1]["name"] == "beta"


def test_scorer_applies_recency_weight():
    now = datetime.now(timezone.utc)
    snapshot = build_snapshot(
        now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        [
            {
                "name": "fresh",
                "last_commit_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            {
                "name": "stale",
                "last_commit_at": (now - timedelta(days=180)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        ],
    )
    scorer = RankingScorer(weights=ScoreWeights(popularity=0, recency=1.0, issue_velocity=0, growth=0, cncf_status=0))
    outputs = scorer.build_outputs(snapshot, data_dir=Path("krs/data/tool_rankings"), dry_run=True)
    category = outputs.canonical["categories"][0]
    assert category["tools"][0]["name"] == "fresh"
    assert category["tools"][1]["name"] == "stale"


def test_persist_outputs_writes_legacy_payload(tmp_path):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    snapshot = build_snapshot(
        now,
        [
            {"name": "alpha", "stars": 10, "forks": 3},
            {"name": "beta", "stars": 5, "forks": 1},
        ],
    )
    scorer = RankingScorer()
    outputs = scorer.build_outputs(snapshot, data_dir=tmp_path, dry_run=True)
    scorer.persist_outputs(outputs, tmp_path)

    canonical_path = tmp_path / "canonical.json"
    kubetools_path = tmp_path.parent / "kubetools_data.json"
    category_rank_path = tmp_path.parent / "category_rank.json"

    assert canonical_path.exists()
    assert kubetools_path.exists()
    assert category_rank_path.exists()

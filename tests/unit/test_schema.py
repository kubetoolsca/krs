from datetime import datetime, timezone

import pytest

from krs.utils.ranking.schema import (
    ValidationError,
    normalise_timestamp,
    validate_canonical,
    validate_snapshot,
    validate_sources,
)


def _sample_snapshot():
    generated = normalise_timestamp(datetime.now(timezone.utc))
    return {
        "metadata": {
            "generated_at": generated,
            "source_repos": ["kubetoolsca/krs"],
            "version": "1.0",
        },
        "tools": [
            {
                "name": "krs",
                "repo": "kubetoolsca/krs",
                "category": "ai-operations",
                "stars": 100,
                "forks": 10,
                "open_issues": 5,
                "last_commit_at": generated,
                "issue_velocity_30d": 0.5,
                "trend_30d_stars": 12,
                "cncf_status": "unlisted",
                "mcp_support": False,
                "capabilities": ["recommend"],
                "score_inputs": {
                    "popularity": 0.0,
                    "recency": 0.0,
                    "growth": 0.0,
                    "issue_velocity": 0.5,
                    "cncf": 0.0,
                },
            }
        ],
    }


def _sample_canonical(snapshot):
    return {
        "metadata": snapshot["metadata"],
        "categories": [
            {
                "name": "ai-operations",
                "tools": [
                    {
                        "name": "krs",
                        "rank": 1,
                        "repo": "kubetoolsca/krs",
                        "score": 0.42,
                        "score_inputs": {
                            "popularity": 0.2,
                            "recency": 0.8,
                            "growth": 0.6,
                        },
                        "cncf_status": "unlisted",
                    }
                ],
            }
        ],
        "legacy": {"kubetools_data": [], "category_rank": {}},
    }


def test_validate_snapshot_accepts_expected_payload():
    snapshot = _sample_snapshot()
    validate_snapshot(snapshot)  # no raise


def test_validate_snapshot_rejects_missing_field():
    snapshot = _sample_snapshot()
    snapshot["tools"][0].pop("stars")
    with pytest.raises(ValidationError):
        validate_snapshot(snapshot)


def test_validate_canonical_accepts_expected_payload():
    snapshot = _sample_snapshot()
    canonical = _sample_canonical(snapshot)
    validate_canonical(canonical)


def test_validate_canonical_requires_rank():
    snapshot = _sample_snapshot()
    canonical = _sample_canonical(snapshot)
    canonical["categories"][0]["tools"][0].pop("rank")
    with pytest.raises(ValidationError):
        validate_canonical(canonical)


def test_validate_sources_accepts_curated_payload():
    payload = {
        "tools": [
            {
                "name": "krs",
                "repo": "kubetoolsca/krs",
                "category": "ai-operations",
                "capabilities": ["diagnose"],
            }
        ]
    }
    validate_sources(payload)


def test_validate_sources_rejects_missing_repo():
    payload = {"tools": [{"name": "missing", "category": "test"}]}
    with pytest.raises(ValidationError):
        validate_sources(payload)

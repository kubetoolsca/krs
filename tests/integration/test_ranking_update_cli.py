import json
from datetime import datetime, timezone
from types import SimpleNamespace

from typer.testing import CliRunner


def test_rank_update_cli(monkeypatch, tmp_path):
    from krs.krs import app, krs as krs_main
    from krs.utils import fetch_tools_krs
    from krs.utils import constants

    runner = CliRunner()

    rankings_dir = tmp_path / "tool_rankings"
    monkeypatch.setattr(constants, "TOOL_RANKINGS_DIR", str(rankings_dir))
    monkeypatch.setattr(constants, "TOOL_RANKINGS_CANONICAL_PATH", str(rankings_dir / "canonical.json"))
    monkeypatch.setattr(fetch_tools_krs, "TOOL_RANKINGS_CANONICAL_PATH", str(rankings_dir / "canonical.json"))

    krs_main.rankings_data_dir = rankings_dir

    call_args = {}

    def fake_update_rankings(*, dry_run: bool):
        call_args['dry_run'] = dry_run

        canonical = {
            "metadata": {
                "generated_at": datetime(2024, 1, 1, tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "source_repos": ["example/repo"],
                "version": "1.0",
            },
            "categories": [
                {
                    "name": "ai-operations",
                    "tools": [
                        {
                            "name": "sample-tool",
                            "rank": 1,
                            "repo": "example/repo",
                            "score": 0.9,
                            "score_inputs": {
                                "popularity": 0.5,
                                "recency": 0.5,
                                "growth": 0.5,
                            },
                            "cncf_status": "unlisted",
                            "reason": "fixture",
                        }
                    ],
                }
            ],
            "legacy": {"kubetools_data": [], "category_rank": {}},
            "weights": {},
        }

        snapshots_dir = rankings_dir / "snapshots"
        snapshots_dir.mkdir(parents=True, exist_ok=True)

        if not dry_run:
            with (rankings_dir / "canonical.json").open("w", encoding="utf-8") as fh:
                json.dump(canonical, fh)

        return SimpleNamespace(
            snapshot={"metadata": canonical["metadata"], "tools": []},
            canonical=canonical,
            legacy={"kubetools_data": [], "category_rank": {}},
            weights={},
            diff_summary="",
            previous_canonical=None,
        )

    monkeypatch.setattr(krs_main, "update_rankings", fake_update_rankings)

    result = runner.invoke(app, ["rank", "update"])
    assert result.exit_code == 0, result.stdout

    canonical_path = rankings_dir / "canonical.json"
    assert canonical_path.exists()
    assert call_args['dry_run'] is False

    with canonical_path.open() as fh:
        canonical = json.load(fh)
    assert canonical["categories"], "Canonical payload should include categories"

    tools_dict, category_dict, cncf = fetch_tools_krs.krs_tool_ranking_info()
    assert tools_dict, "Tools dictionary should be populated from canonical data"
    assert category_dict, "Category mapping should be populated"
    assert cncf["cncftools"], "CNCF status dictionary should be available"

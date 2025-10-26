"""Ranking workflow entrypoints."""

from pathlib import Path
from typing import Optional, Sequence

from .collector import RankingCollector, ToolSource
from .scorer import RankingScorer, RankingOutputs, ScoreWeights
from .schema import validate_snapshot, validate_canonical
from .diffs import describe_rank_deltas


def update_rankings(
    *,
    sources: Sequence[ToolSource],
    data_dir: Path,
    weights: Optional[ScoreWeights] = None,
    dry_run: bool = False,
) -> RankingOutputs:
    data_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir = data_dir / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    collector = RankingCollector()
    snapshot = collector.collect_snapshot(list(sources))
    validate_snapshot(snapshot)

    scorer = RankingScorer(weights=weights)
    outputs = scorer.build_outputs(snapshot, data_dir=data_dir, dry_run=dry_run)
    validate_canonical(outputs.canonical)

    if outputs.previous_canonical:
        outputs.diff_summary = describe_rank_deltas(outputs.previous_canonical, outputs.canonical)

    if not dry_run:
        collector.write_snapshot(snapshot, snapshots_dir)
        scorer.persist_outputs(outputs, data_dir)

    return outputs


__all__ = [
    "ScoreWeights",
    "ToolSource",
    "RankingOutputs",
    "update_rankings",
]

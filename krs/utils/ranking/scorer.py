"""Score ranking snapshots and emit canonical payloads."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


@dataclass(frozen=True)
class ScoreWeights:
    popularity: float = 0.35
    recency: float = 0.25
    issue_velocity: float = 0.20
    growth: float = 0.15
    cncf_status: float = 0.05

    def as_dict(self) -> Dict[str, float]:
        return {
            "popularity": self.popularity,
            "recency": self.recency,
            "issue_velocity": self.issue_velocity,
            "growth": self.growth,
            "cncf_status": self.cncf_status,
        }


@dataclass
class RankingOutputs:
    snapshot: Dict[str, Any]
    canonical: Dict[str, Any]
    legacy: Dict[str, Any]
    weights: ScoreWeights
    previous_canonical: Optional[Dict[str, Any]] = None
    diff_summary: Optional[str] = None


class RankingScorer:
    def __init__(self, *, weights: Optional[ScoreWeights] = None):
        self.weights = weights or ScoreWeights()

    def build_outputs(
        self, snapshot: Dict[str, Any], *, data_dir: Path, dry_run: bool = False
    ) -> RankingOutputs:
        tools = snapshot["tools"]
        generated_at = snapshot["metadata"]["generated_at"]
        generated_dt = _parse_ts(generated_at)

        normalized = self._normalise(tools, generated_dt)
        scored = [self._score_tool(tool, norm) for tool, norm in zip(tools, normalized)]

        categories: Dict[str, List[Dict[str, Any]]] = {}
        for entry in scored:
            categories.setdefault(entry["category"], []).append(entry)

        canonical_categories = []
        for category, items in sorted(categories.items()):
            ranked = sorted(items, key=lambda item: item["score"], reverse=True)
            for rank, item in enumerate(ranked, start=1):
                item["rank"] = rank
            canonical_categories.append({"name": category, "tools": ranked})

        legacy = self._build_legacy(canonical_categories)
        canonical = {
            "metadata": snapshot["metadata"],
            "categories": canonical_categories,
            "legacy": legacy,
            "weights": self.weights.as_dict(),
        }

        previous = None
        canonical_path = data_dir / "canonical.json"
        if canonical_path.exists():
            with canonical_path.open("r", encoding="utf-8") as fh:
                previous = json.load(fh)

        return RankingOutputs(
            snapshot=snapshot,
            canonical=canonical,
            legacy=legacy,
            weights=self.weights,
            previous_canonical=previous,
        )

    def persist_outputs(self, outputs: RankingOutputs, data_dir: Path) -> None:
        data_dir.mkdir(parents=True, exist_ok=True)
        canonical_path = data_dir / "canonical.json"
        with canonical_path.open("w", encoding="utf-8") as fh:
            json.dump(outputs.canonical, fh, indent=2, sort_keys=True)

        legacy_root = data_dir.parent
        legacy_root.mkdir(parents=True, exist_ok=True)

        kubetools_path = legacy_root / "kubetools_data.json"
        with kubetools_path.open("w", encoding="utf-8") as fh:
            json.dump(outputs.legacy["kubetools_data"], fh, indent=2, sort_keys=True)

        category_rank_path = legacy_root / "category_rank.json"
        with category_rank_path.open("w", encoding="utf-8") as fh:
            json.dump(outputs.legacy["category_rank"], fh, indent=2, sort_keys=True)

    def _normalise(self, tools: List[Dict[str, Any]], generated: datetime) -> List[Dict[str, float]]:
        pop_vals = [tool["stars"] + tool["forks"] for tool in tools]
        growth_vals = [tool.get("trend_30d_stars", 0) for tool in tools]
        recency_vals = [
            (generated - _parse_ts(tool["last_commit_at"])).days for tool in tools
        ]
        issue_vals = [tool.get("issue_velocity_30d", 0.0) for tool in tools]

        def min_max(values, invert=False):
            values = list(values)
            if not values:
                return []
            min_val = min(values)
            max_val = max(values)
            scores = []
            for val in values:
                if max_val == min_val:
                    score = 0.0
                else:
                    score = (val - min_val) / (max_val - min_val)
                if invert:
                    score = 1.0 - score
                scores.append(round(score, 6))
            return scores

        return [
            {
                "popularity": pop,
                "growth": growth,
                "recency": rec,
                "issue_velocity": round(min(max(issue_vals[idx], 0.0), 1.0), 6),
            }
            for idx, (pop, growth, rec) in enumerate(
                zip(min_max(pop_vals), min_max(growth_vals), min_max(recency_vals, invert=True))
            )
        ]

    def _score_tool(self, tool: Dict[str, Any], normalized: Dict[str, float]) -> Dict[str, Any]:
        cncf_component = tool["score_inputs"].get("cncf", 0.0)
        score = (
            normalized["popularity"] * self.weights.popularity
            + normalized["recency"] * self.weights.recency
            + normalized["issue_velocity"] * self.weights.issue_velocity
            + normalized["growth"] * self.weights.growth
            + cncf_component * self.weights.cncf_status
        )

        merged_inputs = dict(tool["score_inputs"])
        merged_inputs.update(normalized)

        result = dict(tool)
        result["score"] = round(score, 6)
        result["score_inputs"] = merged_inputs
        result["reason"] = self._reason_for(result)
        return result

    def _reason_for(self, tool: Dict[str, Any]) -> str:
        inputs = tool.get("score_inputs", {})
        reasons = []
        if inputs.get("recency", 0) >= 0.7:
            reasons.append("active commits")
        if inputs.get("growth", 0) >= 0.6:
            reasons.append("30-day star growth")
        if inputs.get("issue_velocity", 0) >= 0.5:
            reasons.append("healthy issue closure rate")
        if tool.get("mcp_support"):
            reasons.append("MCP support")
        if tool.get("capabilities"):
            reasons.append(", ".join(tool["capabilities"][:2]))

        return "; ".join(reasons) if reasons else "steady ecosystem signals"

    def _build_legacy(self, categories: List[Dict[str, Any]]) -> Dict[str, Any]:
        kubetools = []
        category_rank: Dict[str, Dict[int, Dict[str, str]]] = {}
        for category in categories:
            formatted = []
            ranks: Dict[int, Dict[str, str]] = {}
            for item in category["tools"]:
                formatted.append(
                    {
                        "name": item["name"],
                        "link": f"https://github.com/{item['repo']}",
                        "githubStars": item.get("stars", 0),
                    }
                )
                ranks[item["rank"]] = {
                    "name": item["name"],
                    "url": f"https://github.com/{item['repo']}",
                }
            kubetools.append({"category": {"name": category["name"]}, "tools": formatted})
            category_rank[category["name"]] = ranks

        return {"kubetools_data": kubetools, "category_rank": category_rank}


__all__ = ["RankingOutputs", "RankingScorer", "ScoreWeights"]

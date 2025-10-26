"""Diff helper for ranking updates."""

from __future__ import annotations

from typing import Dict, List, Tuple


def describe_rank_deltas(previous: Dict, current: Dict, *, max_lines: int = 8) -> str:
    prev_positions = _index(previous)
    curr_positions = _index(current)

    lines: List[str] = []

    for key, entry in curr_positions.items():
        prev_entry = prev_positions.get(key)
        category, tool = key
        if prev_entry is None:
            lines.append(f"{tool} enters {category} at #{entry['rank']} ({entry.get('reason', 'new entry')}).")
            continue
        delta = prev_entry["rank"] - entry["rank"]
        if delta > 0:
            lines.append(
                f"{tool} ↑ {prev_entry['rank']}→{entry['rank']} in {category} "
                f"(score {entry['score']:.2f}; {entry.get('reason', 'momentum')})."
            )
        elif delta < 0:
            lines.append(
                f"{tool} ↓ {prev_entry['rank']}→{entry['rank']} in {category} "
                f"(score {entry['score']:.2f})."
            )

    for key, entry in prev_positions.items():
        if key not in curr_positions:
            category, tool = key
            lines.append(f"{tool} drops out of {category} (previously #{entry['rank']}).")

    if not lines:
        return "No ranking changes detected."
    return "\n".join(lines[:max_lines])


def _index(payload: Dict) -> Dict[Tuple[str, str], Dict]:
    mapping: Dict[Tuple[str, str], Dict] = {}
    for category in payload.get("categories", []):
        name = category.get("name")
        for item in category.get("tools", []):
            mapping[(name, item.get("name"))] = item
    return mapping


__all__ = ["describe_rank_deltas"]

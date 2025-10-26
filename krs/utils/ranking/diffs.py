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


def summarize_repo_diff(previous: Dict, current: Dict, *, limit: int = 5) -> str:
    prev_positions = _index(previous)
    curr_positions = _index(current)

    improvements: List[Tuple[int, str, str, Dict, Dict]] = []
    declines: List[Tuple[int, str, str, Dict, Dict]] = []
    additions: List[Tuple[str, str, Dict]] = []
    removals: List[Tuple[str, str, Dict]] = []

    for (category, tool), entry in curr_positions.items():
        previous_entry = prev_positions.get((category, tool))
        if previous_entry is None:
            additions.append((category, tool, entry))
            continue
        delta = previous_entry["rank"] - entry["rank"]
        if delta > 0:
            improvements.append((delta, category, tool, previous_entry, entry))
        elif delta < 0:
            declines.append((delta, category, tool, previous_entry, entry))

    for (category, tool), entry in prev_positions.items():
        if (category, tool) not in curr_positions:
            removals.append((category, tool, entry))

    improvements.sort(key=lambda item: (-item[0], item[2]))
    declines.sort(key=lambda item: (item[0], item[2]))

    lines: List[str] = []

    for delta, category, tool, prev_entry, entry in improvements[:limit]:
        reason = entry.get("reason") or "momentum"
        lines.append(
            f"- ↑ {tool} ({category}) #{prev_entry['rank']}→#{entry['rank']} – {reason}."
        )

    for delta, category, tool, prev_entry, entry in declines[:limit]:
        reason = entry.get("reason") or "slower signals"
        lines.append(
            f"- ↓ {tool} ({category}) #{prev_entry['rank']}→#{entry['rank']} – {reason}."
        )

    for category, tool, entry in additions[:limit]:
        reason = entry.get("reason") or "new entry"
        lines.append(
            f"- ➕ {tool} ({category}) enters at #{entry['rank']} – {reason}."
        )

    for category, tool, entry in removals[:limit]:
        lines.append(
            f"- ✖ {tool} drops from {category} (was #{entry['rank']})."
        )

    if not lines:
        return "- No ranking changes detected."

    return "\n".join(lines[: limit * 4])


def _index(payload: Dict) -> Dict[Tuple[str, str], Dict]:
    mapping: Dict[Tuple[str, str], Dict] = {}
    for category in payload.get("categories", []):
        name = category.get("name")
        for item in category.get("tools", []):
            mapping[(name, item.get("name"))] = item
    return mapping


__all__ = ["describe_rank_deltas", "summarize_repo_diff"]

from krs.utils.ranking.diffs import describe_rank_deltas, summarize_repo_diff


def make_payload(rankings):
    return {
        "categories": [
            {
                "name": category,
                "tools": [
                    {
                        "name": tool[0],
                        "rank": tool[1],
                        "score": tool[2],
                        "reason": tool[3],
                    }
                    for tool in tools
                ],
            }
            for category, tools in rankings.items()
        ]
    }


def test_describe_rank_deltas_reports_improvement():
    previous = make_payload({
        "logging": [
            ("loki", 3, 0.45, "steady"),
            ("promtail", 1, 0.60, "steady"),
        ]
    })
    current = make_payload({
        "logging": [
            ("loki", 1, 0.72, "active commits"),
            ("promtail", 2, 0.50, "steady"),
        ]
    })

    summary = describe_rank_deltas(previous, current)

    assert "loki" in summary
    assert "3→1" in summary
    assert "logging" in summary


def test_describe_rank_deltas_handles_new_entries():
    previous = make_payload({"logging": [("loki", 1, 0.7, "steady")]})
    current = make_payload({
        "logging": [
            ("loki", 1, 0.7, "steady"),
            ("vector", 2, 0.5, "growth"),
        ],
        "security": [("falco", 1, 0.8, "healthy")],
    })

    summary = describe_rank_deltas(previous, current)

    assert "vector" in summary
    assert "enters" in summary


def test_summarize_repo_diff_outputs_markdown_bullets():
    previous = make_payload({
        "observability": [
            ("loki", 3, 0.45, "steady"),
            ("prometheus", 1, 0.80, "trusted"),
        ],
        "gitops": [
            ("argo-cd", 1, 0.92, "active"),
        ],
    })

    current = make_payload({
        "observability": [
            ("loki", 1, 0.72, "active commits"),
            ("prometheus", 2, 0.78, "steady"),
            ("vector", 3, 0.50, "growth"),
        ],
        "gitops": [
            ("argo-cd", 2, 0.85, "steady"),
            ("flux", 1, 0.88, "momentum"),
        ],
    })

    summary = summarize_repo_diff(previous, current)

    lines = [line.strip() for line in summary.splitlines() if line.strip()]

    assert lines[0].startswith("- ↑ loki (observability)")
    assert any(line.startswith("- ↓ argo-cd") for line in lines)
    assert any("flux" in line and "➕" in line for line in lines)

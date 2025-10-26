from krs.utils.ranking.diffs import describe_rank_deltas


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

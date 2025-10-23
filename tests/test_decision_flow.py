from graph.nodes.decision_flow_controller import decision_flow_controller


def test_decision_flow_selects_best_candidate() -> None:
    state = {
        "countries": ["USA"],
        "rules": {"min_evidence": 2},
        "market": {
            "USA": {
                "market_overview": {"cagr_pct": 8.0},
                "barriers": {"fdi_restriction": "low"},
                "evidence": [{"fact": "", "source_url": ""}, {"fact": "", "source_url": ""}],
            }
        },
        "strategies": {
            "USA": {
                "candidates": [
                    {"mode": "direct_investment", "fit": 70},
                    {"mode": "joint_venture", "fit": 60},
                ]
            }
        },
    }

    result = decision_flow_controller(state)
    decision = result["decision"]["USA"]
    assert decision["recommended"] == "direct_investment"
    assert len(decision["rationale"]) >= 2


def test_decision_flow_flags_low_evidence() -> None:
    state = {
        "countries": ["MNG"],
        "rules": {"min_evidence": 3},
        "market": {
            "MNG": {
                "market_overview": {"cagr_pct": 5.0},
                "barriers": {"fdi_restriction": "medium"},
                "evidence": [{"fact": "", "source_url": ""}],
            }
        },
        "strategies": {
            "MNG": {
                "candidates": [
                    {"mode": "joint_venture", "fit": 65},
                ]
            }
        },
    }

    result = decision_flow_controller(state)
    assert result.get("trigger_retry")
    assert "MNG" in result.get("retry_countries", [])

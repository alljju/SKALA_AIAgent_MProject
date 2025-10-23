from graph.nodes.insight_integrator import insight_integrator


def test_insight_integrator_collects_evidence() -> None:
    state = {
        "countries": ["USA"],
        "interim": {
            "market": {
                "USA": {
                    "market": {
                        "segment": "logistics",
                        "market_size_usd": 2_000_000_000,
                        "cagr_pct": 12.0,
                        "period": "2024-2029",
                        "aux_indicators": {},
                    },
                    "evidence": [
                        {"fact": "Market expected to grow", "source_url": "https://example.com/market"}
                    ],
                }
            },
            "competition": {
                "USA": {
                    "competitors": [
                        {"name": "Firm A", "share_pct": 20.0, "notes": None, "source_url": "https://example.com/a"}
                    ],
                    "evidence": [
                        {"fact": "Firm A dominates", "source_url": "https://example.com/a"}
                    ],
                }
            },
            "barriers": {
                "USA": {
                    "fdi_restriction": "low",
                    "data_localization": "none",
                    "tax_regime": {},
                    "labor_regulation": {},
                    "other": [],
                }
            },
            "law": {
                "USA": {
                    "evidence": [
                        {"fact": "FDI open", "source_url": "https://example.com/law"}
                    ]
                }
            },
        },
    }

    result = insight_integrator(state)
    insight = result["insights"][0]
    assert insight["country"] == "USA"
    assert len(insight["evidence"]) == 3
    assert insight["scores"]["attractiveness"] > 0

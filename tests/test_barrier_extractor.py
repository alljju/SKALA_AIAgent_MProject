from graph.nodes.barrier_extractor import barrier_extractor


def test_barrier_extractor_normalizes_keys() -> None:
    state = {
        "interim": {
            "law": {
                "Mongolia": {
                    "barriers": {
                        "fdi_restriction": "medium",
                        "data_localization": "sectoral",
                        "tax_regime": {"corp_tax_pct": 25},
                        "labor_regulation": {"overtime_limit": 20},
                        "other": ["custom clearance"],
                    }
                }
            }
        }
    }

    result = barrier_extractor(state)
    barriers = result["interim"]["barriers"]["Mongolia"]
    assert barriers["fdi_restriction"] == "medium"
    assert barriers["data_localization"] == "sectoral"
    assert barriers["tax_regime"]["corp_tax_pct"] == 25
    assert barriers["labor_regulation"]["overtime_limit"] == 20
    assert barriers["other"] == ["custom clearance"]

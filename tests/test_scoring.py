from tools.scoring import score_country, score_entry_modes


def test_score_country_uses_market_size() -> None:
    barriers = {"fdi_restriction": "low"}
    market = {"market_size_usd": 1_000_000_000, "cagr_pct": 10.0}
    competitors = []
    scores = score_country(barriers, market, competitors)
    assert scores["attractiveness"] > 0
    assert scores["risk"] < 30


def test_score_entry_modes_penalizes_direct_with_restrictions() -> None:
    barriers = {"fdi_restriction": "high", "data_localization": "broad", "other": ["equity cap"]}
    market = {"cagr_pct": 12.0}
    firm = {"control_pref": "high", "risk_appetite": "medium"}
    rules = {"cagr_good": 8.0}

    modes = score_entry_modes(barriers, market, firm, rules)
    direct = next(mode for mode in modes if mode["mode"] == "direct_investment")
    jv = next(mode for mode in modes if mode["mode"] == "joint_venture")

    assert direct["fit"] < jv["fit"]
    assert any("equity" in reason for reason in direct["cons"])

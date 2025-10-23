from tools.parsing import extract_numbers


def test_extract_numbers_parses_usd_and_cagr() -> None:
    text = "The market reached $1.5 billion in 2023 and will grow at 12.5% CAGR through 2028."
    result = extract_numbers(text)
    assert result["usd"] == 1_500_000_000.0
    assert result["cagr_pct"] == 12.5
    assert result["period"] == "2023-2028"

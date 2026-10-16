import json
from pathlib import Path

from src.feature_extraction import extract_features

SAMPLES = Path(__file__).resolve().parents[1] / "data" / "samples"


def _load(name: str) -> dict:
    return json.loads((SAMPLES / name).read_text())


def test_good_profile_has_positive_income():
    feats = extract_features(_load("sample_good.json"))
    assert feats["income_mean_3m"] > 0
    assert feats["income_cv_3m"] < 1.0


def test_bad_profile_has_dpd():
    feats = extract_features(_load("sample_bad.json"))
    assert feats["dpd_mean"] > 0
    assert feats["punctuality_index"] < 1.0


def test_all_expected_keys_present():
    feats = extract_features(_load("sample_medium.json"))
    for k in [
        "income_mean_3m", "income_median_6m", "income_std_12m", "income_cv_3m",
        "overdraft_freq", "overdraft_ratio", "essential_ratio", "eom_balance_mean",
        "dpd_mean", "punctuality_index", "min_payment_ratio",
    ]:
        assert k in feats, f"faltando feature {k}"

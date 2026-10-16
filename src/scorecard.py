from __future__ import annotations

from dataclasses import dataclass

FEATURE_DIRECTIONS = {
    "income_mean_3m": "higher_is_better",
    "income_median_6m": "higher_is_better",
    "income_std_12m": "lower_is_better",
    "income_cv_3m": "lower_is_better",
    "overdraft_freq": "lower_is_better",
    "overdraft_ratio": "lower_is_better",
    "essential_ratio": "lower_is_better",
    "eom_balance_mean": "higher_is_better",
    "dpd_mean": "lower_is_better",
    "punctuality_index": "higher_is_better",
    "min_payment_ratio": "lower_is_better",
}

FEATURE_WEIGHTS = {
    "income_mean_3m": 0.22,
    "income_cv_3m": 0.12,
    "overdraft_freq": 0.12,
    "overdraft_ratio": 0.08,
    "essential_ratio": 0.08,
    "eom_balance_mean": 0.10,
    "dpd_mean": 0.15,
    "punctuality_index": 0.08,
    "min_payment_ratio": 0.05,
}

REFERENCE = {
    "income_mean_3m": (0.0, 10000.0),
    "income_median_6m": (0.0, 10000.0),
    "income_std_12m": (0.0, 5000.0),
    "income_cv_3m": (0.0, 1.5),
    "overdraft_freq": (0.0, 0.30),
    "overdraft_ratio": (0.0, 0.30),
    "essential_ratio": (0.0, 1.0),
    "eom_balance_mean": (0.0, 8000.0),
    "dpd_mean": (0.0, 30.0),
    "punctuality_index": (0.0, 1.0),
    "min_payment_ratio": (0.0, 1.0),
}


@dataclass
class ScoreResult:
    score: int
    pd: float
    contributions: dict[str, float]


def _normalize(value: float, direction: str, ref_low: float, ref_high: float) -> float:
    if ref_high == ref_low:
        return 0.5
    x = (value - ref_low) / (ref_high - ref_low)
    x = max(0.0, min(1.0, x))
    return x if direction == "higher_is_better" else 1.0 - x


def compute_pd(features: dict[str, float]) -> float:
    total_weight = sum(FEATURE_WEIGHTS.values())
    score_unit = 0.0
    for feat, weight in FEATURE_WEIGHTS.items():
        direction = FEATURE_DIRECTIONS[feat]
        low, high = REFERENCE[feat]
        norm = _normalize(features.get(feat, 0.0), direction, low, high)
        score_unit += norm * weight
    score_unit /= total_weight
    pd = 0.30 * (1 - score_unit) + 0.01
    return float(round(min(max(pd, 0.01), 0.50), 4))


def compute_score(features: dict[str, float]) -> ScoreResult:
    contributions: dict[str, float] = {}
    total_weight = sum(FEATURE_WEIGHTS.values())
    score_unit = 0.0
    for feat, weight in FEATURE_WEIGHTS.items():
        direction = FEATURE_DIRECTIONS[feat]
        low, high = REFERENCE[feat]
        norm = _normalize(features.get(feat, 0.0), direction, low, high)
        contrib = norm * weight
        contributions[feat] = round(contrib, 4)
        score_unit += contrib
    score_unit /= total_weight

    # Score calibration: 200 (pior) a 1000 (melhor)
    # score_unit ∈ [0,1] é mapeado linearmente
    # Garante separação clara entre APPROVED/MANUAL/REJECTED
    score = 200 + score_unit * 800
    score_int = int(max(0, min(1000, round(score))))

    pd_value = compute_pd(features)
    return ScoreResult(score=score_int, pd=pd_value, contributions=contributions)


def top_factors(contributions: dict[str, float], n: int = 3) -> list[str]:
    ordered = sorted(contributions.items(), key=lambda kv: kv[1], reverse=True)
    return [k for k, _ in ordered[:n]]

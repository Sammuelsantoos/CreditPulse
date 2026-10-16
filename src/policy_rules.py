from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from api.schemas import DecisionEnum
from src.scorecard import ScoreResult


MIN_INCOME = 800.0
MAX_DPD = 30.0


@dataclass
class PolicyDecision:
    decision: DecisionEnum
    approved_limit: float
    reason_codes: list[str]


def apply_knockout(payload: dict[str, Any], features: dict[str, float]) -> list[str]:
    reasons: list[str] = []
    applicant = payload.get("applicant", {})

    if applicant.get("has_restriction"):
        reasons.append("RESTRICAO_CPF")

    if features.get("income_mean_3m", 0.0) < MIN_INCOME:
        reasons.append("RENDA_INSUFICIENTE")

    if features.get("dpd_mean", 0.0) > MAX_DPD:
        reasons.append("ATRASO_GRAVE")

    return reasons


def compute_limit(score: int, features: dict[str, float]) -> float:
    income = features.get("income_mean_3m", 0.0)
    if income <= 0:
        return 0.0
    if score > 750:
        factor = 1.5
    elif score >= 550:
        factor = 0.8
    else:
        factor = 0.3
    return round(income * factor, 2)


def decide(
    payload: dict[str, Any],
    features: dict[str, float],
    score_result: ScoreResult,
) -> PolicyDecision:
    knockout = apply_knockout(payload, features)
    if knockout:
        return PolicyDecision(
            decision=DecisionEnum.REJECTED,
            approved_limit=0.0,
            reason_codes=knockout,
        )

    score = score_result.score
    limit = compute_limit(score, features)

    if score > 750:
        return PolicyDecision(DecisionEnum.APPROVED, limit, ["SCORE_ALTO"])
    if score >= 550:
        return PolicyDecision(DecisionEnum.MANUAL_REVIEW, limit, ["SCORE_MEDIO"])
    return PolicyDecision(DecisionEnum.REJECTED, 0.0, ["SCORE_BAIXO"])

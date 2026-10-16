from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from api.schemas import (
    CreditDecisionResponse,
    OpenFinancePayload,
)
from src.feature_extraction import extract_features
from src.policy_rules import decide
from src.scorecard import compute_score, top_factors

app = FastAPI(
    title="CreditPulse Decision Engine",
    description="Motor de decisão de crédito com Open Finance Scoring",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/credit-decision", response_model=CreditDecisionResponse)
def credit_decision(payload: OpenFinancePayload) -> CreditDecisionResponse:
    try:
        payload_dict = payload.model_dump(mode="json")
        features = extract_features(payload_dict)
        score_result = compute_score(features)
        policy = decide(payload_dict, features, score_result)
        factors = top_factors(score_result.contributions, n=3)

        return CreditDecisionResponse(
            decision=policy.decision,
            score=score_result.score,
            probability_of_default=score_result.pd,
            approved_limit=policy.approved_limit,
            top_factors=factors,
            reason_codes=policy.reason_codes,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.exception_handler(ValueError)
def value_error_handler(_, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})

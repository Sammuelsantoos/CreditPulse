from __future__ import annotations

from datetime import timedelta
from typing import Any

import polars as pl


CREDIT_TYPES = {"CREDIT", "PIX_IN", "TED_IN"}
DEBIT_TYPES = {"DEBIT", "PIX_OUT", "TED_OUT", "CARD_PAYMENT", "OVERDRAFT"}


def _flatten_transactions(payload: dict[str, Any]) -> pl.DataFrame:
    rows = []
    for stmt in payload.get("statements", []):
        for tx in stmt.get("transactions", []):
            rows.append({
                "date": tx["date"],
                "amount": float(tx["amount"]),
                "type": tx["type"],
                "balance_after": float(tx.get("balance_after") or 0.0),
                "bank": stmt.get("bank_name", "unknown"),
            })
    if not rows:
        return pl.DataFrame(schema={
            "date": pl.Utf8,
            "amount": pl.Float64,
            "type": pl.Utf8,
            "balance_after": pl.Float64,
            "bank": pl.Utf8,
        })
    df = pl.DataFrame(rows)
    df = df.with_columns(pl.col("date").str.to_date())
    return df


def income_features(
    df: pl.DataFrame,
    windows: tuple[int, ...] = (3, 6, 12),
) -> dict[str, float]:
    feats: dict[str, float] = {}
    if df.is_empty():
        for w in windows:
            feats[f"income_mean_{w}m"] = 0.0
            feats[f"income_median_{w}m"] = 0.0
            feats[f"income_std_{w}m"] = 0.0
            feats[f"income_cv_{w}m"] = 0.0
        return feats

    credits = df.filter(pl.col("type").is_in(list(CREDIT_TYPES)))
    today = df["date"].max()

    for w in windows:
        cutoff = today - timedelta(days=30 * w)
        wdf = credits.filter(pl.col("date") >= cutoff)
        if wdf.is_empty():
            feats[f"income_mean_{w}m"] = 0.0
            feats[f"income_median_{w}m"] = 0.0
            feats[f"income_std_{w}m"] = 0.0
            feats[f"income_cv_{w}m"] = 0.0
            continue
        mean = float(wdf["amount"].mean())
        median = float(wdf["amount"].median())
        std = float(wdf["amount"].std() or 0.0)
        feats[f"income_mean_{w}m"] = round(mean, 2)
        feats[f"income_median_{w}m"] = round(median, 2)
        feats[f"income_std_{w}m"] = round(std, 2)
        feats[f"income_cv_{w}m"] = round(std / mean, 4) if mean > 0 else 0.0

    return feats


def extract_features(payload: dict[str, Any]) -> dict[str, float]:
    df = _flatten_transactions(payload)
    features: dict[str, float] = {}
    features.update(income_features(df))
    return features

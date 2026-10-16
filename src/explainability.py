from __future__ import annotations

from typing import Any

import numpy as np
import shap
from sklearn.ensemble import GradientBoostingClassifier

from src.scorecard import FEATURE_WEIGHTS

FEATURE_ORDER = list(FEATURE_WEIGHTS.keys())


def _synthetic_training_data(
    n: int = 500, seed: int = 42
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 1, (n, len(FEATURE_ORDER)))
    logits = x @ rng.normal(0.6, 0.3, len(FEATURE_ORDER))
    y = (logits > 0).astype(int)
    return x, y


def train_surrogate() -> tuple[GradientBoostingClassifier, shap.TreeExplainer]:
    x, y = _synthetic_training_data()
    clf = GradientBoostingClassifier(n_estimators=80, max_depth=3, random_state=42)
    clf.fit(x, y)
    explainer = shap.TreeExplainer(clf)
    return clf, explainer


def explain_features(features: dict[str, float]) -> list[dict[str, Any]]:
    clf, explainer = train_surrogate()
    x = np.array([[features.get(k, 0.0) for k in FEATURE_ORDER]], dtype=float)
    shap_values = explainer.shap_values(x)
    values = shap_values[0] if isinstance(shap_values, list) else shap_values[0]

    pairs = sorted(
        zip(FEATURE_ORDER, values.tolist(), strict=False),
        key=lambda kv: abs(kv[1]),
        reverse=True,
    )
    return [{"feature": f, "shap": round(v, 4)} for f, v in pairs]


if __name__ == "__main__":
    demo = {
        "income_mean_3m": 5200.0,
        "income_cv_3m": 0.15,
        "overdraft_freq": 0.02,
        "dpd_mean": 0.0,
    }
    for row in explain_features(demo):
        print(row)

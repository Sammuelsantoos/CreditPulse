from src.explainability import FEATURE_ORDER, explain_features


def test_explain_features_returns_all_features():
    feats = {k: 1.0 for k in FEATURE_ORDER}
    result = explain_features(feats)
    assert len(result) == len(FEATURE_ORDER)
    assert all("feature" in r and "shap" in r for r in result)


def test_explain_features_sorted_by_abs_shap():
    feats = {k: float(i) for i, k in enumerate(FEATURE_ORDER)}
    result = explain_features(feats)
    abs_values = [abs(r["shap"]) for r in result]
    assert abs_values == sorted(abs_values, reverse=True)

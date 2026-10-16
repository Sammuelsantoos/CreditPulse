from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report


def build_reference(n: int = 1000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "score": rng.normal(700, 80, n),
        "pd": rng.uniform(0.01, 0.25, n),
        "income_mean_3m": rng.normal(5000, 1500, n).clip(500, None),
        "dpd_mean": rng.gamma(2, 2, n),
    })


def build_current(n: int = 1000, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "score": rng.normal(660, 95, n),
        "pd": rng.uniform(0.02, 0.32, n),
        "income_mean_3m": rng.normal(4300, 1700, n).clip(400, None),
        "dpd_mean": rng.gamma(2.5, 3, n),
    })


def generate_report(out_dir: str | Path = "reports") -> Path:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    reference = build_reference()
    current = build_current()

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference, current_data=current)

    html_path = out_path / "drift_report.html"
    report.save_html(str(html_path))
    return html_path

if __name__ == "__main__":
    path = generate_report()
    print(f"Relatorio gerado em: {path}")

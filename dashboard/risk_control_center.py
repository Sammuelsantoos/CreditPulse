from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.feature_extraction import extract_features  # noqa: E402
from src.policy_rules import decide  # noqa: E402
from src.scorecard import compute_score, top_factors  # noqa: E402

st.set_page_config(
    page_title="CreditPulse – Risk Control Center",
    page_icon="💳",
    layout="wide",
)

SAMPLES_DIR = Path(__file__).resolve().parents[1] / "data" / "samples"


@st.cache_data(show_spinner=False)
def load_sample(name: str) -> dict:
    return json.loads((SAMPLES_DIR / name).read_text())


def run_pipeline(payload: dict) -> dict:
    features = extract_features(payload)
    score_result = compute_score(features)
    policy = decide(payload, features, score_result)
    return {
        "score": score_result.score,
        "pd": score_result.pd,
        "decision": policy.decision.value,
        "limit": policy.approved_limit,
        "reasons": policy.reason_codes,
        "top_factors": top_factors(score_result.contributions, n=5),
        "contributions": score_result.contributions,
        "features": features,
    }


@st.cache_data(show_spinner=False)
def build_vintage_data(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    cohorts = pd.date_range(end=date.today(), periods=12, freq="MS")
    rows = []
    for cohort in cohorts:
        n = int(rng.integers(80, 200))
        base_dpd = rng.uniform(0.02, 0.10)
        for m in range(0, 7):
            dpd = min(base_dpd * (1.25 ** m), 0.6)
            rows.append({
                "cohort": cohort.strftime("%Y-%m"),
                "months_on_book": m,
                "dpd_rate": round(dpd, 4),
                "n_loans": n,
            })
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def build_score_distribution(seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    good = rng.normal(720, 80, 800)
    bad = rng.normal(560, 90, 400)
    scores = np.clip(np.concatenate([good, bad]), 0, 1000).astype(int)
    labels = ["Bom"] * 800 + ["Mau"] * 400
    return pd.DataFrame({"score": scores, "target": labels})


st.title("💳 CreditPulse – Risk Control Center")
st.caption("Open Finance Scoring & Decision Engine · Monitoramento de safra, scores e decisões")

tab_overview, tab_simulate, tab_vintage, tab_drift = st.tabs(
    ["📊 Visão Executiva", "🧪 Simulador de Decisão", "📈 Vintage Analysis", "🌊 Drift"]
)

with tab_overview:
    st.subheader("Visão Executiva de Aprovação")

    samples = {
        "Bom": load_sample("sample_good.json"),
        "Médio": load_sample("sample_medium.json"),
        "Ruim": load_sample("sample_bad.json"),
    }
    results = {k: run_pipeline(v) for k, v in samples.items()}

    cols = st.columns(4)
    cols[0].metric("Total de propostas", len(results))
    approved = sum(1 for r in results.values() if r["decision"] == "APPROVED")
    cols[1].metric("Taxa de aprovação", f"{approved / len(results):.0%}")
    avg_score = np.mean([r["score"] for r in results.values()])
    cols[2].metric("Score médio", f"{avg_score:.0f}")
    avg_limit = np.mean([r["limit"] for r in results.values()])
    cols[3].metric("Ticket médio aprovado", f"R$ {avg_limit:,.2f}")

    df_res = pd.DataFrame([
        {
            "Perfil": k,
            "Decisão": v["decision"],
            "Score": v["score"],
            "PD": v["pd"],
            "Limite (R$)": v["limit"],
            "Top Fator": v["top_factors"][0] if v["top_factors"] else "-",
        }
        for k, v in results.items()
    ])
    st.dataframe(df_res, use_container_width=True, hide_index=True)

    dist = build_score_distribution()
    fig = px.histogram(
        dist, x="score", color="target", nbins=40,
        title="Distribuição de Score (Bons vs Maus)",
        color_discrete_map={"Bom": "#2ecc71", "Mau": "#e74c3c"},
        barmode="overlay", opacity=0.7,
    )
    fig.update_layout(xaxis_title="Score", yaxis_title="Clientes")
    st.plotly_chart(fig, use_container_width=True)

with tab_simulate:
    st.subheader("Simulador de Decisão em Tempo Real")
    profile = st.selectbox("Selecione um perfil de sample", ["good", "medium", "bad"])
    payload = load_sample(f"sample_{profile}.json")

    with st.expander("📄 Payload Open Finance (input)"):
        st.json(payload)

    if st.button("▶️ Rodar decisão", type="primary"):
        out = run_pipeline(payload)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Decisão", out["decision"])
        c2.metric("Score", out["score"])
        c3.metric("PD", f"{out['pd']:.2%}")
        c4.metric("Limite proposto", f"R$ {out['limit']:,.2f}")

        st.markdown("**Fatores principais (contribuições)**")
        contrib = pd.DataFrame(
            sorted(out["contributions"].items(), key=lambda x: x[1], reverse=True),
            columns=["Feature", "Contribuição"],
        )
        fig_c = px.bar(
            contrib, x="Contribuição", y="Feature", orientation="h",
            color="Contribuição", color_continuous_scale="Blugrn",
        )
        fig_c.update_layout(yaxis={"autorange": "reversed"}, height=350)
        st.plotly_chart(fig_c, use_container_width=True)

        st.markdown("**Features calculadas**")
        st.dataframe(
            pd.DataFrame([out["features"]]).T.rename(columns={0: "Valor"}),
            use_container_width=True,
        )

        if out["reasons"]:
            st.warning(f"Reason codes: {', '.join(out['reasons'])}")

with tab_vintage:
    st.subheader("Vintage Analysis – Inadimplência acumulada por safra")
    vintage = build_vintage_data()

    fig_v = px.line(
        vintage, x="months_on_book", y="dpd_rate", color="cohort",
        markers=True, title="DPD acumulado por safra (meses pós-concessão)",
    )
    fig_v.update_layout(
        xaxis_title="Meses desde a concessão",
        yaxis_title="Taxa de inadimplência (DPD 30+)",
        yaxis_tickformat=".1%",
    )
    st.plotly_chart(fig_v, use_container_width=True)

    pivot = vintage.pivot_table(
        index="cohort", columns="months_on_book", values="dpd_rate"
    )
    st.markdown("**Heatmap de safras**")
    fig_h = go.Figure(data=go.Heatmap(
        z=pivot.values, x=pivot.columns, y=pivot.index,
        colorscale="Reds", texttemplate="%{z:.1%}",
    ))
    fig_h.update_layout(height=500)
    st.plotly_chart(fig_h, use_container_width=True)

with tab_drift:
    st.subheader("Data Drift – Comparação de safras")
    rng = np.random.default_rng(3)
    ref = pd.DataFrame({"score": rng.normal(700, 80, 1000)})
    cur = pd.DataFrame({"score": rng.normal(660, 95, 1000)})

    fig_d = go.Figure()
    fig_d.add_trace(go.Histogram(x=ref["score"], name="Referência", opacity=0.6,
                                 marker_color="#3498db", nbinsx=40))
    fig_d.add_trace(go.Histogram(x=cur["score"], name="Atual", opacity=0.6,
                                 marker_color="#e67e22", nbinsx=40))
    fig_d.update_layout(barmode="overlay", title="Distribuição do Score – Ref vs Atual")
    st.plotly_chart(fig_d, use_container_width=True)

    bins = np.linspace(0, 1000, 21)
    ref_pct = np.histogram(ref["score"], bins=bins)[0] / len(ref)
    cur_pct = np.histogram(cur["score"], bins=bins)[0] / len(cur)
    ref_pct = np.where(ref_pct == 0, 1e-6, ref_pct)
    cur_pct = np.where(cur_pct == 0, 1e-6, cur_pct)
    psi = float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))

    if psi < 0.1:
        st.success(f"PSI = {psi:.4f} → sem drift relevante")
    elif psi < 0.25:
        st.warning(f"PSI = {psi:.4f} → drift moderado (monitorar)")
    else:
        st.error(f"PSI = {psi:.4f} → drift severo (recalibrar modelo)")

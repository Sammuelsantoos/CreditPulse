# 💳 CreditPulse – Open Finance Scoring & Decision Engine

Motor de decisão de crédito que consome dados de **Open Finance**
(extratos bancários e faturas em JSON), calcula features transacionais,
gera um **Score de Crédito Alternativo (0–1000)**, estima a
**Probabilidade de Default (PD)** e automatiza a decisão de concessão
(**Aprovação / Reprovação / Análise Manual**).

## 🎯 Objetivo

Avaliar pessoas **unbanked** ou sem histórico tradicional usando dados
transacionais descentralizados (Open Finance).

## 🧱 Stack

| Camada | Tecnologias |
|---|---|
| Linguagem | Python 3.11+, Docker |
| Data Processing | Polars, Pandas, NumPy |
| ML & Stats | Scikit-learn, SciPy, Statsmodels |
| Explainability | SHAP, Evidently AI |
| API | FastAPI, Pydantic |
| Dashboard | Streamlit, Plotly |
| CI/CD | GitHub Actions, Ruff, Pytest |

## 🏗️ Arquitetura

    [ JSON Open Finance ] → [ Feature Extraction (Polars) ] → [ Scorecard + PD ]
                                     │
                                     ▼
                        [ Policy Engine (Knockout + Limite) ]
                                     │
                                     ▼
                        [ API / Dashboard / Monitoramento ]

## 🚀 Como rodar

### Local

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python data/samples/generate_samples.py
    uvicorn api.app:app --reload --port 8000
    streamlit run dashboard/risk_control_center.py

### Docker

    docker compose up --build
    # API:       http://localhost:8000
    # Dashboard: http://localhost:8501

## 🔌 Endpoint principal

POST /v1/credit-decision

Payload: ver data/samples/sample_good.json.

Resposta:

    {
      "decision": "APPROVED",
      "score": 824,
      "probability_of_default": 0.0758,
      "approved_limit": 9115.4,
      "top_factors": ["dpd_mean", "income_mean_3m", "overdraft_freq"],
      "reason_codes": ["SCORE_ALTO"]
    }

## 🧪 Testes

    pytest tests/ -v
    ruff check .

## 📊 Métricas de crédito suportadas

- Gini / ROC-AUC
- KS (Kolmogorov-Smirnov)
- PSI (Population Stability Index)
- WoE / IV
- Vintage Analysis

## 🌳 Estratégia de Branches

- main: código estável (releases)
- develop: integração contínua dos cards
- feature/cp-XXX-*: uma branch por card do sprint
- chore/cp-XXX-*: tarefas de infraestrutura
- test/cp-XXX-*: branches dedicadas a testes
- fix/cp-XXX-*: correções

Cada card é desenvolvido em sua própria branch e mergeado na develop
via --no-ff, preservando o histórico visual do sprint.

## 📁 Estrutura

    creditpulse-decision-engine/
    ├── api/                  # FastAPI + schemas Pydantic
    ├── dashboard/            # Streamlit
    ├── data/samples/         # JSONs sintéticos de Open Finance
    ├── notebooks/            # EDA, WoE/IV, calibração, drift
    ├── src/                  # Núcleo (features, scorecard, policy)
    ├── tests/                # Pytest
    ├── Dockerfile
    ├── docker-compose.yml
    ├── pyproject.toml
    └── requirements.txt

## 📜 Licença

MIT

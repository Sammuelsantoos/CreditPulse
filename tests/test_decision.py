import json
from pathlib import Path

from fastapi.testclient import TestClient

from api.app import app

client = TestClient(app)
SAMPLES = Path(__file__).resolve().parents[1] / "data" / "samples"


def _load(name: str) -> dict:
    return json.loads((SAMPLES / name).read_text())


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_good_profile_approved():
    r = client.post("/v1/credit-decision", json=_load("sample_good.json"))
    assert r.status_code == 200
    body = r.json()
    assert body["decision"] in {"APPROVED", "MANUAL_REVIEW"}
    assert 0 <= body["score"] <= 1000
    assert body["approved_limit"] >= 0


def test_bad_profile_rejected():
    r = client.post("/v1/credit-decision", json=_load("sample_bad.json"))
    assert r.status_code == 200
    body = r.json()
    assert body["decision"] == "REJECTED"
    assert (
        "RESTRICAO_CPF" in body["reason_codes"]
        or "ATRASO_GRAVE" in body["reason_codes"]
    )


def test_invalid_payload():
    r = client.post("/v1/credit-decision", json={"applicant": {}})
    assert r.status_code == 422

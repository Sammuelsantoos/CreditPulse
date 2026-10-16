import json
import random
from datetime import date, timedelta
from pathlib import Path

OUT_DIR = Path(__file__).parent


def gen_transactions(n: int, base_income: float) -> list[dict]:
    txs = []
    today = date.today()
    for i in range(n):
        d = today - timedelta(days=i)
        if random.random() < 0.15:
            txs.append({
                "date": d.isoformat(),
                "amount": round(base_income + random.uniform(-300, 300), 2),
                "type": "PIX_IN",
                "description": "Salário/PIX recebido",
                "balance_after": round(random.uniform(500, 5000), 2),
            })
        else:
            txs.append({
                "date": d.isoformat(),
                "amount": -round(random.uniform(20, 400), 2),
                "type": random.choice(["DEBIT", "PIX_OUT", "CARD_PAYMENT"]),
                "description": "Consumo",
                "balance_after": round(random.uniform(100, 3000), 2),
            })
    return txs


def build_payload(profile: str) -> dict:
    if profile == "good":
        income = 6000.0
        has_restriction = False
        dpd = 0
    elif profile == "medium":
        income = 3200.0
        has_restriction = False
        dpd = random.randint(1, 5)
    else:
        income = 1500.0
        has_restriction = True
        dpd = random.randint(15, 60)

    return {
        "applicant": {
            "cpf": f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}",
            "name": f"Cliente {profile}",
            "birth_date": "1990-05-12",
            "monthly_income_declared": income,
            "has_restriction": has_restriction,
        },
        "statements": [{
            "bank_name": "Banco Exemplo",
            "account_type": "CHECKING",
            "transactions": gen_transactions(90, income),
        }],
        "invoices": [{
            "bank_name": "Banco Exemplo",
            "due_date": date.today().isoformat(),
            "total_amount": round(income * 0.35, 2),
            "minimum_payment": round(income * 0.10, 2),
            "paid_amount": round(income * 0.35, 2) if profile == "good" else round(income * 0.10, 2),
            "days_past_due": dpd,
        }],
    }


if __name__ == "__main__":
    for profile in ["good", "medium", "bad"]:
        payload = build_payload(profile)
        (OUT_DIR / f"sample_{profile}.json").write_text(json.dumps(payload, indent=2))
        print(f"Gerado sample_{profile}.json")

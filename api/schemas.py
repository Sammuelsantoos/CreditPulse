from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class TransactionType(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    PIX_IN = "PIX_IN"
    PIX_OUT = "PIX_OUT"
    TED_IN = "TED_IN"
    TED_OUT = "TED_OUT"
    CARD_PAYMENT = "CARD_PAYMENT"
    OVERDRAFT = "OVERDRAFT"


class Transaction(BaseModel):
    date: date
    amount: float = Field(..., description="Valor em BRL (positivo=credito, negativo=debito)")
    type: TransactionType
    description: Optional[str] = None
    balance_after: Optional[float] = None


class BankStatement(BaseModel):
    bank_name: str
    account_type: str = Field(..., description="CHECKING | SAVINGS")
    transactions: List[Transaction]

    @field_validator("transactions")
    @classmethod
    def at_least_one_tx(cls, v: List[Transaction]) -> List[Transaction]:
        if not v:
            raise ValueError("Transacoes nao podem ser vazias")
        return v


class CreditCardInvoice(BaseModel):
    bank_name: str
    due_date: date
    total_amount: float
    minimum_payment: float
    paid_amount: float
    days_past_due: int = 0


class ApplicantProfile(BaseModel):
    cpf: str
    name: str
    birth_date: date
    monthly_income_declared: Optional[float] = None
    has_restriction: bool = False


class OpenFinancePayload(BaseModel):
    applicant: ApplicantProfile
    statements: List[BankStatement]
    invoices: List[CreditCardInvoice] = []


class DecisionEnum(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class CreditDecisionResponse(BaseModel):
    decision: DecisionEnum
    score: int
    probability_of_default: float
    approved_limit: float
    top_factors: List[str]
    reason_codes: List[str]

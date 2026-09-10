"""Transport-independent mortgage domain models."""

from datetime import date
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, model_validator


def _parse_decimal(value: object) -> Decimal:
    if isinstance(value, float):
        raise ValueError("decimal values must be supplied as strings, integers, or Decimal values")
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise ValueError("invalid decimal value")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("invalid decimal value") from exc


Principal = Annotated[
    Decimal,
    BeforeValidator(_parse_decimal),
    Field(gt=Decimal("0"), le=Decimal("10000000"), decimal_places=2),
]
AnnualRate = Annotated[
    Decimal,
    BeforeValidator(_parse_decimal),
    Field(ge=Decimal("0"), le=Decimal("25"), decimal_places=6),
]


class ProductType(StrEnum):
    """Mortgage repayment products supported by calculation specification v1."""

    ANNUITY = "annuity"
    LINEAR = "linear"


class MortgageRequest(BaseModel):
    """Validated input for one indicative mortgage calculation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    principal_eur: Principal
    annual_interest_percent: AnnualRate
    term_years: Annotated[int, Field(ge=1, le=40)]
    product_type: ProductType
    start_date: date
    fixed_rate_years: Annotated[int, Field(ge=1, le=40)] | None = None

    @model_validator(mode="after")
    def fixed_rate_cannot_exceed_term(self) -> "MortgageRequest":
        if self.fixed_rate_years is not None and self.fixed_rate_years > self.term_years:
            raise ValueError("fixed_rate_years cannot exceed term_years")
        return self


class PaymentLine(BaseModel):
    """One displayed monthly line in an amortization schedule."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    period: int
    payment_eur: Decimal
    interest_eur: Decimal
    principal_eur: Decimal
    remaining_balance_eur: Decimal


class MortgageResult(BaseModel):
    """Auditable result for an indicative mortgage calculation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    currency: str = "EUR"
    calculation_version: str = "v1"
    product_type: ProductType
    start_date: date
    principal_eur: Decimal
    annual_interest_percent: Decimal
    term_years: int
    monthly_payment_eur: Decimal
    total_payment_eur: Decimal
    total_interest_eur: Decimal
    schedule: tuple[PaymentLine, ...]
    assumptions: tuple[str, ...]

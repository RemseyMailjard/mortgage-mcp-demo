"""Deterministic mortgage calculations following specification v1."""

from decimal import ROUND_HALF_EVEN, Decimal, localcontext

from mortgage_mcp.domain import MortgageRequest, MortgageResult, PaymentLine, ProductType

CENT = Decimal("0.01")
MONTHS_PER_YEAR = 12
PERCENT_PER_UNIT = Decimal("100")


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_EVEN)


def calculate_mortgage(request: MortgageRequest) -> MortgageResult:
    """Calculate a complete monthly schedule for one validated mortgage."""
    with localcontext() as context:
        context.prec = 50
        periods = request.term_years * MONTHS_PER_YEAR
        monthly_rate = request.annual_interest_percent / PERCENT_PER_UNIT / MONTHS_PER_YEAR
        scheduled_principal = request.principal_eur / periods
        if monthly_rate == 0:
            annuity_payment = scheduled_principal
        else:
            annuity_payment = request.principal_eur * monthly_rate / (
                Decimal(1) - (Decimal(1) + monthly_rate) ** -periods
            )

        balance = request.principal_eur
        displayed_principal_total = Decimal(0)
        schedule: list[PaymentLine] = []

        for period in range(1, periods + 1):
            interest = balance * monthly_rate
            if period == periods:
                principal = balance
                displayed_principal = _money(request.principal_eur - displayed_principal_total)
            else:
                principal = (
                    annuity_payment - interest
                    if request.product_type is ProductType.ANNUITY
                    else scheduled_principal
                )
                remaining_displayed_principal = _money(
                    request.principal_eur - displayed_principal_total
                )
                displayed_principal = min(_money(principal), remaining_displayed_principal)

            balance -= principal
            displayed_interest = _money(interest)
            displayed_payment = displayed_principal + displayed_interest
            displayed_balance = Decimal(0) if period == periods else _money(balance)
            displayed_principal_total += displayed_principal

            schedule.append(
                PaymentLine(
                    period=period,
                    payment_eur=displayed_payment,
                    interest_eur=displayed_interest,
                    principal_eur=displayed_principal,
                    remaining_balance_eur=displayed_balance,
                )
            )

        total_payment = sum((line.payment_eur for line in schedule), Decimal(0))
        total_interest = sum((line.interest_eur for line in schedule), Decimal(0))
        assumptions = (
            "Monthly payments and annual nominal interest divided by 12.",
            "EUR amounts use round-half-even at display boundaries.",
            "Rate remains unchanged for the full calculated schedule.",
            "Indicative calculation; not an offer, approval, or financial advice.",
        )
        return MortgageResult(
            product_type=request.product_type,
            start_date=request.start_date,
            principal_eur=_money(request.principal_eur),
            annual_interest_percent=request.annual_interest_percent,
            term_years=request.term_years,
            monthly_payment_eur=schedule[0].payment_eur,
            total_payment_eur=total_payment,
            total_interest_eur=total_interest,
            schedule=tuple(schedule),
            assumptions=assumptions,
        )

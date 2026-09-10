# Mortgage calculation specification v1

Status: demo specification, effective 2026-09-10.

This document defines deterministic indicative calculations. It does not define a Rabobank
credit decision, binding offer, borrowing capacity, or personalized financial advice.

## Supported products

- **Annuity mortgage:** a constant gross monthly payment while the annual nominal rate is
  unchanged. The interest share falls and principal repayment rises.
- **Linear mortgage:** a constant monthly principal repayment plus interest on the opening
  balance. The gross monthly payment falls over time.

Interest-only loans, mixed loan parts, early repayment, fees, taxes, insurance, NHG, rate
discounts, income-based affordability, and rate changes are outside v1.

## Inputs

| Field | Unit and constraints |
| --- | --- |
| Principal | EUR, greater than 0, at most EUR 10,000,000, at most 2 decimals |
| Annual nominal interest rate | Percentage, from 0 through 25, at most 6 decimals |
| Term | Whole years, from 1 through 40 |
| Product type | `annuity` or `linear` |
| Start date | ISO 8601 calendar date |
| Rate effective date | ISO 8601 calendar date, provided by the rate source |

Payments occur monthly, so the number of periods is $n = 12y$ and the monthly rate is
$r = i / 1200$, where $i$ is the annual nominal percentage and $y$ is the term in years.
All calculations use EUR.

## Annuity calculation

For principal $P$, monthly rate $r > 0$, and $n$ periods, the unrounded monthly payment is:

$$
A = P \frac{r}{1 - (1 + r)^{-n}}
$$

When $r = 0$, $A = P/n$. For each period, interest is opening balance times $r$, principal
repayment is $A$ minus interest, and closing balance is opening balance minus repayment.

## Linear calculation

The unrounded scheduled principal repayment is $L = P/n$. For each period, interest is opening
balance times $r$, payment is $L$ plus interest, and closing balance is opening balance minus
$L$.

## Precision and rounding

- Parse monetary and rate inputs from decimal strings; binary floating-point is prohibited.
- Calculate with at least 28 significant decimal digits.
- Keep unrounded values between periods to prevent accumulated cent drift.
- Present money rounded to EUR cents using round-half-even.
- In the final period, set principal repayment to the remaining unrounded balance and closing
  balance to exactly zero.
- Totals are the sums of displayed period amounts, not independently rounded formulas.

## Result metadata

Every result states currency (`EUR`), calculation version (`v1`), product type, start date,
assumptions, and rate provenance. Rate provenance includes provider, source reference, effective
date, retrieval date, and whether data is demo data.

## Rabobank data boundary

Product rules and rates enter through a replaceable provider. Demo fixtures must be visibly
marked as examples and dated. Production data requires an approved Rabobank source or authorized
API. The server must not scrape public pages or call undocumented/private APIs. Missing, expired,
or stale data is reported explicitly and is never silently presented as current.

## Review checklist

- A mortgage/product specialist verifies formulas and product assumptions.
- A Rabobank-authorized owner verifies every Rabobank-specific source and effective date.
- Privacy, security, legal, and compliance owners approve customer-facing wording and data use.
- Independently calculated examples become golden tests before a production release.
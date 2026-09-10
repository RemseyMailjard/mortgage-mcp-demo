# Security, privacy, and responsible use

## Deployment boundary

The demo supports local stdio transport only. Its entry point rejects every remote transport.
Do not expose it on a network until a reviewed gateway provides authentication, authorization,
TLS, rate limiting, request-size limits, audit controls, and secret management.

## Data classification and minimization

| Data | Classification | Handling |
| --- | --- | --- |
| Principal, rate, term, product, dates | Customer financial data | Process in memory; do not log or persist |
| Name, address, account number, BSN, income | Not required | Do not collect |
| Demo products and rates | Public demo data | Version in source with provenance |
| Event name and random correlation ID | Operational metadata | May be logged for up to 30 days |

The service has no customer database and no analytics integration. Operational logging accepts
only an event name and generates its own correlation ID, preventing callers from attaching raw
request data. Production retention and deletion controls require a separate privacy review.

## Threat model

- **Untrusted tool input:** strict schemas, bounded values, and forbidden extra fields reduce
  malformed or oversized requests.
- **Sensitive logs:** customer values are excluded from operational events and tool errors avoid
  echoing complete requests.
- **False or stale rates:** dated provider data expires closed and includes source metadata.
- **Unauthorized network use:** non-stdio startup is denied until real gateway controls exist.
- **Dependency compromise:** dependencies are locked; CI runs tests and should add automated
  vulnerability scanning before production use.
- **Misleading outcomes:** output and documentation state that calculations are indicative and
  are not approval, an offer, or advice.

## Responsible-use boundary

This server performs arithmetic; it does not assess eligibility, creditworthiness, affordability,
or suitability. It must not make or automate a lending decision. Customer-facing experiences must
display the Dutch disclaimer and direct customers to official Rabobank channels for current product
information and personal advice.

## Production approval gates

- Security review and penetration test of the selected remote gateway and deployment.
- Privacy assessment covering lawful basis, retention, deletion, and data-subject rights.
- Legal/compliance approval of wording, formulas, sources, and product representation.
- Rabobank authorization for brand use and every non-demo data integration.
- Incident response owner, vulnerability reporting route, and tested rollback procedure.
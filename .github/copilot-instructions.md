# Copilot instructions

- Target Python 3.12 and the stable v2 line of the official MCP Python SDK.
- Keep mortgage calculations independent from MCP transport and rate providers.
- Use `Decimal` for money and rates; never use binary floating point for financial math.
- Treat outputs as indicative calculations, never as approval, an offer, or financial advice.
- Do not log customer inputs or add unauthorized Rabobank API or scraping integrations.
- Add tests for formulas, validation, MCP schemas, and error behavior.

SDK references:

- https://py.sdk.modelcontextprotocol.io/
- https://py.sdk.modelcontextprotocol.io/get-started/
- https://py.sdk.modelcontextprotocol.io/servers/
- https://py.sdk.modelcontextprotocol.io/client/

# Mortgage MCP demo

Een Python MCP-server voor transparante, indicatieve hypotheekberekeningen met annuiteiten- en
lineaire hypotheken.

> Dit is een onafhankelijke demo en is niet verbonden aan of goedgekeurd door Rabobank. De
> voorbeeldrentes zijn fictief. Uitkomsten zijn geen aanbod, kredietbesluit of persoonlijk advies.

## Snel starten

Installeer [uv](https://docs.astral.sh/uv/). `uv` installeert zelf de vereiste Python-versie.

```powershell
uv sync --frozen --all-extras --dev
uv run pytest
uv run mortgage-mcp
```

De meegeleverde `.vscode/mcp.json` registreert `rabobank-mortgage-demo` automatisch in VS Code.
Open de MCP-weergave, start de server en gebruik de beschikbare tools. Voor MCP Inspector:

```powershell
uv run mcp dev src/mortgage_mcp/server.py
```

## Beschikbare tools

| Tool | Doel |
| --- | --- |
| `calculate_mortgage` | Berekent een scenario en retourneert standaard 12 aflossingsregels |
| `compare_mortgages` | Vergelijkt annuiteiten en lineair met identieke invoer |
| `list_mortgage_products` | Toont ondersteunde producten en rentevaste perioden |
| `get_interest_rates` | Toont gedateerde demo-rentes inclusief herkomst |
| `health` | Controleert of de MCP-server reageert |

Geldbedragen zijn decimale tekenreeksen, bijvoorbeeld `"300000.00"`. Datums gebruiken ISO 8601,
bijvoorbeeld `"2026-09-10"`. Gebruik `schedule_offset` en `schedule_limit` (maximaal 120) om door
een aflossingsschema te bladeren. Zie [de toolreferentie](docs/tool-reference.md) voor voorbeelden.

## Kwaliteitscontroles

```powershell
uv run ruff check .
uv run mypy
uv run pytest
uv build
```

De rekenregels staan in [specificatie v1](docs/calculation-spec-v1.md). Lees ook het
[security- en privacybeleid](docs/security-and-privacy.md) en het
[operationeel draaiboek](docs/operations.md).

## Beperkingen

De demo ondersteunt geen leencapaciteit, kredietwaardigheid, belastingeffecten, NHG, verzekeringen,
kosten, rentewijzigingen, vervroegd aflossen of samengestelde leningdelen. Alleen lokale stdio-
uitvoering is toegestaan. Voor actuele producten, rentes en persoonlijk advies moeten klanten de
officiele Rabobank-kanalen gebruiken.

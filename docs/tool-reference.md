# MCP-toolreferentie

## Voorbeeldscenario

Alle gegevens hieronder zijn fictief en gebruiken de demo-rente met peildatum 2026-09-10:

- hoofdsom: EUR 300.000;
- looptijd: 30 jaar;
- rentevaste periode: 10 jaar;
- nominale jaarrente: 4,00%;
- ingangsdatum: 2026-09-10.

Een aanroep van `calculate_mortgage` gebruikt bijvoorbeeld:

```json
{
  "principal_eur": "300000.00",
  "term_years": 30,
  "product_type": "annuity",
  "fixed_rate_years": 10,
  "start_date": "2026-09-10",
  "rate_date": "2026-09-10",
  "schedule_offset": 0,
  "schedule_limit": 12
}
```

Het antwoord bevat `currency`, `calculation_version`, aannames, totalen, renteherkomst en een
begrensd deel van het aflossingsschema. `schedule_total_periods`, `schedule_offset` en
`schedule_count` maken paginering controleerbaar.

## Transparante vergelijking

`compare_mortgages` gebruikt voor beide producten dezelfde hoofdsom, looptijd, rentevaste periode,
peildatum en ingangsdatum. Voor het fictieve voorbeeld geeft de huidige rekenversie:

| Product | Eerste maand | Totale betaling | Totale rente |
| --- | ---: | ---: | ---: |
| Annuiteit | EUR 1.432,25 | EUR 515.608,48 | EUR 215.608,48 |
| Lineair | EUR 1.833,33 | EUR 480.500,00 | EUR 180.500,00 |

Dit beschrijft verschillen; het is geen productadvies. De demo veronderstelt dat de rente voor het
hele berekende schema gelijk blijft, ook als de gekozen rentevaste periode korter is dan de looptijd.

## Rente en herkomst

`get_interest_rates` vereist een `as_of`-datum. Elke rente vermeldt provider, bronreferentie,
ingangsdatum, vervaldatum, ophaaldatum en `is_demo_data`. Na de vervaldatum geeft de tool een fout in
plaats van oude data als actueel te tonen.

## Fouten oplossen

- **Geen actuele demo-rente:** gebruik een peildatum binnen de geldigheid van de fixture of voeg na
  broncontrole een nieuwe fixture toe.
- **Ongeldige Decimal:** stuur geld en rente als tekenreeks, niet als JSON floating-pointgetal.
- **Te groot schema:** kies een `schedule_limit` van 1 tot en met 120 en blader met de offset.
- **Server start niet op afstand:** netwerktransport is bewust geblokkeerd totdat echte
  authenticatie en autorisatie zijn geimplementeerd.
- **VS Code vindt de server niet:** voer eerst `uv sync --frozen --all-extras --dev` uit en controleer
  dat `uv` in `PATH` staat.
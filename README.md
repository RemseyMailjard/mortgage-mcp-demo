# Mortgage MCP demo

A Python MCP server for transparent, indicative mortgage calculations.

> This independent demo is not affiliated with or endorsed by Rabobank. Results are not a
> mortgage offer, credit decision, or personalized financial advice.

## Development

Requirements: [uv](https://docs.astral.sh/uv/). `uv` installs the required Python version.

```powershell
uv sync --all-extras --dev
uv run pytest
uv run ruff check .
uv run mypy
```

Start the stdio server:

```powershell
uv run mortgage-mcp
```

The committed `.vscode/mcp.json` registers the server as `rabobank-mortgage-demo` for VS Code.
Use MCP Inspector during development with `uv run mcp dev src/mortgage_mcp/server.py`.

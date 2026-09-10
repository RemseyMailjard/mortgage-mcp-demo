"""MCP server entry point."""

from mcp.server import MCPServer

mcp = MCPServer(
    "Rabobank Mortgage Demo",
    instructions=(
        "Provide transparent, indicative mortgage calculations. "
        "Never describe results as approval, an offer, or personalized financial advice."
    ),
)


@mcp.tool(title="Check server health")
def health() -> str:
    """Return the service health status."""
    return "ok"


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()

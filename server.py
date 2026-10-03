from fastmcp import FastMCP

mcp = FastMCP("Mozzart EuroLeague")

@mcp.tool()
def health() -> dict:
    """Proverava da li Mozzart EuroLeague MCP radi."""
    return {
        "status": "ok",
        "service": "Mozzart EuroLeague MCP"
    }

@mcp.tool()
def get_mozzart_lines(
    date: str = "",
    player: str = "",
) -> dict:
    """
    Vraca Mozzart EuroLeague player-points margine i kvote.
    Trenutno je alat inicijalizovan; bazu i automatski import dodajemo sledece.
    """
    return {
        "date": date,
        "player": player,
        "lines": [],
        "status": "database_not_configured"
    }


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000
    )

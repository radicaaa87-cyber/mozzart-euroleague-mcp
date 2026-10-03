from fastmcp import FastMCP
import sqlite3
import os

mcp = FastMCP("Mozzart EuroLeague")

DB_PATH = os.getenv("MOZZART_DB_PATH", "mozzart.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS player_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            date TEXT NOT NULL,
            player TEXT NOT NULL,
            team TEXT,

            main_line REAL,
            main_over REAL,
            main_under REAL,

            low_line REAL,
            low_under REAL,
            low_over REAL,

            high_line REAL,
            high_under REAL,
            high_over REAL,

            source TEXT,

            UNIQUE(date, player)
        )
    """)

    conn.commit()
    conn.close()


init_db()


@mcp.tool()
def health() -> dict:
    """Proverava da li Mozzart EuroLeague MCP radi."""

    conn = get_db()

    count = conn.execute(
        "SELECT COUNT(*) AS n FROM player_lines"
    ).fetchone()["n"]

    conn.close()

    return {
        "status": "ok",
        "service": "Mozzart EuroLeague MCP",
        "database": "ok",
        "stored_lines": count
    }


@mcp.tool()
def add_mozzart_line(
    date: str,
    player: str,
    team: str = "",

    main_line: float = None,
    main_over: float = None,
    main_under: float = None,

    low_line: float = None,
    low_under: float = None,
    low_over: float = None,

    high_line: float = None,
    high_under: float = None,
    high_over: float = None,

    source: str = ""
) -> dict:
    """
    Dodaje ili menja Mozzart EuroLeague player-points marginu.
    """

    conn = get_db()

    conn.execute("""
        INSERT INTO player_lines (
            date,
            player,
            team,

            main_line,
            main_over,
            main_under,

            low_line,
            low_under,
            low_over,

            high_line,
            high_under,
            high_over,

            source
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(date, player)
        DO UPDATE SET

            team = excluded.team,

            main_line = excluded.main_line,
            main_over = excluded.main_over,
            main_under = excluded.main_under,

            low_line = excluded.low_line,
            low_under = excluded.low_under,
            low_over = excluded.low_over,

            high_line = excluded.high_line,
            high_under = excluded.high_under,
            high_over = excluded.high_over,

            source = excluded.source
    """, (
        date,
        player,
        team,

        main_line,
        main_over,
        main_under,

        low_line,
        low_under,
        low_over,

        high_line,
        high_under,
        high_over,

        source
    ))

    conn.commit()
    conn.close()

    return {
        "status": "saved",
        "date": date,
        "player": player
    }


@mcp.tool()
def get_mozzart_lines(
    date: str = "",
    player: str = ""
) -> dict:
    """
    Vraca Mozzart EuroLeague player-points margine i kvote.
    Moze da filtrira po datumu i/ili igracu.
    """

    conn = get_db()

    query = """
        SELECT
            date,
            player,
            team,

            main_line,
            main_over,
            main_under,

            low_line,
            low_under,
            low_over,

            high_line,
            high_under,
            high_over,

            source

        FROM player_lines
        WHERE 1=1
    """

    params = []

    if date:
        query += " AND date = ?"
        params.append(date)

    if player:
        query += " AND LOWER(player) LIKE LOWER(?)"
        params.append(f"%{player}%")

    query += " ORDER BY date, player"

    rows = conn.execute(query, params).fetchall()

    conn.close()

    return {
        "date": date,
        "player": player,
        "count": len(rows),
        "lines": [dict(row) for row in rows],
        "status": "ok"
    }


@mcp.tool()
def delete_mozzart_lines(
    date: str
) -> dict:
    """
    Brise sve sacuvane Mozzart margine za jedan datum.
    Koristi se ako treba ponovo importovati ispravljenu ponudu.
    """

    conn = get_db()

    cursor = conn.execute(
        "DELETE FROM player_lines WHERE date = ?",
        (date,)
    )

    deleted = cursor.rowcount

    conn.commit()
    conn.close()

    return {
        "status": "deleted",
        "date": date,
        "deleted_rows": deleted
    }


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000"))
    )

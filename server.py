from fastmcp import FastMCP
import os
import requests

mcp = FastMCP("OddsPapi EuroLeague + ACB")

BASE_URL = "https://api.oddspapi.io/v4"
API_KEY = os.getenv("ODDSPAPI_API_KEY")

BASKETBALL_SPORT_ID = 11

LEAGUE_ALIASES = {
    "euroleague": ["euroleague", "euro league"],
    "acb": ["liga endesa", "acb", "liga acb", "endesa"],
    "liga endesa": ["liga endesa", "acb", "liga acb", "endesa"],
}


def api_get(endpoint: str, params=None):
    if not API_KEY:
        return {
            "error": "ODDSPAPI_API_KEY is not configured on the server"
        }

    params = params or {}
    params["apiKey"] = API_KEY

    try:
        r = requests.get(
            f"{BASE_URL}/{endpoint}",
            params=params,
            timeout=30
        )

        if r.status_code != 200:
            return {
                "error": f"OddsPapi returned HTTP {r.status_code}",
                "body": r.text[:1000]
            }

        return r.json()

    except Exception as e:
        return {"error": str(e)}


def _normalize(value: str) -> str:
    return " ".join((value or "").strip().lower().replace("-", " ").split())


def _resolve_league(league: str):
    """
    Resolve a basketball league name/alias to one OddsPapi tournament object.
    This intentionally resolves dynamically instead of hardcoding tournament IDs.
    """
    query = _normalize(league)
    aliases = LEAGUE_ALIASES.get(query, [query])

    tournaments = api_get(
        "tournaments",
        {
            "sportId": BASKETBALL_SPORT_ID,
            "language": "en"
        }
    )

    if isinstance(tournaments, dict) and tournaments.get("error"):
        return tournaments

    if not isinstance(tournaments, list):
        return {
            "error": "Unexpected tournaments response",
            "response": tournaments
        }

    normalized_aliases = [_normalize(x) for x in aliases]

    exact_matches = []
    partial_matches = []

    for tournament in tournaments:
        name = _normalize(str(tournament.get("tournamentName", "")))
        slug = _normalize(str(tournament.get("tournamentSlug", "")))

        if name in normalized_aliases or slug in normalized_aliases:
            exact_matches.append(tournament)
            continue

        if any(alias and (alias in name or alias in slug) for alias in normalized_aliases):
            partial_matches.append(tournament)

    matches = exact_matches or partial_matches

    if not matches:
        return {
            "error": f"League '{league}' was not found in OddsPapi basketball tournaments",
            "sportId": BASKETBALL_SPORT_ID
        }

    # Prefer the tournament with the largest amount of currently visible fixtures.
    def fixture_count(item):
        return (
            int(item.get("futureFixtures") or 0)
            + int(item.get("upcomingFixtures") or 0)
            + int(item.get("liveFixtures") or 0)
        )

    matches.sort(key=fixture_count, reverse=True)
    return matches[0]


@mcp.tool()
def test_connection():
    """
    Test whether the OddsPapi API key and connection work.
    """
    return api_get("account")


@mcp.tool()
def get_tournaments(sport_id: int):
    """
    Get OddsPapi tournaments for a sport.
    Basketball sportId is 11.
    """
    return api_get(
        "tournaments",
        {
            "sportId": sport_id,
            "language": "en"
        }
    )


@mcp.tool()
def find_basketball_league(league: str):
    """
    Find a basketball league and return its OddsPapi tournament metadata.

    Supported aliases include:
    - EuroLeague / Euroleague
    - ACB / Liga Endesa
    """
    return _resolve_league(league)


@mcp.tool()
def get_fixtures(
    tournament_id: int,
    date_from: str = "",
    date_to: str = "",
    status_id: int = -1,
    bookmakers: str = ""
):
    """
    Get fixtures for a tournament.

    date_from/date_to should be ISO dates/times, for example:
    2026-01-15T00:00:00Z
    2026-01-16T23:59:59Z

    status_id:
    0 = upcoming
    1 = live
    2 = finished
    3 = cancelled
    -1 = don't filter
    """

    params = {
        "tournamentId": tournament_id,
        "language": "en"
    }

    if date_from:
        params["from"] = date_from

    if date_to:
        params["to"] = date_to

    if status_id >= 0:
        params["statusId"] = status_id

    if bookmakers:
        params["bookmakers"] = bookmakers
        params["hasOdds"] = "true"

    return api_get("fixtures", params)


@mcp.tool()
def get_league_fixtures(
    league: str,
    date_from: str = "",
    date_to: str = "",
    status_id: int = -1,
    bookmakers: str = ""
):
    """
    Get basketball fixtures by league name instead of tournament ID.

    Examples:
    league="euroleague"
    league="acb"
    league="liga endesa"
    """
    tournament = _resolve_league(league)

    if isinstance(tournament, dict) and tournament.get("error"):
        return tournament

    tournament_id = tournament.get("tournamentId")
    if tournament_id is None:
        return {
            "error": "Resolved league has no tournamentId",
            "tournament": tournament
        }

    params = {
        "tournamentId": tournament_id,
        "language": "en"
    }

    if date_from:
        params["from"] = date_from

    if date_to:
        params["to"] = date_to

    if status_id >= 0:
        params["statusId"] = status_id

    if bookmakers:
        params["bookmakers"] = bookmakers
        params["hasOdds"] = "true"

    fixtures = api_get("fixtures", params)

    return {
        "league": league,
        "resolvedTournament": tournament,
        "fixtures": fixtures
    }


@mcp.tool()
def get_acb_fixtures(
    date_from: str = "",
    date_to: str = "",
    status_id: int = -1,
    bookmakers: str = ""
):
    """
    Convenience tool for Spain's ACB / Liga Endesa.
    The tournament ID is resolved dynamically from OddsPapi.
    """
    tournament = _resolve_league("acb")

    if isinstance(tournament, dict) and tournament.get("error"):
        return tournament

    tournament_id = tournament.get("tournamentId")
    if tournament_id is None:
        return {
            "error": "Resolved ACB league has no tournamentId",
            "tournament": tournament
        }

    params = {
        "tournamentId": tournament_id,
        "language": "en"
    }

    if date_from:
        params["from"] = date_from

    if date_to:
        params["to"] = date_to

    if status_id >= 0:
        params["statusId"] = status_id

    if bookmakers:
        params["bookmakers"] = bookmakers
        params["hasOdds"] = "true"

    return {
        "league": "ACB / Liga Endesa",
        "resolvedTournament": tournament,
        "fixtures": api_get("fixtures", params)
    }


@mcp.tool()
def get_fixture(fixture_id: str):
    """
    Get metadata for one fixture.
    """
    return api_get(
        "fixture",
        {
            "fixtureId": fixture_id,
            "language": "en"
        }
    )


@mcp.tool()
def get_odds(
    fixture_id: str,
    bookmakers: str = ""
):
    """
    Get current/full bookmaker odds for a fixture.

    bookmakers can be:
    pinnacle
    bet365
    or comma-separated bookmaker slugs.
    """

    params = {
        "fixtureId": fixture_id,
        "oddsFormat": "decimal",
        "language": "en",
        "verbosity": 3
    }

    if bookmakers:
        params["bookmakers"] = bookmakers

    return api_get("odds", params)


@mcp.tool()
def get_historical_odds(
    fixture_id: str,
    bookmakers: str,
    player_id: int = 0,
    outcome_id: int = 0
):
    """
    Get historical bookmaker odds for a fixture.

    IMPORTANT:
    OddsPapi allows maximum 3 bookmaker slugs per request.

    Historical data is available from January 2026 onward.
    """

    bookmaker_list = [
        x.strip()
        for x in bookmakers.split(",")
        if x.strip()
    ]

    if not bookmaker_list:
        return {
            "error": "At least one bookmaker is required"
        }

    if len(bookmaker_list) > 3:
        return {
            "error": "OddsPapi historical endpoint allows max 3 bookmakers per request"
        }

    params = {
        "fixtureId": fixture_id,
        "bookmakers": ",".join(bookmaker_list)
    }

    if player_id:
        params["playerId"] = player_id

    if outcome_id:
        params["outcomeId"] = outcome_id

    return api_get("historical-odds", params)


@mcp.tool()
def get_markets():
    """
    Get OddsPapi market definitions.
    We will use this to identify the exact Player Points market IDs.
    """
    return api_get("markets")


@mcp.tool()
def get_participants(sport_id: int):
    """
    Get participant/team names for a sport.
    Basketball sportId is 11.
    """
    return api_get(
        "participants",
        {
            "sportId": sport_id,
            "language": "en"
        }
    )


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080"))
    )

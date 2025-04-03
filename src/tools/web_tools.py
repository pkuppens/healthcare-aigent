"""Mocked web tools for the healthcare multi-agent system."""

from crewai_tools import tool


@tool("Mocked Web Search Tool")
def search_web_mock(query: str) -> str:
    """Simulate web search functionality.

    Args:
        query (str): Search query

    Returns:
        str: Mocked search results
    """
    print(f"[MOCK_SEARCH] Zoeken naar: {query}")

    # Mock responses for common medical queries
    mock_responses = {
        "hypertensie": "Hypertensie (hoge bloeddruk) is een veelvoorkomende aandoening. "
        "Meer informatie: https://www.thuisarts.nl/hoge-bloeddruk",
        "diabetes": "Diabetes type 2 is een stofwisselingsziekte. " "Meer informatie: https://www.thuisarts.nl/diabetes",
        "metoprolol": "Metoprolol is een bètablokker gebruikt bij hoge bloeddruk en hartritmestoornissen. "
        "Bijwerkingen kunnen zijn: vermoeidheid, duizeligheid. "
        "Meer informatie: https://www.apotheek.nl/medicijnen/metoprolol",
        "metformine": "Metformine wordt gebruikt bij diabetes type 2. "
        "Het verlaagt de bloedsuikerspiegel. "
        "Meer informatie: https://www.apotheek.nl/medicijnen/metformine",
    }

    # Return specific mock response if available, otherwise generic response
    if query.lower() in mock_responses:
        return mock_responses[query.lower()]

    return (
        f"Mock resultaat voor '{query}':\n"
        f"1. Algemene informatie over {query} - https://www.thuisarts.nl\n"
        f"2. Medicatie-informatie - https://www.apotheek.nl\n"
        f"3. Richtlijnen - https://www.nhg.org"
    )

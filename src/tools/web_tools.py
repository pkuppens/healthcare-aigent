"""Web tools for healthcare system."""

from crewai.tools import BaseTool


class WebSearchTool(BaseTool):
    """Tool for searching medical information on the web."""

    name: str = "search_medical_info"
    description: str = "Search for medical information on the web"

    async def _run(self, query: str) -> str:
        """Run the web search tool.

        Args:
            query: Search query

        Returns:
            Search results
        """
        return f"Mock search results for: {query}"

"""Web tools for healthcare system."""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class WebSearchTool(BaseTool):
    """Tool for searching medical information on the web."""

    name = "web_search"
    description = "Searches for medical information on the web"

    class InputSchema(BaseModel):
        """Input schema for web search tool."""

        query: str = Field(..., description="Search query for medical information")

    async def _run(self, query: str) -> str:
        """Search for medical information on the web.

        Args:
            query: Search query for medical information

        Returns:
            Search results as a string
        """
        # TODO: Implement actual web search
        return f"Search results for: {query}"

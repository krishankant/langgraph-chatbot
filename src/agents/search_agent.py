import logging
from typing import Dict, Any, List
from tavily import TavilyClient
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from src.config.settings import settings

logger = logging.getLogger(__name__)

class SearchAgent:
    def __init__(self):
        self.tavily_client = TavilyClient(api_key=settings.tavily_api_key)
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            model_name=settings.llm_model,
            temperature=settings.temperature
        )
        self.search_prompt = PromptTemplate(
            input_variables=["query", "search_results"],
            template=""" Based on the user's query and the search results below, provide a comprehensive and accurate answer.
            User Query: {query}
            Search Results: {search_results}
            Please provide a well-structured response that:
            1. Directly answers the user's question
            2. Includes relevant information from the search results
            3. Cites sources when appropriate
            4. Is clear and concise
            Response: """
        )

    def search_and_respond(self, query: str) -> Dict[str, Any]:
        """Perform internet search and generate response."""
        try:
            logger.info(f"Performing search for query: {query}")
            # Perform search
            search_results = self._perform_search(query)
            if not search_results:
                return {
                    "success": False,
                    "response": "I couldn't find relevant information for your query. Please try rephrasing your question.",
                    "sources": []
                }
            # Format search results for prompt
            formatted_results = self._format_search_results(search_results)
            # Generate response using LLM
            prompt = self.search_prompt.format(
                query=query,
                search_results=formatted_results
            )
            response = self.llm.invoke(prompt)
            # Extract sources
            sources = [
                {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("content", "")[:200] + "..."
                }
                for result in search_results
            ]
            logger.info(f"Generated response for search query: {query}")
            return {
                "success": True,
                "response": response.content.strip(),
                "sources": sources,
                "search_performed": True
            }
        except Exception as e:
            logger.error(f"Error in search and respond: {str(e)}")
            return {
                "success": False,
                "response": f"I encountered an error while searching: {str(e)}",
                "sources": [],
                "search_performed": False
            }

    def _perform_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform search using Tavily API."""
        try:
            response = self.tavily_client.search(
                query=query,
                max_results=settings.max_search_results,
                search_depth="advanced"
            )
            return response.get("results", [])
        except Exception as e:
            logger.error(f"Error performing Tavily search: {str(e)}")
            return []

    def _format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for prompt."""
        formatted = ""
        for i, result in enumerate(results, 1):
            title = result.get("title", "Untitled")
            content = result.get("content", "No content available")
            url = result.get("url", "")
            formatted += f"{i}. Title: {title}\n"
            formatted += f" URL: {url}\n"
            formatted += f" Content: {content}\n\n"
        return formatted

    def should_search(self, query: str, context: str = "") -> bool:
        """Determine if a search is needed for the query."""
        search_indicators = [
            "what is", "who is", "when did", "where is", "how to",
            "latest", "recent", "current", "news", "update", "weather",
            "stock price", "market", "today", "happening now", "breaking"
        ]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in search_indicators)
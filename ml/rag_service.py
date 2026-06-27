import logging
import time
from typing import List, Dict

logger = logging.getLogger(__name__)

class RAGService:
    """
    Retrieval-Augmented Generation (RAG) Service.
    Fetches real-time web context to ground LLM responses with up-to-date information.
    """
    
    def __init__(self):
        self.max_results = 5
        self.enabled = True
        
    def search(self, goal: str, category: str) -> Dict:
        """
        Searches the web for context relevant to the user's goal.
        Returns a dict with results and metadata.
        """
        start = time.time()
        query = f"{goal} {category} beginner guide tips 2025"
        
        results = []
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                raw = list(ddgs.text(query, max_results=self.max_results))
                for r in raw:
                    results.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("body", ""),
                        "url": r.get("href", "")
                    })
            logger.info(f"RAG: Retrieved {len(results)} results for query: '{query}'")
        except Exception as e:
            logger.warning(f"RAG web search failed: {e}. Proceeding without context.")
            results = []

        latency_ms = (time.time() - start) * 1000
        return {
            "query": query,
            "results": results,
            "latency_ms": latency_ms,
            "source_count": len(results)
        }

    def format_context(self, search_results: Dict) -> str:
        """Formats web search results into a clean context string for the LLM prompt."""
        results = search_results.get("results", [])
        if not results:
            return ""
        
        context_lines = ["## Real-Time Web Context (use this to enrich your plan):"]
        for i, r in enumerate(results[:3], 1):
            context_lines.append(f"{i}. **{r['title']}**")
            context_lines.append(f"   {r['snippet'][:200]}...")
            context_lines.append(f"   Source: {r['url']}")
        
        return "\n".join(context_lines)

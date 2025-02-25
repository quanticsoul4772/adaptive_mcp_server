"""
Mock modules for testing
"""

class ResearchContext:
    """Mock research context for testing"""
    def __init__(self, original_query, processed_queries=None, search_results=None, metadata=None, confidence=0.85):
        self.original_query = original_query
        self.processed_queries = processed_queries or [original_query]
        self.search_results = search_results or []
        self.metadata = metadata or {}
        self.confidence = confidence

class SearchResult:
    """Mock search result for testing"""
    def __init__(self, url, title, text, relevance_score, source, metadata=None):
        self.url = url
        self.title = title
        self.text = text
        self.relevance_score = relevance_score
        self.source = source
        self.metadata = metadata or {}

class MockResearchIntegrator:
    """Mock research integrator for testing"""
    async def research(self, query):
        """Mock research method"""
        return ResearchContext(
            original_query=query,
            processed_queries=[query, f"more about {query}"],
            search_results=[
                SearchResult(
                    url="https://example.com/article",
                    title="Test Article",
                    text="This is test content about the query.",
                    relevance_score=0.9,
                    source="example.com"
                )
            ],
            confidence=0.85
        )
    
    def extract_key_information(self, context, max_sources=3):
        """Mock extract key information method"""
        return {
            "query": context.original_query,
            "confidence": context.confidence,
            "sources": [{"url": r.url, "title": r.title} for r in context.search_results[:max_sources]],
            "key_facts": ["Test fact 1", "Test fact 2"]
        }

# Singleton instance
research_integrator = MockResearchIntegrator()

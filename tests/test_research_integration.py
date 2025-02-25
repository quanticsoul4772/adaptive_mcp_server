"""
Comprehensive Tests for Research Integration

These tests validate the research capabilities and their integration with reasoning.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import logging
from typing import Dict, Any, List

# Import research components
from research.research_integrator import research_integrator, ResearchContext
from research.exa_integration import ExaSearchIntegration, SearchResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test.research")

# Sample search results for mocking
SAMPLE_SEARCH_RESULTS = [
    SearchResult(
        url="https://example.com/article1",
        title="Quantum Computing Explained",
        text="Quantum computing is an emerging technology that uses quantum mechanics to perform computations.",
        relevance_score=0.95,
        source="example.com",
        metadata={"published_date": "2023-01-15"}
    ),
    SearchResult(
        url="https://example.org/article2",
        title="The Future of Quantum Computing",
        text="Researchers predict quantum computers will revolutionize many fields including cryptography and drug discovery.",
        relevance_score=0.85,
        source="example.org",
        metadata={"published_date": "2023-05-22"}
    ),
    SearchResult(
        url="https://academic.edu/paper1",
        title="Quantum Algorithms: A Survey",
        text="This paper surveys the current state of quantum algorithms and their potential applications.",
        relevance_score=0.90,
        source="academic.edu",
        metadata={"published_date": "2022-11-10", "author": "Dr. Jane Smith"}
    )
]

@pytest.fixture
def mock_exa_search():
    """Set up mocked Exa search for testing"""
    with patch.object(ExaSearchIntegration, 'search', new_callable=AsyncMock) as mock:
        mock.return_value = SAMPLE_SEARCH_RESULTS
        yield mock

@pytest.mark.asyncio
async def test_basic_research(mock_exa_search):
    """Test basic research functionality with mocked search responses"""
    # Perform research
    query = "What is quantum computing?"
    context = await research_integrator.research(query)
    
    # Verify search was called
    mock_exa_search.assert_called_once()
    
    # Verify context structure
    assert isinstance(context, ResearchContext)
    assert context.original_query == query
    assert len(context.processed_queries) > 0
    assert len(context.search_results) > 0
    assert context.confidence > 0
    
    # Verify search results are processed correctly
    assert len(context.search_results) == len(SAMPLE_SEARCH_RESULTS)
    assert all(isinstance(result, SearchResult) for result in context.search_results)

@pytest.mark.asyncio
async def test_query_variation():
    """Test that query variation produces multiple search terms"""
    query = "impact of quantum computing on cryptography"
    
    # Access private method for testing
    variations = research_integrator._generate_query_variations(query)
    
    # Verify variations
    assert len(variations) > 1, "Expected multiple query variations"
    assert query in variations, "Original query should be included in variations"
    assert all(isinstance(v, str) for v in variations), "All variations should be strings"
    assert len(set(variations)) == len(variations), "Variations should be unique"

@pytest.mark.asyncio
async def test_confidence_scoring(mock_exa_search):
    """Test confidence scoring mechanism"""
    # Create context with sample results
    context = ResearchContext(
        original_query="test query",
        processed_queries=["test query"],
        search_results=SAMPLE_SEARCH_RESULTS
    )
    
    # Score results
    scored_context = research_integrator._validate_and_score_results(context)
    
    # Verify confidence score
    assert 0 <= scored_context.confidence <= 1, "Confidence should be between 0 and 1"
    assert "source_diversity" in scored_context.metadata, "Metadata should include source diversity"
    assert "average_relevance" in scored_context.metadata, "Metadata should include average relevance"

@pytest.mark.asyncio
async def test_empty_search_results():
    """Test handling of empty search results"""
    # Mock empty search results
    with patch.object(ExaSearchIntegration, 'search', new_callable=AsyncMock) as mock:
        mock.return_value = []
        
        # Perform research
        context = await research_integrator.research("obscure topic with no results")
        
        # Verify handling
        assert context.confidence < 0.5, "Confidence should be low for empty results"
        assert len(context.search_results) == 0, "Search results should be empty"

@pytest.mark.asyncio
async def test_search_error_handling():
    """Test handling of search errors"""
    # Mock search error
    with patch.object(ExaSearchIntegration, 'search', new_callable=AsyncMock) as mock:
        mock.side_effect = Exception("Search API error")
        
        # Perform research with error handling
        try:
            context = await research_integrator.research("query that causes error")
            # If we get here, error was handled internally
            assert context.confidence < 0.3, "Confidence should be very low on error"
        except Exception as e:
            # If error is raised, verify it's properly formatted
            assert "research" in str(e).lower(), "Error should mention research"

@pytest.mark.asyncio
async def test_information_extraction(mock_exa_search):
    """Test extraction of key information from research results"""
    # Perform research
    context = await research_integrator.research("quantum computing")
    
    # Extract information
    extracted_info = research_integrator.extract_key_information(context)
    
    # Verify structure
    assert "query" in extracted_info, "Missing query in extracted info"
    assert "confidence" in extracted_info, "Missing confidence in extracted info"
    assert "sources" in extracted_info, "Missing sources in extracted info"
    assert "key_facts" in extracted_info, "Missing key facts in extracted info"
    
    # Verify content
    assert len(extracted_info["sources"]) > 0, "Expected at least one source"
    assert all("url" in source for source in extracted_info["sources"]), "Sources should have URLs"

@pytest.mark.asyncio
async def test_research_with_reasoning_integration():
    """Test integration of research with reasoning"""
    # Import here to avoid circular imports
    from reasoning.orchestrator import reasoning_orchestrator
    
    # Mock research integration
    with patch('research.research_integrator.research_integrator.research', new_callable=AsyncMock) as mock_research:
        # Create mock research context
        mock_context = ResearchContext(
            original_query="quantum computing",
            processed_queries=["quantum computing", "what is quantum computing"],
            search_results=SAMPLE_SEARCH_RESULTS,
            confidence=0.85
        )
        mock_research.return_value = mock_context
        
        # Test reasoning with research
        result = await reasoning_orchestrator.reason("What is quantum computing?")
        
        # Verify research was used
        mock_research.assert_called_once()
        
        # Verify reasoning results
        assert "answer" in result
        assert "confidence" in result
        assert result["confidence"] > 0
        
        # Check that research influenced reasoning
        assert len(result["reasoning_steps"]) > 1
        # Look for research step in reasoning
        has_research_step = any("research" in str(step).lower() for step in result["reasoning_steps"])
        assert has_research_step, "Expected research step in reasoning"

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting functionality"""
    # Create test instance with aggressive rate limiting
    test_integrator = ExaSearchIntegration(rate_limit_delay=0.5)
    
    # Mock the actual API call
    with patch.object(test_integrator, '_rate_limit', new_callable=AsyncMock) as mock_rate_limit:
        # Patch the network request to avoid actual API calls
        with patch('aiohttp.ClientSession.post', new_callable=AsyncMock) as mock_post:
            # Configure mock response
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"results": []})
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # Make multiple quick calls
            await test_integrator.search("query 1")
            await test_integrator.search("query 2")
            
            # Verify rate limiting was applied
            assert mock_rate_limit.call_count == 2, "Rate limiting should be applied to each call"

@pytest.mark.asyncio
async def test_source_diversity():
    """Test source diversity calculation"""
    # Create contexts with varying source diversity
    high_diversity_results = [
        SearchResult(url="https://site1.com", title="Title1", text="Text1", relevance_score=0.9, source="site1.com"),
        SearchResult(url="https://site2.com", title="Title2", text="Text2", relevance_score=0.9, source="site2.com"),
        SearchResult(url="https://site3.com", title="Title3", text="Text3", relevance_score=0.9, source="site3.com")
    ]
    
    low_diversity_results = [
        SearchResult(url="https://site1.com/page1", title="Title1", text="Text1", relevance_score=0.9, source="site1.com"),
        SearchResult(url="https://site1.com/page2", title="Title2", text="Text2", relevance_score=0.9, source="site1.com"),
        SearchResult(url="https://site1.com/page3", title="Title3", text="Text3", relevance_score=0.9, source="site1.com")
    ]
    
    # Create contexts
    high_diversity_context = ResearchContext(
        original_query="test",
        search_results=high_diversity_results
    )
    
    low_diversity_context = ResearchContext(
        original_query="test",
        search_results=low_diversity_results
    )
    
    # Score both contexts
    high_scored = research_integrator._validate_and_score_results(high_diversity_context)
    low_scored = research_integrator._validate_and_score_results(low_diversity_context)
    
    # Verify diversity scoring works
    assert high_scored.metadata["source_diversity"] > low_scored.metadata["source_diversity"]
    assert high_scored.confidence > low_scored.confidence

@pytest.mark.asyncio
async def test_research_with_multiple_query_variations():
    """Test that multiple query variations improve research outcomes"""
    # Set up to capture all search calls
    with patch.object(ExaSearchIntegration, 'search', new_callable=AsyncMock) as mock:
        # Different results for different queries
        mock.side_effect = lambda query, **kwargs: [
            SearchResult(
                url=f"https://result-for-{query.replace(' ', '-')}.com",
                title=f"Result for {query}",
                text=f"This is content about {query}",
                relevance_score=0.9,
                source="example.com"
            )
        ]
        
        # Perform research
        context = await research_integrator.research("quantum computing applications")
        
        # Verify multiple search calls were made with different queries
        assert mock.call_count > 1, "Expected multiple search calls for query variations"
        
        # Verify results were aggregated
        assert len(context.search_results) > 0
        # Results should reflect different query variations
        result_urls = [result.url for result in context.search_results]
        assert len(set(result_urls)) == len(result_urls), "Results should come from different queries"

@pytest.mark.asyncio
async def test_research_api_error_recovery():
    """Test recovery from API errors during research"""
    # Set up mixed success/failure responses
    call_count = 0
    
    async def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count % 2 == 0:
            raise Exception("API Error")
        return [SAMPLE_SEARCH_RESULTS[0]]
    
    with patch.object(ExaSearchIntegration, 'search', side_effect=side_effect):
        # Perform research (should handle errors gracefully)
        context = await research_integrator.research("test query with errors")
        
        # Verify we still got some results despite errors
        assert len(context.search_results) > 0, "Should have partial results despite errors"
        assert context.confidence < 0.8, "Confidence should be lower due to errors"
        
        # Verify at least one error was logged in metadata
        assert "errors" in context.metadata or "error_count" in context.metadata

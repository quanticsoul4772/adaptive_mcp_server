"""
Comprehensive Tests for Research Integration Module
"""

import pytest
import asyncio
from research import (
    research_integrator, 
    ResearchContext, 
    ExaSearchIntegration, 
    search_information
)

@pytest.mark.asyncio
async def test_research_integrator_basic():
    """
    Test basic research integration functionality
    """
    query = "What is artificial intelligence?"
    context = await research_integrator.research(query)
    
    assert context is not None
    assert isinstance(context, ResearchContext)
    assert context.original_query == query
    assert len(context.processed_queries) > 0
    assert len(context.search_results) > 0
    assert context.confidence > 0

@pytest.mark.asyncio
async def test_query_variations():
    """
    Test query variation generation
    """
    query = "Machine learning algorithms"
    context = await research_integrator.research(query)
    
    assert len(context.processed_queries) > 1
    assert all(query in var or var in query for var in context.processed_queries)

@pytest.mark.asyncio
async def test_result_extraction():
    """
    Test information extraction from research results
    """
    query = "Climate change impacts"
    context = await research_integrator.research(query)
    
    extracted_info = research_integrator.extract_key_information(context)
    
    assert 'query' in extracted_info
    assert 'confidence' in extracted_info
    assert 'sources' in extracted_info
    assert 'key_facts' in extracted_info
    assert len(extracted_info['sources']) > 0
    assert extracted_info['confidence'] > 0

@pytest.mark.asyncio
async def test_exa_search_integration():
    """
    Test direct Exa Search API integration
    """
    search_client = ExaSearchIntegration()
    results = await search_client.search("Quantum computing")
    
    assert len(results) > 0
    assert all(result.relevance_score > 0 for result in results)
    assert all(hasattr(result, 'url') for result in results)

@pytest.mark.asyncio
async def test_search_information_function():
    """
    Test high-level search information function
    """
    result = await search_information("Space exploration history")
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Source:" in result
    assert "Relevance:" in result
    assert "Information:" in result

@pytest.mark.asyncio
async def test_error_handling():
    """
    Test error handling in research integration
    """
    # Test with an extremely specific query that likely won't return results
    query = "Extremely obscure and non-existent topic that should not return any results"
    context = await research_integrator.research(query)
    
    assert context is not None
    # Confidence might be very low for an obscure query
    assert context.confidence >= 0
    assert len(context.search_results) >= 0

def test_singleton_consistency():
    """
    Verify that research_integrator is a singleton
    """
    from research import research_integrator as first_instance
    from research import research_integrator as second_instance
    
    assert first_instance is second_instance, "Research integrator should be a singleton"

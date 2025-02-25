"""
Advanced Research Integration Module

Provides sophisticated research capabilities for the Adaptive MCP Server.
Combines multiple search strategies, handles complex query generation,
and provides comprehensive information retrieval.
"""

from typing import List, Dict, Any, Optional
import asyncio
import re
import json
import logging
from dataclasses import dataclass, field

# External search and processing libraries
try:
    import nltk
    nltk_available = True
except ImportError:
    nltk_available = False
    print("Warning: NLTK not available, using fallback implementations")

try:
    from transformers import pipeline
    transformers_available = True
except ImportError:
    transformers_available = False
    print("Warning: Transformers not available, using fallback implementations")

# Local imports
from .exa_integration import ExaSearchIntegration, SearchResult
from ..core.errors import ResearchError

@dataclass
class ResearchContext:
    """
    Represents the context and state of a research query
    """
    original_query: str
    processed_queries: List[str] = field(default_factory=list)
    search_results: List[SearchResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0

class ResearchIntegrator:
    """
    Advanced research integration system with multiple search and 
    information processing capabilities
    """
    def __init__(
        self, 
        search_client: Optional[ExaSearchIntegration] = None,
        max_queries: int = 3,
        confidence_threshold: float = 0.6
    ):
        """
        Initialize the research integrator
        
        Args:
            search_client: Optional custom search client
            max_queries: Maximum number of query variations to attempt
            confidence_threshold: Minimum confidence for accepting research
        """
        self._search_client = search_client or ExaSearchIntegration()
        self._max_queries = max_queries
        self._confidence_threshold = confidence_threshold
        
        # Setup logging
        self._logger = logging.getLogger('mcp.research_integrator')
        
        # Setup NLP tools if available
        if nltk_available:
            nltk.download('punkt', quiet=True)
            nltk.download('wordnet', quiet=True)
        
        # Setup query expansion model if available
        if transformers_available:
            self._query_expander = pipeline('text-generation')
        else:
            self._query_expander = None

    def _generate_query_variations(self, original_query: str) -> List[str]:
        """
        Generate multiple query variations to improve search coverage
        
        Args:
            original_query: Original user query
        
        Returns:
            List of query variations
        """
        variations = [original_query]
        
        # Basic query transformations
        transformations = [
            # Make more generic
            lambda q: f"What is general information about {q}",
            # Make more specific
            lambda q: f"Detailed explanation of {q}"
        ]
        
        # Add transformer-based rephrasing if available
        if transformers_available and self._query_expander:
            transformations.append(
                # Rephrase with alternative language
                lambda q: self._query_expander(f"Rephrase: {q}", max_length=100)[0]['generated_text']
            )
        
        for transform in transformations:
            try:
                variation = transform(original_query)
                if variation not in variations:
                    variations.append(variation)
            except Exception as e:
                self._logger.warning(f"Query variation failed: {e}")
        
        return variations[:self._max_queries]

    async def _execute_search(
        self, 
        query: str, 
        context: Optional[ResearchContext] = None
    ) -> List[SearchResult]:
        """
        Execute search for a specific query
        
        Args:
            query: Search query
            context: Optional research context
        
        Returns:
            List of search results
        """
        try:
            results = await self._search_client.search(query)
            
            # Annotate results with query context if possible
            if context:
                for result in results:
                    result.metadata['source_query'] = query
            
            return results
        except Exception as e:
            self._logger.error(f"Search failed for query '{query}': {e}")
            return []

    def _validate_and_score_results(
        self, 
        context: ResearchContext
    ) -> ResearchContext:
        """
        Validate and score research results
        
        Args:
            context: Current research context
        
        Returns:
            Updated research context with confidence scoring
        """
        # Aggregate results
        all_results = context.search_results
        
        # Scoring mechanisms
        source_diversity_score = len({r.source for r in all_results}) / len(all_results) if all_results else 0
        relevance_score = sum(r.relevance_score for r in all_results) / len(all_results) if all_results else 0
        
        # Compute overall confidence
        confidence = (source_diversity_score * 0.4) + (relevance_score * 0.6)
        
        # Update context
        context.confidence = confidence
        context.metadata['source_diversity'] = source_diversity_score
        context.metadata['average_relevance'] = relevance_score
        
        return context

    async def research(self, query: str) -> ResearchContext:
        """
        Comprehensive research method
        
        Args:
            query: User's research query
        
        Returns:
            Researched context with results
        """
        # Initialize research context
        context = ResearchContext(original_query=query)
        
        try:
            # Generate query variations
            query_variations = self._generate_query_variations(query)
            context.processed_queries = query_variations
            
            # Parallel search execution
            search_tasks = [
                self._execute_search(variation, context) 
                for variation in query_variations
            ]
            
            # Wait for all searches to complete
            search_results = await asyncio.gather(*search_tasks)
            
            # Flatten and deduplicate results
            context.search_results = list({
                result.url: result 
                for results in search_results 
                for result in results
            }.values())
            
            # Validate and score results
            context = self._validate_and_score_results(context)
            
            # Log research summary
            self._logger.info(
                f"Research completed for '{query}'. "
                f"Confidence: {context.confidence:.2f}, "
                f"Sources: {len(context.search_results)}"
            )
            
            return context
        
        except Exception as e:
            self._logger.error(f"Research failed: {e}")
            raise ResearchError(f"Unable to complete research for query: {query}")

    def extract_key_information(
        self, 
        context: ResearchContext, 
        max_sources: int = 3
    ) -> Dict[str, Any]:
        """
        Extract key information from research results
        
        Args:
            context: Research context with results
            max_sources: Maximum number of sources to process
        
        Returns:
            Extracted key information
        """
        # Sort results by relevance
        sorted_results = sorted(
            context.search_results, 
            key=lambda r: r.relevance_score, 
            reverse=True
        )
        
        # Process top sources
        extracted_info = {
            'query': context.original_query,
            'confidence': context.confidence,
            'sources': [],
            'key_facts': []
        }
        
        for result in sorted_results[:max_sources]:
            source_info = {
                'url': result.url,
                'title': result.title,
                'relevance': result.relevance_score
            }
            extracted_info['sources'].append(source_info)
            
            # Basic fact extraction (could be enhanced with NLP)
            facts = re.findall(r'\b[A-Z][^.!?]+[.!?]', result.text)
            extracted_info['key_facts'].extend(facts[:3])
        
        return extracted_info

# Singleton research integrator
research_integrator = ResearchIntegrator()

"""
Enhanced Search Integration Module

Provides advanced search capabilities with query refinement, 
result validation, and source corroboration.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
import re
from mcp.types import McpError

@dataclass
class SearchResult:
    """Structured search result with metadata"""
    content: str
    source_url: str
    relevance_score: float
    credibility_score: float
    timestamp: Optional[str] = None

@dataclass
class QueryRefinement:
    """Represents a refined search query"""
    query: str
    focus_area: str
    priority: float
    required_terms: Set[str]

class EnhancedSearchManager:
    """
    Manages advanced search operations with query refinement and result validation.
    
    Features:
    - Query analysis and refinement
    - Multiple search providers
    - Result corroboration
    - Source credibility assessment
    """
    
    def __init__(self):
        self.credible_domains = {
            "edu": 0.9,
            "gov": 0.9,
            "org": 0.7,
            "wikipedia.org": 0.75
        }
        
        self.query_markers = {
            "what": "definition",
            "why": "explanation",
            "how": "process",
            "when": "temporal",
            "where": "location",
            "who": "entity"
        }
    
    async def search(self, question: str, min_results: int = 3) -> List[SearchResult]:
        """
        Perform enhanced search with query refinement and validation.
        
        Args:
            question: Question to research
            min_results: Minimum number of results required
            
        Returns:
            List of validated search results
            
        Raises:
            McpError: If search fails or insufficient results
        """
        try:
            # Step 1: Analyze and refine query
            refined_queries = self._refine_query(question)
            
            # Step 2: Search with multiple providers
            results = []
            for query in refined_queries:
                # Try Exa search first
                exa_results = await self._search_exa(query)
                results.extend(exa_results)
                
                # If needed, try Brave search as backup
                if len(results) < min_results:
                    brave_results = await self._search_brave(query)
                    results.extend(brave_results)
            
            # Step 3: Validate and score results
            validated_results = self._validate_results(results)
            
            # Step 4: Ensure sufficient coverage
            if not validated_results:
                raise McpError("No valid results found")
            
            if len(validated_results) < min_results:
                # Try one more time with broader queries
                broad_query = self._broaden_query(question)
                additional_results = await self._search_exa(broad_query)
                validated_results.extend(
                    self._validate_results(additional_results)
                )
            
            # Step 5: Sort by relevance and credibility
            validated_results.sort(
                key=lambda r: (r.relevance_score + r.credibility_score) / 2,
                reverse=True
            )
            
            return validated_results[:min_results]
            
        except Exception as e:
            raise McpError(f"Enhanced search failed: {str(e)}")

    def _refine_query(self, question: str) -> List[QueryRefinement]:
        """Generate refined search queries based on question analysis"""
        queries = []
        question_lower = question.lower()
        
        # Identify question type
        question_type = next(
            (qtype for term, qtype in self.query_markers.items()
             if question_lower.startswith(term)),
            "general"
        )
        
        # Extract key terms
        key_terms = self._extract_key_terms(question)
        
        # Generate primary query
        primary_query = QueryRefinement(
            query=question,
            focus_area=question_type,
            priority=1.0,
            required_terms=key_terms
        )
        queries.append(primary_query)
        
        # Generate supporting queries
        if question_type == "definition":
            queries.append(QueryRefinement(
                query=f"define {' '.join(key_terms)}",
                focus_area="definition",
                priority=0.8,
                required_terms=key_terms
            ))
        elif question_type == "process":
            queries.append(QueryRefinement(
                query=f"steps to {question}",
                focus_area="process",
                priority=0.8,
                required_terms=key_terms
            ))
        
        return queries

    def _broaden_query(self, question: str) -> QueryRefinement:
        """Create a broader version of the query"""
        # Remove specific constraints
        broader = re.sub(r'specifically|exactly|precisely', '', question)
        
        # Remove temporal constraints
        broader = re.sub(r'in \d{4}|this year|last year', '', broader)
        
        key_terms = self._extract_key_terms(broader)
        
        return QueryRefinement(
            query=broader.strip(),
            focus_area="general",
            priority=0.7,
            required_terms=key_terms
        )

    async def _search_exa(self, query: QueryRefinement) -> List[SearchResult]:
        """Search using Exa Search API"""
        from mcp.tools import search
        
        try:
            results = await search(query=query.query, numResults=5)
            
            return [
                SearchResult(
                    content=result.get('text', ''),
                    source_url=result.get('url', ''),
                    relevance_score=self._calculate_relevance(
                        result.get('text', ''),
                        query.required_terms
                    ),
                    credibility_score=self._assess_credibility(result.get('url', '')),
                    timestamp=result.get('date')
                )
                for result in results
            ]
        except Exception as e:
            print(f"Exa search failed: {str(e)}")
            return []

    async def _search_brave(self, query: QueryRefinement) -> List[SearchResult]:
        """Search using Brave Search API as backup"""
        from mcp.tools import brave_web_search
        
        try:
            results = await brave_web_search(query=query.query, count=5)
            
            return [
                SearchResult(
                    content=result.get('snippet', ''),
                    source_url=result.get('url', ''),
                    relevance_score=self._calculate_relevance(
                        result.get('snippet', ''),
                        query.required_terms
                    ),
                    credibility_score=self._assess_credibility(result.get('url', '')),
                    timestamp=None
                )
                for result in results
            ]
        except Exception as e:
            print(f"Brave search failed: {str(e)}")
            return []

    def _validate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Validate and filter search results"""
        validated = []
        seen_content = set()
        
        for result in results:
            # Skip if content is too short
            if len(result.content.split()) < 10:
                continue
                
            # Skip duplicate content
            content_hash = hash(result.content.lower())
            if content_hash in seen_content:
                continue
            seen_content.add(content_hash)
            
            # Require minimum scores
            if (result.relevance_score + result.credibility_score) / 2 >= 0.5:
                validated.append(result)
        
        return validated

    def _calculate_relevance(self, text: str, required_terms: Set[str]) -> float:
        """Calculate relevance score for a result"""
        if not text or not required_terms:
            return 0.0
            
        text_lower = text.lower()
        words = set(text_lower.split())
        
        # Calculate term overlap
        overlap = len(required_terms.intersection(words))
        term_score = overlap / len(required_terms)
        
        # Adjust for text length
        length_score = min(1.0, len(text.split()) / 50)
        
        return (term_score * 0.7 + length_score * 0.3)

    def _assess_credibility(self, url: str) -> float:
        """Assess credibility of a source"""
        if not url:
            return 0.0
            
        # Check for credible domains
        for domain, score in self.credible_domains.items():
            if domain in url:
                return score
        
        # Basic scoring for other domains
        if url.endswith('.com'):
            return 0.6
        elif url.endswith('.net'):
            return 0.5
        
        return 0.4

    def _extract_key_terms(self, text: str) -> Set[str]:
        """Extract key terms from text"""
        # Remove common words
        common_words = {
            'the', 'is', 'at', 'which', 'on', 'in', 'a', 'an', 'and',
            'or', 'but', 'what', 'why', 'how', 'when', 'where', 'who'
        }
        
        words = text.lower().split()
        return {w for w in words if len(w) > 3 and w not in common_words}

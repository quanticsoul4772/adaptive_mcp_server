"""
Lateral (Creative) Reasoning Module

Implements creative thinking strategies to generate novel solutions and perspectives.
Uses techniques like analogy, random association, and perspective shifting.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
import random
from mcp.types import McpError

@dataclass
class CreativeApproach:
    """Represents a specific creative thinking technique"""
    name: str
    description: str
    strategy: callable
    creativity_weight: float = 1.0

@dataclass
class CreativeResult:
    """Result from a creative thinking approach"""
    idea: str
    originality_score: float
    usefulness_score: float
    reasoning_path: List[str]
    associations: List[str]

class LateralReasoner:
    """
    Implements creative reasoning using various lateral thinking techniques.
    
    Features:
    - Multiple creative thinking strategies
    - Analogy generation
    - Random association
    - Perspective shifting
    - Idea combination
    """
    
    def __init__(self):
        self.approaches: List[CreativeApproach] = []
        self._setup_approaches()
        
    def _setup_approaches(self):
        """Initialize creative thinking approaches"""
        self.approaches = [
            CreativeApproach(
                name="analogy",
                description="Uses analogical reasoning to find novel solutions",
                strategy=self._analogical_thinking,
                creativity_weight=1.0
            ),
            CreativeApproach(
                name="random_association",
                description="Generates ideas through random connections",
                strategy=self._random_association,
                creativity_weight=0.8
            ),
            CreativeApproach(
                name="perspective_shift",
                description="Views problem from different perspectives",
                strategy=self._perspective_shift,
                creativity_weight=0.9
            )
        ]

    async def reason(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate creative solutions using lateral thinking.
        
        Args:
            question: Question to reason about
            context: Optional additional context
            
        Returns:
            Dict containing creative solution and reasoning process
        """
        try:
            # Generate ideas using each approach
            results = []
            for approach in self.approaches:
                result = await approach.strategy(question, context)
                if result:
                    results.append(result)
            
            if not results:
                raise McpError("No creative solutions generated")
            
            # Select best idea based on originality and usefulness
            best_result = max(
                results,
                key=lambda r: (r.originality_score * 0.6 + r.usefulness_score * 0.4)
            )
            
            # Validate the creative solution
            from ..validators.basic_validator import validate_answer
            validation = validate_answer(question, best_result.idea)
            
            return {
                "answer": best_result.idea,
                "confidence": validation["confidence"] * best_result.originality_score,
                "reasoning_steps": [
                    {"step": "Path", "output": step}
                    for step in best_result.reasoning_path
                ],
                "metadata": {
                    "approach": "lateral",
                    "originality_score": best_result.originality_score,
                    "usefulness_score": best_result.usefulness_score,
                    "associations": best_result.associations,
                    "validation": validation
                }
            }
            
        except Exception as e:
            raise McpError(f"Lateral reasoning failed: {str(e)}")

    async def _analogical_thinking(
        self,
        question: str,
        context: Optional[Dict[str, Any]]
    ) -> Optional[CreativeResult]:
        """Generate ideas through analogical reasoning"""
        # Find related domains
        from ..research.exa_integration import search_information
        search_terms = self._extract_key_concepts(question)
        analogies = []
        
        for term in search_terms[:2]:  # Limit searches
            results = await search_information(f"analogy for {term}")
            analogies.extend(self._extract_analogies(results))
        
        if not analogies:
            return None
            
        # Select and apply best analogy
        best_analogy = random.choice(analogies)  # Could be more sophisticated
        solution = f"Drawing an analogy to {best_analogy}, we can say that {question} might be similar to..."
        
        return CreativeResult(
            idea=solution,
            originality_score=0.8,  # Analogies are moderately original
            usefulness_score=0.7,
            reasoning_path=[
                f"Identified key concepts: {', '.join(search_terms)}",
                f"Found analogy: {best_analogy}",
                "Applied analogical reasoning"
            ],
            associations=[best_analogy]
        )

    async def _random_association(
        self,
        question: str,
        context: Optional[Dict[str, Any]]
    ) -> Optional[CreativeResult]:
        """Generate ideas through random association"""
        # Get random related concepts
        from ..research.exa_integration import search_information
        base_results = await search_information(question)
        
        # Extract key terms
        terms = self._extract_key_terms(base_results)
        if not terms:
            return None
            
        # Generate random associations
        selected_terms = random.sample(terms, min(3, len(terms)))
        associations = []
        
        for term in selected_terms:
            results = await search_information(f"unexpected uses of {term}")
            associations.extend(self._extract_key_terms(results))
        
        # Combine associations creatively
        idea = f"Combining the concepts of {', '.join(selected_terms)}, we could..."
        
        return CreativeResult(
            idea=idea,
            originality_score=0.9,  # Random associations tend to be very original
            usefulness_score=0.5,  # But may be less practical
            reasoning_path=[
                f"Selected random terms: {', '.join(selected_terms)}",
                "Generated associations",
                "Combined ideas creatively"
            ],
            associations=associations
        )

    async def _perspective_shift(
        self,
        question: str,
        context: Optional[Dict[str, Any]]
    ) -> Optional[CreativeResult]:
        """Generate ideas by shifting perspectives"""
        perspectives = [
            "efficiency",
            "sustainability",
            "innovation",
            "simplicity",
            "user experience"
        ]
        
        # Select random perspectives
        selected_perspectives = random.sample(perspectives, 2)
        insights = []
        
        # Analyze from each perspective
        for perspective in selected_perspectives:
            from ..research.exa_integration import search_information
            results = await search_information(f"{question} from {perspective} perspective")
            insights.append(f"{perspective}: {results}")
        
        if not insights:
            return None
            
        # Combine insights
        idea = f"Looking at this from multiple perspectives ({', '.join(selected_perspectives)}), we can see that..."
        
        return CreativeResult(
            idea=idea,
            originality_score=0.7,
            usefulness_score=0.8,  # Multiple perspectives often yield practical insights
            reasoning_path=[
                f"Selected perspectives: {', '.join(selected_perspectives)}",
                "Analyzed from each perspective",
                "Synthesized insights"
            ],
            associations=selected_perspectives
        )

    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text"""
        # Simple word-based extraction - could be more sophisticated
        words = text.lower().split()
        # Filter out common words and short words
        return [w for w in words if len(w) > 4 and w not in {"the", "and", "that", "with"}]

    def _extract_analogies(self, text: str) -> List[str]:
        """Extract potential analogies from text"""
        # Look for phrases that often indicate analogies
        markers = ["like", "similar to", "just as", "comparable to"]
        analogies = []
        
        sentences = text.split('.')
        for sentence in sentences:
            for marker in markers:
                if marker in sentence.lower():
                    analogies.append(sentence.strip())
                    break
                    
        return analogies

    def _extract_key_terms(self, text: str) -> Set[str]:
        """Extract unique key terms from text"""
        # Basic term extraction - could be enhanced
        words = text.lower().split()
        return {w for w in words if len(w) > 4}

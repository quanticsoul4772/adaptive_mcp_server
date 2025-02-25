"""
Abductive Reasoning Module

Implements hypothesis-based reasoning that forms initial hypotheses
and then searches for supporting evidence.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
from mcp.types import McpError

@dataclass
class Hypothesis:
    """Represents a potential explanation or answer"""
    statement: str
    confidence: float
    evidence: List[str]
    counter_evidence: List[str]

class AbductiveReasoner:
    """
    Implements hypothesis-driven reasoning.
    
    Process:
    1. Generate initial hypotheses
    2. Search for supporting evidence
    3. Look for counter-evidence
    4. Refine hypotheses
    5. Select best explanation
    """
    
    def __init__(self, max_hypotheses: int = 3):
        self.max_hypotheses = max_hypotheses
        self.hypotheses: List[Hypothesis] = []
        
    async def reason(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform abductive reasoning to find best explanation.
        
        Args:
            question: Question to reason about
            context: Optional additional context
            
        Returns:
            Dict containing best explanation and reasoning process
            
        Raises:
            McpError: If reasoning fails
        """
        try:
            # Step 1: Generate initial hypotheses
            self.hypotheses = await self._generate_hypotheses(question)
            
            # Step 2: Gather evidence for each hypothesis
            evidence_tasks = [
                self._gather_evidence(h.statement)
                for h in self.hypotheses
            ]
            evidence_results = await asyncio.gather(*evidence_tasks)
            
            # Step 3: Update hypotheses with evidence
            for hypothesis, (supporting, counter) in zip(self.hypotheses, evidence_results):
                hypothesis.evidence.extend(supporting)
                hypothesis.counter_evidence.extend(counter)
                
                # Adjust confidence based on evidence quality
                evidence_score = self._evaluate_evidence(hypothesis.evidence, hypothesis.counter_evidence)
                hypothesis.confidence *= evidence_score
            
            # Step 4: Select best hypothesis
            best_hypothesis = max(self.hypotheses, key=lambda h: h.confidence)
            
            # Step 5: Validate final answer
            from ..validators.basic_validator import validate_answer
            validation = validate_answer(question, best_hypothesis.statement)
            
            return {
                "answer": best_hypothesis.statement,
                "confidence": min(best_hypothesis.confidence, validation["confidence"]),
                "reasoning_steps": [
                    {
                        "step": "Generate hypotheses",
                        "output": f"Generated {len(self.hypotheses)} potential explanations"
                    },
                    {
                        "step": "Gather evidence",
                        "output": f"Found {len(best_hypothesis.evidence)} supporting and {len(best_hypothesis.counter_evidence)} counter evidence"
                    },
                    {
                        "step": "Select best",
                        "output": f"Selected hypothesis with confidence {best_hypothesis.confidence:.2f}"
                    }
                ],
                "metadata": {
                    "approach": "abductive",
                    "total_hypotheses": len(self.hypotheses),
                    "evidence_summary": {
                        "supporting": len(best_hypothesis.evidence),
                        "counter": len(best_hypothesis.counter_evidence)
                    },
                    "validation": validation
                }
            }
            
        except Exception as e:
            raise McpError(f"Abductive reasoning failed: {str(e)}")

    async def _generate_hypotheses(self, question: str) -> List[Hypothesis]:
        """Generate initial hypotheses based on the question"""
        # Use search to help generate hypotheses
        from ..research.exa_integration import search_information
        search_results = await search_information(question)
        
        # Extract potential hypotheses from search results
        hypotheses = []
        
        # Split into sentences and filter for potential answers
        sentences = search_results.split('.')
        for sentence in sentences[:self.max_hypotheses]:
            if len(sentence.split()) > 5:  # Basic quality check
                hypotheses.append(Hypothesis(
                    statement=sentence.strip(),
                    confidence=0.5,  # Initial confidence
                    evidence=[],
                    counter_evidence=[]
                ))
        
        return hypotheses[:self.max_hypotheses]

    async def _gather_evidence(self, hypothesis: str) -> Tuple[List[str], List[str]]:
        """
        Gather supporting and counter evidence for a hypothesis.
        
        Returns:
            Tuple of (supporting_evidence, counter_evidence)
        """
        from ..research.exa_integration import search_information
        
        # Search for supporting evidence
        supporting_query = f"evidence that {hypothesis}"
        supporting_results = await search_information(supporting_query)
        
        # Search for potential counter evidence
        counter_query = f"evidence against {hypothesis}"
        counter_results = await search_information(counter_query)
        
        # Process results into distinct pieces of evidence
        supporting = [s.strip() for s in supporting_results.split('\n') if s.strip()]
        counter = [s.strip() for s in counter_results.split('\n') if s.strip()]
        
        return supporting, counter

    def _evaluate_evidence(self, supporting: List[str], counter: List[str]) -> float:
        """
        Evaluate evidence quality and compute confidence adjustment.
        
        Returns:
            Confidence multiplier between 0 and 1
        """
        if not supporting and not counter:
            return 0.5
            
        # Weight by evidence quality and quantity
        total_evidence = len(supporting) + len(counter)
        supporting_ratio = len(supporting) / total_evidence if total_evidence > 0 else 0.5
        
        # Adjust based on evidence strength
        avg_supporting_length = sum(len(s.split()) for s in supporting) / len(supporting) if supporting else 0
        avg_counter_length = sum(len(s.split()) for s in counter) / len(counter) if counter else 0
        
        # Evidence quality score (0.2-1.0)
        quality_score = 0.2 + 0.8 * (
            min(1.0, (avg_supporting_length + avg_counter_length) / 50)
        )
        
        # Combine ratio and quality
        confidence = 0.3 + (0.7 * supporting_ratio * quality_score)
        
        return min(1.0, max(0.1, confidence))

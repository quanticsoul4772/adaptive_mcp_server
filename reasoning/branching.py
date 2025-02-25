"""
Branching Reasoning Module

Implements parallel reasoning paths with different approaches to find the best solution.
Combines multiple strategies and picks the most confident result.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
from mcp.types import McpError

@dataclass
class BranchingPath:
    """Represents a single reasoning branch"""
    name: str
    description: str
    strategy: callable
    weight: float = 1.0

@dataclass
class BranchResult:
    """Result from a single branch execution"""
    path_name: str
    answer: str
    confidence: float
    reasoning_steps: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class BranchingReasoner:
    """
    Implements multi-path reasoning by trying different approaches in parallel.
    
    Features:
    - Parallel execution of multiple reasoning strategies
    - Weighted combination of results
    - Confidence-based selection
    """
    
    def __init__(self):
        self.paths: List[BranchingPath] = []
        self._setup_default_paths()
        
    def _setup_default_paths(self):
        """Initialize default reasoning paths"""
        self.paths = [
            BranchingPath(
                name="factual",
                description="Direct fact-based reasoning",
                strategy=self._factual_reasoning,
                weight=1.0
            ),
            BranchingPath(
                name="analytical",
                description="Analytical breakdown approach",
                strategy=self._analytical_reasoning,
                weight=0.8
            ),
            BranchingPath(
                name="comparative",
                description="Comparison-based reasoning",
                strategy=self._comparative_reasoning,
                weight=0.6
            )
        ]

    async def reason(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute multiple reasoning paths and select best result.
        
        Args:
            question: Question to reason about
            context: Optional additional context
            
        Returns:
            Dict containing best answer and reasoning process
            
        Raises:
            McpError: If all reasoning paths fail
        """
        try:
            # Execute all paths in parallel
            tasks = [
                self._execute_path(path, question, context)
                for path in self.paths
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out failures and sort by confidence
            valid_results = [
                r for r in results 
                if isinstance(r, BranchResult)
            ]
            
            if not valid_results:
                raise McpError("All reasoning paths failed")
            
            # Select best result
            best_result = max(
                valid_results,
                key=lambda r: r.confidence * next(
                    p.weight for p in self.paths if p.name == r.path_name
                )
            )
            
            return {
                "answer": best_result.answer,
                "confidence": best_result.confidence,
                "reasoning_steps": best_result.reasoning_steps,
                "metadata": {
                    **best_result.metadata,
                    "selected_path": best_result.path_name,
                    "attempted_paths": len(results),
                    "successful_paths": len(valid_results)
                }
            }
            
        except Exception as e:
            raise McpError(f"Branching reasoning failed: {str(e)}")

    async def _execute_path(
        self, 
        path: BranchingPath,
        question: str,
        context: Optional[Dict[str, Any]]
    ) -> BranchResult:
        """Execute a single reasoning path"""
        try:
            result = await path.strategy(question, context)
            return BranchResult(
                path_name=path.name,
                answer=result["answer"],
                confidence=result["confidence"],
                reasoning_steps=result["reasoning_steps"],
                metadata=result.get("metadata", {})
            )
        except Exception as e:
            # Log error but don't fail entire process
            print(f"Path {path.name} failed: {str(e)}")
            return None

    async def _factual_reasoning(
        self,
        question: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Direct fact-based reasoning approach.
        Focuses on finding and verifying factual information.
        """
        from ..research.exa_integration import search_information
        
        # Get factual information
        facts = await search_information(question)
        
        # Validate facts
        from ..validators.basic_validator import validate_answer
        validation = validate_answer(question, facts)
        
        return {
            "answer": facts,
            "confidence": validation["confidence"],
            "reasoning_steps": [
                {
                    "step": "Gather facts",
                    "output": "Retrieved factual information"
                },
                {
                    "step": "Validate facts",
                    "output": validation["explanation"]
                }
            ],
            "metadata": {
                "approach": "factual",
                "validation_details": validation
            }
        }

    async def _analytical_reasoning(
        self,
        question: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analytical breakdown approach.
        Breaks question into components and analyzes each part.
        """
        # Break down question
        components = question.split()
        key_terms = [w for w in components if len(w) > 3]
        
        # Research each key term
        from ..research.exa_integration import search_information
        research_results = []
        for term in key_terms[:2]:  # Limit to avoid too many searches
            info = await search_information(term)
            research_results.append(info)
            
        # Combine findings
        combined_answer = "\n".join(research_results)
        
        # Validate
        from ..validators.basic_validator import validate_answer
        validation = validate_answer(question, combined_answer)
        
        return {
            "answer": combined_answer,
            "confidence": validation["confidence"],
            "reasoning_steps": [
                {
                    "step": "Question breakdown",
                    "output": f"Key terms: {', '.join(key_terms)}"
                },
                {
                    "step": "Component analysis",
                    "output": "Analyzed individual components"
                }
            ],
            "metadata": {
                "approach": "analytical",
                "key_terms": key_terms
            }
        }

    async def _comparative_reasoning(
        self,
        question: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Comparison-based reasoning approach.
        Looks for similar questions/answers and adapts them.
        """
        # Modify question to find similar cases
        general_question = question.replace("specific", "").replace("exactly", "")
        
        # Get general case information
        from ..research.exa_integration import search_information
        general_info = await search_information(general_question)
        
        # Adapt to specific case
        specific_answer = f"Based on similar cases: {general_info}"
        
        # Validate
        from ..validators.basic_validator import validate_answer
        validation = validate_answer(question, specific_answer)
        
        return {
            "answer": specific_answer,
            "confidence": validation["confidence"] * 0.9,  # Reduce confidence due to adaptation
            "reasoning_steps": [
                {
                    "step": "Find similar cases",
                    "output": "Located relevant examples"
                },
                {
                    "step": "Adapt solution",
                    "output": "Adapted general solution to specific case"
                }
            ],
            "metadata": {
                "approach": "comparative",
                "original_question": question,
                "generalized_question": general_question
            }
        }

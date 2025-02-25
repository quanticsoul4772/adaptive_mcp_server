"""
Sequential Reasoning Module

This module implements a step-by-step reasoning approach using the MCP protocol.
It combines research capabilities with validation to produce well-reasoned answers.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from mcp.types import McpError, ResourceNotFoundError

@dataclass
class ReasoningStep:
    """Represents a single step in the reasoning process"""
    step: str
    output: str
    confidence: float

class SequentialReasoner:
    """
    Implements sequential reasoning using research and validation.
    
    The reasoner follows these steps:
    1. Parse and understand the question
    2. Research relevant information
    3. Form initial answer
    4. Validate the answer
    """

    def __init__(self):
        self.steps: List[ReasoningStep] = []
        self.confidence = 0.0

    async def reason(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform sequential reasoning on a given question.
        
        Args:
            question: The input question to reason about
            context: Optional additional context
            
        Returns:
            Dict containing reasoning steps and final answer
            
        Raises:
            McpError: If reasoning fails
            ResourceNotFoundError: If required resources are unavailable
        """
        try:
            # Step 1: Parse and understand the question
            self.steps.append(ReasoningStep(
                step="Parse question",
                output=f"Processing question: {question}",
                confidence=1.0
            ))

            # Step 2: Research using Exa Search
            from ..research.exa_integration import search_information
            try:
                search_results = await search_information(question)
                self.steps.append(ReasoningStep(
                    step="Research",
                    output=f"Found relevant information: {search_results}",
                    confidence=0.8
                ))
            except ResourceNotFoundError:
                # Fallback if search fails
                self.steps.append(ReasoningStep(
                    step="Research",
                    output="Unable to find external information",
                    confidence=0.3
                ))
                search_results = ""

            # Step 3: Form initial answer
            initial_answer = self._form_answer(search_results)
            self.steps.append(ReasoningStep(
                step="Form answer",
                output=initial_answer,
                confidence=0.7
            ))

            # Step 4: Validate answer
            from ..validators.basic_validator import validate_answer
            validation_result = validate_answer(question, initial_answer)
            self.confidence = validation_result["confidence"]

            return {
                "answer": initial_answer,
                "confidence": self.confidence,
                "reasoning_steps": [
                    {
                        "step": step.step,
                        "output": step.output,
                        "confidence": step.confidence
                    }
                    for step in self.steps
                ],
                "metadata": {
                    "strategy_used": "sequential",
                    "processing_time": None,  # To be implemented
                    "sources": []  # To be implemented
                }
            }
        except Exception as e:
            raise McpError(f"Sequential reasoning failed: {str(e)}")

    def _form_answer(self, research_results: str) -> str:
        """
        Form an answer based on research results.
        
        Args:
            research_results: Results from research phase
            
        Returns:
            Formatted answer
        """
        if not research_results.strip():
            return "Unable to form a complete answer due to insufficient information"
        return research_results.strip()

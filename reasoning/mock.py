"""
Mock reasoning modules for testing
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import asyncio
import re


class ReasoningStrategy(Enum):
    """Enumeration of available reasoning strategies"""
    SEQUENTIAL = auto()
    BRANCHING = auto()
    ABDUCTIVE = auto()
    LATERAL = auto()
    LOGICAL = auto()


@dataclass
class StrategyResult:
    """Represents the result of a single reasoning strategy"""
    strategy: ReasoningStrategy
    answer: str
    confidence: float
    reasoning_steps: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    research_context: Optional[Any] = None


class MockOrchestrator:
    """Mock reasoning orchestrator for testing"""
    
    def _select_strategies(self, question: str) -> List[ReasoningStrategy]:
        """
        Select appropriate reasoning strategies based on question characteristics
        """
        strategies = []
        
        # Logical reasoning indicators
        if re.search(r'\b(if|then|therefore|implies|because)\b', question, re.IGNORECASE):
            strategies.append(ReasoningStrategy.LOGICAL)
        
        # Abductive reasoning indicators
        if re.search(r'\b(why|explain|reason|cause)\b', question, re.IGNORECASE):
            strategies.append(ReasoningStrategy.ABDUCTIVE)
        
        # Lateral (creative) thinking indicators
        if re.search(r'\b(creative|innovative|new approach|alternative)\b', question, re.IGNORECASE):
            strategies.append(ReasoningStrategy.LATERAL)
        
        # Branching for complex questions
        if len(question.split()) > 10:
            strategies.append(ReasoningStrategy.BRANCHING)
        
        # Fallback to sequential if no specific strategy detected
        if not strategies:
            strategies.append(ReasoningStrategy.SEQUENTIAL)
        
        return strategies
    
    async def reason(self, question: str) -> Dict[str, Any]:
        """
        Mock reasoning method
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
            
        # Get strategies
        strategies = self._select_strategies(question)
        
        # Generate mock steps based on strategies
        steps = []
        for strategy in strategies:
            steps.append({
                "step": f"{strategy.name} analysis",
                "output": f"Performed {strategy.name.lower()} analysis on '{question}'",
                "confidence": 0.8
            })
        
        # Generate mock answer
        answer = f"Based on {', '.join(s.name.lower() for s in strategies)} analysis, "
        answer += f"the answer to '{question}' is: This is a test answer that incorporates "
        
        # Add some keywords from the question to make it relevant
        keywords = [word for word in question.split() if len(word) > 3]
        if keywords:
            answer += f"key concepts including {', '.join(keywords[:3])}."
        else:
            answer += "relevant concepts."
        
        result = {
            "answer": answer,
            "confidence": 0.85,
            "reasoning_steps": steps,
            "metadata": {
                "strategies_used": [s.name for s in strategies],
                "processing_time": 0.5,
                "total_strategies": len(strategies)
            }
        }
        
        # Simulate async processing
        await asyncio.sleep(0.1)
        
        return result


# Singleton instance
reasoning_orchestrator = MockOrchestrator()

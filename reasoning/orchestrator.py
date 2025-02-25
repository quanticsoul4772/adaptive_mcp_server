"""
Reasoning Orchestrator with Integrated Research Capabilities

Manages multiple reasoning strategies and incorporates research integration.
"""

from typing import Dict, Any, List, Optional
from enum import Enum, auto
from dataclasses import dataclass, field
import asyncio
import logging
import re

# Local imports
from ..research import research_integrator, ResearchContext

# Try to import advanced_validator, use mock if not available
try:
    from ..validators import advanced_validator
    validator_available = True
except ImportError:
    validator_available = False
    print("Warning: Advanced validator not available, using mock implementation")
    from ..validators import mock as advanced_validator
from .sequential import SequentialReasoner
from .branching import BranchingReasoner
from .abductive import AbductiveReasoner
from .lateral import LateralReasoner
from .logical import LogicalReasoner

class ReasoningStrategy(Enum):
    """
    Enumeration of available reasoning strategies
    """
    SEQUENTIAL = auto()
    BRANCHING = auto()
    ABDUCTIVE = auto()
    LATERAL = auto()
    LOGICAL = auto()

@dataclass
class StrategyResult:
    """
    Represents the result of a single reasoning strategy
    """
    strategy: ReasoningStrategy
    answer: str
    confidence: float
    reasoning_steps: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    research_context: Optional[ResearchContext] = None

class ReasoningOrchestrator:
    """
    Orchestrates reasoning across multiple strategies with integrated research
    """
    def __init__(self):
        """
        Initialize reasoning modules and research integration
        """
        self._logger = logging.getLogger('mcp.reasoning_orchestrator')
        
        # Initialize reasoning modules
        self._reasoning_modules = {
            ReasoningStrategy.SEQUENTIAL: SequentialReasoner(),
            ReasoningStrategy.BRANCHING: BranchingReasoner(),
            ReasoningStrategy.ABDUCTIVE: AbductiveReasoner(),
            ReasoningStrategy.LATERAL: LateralReasoner(),
            ReasoningStrategy.LOGICAL: LogicalReasoner()
        }

    def _select_strategies(self, question: str) -> List[ReasoningStrategy]:
        """
        Select appropriate reasoning strategies based on question characteristics
        
        Args:
            question: Input question to analyze
        
        Returns:
            List of recommended reasoning strategies
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

    async def _execute_single_strategy(
        self, 
        strategy: ReasoningStrategy, 
        question: str, 
        research_context: Optional[ResearchContext] = None
    ) -> StrategyResult:
        """
        Execute a single reasoning strategy
        
        Args:
            strategy: Reasoning strategy to execute
            question: Input question
            research_context: Optional research context
        
        Returns:
            Result of the reasoning strategy
        """
        try:
            module = self._reasoning_modules[strategy]
            
            # Inject research context if available
            if research_context:
                result = await module.reason(
                    question, 
                    context={'research': research_context}
                )
            else:
                result = await module.reason(question)
            
            return StrategyResult(
                strategy=strategy,
                answer=result.get('answer', ''),
                confidence=result.get('confidence', 0.0),
                reasoning_steps=result.get('reasoning_steps', []),
                metadata=result.get('metadata', {}),
                research_context=research_context
            )
        
        except Exception as e:
            self._logger.error(f"Strategy {strategy} failed: {e}")
            return StrategyResult(
                strategy=strategy,
                answer='',
                confidence=0.0,
                reasoning_steps=[],
                metadata={'error': str(e)}
            )

    async def _integrate_research(self, question: str) -> Optional[ResearchContext]:
        """
        Perform research for the given question
        
        Args:
            question: Input question
        
        Returns:
            Research context or None
        """
        try:
            # Perform research
            research_context = await research_integrator.research(question)
            
            # Only return if confidence is sufficiently high
            return research_context if research_context.confidence > 0.5 else None
        except Exception as e:
            self._logger.warning(f"Research integration failed: {e}")
            return None

    async def reason(self, question: str) -> Dict[str, Any]:
        """
        Main reasoning method that coordinates multiple strategies
        
        Args:
            question: Input question to reason about
        
        Returns:
            Reasoning result with integrated insights
        """
        # Validate input
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        # Perform research
        research_context = await self._integrate_research(question)
        
        # Select strategies
        selected_strategies = self._select_strategies(question)
        
        # Execute strategies in parallel
        strategy_tasks = [
            self._execute_single_strategy(strategy, question, research_context)
            for strategy in selected_strategies
        ]
        
        # Wait for all strategies to complete
        strategy_results = await asyncio.gather(*strategy_tasks)
        
        # Validate and filter results
        valid_results = self._validate_results(strategy_results)
        
        # Combine results
        final_result = self._combine_results(valid_results)
        
        # Perform final validation
        validated_result = await self._final_validation(final_result)
        
        return validated_result

    def _validate_results(
        self, 
        results: List[StrategyResult]
    ) -> List[StrategyResult]:
        """
        Validate and filter strategy results
        
        Args:
            results: List of strategy results
        
        Returns:
            Filtered list of valid results
        """
        # Filter out low-confidence results
        valid_results = [
            result for result in results 
            if result.confidence >= 0.5
        ]
        
        # Sort by confidence
        valid_results.sort(key=lambda x: x.confidence, reverse=True)
        
        return valid_results

    def _combine_results(
        self, 
        results: List[StrategyResult]
    ) -> Dict[str, Any]:
        """
        Combine results from multiple strategies
        
        Args:
            results: List of strategy results
        
        Returns:
            Combined reasoning result
        """
        if not results:
            return {
                'answer': 'Unable to generate a conclusive answer.',
                'confidence': 0.0,
                'reasoning_steps': [],
                'metadata': {'error': 'No valid strategies produced results'}
            }
        
        # If only one result, return it
        if len(results) == 1:
            result = results[0]
            return {
                'answer': result.answer,
                'confidence': result.confidence,
                'reasoning_steps': result.reasoning_steps,
                'metadata': {
                    'selected_strategy': result.strategy.name,
                    'research_context': result.research_context
                }
            }
        
        # Multiple results: combine insights
        combined_answer = "Based on multiple reasoning approaches:\n"
        total_confidence = 0
        all_steps = []
        strategies_used = []
        
        for result in results:
            combined_answer += f"- {result.strategy.name} approach: {result.answer}\n"
            total_confidence += result.confidence
            all_steps.extend(result.reasoning_steps)
            strategies_used.append(result.strategy.name)
        
        return {
            'answer': combined_answer,
            'confidence': total_confidence / len(results),
            'reasoning_steps': all_steps,
            'metadata': {
                'combination_method': 'weighted_average',
                'strategies_used': strategies_used,
                'total_strategies': len(results)
            }
        }

    async def _final_validation(
        self, 
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform final validation on the reasoning result
        
        Args:
            result: Initial reasoning result
        
        Returns:
            Validated result
        """
        try:
            # Validate the result
            validation_result = await advanced_validator.validate(
                question=result.get('question', ''),
                answer=result.get('answer', ''),
                confidence=result.get('confidence', 0.0)
            )
            
            # Merge validation results
            result['validation'] = validation_result
            
            return result
        
        except Exception as e:
            self._logger.error(f"Final validation failed: {e}")
            return result

# Singleton orchestrator
reasoning_orchestrator = ReasoningOrchestrator()

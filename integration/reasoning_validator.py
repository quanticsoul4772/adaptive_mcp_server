"""
Integration module connecting reasoning and validation components.

Features:
- Bi-directional feedback between reasoning and validation
- Dynamic strategy adjustment based on validation results
- Confidence-based routing
- Real-time validation feedback
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
from ..reasoning.sequential import SequentialReasoner
from ..reasoning.branching import BranchingReasoner
from ..reasoning.abductive import AbductiveReasoner
from ..reasoning.lateral import LateralReasoner
from ..reasoning.logical import LogicalReasoner
from ..validators.enhanced_validator import (
    EnhancedValidator,
    ValidationConfig,
    ValidationLevel,
    ValidationAspect
)
from ..core.errors import ProcessingError

@dataclass
class ReasoningFeedback:
    """Feedback from validation to reasoning"""
    confidence: float
    issues: List[str]
    suggestions: List[str]
    aspect_scores: Dict[str, float]
    requires_revision: bool

@dataclass
class ValidationFeedback:
    """Feedback from reasoning to validation"""
    strategy_used: str
    reasoning_steps: List[Dict[str, Any]]
    evidence: List[str]
    context: Dict[str, Any]

class ReasoningValidator:
    """
    Integrates reasoning and validation components.
    
    Features:
    - Strategy selection based on validation results
    - Real-time validation during reasoning
    - Feedback loop between components
    - Automatic strategy adjustment
    """
    
    def __init__(self):
        # Initialize reasoners
        self.reasoners = {
            "sequential": SequentialReasoner(),
            "branching": BranchingReasoner(),
            "abductive": AbductiveReasoner(),
            "lateral": LateralReasoner(),
            "logical": LogicalReasoner()
        }
        
        # Initialize validator
        self.validator = EnhancedValidator()
        
        # Strategy effectiveness tracking
        self.strategy_performance = {
            strategy: {
                "success_count": 0,
                "total_count": 0,
                "avg_confidence": 0.0
            }
            for strategy in self.reasoners.keys()
        }

    async def process(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process question using integrated reasoning and validation.
        
        Args:
            question: Question to process
            context: Optional context
            
        Returns:
            Dict containing answer and process metadata
        """
        try:
            # Initial strategy selection
            strategy = self._select_initial_strategy(question, context)
            
            # Initialize validation config
            validation_config = self._create_validation_config(question, context)
            
            # Process with feedback loop
            max_attempts = 3
            attempts = 0
            final_result = None
            
            while attempts < max_attempts:
                attempts += 1
                
                # Get reasoner for current strategy
                reasoner = self.reasoners[strategy]
                
                # Run reasoning process
                reasoning_result = await reasoner.reason(question, context)
                
                # Create validation feedback
                validation_feedback = ValidationFeedback(
                    strategy_used=strategy,
                    reasoning_steps=reasoning_result["reasoning_steps"],
                    evidence=reasoning_result.get("evidence", []),
                    context=context or {}
                )
                
                # Validate with feedback
                validation_result = await self._validate_with_feedback(
                    question,
                    reasoning_result["answer"],
                    validation_config,
                    validation_feedback
                )
                
                # Create reasoning feedback
                reasoning_feedback = ReasoningFeedback(
                    confidence=validation_result.confidence,
                    issues=validation_result.issues,
                    suggestions=validation_result.suggestions,
                    aspect_scores={k.value: v for k, v in validation_result.aspects.items()},
                    requires_revision=validation_result.confidence < validation_config.min_confidence
                )
                
                # Update strategy performance
                self._update_strategy_performance(
                    strategy,
                    validation_result.confidence
                )
                
                if not reasoning_feedback.requires_revision:
                    final_result = self._combine_results(
                        reasoning_result,
                        validation_result
                    )
                    break
                
                # Adjust strategy based on feedback
                strategy = self._adjust_strategy(
                    strategy,
                    reasoning_feedback,
                    attempts
                )
            
            if final_result is None:
                raise ProcessingError(
                    "Failed to generate satisfactory answer",
                    {
                        "attempts": attempts,
                        "strategies_tried": strategy,
                        "last_confidence": reasoning_feedback.confidence
                    }
                )
            
            return final_result
            
        except Exception as e:
            raise ProcessingError(
                f"Integration processing failed: {str(e)}"
            )

    def _select_initial_strategy(
        self,
        question: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Select initial reasoning strategy"""
        # Look for strategy indicators in question
        if_then_pattern = r"if.*then|implies|therefore"
        why_pattern = r"\bwhy\b|\bcause\b|\bbecause\b"
        creative_pattern = r"creative|innovative|new way|design"
        complex_pattern = r".*,.*and.*|.*,.*or.*|multiple|several"
        
        # Check patterns
        if re.search(if_then_pattern, question, re.IGNORECASE):
            return "logical"
        elif re.search(why_pattern, question, re.IGNORECASE):
            return "abductive"
        elif re.search(creative_pattern, question, re.IGNORECASE):
            return "lateral"
        elif re.search(complex_pattern, question, re.IGNORECASE):
            return "branching"
            
        # Consider context if available
        if context:
            if "domain" in context:
                if context["domain"] in ["math", "physics", "logic"]:
                    return "logical"
                elif context["domain"] in ["art", "design", "innovation"]:
                    return "lateral"
            
            # Check previous performance in context
            if "previous_strategies" in context:
                best_strategy = max(
                    self.strategy_performance.items(),
                    key=lambda x: x[1]["avg_confidence"]
                )[0]
                return best_strategy
        
        # Default to sequential
        return "sequential"

    def _create_validation_config(
        self,
        question: str,
        context: Optional[Dict[str, Any]]
    ) -> ValidationConfig:
        """Create validation configuration based on question and context"""
        # Determine validation level
        if context and context.get("validation_level"):
            level = ValidationLevel[context["validation_level"].upper()]
        else:
            # Choose level based on question complexity
            words = question.split()
            if len(words) > 20 or "," in question:
                level = ValidationLevel.STRICT
            elif len(words) > 10:
                level = ValidationLevel.STANDARD
            else:
                level = ValidationLevel.BASIC
        
        # Determine required aspects
        required_aspects = {ValidationAspect.COMPLETENESS, ValidationAspect.RELEVANCE}
        
        if level in [ValidationLevel.STANDARD, ValidationLevel.STRICT]:
            required_aspects.update({
                ValidationAspect.ACCURACY,
                ValidationAspect.CLARITY,
                ValidationAspect.CONSISTENCY
            })
        
        if level == ValidationLevel.STRICT:
            required_aspects.update({
                ValidationAspect.SOURCING,
                ValidationAspect.REASONING
            })
        
        # Set confidence threshold
        if context and "min_confidence" in context:
            min_confidence = context["min_confidence"]
        else:
            min_confidence = {
                ValidationLevel.BASIC: 0.6,
                ValidationLevel.STANDARD: 0.7,
                ValidationLevel.STRICT: 0.8,
                ValidationLevel.EXPERT: 0.9
            }[level]
        
        return ValidationConfig(
            level=level,
            required_aspects=required_aspects,
            min_confidence=min_confidence,
            cross_validate=level in [ValidationLevel.STRICT, ValidationLevel.EXPERT],
            domain=context.get("domain") if context else None
        )

    async def _validate_with_feedback(
        self,
        question: str,
        answer: str,
        config: ValidationConfig,
        feedback: ValidationFeedback
    ) -> ValidationResult:
        """Validate answer with reasoning feedback"""
        # Enhance context with reasoning feedback
        enhanced_context = {
            "strategy_used": feedback.strategy_used,
            "reasoning_steps": feedback.reasoning_steps,
            "evidence": feedback.evidence
        }
        
        if feedback.context:
            enhanced_context.update(feedback.context)
        
        # Perform validation
        return await self.validator.validate(
            question,
            answer,
            config,
            enhanced_context
        )

    def _update_strategy_performance(
        self,
        strategy: str,
        confidence: float
    ):
        """Update strategy performance metrics"""
        perf = self.strategy_performance[strategy]
        perf["total_count"] += 1
        
        if confidence >= 0.7:  # Consider it successful if confidence is good
            perf["success_count"] += 1
        
        # Update running average
        perf["avg_confidence"] = (
            (perf["avg_confidence"] * (perf["total_count"] - 1) + confidence) /
            perf["total_count"]
        )

    def _adjust_strategy(
        self,
        current_strategy: str,
        feedback: ReasoningFeedback,
        attempt: int
    ) -> str:
        """Adjust strategy based on feedback"""
        # Don't change on last attempt
        if attempt >= 3:
            return current_strategy
        
        # Check specific issues
        if "logical fallacy" in str(feedback.issues):
            return "logical"
        elif "creativity" in str(feedback.suggestions):
            return "lateral"
        elif "evidence" in str(feedback.suggestions):
            return "abductive"
        
        # Check aspect scores
        aspect_scores = feedback.aspect_scores
        if aspect_scores.get("reasoning", 0) < 0.6:
            return "logical"
        elif aspect_scores.get("creativity", 0) < 0.6:
            return "lateral"
        elif aspect_scores.get("completeness", 0) < 0.6:
            return "branching"
        
        # Fall back to best performing strategy
        return max(
            self.strategy_performance.items(),
            key=lambda x: x[1]["avg_confidence"]
        )[0]

    def _combine_results(
        self,
        reasoning_result: Dict[str, Any],
        validation_result: ValidationResult
    ) -> Dict[str, Any]:
        """Combine reasoning and validation results"""
        return {
            "answer": reasoning_result["answer"],
            "confidence": validation_result.confidence,
            "reasoning_steps": reasoning_result["reasoning_steps"],
            "validation": {
                "aspects": {
                    k.value: v for k, v in validation_result.aspects.items()
                },
                "issues": validation_result.issues,
                "suggestions": validation_result.suggestions
            },
            "metadata": {
                **reasoning_result.get("metadata", {}),
                "validation_level": validation_result.metadata["validation_level"],
                "strategy_performance": self.strategy_performance
            }
        }

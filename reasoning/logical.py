"""
Logical Reasoning Module

Implements formal logical reasoning using rules, deduction, and validation.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
from mcp.types import McpError

class LogicOperator(Enum):
    """Basic logical operators"""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    IMPLIES = "IMPLIES"

@dataclass
class LogicalStatement:
    """Represents a logical statement or premise"""
    text: str
    certainty: float
    source: Optional[str] = None
    operator: Optional[LogicOperator] = None

@dataclass
class LogicalArgument:
    """Represents a complete logical argument"""
    premises: List[LogicalStatement]
    conclusion: LogicalStatement
    validity_score: float
    soundness_score: float

class LogicalReasoner:
    """
    Implements formal logical reasoning.
    
    Features:
    - Statement validation
    - Logical deduction
    - Consistency checking
    - Fallacy detection
    """
    
    def __init__(self):
        self.statements: List[LogicalStatement] = []
        self.known_fallacies: Set[str] = {
            "circular reasoning",
            "false causality",
            "hasty generalization",
            "appeal to authority"
        }
        
    async def reason(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Apply logical reasoning to reach a conclusion.
        
        Args:
            question: Question to reason about
            context: Optional additional context
            
        Returns:
            Dict containing logical conclusion and reasoning process
        """
        try:
            # Step 1: Extract premises from question and research
            premises = await self._gather_premises(question)
            
            # Step 2: Construct logical arguments
            arguments = self._construct_arguments(premises)
            
            # Step 3: Validate arguments
            valid_arguments = []
            for argument in arguments:
                if self._validate_argument(argument):
                    valid_arguments.append(argument)
            
            if not valid_arguments:
                raise McpError("No valid logical arguments found")
            
            # Step 4: Select best argument
            best_argument = max(
                valid_arguments,
                key=lambda a: (a.validity_score * 0.6 + a.soundness_score * 0.4)
            )
            
            # Step 5: Validate conclusion
            from ..validators.basic_validator import validate_answer
            validation = validate_answer(question, best_argument.conclusion.text)
            
            return {
                "answer": best_argument.conclusion.text,
                "confidence": min(
                    best_argument.validity_score,
                    best_argument.soundness_score,
                    validation["confidence"]
                ),
                "reasoning_steps": [
                    {
                        "step": "Premises",
                        "output": "Gathered logical premises from research"
                    },
                    {
                        "step": "Arguments",
                        "output": f"Constructed {len(arguments)} logical arguments"
                    },
                    {
                        "step": "Validation",
                        "output": f"Found {len(valid_arguments)} valid arguments"
                    },
                    {
                        "step": "Conclusion",
                        "output": f"Selected best argument (validity: {best_argument.validity_score:.2f}, soundness: {best_argument.soundness_score:.2f})"
                    }
                ],
                "metadata": {
                    "approach": "logical",
                    "argument_structure": {
                        "premises": [p.text for p in best_argument.premises],
                        "conclusion": best_argument.conclusion.text
                    },
                    "scores": {
                        "validity": best_argument.validity_score,
                        "soundness": best_argument.soundness_score
                    },
                    "validation": validation
                }
            }
            
        except Exception as e:
            raise McpError(f"Logical reasoning failed: {str(e)}")

    async def _gather_premises(self, question: str) -> List[LogicalStatement]:
        """Gather logical premises from research"""
        from ..research.exa_integration import search_information
        research_results = await search_information(question)
        
        # Extract statements that could serve as premises
        statements = []
        
        sentences = research_results.split('.')
        for sentence in sentences:
            if self._is_logical_statement(sentence):
                certainty = self._assess_statement_certainty(sentence)
                statements.append(LogicalStatement(
                    text=sentence.strip(),
                    certainty=certainty,
                    source="research"
                ))
        
        return statements

    def _is_logical_statement(self, text: str) -> bool:
        """Check if text could be a logical statement"""
        # Look for logical indicators
        logical_markers = {
            "if", "then", "therefore", "because", "must", "always",
            "never", "all", "none", "some", "implies"
        }
        
        return any(marker in text.lower() for marker in logical_markers)

    def _assess_statement_certainty(self, text: str) -> float:
        """Assess how certain a statement seems"""
        # Look for certainty/uncertainty markers
        certainty_markers = {"definitely", "certainly", "always", "must"}
        uncertainty_markers = {"maybe", "might", "could", "possibly"}
        
        text_lower = text.lower()
        certainty_count = sum(1 for m in certainty_markers if m in text_lower)
        uncertainty_count = sum(1 for m in uncertainty_markers if m in text_lower)
        
        # Base certainty of 0.5, adjusted by markers
        certainty = 0.5 + (0.1 * certainty_count) - (0.1 * uncertainty_count)
        return min(1.0, max(0.1, certainty))

    def _construct_arguments(self, premises: List[LogicalStatement]) -> List[LogicalArgument]:
        """Construct logical arguments from premises"""
        arguments = []
        
        # Try different combinations of premises
        for i in range(len(premises)):
            # Use current premise as conclusion
            conclusion = premises[i]
            
            # Use other premises as support
            supporting_premises = [
                p for j, p in enumerate(premises)
                if j != i and self._could_support(p, conclusion)
            ]
            
            if supporting_premises:
                validity, soundness = self._evaluate_argument(
                    supporting_premises,
                    conclusion
                )
                
                arguments.append(LogicalArgument(
                    premises=supporting_premises,
                    conclusion=conclusion,
                    validity_score=validity,
                    soundness_score=soundness
                ))
        
        return arguments

    def _could_support(self, premise: LogicalStatement, conclusion: LogicalStatement) -> bool:
        """Check if premise could logically support conclusion"""
        # Look for term overlap
        premise_terms = set(premise.text.lower().split())
        conclusion_terms = set(conclusion.text.lower().split())
        
        # Need some term overlap
        overlap = premise_terms.intersection(conclusion_terms)
        return len(overlap) >= 2  # Arbitrary threshold

    def _evaluate_argument(
        self,
        premises: List[LogicalStatement],
        conclusion: LogicalStatement
    ) -> Tuple[float, float]:
        """
        Evaluate argument validity and soundness.
        
        Returns:
            Tuple of (validity_score, soundness_score)
        """
        # Check validity (logical structure)
        validity = self._check_validity(premises, conclusion)
        
        # Check soundness (truth of premises)
        premise_certainties = [p.certainty for p in premises]
        soundness = min(premise_certainties) if premise_certainties else 0.0
        
        return validity, soundness

    def _check_validity(
        self,
        premises: List[LogicalStatement],
        conclusion: LogicalStatement
    ) -> float:
        """Check logical validity of argument"""
        # Basic validity checks
        if not premises:
            return 0.0
            
        # Check for common fallacies
        if self._contains_fallacy(premises, conclusion):
            return 0.3  # Penalize but don't completely invalidate
            
        # Check logical connection
        connection_strength = self._assess_logical_connection(premises, conclusion)
        
        # Consider number of supporting premises
        premise_bonus = min(0.2, len(premises) * 0.1)  # More premises can strengthen up to a point
        
        return min(1.0, connection_strength + premise_bonus)

    def _contains_fallacy(
        self,
        premises: List[LogicalStatement],
        conclusion: LogicalStatement
    ) -> bool:
        """Check for common logical fallacies"""
        # Check for circular reasoning
        if conclusion.text in [p.text for p in premises]:
            return True
            
        # Check for hasty generalization
        if len(premises) < 2 and ("all" in conclusion.text.lower() or "every" in conclusion.text.lower()):
            return True
            
        return False

    def _assess_logical_connection(
        self,
        premises: List[LogicalStatement],
        conclusion: LogicalStatement
    ) -> float:
        """Assess strength of logical connection between premises and conclusion"""
        # Look for logical flow indicators
        flow_markers = {
            "therefore": 0.3,
            "thus": 0.3,
            "because": 0.2,
            "since": 0.2,
            "implies": 0.4
        }
        
        # Check term relationships
        all_premise_terms = set()
        for premise in premises:
            all_premise_terms.update(premise.text.lower().split())
        
        conclusion_terms = set(conclusion.text.lower().split())
        term_overlap = len(all_premise_terms.intersection(conclusion_terms))
        term_score = min(0.5, term_overlap * 0.1)
        
        # Check for flow markers
        marker_score = sum(
            weight
            for marker, weight in flow_markers.items()
            if marker in conclusion.text.lower()
        )
        
        return min(1.0, term_score + marker_score)

    def _validate_argument(self, argument: LogicalArgument) -> bool:
        """Final validation of an argument"""
        return (
            argument.validity_score >= 0.6 and
            argument.soundness_score >= 0.4 and
            not self._contains_fallacy(argument.premises, argument.conclusion)
        )

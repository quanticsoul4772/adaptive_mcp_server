"""
Inductive Reasoning Module

Implements pattern-based reasoning from specific examples to general conclusions.
Features:
- Pattern recognition
- Trend analysis
- Generalization with confidence levels
- Example-based learning
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import re
from ..core.errors import McpError

@dataclass
class Pattern:
    """Represents a recognized pattern"""
    pattern_type: str
    examples: List[str]
    confidence: float
    generalization: str
    limitations: List[str]

class InductiveReasoner:
    """
    Implements inductive reasoning by recognizing patterns and forming generalizations.
    """
    
    def __init__(self):
        self.patterns = []
        self.confidence_threshold = 0.7
    
    async def reason(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform inductive reasoning.
        
        Args:
            question: Question to reason about
            context: Optional additional context
        """
        try:
            # Step 1: Gather examples
            examples = await self._gather_examples(question, context)
            
            # Step 2: Identify patterns
            patterns = await self._identify_patterns(examples)
            
            # Step 3: Form generalizations
            generalizations = self._form_generalizations(patterns)
            
            # Step 4: Validate and combine
            answer = self._combine_generalizations(generalizations)
            
            # Calculate confidence
            confidence = self._calculate_confidence(patterns, examples)
            
            # Return result
            return {
                "answer": answer,
                "confidence": confidence,
                "reasoning_steps": [
                    {
                        "step": "Gather Examples",
                        "output": f"Found {len(examples)} relevant examples"
                    },
                    {
                        "step": "Identify Patterns",
                        "output": f"Identified {len(patterns)} patterns"
                    },
                    {
                        "step": "Form Generalizations",
                        "output": f"Formed {len(generalizations)} generalizations"
                    }
                ],
                "metadata": {
                    "strategy": "inductive",
                    "examples_used": len(examples),
                    "patterns_found": len(patterns),
                    "limitations": self._identify_limitations(patterns)
                }
            }
            
        except Exception as e:
            raise McpError(f"Inductive reasoning failed: {str(e)}")

    async def _gather_examples(
        self,
        question: str,
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Gather relevant examples for pattern analysis"""
        from ..research.enhanced_search import EnhancedSearchManager
        
        search_manager = EnhancedSearchManager()
        examples = []
        
        # Extract key terms for search
        terms = self._extract_key_terms(question)
        
        # Search for examples
        for term in terms:
            results = await search_manager.search(
                f"examples of {term}",
                min_results=3
            )
            examples.extend(result.content for result in results)
        
        # Add examples from context if available
        if context and "examples" in context:
            examples.extend(context["examples"])
        
        return examples

    async def _identify_patterns(
        self,
        examples: List[str]
    ) -> List[Pattern]:
        """Identify patterns in examples"""
        patterns = []
        
        # Look for different types of patterns
        temporal_pattern = self._find_temporal_pattern(examples)
        if temporal_pattern:
            patterns.append(temporal_pattern)
            
        causal_pattern = self._find_causal_pattern(examples)
        if causal_pattern:
            patterns.append(causal_pattern)
            
        structural_pattern = self._find_structural_pattern(examples)
        if structural_pattern:
            patterns.append(structural_pattern)
            
        frequency_pattern = self._find_frequency_pattern(examples)
        if frequency_pattern:
            patterns.append(frequency_pattern)
        
        return patterns

    def _find_temporal_pattern(self, examples: List[str]) -> Optional[Pattern]:
        """Find temporal patterns in examples"""
        # Look for time-related words
        time_markers = ["before", "after", "when", "during", "then"]
        temporal_examples = []
        
        for example in examples:
            if any(marker in example.lower() for marker in time_markers):
                temporal_examples.append(example)
        
        if len(temporal_examples) >= 2:
            return Pattern(
                pattern_type="temporal",
                examples=temporal_examples,
                confidence=len(temporal_examples) / len(examples),
                generalization=self._extract_temporal_relation(temporal_examples),
                limitations=["Time-dependent variations possible"]
            )
        return None

    def _find_causal_pattern(self, examples: List[str]) -> Optional[Pattern]:
        """Find cause-effect patterns"""
        # Look for causal indicators
        causal_markers = ["because", "causes", "leads to", "results in"]
        causal_examples = []
        
        for example in examples:
            if any(marker in example.lower() for marker in causal_markers):
                causal_examples.append(example)
        
        if len(causal_examples) >= 2:
            return Pattern(
                pattern_type="causal",
                examples=causal_examples,
                confidence=len(causal_examples) / len(examples),
                generalization=self._extract_causal_relation(causal_examples),
                limitations=["Correlation vs causation", "Multiple factors possible"]
            )
        return None

    def _find_structural_pattern(self, examples: List[str]) -> Optional[Pattern]:
        """Find structural/compositional patterns"""
        # Look for structural indicators
        structural_markers = ["consists of", "contains", "composed of", "parts"]
        structural_examples = []
        
        for example in examples:
            if any(marker in example.lower() for marker in structural_markers):
                structural_examples.append(example)
        
        if len(structural_examples) >= 2:
            return Pattern(
                pattern_type="structural",
                examples=structural_examples,
                confidence=len(structural_examples) / len(examples),
                generalization=self._extract_structural_relation(structural_examples),
                limitations=["Variations in composition possible"]
            )
        return None

    def _find_frequency_pattern(self, examples: List[str]) -> Optional[Pattern]:
        """Find frequency/occurrence patterns"""
        # Count term frequencies
        term_counts = {}
        for example in examples:
            words = example.lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    term_counts[word] = term_counts.get(word, 0) + 1
        
        # Find frequent terms
        frequent_terms = [
            term for term, count in term_counts.items()
            if count >= len(examples) * 0.5
        ]
        
        if frequent_terms:
            return Pattern(
                pattern_type="frequency",
                examples=examples,
                confidence=len(frequent_terms) / len(term_counts) if term_counts else 0,
                generalization=f"Common elements: {', '.join(frequent_terms)}",
                limitations=["Sample size limitations"]
            )
        return None

    def _extract_temporal_relation(self, examples: List[str]) -> str:
        """Extract temporal relationship from examples"""
        before_after = {}
        for example in examples:
            match = re.search(r"(\w+)\s+before\s+(\w+)", example)
            if match:
                before, after = match.groups()
                before_after[before] = after
        
        if before_after:
            sequences = [f"{before} precedes {after}" 
                        for before, after in before_after.items()]
            return f"Temporal sequence: {'; '.join(sequences)}"
        return "No clear temporal sequence found"

    def _extract_causal_relation(self, examples: List[str]) -> str:
        """Extract cause-effect relationship from examples"""
        causes_effects = {}
        for example in examples:
            match = re.search(r"(\w+)\s+causes?\s+(\w+)", example)
            if match:
                cause, effect = match.groups()
                causes_effects[cause] = effect
        
        if causes_effects:
            relations = [f"{cause} leads to {effect}" 
                        for cause, effect in causes_effects.items()]
            return f"Causal relationship: {'; '.join(relations)}"
        return "No clear causal relationship found"

    def _extract_structural_relation(self, examples: List[str]) -> str:
        """Extract structural relationships from examples"""
        components = set()
        for example in examples:
            match = re.search(r"consists? of\s+(.+)", example)
            if match:
                parts = match.group(1).split(",")
                components.update(part.strip() for part in parts)
        
        if components:
            return f"Common components: {', '.join(components)}"
        return "No clear structural pattern found"

    def _form_generalizations(self, patterns: List[Pattern]) -> List[str]:
        """Form generalizations from identified patterns"""
        generalizations = []
        
        # Group patterns by type
        by_type = {}
        for pattern in patterns:
            if pattern.pattern_type not in by_type:
                by_type[pattern.pattern_type] = []
            by_type[pattern.pattern_type].append(pattern)
        
        # Form generalizations for each type
        for pattern_type, type_patterns in by_type.items():
            if pattern_type == "temporal":
                generalizations.append(
                    self._form_temporal_generalization(type_patterns)
                )
            elif pattern_type == "causal":
                generalizations.append(
                    self._form_causal_generalization(type_patterns)
                )
            elif pattern_type == "structural":
                generalizations.append(
                    self._form_structural_generalization(type_patterns)
                )
            elif pattern_type == "frequency":
                generalizations.append(
                    self._form_frequency_generalization(type_patterns)
                )
        
        return [g for g in generalizations if g]  # Remove empty generalizations

    def _form_temporal_generalization(self, patterns: List[Pattern]) -> str:
        """Form temporal generalization"""
        sequences = []
        for pattern in patterns:
            if "Temporal sequence:" in pattern.generalization:
                sequence = pattern.generalization.split(": ")[1]
                sequences.append(sequence)
        
        if sequences:
            return f"Based on temporal patterns: {'; '.join(sequences)}"
        return ""

    def _form_causal_generalization(self, patterns: List[Pattern]) -> str:
        """Form causal generalization"""
        relations = []
        for pattern in patterns:
            if "Causal relationship:" in pattern.generalization:
                relation = pattern.generalization.split(": ")[1]
                relations.append(relation)
        
        if relations:
            return f"Based on causal patterns: {'; '.join(relations)}"
        return ""

    def _form_structural_generalization(self, patterns: List[Pattern]) -> str:
        """Form structural generalization"""
        components = set()
        for pattern in patterns:
            if "Common components:" in pattern.generalization:
                parts = pattern.generalization.split(": ")[1].split(", ")
                components.update(parts)
        
        if components:
            return f"Based on structural patterns: Contains {', '.join(components)}"
        return ""

    def _form_frequency_generalization(self, patterns: List[Pattern]) -> str:
        """Form frequency-based generalization"""
        common_elements = set()
        for pattern in patterns:
            if "Common elements:" in pattern.generalization:
                elements = pattern.generalization.split(": ")[1].split(", ")
                common_elements.update(elements)
        
        if common_elements:
            return f"Based on frequency patterns: Commonly involves {', '.join(common_elements)}"
        return ""

    def _combine_generalizations(self, generalizations: List[str]) -> str:
        """Combine generalizations into final answer"""
        if not generalizations:
            return "No clear patterns identified"
        
        # Group by type
        temporal = []
        causal = []
        structural = []
        frequency = []
        
        for gen in generalizations:
            if gen.startswith("Based on temporal"):
                temporal.append(gen)
            elif gen.startswith("Based on causal"):
                causal.append(gen)
            elif gen.startswith("Based on structural"):
                structural.append(gen)
            elif gen.startswith("Based on frequency"):
                frequency.append(gen)
        
        # Combine in logical order
        combined = []
        if structural:
            combined.append(structural[0])  # Start with structure
        if causal:
            combined.append(causal[0])      # Then causation
        if temporal:
            combined.append(temporal[0])     # Then temporal sequence 
        if frequency:
            combined.append(frequency[0])    # Finally frequency patterns
        
        return " Furthermore, ".join(combined)

    def _calculate_confidence(
        self,
        patterns: List[Pattern],
        examples: List[str]
    ) -> float:
        """Calculate confidence in the inductive reasoning"""
        if not patterns:
            return 0.0
        
        # Factors affecting confidence
        pattern_scores = [pattern.confidence for pattern in patterns]
        avg_pattern_confidence = sum(pattern_scores) / len(pattern_scores)
        
        example_coverage = len([p for p in patterns if p.examples]) / len(examples) if examples else 0
        
        pattern_diversity = len(set(p.pattern_type for p in patterns)) / 4  # 4 pattern types
        
        # Weight the factors
        confidence = (
            0.4 * avg_pattern_confidence +
            0.3 * example_coverage +
            0.3 * pattern_diversity
        )
        
        return min(1.0, confidence)

    def _identify_limitations(self, patterns: List[Pattern]) -> List[str]:
        """Identify limitations of the inductive reasoning"""
        limitations = set()
        
        # Collect limitations from patterns
        for pattern in patterns:
            limitations.update(pattern.limitations)
        
        # Add general limitations
        if len(patterns) < 3:
            limitations.add("Limited number of patterns identified")
        
        pattern_types = set(p.pattern_type for p in patterns)
        if len(pattern_types) < 3:
            limitations.add("Limited pattern diversity")
        
        if patterns:
            avg_examples = sum(len(p.examples) for p in patterns) / len(patterns)
            if avg_examples < 3:
                limitations.add("Limited examples per pattern")
        
        return list(limitations)

    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms for searching examples"""
        # Remove common words
        common_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "up", "down", "what", "why",
            "how", "when", "where", "who", "which", "that"
        }
        
        # Tokenize and clean
        words = text.lower().split()
        terms = [word for word in words if word not in common_words and len(word) > 3]
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(terms))

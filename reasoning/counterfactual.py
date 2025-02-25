"""
Counterfactual Reasoning Module

Implements reasoning about hypothetical scenarios and alternative possibilities.
Features:
- Alternative scenario generation
- Causal analysis
- Impact assessment
- Plausibility evaluation
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
import re
from ..core.errors import McpError

@dataclass
class Scenario:
    """Represents a counterfactual scenario"""
    premise: str
    changes: List[str]
    implications: List[str]
    plausibility: float
    evidence: List[str]
    limitations: List[str]

@dataclass
class CausalChain:
    """Represents a chain of causal effects"""
    initial_change: str
    effects: List[str]
    probability: float
    stopping_conditions: List[str]

class CounterfactualReasoner:
    """
    Implements counterfactual reasoning about alternative scenarios.
    """
    
    def __init__(self):
        self.plausibility_threshold = 0.6
        self.max_causal_depth = 3
    
    async def reason(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform counterfactual reasoning.
        
        Args:
            question: Question to reason about
            context: Optional additional context
            
        Returns:
            Dict containing counterfactual analysis
        """
        try:
            # Step 1: Extract counterfactual premise
            premise = self._extract_premise(question)
            
            # Step 2: Generate alternative scenarios
            scenarios = await self._generate_scenarios(premise, context)
            
            # Step 3: Analyze causal implications
            causal_chains = self._analyze_causality(scenarios)
            
            # Step 4: Evaluate plausibility
            plausible_scenarios = self._evaluate_plausibility(scenarios)
            
            # Step 5: Generate answer
            answer = self._generate_answer(plausible_scenarios, causal_chains)
            
            # Calculate confidence
            confidence = self._calculate_confidence(plausible_scenarios)
            
            return {
                "answer": answer,
                "confidence": confidence,
                "reasoning_steps": [
                    {
                        "step": "Premise Extraction",
                        "output": f"Counterfactual premise: {premise}"
                    },
                    {
                        "step": "Scenario Generation",
                        "output": f"Generated {len(scenarios)} alternative scenarios"
                    },
                    {
                        "step": "Causal Analysis",
                        "output": f"Identified {len(causal_chains)} causal chains"
                    },
                    {
                        "step": "Plausibility Evaluation",
                        "output": f"Found {len(plausible_scenarios)} plausible scenarios"
                    }
                ],
                "metadata": {
                    "strategy": "counterfactual",
                    "scenarios_generated": len(scenarios),
                    "plausible_scenarios": len(plausible_scenarios),
                    "causal_chains": len(causal_chains),
                    "limitations": self._identify_limitations(plausible_scenarios)
                }
            }
            
        except Exception as e:
            raise McpError(f"Counterfactual reasoning failed: {str(e)}")

    def _extract_premise(self, question: str) -> str:
        """Extract counterfactual premise from question"""
        # Look for counterfactual indicators
        indicators = [
            "what if",
            "suppose",
            "imagine if",
            "if only",
            "had",
            "would have",
            "could have"
        ]
        
        for indicator in indicators:
            if indicator in question.lower():
                parts = question.lower().split(indicator)
                if len(parts) > 1:
                    return parts[1].strip()
        
        return question  # Return full question if no explicit counterfactual

    async def _generate_scenarios(
        self,
        premise: str,
        context: Optional[Dict[str, Any]]
    ) -> List[Scenario]:
        """Generate alternative scenarios based on premise"""
        from ..research.enhanced_search import EnhancedSearchManager
        
        search_manager = EnhancedSearchManager()
        scenarios = []
        
        # Search for similar historical scenarios
        results = await search_manager.search(
            f"examples similar to {premise}",
            min_results=3
        )
        
        for result in results:
            # Extract changes and implications
            changes = self._extract_changes(result.content)
            implications = self._extract_implications(result.content)
            
            if changes and implications:
                scenarios.append(Scenario(
                    premise=premise,
                    changes=changes,
                    implications=implications,
                    plausibility=result.credibility_score,
                    evidence=[result.content],
                    limitations=self._identify_scenario_limitations(changes)
                ))
        
        # Generate additional scenarios through permutation
        generated = self._generate_permuted_scenarios(scenarios)
        scenarios.extend(generated)
        
        return scenarios

    def _extract_changes(self, text: str) -> List[str]:
        """Extract described changes from text"""
        # Look for change indicators
        change_patterns = [
            r"changed to\s+([^,.]+)",
            r"became\s+([^,.]+)",
            r"turned into\s+([^,.]+)",
            r"replaced by\s+([^,.]+)",
            r"instead of\s+([^,.]+)"
        ]
        
        changes = []
        for pattern in change_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            changes.extend(match.group(1).strip() for match in matches)
        
        return changes

    def _extract_implications(self, text: str) -> List[str]:
        """Extract implications from text"""
        # Look for implication indicators
        implication_patterns = [
            r"led to\s+([^,.]+)",
            r"resulted in\s+([^,.]+)",
            r"caused\s+([^,.]+)",
            r"consequently\s+([^,.]+)",
            r"therefore\s+([^,.]+)"
        ]
        
        implications = []
        for pattern in implication_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            implications.extend(match.group(1).strip() for match in matches)
        
        return implications

    def _generate_permuted_scenarios(
        self,
        base_scenarios: List[Scenario]
    ) -> List[Scenario]:
        """Generate new scenarios by permuting existing ones"""
        import itertools
        
        new_scenarios = []
        
        # Get all changes and implications
        all_changes = list(set(
            change
            for scenario in base_scenarios
            for change in scenario.changes
        ))
        
        all_implications = list(set(
            implication
            for scenario in base_scenarios
            for implication in scenario.implications
        ))
        
        # Generate new combinations
        for changes in itertools.combinations(all_changes, 2):
            # For each change combination, pick relevant implications
            relevant_implications = [
                impl for impl in all_implications
                if self._are_changes_relevant_to_implication(changes, impl)
            ]
            
            if relevant_implications:
                new_scenarios.append(Scenario(
                    premise=base_scenarios[0].premise if base_scenarios else "",
                    changes=list(changes),
                    implications=relevant_implications[:2],  # Limit implications
                    plausibility=0.5,  # Lower plausibility for generated scenarios
                    evidence=[],
                    limitations=["Generated through combination"]
                ))
        
        return new_scenarios[:len(base_scenarios)] if base_scenarios else []  # Return same number as base scenarios

    def _are_changes_relevant_to_implication(
        self,
        changes: Tuple[str, ...],
        implication: str
    ) -> bool:
        """Check if changes are relevant to an implication"""
        # Simple relevance check based on word overlap
        change_words = set(' '.join(changes).lower().split())
        implication_words = set(implication.lower().split())
        
        overlap = len(change_words.intersection(implication_words))
        return overlap >= 1  # At least one word overlap

    def _analyze_causality(
        self,
        scenarios: List[Scenario]
    ) -> List[CausalChain]:
        """Analyze causal chains in scenarios"""
        causal_chains = []
        
        for scenario in scenarios:
            for change in scenario.changes:
                chain = self._build_causal_chain(
                    change,
                    scenario.implications,
                    depth=0
                )
                if chain:
                    causal_chains.append(chain)
        
        return causal_chains

    def _build_causal_chain(
        self,
        initial_change: str,
        available_effects: List[str],
        depth: int
    ) -> Optional[CausalChain]:
        """Build a causal chain from an initial change"""
        if depth >= self.max_causal_depth or not available_effects:
            return None
        
        effects = []
        remaining_effects = available_effects.copy()
        probability = 1.0
        
        while remaining_effects and len(effects) < 3:
            # Find most likely next effect
            next_effect, effect_prob = self._find_most_likely_effect(
                initial_change if not effects else effects[-1],
                remaining_effects
            )
            
            if effect_prob > 0.5:
                effects.append(next_effect)
                remaining_effects.remove(next_effect)
                probability *= effect_prob
            else:
                break
        
        if effects:
            return CausalChain(
                initial_change=initial_change,
                effects=effects,
                probability=probability,
                stopping_conditions=self._identify_stopping_conditions(effects)
            )
        
        return None

    def _find_most_likely_effect(
        self,
        cause: str,
        possible_effects: List[str]
    ) -> Tuple[str, float]:
        """Find the most likely effect from possible effects"""
        best_effect = ""
        best_prob = 0.0
        
        for effect in possible_effects:
            prob = self._calculate_causal_probability(cause, effect)
            if prob > best_prob:
                best_prob = prob
                best_effect = effect
        
        return best_effect, best_prob

    def _calculate_causal_probability(
        self,
        cause: str,
        effect: str
    ) -> float:
        """Calculate probability of causal relationship"""
        # Look for causal indicators
        causal_indicators = {
            "direct": ["leads to", "causes", "results in"],
            "indirect": ["contributes to", "influences", "affects"],
            "conditional": ["might lead to", "could cause", "potentially"]
        }
        
        score = 0.0
        
        # Check for direct causation
        if any(ind in f"{cause} {effect}" for ind in causal_indicators["direct"]):
            score += 0.4
        
        # Check for indirect causation
        if any(ind in f"{cause} {effect}" for ind in causal_indicators["indirect"]):
            score += 0.2
        
        # Check for conditional causation
        if any(ind in f"{cause} {effect}" for ind in causal_indicators["conditional"]):
            score += 0.1
        
        # Check semantic similarity
        similarity = self._calculate_semantic_similarity(cause, effect)
        score += similarity * 0.3
        
        return min(1.0, score)

    def _calculate_semantic_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Calculate semantic similarity between texts"""
        # Convert to word sets
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

    def _identify_stopping_conditions(
        self,
        effects: List[str]
    ) -> List[str]:
        """Identify conditions that would stop the causal chain"""
        conditions = []
        
        for effect in effects:
            # Look for limiting factors
            if "until" in effect:
                conditions.append(effect.split("until")[1].strip())
            elif "unless" in effect:
                conditions.append(effect.split("unless")[1].strip())
            elif "except" in effect:
                conditions.append(effect.split("except")[1].strip())
        
        return conditions

    def _evaluate_plausibility(
        self,
        scenarios: List[Scenario]
    ) -> List[Scenario]:
        """Evaluate and filter scenarios by plausibility"""
        plausible = []
        
        for scenario in scenarios:
            # Calculate modified plausibility
            evidence_factor = min(1.0, len(scenario.evidence) * 0.2)
            complexity_penalty = max(0.0, (len(scenario.changes) - 2) * 0.1)
            
            modified_plausibility = (
                scenario.plausibility * 0.6 +
                evidence_factor * 0.3 -
                complexity_penalty
            )
            
            if modified_plausibility >= self.plausibility_threshold:
                # Create new scenario with updated plausibility
                plausible.append(Scenario(
                    premise=scenario.premise,
                    changes=scenario.changes,
                    implications=scenario.implications,
                    plausibility=modified_plausibility,
                    evidence=scenario.evidence,
                    limitations=scenario.limitations
                ))
        
        return plausible

    def _generate_answer(
        self,
        scenarios: List[Scenario],
        causal_chains: List[CausalChain]
    ) -> str:
        """Generate final answer from analyzed scenarios"""
        if not scenarios:
            return "No plausible counterfactual scenarios identified."
        
        # Sort scenarios by plausibility
        scenarios.sort(key=lambda s: s.plausibility, reverse=True)
        
        # Generate answer components
        parts = []
        
        # Main scenario
        best_scenario = scenarios[0]
        parts.append(f"The most plausible scenario involves: {', '.join(best_scenario.changes)}")
        
        # Key implications
        if best_scenario.implications:
            parts.append(f"This would likely lead to: {', '.join(best_scenario.implications)}")
        
        # Alternative scenarios
        if len(scenarios) > 1:
            alt_scenario = scenarios[1]
            parts.append(f"An alternative possibility would be: {', '.join(alt_scenario.changes)}")
        
        # Causal chains
        if causal_chains:
            best_chain = max(causal_chains, key=lambda c: c.probability)
            chain_desc = " → ".join([best_chain.initial_change] + best_chain.effects)
            parts.append(f"The primary causal chain would be: {chain_desc}")
        
        # Limitations
        key_limitations = self._identify_limitations(scenarios)
        if key_limitations:
            parts.append(f"Key limitations: {', '.join(key_limitations)}")
        
        return " ".join(parts)

    def _calculate_confidence(
        self,
        scenarios: List[Scenario]
    ) -> float:
        """Calculate overall confidence in counterfactual analysis"""
        if not scenarios:
            return 0.0
        
        # Factors affecting confidence
        plausibility_scores = [s.plausibility for s in scenarios]
        avg_plausibility = sum(plausibility_scores) / len(plausibility_scores)
        
        evidence_coverage = sum(
            1 for s in scenarios if s.evidence
        ) / len(scenarios)
        
        scenario_diversity = len(set(
            tuple(sorted(s.changes)) for s in scenarios
        )) / len(scenarios)
        
        # Combine factors
        confidence = (
            0.4 * avg_plausibility +
            0.3 * evidence_coverage +
            0.3 * scenario_diversity
        )
        
        return min(1.0, confidence)

    def _identify_limitations(
        self,
        scenarios: List[Scenario]
    ) -> List[str]:
        """Identify limitations of the counterfactual analysis"""
        limitations = set()
        
        # Collect limitations from scenarios
        for scenario in scenarios:
            limitations.update(scenario.limitations)
        
        # Add general limitations
        if len(scenarios) < 2:
            limitations.add("Limited number of plausible scenarios")
        
        avg_plausibility = sum(s.plausibility for s in scenarios) / len(scenarios) if scenarios else 0
        if avg_plausibility < 0.7:
            limitations.add("Limited confidence in scenario plausibility")
        
        evidence_count = sum(len(s.evidence) for s in scenarios)
        if evidence_count < len(scenarios):
            limitations.add("Limited supporting evidence")
        
        return list(limitations)

    def _identify_scenario_limitations(
        self,
        changes: List[str]
    ) -> List[str]:
        """Identify limitations specific to a scenario"""
        limitations = []
        
        # Check change complexity
        if len(changes) > 3:
            limitations.append("Complex combination of changes")
        
        # Check for speculative language
        speculative_terms = ["might", "could", "possibly", "perhaps", "maybe"]
        if any(term in ' '.join(changes).lower() for term in speculative_terms):
            limitations.append("Includes speculative elements")
        
        return limitations

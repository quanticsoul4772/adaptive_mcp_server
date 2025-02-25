"""
Enhanced validation module combining multiple validation strategies.
[Previous content remains the same until _adjust_results method...]
"""

    def _adjust_results(
        self,
        initial: ValidationResult,
        adjustments: Dict[ValidationAspect, float]
    ) -> ValidationResult:
        """Apply cross-validation adjustments"""
        adjusted_aspects = initial.aspects.copy()
        
        # Apply adjustments while keeping scores in valid range
        for aspect, adjustment in adjustments.items():
            if aspect in adjusted_aspects:
                adjusted_aspects[aspect] = max(0.0, min(1.0, 
                    adjusted_aspects[aspect] + adjustment
                ))
        
        # Recalculate confidence
        avg_confidence = sum(adjusted_aspects.values()) / len(adjusted_aspects)
        
        # Add adjustment info to metadata
        metadata = initial.metadata.copy()
        metadata["adjustments"] = {
            aspect.value: adjustment
            for aspect, adjustment in adjustments.items()
        }
        
        return ValidationResult(
            valid=initial.valid,  # Keep original validity
            confidence=avg_confidence,
            aspects=adjusted_aspects,
            issues=initial.issues,
            suggestions=initial.suggestions,
            metadata=metadata
        )

    def _calculate_text_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Calculate similarity between two texts"""
        # Tokenize and clean texts
        tokens1 = set(self._clean_text(text1).split())
        tokens2 = set(self._clean_text(text2).split())
        
        # Calculate Jaccard similarity
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        
        return intersection / union if union > 0 else 0.0

    def _clean_text(self, text: str) -> str:
        """Clean text for comparison"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text

    def _extract_claims(self, text: str) -> List[str]:
        """Extract factual claims from text"""
        # Split into sentences
        sentences = nltk.sent_tokenize(text)
        
        # Look for claim indicators
        claim_indicators = {
            "is", "are", "was", "were",
            "will", "must", "should",
            "always", "never", "all",
            "none", "every", "most"
        }
        
        claims = []
        for sentence in sentences:
            words = set(sentence.lower().split())
            if any(indicator in words for indicator in claim_indicators):
                claims.append(sentence)
        
        return claims

    def _supports_claim(self, source: str, claim: str) -> bool:
        """Check if source supports a claim"""
        # Calculate similarity
        similarity = self._calculate_text_similarity(source, claim)
        
        # Look for supporting/contradicting language
        supporting_words = {"confirm", "support", "prove", "demonstrate", "show"}
        contradicting_words = {"contradict", "disprove", "refute", "deny", "reject"}
        
        source_words = set(source.lower().split())
        has_support = any(word in source_words for word in supporting_words)
        has_contradiction = any(word in source_words for word in contradicting_words)
        
        # Return true if similar enough and not contradicted
        return similarity > 0.6 and (has_support or not has_contradiction)

    def _calculate_readability(self, text: str) -> float:
        """Calculate text readability score"""
        sentences = nltk.sent_tokenize(text)
        words = nltk.word_tokenize(text)
        
        if not sentences or not words:
            return 0.0
        
        # Calculate basic metrics
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Penalize extremes
        sentence_score = 1.0 - min(1.0, abs(avg_sentence_length - 15) / 15)
        word_score = 1.0 - min(1.0, (avg_word_length - 5) / 5)
        
        return (sentence_score + word_score) / 2

    def _find_complex_terms(self, text: str) -> List[str]:
        """Find complex or technical terms"""
        words = nltk.word_tokenize(text)
        complex_terms = []
        
        for word in words:
            # Check word length
            if len(word) > 12:
                complex_terms.append(word)
                continue
            
            # Check for technical patterns
            if re.search(r'[A-Z]{2,}', word):  # Acronyms
                complex_terms.append(word)
            elif re.search(r'\d.*[a-zA-Z]|[a-zA-Z].*\d', word):  # Alphanumeric
                complex_terms.append(word)
        
        return complex_terms

    def _extract_sources(self, text: str) -> List[str]:
        """Extract source references from text"""
        sources = []
        
        # Look for citation patterns
        patterns = [
            r'\(([^)]+\d{4}[^)]*)\)',  # (Author YYYY)
            r'according to ([^,.]+)',   # according to Source
            r'cited in ([^,.]+)',       # cited in Source
            r'source:\s*([^,.]+)',      # source: Source
            r'reference:\s*([^,.]+)'    # reference: Source
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            sources.extend(match.group(1).strip() for match in matches)
        
        return sources

    async def _evaluate_source_credibility(self, source: str) -> float:
        """Evaluate source credibility"""
        # Define credibility indicators
        credible_domains = {
            "edu": 0.9,
            "gov": 0.9,
            "org": 0.7,
            "ac.uk": 0.9,
            "wikipedia.org": 0.7
        }
        
        # Check for academic citation format
        if re.search(r'[A-Za-z]+,?\s+et al\.?,?\s+\d{4}', source):
            return 0.8
        
        # Check domain credibility
        for domain, score in credible_domains.items():
            if domain in source.lower():
                return score
        
        # Default credibility
        return 0.5

    def _check_logical_structure(self, text: str) -> float:
        """Check logical structure of text"""
        # Look for logical connectors
        connectors = {
            "therefore": 0.3,
            "because": 0.2,
            "if": 0.2,
            "then": 0.2,
            "however": 0.1,
            "moreover": 0.1,
            "furthermore": 0.1,
            "consequently": 0.2,
            "thus": 0.2,
            "hence": 0.2
        }
        
        score = 0.0
        words = text.lower().split()
        
        for word in words:
            if word in connectors:
                score += connectors[word]
        
        return min(1.0, score)

    def _check_argument_strength(self, text: str) -> float:
        """Check argument strength"""
        # Define argument components
        components = {
            "claim": r"(argue|claim|propose|suggest)",
            "evidence": r"(evidence|data|study|research|shows)",
            "warrant": r"(because|since|as|given that)",
            "backing": r"(supported by|based on|according to)",
            "qualifier": r"(most|some|often|usually|typically)",
            "rebuttal": r"(however|although|unless|except)"
        }
        
        score = 0.0
        for component, pattern in components.items():
            if re.search(pattern, text, re.IGNORECASE):
                score += 1/len(components)
        
        return score

    def _check_fallacies(self, text: str) -> List[str]:
        """Check for logical fallacies"""
        fallacies = {
            "ad_hominem": r"(attack.*person|insult.*character)",
            "appeal_authority": r"(expert.*said|authority.*states)",
            "bandwagon": r"(everyone.*does|popular.*therefore)",
            "false_causality": r"(because.*followed|leads to)",
            "hasty_generalization": r"(all.*are|none.*are)",
            "slippery_slope": r"(will lead to|result in.*disaster)",
            "straw_man": r"(misrepresent.*argument|distort.*view)",
            "circular": r"(true because.*true|is because.*is)"
        }
        
        found_fallacies = []
        for fallacy, pattern in fallacies.items():
            if re.search(pattern, text, re.IGNORECASE):
                found_fallacies.append(fallacy)
        
        return found_fallacies

    def _check_tone(self, text: str) -> float:
        """Check tone appropriateness"""
        # Define tone indicators
        informal_words = {"like", "stuff", "things", "kinda", "sort of"}
        emotional_words = {"love", "hate", "awful", "terrible", "amazing"}
        professional_words = {"therefore", "consequently", "furthermore", "moreover"}
        
        words = set(text.lower().split())
        
        informal_count = len(words.intersection(informal_words))
        emotional_count = len(words.intersection(emotional_words))
        professional_count = len(words.intersection(professional_words))
        
        # Calculate tone score
        base_score = 0.7
        base_score -= 0.1 * informal_count
        base_score -= 0.1 * emotional_count
        base_score += 0.1 * professional_count
        
        return max(0.0, min(1.0, base_score))

    def _check_formality(self, text: str) -> float:
        """Check language formality"""
        # Define formality indicators
        contractions = r"('ll|'re|'ve|'m|n't|'s)"
        first_person = r"\b(I|we|my|our)\b"
        active_voice = r"\b(am|is|are|was|were)\b.*\b(by)\b"
        
        # Count indicators
        contraction_count = len(re.findall(contractions, text))
        first_person_count = len(re.findall(first_person, text))
        passive_count = len(re.findall(active_voice, text))
        
        # Calculate formality score
        base_score = 0.8
        base_score -= 0.1 * contraction_count
        base_score -= 0.1 * first_person_count
        base_score += 0.1 * passive_count
        
        return max(0.0, min(1.0, base_score))

"""
Advanced validation module with sophisticated validation strategies.
"""

[Previous content remains the same until _check_answer_consistency method...]

    def _check_answer_consistency(self, answer: str, prev_answer: str) -> float:
        """Check consistency between answers"""
        # Convert to token sets
        answer_tokens = set(nltk.word_tokenize(answer.lower()))
        prev_tokens = set(nltk.word_tokenize(prev_answer.lower()))
        
        # Look for contradictions
        contradiction_markers = {
            "not", "never", "no", "isn't", "aren't", "wasn't",
            "weren't", "doesn't", "don't", "didn't", "cannot"
        }
        
        # Check for semantic contradictions
        for word in contradiction_markers:
            if word in answer_tokens and word not in prev_tokens:
                # Look for the negated statement in previous answer
                negated_statement = self._get_negated_context(word, answer)
                if negated_statement and self._contains_statement(prev_answer, negated_statement):
                    return 0.3  # Significant contradiction
        
        # Calculate semantic similarity
        common_tokens = answer_tokens.intersection(prev_tokens)
        similarity = len(common_tokens) / max(len(answer_tokens), len(prev_tokens))
        
        # Adjust score based on similarity
        if similarity < 0.1:
            return 1.0  # Different topics, no contradiction
        elif similarity > 0.8:
            return 0.9  # High consistency
        else:
            return 0.7  # Moderate consistency

    def _get_negated_context(self, negation: str, text: str) -> Optional[str]:
        """Extract the context of a negation"""
        words = text.split()
        try:
            neg_index = words.index(negation)
            # Get 5 words after negation
            context = ' '.join(words[neg_index+1:neg_index+6])
            return context
        except ValueError:
            return None

    def _contains_statement(self, text: str, statement: str) -> bool:
        """Check if text contains a statement (allowing for variations)"""
        text_tokens = set(nltk.word_tokenize(text.lower()))
        statement_tokens = set(nltk.word_tokenize(statement.lower()))
        
        # Check for significant overlap
        overlap = len(text_tokens.intersection(statement_tokens))
        return overlap / len(statement_tokens) > 0.7

    def _check_domain_consistency(self, answer: str, domain: str) -> float:
        """Check consistency with specified domain"""
        # Define domain-specific keywords
        domain_keywords = {
            "physics": {
                "primary": {"energy", "force", "mass", "particle", "field", "quantum", "velocity"},
                "secondary": {"motion", "acceleration", "momentum", "wave", "matter"}
            },
            "biology": {
                "primary": {"cell", "organism", "species", "gene", "protein", "evolution"},
                "secondary": {"tissue", "membrane", "enzyme", "metabolism", "dna"}
            },
            "computer_science": {
                "primary": {"algorithm", "data", "program", "function", "code", "system"},
                "secondary": {"variable", "memory", "output", "software", "hardware"}
            }
            # Add more domains as needed
        }
        
        if domain not in domain_keywords:
            return 1.0  # No domain-specific check needed
        
        # Check keyword presence
        answer_tokens = set(nltk.word_tokenize(answer.lower()))
        primary_matches = answer_tokens.intersection(domain_keywords[domain]["primary"])
        secondary_matches = answer_tokens.intersection(domain_keywords[domain]["secondary"])
        
        # Calculate domain score
        primary_score = len(primary_matches) * 0.15
        secondary_score = len(secondary_matches) * 0.05
        
        return min(1.0, 0.5 + primary_score + secondary_score)

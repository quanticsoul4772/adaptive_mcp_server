"""
Explanation Formatter Module

Formats reasoning steps, evidence, and explanations into clear, structured documentation.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class ExplanationFormat(Enum):
    """Available explanation formats"""
    PLAIN = "plain"
    MARKDOWN = "markdown"
    JSON = "json"

@dataclass
class ReasoningStep:
    """Represents a single step in the reasoning process"""
    description: str
    evidence: List[str]
    confidence: float
    sources: Optional[List[str]] = None

@dataclass
class ExplanationMetadata:
    """Metadata about the explanation process"""
    strategies_used: List[str]
    total_sources: int
    processing_time: float
    confidence_scores: Dict[str, float]

class ExplanationFormatter:
    """
    Formats reasoning processes into clear explanations.
    
    Features:
    - Multiple output formats
    - Evidence linking
    - Source citation
    - Confidence scoring
    """
    
    def format_explanation(
        self,
        question: str,
        answer: str,
        reasoning_steps: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        format: ExplanationFormat = ExplanationFormat.MARKDOWN
    ) -> str:
        """
        Format complete reasoning process into clear explanation.
        
        Args:
            question: Original question
            answer: Final answer
            reasoning_steps: List of reasoning steps
            metadata: Additional metadata
            format: Desired output format
            
        Returns:
            Formatted explanation
        """
        if format == ExplanationFormat.MARKDOWN:
            return self._format_markdown(question, answer, reasoning_steps, metadata)
        elif format == ExplanationFormat.PLAIN:
            return self._format_plain(question, answer, reasoning_steps, metadata)
        else:
            return self._format_json(question, answer, reasoning_steps, metadata)

    def _format_markdown(
        self,
        question: str,
        answer: str,
        reasoning_steps: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> str:
        """Format explanation as Markdown"""
        # Format main sections
        sections = [
            "# Question Analysis and Answer\n",
            f"**Question:** {question}\n",
            f"**Answer:** {answer}\n",
            "\n## Reasoning Process\n"
        ]
        
        # Add reasoning steps
        for i, step in enumerate(reasoning_steps, 1):
            sections.extend([
                f"### Step {i}: {step['step']}\n",
                f"{step['output']}\n",
                f"*Confidence: {step.get('confidence', 'N/A')}*\n"
            ])
            
            # Add evidence if present
            if 'evidence' in step:
                sections.append("\n**Supporting Evidence:**\n")
                for evidence in step['evidence']:
                    sections.append(f"- {evidence}\n")
        
        # Add metadata section
        sections.extend([
            "\n## Additional Information\n",
            "**Strategies Used:**\n"
        ])
        
        for strategy in metadata.get('strategies_used', []):
            sections.append(f"- {strategy}\n")
            
        if 'confidence' in metadata:
            sections.append(f"\n**Overall Confidence:** {metadata['confidence']:.2f}\n")
            
        if 'sources' in metadata:
            sections.extend([
                "\n**Sources Consulted:**\n",
                *[f"- {source}\n" for source in metadata['sources']]
            ])
        
        return ''.join(sections)

    def _format_plain(
        self,
        question: str,
        answer: str,
        reasoning_steps: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> str:
        """Format explanation as plain text"""
        # Format main sections
        sections = [
            "QUESTION ANALYSIS AND ANSWER\n",
            f"Question: {question}\n",
            f"Answer: {answer}\n",
            "\nREASONING PROCESS\n"
        ]
        
        # Add reasoning steps
        for i, step in enumerate(reasoning_steps, 1):
            sections.extend([
                f"\nStep {i}: {step['step']}\n",
                f"{step['output']}\n",
                f"Confidence: {step.get('confidence', 'N/A')}\n"
            ])
            
            if 'evidence' in step:
                sections.append("\nSupporting Evidence:\n")
                for evidence in step['evidence']:
                    sections.append(f"* {evidence}\n")
        
        # Add metadata
        sections.extend([
            "\nADDITIONAL INFORMATION\n",
            "Strategies Used:\n"
        ])
        
        for strategy in metadata.get('strategies_used', []):
            sections.append(f"* {strategy}\n")
            
        if 'confidence' in metadata:
            sections.append(f"\nOverall Confidence: {metadata['confidence']:.2f}\n")
            
        if 'sources' in metadata:
            sections.extend([
                "\nSources Consulted:\n",
                *[f"* {source}\n" for source in metadata['sources']]
            ])
        
        return ''.join(sections)

    def _format_json(
        self,
        question: str,
        answer: str,
        reasoning_steps: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> str:
        """Format explanation as JSON"""
        import json
        
        explanation = {
            "question": question,
            "answer": answer,
            "reasoning_process": [
                {
                    "step_number": i,
                    "description": step['step'],
                    "output": step['output'],
                    "confidence": step.get('confidence'),
                    "evidence": step.get('evidence', [])
                }
                for i, step in enumerate(reasoning_steps, 1)
            ],
            "metadata": metadata
        }
        
        return json.dumps(explanation, indent=2)

    def get_summary(
        self,
        question: str,
        answer: str,
        reasoning_steps: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> str:
        """Generate brief summary of reasoning process"""
        # Get key points from reasoning
        key_steps = [
            step['step']
            for step in reasoning_steps
            if step.get('confidence', 0) > 0.7
        ]
        
        # Format summary
        summary = [
            f"Question: {question}\n",
            f"Answer: {answer}\n",
            "\nKey Reasoning Steps:\n"
        ]
        
        for i, step in enumerate(key_steps, 1):
            summary.append(f"{i}. {step}\n")
            
        if 'confidence' in metadata:
            summary.append(f"\nOverall Confidence: {metadata['confidence']:.2f}")
            
        return ''.join(summary)

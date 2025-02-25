"""Tests for the explanation formatter module"""

import json
from ..explanation.formatter import (
    ExplanationFormatter,
    ExplanationFormat,
    ReasoningStep,
    ExplanationMetadata
)

def test_formatter_initialization():
    """Test formatter initialization"""
    formatter = ExplanationFormatter()
    assert isinstance(formatter, ExplanationFormatter)

def test_markdown_formatting():
    """Test Markdown format output"""
    formatter = ExplanationFormatter()
    
    # Test data
    question = "What is the capital of France?"
    answer = "The capital of France is Paris."
    reasoning_steps = [
        {
            "step": "Research",
            "output": "Found multiple sources confirming Paris as capital",
            "confidence": 0.9,
            "evidence": ["Official geographic data", "Historical records"]
        },
        {
            "step": "Verification",
            "output": "Verified current status",
            "confidence": 0.95
        }
    ]
    metadata = {
        "strategies_used": ["research", "verification"],
        "confidence": 0.92,
        "sources": ["Geographic database", "Government records"]
    }
    
    # Generate markdown
    markdown = formatter.format_explanation(
        question, answer, reasoning_steps, metadata,
        format=ExplanationFormat.MARKDOWN
    )
    
    # Check markdown formatting
    assert "# Question Analysis" in markdown
    assert "**Question:**" in markdown
    assert "**Answer:**" in markdown
    assert "### Step 1:" in markdown
    assert "### Step 2:" in markdown
    assert "*Confidence:" in markdown
    assert "**Supporting Evidence:**" in markdown
    assert "- Official geographic data" in markdown

def test_plain_text_formatting():
    """Test plain text format output"""
    formatter = ExplanationFormatter()
    
    # Test data
    question = "How does photosynthesis work?"
    answer = "Photosynthesis converts sunlight into energy."
    reasoning_steps = [
        {
            "step": "Basic explanation",
            "output": "Process overview",
            "confidence": 0.8
        }
    ]
    metadata = {
        "strategies_used": ["scientific"],
        "confidence": 0.8
    }
    
    # Generate plain text
    plain = formatter.format_explanation(
        question, answer, reasoning_steps, metadata,
        format=ExplanationFormat.PLAIN
    )
    
    # Check plain text formatting
    assert "QUESTION ANALYSIS AND ANSWER" in plain
    assert "Question:" in plain
    assert "Answer:" in plain
    assert "Step 1:" in plain
    assert "ADDITIONAL INFORMATION" in plain
    assert "Confidence:" in plain

def test_json_formatting():
    """Test JSON format output"""
    formatter = ExplanationFormatter()
    
    # Test data
    question = "Test question?"
    answer = "Test answer."
    reasoning_steps = [
        {
            "step": "Step 1",
            "output": "Output 1",
            "confidence": 0.8
        }
    ]
    metadata = {
        "strategies_used": ["test"],
        "confidence": 0.8
    }
    
    # Generate JSON
    json_output = formatter.format_explanation(
        question, answer, reasoning_steps, metadata,
        format=ExplanationFormat.JSON
    )
    
    # Parse and verify JSON structure
    parsed = json.loads(json_output)
    assert "question" in parsed
    assert "answer" in parsed
    assert "reasoning_process" in parsed
    assert "metadata" in parsed
    assert len(parsed["reasoning_process"]) == 1
    assert parsed["reasoning_process"][0]["step_number"] == 1

def test_summary_generation():
    """Test summary generation"""
    formatter = ExplanationFormatter()
    
    # Test data
    question = "What is quantum computing?"
    answer = "Quantum computing uses quantum mechanics for computation."
    reasoning_steps = [
        {
            "step": "Basic definition",
            "output": "Quantum computing explanation",
            "confidence": 0.9
        },
        {
            "step": "Low confidence step",
            "output": "Additional details",
            "confidence": 0.5
        }
    ]
    metadata = {
        "confidence": 0.85
    }
    
    # Generate summary
    summary = formatter.get_summary(question, answer, reasoning_steps, metadata)
    
    # Verify summary content
    assert question in summary
    assert answer in summary
    assert "Key Reasoning Steps:" in summary
    assert "Basic definition" in summary  # High confidence step
    assert "Low confidence step" not in summary  # Low confidence step
    assert "Overall Confidence: 0.85" in summary

def test_evidence_handling():
    """Test handling of evidence in formatting"""
    formatter = ExplanationFormatter()
    
    # Test data with evidence
    reasoning_steps = [
        {
            "step": "Research",
            "output": "Research results",
            "confidence": 0.8,
            "evidence": [
                "Evidence item 1",
                "Evidence item 2"
            ]
        }
    ]
    
    # Test in different formats
    markdown = formatter.format_explanation(
        "Q", "A", reasoning_steps, {},
        format=ExplanationFormat.MARKDOWN
    )
    assert "**Supporting Evidence:**" in markdown
    assert "- Evidence item 1" in markdown
    
    plain = formatter.format_explanation(
        "Q", "A", reasoning_steps, {},
        format=ExplanationFormat.PLAIN
    )
    assert "Supporting Evidence:" in plain
    assert "* Evidence item 1" in plain
    
    json_output = formatter.format_explanation(
        "Q", "A", reasoning_steps, {},
        format=ExplanationFormat.JSON
    )
    parsed = json.loads(json_output)
    assert "evidence" in parsed["reasoning_process"][0]
    assert len(parsed["reasoning_process"][0]["evidence"]) == 2

def test_edge_cases():
    """Test handling of edge cases"""
    formatter = ExplanationFormatter()
    
    # Empty/minimal data
    minimal = formatter.format_explanation(
        "", "", [], {},
        format=ExplanationFormat.MARKDOWN
    )
    assert minimal.strip() != ""
    
    # Missing optional fields
    no_options = formatter.format_explanation(
        "Q", "A",
        [{"step": "Step", "output": "Output"}],
        {}
    )
    assert "N/A" in no_options  # Default for missing confidence
    
    # Unicode characters
    unicode_test = formatter.format_explanation(
        "¿Qué?", "答え", 
        [{"step": "テスト", "output": "résultat"}],
        {}
    )
    assert "¿Qué?" in unicode_test
    assert "答え" in unicode_test
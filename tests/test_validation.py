"""
Comprehensive Validation Testing for MCP Server
"""

import pytest
import asyncio
from validators import advanced_validator

@pytest.mark.asyncio
async def test_basic_validation():
    """
    Test basic validation functionality
    """
    test_cases = [
        {
            'question': 'What is the capital of France?',
            'answer': 'Paris is the capital of France.',
            'expected_validity': True
        },
        {
            'question': 'Explain quantum mechanics',
            'answer': 'Quantum mechanics is a fundamental theory in physics that describes nature at the smallest scales of energy levels of atoms and subatomic particles.',
            'expected_validity': True
        },
        {
            'question': 'What is 2 + 2?',
            'answer': '5',
            'expected_validity': False
        }
    ]

    for case in test_cases:
        validation_result = await advanced_validator.validate(
            question=case['question'],
            answer=case['answer']
        )
        
        assert 'valid' in validation_result
        assert 'confidence' in validation_result
        assert validation_result['valid'] == case['expected_validity']

@pytest.mark.asyncio
async def test_semantic_validation():
    """
    Test semantic validation capabilities
    """
    test_cases = [
        {
            'question': 'What causes gravity?',
            'answer': 'Gravity is caused by the curvature of spacetime as described by Einstein\'s theory of general relativity.',
            'min_semantic_score': 0.7
        },
        {
            'question': 'Explain photosynthesis',
            'answer': 'A process by which plants use sunlight to convert carbon dioxide and water into glucose and oxygen.',
            'min_semantic_score': 0.7
        }
    ]

    for case in test_cases:
        validation_result = await advanced_validator.validate(
            question=case['question'],
            answer=case['answer']
        )
        
        semantic_score = validation_result.get('aspects', {}).get('semantic_similarity', 0)
        assert semantic_score >= case['min_semantic_score'], f"Semantic score too low for: {case['question']}"

@pytest.mark.asyncio
async def test_complex_validation():
    """
    Test validation with complex scenarios
    """
    test_cases = [
        {
            'question': 'What are the potential solutions to climate change?',
            'answer': 'Solutions include renewable energy, carbon capture, reforestation, and reducing fossil fuel consumption.',
            'checks': {
                'has_multiple_solutions': True,
                'includes_actionable_items': True
            }
        },
        {
            'question': 'Describe the moon landing',
            'answer': 'Humans first landed on the moon during the Apollo 11 mission on July 20, 1969, with Neil Armstrong and Buzz Aldrin becoming the first humans to walk on the lunar surface.',
            'checks': {
                'includes_key_details': True,
                'historical_accuracy': True
            }
        }
    ]

    for case in test_cases:
        validation_result = await advanced_validator.validate(
            question=case['question'],
            answer=case['answer']
        )
        
        # Additional custom validation checks
        for check, expected in case['checks'].items():
            assert check in validation_result.get('metadata', {}), f"Missing check: {check}"

@pytest.mark.asyncio
async def test_error_handling():
    """
    Test validator error handling
    """
    # Test empty inputs
    with pytest.raises(ValueError):
        await advanced_validator.validate(question='', answer='')
    
    # Test extremely long inputs
    long_question = 'x' * 10000
    long_answer = 'y' * 20000
    
    validation_result = await advanced_validator.validate(
        question=long_question, 
        answer=long_answer
    )
    
    assert 'valid' in validation_result
    assert 'confidence' in validation_result

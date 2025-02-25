"""
Validation Demonstration for Adaptive MCP Server
"""

import asyncio
from validators import advanced_validator

async def main():
    # Test cases with varying complexity
    test_cases = [
        {
            'question': 'What is photosynthesis?',
            'answer': 'Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy that can be later released to fuel the organisms\' activities.',
            'description': 'Scientifically accurate definition'
        },
        {
            'question': 'Explain gravity',
            'answer': 'Gravity is a force that attracts objects with mass towards each other. According to Einstein\'s theory of general relativity, massive objects cause a distortion in space-time, which is perceived as gravity.',
            'description': 'Complex scientific explanation'
        },
        {
            'question': 'What is 2 + 2?',
            'answer': '5',
            'description': 'Intentionally incorrect answer'
        }
    ]

    for case in test_cases:
        print(f"\n--- Validating: {case['description']} ---")
        print(f"Question: {case['question']}")
        print(f"Answer: {case['answer']}")
        
        try:
            # Perform validation
            validation_result = await advanced_validator.validate(
                question=case['question'],
                answer=case['answer']
            )
            
            # Display validation details
            print("\nValidation Results:")
            print(f"Valid: {validation_result.get('valid', False)}")
            print(f"Confidence: {validation_result.get('confidence', 0)}")
            
            # Display detailed aspects
            print("\nValidation Aspects:")
            for aspect, score in validation_result.get('aspects', {}).items():
                print(f"- {aspect}: {score}")
            
            # Display any suggestions
            suggestions = validation_result.get('suggestions', [])
            if suggestions:
                print("\nImprovement Suggestions:")
                for suggestion in suggestions:
                    print(f"- {suggestion}")
        
        except Exception as e:
            print(f"Validation error: {e}")

if __name__ == '__main__':
    asyncio.run(main())

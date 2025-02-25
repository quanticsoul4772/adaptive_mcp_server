"""
Basic Reasoning Example for Adaptive MCP Server
"""

import asyncio
from reasoning import reasoning_orchestrator

async def main():
    # Example questions demonstrating different reasoning approaches
    questions = [
        "What is the capital of France?",
        "Explain the concept of quantum entanglement",
        "What are innovative solutions to reduce plastic waste?",
        "How do economic policies impact social inequality?"
    ]

    for question in questions:
        print(f"\n--- Reasoning for: {question} ---")
        
        try:
            # Perform reasoning
            result = await reasoning_orchestrator.reason(question)
            
            # Print results
            print("Answer:", result['answer'])
            print("Confidence:", result['confidence'])
            print("Strategies Used:", result['metadata'].get('strategies_used', []))
            
            # Detailed reasoning steps
            print("\nReasoning Steps:")
            for step in result.get('reasoning_steps', []):
                print(f"- {step}")
        
        except Exception as e:
            print(f"Error processing question: {e}")

if __name__ == '__main__':
    asyncio.run(main())

"""
Advanced Research Integration Example
"""

import asyncio
from research import research_integrator

async def main():
    # Complex research queries
    queries = [
        "Latest advances in artificial intelligence",
        "Climate change mitigation strategies",
        "Evolution of quantum computing",
        "Sustainable urban development approaches"
    ]

    for query in queries:
        print(f"\n--- Researching: {query} ---")
        
        try:
            # Perform research
            context = await research_integrator.research(query)
            
            # Extract and display key information
            extracted_info = research_integrator.extract_key_information(context)
            
            print("Research Confidence:", context.confidence)
            print("\nKey Sources:")
            for source in extracted_info['sources']:
                print(f"- {source['url']} (Relevance: {source['relevance']})")
            
            print("\nKey Facts:")
            for fact in extracted_info['key_facts']:
                print(f"- {fact}")
        
        except Exception as e:
            print(f"Research error: {e}")

if __name__ == '__main__':
    asyncio.run(main())

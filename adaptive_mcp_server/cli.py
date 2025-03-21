"""
Command Line Interface for Adaptive MCP Server
"""

import argparse
import asyncio
import logging
import json
from typing import Dict, Any, Optional

# Import the orchestrator
try:
    from reasoning.orchestrator import reasoning_orchestrator
except ImportError:
    # Try with package prefix
    from adaptive_mcp_server.reasoning.orchestrator import reasoning_orchestrator

logger = logging.getLogger("adaptive_mcp_server.cli")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Adaptive MCP Server - Multi-strategy reasoning system"
    )
    
    # Main commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Reason command
    reason_parser = subparsers.add_parser("reason", help="Answer a question using reasoning strategies")
    reason_parser.add_argument("question", help="The question to reason about")
    reason_parser.add_argument(
        "--strategy", 
        choices=["sequential", "branching", "abductive", "lateral", "logical", "auto"],
        default="auto",
        help="Reasoning strategy to use (default: auto)"
    )
    reason_parser.add_argument(
        "--output", 
        choices=["simple", "detailed", "json"],
        default="simple",
        help="Output format (default: simple)"
    )
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start the MCP server")
    server_parser.add_argument(
        "--host", 
        default="localhost",
        help="Host to bind the server (default: localhost)"
    )
    server_parser.add_argument(
        "--port", 
        type=int,
        default=8000,
        help="Port to bind the server (default: 8000)"
    )
    
    return parser.parse_args()

async def process_question(question: str, strategy: str = "auto") -> Dict[str, Any]:
    """
    Process a question using the specified reasoning strategy
    
    Args:
        question: The question to process
        strategy: The reasoning strategy to use
        
    Returns:
        The reasoning result
    """
    try:
        # Pass directly to orchestrator
        return await reasoning_orchestrator.reason(question)
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        return {
            "answer": f"Error: {str(e)}",
            "confidence": 0.0,
            "reasoning_steps": [],
            "metadata": {"error": str(e)}
        }

def format_output(result: Dict[str, Any], format_type: str) -> str:
    """
    Format the reasoning result based on the specified output format
    
    Args:
        result: The reasoning result
        format_type: The output format (simple, detailed, json)
        
    Returns:
        The formatted output
    """
    if format_type == "json":
        return json.dumps(result, indent=2)
    
    if format_type == "simple":
        return f"{result.get('answer', 'No answer available')}"
    
    # Detailed format
    output = []
    output.append(f"Answer: {result.get('answer', 'No answer available')}")
    output.append(f"Confidence: {result.get('confidence', 0.0):.2f}")
    
    # Add reasoning steps
    steps = result.get("reasoning_steps", [])
    if steps:
        output.append("\nReasoning steps:")
        for i, step in enumerate(steps, 1):
            output.append(f"  {i}. {step.get('step', 'Unknown step')}")
            output.append(f"     Output: {step.get('output', 'No output')}")
            if "confidence" in step:
                output.append(f"     Confidence: {step.get('confidence', 0.0):.2f}")
    
    # Add metadata
    metadata = result.get("metadata", {})
    if metadata:
        output.append("\nMetadata:")
        for key, value in metadata.items():
            if isinstance(value, list):
                output.append(f"  {key}: {', '.join(str(v) for v in value)}")
            else:
                output.append(f"  {key}: {value}")
    
    return "\n".join(output)

def main() -> int:
    """Main entry point for the CLI"""
    args = parse_args()
    
    if args.command == "reason":
        # Process the question
        result = asyncio.run(process_question(args.question, args.strategy))
        print(format_output(result, args.output))
        return 0
    
    elif args.command == "server":
        print(f"Starting server on {args.host}:{args.port}")
        # TODO: Implement server functionality
        print("Server functionality not implemented yet")
        return 1
    
    else:
        print("Please specify a command. Use --help for more information.")
        return 1

if __name__ == "__main__":
    main()

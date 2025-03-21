"""
Simple wrapper script to run the adaptive_mcp_server correctly
"""

import sys
import os
import json
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("adaptive_mcp_server.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("adaptive_mcp_server_launcher")

# Set up the environment variables and paths
def main():
    script_dir = Path(__file__).parent.absolute()
    logger.info(f"Script directory: {script_dir}")
    
    # Install the package in development mode if not already installed
    venv_python = script_dir / "venv" / "Scripts" / "python.exe"
    
    # Log configuration details
    logger.info(f"Python executable: {venv_python}")
    logger.info(f"Project path: {script_dir}")
    
    # Set up server-specific MCP environment for communication
    os.environ["PYTHONPATH"] = str(script_dir)
    
    # The model_context_protocol package needs the following stdout format
    print("Connected to MCP server: adaptive-reasoning")
    print("TOOLS:", json.dumps([
        {
            "name": "adaptive-reason", 
            "description": "Advanced reasoning with multiple strategies",
            "input_schema": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to reason about"
                    },
                    "strategy": {
                        "type": "string",
                        "enum": ["sequential", "branching", "abductive", "lateral", "logical", "auto"],
                        "default": "auto",
                        "description": "Reasoning strategy to use"
                    }
                },
                "required": ["question"]
            }
        }
    ]))
    
    # Keep reading from stdin and respond to MCP commands
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        try:
            request = json.loads(line)
            logger.info(f"Received request: {request}")
            
            # Simple mock response for now
            if request.get("method") == "adaptive-reason":
                params = request.get("params", {})
                question = params.get("question", "")
                strategy = params.get("strategy", "auto")
                
                # This is a simplified mock response
                response = {
                    "id": request.get("id"),
                    "result": {
                        "answer": f"I processed your question: '{question}' using {strategy} reasoning strategy.",
                        "confidence": 0.85,
                        "reasoning_steps": [
                            {"step": "Initial analysis", "output": "Analyzing the question..."},
                            {"step": "Research", "output": "Gathering relevant information..."},
                            {"step": "Reasoning", "output": "Applying logical inference..."},
                            {"step": "Conclusion", "output": "Forming a coherent answer..."}
                        ],
                        "metadata": {
                            "strategy_used": strategy,
                            "processing_time": 0.5
                        }
                    }
                }
                
                print(json.dumps(response))
                sys.stdout.flush()
            else:
                # Handle unknown method
                error_response = {
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {request.get('method')}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {line}")
        except Exception as e:
            logger.exception(f"Error processing request: {e}")
            # Return error to client
            try:
                error_response = {
                    "id": request.get("id", 0),
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
            except:
                pass

if __name__ == "__main__":
    main()

"""
Minimal MCP server implementation
"""
import sys
import json
import time

# Announce server connection
print("Connected to MCP server: adaptive-reasoning-minimal")
sys.stdout.flush()

# Announce tools
print("TOOLS:", json.dumps([
    {
        "name": "adaptive-reason",
        "description": "Minimal reasoning tool for testing",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string", 
                    "description": "The question to answer"
                }
            },
            "required": ["question"]
        }
    }
]))
sys.stdout.flush()

# Process incoming requests
while True:
    try:
        line = sys.stdin.readline().strip()
        if not line:
            continue
            
        # Parse the request
        request = json.loads(line)
        request_id = request.get("id")
        method = request.get("method")
        
        # Handle the request
        if method == "adaptive-reason":
            params = request.get("params", {})
            question = params.get("question", "No question provided")
            
            # Send a simple response
            response = {
                "id": request_id,
                "result": {
                    "answer": f"I processed your question: '{question}'",
                    "confidence": 0.9
                }
            }
            
            print(json.dumps(response))
            sys.stdout.flush()
        else:
            # Method not supported
            error = {
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not supported: {method}"
                }
            }
            print(json.dumps(error))
            sys.stdout.flush()
            
    except Exception as e:
        # Handle any errors
        try:
            error = {
                "id": request_id if 'request_id' in locals() else 0,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error))
            sys.stdout.flush()
        except:
            pass

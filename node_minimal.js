// Simple Node.js MCP server for testing

// Announce the server connection
console.log("Connected to MCP server: adaptive-reasoning-node");

// Announce the tools
console.log("TOOLS:", JSON.stringify([
  {
    "name": "adaptive-reason-node",
    "description": "Advanced reasoning tool (Node.js implementation)",
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
]));

// Process incoming requests from stdin
process.stdin.setEncoding('utf8');
let inputBuffer = '';

process.stdin.on('data', (chunk) => {
  inputBuffer += chunk;
  
  // Process complete lines
  const lines = inputBuffer.split('\n');
  inputBuffer = lines.pop(); // Keep the last incomplete line
  
  for (const line of lines) {
    if (line.trim()) {
      try {
        const request = JSON.parse(line);
        handleRequest(request);
      } catch (err) {
        console.error('Error parsing request:', err.message);
      }
    }
  }
});

function handleRequest(request) {
  const requestId = request.id;
  const method = request.method;
  
  if (method === 'adaptive-reason-node') {
    const params = request.params || {};
    const question = params.question || 'No question provided';
    const strategy = params.strategy || 'auto';
    
    // Create a response
    const response = {
      id: requestId,
      result: {
        answer: `I processed your question: '${question}' using ${strategy} reasoning strategy.`,
        confidence: 0.9,
        reasoning_steps: [
          { step: "Initial analysis", output: "Analyzing the question..." },
          { step: "Reasoning", output: "Applying logical inference..." },
          { step: "Conclusion", output: "Forming an answer..." }
        ],
        metadata: {
          strategy_used: strategy,
          processing_time: 0.5
        }
      }
    };
    
    console.log(JSON.stringify(response));
  } else {
    // Method not supported
    const error = {
      id: requestId,
      error: {
        code: -32601,
        message: `Method not supported: ${method}`
      }
    };
    
    console.log(JSON.stringify(error));
  }
}

// Keep the process running
setInterval(() => {}, 1000);

// JSON-RPC 2.0 compliant MCP server

// Import required Node.js modules
const readline = require('readline');

// Set up readline interface for stdio communication
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

// Track request IDs
let nextId = 1;

// Define available tools
const tools = [
  {
    name: "adaptive-reason",
    description: "Advanced reasoning with multiple strategies",
    input_schema: {
      type: "object",
      properties: {
        question: {
          type: "string",
          description: "The question to reason about"
        },
        strategy: {
          type: "string",
          enum: ["sequential", "branching", "abductive", "lateral", "logical", "auto"],
          default: "auto",
          description: "Reasoning strategy to use"
        }
      },
      required: ["question"]
    }
  }
];

// Send a valid JSON-RPC response
function sendResponse(id, result) {
  const response = {
    jsonrpc: "2.0",
    id: id,
    result: result
  };
  console.log(JSON.stringify(response));
}

// Send a valid JSON-RPC error
function sendError(id, code, message, data = undefined) {
  const error = {
    jsonrpc: "2.0",
    id: id,
    error: {
      code: code,
      message: message
    }
  };
  
  if (data !== undefined) {
    error.error.data = data;
  }
  
  console.log(JSON.stringify(error));
}

// Handle the initialize method
function handleInitialize(id, params) {
  // Respond with capabilities and tool definitions
  sendResponse(id, {
    serverInfo: {
      name: "adaptive-reasoning-server",
      version: "0.1.0"
    },
    capabilities: {},
    tools: tools
  });
}

// Handle the adaptive-reason method
function handleAdaptiveReason(id, params) {
  // Extract parameters
  const question = params.question || "No question provided";
  const strategy = params.strategy || "auto";
  
  // Generate a mock response
  const result = {
    answer: `I processed your question: '${question}' using ${strategy} reasoning strategy.`,
    confidence: 0.85,
    reasoning_steps: [
      { step: "Initial analysis", output: "Analyzing the question..." },
      { step: "Research", output: "Gathering relevant information..." },
      { step: "Reasoning", output: "Applying logical inference..." },
      { step: "Conclusion", output: "Forming a coherent answer..." }
    ],
    metadata: {
      strategy_used: strategy,
      processing_time: 0.5
    }
  };
  
  // Send the response
  sendResponse(id, result);
}

// Process incoming messages
rl.on('line', (line) => {
  // Skip empty lines
  if (!line.trim()) return;
  
  try {
    // Parse the JSON-RPC request
    const request = JSON.parse(line);
    
    // Log the request to stderr for debugging
    console.error(`Received request: ${JSON.stringify(request)}`);
    
    // Make sure it's a valid JSON-RPC 2.0 request
    if (request.jsonrpc !== "2.0") {
      sendError(request.id || null, -32600, "Invalid Request: Not a valid JSON-RPC 2.0 request");
      return;
    }
    
    // Process the method
    switch (request.method) {
      case "initialize":
        handleInitialize(request.id, request.params || {});
        break;
      
      case "adaptive-reason":
        handleAdaptiveReason(request.id, request.params || {});
        break;
        
      case "shutdown":
        sendResponse(request.id, null);
        // Don't exit immediately - wait for any pending operations
        setTimeout(() => process.exit(0), 1000);
        break;
        
      default:
        sendError(request.id, -32601, `Method not found: ${request.method}`);
        break;
    }
  } catch (err) {
    console.error(`Error processing request: ${err.message}`);
    sendError(null, -32700, "Parse error", { details: err.message });
  }
});

// Keep the process alive with an interval
const keepAlive = setInterval(() => {
  console.error('Server still alive - ' + new Date().toISOString());
}, 30000);

// Handle process termination gracefully
process.on('SIGINT', () => {
  console.error('SIGINT received, shutting down');
  clearInterval(keepAlive);
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.error('SIGTERM received, shutting down');
  clearInterval(keepAlive);
  process.exit(0);
});

// Prevent the process from closing if there's an uncaught exception
process.on('uncaughtException', (err) => {
  console.error(`Uncaught exception: ${err.message}`);
  console.error(err.stack);
});

// Log startup message to stderr
console.error('Adaptive reasoning MCP server started at ' + new Date().toISOString());

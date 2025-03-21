// MCP Server implementation using Node.js following the official MCP specification
// Based on the JSON-RPC 2.0 protocol

const fs = require('fs');
const readline = require('readline');
const { Buffer } = require('buffer');

// Log to a file for debugging
const logFile = fs.createWriteStream('mcp_server.log', { flags: 'a' });
function log(message) {
  const timestamp = new Date().toISOString();
  logFile.write(`${timestamp}: ${message}\n`);
}

// Initialize the server
log('Starting MCP server...');

// Ensure stdout doesn't buffer response
process.stdout.setDefaultEncoding('utf8');

// Set up the readline interface without closing on Ctrl+C
const rl = readline.createInterface({
  input: process.stdin,
  output: null,  // Don't output to stdout through readline
  terminal: false
});

// Define server tools
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

// Send a JSON-RPC 2.0 message
function sendMessage(msg) {
  try {
    const jsonStr = JSON.stringify(msg);
    log(`Sending message: ${jsonStr}`);
    process.stdout.write(jsonStr + '\n');
  } catch (error) {
    log(`Error serializing message: ${error.message}`);
  }
}

// Send a JSON-RPC 2.0 response
function sendResponse(id, result) {
  sendMessage({
    jsonrpc: "2.0",
    id: id,
    result: result
  });
}

// Send a JSON-RPC 2.0 error
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
  
  sendMessage(error);
}

// Handle the initialize method
function handleInitialize(id, params) {
  log(`Handling initialize request with id: ${id}`);
  
  // Respond with capabilities and tool definitions
  sendResponse(id, {
    serverInfo: {
      name: "adaptive-reasoning-server",
      version: "0.1.0"
    },
    capabilities: {},
    tools: tools
  });
  
  log('Initialize response sent');
}

// Handle the adaptive-reason method
function handleAdaptiveReason(id, params) {
  log(`Handling adaptive-reason request with id: ${id}, params: ${JSON.stringify(params)}`);
  
  // Extract parameters
  const question = params.question || "No question provided";
  const strategy = params.strategy || "auto";
  
  // Generate a response
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
  log('Adaptive reasoning response sent');
}

// Process incoming messages
rl.on('line', (line) => {
  // Skip empty lines
  if (!line || !line.trim()) {
    log('Received empty line, skipping');
    return;
  }
  
  log(`Received message: ${line}`);
  
  try {
    // Parse the JSON-RPC request
    const request = JSON.parse(line);
    
    // Make sure it's a valid JSON-RPC 2.0 request
    if (request.jsonrpc !== "2.0") {
      log('Invalid JSON-RPC request: missing or invalid jsonrpc field');
      sendError(request.id || null, -32600, "Invalid Request: Not a valid JSON-RPC 2.0 request");
      return;
    }
    
    // Process the method
    log(`Processing method: ${request.method}`);
    switch (request.method) {
      case "initialize":
        handleInitialize(request.id, request.params || {});
        break;
      
      case "adaptive-reason":
        handleAdaptiveReason(request.id, request.params || {});
        break;
        
      case "shutdown":
        log('Received shutdown request, sending response');
        sendResponse(request.id, null);
        // Don't exit immediately - allow time for response to be sent
        setTimeout(() => {
          log('Shutting down gracefully');
          process.exit(0);
        }, 500);
        break;
        
      default:
        log(`Method not found: ${request.method}`);
        sendError(request.id, -32601, `Method not found: ${request.method}`);
        break;
    }
  } catch (err) {
    log(`Error processing request: ${err.message}`);
    sendError(null, -32700, "Parse error", { details: err.message });
  }
});

// Handle process events to ensure graceful cleanup
process.on('SIGINT', () => {
  log('SIGINT received, shutting down');
  process.exit(0);
});

process.on('SIGTERM', () => {
  log('SIGTERM received, shutting down');
  process.exit(0);
});

// Prevent the process from closing if there's an uncaught exception
process.on('uncaughtException', (err) => {
  log(`Uncaught exception: ${err.message}\n${err.stack}`);
});

// Properly handle process exit
process.on('exit', () => {
  log('Process exiting, cleaning up');
  rl.close();
  logFile.end();
});

// Keep the process running (Node.js stdio streams should keep it running naturally)
log('MCP server started and ready to process requests');

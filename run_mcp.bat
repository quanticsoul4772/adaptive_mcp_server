@echo off
echo Connected to MCP server: adaptive-reasoning-batch
echo TOOLS: [{"name":"adaptive-reason-batch","description":"Reasoning tool launched through batch file","input_schema":{"type":"object","properties":{"question":{"type":"string","description":"The question to reason about"}},"required":["question"]}}]

set "PYTHONPATH=C:\project-root\adaptive_mcp_server"

C:\project-root\adaptive_mcp_server\venv\Scripts\python.exe C:\project-root\adaptive_mcp_server\mcp_minimal.py

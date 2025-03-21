"""
Main entry point for the Adaptive MCP Server
"""

import sys
import logging
from adaptive_mcp_server.cli import main

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    sys.exit(main())

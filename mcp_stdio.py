#!/usr/bin/env python3
"""MCP Server - stdio transport.

This script runs the PyATS MCP server using stdio (standard input/output) transport.
Used for local AI assistants like Claude Desktop.

Usage:
    python mcp_stdio.py

Configuration:
    Set environment variables for jumphost (optional):
    - JUMPHOST_HOST
    - JUMPHOST_PORT
    - JUMPHOST_USERNAME
    - JUMPHOST_KEY_PATH
"""

import asyncio
import logging
from mcp.server.stdio import stdio_server

from mcp_server import server

# Configure logging to stderr (stdout is used for MCP protocol)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # Logs go to stderr
)
logger = logging.getLogger(__name__)


async def main():
    """Run the MCP server with stdio transport."""
    logger.info("Starting PyATS MCP Server (stdio transport)")
    logger.info("Waiting for MCP client connection via stdin/stdout...")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())

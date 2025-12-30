#!/usr/bin/env python3
"""MCP Server - SSE (Server-Sent Events) transport.

This script runs the PyATS MCP server using SSE over HTTP.
Used for remote access and web-based MCP clients.

Usage:
    python mcp_sse.py

Configuration:
    Environment variables:
    - MCP_HOST: Host to bind to (default: 0.0.0.0)
    - MCP_PORT: Port to listen on (default: 3000)
    - JUMPHOST_HOST: Jumphost hostname (optional)
    - JUMPHOST_PORT: Jumphost SSH port (optional)
    - JUMPHOST_USERNAME: Jumphost username (optional)
    - JUMPHOST_KEY_PATH: Path to jumphost SSH key (optional)

Endpoints:
    - GET  /sse - SSE endpoint for MCP protocol
    - GET  /health - Health check endpoint
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sse_starlette import EventSourceResponse
from mcp.server.sse import SseServerTransport

from mcp_server import server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "3000"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info("Starting PyATS MCP Server (SSE transport)")
    logger.info(f"Listening on http://{MCP_HOST}:{MCP_PORT}")
    logger.info(f"SSE endpoint: http://{MCP_HOST}:{MCP_PORT}/sse")
    yield
    logger.info("Shutting down PyATS MCP Server")


# Create FastAPI application for SSE transport
app = FastAPI(
    title="PyATS MCP Server (SSE)",
    description="MCP server for executing show commands on Cisco network devices via SSE transport",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "name": "PyATS MCP Server",
        "transport": "SSE (Server-Sent Events)",
        "version": "1.0.0",
        "endpoints": {
            "sse": "/sse",
            "health": "/health"
        },
        "documentation": "Connect MCP clients to /sse endpoint"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "transport": "sse"}


@app.get("/sse")
async def handle_sse(request):
    """SSE endpoint for MCP protocol.
    
    This endpoint handles MCP communication via Server-Sent Events.
    MCP clients connect to this endpoint to interact with the server.
    """
    logger.info(f"New SSE connection from {request.client.host}")
    
    async def event_generator():
        """Generate SSE events for MCP protocol."""
        try:
            # Create SSE transport
            transport = SseServerTransport("/messages")
            
            # Run the MCP server with this transport
            async with transport.connect_sse(
                request.scope,
                request.receive,
                request._send
            ) as streams:
                await server.run(
                    streams[0],
                    streams[1],
                    server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"SSE connection error: {e}", exc_info=True)
            yield {
                "event": "error",
                "data": str(e)
            }
    
    return EventSourceResponse(event_generator())


@app.post("/messages")
async def handle_messages(request):
    """Handle MCP messages (used internally by SSE transport)."""
    # This endpoint is used by the SSE transport for bidirectional communication
    # The actual handling is done by the transport layer
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=MCP_HOST,
        port=MCP_PORT,
        log_level="info"
    )

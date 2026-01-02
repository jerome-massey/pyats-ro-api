"""FastAPI application for network device show commands."""

import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List

from app.models import (
    ShowCommandRequest,
    ShowCommandResponse,
    DeviceResult,
    CommandResult,
    OutputFormat
)
from app.device_manager import DeviceManager
from app.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info("Starting PyATS API application")
    yield
    logger.info("Shutting down PyATS API application")


# Create FastAPI application
app = FastAPI(
    title="PyATS Show Command API",
    description="Execute show commands on network devices via PyATS/Unicon",
    version="0.3.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "PyATS Show Command API",
        "version": "0.3.0",
        "description": "Execute show commands on network devices",
        "endpoints": {
            "health": "/health",
            "execute": "/api/v1/execute (POST)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/v1/execute", response_model=ShowCommandResponse)
async def execute_commands(request: ShowCommandRequest):
    """Execute show commands on one or more network devices.
    
    Args:
        request: ShowCommandRequest containing devices and commands
        
    Returns:
        ShowCommandResponse with results from all devices
    """
    logger.info(f"Received request to execute commands on {len(request.devices)} device(s)")
    
    # Validate that only show commands are being executed
    for cmd in request.commands:
        full_command = cmd.get_full_command()
        logger.info(f"Validated command: {full_command}")
    
    results: List[DeviceResult] = []
    
    # Process each device
    for device_creds in request.devices:
        device_result = await process_device(
            device_creds,
            request.commands,
            request.timeout,
            request.output_format
        )
        results.append(device_result)
    
    # Calculate summary statistics
    successful_devices = sum(1 for r in results if r.success)
    failed_devices = len(results) - successful_devices
    
    return ShowCommandResponse(
        results=results,
        total_devices=len(results),
        successful_devices=successful_devices,
        failed_devices=failed_devices
    )


async def process_device(device_creds, commands, timeout, output_format: OutputFormat) -> DeviceResult:
    """Process commands for a single device.
    
    Args:
        device_creds: Device credentials
        commands: List of commands to execute
        timeout: Command timeout in seconds
        
    Returns:
        DeviceResult with command outputs
    """
    device_manager = None
    command_results: List[CommandResult] = []
    
    try:
        # Create device manager
        device_manager = DeviceManager(device_creds=device_creds, timeout=timeout)
        
        # Connect to device
        device_manager.connect()
        
        # Execute each command
        parse_requested = output_format in (OutputFormat.PARSED, OutputFormat.BOTH)
        for cmd in commands:
            try:
                raw_output, parsed_output, parse_error = device_manager.execute_command(
                    cmd,
                    parse=parse_requested
                )
                command_results.append(CommandResult(
                    command=cmd.get_full_command(),
                    output=raw_output,
                    parsed=parsed_output,
                    parse_error=parse_error,
                    success=True
                ))
            except Exception as e:
                logger.error(f"Command failed on {device_creds.hostname}: {e}")
                command_results.append(CommandResult(
                    command=cmd.get_full_command(),
                    output="",
                    parsed=None,
                    parse_error=None,
                    success=False,
                    error=str(e)
                ))
        
        return DeviceResult(
            hostname=device_creds.hostname,
            success=True,
            commands=command_results
        )
    
    except Exception as e:
        logger.error(f"Failed to process device {device_creds.hostname}: {e}")
        return DeviceResult(
            hostname=device_creds.hostname,
            success=False,
            commands=command_results,
            error=str(e)
        )
    
    finally:
        # Disconnect from device
        if device_manager:
            try:
                device_manager.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting from {device_creds.hostname}: {e}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

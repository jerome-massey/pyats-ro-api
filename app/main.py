"""FastAPI application for network device show commands."""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List

from app.models import (
    ShowCommandRequest,
    ShowCommandResponse,
    DeviceResult,
    CommandResult
)
from app.device_manager import DeviceManager
from app.jumphost import JumphostManager
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
    description="Execute show commands on network devices via PyATS/Unicon with optional SSH jumphost support",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "PyATS Show Command API",
        "version": "1.0.0",
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
        
    Raises:
        HTTPException: If validation or execution fails
    """
    logger.info(f"Received request to execute commands on {len(request.devices)} device(s)")
    
    # Validate that only show commands are being executed
    for cmd in request.commands:
        if not cmd.command.strip().lower().startswith("show"):
            raise HTTPException(
                status_code=400,
                detail=f"Only 'show' commands are allowed. Got: {cmd.command}"
            )
    
    results: List[DeviceResult] = []
    jumphost_manager = None
    
    try:
        # Initialize jumphost if requested
        if request.use_jumphost:
            if not all([
                settings.jumphost_host,
                settings.jumphost_username,
                settings.jumphost_key_path
            ]):
                raise HTTPException(
                    status_code=400,
                    detail="Jumphost requested but configuration is incomplete. "
                           "Check JUMPHOST_HOST, JUMPHOST_USERNAME, and JUMPHOST_KEY_PATH."
                )
            
            logger.info("Initializing jumphost connection")
            jumphost_manager = JumphostManager(
                jumphost_host=settings.jumphost_host,
                jumphost_port=settings.jumphost_port,
                jumphost_username=settings.jumphost_username,
                jumphost_key_path=settings.jumphost_key_path
            )
            jumphost_manager.connect()
        
        # Process each device
        for device_creds in request.devices:
            device_result = await process_device(
                device_creds,
                request.commands,
                jumphost_manager,
                request.timeout
            )
            results.append(device_result)
    
    finally:
        # Cleanup jumphost connection
        if jumphost_manager:
            try:
                jumphost_manager.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting jumphost: {e}")
    
    # Calculate summary statistics
    successful_devices = sum(1 for r in results if r.success)
    failed_devices = len(results) - successful_devices
    
    return ShowCommandResponse(
        results=results,
        total_devices=len(results),
        successful_devices=successful_devices,
        failed_devices=failed_devices
    )


async def process_device(device_creds, commands, jumphost_manager, timeout) -> DeviceResult:
    """Process commands for a single device.
    
    Args:
        device_creds: Device credentials
        commands: List of commands to execute
        jumphost_manager: Optional jumphost manager
        timeout: Command timeout
        
    Returns:
        DeviceResult with command outputs
    """
    device_manager = None
    command_results: List[CommandResult] = []
    
    try:
        # Create device manager
        device_manager = DeviceManager(
            device_creds=device_creds,
            jumphost_manager=jumphost_manager,
            timeout=timeout
        )
        
        # Connect to device
        device_manager.connect()
        
        # Execute each command
        for cmd in commands:
            try:
                output = device_manager.execute_command(cmd)
                command_results.append(CommandResult(
                    command=cmd.get_full_command(),
                    output=output,
                    success=True
                ))
            except Exception as e:
                logger.error(f"Command failed on {device_creds.hostname}: {e}")
                command_results.append(CommandResult(
                    command=cmd.get_full_command(),
                    output="",
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

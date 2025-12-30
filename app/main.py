"""FastAPI application for network device show commands."""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List, Dict

from app.models import (
    ShowCommandRequest,
    ShowCommandResponse,
    DeviceResult,
    CommandResult,
    JumphostTestRequest,
    JumphostTestResult
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
            "execute": "/api/v1/execute (POST)",
            "test-jumphost": "/api/v1/jumphost/test (POST)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/v1/jumphost/test", response_model=JumphostTestResult)
async def test_jumphost(request: JumphostTestRequest):
    """Test SSH jumphost connectivity.
    
    Validates that a jumphost configuration is correct and accessible
    without connecting to target devices.
    
    Args:
        request: JumphostTestRequest containing jumphost configuration
        
    Returns:
        JumphostTestResult with connection test results
    """
    jumphost_config = request.jumphost
    logger.info(f"Testing jumphost connection to {jumphost_config.host}:{jumphost_config.port}")
    
    jumphost_manager = None
    
    try:
        # Create jumphost manager with provided config
        jumphost_manager = JumphostManager(
            jumphost_host=jumphost_config.host,
            jumphost_port=jumphost_config.port,
            jumphost_username=jumphost_config.username,
            jumphost_key_path=jumphost_config.key_path
        )
        
        # Attempt connection
        jumphost_manager.connect()
        
        logger.info(f"Successfully connected to jumphost {jumphost_config.host}")
        
        return JumphostTestResult(
            host=jumphost_config.host,
            port=jumphost_config.port,
            username=jumphost_config.username,
            success=True,
            message=f"Successfully connected to jumphost {jumphost_config.host}:{jumphost_config.port} as user '{jumphost_config.username}'"
        )
    
    except FileNotFoundError as e:
        error_msg = f"SSH key not found: {jumphost_config.key_path}"
        logger.error(error_msg)
        return JumphostTestResult(
            host=jumphost_config.host,
            port=jumphost_config.port,
            username=jumphost_config.username,
            success=False,
            message="Jumphost connection failed: SSH key not found",
            error=error_msg
        )
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Jumphost connection test failed: {error_msg}")
        
        return JumphostTestResult(
            host=jumphost_config.host,
            port=jumphost_config.port,
            username=jumphost_config.username,
            success=False,
            message="Jumphost connection failed",
            error=error_msg
        )
    
    finally:
        # Cleanup connection
        if jumphost_manager:
            try:
                jumphost_manager.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting from jumphost during cleanup: {e}")


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
    # Note: Pydantic validation already occurs via field_validator in ShowCommand
    for cmd in request.commands:
        full_command = cmd.get_full_command()
        logger.info(f"Validated command: {full_command}")
    
    results: List[DeviceResult] = []
    global_jumphost_manager = None
    device_jumphost_managers: Dict[str, JumphostManager] = {}
    
    try:
        # Initialize global jumphost if requested (fallback for devices without per-device config)
        if request.use_jumphost:
            if not all([
                settings.jumphost_host,
                settings.jumphost_username,
                settings.jumphost_key_path
            ]):
                raise HTTPException(
                    status_code=400,
                    detail="Jumphost requested but global configuration is incomplete. "
                           "Set JUMPHOST_HOST, JUMPHOST_USERNAME, and JUMPHOST_KEY_PATH environment variables, "
                           "or provide per-device jumphost configuration."
                )
            
            logger.info("Initializing global jumphost connection")
            global_jumphost_manager = JumphostManager(
                jumphost_host=settings.jumphost_host,
                jumphost_port=settings.jumphost_port,
                jumphost_username=settings.jumphost_username,
                jumphost_key_path=settings.jumphost_key_path
            )
            global_jumphost_manager.connect()
        
        # Process each device
        for device_creds in request.devices:
            # Determine which jumphost to use for this device
            jumphost_manager = None
            
            # Priority 1: Per-device jumphost config
            if device_creds.jumphost:
                logger.info(f"Using per-device jumphost config for {device_creds.hostname}")
                device_key = f"{device_creds.jumphost.host}:{device_creds.jumphost.port}:{device_creds.jumphost.username}"
                
                # Create device-specific jumphost if not already created
                if device_key not in device_jumphost_managers:
                    device_jumphost_managers[device_key] = JumphostManager(
                        jumphost_host=device_creds.jumphost.host,
                        jumphost_port=device_creds.jumphost.port,
                        jumphost_username=device_creds.jumphost.username,
                        jumphost_key_path=device_creds.jumphost.key_path
                    )
                    device_jumphost_managers[device_key].connect()
                
                jumphost_manager = device_jumphost_managers[device_key]
            
            # Priority 2: Global jumphost config
            elif request.use_jumphost:
                logger.info(f"Using global jumphost for {device_creds.hostname}")
                jumphost_manager = global_jumphost_manager
            
            # Process device
            device_result = await process_device(
                device_creds,
                request.commands,
                jumphost_manager,
                request.timeout
            )
            results.append(device_result)
    
    finally:
        # Cleanup all jumphost connections
        if global_jumphost_manager:
            try:
                global_jumphost_manager.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting global jumphost: {e}")
        
        for device_key, jumphost_manager in device_jumphost_managers.items():
            try:
                jumphost_manager.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting device jumphost ({device_key}): {e}")
    
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

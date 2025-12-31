"""MCP Server implementation for PyATS Show Commands.

This module provides MCP (Model Context Protocol) tools that expose
the PyATS show command functionality to AI assistants and other MCP clients.

The server uses existing business logic from app/ without modification.
"""

import logging
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import ValidationError

# Import existing business logic (no modifications needed)
from app.models import (
    DeviceCredentials,
    ShowCommand,
    DeviceOS,
    PipeOption
)
from app.device_manager import DeviceManager
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server("pyats-show-commands")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="execute_show_commands",
            description=(
                "Execute show commands on Cisco network devices (IOS, IOS-XE, IOS-XR, NX-OS, ASA). "
                "Supports optional SSH jumphost and pipe filters (include, exclude, begin, section). "
                "Only read-only 'show' commands are allowed for security."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "hostname": {
                        "type": "string",
                        "description": "Device hostname or IP address"
                    },
                    "username": {
                        "type": "string",
                        "description": "Device SSH username"
                    },
                    "password": {
                        "type": "string",
                        "description": "Device SSH password"
                    },
                    "os": {
                        "type": "string",
                        "enum": ["ios", "iosxe", "iosxr", "nxos", "asa"],
                        "description": "Device operating system"
                    },
                    "commands": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of show commands to execute (must start with 'show')"
                    },
                    "port": {
                        "type": "integer",
                        "description": "SSH port (default: 22)",
                        "default": 22
                    },
                    "enable_password": {
                        "type": "string",
                        "description": "Enable password if required (optional)"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Command timeout in seconds (default: 30)",
                        "default": 30
                    }
                },
                "required": ["hostname", "username", "password", "os", "commands"]
            }
        ),
        Tool(
            name="list_supported_os",
            description="List all supported network device operating systems",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_pipe_options",
            description="List all available pipe filter options for show commands",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle MCP tool calls."""
    
    if name == "execute_show_commands":
        return await execute_show_commands_tool(arguments)
    elif name == "list_supported_os":
        return await list_supported_os_tool()
    elif name == "list_pipe_options":
        return await list_pipe_options_tool()
    else:
        raise ValueError(f"Unknown tool: {name}")


async def execute_show_commands_tool(arguments: dict) -> list[TextContent]:
    """Execute show commands on a network device.
    
    Uses existing DeviceManager and JumphostManager business logic.
    """
    try:
        # Validate and create device credentials using existing model
        device_creds = DeviceCredentials(
            hostname=arguments["hostname"],
            username=arguments["username"],
            password=arguments["password"],
            os=arguments["os"],
            port=arguments.get("port", 22),
            enable_password=arguments.get("enable_password")
        )
        
        # Parse commands
        commands = arguments["commands"]
        timeout = arguments.get("timeout", 30)
        
        # Validate all commands
        show_commands = []
        for cmd_str in commands:
            try:
                show_cmd = ShowCommand(command=cmd_str)
                show_commands.append(show_cmd)
            except ValidationError as e:
                return [TextContent(
                    type="text",
                    text=f"Command validation failed for '{cmd_str}': {e.errors()[0]['msg']}"
                )]
        
        # Execute commands using existing DeviceManager
        device_manager = None
        results = []
        
        try:
            device_manager = DeviceManager(
                device_creds=device_creds,
                timeout=timeout
            )
            
            device_manager.connect()
            
            for show_cmd in show_commands:
                try:
                    output = device_manager.execute_command(show_cmd)
                    results.append({
                        "command": show_cmd.get_full_command(),
                        "success": True,
                        "output": output
                    })
                except Exception as e:
                    results.append({
                        "command": show_cmd.get_full_command(),
                        "success": False,
                        "error": str(e)
                    })
            
            # Format results
            result_text = f"Device: {device_creds.hostname} ({device_creds.os})\n"
            result_text += f"Commands executed: {len(results)}\n\n"
            
            for i, result in enumerate(results, 1):
                result_text += f"--- Command {i}: {result['command']} ---\n"
                if result['success']:
                    result_text += f"{result['output']}\n"
                else:
                    result_text += f"ERROR: {result['error']}\n"
                result_text += "\n"
            
            return [TextContent(type="text", text=result_text)]
            
        finally:
            if device_manager:
                device_manager.disconnect()
    
    except ValidationError as e:
        error_msg = f"Validation error: {e.errors()[0]['msg']}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]
    
    except Exception as e:
        error_msg = f"Error executing commands: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [TextContent(type="text", text=error_msg)]


async def list_supported_os_tool() -> list[TextContent]:
    """List supported device operating systems."""
    os_list = "\n".join([
        "Supported Cisco Network Device Operating Systems:",
        "",
        "- ios       : Cisco IOS",
        "- iosxe     : Cisco IOS-XE",
        "- iosxr     : Cisco IOS-XR",
        "- nxos      : Cisco NX-OS",
        "- asa       : Cisco ASA",
        "",
        "Note: JunOS is not supported due to incompatible command syntax."
    ])
    return [TextContent(type="text", text=os_list)]


async def list_pipe_options_tool() -> list[TextContent]:
    """List available pipe filter options."""
    pipe_list = "\n".join([
        "Available Pipe Filter Options:",
        "",
        "- include  : Show only lines containing the pattern",
        "- exclude  : Show lines NOT containing the pattern",
        "- begin    : Show output starting from the pattern",
        "- section  : Show the section containing the pattern",
        "",
        "Example usage:",
        "  Command: show running-config",
        "  Pipe: include",
        "  Value: interface",
        "  Result: show running-config | include interface"
    ])
    return [TextContent(type="text", text=pipe_list)]

# PyATS MCP Server

MCP (Model Context Protocol) server implementation for executing show commands on Cisco network devices. This allows AI assistants like Claude to directly interact with network devices through standardized tools.

## Overview

The PyATS MCP server exposes the same functionality as the REST API but through the MCP protocol, enabling AI assistants to:
- Execute show commands on Cisco devices
- Query supported OS types and pipe options
- All with the same security restrictions (show commands only)

## Architecture

```
┌──────────────────────────────────────────────┐
│         Presentation Layer                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ REST API │  │MCP stdio │  │ MCP SSE  │  │
│  │ Port 8000│  │ on-demand│  │ Port 3000│  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼─────────────┼─────────┘
        │             │             │
        └─────────────┴─────────────┘
                      │
        ┌─────────────▼─────────────┐
        │    Business Logic         │
        │  (Shared - Unchanged)     │
        │  - DeviceManager          │

        │  - Models & Validation    │
        └───────────────────────────┘
```

## MCP Tools Available

### 1. `execute_show_commands`
Execute show commands on a Cisco network device.

**Parameters:**
- `hostname` (required): Device IP or hostname
- `username` (required): SSH username
- `password` (required): SSH password  
- `os` (required): Device OS (ios, iosxe, iosxr, nxos, asa)
- `commands` (required): Array of show commands
- `port` (optional): SSH port (default: 22)
- `enable_password` (optional): Enable password
- `timeout` (optional): Command timeout in seconds (default: 30)

**Example:**
```json
{
  "hostname": "192.168.1.1",
  "username": "admin",
  "password": "cisco123",
  "os": "iosxe",
  "commands": ["show version", "show ip interface brief"]
}
```

### 2. `list_supported_os`
List all supported network device operating systems.

No parameters required.

### 3. `list_pipe_options`
List available pipe filter options for show commands.

No parameters required.

## Transport Options

### stdio Transport (Local)

**Use Case:** Claude Desktop, local AI assistants, CLI tools

**Start Server:**
```bash
# Via Docker
docker-compose -f docker-compose.mcp.yml run --rm pyats-mcp-stdio

# Or directly
python mcp_stdio.py
```

**Claude Desktop Configuration:**

Add to `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pyats": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "/home/user/.ssh:/root/.ssh:ro",
        "pyats-unified:latest",
        "python", "mcp_stdio.py"
      ],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

Or without Docker:
```json
{
  "mcpServers": {
    "pyats": {
      "command": "python",
      "args": ["/path/to/pyats-api/mcp_stdio.py"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### SSE Transport (Remote)

**Use Case:** Web-based clients, remote MCP access, multiple clients

**Start Server:**
```bash
# Via Docker Compose
docker-compose -f docker-compose.mcp.yml up -d pyats-mcp-sse

# Or directly
python mcp_sse.py
```

**Endpoints:**
- SSE: `http://localhost:3000/sse`
- Health: `http://localhost:3000/health`
- Info: `http://localhost:3000/`

**Client Connection Example:**
```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client("http://localhost:3000/sse") as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        result = await session.call_tool(
            "execute_show_commands",
            arguments={
                "hostname": "192.168.1.1",
                "username": "admin",
                "password": "cisco123",
                "os": "iosxe",
                "commands": ["show version"]
            }
        )
        print(result)
```

## Deployment

### Quick Start - All Services

```bash
# Build the unified image
docker-compose -f docker-compose.mcp.yml build

# Start REST API and MCP SSE server
docker-compose -f docker-compose.mcp.yml up -d

# Services running:
# - REST API: http://localhost:8000
# - MCP SSE: http://localhost:3000
```

### Individual Services

```bash
# Only REST API
docker-compose -f docker-compose.mcp.yml up -d pyats-api

# Only MCP SSE
docker-compose -f docker-compose.mcp.yml up -d pyats-mcp-sse

# MCP stdio (on-demand)
docker-compose -f docker-compose.mcp.yml run --rm pyats-mcp-stdio
```

### Production Deployment

```bash
# Start REST API and MCP SSE as persistent services
docker-compose -f docker-compose.mcp.yml up -d pyats-api pyats-mcp-sse

# Check logs
docker-compose -f docker-compose.mcp.yml logs -f

# Check health
curl http://localhost:8000/health
curl http://localhost:3000/health
```

## Environment Variables

Same as REST API:

**MCP SSE Configuration:**
- `MCP_HOST`: Host to bind to (default: 0.0.0.0)
- `MCP_PORT`: Port for SSE server (default: 3000)

**API Configuration:**
- `API_HOST`: API bind address (default: 0.0.0.0)
- `API_PORT`: API port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)

## Usage Examples

### Example 1: Execute Show Commands (via Claude Desktop)

Once configured in Claude Desktop, simply ask:

```
Can you check the version on my router at 192.168.1.1?
Username: admin, Password: cisco123, OS: iosxe
```

Claude will use the `execute_show_commands` tool automatically.

### Example 2: Query Available Tools

```
What network device operating systems do you support?
```

Claude will use `list_supported_os` tool.

## Security Considerations

Same security model as REST API:

1. **Show Commands Only**: Only commands starting with "show" are allowed
2. **Input Validation**: All inputs validated via Pydantic models
3. **No Credential Storage**: Credentials passed per-request (not stored)
4. **Container Isolation**: Runs in isolated Docker containers
5. **SSH Config Jumphost**: Jumphost routing via SSH config (transparent)

**Additional MCP Security:**
- stdio transport: Local only, no network exposure
- SSE transport: Can be put behind authentication proxy
- Tool permissions: MCP clients can restrict which tools are callable

## Troubleshooting

### stdio Transport Issues

**Problem:** Claude Desktop can't connect

**Solutions:**
1. Check Claude Desktop logs: `~/Library/Logs/Claude/`
2. Verify Docker image exists: `docker images | grep pyats`
3. Test manually: `docker run -i pyats-unified:latest python mcp_stdio.py`
4. Check file paths in configuration

### SSE Transport Issues

**Problem:** Can't connect to SSE endpoint

**Solutions:**
1. Verify server is running: `docker ps | grep mcp-sse`
2. Check logs: `docker logs pyats-mcp-sse`
3. Test endpoint: `curl http://localhost:3000/health`
4. Check firewall rules for port 3000

### Tool Execution Issues

**Problem:** Commands fail or timeout

**Solutions:**
1. Same as REST API troubleshooting
2. Check device connectivity
3. Verify credentials
4. Increase timeout value
5. Check logs for detailed error messages

## Comparison: MCP vs REST API

| Feature | REST API | MCP stdio | MCP SSE |
|---------|----------|-----------|---------|
| **Access** | HTTP/curl | Local only | HTTP |
| **Use Case** | Scripts/automation | AI assistants | Remote AI/Web |
| **Auth** | Manual | Config file | Can add proxy |
| **Discovery** | OpenAPI docs | Auto-discovery | Auto-discovery |
| **Client** | Any HTTP client | MCP-compatible | MCP-compatible |
| **Port** | 8000 | None (stdio) | 3000 |

## Files Added

MCP implementation adds these files **without modifying existing code**:

```
pyats-api/
├── mcp_server.py           # Core MCP server with tool definitions
├── mcp_stdio.py            # stdio transport implementation
├── mcp_sse.py              # SSE transport implementation
├── docker-compose.mcp.yml  # Multi-service Docker Compose config
└── MCP_README.md           # This file
```

**Modified files (minimal changes):**
- `requirements.txt` - Added MCP dependencies
- `Dockerfile` - Added COPY commands for MCP files, exposed port 3000
- `Dockerfile.dev` - Same as Dockerfile

**Unchanged files:**
- `app/main.py` - REST API unchanged
- `app/device_manager.py` - Business logic unchanged
- `app/models.py` - Validation unchanged
- All other app/ files - Unchanged

## Development

### Local Development (Without Docker)

```bash
# Install MCP dependencies
pip install -r requirements.txt

# Run stdio server
python mcp_stdio.py

# Run SSE server (in another terminal)
python mcp_sse.py
```

### Testing MCP Tools

```bash
# Test with MCP Inspector (if available)
npx @modelcontextprotocol/inspector python mcp_stdio.py

# Or build and test with Docker
docker-compose -f docker-compose.mcp.yml build
docker-compose -f docker-compose.mcp.yml run --rm pyats-mcp-stdio
```

## Support

For issues:
1. Check existing REST API documentation
2. Review MCP protocol documentation: https://modelcontextprotocol.io
3. Check Docker logs
4. Verify environment configuration

## License

Same as main project (MIT License)

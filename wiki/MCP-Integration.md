# MCP Integration

Model Context Protocol (MCP) server implementation for PyATS Show Commands. This enables AI assistants like Claude to directly interact with network devices.

## Overview

The PyATS MCP server exposes the same functionality as the REST API but through the MCP protocol, enabling AI assistants to:
- Execute show commands on Cisco devices
- Test jumphost connectivity
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
        │  - JumphostManager        │
        │  - Models & Validation    │
        └───────────────────────────┘
```

---

## MCP Transport Options

### stdio Transport (Local)

**Use Case**: Claude Desktop, local AI assistants, CLI tools

**Pros**:
- No network exposure
- Simple configuration
- Secure (local only)

**Cons**:
- Single user
- Local access only

### SSE Transport (Remote)

**Use Case**: Web-based clients, remote MCP access, multiple clients

**Pros**:
- Remote access
- Multiple concurrent clients
- Network-accessible

**Cons**:
- Requires network configuration
- Should be secured with authentication

---

## Available MCP Tools

### 1. `execute_show_commands`

Execute show commands on a Cisco network device.

**Parameters**:
```json
{
  "hostname": "192.168.1.1",
  "username": "admin",
  "password": "cisco123",
  "os": "iosxe",
  "commands": ["show version", "show ip interface brief"],
  "port": 22,
  "enable_password": null,
  "timeout": 30,
  "output_format": "raw"
}
```

**Fields**:
- `hostname` (required): Device IP or hostname
- `username` (required): SSH username
- `password` (required): SSH password
- `os` (required): Device OS (ios, iosxe, iosxr, nxos, asa)
- `commands` (required): Array of show commands
- `port` (optional): SSH port (default: 22)
- `enable_password` (optional): Enable password
- `timeout` (optional): Command timeout in seconds (default: 30)
- `output_format` (optional): Output format: raw, parsed, or both (default: raw)

> **Note**: Jumphost configuration is handled via SSH config files, not API/MCP parameters. See [SSH Configuration](SSH-Configuration) for setup.

### 2. `list_supported_os`

List all supported network device operating systems.

No parameters required.

### 3. `list_pipe_options`

List available pipe filter options for show commands.

No parameters required.

---

## Setup: stdio Transport (Claude Desktop)

### Step 1: Build or Pull Docker Image

**Option A: Pull from Docker Hub**
```bash
docker pull jeromemassey76/pyats-ro-api:latest
```

**Option B: Build Locally**
```bash
git clone https://github.com/jerome-massey/pyats-ro-api.git
cd pyats-ro-api
docker build -t pyats-unified:latest .
```

### Step 2: Configure Claude Desktop

Edit Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

**With Docker**:
```json
{
  "mcpServers": {
    "pyats": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v",
        "/home/user/.ssh:/root/.ssh:ro",
        "jeromemassey76/pyats-ro-api:latest",
        "python",
        "mcp_stdio.py"
      ],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Without Docker** (if running locally):
```json
{
  "mcpServers": {
    "pyats": {
      "command": "python",
      "args": ["/path/to/pyats-api/mcp_stdio.py"],
      "env": {
        "LOG_LEVEL": "INFO",
        "JUMPHOST_HOST": "jumphost.example.com",
        "JUMPHOST_USERNAME": "jumpuser",
        "JUMPHOST_KEY_PATH": "/home/user/.ssh/id_rsa"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop to load the new configuration.

### Step 4: Verify Connection

In Claude Desktop, ask:
```
Can you check what PyATS tools are available?
```

Claude should respond with information about the available MCP tools.

### Step 5: Test Command Execution

Ask Claude:
```
Can you run "show version" on my router at 192.168.1.1?
Username is "admin" and password is "cisco123", OS type is "iosxe"
```

---

## Setup: SSE Transport (Remote Access)

### Step 1: Start MCP SSE Server

**Using Docker Compose**:
```bash
# Pull production compose file
curl -O https://raw.githubusercontent.com/jerome-massey/pyats-ro-api/main/docker-compose.mcp.prod.yml

# Start services
docker-compose -f docker-compose.mcp.prod.yml up -d

# Verify MCP SSE is running
curl http://localhost:3000/health
```

**Using Docker Run**:
```bash
docker run -d \
  --name pyats-mcp-sse \
  -p 3000:3000 \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=3000 \
  jeromemassey76/pyats-ro-api:latest \
  python mcp_sse.py
```

### Step 2: Test Endpoint

```bash
# Check health
curl http://localhost:3000/health

# Check info
curl http://localhost:3000/
```

### Step 3: Connect MCP Client

Example Python client:

```python
from mcp import ClientSession
from mcp.client.sse import sse_client
import asyncio

async def test_mcp_sse():
    async with sse_client("http://localhost:3000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize session
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])
            
            # Execute show command
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
            print("Command result:", result)

# Run the async function
asyncio.run(test_mcp_sse())
```

---

## Usage Examples

### Example 1: Check Device Version

**Ask Claude**:
```
Can you check the software version on my router at 192.168.1.1?
- Username: admin
- Password: cisco123
- OS: iosxe
```

**Claude will**:
1. Use the `execute_show_commands` tool
2. Connect to the device
3. Execute "show version"
4. Parse and summarize the results

### Example 2: Multiple Commands

**Ask Claude**:
```
Run these commands on 192.168.1.1 (admin/cisco123, iosxe):
1. show version
2. show ip interface brief
3. show running-config | section interface
```

### Example 3: Test Jumphost

**Ask Claude**:
```
Test connectivity to my jumphost:
- Host: jumphost.example.com
- Username: netadmin
- Key: /root/.ssh/id_rsa
```

### Example 4: Query Capabilities

**Ask Claude**:
```
What network device operating systems do you support?
```

Claude will use the `list_supported_os` tool.

---

## Environment Variables

### MCP SSE Configuration

- `MCP_HOST` - Host to bind to (default: 0.0.0.0)
- `MCP_PORT` - Port for SSE server (default: 3000)
- `LOG_LEVEL` - Logging level (INFO, DEBUG, WARNING, ERROR)

### Jumphost Configuration (Optional)

- `JUMPHOST_HOST` - Jumphost hostname
- `JUMPHOST_PORT` - Jumphost SSH port (default: 22)
- `JUMPHOST_USERNAME` - Jumphost username
- `JUMPHOST_KEY_PATH` - Path to SSH private key

Example `.env` file:
```bash
# MCP Configuration
MCP_HOST=0.0.0.0
MCP_PORT=3000
LOG_LEVEL=INFO

# Jumphost Configuration
JUMPHOST_HOST=jumphost.example.com
JUMPHOST_PORT=22
JUMPHOST_USERNAME=jumpuser
JUMPHOST_KEY_PATH=/root/.ssh/jumphost_key
```

---

## Security Considerations

### Same Security Model as REST API

1. **Show Commands Only**: Only commands starting with "show" are allowed
2. **Input Validation**: All inputs validated via Pydantic models
3. **No Credential Storage**: Credentials passed per-request (not stored)
4. **SSH Key Auth**: Jumphost uses SSH key authentication
5. **Container Isolation**: Runs in isolated Docker containers

### Additional MCP Security

- **stdio transport**: Local only, no network exposure
- **SSE transport**: Can be put behind authentication proxy (Nginx, Traefik)
- **Tool permissions**: MCP clients can restrict which tools are callable

### Production Recommendations

1. **Use HTTPS** for SSE transport
2. **Implement authentication** (OAuth2, API keys)
3. **Network restrictions** (firewall, VPN)
4. **Audit logging** of all commands
5. **Rate limiting** to prevent abuse

---

## Troubleshooting

### stdio Transport Issues

**Problem**: Claude Desktop can't connect

**Solutions**:
1. Check Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\Logs\`
   - Linux: `~/.config/Claude/logs/`

2. Verify Docker image exists:
   ```bash
   docker images | grep pyats
   ```

3. Test manually:
   ```bash
   docker run -i jeromemassey76/pyats-ro-api:latest python mcp_stdio.py
   ```

4. Check file paths in configuration

**Problem**: SSH keys not accessible

**Solution**: Mount SSH directory correctly:
```json
{
  "args": [
    "run", "-i", "--rm",
    "-v", "/home/user/.ssh:/root/.ssh:ro",
    ...
  ]
}
```

### SSE Transport Issues

**Problem**: Can't connect to SSE endpoint

**Solutions**:
1. Verify server is running:
   ```bash
   docker ps | grep mcp-sse
   ```

2. Check logs:
   ```bash
   docker logs pyats-mcp-sse
   ```

3. Test endpoint:
   ```bash
   curl http://localhost:3000/health
   ```

4. Check firewall rules for port 3000

**Problem**: CORS errors

**Solution**: Configure CORS in `mcp_sse.py` or use a reverse proxy

### Tool Execution Issues

**Problem**: Commands fail or timeout

**Solutions**:
1. Verify device connectivity
2. Check credentials are correct
3. Increase timeout value
4. Check logs for detailed error messages:
   ```bash
   docker logs pyats-mcp-sse -f
   ```

---

## Comparison: MCP vs REST API

| Feature | REST API | MCP stdio | MCP SSE |
|---------|----------|-----------|---------|
| **Access** | HTTP/curl | Local only | HTTP |
| **Use Case** | Scripts/automation | AI assistants | Remote AI/Web |
| **Auth** | Manual | Config file | Can add proxy |
| **Discovery** | OpenAPI docs | Auto-discovery | Auto-discovery |
| **Client** | Any HTTP client | MCP-compatible | MCP-compatible |
| **Port** | 8000 | None (stdio) | 3000 |
| **Multi-user** | Yes | No | Yes |

---

## Advanced Configuration

### Custom Commands with Claude

You can create custom shortcuts in Claude. For example:

```
Create a shortcut called "check-router" that runs these commands on 192.168.1.1:
- show version
- show ip interface brief
- show ip route summary
```

Claude will remember this and you can later say:
```
Run check-router
```

### Batch Operations

```
Check the version on these devices:
1. 192.168.1.1 (admin/pass1, iosxe)
2. 192.168.1.2 (admin/pass2, nxos)
3. 192.168.1.3 (admin/pass3, iosxr)
```

Claude will execute commands on all devices and summarize results.

---

## Next Steps

- **[Examples](Examples)** - More usage examples
- **[API Reference](API-Reference)** - REST API documentation
- **[Configuration](Configuration)** - Environment setup
- **[Troubleshooting](Troubleshooting)** - Common issues

---

**Navigation**: [← API Reference](API-Reference) | [Home](Home) | [Examples →](Examples)

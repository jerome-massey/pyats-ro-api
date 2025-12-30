# PyATS Show Command API

A FastAPI-based REST API and MCP (Model Context Protocol) server for executing show commands on Cisco network devices using PyATS/Unicon with optional SSH jumphost support.

## Features

### Core Functionality
- ✅ Execute show commands on Cisco network devices via PyATS/Unicon
- ✅ Support for multiple devices in a single API call
- ✅ No testbed file required - pass device credentials directly
- ✅ Pipe options support: `include`, `exclude`, `begin`, `section`
- ✅ Optional SSH jumphost support with key-based authentication
- ✅ Password authentication to target devices
- ✅ Support for Cisco network OS types (IOS, IOS-XE, IOS-XR, NX-OS, ASA)
- ✅ Show commands only (security restriction - read-only access)

### Access Methods
- ✅ **REST API** - HTTP/JSON interface on port 8000
- ✅ **MCP SSE** - Remote Model Context Protocol via Server-Sent Events on port 3000
- ✅ **MCP stdio** - Local MCP for AI assistants (Claude Desktop integration)

### Security Features
- ✅ Command validation - only `show` commands allowed
- ✅ Input sanitization - blocks 12+ dangerous patterns (`;`, `|`, `&&`, etc.)
- ✅ OS-specific validation - JunOS explicitly rejected with helpful error
- ✅ SSH key-based jumphost authentication
- ✅ No credential storage - ephemeral per-request
- ✅ Container isolation via Docker

## Installation

### Option 1: Docker (Recommended)

**Quick Start - REST API Only:**
```bash
# Development with hot-reload
make dev

# Or using docker-compose directly
docker-compose -f docker-compose.dev.yml up
```

**Quick Start - All Services (REST API + MCP):**
```bash
# Build and run all services
docker-compose -f docker-compose.mcp.yml up -d

# Services available:
# - REST API: http://localhost:8000
# - MCP SSE: http://localhost:3000
```

**Production:**
```bash
# REST API only
docker-compose up -d

# Or REST API + MCP servers
docker-compose -f docker-compose.mcp.yml up -d
```

**Endpoints:**
- REST API: http://localhost:8000
- REST API Docs (Swagger UI): http://localhost:8000/docs
- REST API Docs (ReDoc): http://localhost:8000/redoc
- MCP SSE Server: http://localhost:3000 (if using docker-compose.mcp.yml)

**Docker Configuration:**

For jumphost support, edit `docker-compose.yml` or `docker-compose.mcp.yml`:

```yaml
environment:
  - JUMPHOST_HOST=jumphost.example.com
  - JUMPHOST_PORT=22
  - JUMPHOST_USERNAME=jumpuser
  - JUMPHOST_KEY_PATH=/root/.ssh/jumphost_key

volumes:
  - ~/.ssh/id_rsa:/root/.ssh/jumphost_key:ro
```

### Option 2: Local Python Environment (Optional)

If you prefer to run without Docker:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional for jumphost)
cp .env.example .env
# Edit .env with your jumphost settings

# Run the server
python run.py
```

## Configuration

### Environment Variables

Create a `.env` file for jumphost configuration (optional):

```bash
# SSH Jumphost Configuration (Optional)
JUMPHOST_HOST=jumphost.example.com
JUMPHOST_PORT=22
JUMPHOST_USERNAME=jumpuser
JUMPHOST_KEY_PATH=/path/to/private/key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1

# Logging
LOG_LEVEL=INFO
```

### SSH Key Setup

If using jumphost, ensure your SSH private key is accessible:

```bash
# Example: Use existing SSH key
JUMPHOST_KEY_PATH=~/.ssh/id_rsa

# Or generate a new key
ssh-keygen -t rsa -b 4096 -f ~/.ssh/jumphost_key
# Copy public key to jumphost
ssh-copy-id -i ~/.ssh/jumphost_key.pub user@jumphost.example.com
```

## Usage

### Start the API Server

**With Docker:**
```bash
# Development (with hot-reload)
make dev

# Production
make run

# View logs
make logs

# Stop container
make stop
```

**Without Docker:**
```bash
# Using the run script
python run.py

# Or directly with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Development mode with hot-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```
### Test Jumphost Configuration
Test SSH jumphost connectivity before executing commands:

```bash
curl -X POST http://localhost:8000/api/v1/jumphost/test \
  -H "Content-Type: application/json" \
  -d '{
    "jumphost": {
      "host": "jumphost.example.com",
      "port": 22,
      "username": "jumpuser",
      "key_path": "/root/.ssh/jumphost_key"
    }
  }'
```

**Response (Success):**
```json
{
  "host": "jumphost.example.com",
  "port": 22,
  "username": "jumpuser",
  "success": true,
  "message": "Successfully connected to jumphost jumphost.example.com:22 as user 'jumpuser'",
  "error": null
}
```

**Response (Failure):**
```json
{
  "host": "jumphost.example.com",
  "port": 22,
  "username": "jumpuser",
  "success": false,
  "message": "Jumphost connection failed: SSH key not found",
  "error": "SSH key not found: /root/.ssh/jumphost_key"
}
```

**Use Cases:**
- Verify SSH key file exists and is readable
- Test network connectivity to jumphost
- Validate jumphost credentials before bulk operations
- Debug connectivity issues
- CI/CD pipeline integration (fail fast if jumphost unavailable)
### Execute Commands

**Direct Connection (No Jumphost):**

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "hostname": "192.168.1.1",
        "port": 22,
        "username": "admin",
        "password": "cisco123",
        "os": "iosxe"
      }
    ],
    "commands": [
      {
        "command": "show version"
      },
      {
        "command": "show ip interface brief"
      }
    ],
    "use_jumphost": false,
    "timeout": 30
  }'
```

**With Jumphost:**

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "hostname": "10.10.10.1",
        "port": 22,
        "username": "admin",
        "password": "cisco123",
        "os": "iosxe"
      }
    ],
    "commands": [
      {
        "command": "show version"
      }
    ],
    "use_jumphost": true,
    "timeout": 30
  }'
```

**With Pipe Options:**

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "hostname": "192.168.1.1",
        "port": 22,
        "username": "admin",
        "password": "cisco123",
        "os": "iosxe"
      }
    ],
    "commands": [
      {
        "command": "show running-config",
        "pipe_option": "include",
        "pipe_value": "interface"
      },
      {
        "command": "show ip route",
        "pipe_option": "exclude",
        "pipe_value": "local"
      },
      {
        "command": "show version",
        "pipe_option": "begin",
        "pipe_value": "Cisco IOS"
      },
      {
        "command": "show running-config",
        "pipe_option": "section",
        "pipe_value": "router bgp"
      }
    ],
    "use_jumphost": false,
    "timeout": 30
  }'
```

**Multiple Devices:**

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "hostname": "192.168.1.1",
        "username": "admin",
        "password": "cisco123",
        "os": "iosxe"
      },
      {
        "hostname": "192.168.1.2",
        "username": "admin",
        "password": "cisco123",
        "os": "nxos"
      }
    ],
    "commands": [
      {
        "command": "show version"
      }
    ],
    "use_jumphost": false
  }'
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Request Schema

### ShowCommandRequest

```json
{
  "devices": [
    {
      "hostname": "string (IP or hostname)",
      "port": "integer (default: 22)",
      "username": "string",
      "password": "string",
      "os": "enum: ios|iosxe|iosxr|nxos|asa",
      "enable_password": "string (optional)"
    }
  ],
  "commands": [
    {
      "command": "string (must start with 'show')",
      "pipe_option": "enum: include|exclude|begin|section (optional)",
      "pipe_value": "string (required if pipe_option set)"
    }
  ],
  "use_jumphost": "boolean (default: false)",
  "timeout": "integer (default: 30)"
}
```

## Response Schema

### ShowCommandResponse

```json
{
  "results": [
    {
      "hostname": "string",
      "success": "boolean",
      "commands": [
        {
          "command": "string",
          "output": "string",
          "success": "boolean",
          "error": "string (optional)"
        }
      ],
      "error": "string (optional)"
    }
  ],
  "total_devices": "integer",
  "successful_devices": "integer",
  "failed_devices": "integer"
}
```

## Supported Operating Systems

- `ios` - Cisco IOS
- `iosxe` - Cisco IOS-XE
- `iosxr` - Cisco IOS-XR
- `nxos` - Cisco NX-OS
- `asa` - Cisco ASA

**Note:** JunOS is **not supported** due to incompatible command syntax (uses `match` instead of `include`). Attempts to use JunOS will return a validation error with explanation.

## Security Considerations

### Built-In Security
1. **Show Commands Only**: The API enforces that only commands starting with "show" can be executed
2. **Input Validation**: Blocks dangerous patterns:
   - Command separators: `;`, `&&`, `||`
   - Redirects: `>`, `<`
   - Shell expansion: `$`, `` ` ``, `!`
   - Newlines, pipes, background operators
3. **OS Validation**: Rejects unsupported OS types (e.g., JunOS) with helpful error messages
4. **Length Limits**: Commands max 1000 chars, pipe values max 500 chars
5. **SSH Key Authentication**: Jumphost uses SSH key authentication (more secure than passwords)
6. **No Credential Storage**: Credentials passed per-request, not stored
7. **Container Isolation**: Runs in isolated Docker containers
8. **Environment Protection**: `.env` files excluded from git via `.gitignore`

### What You Should Add
1. **HTTPS/TLS**: Deploy behind reverse proxy with certificates
2. **API Authentication**: Add OAuth2, JWT, or API key validation
3. **Rate Limiting**: Prevent abuse with request throttling
4. **Network Segmentation**: Restrict container network access
5. **Secret Management**: Use Vault or similar for sensitive data
6. **Audit Logging**: Log all command executions for compliance

## MCP (Model Context Protocol) Support

This API also functions as an MCP server, allowing AI assistants like Claude to directly execute network commands.

### MCP Features
- **4 Tools Available**:
  - `execute_show_commands` - Run show commands on devices
  - `test_jumphost` - Test jumphost connectivity
  - `list_supported_os` - List supported operating systems
  - `list_pipe_options` - List available pipe filters
- **Dual Transport**: stdio (local) and SSE (remote)
- **Same Security**: All validation rules apply to MCP tools

### Quick Start - MCP

**For Claude Desktop (stdio):**
Add to `~/.config/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "pyats": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "pyats-unified:latest",
        "python", "mcp_stdio.py"
      ]
    }
  }
}
```

**For Remote Access (SSE):**
```bash
# Start MCP SSE server
docker-compose -f docker-compose.mcp.yml up -d pyats-mcp-sse

# Available at: http://localhost:3000/sse
```

**Full Documentation**: See [MCP_README.md](MCP_README.md) for complete MCP setup and usage.

## Production Recommendations

1. **Use HTTPS**: Deploy behind a reverse proxy (nginx/Apache) with TLS
2. **Authentication**: Add API authentication (OAuth2, JWT, API keys)
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Logging**: Configure centralized logging
5. **Monitoring**: Add health checks and metrics
6. **Secret Management**: Use a secret manager (Vault, AWS Secrets Manager, etc.)

## Limitations

### Current Limitations
- **Cisco Only**: Supports ios, iosxe, iosxr, nxos, asa (JunOS explicitly unsupported)
- **Show Commands Only**: Cannot make configuration changes (by design)
- **No Connection Pooling**: New connection per request
- **Sequential Execution**: Commands execute one at a time per device
- **No Caching**: Same command = new execution
- **Password Auth to Devices**: SSH key auth only for jumphost
- **30s Default Timeout**: Configurable but applies to all commands
- **No Multi-Hop Jumphost**: Single jumphost only

### Validation Rules
- Commands must start with `show`
- Max command length: 1000 characters
- Max pipe value length: 500 characters
- Hostname/IP max length: 255 characters
- Username max length: 255 characters
- Password max length: 1024 characters
- Port range: 1-65535

## Troubleshooting

### Connection Issues

1. **Jumphost Connection Fails**:
   - Verify SSH key path and permissions (`chmod 600 ~/.ssh/key`)
   - Test manual SSH: `ssh -i ~/.ssh/key user@jumphost`
   - Check firewall rules

2. **Device Connection Fails**:
   - Verify device credentials
   - Check network connectivity
   - Ensure correct OS type specified
   - Review logs: `LOG_LEVEL=DEBUG`

3. **Command Timeout**:
   - Increase timeout value in request
   - Check device performance
   - Verify command is valid for device OS

### Debug Mode

Enable debug logging:

```bash
# In .env file
LOG_LEVEL=DEBUG
```

Or set environment variable:

```bash
export LOG_LEVEL=DEBUG
python run.py
```

## Development

### Docker Development Environment

The development Docker setup includes:
- Hot-reload (code changes automatically restart the server)
- Debug logging enabled
- Development tools (pytest, black, flake8, ipython)
- Volume mounts for live code editing

```bash
# Start development environment
make dev

# Access container shell
make shell-dev

# View logs
make logs-dev

# Run tests inside container
make test
```

### Local Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run with hot-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Install dev dependencies
pip install pytest pytest-asyncio httpx black flake8

# Run tests
pytest tests/

# Format code
black app/

# Lint code
flake8 app/
```

### Make Commands

```bash
make help          # Show all available commands
make build         # Build production image
make run           # Run production container
make dev           # Run development container
make dev-build     # Build development image
make stop          # Stop containers
make clean         # Remove containers and images
make logs          # View logs
make shell         # Access container shell
```

### Code Structure

```
pyats-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── config.py            # Configuration
│   ├── device_manager.py    # PyATS/Unicon device handling
│   └── jumphost.py          # SSH jumphost manager
├── examples/
│   ├── client_example.py    # Python client examples
│   └── curl_examples.sh     # cURL examples
├── Dockerfile               # Production container
├── Dockerfile.dev           # Development container
├── docker-compose.yml       # Production compose
├── docker-compose.dev.yml   # Development compose
├── Makefile                 # Make commands
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment config
├── .dockerignore           # Docker ignore rules
├── .gitignore              # Git ignore rules
├── run.py                  # Server startup script
├── quickstart.sh           # Quick setup script
└── README.md               # This file
```

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section
- Review logs with DEBUG level
- Open an issue on GitHub

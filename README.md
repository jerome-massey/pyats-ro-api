# PyATS Show Command API

A FastAPI-based REST API for executing show commands on network devices using PyATS/Unicon with optional SSH jumphost support.

## Features

- ✅ Execute show commands on network devices via PyATS/Unicon
- ✅ Support for multiple devices in a single API call
- ✅ No testbed file required - pass device credentials directly
- ✅ Pipe options support: `include`, `exclude`, `begin`, `section`
- ✅ Optional SSH jumphost support with key-based authentication
- ✅ Password authentication to target devices
- ✅ Support for multiple network OS types (IOS, IOS-XE, IOS-XR, NX-OS, ASA, JunOS)
- ✅ Show commands only (security restriction)

## Installation

### Option 1: Docker (Recommended)

**Quick Start:**
```bash
# Development with hot-reload
make dev

# Or using docker-compose directly
docker-compose -f docker-compose.dev.yml up
```

**Production:**
```bash
# Build and run
make build
make run

# Or using docker-compose directly
docker-compose up -d
```

The API will be available at:
- http://localhost:8000
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

**Docker Configuration:**

For jumphost support, edit `docker-compose.yml` or `docker-compose.dev.yml`:

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

#### Execute Commands

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
      "os": "enum: ios|iosxe|iosxr|nxos|asa|junos",
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
- `junos` - Juniper JunOS

## Security Considerations

1. **Show Commands Only**: The API enforces that only commands starting with "show" can be executed
2. **No Testbed Files**: All credentials are passed via API (consider using HTTPS in production)
3. **SSH Key Authentication**: Jumphost uses SSH key authentication (more secure than passwords)
4. **Password to Device**: Target devices use password authentication
5. **Environment Variables**: Sensitive jumphost credentials should be in `.env` (not committed to git)

## Production Recommendations

1. **Use HTTPS**: Deploy behind a reverse proxy (nginx/Apache) with TLS
2. **Authentication**: Add API authentication (OAuth2, JWT, API keys)
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Logging**: Configure centralized logging
5. **Monitoring**: Add health checks and metrics
6. **Secret Management**: Use a secret manager (Vault, AWS Secrets Manager, etc.)

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

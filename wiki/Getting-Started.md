# Getting Started

This guide will help you get up and running with the PyATS Show Command API in under 5 minutes.

## Prerequisites

### System Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Linux (Ubuntu, RHEL, CentOS, Debian) |
| **Container Runtime** | Docker 20.10+ or Podman |
| **Python** | 3.11+ (if running without Docker) |
| **CPU** | 2+ cores (recommended) |
| **Memory** | 4GB+ (recommended) |
| **Disk** | 10GB+ (for image cache) |

### Network Access

- **Inbound**: Port 8000 (REST API), Port 3000 (MCP SSE) - optional
- **Outbound**: Port 22 (SSH to devices and jumphost)

## Quick Start

### Option 1: Docker Hub (Recommended)

The fastest way to get started is using the pre-built Docker image:

```bash
# Pull and run the latest image
docker pull jeromemassey76/pyats-ro-api:latest
docker run -d -p 8000:8000 --name pyats-api jeromemassey76/pyats-ro-api:latest

# Verify it's running
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy"
}
```

> **Note**: The current version (0.3.0) does not include a version field in the health check response.

### Option 2: Docker Compose

For a complete setup with all services:

```bash
# Download the production compose file
curl -O https://raw.githubusercontent.com/jerome-massey/pyats-ro-api/main/docker-compose.prod.yml

# Start the API
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Option 3: Build Locally

For development or customization:

```bash
# Clone the repository
git clone https://github.com/jerome-massey/pyats-ro-api.git
cd pyats-ro-api

# Start development environment
make dev

# Or use docker-compose directly
docker-compose -f docker-compose.dev.yml up
```

## First API Call

Once the API is running, test it with a simple command:

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
      }
    ],
    "commands": [
      {"command": "show version"}
    ]
  }'
```

### Expected Response

```json
{
  "results": [
    {
      "hostname": "192.168.1.1",
      "success": true,
      "commands": [
        {
          "command": "show version",
          "success": true,
          "output": "Cisco IOS XE Software, Version 16.09.03...",
          "error": null
        }
      ],
      "error": null
    }
  ],
  "total_devices": 1,
  "successful_devices": 1,
  "failed_devices": 0
}
```

## Access the API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Explore all API endpoints
- Test API calls interactively
- View request/response schemas
- Download OpenAPI specification

## Next Steps

Now that you have the API running, explore these topics:

1. **[Installation Guide](Installation)** - Detailed installation options
2. **[Configuration](Configuration)** - Environment setup and jumphost config
3. **[API Reference](API-Reference)** - Complete API documentation
4. **[Examples](Examples)** - More usage examples
5. **[MCP Integration](MCP-Integration)** - Use with AI assistants

## Common First-Time Issues

### Issue: Connection Refused

**Symptom**: `curl: (7) Failed to connect to localhost port 8000`

**Solution**: 
```bash
# Check if container is running
docker ps | grep pyats-api

# If not running, check logs
docker logs pyats-api

# Restart the container
docker restart pyats-api
```

### Issue: Authentication Failed

**Symptom**: API returns device connection errors

**Solution**:
- Verify device credentials are correct
- Ensure device is reachable from the API container
- Check if device supports SSH access
- Verify the OS type is correct (ios, iosxe, iosxr, nxos, asa)

### Issue: Command Not Allowed

**Symptom**: `"error": "Only 'show' commands are allowed"`

**Solution**:
- This API only supports read-only show commands
- Ensure all commands start with "show"
- Configuration commands are blocked for security

### Issue: Port Already in Use

**Symptom**: `Error starting userland proxy: listen tcp 0.0.0.0:8000: bind: address already in use`

**Solution**:
```bash
# Find what's using port 8000
sudo netstat -tlnp | grep 8000

# Use a different port
docker run -d -p 8001:8000 --name pyats-api jeromemassey76/pyats-ro-api:latest
```

## Test Without a Real Device

For testing without network devices, use the health check and API documentation:

```bash
# Health check
curl http://localhost:8000/health

# List supported OS types
curl http://localhost:8000/api/v1/supported_os

# List pipe options
curl http://localhost:8000/api/v1/pipe_options
```

## Stopping the API

### Docker Run
```bash
docker stop pyats-api
docker rm pyats-api
```

### Docker Compose
```bash
docker-compose -f docker-compose.prod.yml down
```

### Make (Development)
```bash
make stop
```

## Upgrading

### Docker Hub Image
```bash
# Pull latest version
docker pull jeromemassey76/pyats-ro-api:latest

# Stop and remove old container
docker stop pyats-api && docker rm pyats-api

# Start with new image
docker run -d -p 8000:8000 --name pyats-api jeromemassey76/pyats-ro-api:latest
```

### Docker Compose
```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Restart with new images
docker-compose -f docker-compose.prod.yml up -d
```

## Verifying Installation

Run this verification script:

```bash
#!/bin/bash

echo "Verifying PyATS API installation..."

# Check if container is running
if docker ps | grep -q pyats-api; then
    echo "✅ Container is running"
else
    echo "❌ Container is not running"
    exit 1
fi

# Check health endpoint
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi

# Check API docs are accessible
if curl -s http://localhost:8000/docs | grep -q "FastAPI"; then
    echo "✅ API documentation accessible"
else
    echo "❌ API documentation not accessible"
    exit 1
fi

echo ""
echo "Installation verified successfully!"
echo "Access the API at: http://localhost:8000"
echo "Documentation at: http://localhost:8000/docs"
```

## What's Next?

- **Configure Jumphost**: [Jumphost Configuration](Jumphost-Configuration)
- **Production Deployment**: [Deployment Guide](Deployment)
- **Use with AI**: [MCP Integration](MCP-Integration)
- **Explore Examples**: [Examples](Examples)

---

**Navigation**: [← Home](Home) | [Installation →](Installation)

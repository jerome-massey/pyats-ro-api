# Docker Hub Deployment Guide

This document explains how to use the published Docker images from Docker Hub.

## Published Images

The PyATS API is automatically published to Docker Hub at:
- **Repository**: `jeromemassey76/pyats-ro-api`
- **Docker Hub URL**: https://hub.docker.com/r/jeromemassey76/pyats-ro-api

### Available Tags

- `latest` - Latest stable release from the main branch
- `v1.x.x` - Specific version numbers (e.g., `v1.0.0`, `v1.2.3`)
- `1.x` - Major.minor versions (e.g., `1.0`, `1.2`)
- `1` - Major version only (e.g., `1`)

## Quick Start

### REST API Only

Pull and run the API server:

```bash
# Pull the latest image
docker pull jeromemassey76/pyats-ro-api:latest

# Run REST API on port 8000
docker run -d \
  --name pyats-api \
  -p 8000:8000 \
  -e API_HOST=0.0.0.0 \
  -e API_PORT=8000 \
  jeromemassey76/pyats-ro-api:latest
```

Test it:
```bash
curl http://localhost:8000/health
```

### Using Docker Compose (Production)

For a complete production setup:

```bash
# Download the production compose file
curl -O https://raw.githubusercontent.com/jerome-massey/pyats-ro-api/main/docker-compose.prod.yml

# Start the API
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### REST API + MCP Servers

For all services (REST API, MCP SSE, and MCP stdio):

```bash
# Download the MCP production compose file
curl -O https://raw.githubusercontent.com/jerome-massey/pyats-ro-api/main/docker-compose.mcp.prod.yml

# Start all services
docker-compose -f docker-compose.mcp.prod.yml up -d

# This starts:
# - REST API on port 8000
# - MCP SSE server on port 3000
# - MCP stdio (on-demand only)
```

## Configuration

### Environment Variables

Configure the container using environment variables:

```bash
docker run -d \
  --name pyats-api \
  -p 8000:8000 \
  -e API_HOST=0.0.0.0 \
  -e API_PORT=8000 \
  -e API_WORKERS=1 \
  -e LOG_LEVEL=INFO \
  jeromemassey76/pyats-ro-api:latest
```

### Jumphost Support

To use SSH jumphost authentication:

```bash
docker run -d \
  --name pyats-api \
  -p 8000:8000 \
  -v ~/.ssh/id_rsa:/root/.ssh/jumphost_key:ro \
  -e JUMPHOST_HOST=jumphost.example.com \
  -e JUMPHOST_PORT=22 \
  -e JUMPHOST_USERNAME=jumpuser \
  -e JUMPHOST_KEY_PATH=/root/.ssh/jumphost_key \
  jeromemassey76/pyats-ro-api:latest
```

## Specific Version Tags

### Pinning to a Specific Version

For production stability, pin to a specific version:

```bash
# Use a specific version
docker pull jeromemassey76/pyats-ro-api:v1.0.0
docker run -d -p 8000:8000 jeromemassey76/pyats-ro-api:v1.0.0

# Use major.minor version (gets patch updates)
docker pull jeromemassey76/pyats-ro-api:1.0
docker run -d -p 8000:8000 jeromemassey76/pyats-ro-api:1.0

# Use major version only (gets minor and patch updates)
docker pull jeromemassey76/pyats-ro-api:1
docker run -d -p 8000:8000 jeromemassey76/pyats-ro-api:1
```

### Update docker-compose.yml to Use Specific Version

```yaml
services:
  pyats-api:
    image: jeromemassey76/pyats-ro-api:v1.0.0  # Pinned version
    # or
    image: jeromemassey76/pyats-ro-api:1.0     # Major.minor
    # or
    image: jeromemassey76/pyats-ro-api:latest  # Always latest
```

## Multi-Service Deployment

### Option 1: All Services Together

```bash
docker-compose -f docker-compose.mcp.prod.yml up -d
```

This starts:
- `pyats-api` - REST API on port 8000
- `pyats-mcp-sse` - MCP SSE server on port 3000

### Option 2: Individual Services

Start only what you need:

```bash
# Just REST API
docker-compose -f docker-compose.mcp.prod.yml up -d pyats-api

# Just MCP SSE
docker-compose -f docker-compose.mcp.prod.yml up -d pyats-mcp-sse

# Both
docker-compose -f docker-compose.mcp.prod.yml up -d pyats-api pyats-mcp-sse
```

### Option 3: MCP stdio (On-Demand)

For Claude Desktop or other stdio MCP clients:

```bash
# Run stdio server on-demand
docker-compose -f docker-compose.mcp.prod.yml run --rm pyats-mcp-stdio
```

## Updating to Latest Version

```bash
# Pull latest image
docker pull jeromemassey76/pyats-ro-api:latest

# Restart services with new image
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Or for MCP setup
docker-compose -f docker-compose.mcp.prod.yml down
docker-compose -f docker-compose.mcp.prod.yml up -d
```

## Health Checks

All services include health checks:

```bash
# Check API health
curl http://localhost:8000/health

# Check MCP SSE health
curl http://localhost:3000/health

# View health status
docker ps
```

## Logs and Monitoring

```bash
# View logs for all services
docker-compose -f docker-compose.mcp.prod.yml logs -f

# View logs for specific service
docker-compose -f docker-compose.mcp.prod.yml logs -f pyats-api
docker-compose -f docker-compose.mcp.prod.yml logs -f pyats-mcp-sse

# Or using docker directly
docker logs -f pyats-api
docker logs -f pyats-mcp-sse
```

## Development vs Production

### Development (Build Locally)
- Use `docker-compose.dev.yml` or `docker-compose.mcp.yml`
- Builds from local source
- Includes dev tools (pytest, black, flake8)
- Volume mounts for hot-reload

### Production (Published Image)
- Use `docker-compose.prod.yml` or `docker-compose.mcp.prod.yml`
- Pulls from Docker Hub
- No dev dependencies
- Optimized for deployment

## Troubleshooting

### Image Pull Issues

```bash
# Verify image exists
docker pull jeromemassey76/pyats-ro-api:latest

# List local images
docker images | grep pyats-ro-api
```

### Port Conflicts

If ports 8000 or 3000 are in use:

```bash
# Change port mapping in docker run
docker run -d -p 9000:8000 jeromemassey76/pyats-ro-api:latest

# Or edit docker-compose.prod.yml
services:
  pyats-api:
    ports:
      - "9000:8000"  # Host:Container
```

### Container Won't Start

```bash
# Check logs
docker logs pyats-api

# Check container status
docker ps -a | grep pyats

# Remove and recreate
docker rm -f pyats-api
docker run -d -p 8000:8000 jeromemassey76/pyats-ro-api:latest
```

## CI/CD Integration

The Docker image is automatically built and published when:
- A new GitHub release is published
- Manually triggered via GitHub Actions

See [.github/workflows/docker-publish.yml](.github/workflows/docker-publish.yml) for details.

## Security Best Practices

1. **Pin Versions in Production**:
   ```yaml
   image: jeromemassey76/pyats-ro-api:v1.0.0  # Not 'latest'
   ```

2. **Read-Only SSH Keys**:
   ```yaml
   volumes:
     - ~/.ssh/id_rsa:/root/.ssh/jumphost_key:ro  # Note ':ro'
   ```

3. **Network Isolation**:
   ```yaml
   networks:
     pyats-network:
       driver: bridge
       internal: false  # Set to true if no external access needed
   ```

4. **Regular Updates**:
   ```bash
   # Check for updates
   docker pull jeromemassey76/pyats-ro-api:latest
   ```

## Support

- **GitHub Issues**: https://github.com/jerome-massey/pyats-ro-api/issues
- **Documentation**: https://github.com/jerome-massey/pyats-ro-api
- **Docker Hub**: https://hub.docker.com/r/jeromemassey76/pyats-ro-api

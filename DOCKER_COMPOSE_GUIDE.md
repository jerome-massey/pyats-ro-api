# Docker Compose Files Guide

This document describes all available Docker Compose files and when to use each one.

## Quick Reference

| File | Purpose | Uses Docker Hub? | Builds Locally? | When to Use |
|------|---------|------------------|-----------------|-------------|
| `docker-compose.yml` | Production - REST API only | ✅ Yes | ❌ No | Simple production deployment |
| `docker-compose.dev.yml` | Development - hot reload | ❌ No | ✅ Yes | Local development with code changes |
| `docker-compose.mcp.yml` | Development - API + MCP | ❌ No | ✅ Yes | Local development with MCP features |
| `docker-compose.prod.yml` | Production - REST API only | ✅ Yes | ❌ No | Simple production (alternative) |
| `docker-compose.mcp.prod.yml` | Production - API + MCP | ✅ Yes | ❌ No | Production with MCP services |
| `docker-compose.nginx.yml` | Production - HTTPS + all services | ✅ Yes | ❌ No | Production with SSL/TLS proxy |

## Detailed Descriptions

### 1. `docker-compose.yml` (Recommended for Simple Production)

**Purpose**: Quick production deployment with REST API only

**Uses**: Docker Hub image (`jeromemassey76/pyats-ro-api:latest`)

**Services**:
- REST API on port 8000

**Example**:
```bash
docker-compose up -d
curl http://localhost:8000/health
```

**Best for**:
- Simple production deployments
- Users who just need the REST API
- Stateless cloud deployments

### 2. `docker-compose.dev.yml` (Development with Hot Reload)

**Purpose**: Local development with code hot-reload

**Uses**: Local build from `Dockerfile.dev` (development image with extra tools)

**Services**:
- REST API on port 8000 with hot-reload
- Includes: pytest, black, flake8, ipython

**Features**:
- Volume mounts for hot-reload (`./app`, `./run.py`, `./test_validation.py`)
- DEBUG log level
- stdin_open + tty for interactive debugging

**Example**:
```bash
docker-compose -f docker-compose.dev.yml up
# Make changes to code, API automatically reloads
```

**Best for**:
- Active development on the REST API
- Code changes without rebuilding
- Testing and validation during development

### 3. `docker-compose.mcp.yml` (Development with API + MCP)

**Purpose**: Local development with all services (REST API + MCP)

**Uses**: Local build from `Dockerfile` (single multi-purpose image)

**Services**:
- REST API on port 8000
- MCP SSE server on port 3000
- MCP stdio server (on-demand: `docker-compose -f docker-compose.mcp.yml run --rm pyats-mcp-stdio`)

**Features**:
- Volume mounts for examples (`./examples`)
- Single image supports all endpoints
- Perfect for developing MCP features

**Example**:
```bash
# Start all services
docker-compose -f docker-compose.mcp.yml up -d

# Run MCP stdio on-demand
docker-compose -f docker-compose.mcp.yml run --rm pyats-mcp-stdio

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:3000/health
```

**Best for**:
- Developing new MCP features
- Testing all three service modes simultaneously
- Local integration testing

### 4. `docker-compose.prod.yml` (Production - REST API Only)

**Purpose**: Production REST API deployment

**Uses**: Docker Hub image (`jeromemassey76/pyats-ro-api:latest`)

**Services**:
- REST API on port 8000

**Features**:
- No local build (pulls pre-built image)
- Health checks enabled
- Optimized for production

**Example**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Best for**:
- Alternative to `docker-compose.yml` for explicit production labeling

### 5. `docker-compose.mcp.prod.yml` (Production - All Services)

**Purpose**: Production deployment with REST API + MCP services

**Uses**: Docker Hub image (`jeromemassey76/pyats-ro-api:latest`)

**Services**:
- REST API on port 8000
- MCP SSE server on port 3000
- MCP stdio server (on-demand)

**Features**:
- No local build
- Health checks for all services
- All three access methods available

**Example**:
```bash
# Start API and MCP SSE
docker-compose -f docker-compose.mcp.prod.yml up -d

# Or just the API
docker-compose -f docker-compose.mcp.prod.yml up -d pyats-api

# Or just MCP SSE
docker-compose -f docker-compose.mcp.prod.yml up -d pyats-mcp-sse

# Run MCP stdio on-demand
docker-compose -f docker-compose.mcp.prod.yml run --rm pyats-mcp-stdio
```

**Best for**:
- Production deployments needing all service types
- Distributed MCP clients via SSE
- Maximum flexibility in production

### 6. `docker-compose.nginx.yml` (Production HTTPS with Reverse Proxy)

**Purpose**: Production deployment with HTTPS and reverse proxy

**Uses**: Docker Hub image for API/MCP services, nginx:alpine for reverse proxy

**Services**:
- Nginx reverse proxy on 80 (HTTP) and 443 (HTTPS)
- REST API on internal port 8000
- MCP SSE on internal port 3000

**Features**:
- SSL/TLS termination via Nginx
- Health checks for all services
- Log persistence via volumes
- Network isolation between services

**Required Setup**:
1. Create SSL certificates:
   ```bash
   mkdir -p ssl
   # Add your ssl/certificate.crt and ssl/private.key
   ```

2. Configure nginx.conf (already exists)

3. Start the stack:
   ```bash
   docker-compose -f docker-compose.nginx.yml up -d
   ```

4. Access via HTTPS:
   ```bash
   curl https://localhost/
   curl https://localhost:3000/
   ```

**Best for**:
- Production with SSL/TLS requirements
- Public internet deployments
- High-security environments
- Reverse proxy benefits (load balancing, caching, etc.)

## Decision Tree

```
Need to deploy PyATS API?
│
├─ Development?
│  ├─ Just REST API with hot-reload?
│  │  └─ Use: docker-compose.dev.yml
│  │
│  └─ Need MCP features too?
│     └─ Use: docker-compose.mcp.yml
│
├─ Production?
│  ├─ Simple REST API only?
│  │  └─ Use: docker-compose.yml or docker-compose.prod.yml
│  │
│  ├─ Need all services (API + MCP)?
│  │  ├─ Need HTTPS/SSL?
│  │  │  └─ Use: docker-compose.nginx.yml
│  │  │
│  │  └─ Just HTTP?
│  │     └─ Use: docker-compose.mcp.prod.yml
│  │
│  └─ Need HTTPS but only API?
│     └─ Use: docker-compose.nginx.yml (disable MCP service)
```

## Common Commands

### Development

```bash
# REST API with hot-reload
docker-compose -f docker-compose.dev.yml up

# All services (API + MCP) in development
docker-compose -f docker-compose.mcp.yml up -d
docker-compose -f docker-compose.mcp.yml logs -f
```

### Production

```bash
# Simple API
docker-compose -f docker-compose.prod.yml up -d

# All services
docker-compose -f docker-compose.mcp.prod.yml up -d

# HTTPS with Nginx
docker-compose -f docker-compose.nginx.yml up -d
```

### Testing

```bash
# Test API health
curl http://localhost:8000/health

# Test MCP SSE health
curl http://localhost:3000/health

# Run MCP stdio
docker-compose -f docker-compose.mcp.yml run --rm pyats-mcp-stdio
```

### Cleanup

```bash
# Stop services
docker-compose -f <file> down

# Remove all containers and networks
docker-compose -f <file> down -v

# Remove images too
docker rmi jeromemassey76/pyats-ro-api:latest
```

## Environment Variables

All files support these environment variables:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1
LOG_LEVEL=INFO        # or DEBUG for development

# MCP Configuration
MCP_HOST=0.0.0.0
MCP_PORT=3000
LOG_LEVEL=INFO

# Jumphost (Optional)
JUMPHOST_HOST=jumphost.example.com
JUMPHOST_PORT=22
JUMPHOST_USERNAME=jumpuser
JUMPHOST_KEY_PATH=/root/.ssh/jumphost_key
```

## Version Pinning

To pin to a specific version:

```bash
# Edit the compose file and change:
# image: jeromemassey76/pyats-ro-api:latest
# To:
# image: jeromemassey76/pyats-ro-api:v1.0.0
# Or:
# image: jeromemassey76/pyats-ro-api:1.0
# Or:
# image: jeromemassey76/pyats-ro-api:1
```

## Comparison Table

| Aspect | dev.yml | mcp.yml | prod.yml | mcp.prod.yml | nginx.yml |
|--------|---------|---------|----------|--------------|-----------|
| **Uses Docker Hub** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Builds Locally** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Hot Reload** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **REST API** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **MCP SSE** | ❌ | ✅ | ❌ | ✅ | ✅ |
| **MCP stdio** | ❌ | ✅ | ❌ | ✅ | ❌ |
| **HTTPS/SSL** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Nginx Proxy** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Dev Tools** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Best For** | Dev | Dev+MCP | Prod | Prod+MCP | Prod+HTTPS |

## Migration Guide

### From Development to Production

```bash
# Development
docker-compose -f docker-compose.dev.yml down

# Production (same services)
docker-compose -f docker-compose.mcp.prod.yml up -d
```

### Adding HTTPS to Existing Setup

```bash
# Current setup
docker-compose -f docker-compose.mcp.prod.yml down

# New setup with HTTPS
docker-compose -f docker-compose.nginx.yml up -d
```

## Troubleshooting

### "Image not found"
The image must be pulled from Docker Hub first:
```bash
docker pull jeromemassey76/pyats-ro-api:latest
```

### "Port already in use"
Change port mappings:
```yaml
services:
  pyats-api:
    ports:
      - "9000:8000"  # Host:Container
```

### "Can't connect to health endpoint"
Wait a few seconds for the service to start:
```bash
sleep 5 && curl http://localhost:8000/health
```

### "Build fails"
Make sure you're in the right directory:
```bash
cd /home/jmassey/builds/pyats-api
docker-compose -f docker-compose.dev.yml up
```

## Support

- See [README.md](README.md) for general installation
- See [DOCKER_HUB.md](DOCKER_HUB.md) for Docker Hub details
- See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment guidance

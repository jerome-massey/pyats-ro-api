# Quick Reference: Docker Hub vs Local Build

## TL;DR - What Should I Use?

| Use Case | Command | File |
|----------|---------|------|
| **Production - Simple** | `docker pull jeromemassey76/pyats-ro-api:latest && docker run -d -p 8000:8000 jeromemassey76/pyats-ro-api:latest` | None needed |
| **Production - Compose** | `docker-compose -f docker-compose.prod.yml up -d` | [docker-compose.prod.yml](docker-compose.prod.yml) |
| **Production - API+MCP** | `docker-compose -f docker-compose.mcp.prod.yml up -d` | [docker-compose.mcp.prod.yml](docker-compose.mcp.prod.yml) |
| **Development** | `docker-compose -f docker-compose.dev.yml up` | [docker-compose.dev.yml](docker-compose.dev.yml) |
| **Development - MCP** | `docker-compose -f docker-compose.mcp.yml up -d` | [docker-compose.mcp.yml](docker-compose.mcp.yml) |

## Docker Compose Files Explained

### Production (Uses Docker Hub Images)

| File | Purpose | Build? | When to Use |
|------|---------|--------|-------------|
| `docker-compose.prod.yml` | REST API only | ❌ No (pulls from Docker Hub) | Simple production deployment |
| `docker-compose.mcp.prod.yml` | API + MCP servers | ❌ No (pulls from Docker Hub) | Full production with MCP support |

### Development (Builds Locally)

| File | Purpose | Build? | When to Use |
|------|---------|--------|-------------|
| `docker-compose.yml` | REST API only | ✅ Yes (builds from Dockerfile) | Legacy/simple local testing |
| `docker-compose.dev.yml` | REST API with dev tools | ✅ Yes (builds from Dockerfile.dev) | Development with hot-reload |
| `docker-compose.mcp.yml` | API + MCP servers | ✅ Yes (builds unified image) | Development with MCP |

### Special Purpose

| File | Purpose | When to Use |
|------|---------|-------------|
| `docker-compose.nginx.yml` | HTTPS reverse proxy | Production with SSL/TLS |

## Services Available

### REST API (Port 8000)
- Endpoint: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### MCP SSE (Port 3000)
- Endpoint: `http://localhost:3000`
- Health: `http://localhost:3000/health`
- Type: Server-Sent Events (remote MCP clients)

### MCP stdio
- No port (uses stdin/stdout)
- Type: Standard I/O (local MCP clients like Claude Desktop)
- Run on-demand only

## Common Commands

### Pull Latest Image
```bash
docker pull jeromemassey76/pyats-ro-api:latest
```

### Run API Only
```bash
# From Docker Hub
docker run -d -p 8000:8000 --name pyats-api jeromemassey76/pyats-ro-api:latest

# From local build
docker-compose -f docker-compose.dev.yml up
```

### Run API + MCP
```bash
# From Docker Hub (production)
docker-compose -f docker-compose.mcp.prod.yml up -d

# From local build (development)
docker-compose -f docker-compose.mcp.yml up -d
```

### Run Specific Service
```bash
# Just API
docker-compose -f docker-compose.mcp.prod.yml up -d pyats-api

# Just MCP SSE
docker-compose -f docker-compose.mcp.prod.yml up -d pyats-mcp-sse

# MCP stdio (on-demand)
docker-compose -f docker-compose.mcp.prod.yml run --rm pyats-mcp-stdio
```

### Version Pinning
```bash
# Latest
docker pull jeromemassey76/pyats-ro-api:latest

# Specific version
docker pull jeromemassey76/pyats-ro-api:v1.0.0

# Major.minor
docker pull jeromemassey76/pyats-ro-api:1.0

# Major only
docker pull jeromemassey76/pyats-ro-api:1
```

### Check Health
```bash
# REST API
curl http://localhost:8000/health

# MCP SSE
curl http://localhost:3000/health
```

### View Logs
```bash
# Docker run
docker logs -f pyats-api

# Docker compose
docker-compose -f docker-compose.mcp.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.mcp.prod.yml logs -f pyats-api
```

### Stop Services
```bash
# Docker run
docker stop pyats-api
docker rm pyats-api

# Docker compose
docker-compose -f docker-compose.mcp.prod.yml down
```

## Decision Tree

```
Need to deploy PyATS API?
│
├─ Production?
│  ├─ Just REST API?
│  │  └─ Use: docker-compose.prod.yml (Docker Hub)
│  │
│  ├─ Need MCP too?
│  │  └─ Use: docker-compose.mcp.prod.yml (Docker Hub)
│  │
│  └─ Need HTTPS?
│     └─ Use: docker-compose.nginx.yml
│
└─ Development?
   ├─ Just testing API?
   │  └─ Use: docker-compose.dev.yml (local build)
   │
   ├─ Developing MCP features?
   │  └─ Use: docker-compose.mcp.yml (local build)
   │
   └─ Making code changes?
      └─ Use: docker-compose.dev.yml (has hot-reload)
```

## Environment Variables

### Required for Jumphost
```bash
JUMPHOST_HOST=jumphost.example.com
JUMPHOST_PORT=22
JUMPHOST_USERNAME=jumpuser
JUMPHOST_KEY_PATH=/root/.ssh/jumphost_key
```

### Optional Configuration
```bash
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1
LOG_LEVEL=INFO
MCP_HOST=0.0.0.0
MCP_PORT=3000
```

## Volume Mounts

### SSH Key (for jumphost)
```yaml
volumes:
  - ~/.ssh/id_rsa:/root/.ssh/jumphost_key:ro
```

### Development (hot-reload)
```yaml
volumes:
  - ./app:/app/app
  - ./run.py:/app/run.py
```

## Image Details

| Aspect | Value |
|--------|-------|
| Repository | `jeromemassey76/pyats-ro-api` |
| Registry | Docker Hub |
| Architectures | `linux/amd64`, `linux/arm64` |
| Base Image | `python:3.11-slim` |
| Size | ~500 MB |
| Auto-build | On GitHub releases |

## Links

- **Docker Hub**: https://hub.docker.com/r/jeromemassey76/pyats-ro-api
- **GitHub**: https://github.com/jerome-massey/pyats-ro-api
- **Documentation**: [README.md](README.md)
- **Docker Hub Guide**: [DOCKER_HUB.md](DOCKER_HUB.md)
- **Setup Guide**: [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)

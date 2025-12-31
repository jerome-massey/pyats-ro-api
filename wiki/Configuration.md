# Configuration

Complete guide to configuring the PyATS Show Command API.

## Environment Variables

The API is configured using environment variables. These can be set via:
- `.env` file
- Docker environment variables
- System environment variables
- Kubernetes ConfigMaps/Secrets

### API Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | API server bind address |
| `API_PORT` | `8000` | API server port |
| `API_WORKERS` | `1` | Number of Uvicorn workers |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### MCP Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_HOST` | `0.0.0.0` | MCP SSE server bind address |
| `MCP_PORT` | `3000` | MCP SSE server port |

---

## Configuration Methods

### Method 1: .env File

Create a `.env` file in the project root:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1
LOG_LEVEL=INFO

# MCP Configuration (if using MCP SSE)
MCP_HOST=0.0.0.0
MCP_PORT=3000
```

Then run:
```bash
# With Docker Compose
docker-compose up -d

# With Python
python run.py
```

### Method 2: Docker Environment Variables

**Docker Run**:
```bash
docker run -d \
  --name pyats-api \
  -p 8000:8000 \
  -e API_HOST=0.0.0.0 \
  -e API_PORT=8000 \
  -e LOG_LEVEL=INFO \
  jeromemassey76/pyats-ro-api:latest
```

**Docker Compose**:
```yaml
version: ''3.8''

services:
  pyats-api:
    image: jeromemassey76/pyats-ro-api:latest
    container_name: pyats-api
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - LOG_LEVEL=INFO
```

### Method 3: Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pyats-api-config
data:
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  LOG_LEVEL: "INFO"
```

Apply and reference in deployment:
```bash
kubectl apply -f configmap.yaml
```

```yaml
envFrom:
  - configMapRef:
      name: pyats-api-config
```

---

## SSH Jumphost Configuration

**Note**: As of v0.2.2, jumphost configuration is handled via SSH config files, not environment variables or API parameters.

### Overview

The jumphost feature allows the API to connect to devices behind a bastion/jump host using SSH ProxyJump. This is configured transparently via the container''s SSH config file.

### How It Works

1. SSH config file at `/root/.ssh/config` defines ProxyJump rules
2. When connecting to devices matching specific patterns, SSH automatically routes through the jumphost
3. No API parameters needed - it''s transparent to API requests

### Default Configuration

The default `entrypoint.sh` creates this SSH config:

```bash
# Jumphost configuration
Host jumphost
    HostName 10.0.0.21
    User cisco
    Port 22
    IdentityFile /root/.ssh/jumphost_key

# Route all 10.250.250.* connections through jumphost
Host 10.250.250.*
    ProxyJump jumphost
```

### Custom Configuration

To customize jumphost routing, modify `entrypoint.sh` or mount a custom SSH config:

**Option A: Modify entrypoint.sh**

Edit the SSH config generation in `entrypoint.sh`:

```bash
cat > /root/.ssh/config << ''EOF''
Host jumphost
    HostName YOUR_JUMPHOST_IP
    User YOUR_USERNAME
    Port 22
    IdentityFile /root/.ssh/jumphost_key

# Route specific subnet through jumphost
Host 192.168.100.*
    ProxyJump jumphost
EOF
```

**Option B: Mount SSH Config**

```bash
# Create custom SSH config
cat > ssh_config << ''EOF''
Host prod-jumphost
    HostName bastion.prod.example.com
    User automation
    Port 22
    IdentityFile /root/.ssh/jumphost_key

Host 10.10.*
    ProxyJump prod-jumphost
EOF

# Mount into container
docker run -d \
  -v $(pwd)/ssh_config:/root/.ssh/config:ro \
  -v ~/.ssh/jumphost_key:/root/.ssh/jumphost_key:ro \
  jeromemassey76/pyats-ro-api:latest
```

### SSH Key Setup

1. **Generate SSH Key** (if needed):
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/jumphost_key -N ""
```

2. **Copy Public Key to Jumphost**:
```bash
ssh-copy-id -i ~/.ssh/jumphost_key.pub user@jumphost.example.com
```

3. **Verify Connection**:
```bash
ssh -i ~/.ssh/jumphost_key user@jumphost.example.com
```

4. **Mount Key into Container**:
```bash
docker run -d \
  -v ~/.ssh/jumphost_key:/root/.ssh/jumphost_key:ro \
  jeromemassey76/pyats-ro-api:latest
```

### File Permissions

Ensure SSH keys have correct permissions:

```bash
# Private key (on host)
chmod 600 ~/.ssh/jumphost_key

# Public key on jumphost
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

---

## Logging Configuration

### Log Levels

Set `LOG_LEVEL` environment variable:

- `DEBUG` - Verbose output, including PyATS internals
- `INFO` - Normal operation (default)
- `WARNING` - Only warnings and errors
- `ERROR` - Only errors

### Log Format

Default format:
```
2024-01-15 10:30:45 - app.main - INFO - Starting PyATS API application
2024-01-15 10:30:46 - app.device_manager - INFO - Connecting to 192.168.1.1
```

### Log Locations

**Docker**:
```bash
# View live logs
docker logs -f pyats-api

# View logs with timestamps
docker logs --timestamps pyats-api

# View last 100 lines
docker logs --tail 100 pyats-api
```

**Docker Compose**:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f pyats-api

# Last 50 lines
docker-compose logs --tail 50
```

**Kubernetes**:
```bash
# View logs
kubectl logs -l app=pyats-api -f

# Specific pod
kubectl logs pyats-api-xxxxx -f

# Previous container logs
kubectl logs pyats-api-xxxxx --previous
```

---

## Performance Tuning

### Workers

Increase workers for better concurrency:

```bash
# Set number of Uvicorn workers
API_WORKERS=4
```

**Recommendation**: Set to number of CPU cores

### Timeouts

Adjust command timeout in API requests:

```json
{
  "devices": [...],
  "commands": [...],
  "timeout": 60
}
```

**Recommendation**: 
- Normal commands: 30 seconds (default)
- Long-running commands (show tech): 120+ seconds

### Resource Limits

**Docker**:
```bash
docker run -d \
  --cpus="2.0" \
  --memory="4g" \
  jeromemassey76/pyats-ro-api:latest
```

**Kubernetes**:
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

---

## Security Configuration

### Environment Variable Security

1. **Never commit .env files** to version control
2. **Use secrets management** (Kubernetes Secrets, Docker Secrets)
3. **Rotate SSH keys regularly**
4. **Use read-only volume mounts** for SSH keys

### File Permissions

Ensure SSH keys have correct permissions:

```bash
# Private key (mounted into container)
chmod 600 ~/.ssh/jumphost_key

# On jumphost
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### Network Security

1. **Restrict API access** using firewall rules
2. **Use HTTPS** in production
3. **Implement authentication** (API keys, OAuth2)
4. **Network segmentation** (VLANs, VPNs)

---

## Configuration Examples

### Example 1: Development

```bash
# .env
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=DEBUG
API_WORKERS=1
```

### Example 2: Production

```bash
# .env
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
API_WORKERS=4
```

### Example 3: With Custom Jumphost

```bash
# Custom entrypoint.sh with multiple jumphosts
cat > entrypoint.sh << ''SCRIPT''
#!/bin/bash

# Copy SSH key if mounted
if [ -f "/root/.ssh/jumphost_key.mounted" ]; then
    cp /root/.ssh/jumphost_key.mounted /root/.ssh/jumphost_key
    chmod 600 /root/.ssh/jumphost_key
fi

# Create SSH config with multiple jumphost rules
cat > /root/.ssh/config << ''EOF''
Host *
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

Host prod-jump
    HostName 10.1.1.1
    User produser
    IdentityFile /root/.ssh/jumphost_key

Host dev-jump
    HostName 10.2.2.1
    User devuser
    IdentityFile /root/.ssh/jumphost_key

# Production subnet via prod jumphost
Host 172.16.*
    ProxyJump prod-jump

# Dev subnet via dev jumphost
Host 192.168.*
    ProxyJump dev-jump
EOF

chmod 600 /root/.ssh/config
exec "$@"
SCRIPT

chmod +x entrypoint.sh
```

---

## Next Steps

- **[Getting Started](Getting-Started)** - Quick start guide
- **[API Reference](API-Reference)** - Complete API documentation
- **[Deployment](Deployment)** - Production deployment
- **[Security](Security)** - Security best practices

---

**Navigation**: [ Getting Started](Getting-Started) | [Home](Home) | [Deployment ](Deployment)
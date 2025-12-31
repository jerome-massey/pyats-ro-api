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

### Jumphost Configuration (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `JUMPHOST_HOST` | `None` | Jumphost hostname or IP |
| `JUMPHOST_PORT` | `22` | Jumphost SSH port |
| `JUMPHOST_USERNAME` | `None` | Jumphost SSH username |
| `JUMPHOST_KEY_PATH` | `None` | Path to SSH private key file |

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

# MCP Configuration
MCP_HOST=0.0.0.0
MCP_PORT=3000

# SSH Jumphost Configuration (Optional)
JUMPHOST_HOST=jumphost.example.com
JUMPHOST_PORT=22
JUMPHOST_USERNAME=jumpuser
JUMPHOST_KEY_PATH=/root/.ssh/jumphost_key
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
  -e JUMPHOST_HOST=jumphost.example.com \
  -e JUMPHOST_PORT=22 \
  -e JUMPHOST_USERNAME=jumpuser \
  -e JUMPHOST_KEY_PATH=/root/.ssh/jumphost_key \
  -v ~/.ssh/jumphost_key:/root/.ssh/jumphost_key:ro \
  jeromemassey76/pyats-ro-api:latest
```

**Docker Compose**:
```yaml
version: '3.8'

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
      - JUMPHOST_HOST=jumphost.example.com
      - JUMPHOST_PORT=22
      - JUMPHOST_USERNAME=jumpuser
      - JUMPHOST_KEY_PATH=/root/.ssh/jumphost_key
    volumes:
      - ~/.ssh/jumphost_key:/root/.ssh/jumphost_key:ro
    restart: unless-stopped
```

### Method 3: Kubernetes ConfigMap & Secret

**ConfigMap** (`configmap.yaml`):
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pyats-api-config
  namespace: default
data:
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  API_WORKERS: "1"
  LOG_LEVEL: "INFO"
  MCP_HOST: "0.0.0.0"
  MCP_PORT: "3000"
  JUMPHOST_HOST: "jumphost.example.com"
  JUMPHOST_PORT: "22"
  JUMPHOST_USERNAME: "jumpuser"
  JUMPHOST_KEY_PATH: "/root/.ssh/jumphost_key"
```

**Secret** (for SSH key):
```bash
kubectl create secret generic jumphost-ssh-key \
  --from-file=key=/path/to/jumphost_key \
  --namespace=default
```

**Deployment** (`deployment.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pyats-api
spec:
  template:
    spec:
      containers:
      - name: pyats-api
        image: jeromemassey76/pyats-ro-api:latest
        envFrom:
        - configMapRef:
            name: pyats-api-config
        volumeMounts:
        - name: ssh-key
          mountPath: /root/.ssh
          readOnly: true
      volumes:
      - name: ssh-key
        secret:
          secretName: jumphost-ssh-key
          defaultMode: 0400
```

---

## Jumphost Configuration

### Overview

The jumphost feature allows the API to connect to devices behind a bastion/jump host using SSH key-based authentication.

### Prerequisites

1. **SSH Key Pair**: Generate if you don't have one
2. **Public Key on Jumphost**: Copy to jumphost's `~/.ssh/authorized_keys`
3. **Private Key Accessible**: Mount into container or available on filesystem
4. **Network Access**: API can reach jumphost on port 22

### Step-by-Step Setup

#### 1. Generate SSH Key (if needed)

```bash
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -f ~/.ssh/jumphost_key -N ""

# This creates:
# - ~/.ssh/jumphost_key (private key)
# - ~/.ssh/jumphost_key.pub (public key)
```

#### 2. Copy Public Key to Jumphost

```bash
# Method 1: Using ssh-copy-id
ssh-copy-id -i ~/.ssh/jumphost_key.pub user@jumphost.example.com

# Method 2: Manual copy
cat ~/.ssh/jumphost_key.pub | ssh user@jumphost.example.com \
  "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# Method 3: Direct copy (if you have access)
# On jumphost:
cat >> ~/.ssh/authorized_keys << 'EOF'
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQ... user@host
EOF
```

#### 3. Verify SSH Key Authentication

```bash
# Test connection (should not prompt for password)
ssh -i ~/.ssh/jumphost_key user@jumphost.example.com
```

#### 4. Configure API

**Option A: Global Jumphost (Environment Variables)**

Use for all requests that set `use_jumphost: true`:

```bash
# .env file
JUMPHOST_HOST=jumphost.example.com
JUMPHOST_PORT=22
JUMPHOST_USERNAME=jumpuser
JUMPHOST_KEY_PATH=/root/.ssh/jumphost_key
```

```bash
# Docker run with volume mount
docker run -d \
  -p 8000:8000 \
  -v ~/.ssh/jumphost_key:/root/.ssh/jumphost_key:ro \
  -e JUMPHOST_HOST=jumphost.example.com \
  -e JUMPHOST_PORT=22 \
  -e JUMPHOST_USERNAME=jumpuser \
  -e JUMPHOST_KEY_PATH=/root/.ssh/jumphost_key \
  jeromemassey76/pyats-ro-api:latest
```

**Option B: Per-Device Jumphost (Request Body)**

Specify jumphost config per device in API request:

```json
{
  "devices": [
    {
      "hostname": "192.168.1.1",
      "username": "admin",
      "password": "cisco123",
      "os": "iosxe",
      "jumphost": {
        "host": "jumphost.example.com",
        "port": 22,
        "username": "jumpuser",
        "key_path": "/root/.ssh/jumphost_key"
      }
    }
  ],
  "commands": [
    {"command": "show version"}
  ]
}
```

#### 5. Test Jumphost Connection

Use the jumphost test endpoint:

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

Expected response:
```json
{
  "success": true,
  "message": "Successfully connected to jumphost jumphost.example.com:22 as user 'jumpuser'"
}
```

### Jumphost Troubleshooting

#### SSH Key Not Found

**Error**: `"SSH key not found: /root/.ssh/jumphost_key"`

**Solution**: Ensure key is mounted into container:
```bash
docker run -v ~/.ssh/jumphost_key:/root/.ssh/jumphost_key:ro ...
```

#### Permission Denied

**Error**: `"Authentication failed"`

**Solution**: 
1. Verify public key is in jumphost's `~/.ssh/authorized_keys`
2. Check permissions:
   ```bash
   # On jumphost
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```
3. Test SSH connection manually:
   ```bash
   ssh -i ~/.ssh/jumphost_key user@jumphost.example.com
   ```

#### Connection Timeout

**Error**: `"Connection timeout"`

**Solution**:
1. Verify network connectivity from container to jumphost
2. Check firewall rules
3. Ensure jumphost is listening on specified port:
   ```bash
   ssh -p 22 user@jumphost.example.com
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

### Persistent Logging

Mount log directory to persist logs:

```bash
# Create log directory
mkdir -p logs/api

# Run with volume mount
docker run -d \
  -v $(pwd)/logs/api:/app/logs \
  jeromemassey76/pyats-ro-api:latest
```

**Docker Compose**:
```yaml
services:
  pyats-api:
    image: jeromemassey76/pyats-ro-api:latest
    volumes:
      - ./logs/api:/app/logs
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

Adjust command timeout:

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
chmod 400 ~/.ssh/jumphost_key

# On jumphost
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### Network Security

1. **Restrict API access** using firewall rules
2. **Use HTTPS** in production (see [HTTPS Setup](HTTPS-Setup))
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

### Example 3: With Jumphost

```bash
# .env
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

JUMPHOST_HOST=bastion.prod.example.com
JUMPHOST_PORT=22
JUMPHOST_USERNAME=automation
JUMPHOST_KEY_PATH=/root/.ssh/prod_key
```

### Example 4: MCP SSE Server

```bash
# .env
MCP_HOST=0.0.0.0
MCP_PORT=3000
LOG_LEVEL=INFO

JUMPHOST_HOST=jumphost.example.com
JUMPHOST_PORT=22
JUMPHOST_USERNAME=mcp-user
JUMPHOST_KEY_PATH=/root/.ssh/mcp_key
```

---

## Next Steps

- **[Jumphost Configuration](Jumphost-Configuration)** - Detailed jumphost setup
- **[Security Best Practices](Security)** - Security hardening
- **[Deployment](Deployment)** - Production deployment
- **[Monitoring](Monitoring)** - Logging and monitoring

---

**Navigation**: [← Getting Started](Getting-Started) | [Home](Home) | [Deployment →](Deployment)

# PyATS Show Command API - Deployment Guide

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Pre-Deployment Requirements](#pre-deployment-requirements)
4. [Deployment Options](#deployment-options)
5. [Jumphost Configuration](#jumphost-configuration)
6. [Features & Capabilities](#features--capabilities)
7. [Limitations & Constraints](#limitations--constraints)
8. [Security Hardening](#security-hardening)
9. [Monitoring & Logging](#monitoring--logging)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The PyATS Show Command API is a FastAPI application that provides a REST interface for executing show commands on network devices via PyATS/Unicon. It supports optional SSH jumphost proxying for accessing devices in restricted networks.

### Key Facts
- **Single-purpose API**: Show commands only (write-protection)
- **No testbed required**: Inline device credentials
- **Containerized**: Docker for consistent deployments
- **Stateless**: Each request is independent
- **Lightweight**: Minimal resource footprint

---

## Architecture

```
┌──────────────────┐
│  API Client      │
│  (curl/Python)   │
└────────┬─────────┘
         │
         ▼
    ┌─────────────────────────────────────┐
    │   FastAPI Application               │
    │  ┌─────────────────────────────────┐│
    │  │ Input Validation (Pydantic)     ││
    │  │ - Command injection prevention  ││
    │  │ - Credential validation         ││
    │  │ - Jumphost config validation    ││
    │  └─────────────────────────────────┘│
    │  ┌─────────────────────────────────┐│
    │  │ Endpoints:                      ││
    │  │ - /api/v1/execute               ││
    │  │ - /api/v1/jumphost/test         ││
    │  │ - /health                       ││
    │  └─────────────────────────────────┘│
    └────────┬──────────────────┬──────────┘
             │                  │
    ┌────────▼────────┐  ┌──────▼──────────┐
    │ Direct Device   │  │ Jumphost        │
    │ Connection      │  │ (SSH + Paramiko)│
    │ (Unicon/PyATS)  │  │                 │
    └────────┬────────┘  └──────┬──────────┘
             │                  │
    ┌────────▼──────────────────▼──────┐
    │      Network Devices              │
    │  (IOS, IOS-XE, NX-OS, etc.)       │
    └──────────────────────────────────┘
```

---

## Pre-Deployment Requirements

### System Requirements

| Component | Requirement |
|-----------|-------------|
| OS | Linux (RHEL, Ubuntu, CentOS, Debian) |
| Container Runtime | Docker 20.10+ or Podman |
| Python | 3.11+ (if running without Docker) |
| CPU | 2+ cores (recommended) |
| Memory | 4GB+ (recommended) |
| Disk | 10GB+ (for image cache) |

### Network Requirements

| Direction | Destination | Port | Protocol | Purpose |
|-----------|------------|------|----------|---------|
| Inbound | API Server | 8000 | TCP | API Requests |
| Outbound | Jumphost | 22 | TCP | SSH Key Auth |
| Outbound | Devices | 22 | TCP | SSH Show Commands |

### Credentials & Keys Required

1. **API Server** (if authentication enabled)
   - API keys or JWT tokens
   - TLS certificates for HTTPS

2. **Jumphost Access** (if using jumphost)
   - SSH private key file (passwordless preferred)
   - Jumphost username
   - Jumphost hostname/IP

3. **Target Devices**
   - Device username
   - Device password (plaintext in requests)

---

## Deployment Options

### Option 1: Docker Compose - REST API Only

#### Prerequisites
```bash
docker --version    # 20.10+
docker-compose --version  # 2.0+
```

#### Quick Deploy

```bash
# Clone repository
git clone <repo-url>
cd pyats-api

# Create environment file
cp .env.example .env

# Edit configuration
nano .env
# Set: JUMPHOST_HOST, JUMPHOST_USERNAME, JUMPHOST_KEY_PATH (if needed)

# Start REST API (port 8000)
docker-compose up -d

# Verify
curl http://localhost:8000/health
```

### Option 1b: Docker Compose - Full Stack (REST API + MCP)

Deploy all three services simultaneously:

```bash
# Start all services
docker-compose -f docker-compose.mcp.yml up -d

# Services running:
# - pyats-api:      REST API on port 8000
# - pyats-mcp-sse:  MCP Server (SSE) on port 3000
# - pyats-mcp-stdio: Available for on-demand stdio connections

# Verify REST API
curl http://localhost:8000/health

# Verify MCP SSE
curl http://localhost:3000/health
```

#### With Jumphost

```bash
# Create .env with jumphost config
cat > .env << EOF
JUMPHOST_HOST=jumphost.example.com
JUMPHOST_PORT=22
JUMPHOST_USERNAME=jumpuser
JUMPHOST_KEY_PATH=/root/.ssh/jumphost_key
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
EOF

# Mount SSH key into container
# Edit docker-compose.yml volumes section:
volumes:
  - ~/.ssh/jumphost_key:/root/.ssh/jumphost_key:ro

# Start
docker-compose up -d
```

### Option 2: Kubernetes Deployment

#### Create ConfigMap for Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pyats-api-config
  namespace: default
data:
  JUMPHOST_HOST: "jumphost.example.com"
  JUMPHOST_PORT: "22"
  JUMPHOST_USERNAME: "jumpuser"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  LOG_LEVEL: "INFO"
```

#### Create Secret for SSH Key

```bash
kubectl create secret generic pyats-ssh-key \
  --from-file=jumphost_key=/path/to/id_rsa \
  -n default
```

#### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pyats-api
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: pyats-api
  template:
    metadata:
      labels:
        app: pyats-api
    spec:
      containers:
      - name: pyats-api
        image: pyats-api:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
          name: http
        envFrom:
        - configMapRef:
            name: pyats-api-config
        volumeMounts:
        - name: ssh-key
          mountPath: /root/.ssh
          readOnly: true
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
      volumes:
      - name: ssh-key
        secret:
          secretName: pyats-ssh-key
          defaultMode: 0400
---
apiVersion: v1
kind: Service
metadata:
  name: pyats-api
  namespace: default
spec:
  selector:
    app: pyats-api
  ports:
  - port: 8000
    targetPort: 8000
    name: http
  type: LoadBalancer
```

#### Deploy to K8s

```bash
# Build image
docker build -f Dockerfile -t pyats-api:latest .

# Create namespace
kubectl create namespace pyats

# Create secrets and configmaps
kubectl apply -f config.yaml -n pyats

# Deploy
kubectl apply -f deployment.yaml -n pyats

# Verify
kubectl get pods -n pyats
kubectl logs -n pyats -l app=pyats-api
```

### Option 3: Manual Installation (Development)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings

# Run
python run.py

# Or with uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

### Option 4: Systemd Service (Production Linux)

#### Create Service File

```ini
# /etc/systemd/system/pyats-api.service
[Unit]
Description=PyATS Show Command API
After=network.target

[Service]
Type=notify
User=pyats
WorkingDirectory=/opt/pyats-api
EnvironmentFile=/opt/pyats-api/.env
ExecStart=/opt/pyats-api/venv/bin/uvicorn \
  app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable pyats-api
sudo systemctl start pyats-api
sudo systemctl status pyats-api
```

---

## Jumphost Configuration

### Single Global Jumphost

**Use Case**: All devices accessed through one jumphost

```bash
# .env configuration
JUMPHOST_HOST=corp-jumphost.example.com
JUMPHOST_PORT=22
JUMPHOST_USERNAME=netadmin
JUMPHOST_KEY_PATH=/root/.ssh/jumphost_key

# API request
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [{
      "hostname": "device.internal",
      "username": "admin",
      "password": "pass",
      "os": "iosxe"
    }],
    "commands": [{"command": "show version"}],
    "use_jumphost": true
  }'
```

### Per-Device Jumphost

**Use Case**: Different devices need different jumphosts

```bash
# No global jumphost config needed
# Each device specifies its own jumphost

curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "hostname": "west-device.internal",
        "username": "admin",
        "password": "pass",
        "os": "iosxe",
        "jumphost": {
          "host": "west-jumphost.example.com",
          "port": 22,
          "username": "netadmin",
          "key_path": "/root/.ssh/west_jumphost_key"
        }
      },
      {
        "hostname": "east-device.internal",
        "username": "admin",
        "password": "pass",
        "os": "iosxe",
        "jumphost": {
          "host": "east-jumphost.example.com",
          "port": 22,
          "username": "netadmin",
          "key_path": "/root/.ssh/east_jumphost_key"
        }
      }
    ],
    "commands": [{"command": "show version"}],
    "use_jumphost": false
  }'
```

### Testing Jumphost Configuration

Before executing commands, validate jumphost connectivity:

```bash
curl -X POST http://localhost:8000/api/v1/jumphost/test \
  -H "Content-Type: application/json" \
  -d '{
    "jumphost": {
      "host": "jumphost.example.com",
      "port": 22,
      "username": "netadmin",
      "key_path": "/root/.ssh/jumphost_key"
    }
  }'

# Response example:
# {
#   "host": "jumphost.example.com",
#   "port": 22,
#   "username": "netadmin",
#   "success": true,
#   "message": "Successfully connected...",
#   "error": null
# }
```

### SSH Key Setup

```bash
# Generate new key if needed
ssh-keygen -t ed25519 -f ~/.ssh/jumphost_key -N ""

# Copy to jumphost
ssh-copy-id -i ~/.ssh/jumphost_key.pub user@jumphost.example.com

# Fix permissions
chmod 600 ~/.ssh/jumphost_key

# Test connectivity
ssh -i ~/.ssh/jumphost_key -p 22 user@jumphost.example.com "echo success"
```

---

## Features & Capabilities

### ✅ Core Features

| Feature | Status | Details |
|---------|--------|---------|
| Show Commands Only | ✅ Active | Regex validation, blocks 12+ dangerous patterns |
| Device Credentials | ✅ Active | Supports username/password, enable password |
| Multiple Devices | ✅ Active | Batch execute on multiple devices in one request |
| Pipe Options | ✅ Active | include, exclude, begin, section |
| Direct Connection | ✅ Active | Direct SSH to device |
| SSH Jumphost | ✅ Active | Key-based SSH to jumphost, then to device |
| Per-Device Jumphost | ✅ Active | Each device can use different jumphost |
| Global Jumphost | ✅ Active | Fallback jumphost for devices without config |
| Jumphost Testing | ✅ Active | Test jumphost before executing commands |
| Input Validation | ✅ Active | Pydantic validators, early rejection |
| Async Support | ✅ Active | FastAPI async endpoints |
| Docker Support | ✅ Active | Dev and production containers |
| Hot Reload | ✅ Active | Development mode with auto-reload |

### Supported Operating Systems

- Cisco IOS (ios)
- Cisco IOS-XE (iosxe)
- Cisco IOS-XR (iosxr)
- Cisco NX-OS (nxos)
- Cisco ASA (asa)

**Note**: Juniper JunOS is explicitly **NOT supported**. JunOS uses different pipe syntax (`match` vs `include`) and would require separate implementation. If you attempt to use `os: "junos"`, the API will reject the request with a validation error explaining this limitation.

### Supported Commands

Only commands starting with "show" are allowed.

Examples:
- ✅ `show version`
- ✅ `show ip interface brief`
- ✅ `show running-config | include interface`
- ✅ `show route`
- ❌ `configure terminal` (rejected)
- ❌ `write memory` (rejected)
- ❌ `reload` (rejected)

---

## Limitations & Constraints

### ⚠️ Command Execution

| Limitation | Impact | Workaround |
|-----------|--------|-----------|
| Show commands only | Cannot make config changes | Use different API/tool for config |
| Single device connection | Sequential execution per device | Use batch requests for multiple devices |
| 30 sec default timeout | Long-running commands may timeout | Increase timeout in request (max suggested 60s) |
| No command history | Cannot retrieve previous outputs | Log responses on client side |
| No config backup | Data not persisted | Store responses in external system |

### ⚠️ Jumphost

| Limitation | Impact | Workaround |
|-----------|--------|-----------|
| SSH key auth only | Cannot use password-based jumphost auth | Use SSH agent or key-based auth |
| No multi-hop | Cannot chain multiple jumphosts | Use one jumphost, configure port forwarding on it |
| Single global jumphost | Cannot switch jumphosts without restart | Use per-device jumphost config instead |
| No connection pooling | New connection per request | Deploy multiple instances behind load balancer |
| No keepalive | Connections dropped after use | Acceptable for show commands (fast) |

### ⚠️ Authentication & Security

| Limitation | Impact | Workaround |
|-----------|--------|-----------|
| No API authentication | Anyone with network access can use API | Add reverse proxy (nginx) with auth |
| Passwords in request body | Credentials in logs/history | Use HTTPS only, rotate credentials |
| No encryption at rest | Credentials not encrypted in storage | Treat as ephemeral API |
| No rate limiting | Abuse/DoS possible | Add nginx rate limiting |
| No request signing | Cannot verify request authenticity | Add API key or JWT auth |

### ⚠️ Scale & Performance

| Limitation | Impact | Workaround |
|-----------|--------|-----------|
| Single worker (default) | Sequential request processing | Scale with multiple instances |
| Blocking I/O | No true parallelism | Use asyncio.to_thread() for concurrency |
| Memory per connection | Connection objects not pooled | Limit concurrent connections |
| No caching | Same command repeated = new execution | Implement client-side caching |

### ⚠️ Feature Gaps

| Gap | Impact | Timeline |
|-----|--------|----------|
| No unit tests | Untested code paths | Planned: Q1 2026 |
| No API versioning | Breaking changes possible | Planned: v2 API |
| No webhook support | Cannot push results | Planned: Future |
| No device inventory | Must provide all credentials | Use external source |
| No credential store | Credentials passed per request | Integrate with Vault/SecretManager |
| No multi-tenancy | Single deployment for all users | Planned: Future |

---

## Security Hardening

### ✅ Built-In Protections

```python
# Command injection prevention (12+ patterns)
✓ Regex validation: Must start with "show"
✓ Dangerous character blocking: ; \n \r ` $ && || > < & !
✓ Config keywords blocked: configure, write, reload, delete, etc.
✓ Max length enforcement: 1000 chars
✓ Pipe value sanitization: Only safe chars allowed

# Input validation
✓ Hostname format validation
✓ Port range validation (1-65535)
✓ Username/password non-empty checks
✓ OS type validation (JunOS explicitly rejected)
✓ Pydantic validators on all inputs

# Jumphost security
✓ SSH key authentication only (no password auth)
✓ Key file path validation
✓ Connection timeout (10 sec)
✓ Proper resource cleanup
```

### 🔒 Deployment Hardening

#### 1. Use HTTPS/TLS

```nginx
# nginx reverse proxy
server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    ssl_certificate /etc/ssl/certs/api.crt;
    ssl_certificate_key /etc/ssl/private/api.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 2. Add API Authentication

```python
# Example: FastAPI with API key auth
from fastapi.security import APIKeyHeader
from fastapi import Security, HTTPException

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key not in VALID_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

#### 3. Rate Limiting

```nginx
# nginx rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=jump_test:10m rate=5r/s;

location /api/v1/execute {
    limit_req zone=api_limit burst=20;
    proxy_pass http://localhost:8000;
}

location /api/v1/jumphost/test {
    limit_req zone=jump_test burst=10;
    proxy_pass http://localhost:8000;
}
```

#### 4. Network Isolation

```bash
# Run in Docker network without external access
docker network create pyats-internal
docker-compose up --network pyats-internal

# Or K8s network policy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: pyats-api
spec:
  podSelector:
    matchLabels:
      app: pyats-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 22
```

#### 5. Credential Management

```bash
# Use environment variables for secrets
export JUMPHOST_KEY_PATH=/var/secrets/jumphost_key
export LOG_LEVEL=WARNING

# Or use secret manager
vault kv get secret/pyats-api

# Or K8s secrets
kubectl create secret generic jumphost-key \
  --from-file=/path/to/key
```

---

## Monitoring & Logging

### Logging Configuration

```bash
# Set log level
export LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# View logs
docker-compose logs -f pyats-api
# or
journalctl -u pyats-api -f
```

### Log Format

```
2025-12-30 15:45:30,123 - app.main - INFO - Received request to execute commands on 2 device(s)
2025-12-30 15:45:30,124 - app.main - INFO - Validated command: show version
2025-12-30 15:45:30,456 - app.device_manager - INFO - Connecting directly to 192.168.1.1
2025-12-30 15:45:32,789 - app.device_manager - INFO - Executing on 192.168.1.1: show version
2025-12-30 15:45:33,012 - app.main - INFO - Successfully connected to 192.168.1.1
```

### Health Check Endpoint

```bash
# Check API health
curl http://localhost:8000/health

# Response
{"status": "healthy"}
```

### Monitoring with Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'pyats-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### Log Aggregation

```bash
# Collect logs with fluentd
<source>
  @type tail
  path /var/log/pyats-api/*.log
  pos_file /var/log/pyats-api/position.pos
  <parse>
    @type json
  </parse>
  tag pyats-api
</source>

<match pyats-api>
  @type elasticsearch
  host elasticsearch.local
  port 9200
  index_name pyats-api-%Y.%m.%d
</match>
```

---

## Troubleshooting

### API Health Issues

```bash
# Check if API is running
curl -v http://localhost:8000/health

# Check container logs
docker-compose logs pyats-api

# Check port is listening
netstat -tlnp | grep 8000
```

### Jumphost Connection Issues

```bash
# Test jumphost directly
ssh -i ~/.ssh/jumphost_key -p 22 user@jumphost.example.com "echo success"

# Test via API endpoint
curl -X POST http://localhost:8000/api/v1/jumphost/test \
  -H "Content-Type: application/json" \
  -d '{
    "jumphost": {
      "host": "jumphost.example.com",
      "port": 22,
      "username": "user",
      "key_path": "/root/.ssh/jumphost_key"
    }
  }'

# Enable debug logging
export LOG_LEVEL=DEBUG
docker-compose restart
```

### Device Connection Issues

```bash
# Check device is reachable
ping <device-ip>
ssh -p 22 admin@<device-ip>

# Try via API with longer timeout
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [{...}],
    "commands": [{"command": "show version"}],
    "timeout": 60
  }'

# Check logs for details
docker-compose logs -f pyats-api | grep ERROR
```

### Command Validation Issues

```bash
# Rejected command (semicolon)
curl -X POST http://localhost:8000/api/v1/execute \
  -d '{"commands": [{"command": "show version ; configure"}]}'
# Response: 422 - Command contains disallowed character(s): ';'

# Rejected pipe value
curl -X POST http://localhost:8000/api/v1/execute \
  -d '{"commands": [{"command": "show run", "pipe_value": "; reload"}]}'
# Response: 422 - Pipe value contains disallowed character(s)

# Valid command
curl -X POST http://localhost:8000/api/v1/execute \
  -d '{"commands": [{"command": "show version | include Cisco"}]}'
# Response: Success
```

---

## Support & Resources

- **Documentation**: http://localhost:8000/docs (Swagger UI)
- **API Schema**: http://localhost:8000/openapi.json
- **Examples**: See `examples/` directory
- **GitHub Issues**: Open issue with logs and config (sanitized)

---

## License

MIT License

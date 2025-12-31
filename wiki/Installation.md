# Installation

This guide covers all installation methods for the PyATS Show Command API.

## Table of Contents

- [Docker Hub (Production)](#docker-hub-production)
- [Docker Compose](#docker-compose)
- [Local Python Environment](#local-python-environment)
- [Kubernetes](#kubernetes)
- [Nginx with HTTPS](#nginx-with-https)

---

## Docker Hub (Production)

**Recommended for production deployments**

The easiest way to run the API is using pre-built images from Docker Hub.

### Single Container

```bash
# Pull the latest image
docker pull jeromemassey76/pyats-ro-api:latest

# Run REST API on port 8000
docker run -d \
  --name pyats-api \
  -p 8000:8000 \
  -e API_HOST=0.0.0.0 \
  -e API_PORT=8000 \
  -e LOG_LEVEL=INFO \
  jeromemassey76/pyats-ro-api:latest

# Verify
curl http://localhost:8000/health
```

### Version Pinning

For production stability, pin to a specific version:

```bash
# Specific version
docker pull jeromemassey76/pyats-ro-api:v1.0.0
docker run -d -p 8000:8000 jeromemassey76/pyats-ro-api:v1.0.0

# Major.minor version (gets patch updates)
docker pull jeromemassey76/pyats-ro-api:1.0
docker run -d -p 8000:8000 jeromemassey76/pyats-ro-api:1.0

# Major version only (gets minor and patch updates)
docker pull jeromemassey76/pyats-ro-api:1
docker run -d -p 8000:8000 jeromemassey76/pyats-ro-api:1
```

### Available Tags

- `latest` - Latest stable release from main branch
- `v1.x.x` - Specific version (e.g., `v1.0.0`, `v1.2.3`)
- `1.x` - Major.minor versions (e.g., `1.0`, `1.2`)
- `1` - Major version only

---

## Docker Compose

### Production - REST API Only

Download and run the production compose file:

```bash
# Download the compose file
curl -O https://raw.githubusercontent.com/jerome-massey/pyats-ro-api/main/docker-compose.prod.yml

# Start the service
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop the service
docker-compose -f docker-compose.prod.yml down
```

### Production - API + MCP Services

For all services (REST API + MCP):

```bash
# Download the MCP production compose file
curl -O https://raw.githubusercontent.com/jerome-massey/pyats-ro-api/main/docker-compose.mcp.prod.yml

# Start all services
docker-compose -f docker-compose.mcp.prod.yml up -d

# Services available:
# - REST API: http://localhost:8000
# - MCP SSE: http://localhost:3000
```

### Development - Local Build

For development with hot-reload:

```bash
# Clone the repository
git clone https://github.com/jerome-massey/pyats-ro-api.git
cd pyats-ro-api

# Start development environment
make dev

# Or using docker-compose directly
docker-compose -f docker-compose.dev.yml up

# Code changes will automatically reload
```

### Development - API + MCP

For developing MCP features:

```bash
# Start all services with local builds
docker-compose -f docker-compose.mcp.yml up -d

# Run MCP stdio on-demand
docker-compose -f docker-compose.mcp.yml run --rm pyats-mcp-stdio
```

### Docker Compose Files Overview

| File | Purpose | Build? | When to Use |
|------|---------|--------|-------------|
| `docker-compose.prod.yml` | Production - REST API | No (Docker Hub) | Simple production |
| `docker-compose.mcp.prod.yml` | Production - API + MCP | No (Docker Hub) | Production with MCP |
| `docker-compose.dev.yml` | Development - hot reload | Yes (local) | Active development |
| `docker-compose.mcp.yml` | Development - API + MCP | Yes (local) | MCP development |
| `docker-compose.nginx.yml` | Production - HTTPS | No (Docker Hub) | Production with SSL |

---

## Local Python Environment

Run without Docker for development:

### Prerequisites

- Python 3.11 or higher
- pip
- virtualenv (recommended)

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/jerome-massey/pyats-ro-api.git
cd pyats-ro-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit configuration (optional)
nano .env

# Run the API server
python run.py
```

### Running the Server

**Development mode with hot-reload:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Production mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Using the run script:**
```bash
python run.py
```

### MCP Servers (Local)

```bash
# MCP stdio server
python mcp_stdio.py

# MCP SSE server (in another terminal)
python mcp_sse.py
```

---

## Kubernetes

Deploy to Kubernetes for enterprise-scale deployments.

### Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- Namespace created

### Basic Deployment

Create `deployment.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pyats-api-config
  namespace: default
data:
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  LOG_LEVEL: "INFO"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pyats-api
  namespace: default
spec:
  replicas: 3
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
        image: jeromemassey76/pyats-ro-api:latest
        ports:
        - containerPort: 8000
          protocol: TCP
        envFrom:
        - configMapRef:
            name: pyats-api-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
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
    protocol: TCP
  type: LoadBalancer
```

Deploy:

```bash
# Apply the configuration
kubectl apply -f deployment.yaml

# Check status
kubectl get pods -l app=pyats-api
kubectl get svc pyats-api

# View logs
kubectl logs -l app=pyats-api -f

# Get service endpoint
kubectl get svc pyats-api -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

### With Jumphost (Using Secrets)

Create SSH key secret:

```bash
# Create secret from SSH private key
kubectl create secret generic jumphost-ssh-key \
  --from-file=key=/path/to/jumphost_key \
  --namespace=default
```

Update deployment to mount the secret:

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
        env:
        - name: JUMPHOST_HOST
          value: "jumphost.example.com"
        - name: JUMPHOST_PORT
          value: "22"
        - name: JUMPHOST_USERNAME
          value: "jumpuser"
        - name: JUMPHOST_KEY_PATH
          value: "/root/.ssh/jumphost_key"
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

### Ingress Configuration

For HTTPS access:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pyats-api-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: pyats-api-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: pyats-api
            port:
              number: 8000
```

---

## Nginx with HTTPS

Deploy with Nginx reverse proxy for production HTTPS.

### Prerequisites

- Docker and Docker Compose
- SSL certificates (Let's Encrypt or self-signed)

### Generate SSL Certificates

**Option A: Self-Signed (Testing)**
```bash
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem \
  -subj "/CN=localhost"
```

**Option B: Let's Encrypt (Production)**
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone \
  -d api.yourdomain.com \
  -d mcp.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem
sudo chmod 644 ssl/*.pem
```

### Download Nginx Configuration

```bash
# Download nginx.conf
curl -O https://raw.githubusercontent.com/jerome-massey/pyats-ro-api/main/nginx.conf

# Download nginx compose file
curl -O https://raw.githubusercontent.com/jerome-massey/pyats-ro-api/main/docker-compose.nginx.yml
```

### Configure and Start

```bash
# Edit nginx.conf with your domain names
nano nginx.conf
# Replace: api.yourdomain.com and mcp.yourdomain.com

# Create log directories
mkdir -p logs/nginx logs/api logs/mcp

# Build the image (if needed)
docker build -t pyats-unified:latest .

# Start all services
docker-compose -f docker-compose.nginx.yml up -d

# Verify
curl -k https://localhost/health
curl -k https://localhost:3000/health
```

### Services Available

- **REST API**: https://api.yourdomain.com (or https://localhost)
- **MCP SSE**: https://mcp.yourdomain.com (or https://localhost:3000)
- **API Docs**: https://api.yourdomain.com/docs

---

## Post-Installation

### Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}

# API documentation
curl http://localhost:8000/docs
```

### Configure Jumphost (Optional)

See [Jumphost Configuration](Jumphost-Configuration) for detailed setup.

### Test API Call

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
    ],
    "use_jumphost": false
  }'
```

---

## Next Steps

- **[Configuration](Configuration)** - Configure environment variables
- **[API Reference](API-Reference)** - Explore API endpoints
- **[Examples](Examples)** - See more usage examples
- **[MCP Integration](MCP-Integration)** - Set up AI assistant access

---

**Navigation**: [← Getting Started](Getting-Started) | [Home](Home) | [Configuration →](Configuration)

# Troubleshooting

Common issues and their solutions for the PyATS Show Command API.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Connection Issues](#connection-issues)
- [Authentication Issues](#authentication-issues)
- [Command Execution Issues](#command-execution-issues)
- [Jumphost Issues](#jumphost-issues)
- [Performance Issues](#performance-issues)
- [Docker Issues](#docker-issues)
- [MCP Issues](#mcp-issues)

---

## Installation Issues

### Port Already in Use

**Symptom**:
```
Error starting userland proxy: listen tcp 0.0.0.0:8000: bind: address already in use
```

**Solution**:
```bash
# Find what's using port 8000
sudo netstat -tlnp | grep 8000
# or
sudo lsof -i :8000

# Kill the process or use a different port
docker run -d -p 8001:8000 --name pyats-api jeromemassey76/pyats-ro-api:latest
```

### Docker Image Pull Failed

**Symptom**:
```
Error response from daemon: pull access denied
```

**Solution**:
```bash
# Verify image name is correct
docker pull jeromemassey76/pyats-ro-api:latest

# If behind corporate proxy, configure Docker proxy
# Edit /etc/docker/daemon.json or ~/.docker/config.json
```

### Permission Denied

**Symptom**:
```
docker: Got permission denied while trying to connect to the Docker daemon socket
```

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in, or run:
newgrp docker

# Verify
docker ps
```

---

## Connection Issues

### Cannot Connect to API

**Symptom**:
```bash
curl: (7) Failed to connect to localhost port 8000: Connection refused
```

**Diagnostic Steps**:
```bash
# 1. Check if container is running
docker ps | grep pyats-api

# 2. Check container logs
docker logs pyats-api

# 3. Check if port is bound
netstat -tlnp | grep 8000

# 4. Test from inside container
docker exec pyats-api curl http://localhost:8000/health
```

**Solutions**:
```bash
# Restart container
docker restart pyats-api

# Check firewall
sudo ufw status
sudo ufw allow 8000/tcp

# Verify API_HOST is set correctly (should be 0.0.0.0, not 127.0.0.1)
docker inspect pyats-api | grep API_HOST
```

### Cannot Reach Network Devices

**Symptom**:
```json
{
  "error": "Connection timeout to device 192.168.1.1"
}
```

**Diagnostic Steps**:
```bash
# 1. Test network connectivity from container
docker exec pyats-api ping -c 3 192.168.1.1

# 2. Test SSH connectivity
docker exec pyats-api nc -zv 192.168.1.1 22

# 3. Check if device allows connections from container IP
docker inspect pyats-api | grep IPAddress
```

**Solutions**:
```bash
# Use host network mode
docker run --network host jeromemassey76/pyats-ro-api:latest

# Or use docker-compose with host network
services:
  pyats-api:
    network_mode: "host"

# Check device ACLs and firewall rules
```

### Connection Timeout

**Symptom**:
```json
{
  "error": "Timeout connecting to 192.168.1.1"
}
```

**Solutions**:
1. Increase timeout in request:
```json
{
  "devices": [...],
  "commands": [...],
  "timeout": 60
}
```

2. Check network latency:
```bash
docker exec pyats-api ping 192.168.1.1
```

3. Verify device is reachable:
```bash
docker exec pyats-api ssh admin@192.168.1.1
```

---

## Authentication Issues

### Invalid Credentials

**Symptom**:
```json
{
  "error": "Authentication failed for device 192.168.1.1"
}
```

**Solutions**:
1. Verify credentials are correct
2. Check if device username/password are case-sensitive
3. Ensure password doesn't contain special characters that need escaping
4. Try connecting manually:
```bash
docker exec -it pyats-api ssh admin@192.168.1.1
```

### Enable Password Required

**Symptom**:
```json
{
  "error": "Enable password required but not provided"
}
```

**Solution**:
Add enable password to request:
```json
{
  "devices": [
    {
      "hostname": "192.168.1.1",
      "username": "admin",
      "password": "cisco123",
      "os": "ios",
      "enable_password": "enable123"
    }
  ],
  "commands": [...]
}
```

### SSH Key Authentication Failed

**Symptom**:
```
Authentication failed (publickey)
```

**Solutions**:
```bash
# 1. Verify key permissions
ls -la ~/.ssh/jumphost_key
chmod 400 ~/.ssh/jumphost_key

# 2. Test key manually
ssh -i ~/.ssh/jumphost_key user@jumphost.example.com

# 3. Verify key is mounted in container
docker exec pyats-api ls -la /root/.ssh/

# 4. Check key format (should be OpenSSH format)
head -1 ~/.ssh/jumphost_key
# Should show: -----BEGIN OPENSSH PRIVATE KEY-----
```

---

## Command Execution Issues

### Command Not Allowed

**Symptom**:
```json
{
  "detail": "Only 'show' commands are allowed. Command rejected: configure terminal"
}
```

**Solution**:
This is intentional security restriction. Only `show` commands are permitted.

Valid commands:
- ✅ `show version`
- ✅ `show ip interface brief`
- ✅ `show running-config`

Invalid commands:
- ❌ `configure terminal`
- ❌ `copy running-config startup-config`
- ❌ `reload`

### Invalid OS Type

**Symptom**:
```json
{
  "detail": [
    {
      "msg": "value is not a valid enumeration member; permitted: 'ios', 'iosxe', 'iosxr', 'nxos', 'asa'"
    }
  ]
}
```

**Solution**:
Use valid OS type:
- `ios` - Cisco IOS
- `iosxe` - Cisco IOS-XE
- `iosxr` - Cisco IOS-XR
- `nxos` - Cisco NX-OS
- `asa` - Cisco ASA

```json
{
  "devices": [
    {
      "hostname": "192.168.1.1",
      "username": "admin",
      "password": "cisco123",
      "os": "iosxe"
    }
  ],
  "commands": [...]
}
```

### Command Timeout

**Symptom**:
```json
{
  "error": "Command execution timeout"
}
```

**Solutions**:
1. Increase timeout:
```json
{
  "devices": [...],
  "commands": [...],
  "timeout": 120
}
```

2. Check if command is hung on device
3. Try command manually on device
4. Use pipe filters to reduce output:
```json
{
  "command": "show running-config",
  "pipe": {
    "option": "section",
    "pattern": "interface"
  }
}
```

### Empty Output

**Symptom**:
Command succeeds but returns empty output.

**Solutions**:
1. Verify command is valid for device OS
2. Check if output actually exists on device
3. Try command manually on device
4. Check PyATS logs for details:
```bash
docker logs pyats-api -f
```

---

## Jumphost Issues

### SSH Key Not Found

**Symptom**:
```json
{
  "error": "SSH key not found: /root/.ssh/jumphost_key"
}
```

**Solutions**:
```bash
# 1. Verify key exists on host
ls -la ~/.ssh/jumphost_key

# 2. Verify volume mount
docker inspect pyats-api | grep -A 10 Mounts

# 3. Mount key correctly
docker run -v ~/.ssh/jumphost_key:/root/.ssh/jumphost_key:ro ...

# 4. Check key in container
docker exec pyats-api ls -la /root/.ssh/
```

### Jumphost Connection Failed

**Symptom**:
```json
{
  "success": false,
  "message": "Connection to jumphost failed"
}
```

**Diagnostic Steps**:
```bash
# 1. Test jumphost connectivity
ping jumphost.example.com

# 2. Test SSH to jumphost
ssh -i ~/.ssh/jumphost_key user@jumphost.example.com

# 3. Verify from container
docker exec pyats-api ping jumphost.example.com
docker exec pyats-api ssh -i /root/.ssh/jumphost_key user@jumphost.example.com
```

**Solutions**:
1. Verify jumphost hostname resolves
2. Check firewall allows SSH (port 22)
3. Ensure public key is in jumphost's `~/.ssh/authorized_keys`
4. Check key permissions (400 or 600)

### Jumphost Key Permissions

**Symptom**:
```
Permissions 0644 for '/root/.ssh/jumphost_key' are too open
```

**Solutions**:
```bash
# On host
chmod 400 ~/.ssh/jumphost_key

# In container (if needed)
docker exec pyats-api chmod 400 /root/.ssh/jumphost_key

# Mount with correct permissions
docker run -v ~/.ssh/jumphost_key:/root/.ssh/jumphost_key:ro ...
```

### Cannot Reach Device Through Jumphost

**Symptom**:
Jumphost connection succeeds but cannot reach target device.

**Solutions**:
```bash
# 1. Test from jumphost manually
ssh -i ~/.ssh/jumphost_key user@jumphost.example.com
# Then on jumphost:
ping 10.0.1.100
ssh admin@10.0.1.100

# 2. Verify routing on jumphost
# 3. Check device firewall allows jumphost IP
# 4. Verify device credentials are correct
```

---

## Performance Issues

### Slow Response Times

**Symptoms**:
- API requests take long time to complete
- Commands timeout frequently

**Solutions**:
1. Increase timeout:
```json
{"timeout": 60}
```

2. Increase workers:
```bash
docker run -e API_WORKERS=4 ...
```

3. Use pipe filters to reduce output:
```json
{
  "command": "show running-config",
  "pipe": {"option": "section", "pattern": "interface"}
}
```

4. Check device performance:
```bash
# On device
show processes cpu
show memory
```

5. Monitor API container:
```bash
docker stats pyats-api
```

### High Memory Usage

**Symptom**:
Container using excessive memory.

**Solutions**:
```bash
# 1. Check memory usage
docker stats pyats-api

# 2. Set memory limits
docker run --memory="2g" --memory-swap="2g" ...

# 3. In docker-compose.yml:
services:
  pyats-api:
    deploy:
      resources:
        limits:
          memory: 2G

# 4. Reduce concurrent requests
# 5. Restart container periodically
```

### API Becomes Unresponsive

**Symptom**:
API stops responding to requests.

**Solutions**:
```bash
# 1. Check logs
docker logs pyats-api --tail 100

# 2. Check container status
docker ps -a | grep pyats-api

# 3. Restart container
docker restart pyats-api

# 4. Check for resource exhaustion
docker stats pyats-api

# 5. Enable healthcheck in docker-compose.yml:
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## Docker Issues

### Container Exits Immediately

**Symptom**:
Container starts then immediately stops.

**Diagnostic Steps**:
```bash
# Check logs
docker logs pyats-api

# Check exit code
docker ps -a | grep pyats-api

# Run in foreground to see errors
docker run --rm -p 8000:8000 jeromemassey76/pyats-ro-api:latest
```

**Common Causes**:
1. Missing environment variables
2. Port already in use
3. Invalid configuration
4. Missing volume mounts

### Cannot Build Image

**Symptom**:
```
ERROR: failed to solve: process "/bin/sh -c pip install -r requirements.txt"
```

**Solutions**:
```bash
# 1. Clear Docker cache
docker builder prune -a

# 2. Build with no cache
docker build --no-cache -t pyats-api .

# 3. Check requirements.txt exists
ls -la requirements.txt

# 4. Try building with specific Dockerfile
docker build -f Dockerfile.dev -t pyats-api-dev .
```

### Volume Mount Not Working

**Symptom**:
Files not accessible in container.

**Solutions**:
```bash
# 1. Use absolute paths
docker run -v /home/user/.ssh:/root/.ssh:ro ...

# 2. Check permissions
ls -la ~/.ssh/jumphost_key

# 3. Verify mount inside container
docker exec pyats-api ls -la /root/.ssh/

# 4. Use $(pwd) for relative paths
docker run -v $(pwd)/config:/app/config:ro ...
```

---

## MCP Issues

### Claude Desktop Cannot Connect

**Symptom**:
Claude shows MCP server as disconnected.

**Solutions**:
1. Check Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\Logs\`
   - Linux: `~/.config/Claude/logs/`

2. Verify Docker image:
```bash
docker images | grep pyats
```

3. Test manually:
```bash
docker run -i --rm jeromemassey76/pyats-ro-api:latest python mcp_stdio.py
```

4. Check configuration file syntax:
```bash
# Validate JSON
cat ~/.config/Claude/claude_desktop_config.json | python3 -m json.tool
```

5. Restart Claude Desktop

### MCP SSE Server Not Starting

**Symptom**:
```
Error: Cannot start MCP SSE server
```

**Solutions**:
```bash
# 1. Check logs
docker logs pyats-mcp-sse

# 2. Verify port is available
netstat -tlnp | grep 3000

# 3. Test endpoint
curl http://localhost:3000/health

# 4. Restart service
docker restart pyats-mcp-sse
```

### MCP Tool Execution Fails

**Symptom**:
Claude reports tool execution error.

**Solutions**:
1. Check MCP server logs
2. Verify device credentials
3. Test same command via REST API
4. Increase timeout in MCP call

---

## Diagnostic Commands

### Health Check

```bash
# API health
curl http://localhost:8000/health

# MCP SSE health
curl http://localhost:3000/health
```

### View Logs

```bash
# Docker logs
docker logs pyats-api -f

# Last 100 lines
docker logs pyats-api --tail 100

# With timestamps
docker logs pyats-api --timestamps

# Specific service
docker-compose logs pyats-api -f
```

### Container Information

```bash
# Running containers
docker ps

# All containers
docker ps -a

# Container details
docker inspect pyats-api

# Container stats
docker stats pyats-api

# Container processes
docker top pyats-api
```

### Network Diagnostics

```bash
# From container
docker exec pyats-api ping 192.168.1.1
docker exec pyats-api nc -zv 192.168.1.1 22
docker exec pyats-api curl http://localhost:8000/health

# Container network
docker network inspect bridge
```

### Debug Mode

```bash
# Enable debug logging
docker run -e LOG_LEVEL=DEBUG -p 8000:8000 jeromemassey76/pyats-ro-api:latest

# Or in .env file
LOG_LEVEL=DEBUG
```

---

## Getting Help

If you can't resolve your issue:

1. **Check logs** with DEBUG level
2. **Test manually** (SSH to device, test jumphost)
3. **Search GitHub Issues**: https://github.com/jerome-massey/pyats-ro-api/issues
4. **Create new issue** with:
   - Error message
   - Logs (with sensitive data removed)
   - Steps to reproduce
   - Environment details (Docker version, OS, etc.)

---

## Next Steps

- **[FAQ](FAQ)** - Frequently asked questions
- **[API Reference](API-Reference)** - Complete API documentation
- **[Examples](Examples)** - Usage examples

---

**Navigation**: [← Examples](Examples) | [Home](Home) | [FAQ →](FAQ)

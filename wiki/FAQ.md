# FAQ - Frequently Asked Questions

Common questions and answers about the PyATS Show Command API.

## General Questions

### What is PyATS Show Command API?

A FastAPI-based REST API and MCP server for executing read-only show commands on Cisco network devices using PyATS/Unicon. It provides a simple HTTP interface for network automation without needing testbed files.

### Why use this instead of direct SSH?

- **Standardized Interface**: HTTP/JSON API instead of raw SSH
- **No Testbed Files**: Pass credentials directly in requests
- **Multi-Device Support**: Query multiple devices in one request
- **Pipe Filters**: Built-in support for include/exclude/begin/section
- **Jumphost Support**: Access devices behind bastion hosts
- **AI Integration**: MCP protocol support for AI assistants like Claude
- **Security**: Read-only by design, command validation

### Is this project production-ready?

Yes! The API includes:
- Input validation and sanitization
- Security restrictions (show commands only)
- Docker containerization
- Pre-built images on Docker Hub
- Comprehensive testing
- Production deployment guides

### What's the difference between REST API and MCP?

| Feature | REST API | MCP |
|---------|----------|-----|
| **Protocol** | HTTP/JSON | Model Context Protocol |
| **Use Case** | Scripts, automation | AI assistants |
| **Clients** | curl, Python, etc. | Claude Desktop, MCP clients |
| **Port** | 8000 | 3000 (SSE) or stdio |
| **Discovery** | OpenAPI docs | Auto-discovery |

Both use the same business logic and security model.

---

## Installation Questions

### Should I use Docker Hub or build locally?

**Use Docker Hub for**:
- Production deployments
- Quick testing
- Stable, pre-built images
- Version pinning

**Build locally for**:
- Development
- Custom modifications
- Testing unreleased features

### Which Docker Compose file should I use?

| File | Use When |
|------|----------|
| `docker-compose.prod.yml` | Production, REST API only |
| `docker-compose.mcp.prod.yml` | Production, API + MCP |
| `docker-compose.dev.yml` | Development, hot-reload |
| `docker-compose.mcp.yml` | Development, API + MCP |
| `docker-compose.nginx.yml` | Production with HTTPS |

### Can I run without Docker?

Yes! You can run directly with Python 3.11+:
```bash
pip install -r requirements.txt
python run.py
```

However, Docker is recommended for consistency and ease of deployment.

### What ports need to be open?

- **8000**: REST API (inbound)
- **3000**: MCP SSE (inbound, optional)
- **22**: SSH to devices and jumphost (outbound)

---

## Configuration Questions

### How do I configure the API?

Three methods:
1. **.env file** (recommended for local development)
2. **Environment variables** (recommended for Docker/Kubernetes)
3. **Docker Compose environment section**

See [Configuration](Configuration) for details.

### Do I need a jumphost?

No, jumphost is **optional**. Use it when:
- Devices are behind a bastion host
- Direct access is not available
- Network segmentation requires proxy

Skip jumphost if devices are directly accessible.

### How do I set up a jumphost?

1. Generate SSH key pair
2. Copy public key to jumphost
3. Configure environment variables or per-request
4. Test with `/api/v1/jumphost/test`

See [Jumphost Configuration](Jumphost-Configuration) for step-by-step guide.

### Can I use different jumphosts for different devices?

Yes! You can:
- Set global jumphost via environment variables
- Override per-device in request JSON
- Mix direct and jumphost connections in same request

---

## Usage Questions

### What commands can I execute?

**Only show commands**. For security, configuration commands are blocked.

✅ **Allowed**:
- `show version`
- `show ip interface brief`
- `show running-config`
- `show ip route`

❌ **Blocked**:
- `configure terminal`
- `copy running-config startup-config`
- `reload`
- `write memory`

### Which device OS types are supported?

- **ios** - Cisco IOS
- **iosxe** - Cisco IOS-XE
- **iosxr** - Cisco IOS-XR
- **nxos** - Cisco NX-OS (Nexus)
- **asa** - Cisco ASA (Firewall)

JunOS and other vendors are **not supported** (PyATS limitation).

### Can I execute multiple commands at once?

Yes! In a single request you can:
- Execute multiple commands on one device
- Execute same commands on multiple devices
- Execute different commands on different devices

```json
{
  "devices": [
    {"hostname": "router1", ...},
    {"hostname": "router2", ...}
  ],
  "commands": [
    {"command": "show version"},
    {"command": "show ip interface brief"}
  ]
}
```

### How do I filter command output?

Use pipe options:

```json
{
  "command": "show ip interface brief",
  "pipe": {
    "option": "include",
    "pattern": "up"
  }
}
```

Options: `include`, `exclude`, `begin`, `section`

### Can I save command output to a file?

The API returns JSON. Save it using your client:

**curl**:
```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '...' > output.json
```

**Python**:
```python
result = requests.post(url, json=payload)
with open('output.json', 'w') as f:
    json.dump(result.json(), f, indent=2)
```

---

## Security Questions

### Is it safe to use in production?

Yes, with proper precautions:
- ✅ Only show commands allowed
- ✅ Input validation and sanitization
- ✅ No credential storage
- ✅ Container isolation
- ✅ SSH key-based jumphost auth

**Additional recommendations**:
- Use HTTPS (see [HTTPS Setup](HTTPS-Setup))
- Implement authentication (API keys, OAuth2)
- Network restrictions (firewall, VPN)
- Audit logging
- Regular updates

### Are credentials stored?

**No.** Credentials are:
- Passed per-request
- Used only for that connection
- Not logged or stored
- Discarded after use

### How is command injection prevented?

Multiple layers:
1. **Validation**: Only "show" commands allowed
2. **Sanitization**: 12+ dangerous patterns blocked (`;`, `|`, `&&`, etc.)
3. **OS validation**: Invalid OS types rejected
4. **Pydantic models**: Type and format validation

### Should I expose the API to the internet?

**Not recommended** without additional security:
- Use **authentication** (API keys, OAuth2)
- Use **HTTPS** with valid certificates
- Use **VPN** or private network
- Implement **rate limiting**
- Add **IP whitelisting**
- Enable **audit logging**

### Can I add authentication?

Yes! Options:
1. **Nginx with basic auth**
2. **API Gateway** (AWS API Gateway, Kong, etc.)
3. **Custom middleware** in FastAPI
4. **OAuth2/JWT** implementation

Example with Nginx basic auth:
```nginx
location / {
    auth_basic "PyATS API";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://pyats_api;
}
```

---

## Troubleshooting Questions

### Why can't I connect to my device?

Common causes:
1. **Network connectivity**: Device not reachable
2. **Wrong credentials**: Username/password incorrect
3. **Wrong OS type**: ios vs iosxe vs iosxr
4. **Firewall**: Port 22 blocked
5. **Enable password**: Required but not provided

See [Troubleshooting](Troubleshooting) for detailed diagnostics.

### Commands timeout, what can I do?

Solutions:
1. **Increase timeout**: Default is 30s
```json
{"timeout": 60}
```

2. **Use pipe filters**: Reduce output size
```json
{
  "command": "show running-config",
  "pipe": {"option": "section", "pattern": "interface"}
}
```

3. **Check device**: High CPU or memory usage
4. **Network latency**: Test with ping

### How do I enable debug logging?

Set `LOG_LEVEL` environment variable:

```bash
# Docker
docker run -e LOG_LEVEL=DEBUG ...

# .env file
LOG_LEVEL=DEBUG

# Docker Compose
environment:
  - LOG_LEVEL=DEBUG
```

Then view logs:
```bash
docker logs -f pyats-api
```

### Claude Desktop can't connect to MCP server

Solutions:
1. **Check configuration**: Verify `claude_desktop_config.json`
2. **Restart Claude**: Close and reopen
3. **Check logs**: `~/Library/Logs/Claude/` (macOS)
4. **Test manually**: 
```bash
docker run -i --rm jeromemassey76/pyats-ro-api:latest python mcp_stdio.py
```

See [MCP Integration](MCP-Integration) for detailed setup.

---

## Performance Questions

### How many concurrent requests can it handle?

Depends on:
- **Workers**: Set with `API_WORKERS` (default: 1)
- **Resources**: CPU, memory available
- **Device response time**: How fast devices respond
- **Network latency**: Connection overhead

**Recommendations**:
- Set workers = CPU cores
- Use load balancer for high volume
- Monitor with `docker stats`

### Can I run multiple instances?

Yes! For high availability:
1. **Docker Compose scale**:
```bash
docker-compose up -d --scale pyats-api=3
```

2. **Kubernetes replicas**:
```yaml
spec:
  replicas: 3
```

3. **Load balancer**: Nginx, HAProxy, cloud LB

### How do I optimize performance?

Tips:
1. **Increase workers**: `API_WORKERS=4`
2. **Use pipe filters**: Reduce output
3. **Batch requests**: Multiple devices in one call
4. **Persistent connections**: Reuse API client
5. **Caching**: Cache device info (external)
6. **Resource limits**: Allocate adequate CPU/memory

---

## MCP Questions

### What is MCP?

Model Context Protocol - a standard protocol for AI assistants to interact with external tools and data sources. Developed by Anthropic.

### Do I need MCP if I just want the REST API?

No. MCP is **optional** for AI assistant integration. The REST API works independently.

### Can I use both REST API and MCP?

Yes! They run simultaneously:
- REST API on port 8000
- MCP SSE on port 3000
- MCP stdio on-demand

Both use the same business logic.

### Which MCP transport should I use?

| Transport | Use When |
|-----------|----------|
| **stdio** | Claude Desktop, local AI |
| **SSE** | Remote access, web clients, multiple users |

### Can I use MCP with other AI assistants?

Yes, any MCP-compatible client can connect:
- Claude Desktop (stdio)
- Custom MCP clients (SSE)
- Future MCP-enabled tools

---

## Deployment Questions

### What's the recommended production setup?

```
┌─────────────────┐
│  Load Balancer  │ (Nginx/HAProxy)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│ API 1 │ │ API 2 │ (Multiple instances)
└───┬───┘ └──┬────┘
    └────┬────┘
         │
    ┌────▼────┐
    │Jumphost │ (Optional)
    └────┬────┘
         │
    ┌────▼────┐
    │ Devices │
    └─────────┘
```

Features:
- HTTPS (TLS certificates)
- Authentication (API keys)
- Multiple instances (HA)
- Monitoring (Prometheus/Grafana)
- Logging (centralized)

### Should I use Kubernetes?

**Use Kubernetes for**:
- Enterprise deployments
- High availability requirements
- Auto-scaling needs
- Multi-region deployment

**Use Docker Compose for**:
- Small deployments
- Single server
- Simple setup
- Development/testing

### How do I update to a new version?

**Docker Hub**:
```bash
# Pull latest
docker pull jeromemassey76/pyats-ro-api:latest

# Restart
docker stop pyats-api && docker rm pyats-api
docker run -d -p 8000:8000 --name pyats-api jeromemassey76/pyats-ro-api:latest
```

**Docker Compose**:
```bash
docker-compose pull
docker-compose up -d
```

**Kubernetes**:
```bash
kubectl set image deployment/pyats-api pyats-api=jeromemassey76/pyats-ro-api:latest
```

### How do I backup/restore?

**What to backup**:
- `.env` file (if using)
- SSH private keys
- Custom scripts
- Documentation

**Containerized app has no persistent data** - everything is configured via environment variables.

---

## Integration Questions

### Can I integrate with Ansible?

Yes! Use `uri` module:
```yaml
- name: Execute show commands
  uri:
    url: http://localhost:8000/api/v1/execute
    method: POST
    body_format: json
    body:
      devices:
        - hostname: "{{ inventory_hostname }}"
          username: "{{ ansible_user }}"
          password: "{{ ansible_password }}"
          os: "iosxe"
      commands:
        - command: "show version"
  register: result
```

### Can I use with Terraform?

Yes! Use `http` provider:
```hcl
data "http" "device_info" {
  url    = "http://localhost:8000/api/v1/execute"
  method = "POST"
  request_headers = {
    Content-Type = "application/json"
  }
  request_body = jsonencode({
    devices = [{
      hostname = "192.168.1.1"
      username = "admin"
      password = "cisco123"
      os       = "iosxe"
    }]
    commands = [{ command = "show version" }]
  })
}
```

### Can I use with monitoring systems?

Yes! Examples:
- **Prometheus**: Scrape custom exporter
- **Grafana**: Visualize device data
- **ELK Stack**: Log aggregation
- **Nagios/Zabbix**: External checks

---

## Licensing Questions

### What's the license?

MIT License - free for personal and commercial use.

### Can I modify and distribute?

Yes! MIT License allows:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use

Requirements:
- Include original license
- Include copyright notice

### Can I sell this?

Yes, MIT License allows commercial use. However, please:
- Give credit to original project
- Don't claim it as your own work
- Consider contributing improvements back

---

## Support Questions

### Where do I report bugs?

Create an issue on GitHub:
https://github.com/jerome-massey/pyats-ro-api/issues

Include:
- Error message
- Steps to reproduce
- Environment details
- Logs (sanitized)

### Where do I request features?

GitHub issues with "enhancement" label:
https://github.com/jerome-massey/pyats-ro-api/issues/new

### Is there commercial support?

Currently, support is community-based via:
- GitHub Issues
- GitHub Discussions
- Documentation

For commercial support inquiries, contact the maintainers.

### How can I contribute?

See [Contributing](Contributing) guide for:
- Code contributions
- Documentation improvements
- Bug reports
- Feature requests

---

## Additional Questions?

If your question isn't answered here:

1. Check the [documentation](Home)
2. Search [GitHub Issues](https://github.com/jerome-massey/pyats-ro-api/issues)
3. Create a new issue
4. Join community discussions

---

**Navigation**: [← Troubleshooting](Troubleshooting) | [Home](Home) | [Contributing →](Contributing)

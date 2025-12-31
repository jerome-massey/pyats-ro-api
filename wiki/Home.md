# PyATS Show Command API - Wiki

Welcome to the PyATS Show Command API wiki! This is a comprehensive guide for using, deploying, and contributing to the project.

## 🚀 Quick Links

- **[Getting Started](Getting-Started)** - Installation and first steps
- **[Installation Guide](Installation)** - Detailed installation options
- **[API Reference](API-Reference)** - Complete API documentation
- **[MCP Integration](MCP-Integration)** - Model Context Protocol guide
- **[Deployment Guide](Deployment)** - Production deployment options
- **[Configuration](Configuration)** - Environment and settings
- **[Examples](Examples)** - Usage examples and curl commands
- **[Troubleshooting](Troubleshooting)** - Common issues and solutions
- **[Contributing](Contributing)** - How to contribute
- **[FAQ](FAQ)** - Frequently asked questions

## 📋 Project Overview

The PyATS Show Command API is a FastAPI-based REST API and MCP (Model Context Protocol) server for executing show commands on Cisco network devices using PyATS/Unicon with optional SSH jumphost support.

### Key Features

✅ **Core Functionality**
- Execute show commands on Cisco network devices via PyATS/Unicon
- Support for multiple devices in a single API call
- No testbed file required - pass device credentials directly
- Pipe options support: `include`, `exclude`, `begin`, `section`
- Optional SSH jumphost support with key-based authentication
- Support for Cisco network OS types (IOS, IOS-XE, IOS-XR, NX-OS, ASA)

✅ **Access Methods**
- **REST API** - HTTP/JSON interface on port 8000
- **MCP SSE** - Remote Model Context Protocol via Server-Sent Events on port 3000
- **MCP stdio** - Local MCP for AI assistants (Claude Desktop integration)

✅ **Security Features**
- Command validation - only `show` commands allowed
- Input sanitization - blocks 12+ dangerous patterns
- OS-specific validation - JunOS explicitly rejected with helpful error
- SSH key-based jumphost authentication
- No credential storage - ephemeral per-request
- Container isolation via Docker

### Architecture

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

### Presentation Layer

The project supports three presentation layers that share the same business logic:

```
┌──────────────────────────────────────────────┐
│         Presentation Layer                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ REST API │  │MCP stdio │  │ MCP SSE  │  │
│  │ Port 8000│  │ on-demand│  │ Port 3000│  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼─────────────┼─────────┘
        │             │             │
        └─────────────┴─────────────┘
                      │
        ┌─────────────▼─────────────┐
        │    Business Logic         │
        │  (Shared - Unchanged)     │
        │  - DeviceManager          │
        │  - JumphostManager        │
        │  - Models & Validation    │
        └───────────────────────────┘
```

## 🎯 Use Cases

1. **Network Automation** - Integrate network show commands into automation workflows
2. **Monitoring & Alerting** - Collect device information for monitoring systems
3. **AI-Assisted Network Management** - Use Claude or other AI assistants to query network devices
4. **Multi-Device Queries** - Execute commands across multiple devices in parallel
5. **Secure Remote Access** - Access devices behind jumphosts without VPN

## 📦 Deployment Options

| Option | Description | Best For |
|--------|-------------|----------|
| **Docker Hub** | Pre-built images | Production deployments |
| **Docker Compose** | Local build | Development & testing |
| **Kubernetes** | Container orchestration | Enterprise deployments |
| **Nginx + HTTPS** | Reverse proxy with SSL | Production with HTTPS |
| **Local Python** | No containers | Development without Docker |

## 🛠️ Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **Network Automation**: PyATS/Unicon
- **Protocol**: Model Context Protocol (MCP)
- **SSH**: Paramiko
- **Validation**: Pydantic
- **Containerization**: Docker
- **Web Server**: Uvicorn
- **Reverse Proxy**: Nginx (optional)

## 📚 Documentation Structure

This wiki is organized into the following sections:

### Getting Started
- [Getting Started](Getting-Started) - Quick start guide
- [Installation](Installation) - Installation methods
- [Configuration](Configuration) - Environment setup

### Usage
- [API Reference](API-Reference) - REST API endpoints
- [MCP Integration](MCP-Integration) - MCP server setup
- [Examples](Examples) - Code examples
- [CLI Usage](CLI-Usage) - Command-line examples

### Deployment
- [Deployment Guide](Deployment) - Production deployment
- [Docker Guide](Docker-Guide) - Docker deployment
- [Kubernetes Guide](Kubernetes-Guide) - K8s deployment
- [HTTPS Setup](HTTPS-Setup) - SSL/TLS configuration

### Advanced Topics
- [Jumphost Configuration](Jumphost-Configuration) - SSH jumphost setup
- [Security Best Practices](Security) - Security hardening
- [Performance Tuning](Performance) - Optimization tips
- [Monitoring & Logging](Monitoring) - Observability

### Reference
- [Supported Devices](Supported-Devices) - Compatible OS types
- [Pipe Options](Pipe-Options) - Command filters
- [Error Codes](Error-Codes) - Error reference
- [Troubleshooting](Troubleshooting) - Common issues

### Development
- [Contributing](Contributing) - Contribution guide
- [Development Setup](Development-Setup) - Dev environment
- [Testing](Testing) - Test suite
- [Architecture](Architecture) - Technical architecture

## 🔗 External Resources

- [GitHub Repository](https://github.com/jerome-massey/pyats-ro-api)
- [Docker Hub](https://hub.docker.com/r/jeromemassey76/pyats-ro-api)
- [PyATS Documentation](https://developer.cisco.com/docs/pyats/)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Community

- Report bugs and request features via [GitHub Issues](https://github.com/jerome-massey/pyats-ro-api/issues)
- Contribute code via [Pull Requests](https://github.com/jerome-massey/pyats-ro-api/pulls)
- Follow security guidelines in the [Contributing Guide](Contributing)

---

**Navigation**: [Home](Home) | [Getting Started →](Getting-Started)

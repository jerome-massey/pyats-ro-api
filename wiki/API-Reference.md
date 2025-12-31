# API Reference

Complete reference for all PyATS Show Command API endpoints.

## Base URL

```
http://localhost:8000
```

For production deployments, replace with your actual domain.

## Authentication

Currently, the API does not require authentication for requests. Device credentials are passed per-request.

> **Security Note**: Consider adding authentication in production environments using:
> - API Keys
> - JWT tokens
> - OAuth2
> - Network-level restrictions (firewall, VPN)

---

## Endpoints

### Health Check

Check API health and version.

**Endpoint**: `GET /health`

**Request**:
```bash
curl http://localhost:8000/health
```

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### Root Endpoint

Get API information.

**Endpoint**: `GET /`

**Request**:
```bash
curl http://localhost:8000/
```

**Response**: `200 OK`
```json
{
  "name": "PyATS Show Command API",
  "version": "1.0.0",
  "description": "Execute show commands on network devices via PyATS/Unicon",
  "endpoints": {
    "docs": "/docs",
    "redoc": "/redoc",
    "health": "/health",
    "execute": "/api/v1/execute",
    "jumphost_test": "/api/v1/jumphost/test",
    "supported_os": "/api/v1/supported_os",
    "pipe_options": "/api/v1/pipe_options"
  }
}
```

---

### Execute Show Commands

Execute show commands on one or more network devices.

**Endpoint**: `POST /api/v1/execute`

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "devices": [
    {
      "hostname": "string",
      "port": 22,
      "username": "string",
      "password": "string",
      "os": "ios|iosxe|iosxr|nxos|asa",
      "enable_password": "string",
      "jumphost": {
        "host": "string",
        "port": 22,
        "username": "string",
        "key_path": "string"
      }
    }
  ],
  "commands": [
    {
      "command": "string",
      "pipe": {
        "option": "include|exclude|begin|section",
        "pattern": "string"
      }
    }
  ],
  "use_jumphost": false,
  "timeout": 30
}
```

**Field Descriptions**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `devices` | array | Yes | List of devices to execute commands on |
| `devices[].hostname` | string | Yes | Device IP or hostname |
| `devices[].port` | integer | No | SSH port (default: 22) |
| `devices[].username` | string | Yes | Device SSH username |
| `devices[].password` | string | Yes | Device SSH password |
| `devices[].os` | string | Yes | Device OS type |
| `devices[].enable_password` | string | No | Enable password if required |
| `devices[].jumphost` | object | No | Per-device jumphost config |
| `commands` | array | Yes | List of show commands |
| `commands[].command` | string | Yes | Show command to execute |
| `commands[].pipe` | object | No | Pipe filter options |
| `commands[].pipe.option` | string | No | Filter type |
| `commands[].pipe.pattern` | string | No | Filter pattern |
| `use_jumphost` | boolean | No | Use global jumphost (default: false) |
| `timeout` | integer | No | Command timeout in seconds (default: 30) |

**Supported OS Types**:
- `ios` - Cisco IOS
- `iosxe` - Cisco IOS-XE
- `iosxr` - Cisco IOS-XR
- `nxos` - Cisco NX-OS
- `asa` - Cisco ASA

**Pipe Options**:
- `include` - Include lines matching pattern
- `exclude` - Exclude lines matching pattern
- `begin` - Begin output at pattern
- `section` - Show section matching pattern

**Example Request**:
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
      {
        "command": "show version"
      },
      {
        "command": "show ip interface brief",
        "pipe": {
          "option": "include",
          "pattern": "up"
        }
      }
    ],
    "timeout": 30
  }'
```

**Response**: `200 OK`
```json
{
  "results": [
    {
      "device": "192.168.1.1",
      "success": true,
      "commands": [
        {
          "command": "show version",
          "success": true,
          "output": "Cisco IOS XE Software, Version 16.09.03...",
          "error": null
        },
        {
          "command": "show ip interface brief | include up",
          "success": true,
          "output": "GigabitEthernet1    192.168.1.1     YES NVRAM  up     up",
          "error": null
        }
      ]
    }
  ],
  "summary": {
    "total_devices": 1,
    "successful_devices": 1,
    "failed_devices": 0
  }
}
```

**Error Response**: `422 Unprocessable Entity`
```json
{
  "detail": [
    {
      "loc": ["body", "devices", 0, "os"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

**Error Response**: `400 Bad Request`
```json
{
  "detail": "Only 'show' commands are allowed. Command rejected: configure terminal"
}
```

---

### Test Jumphost Connectivity

Test SSH jumphost connection before executing commands.

**Endpoint**: `POST /api/v1/jumphost/test`

**Request Body**:
```json
{
  "jumphost": {
    "host": "string",
    "port": 22,
    "username": "string",
    "key_path": "string"
  }
}
```

**Example Request**:
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

**Response (Success)**: `200 OK`
```json
{
  "host": "jumphost.example.com",
  "port": 22,
  "username": "jumpuser",
  "success": true,
  "message": "Successfully connected to jumphost jumphost.example.com:22 as user 'jumpuser'",
  "error": null
}
```

**Response (Failure)**: `200 OK`
```json
{
  "host": "jumphost.example.com",
  "port": 22,
  "username": "jumpuser",
  "success": false,
  "message": "Jumphost connection failed: SSH key not found",
  "error": "SSH key not found: /root/.ssh/jumphost_key"
}
```

---

### List Supported OS Types

Get list of supported device operating systems.

**Endpoint**: `GET /api/v1/supported_os`

**Request**:
```bash
curl http://localhost:8000/api/v1/supported_os
```

**Response**: `200 OK`
```json
{
  "supported_os": [
    "ios",
    "iosxe",
    "iosxr",
    "nxos",
    "asa"
  ]
}
```

---

### List Pipe Options

Get list of available pipe filter options.

**Endpoint**: `GET /api/v1/pipe_options`

**Request**:
```bash
curl http://localhost:8000/api/v1/pipe_options
```

**Response**: `200 OK`
```json
{
  "pipe_options": [
    "include",
    "exclude",
    "begin",
    "section"
  ]
}
```

---

## Request Examples

### Single Device, Single Command

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
  "commands": [
    {"command": "show version"}
  ]
}
```

### Multiple Devices, Multiple Commands

```json
{
  "devices": [
    {
      "hostname": "router1.example.com",
      "username": "admin",
      "password": "password1",
      "os": "iosxe"
    },
    {
      "hostname": "switch1.example.com",
      "username": "admin",
      "password": "password2",
      "os": "nxos"
    }
  ],
  "commands": [
    {"command": "show version"},
    {"command": "show ip interface brief"},
    {"command": "show running-config"}
  ]
}
```

### With Pipe Filters

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
  "commands": [
    {
      "command": "show ip interface brief",
      "pipe": {
        "option": "include",
        "pattern": "up"
      }
    },
    {
      "command": "show running-config",
      "pipe": {
        "option": "section",
        "pattern": "interface"
      }
    }
  ]
}
```

### With Global Jumphost

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
  "commands": [
    {"command": "show version"}
  ],
  "use_jumphost": true
}
```

Note: Requires jumphost environment variables to be configured.

### With Per-Device Jumphost

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

### With Enable Password

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
  "commands": [
    {"command": "show running-config"}
  ]
}
```

### With Custom Timeout

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
  "commands": [
    {"command": "show tech-support"}
  ],
  "timeout": 120
}
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| `200` | Success |
| `400` | Bad Request - Invalid command or security violation |
| `422` | Unprocessable Entity - Validation error |
| `500` | Internal Server Error |

---

## Rate Limiting

Currently, there is no built-in rate limiting. Consider implementing:
- Nginx rate limiting
- API gateway
- Application-level rate limiting (Redis)

---

## OpenAPI Specification

Download the OpenAPI (Swagger) specification:

```bash
curl http://localhost:8000/openapi.json > openapi.json
```

---

## Interactive Documentation

Explore and test the API interactively:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Next Steps

- **[Examples](Examples)** - More usage examples
- **[MCP Integration](MCP-Integration)** - Use with AI assistants
- **[Troubleshooting](Troubleshooting)** - Common issues and solutions

---

**Navigation**: [← Installation](Installation) | [Home](Home) | [MCP Integration →](MCP-Integration)

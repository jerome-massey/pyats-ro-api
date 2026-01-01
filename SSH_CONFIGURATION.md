# SSH Configuration and Key Mounting

This guide explains how to configure SSH connections for the PyATS API container, including support for jumphost proxying and network device access.

## Quick Start

### 1. Create SSH Config Files

Create a directory structure with your SSH configurations:

```
ssh_config.d/
  ├── jumphost.conf    # Jumphost configuration
  └── lab_devices.conf # Device routing through jumphost
```

**Example: `ssh_config.d/jumphost.conf`**
```
Host jumphost
    HostName 10.0.0.21
    User cisco
    IdentityFile /root/.ssh/ssh_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

**Example: `ssh_config.d/lab_devices.conf`**
```
Host 10.250.250.*
    ProxyJump jumphost
    User cisco
    IdentityFile /root/.ssh/ssh_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

### 2. Mount in Docker

**Docker Run:**
```powershell
docker run --rm \
  -v ${PWD}/ssh_config.d:/root/.ssh/config.d \
  -v "${PWD}/your_ssh_key:/root/.ssh/ssh_key.mounted:ro" \
  -p 8000:8000 \
  pyats-ro-api:latest python run.py
```

**Docker Compose:**
```yaml
services:
  pyats-api:
    image: pyats-ro-api:latest
    ports:
      - "8000:8000"
    volumes:
      # Mount SSH config directory (writable so entrypoint can fix permissions)
      - ./ssh_config.d:/root/.ssh/config.d
      
      # Mount SSH private key (read-only is fine)
      - ~/.ssh/my_ssh_key:/root/.ssh/ssh_key.mounted:ro
    command: python run.py
```

## Advanced Configuration

### Multiple SSH Keys

If you need multiple SSH keys for different hosts:

**`ssh_config.d/keys.conf`**
```
Host jumphost
    HostName 10.0.0.21
    User cisco
    IdentityFile /root/.ssh/jumphost_key

Host 10.250.250.*
    ProxyJump jumphost
    User cisco
    IdentityFile /root/.ssh/device_key
```

**Docker Mount:**
```yaml
volumes:
  - ./ssh_config.d:/root/.ssh/config.d
  - ~/.ssh/jumphost_key:/root/.ssh/jumphost_key.mounted:ro
  - ~/.ssh/device_key:/root/.ssh/device_key.mounted:ro
```

### Custom SSH Key Name

By default, SSH keys are mounted to `/root/.ssh/ssh_key`. To use a different name:

**Environment Variable:**
```yaml
environment:
  - SSH_KEY_NAME=my_custom_key

volumes:
  - ~/.ssh/my_custom_key:/root/.ssh/my_custom_key.mounted:ro
```

### Custom SSH Config (No Config.d)

If you prefer to mount a single SSH config file instead of using `config.d`:

```yaml
volumes:
  - ./ssh_config:/root/.ssh/config.mounted:ro
  - ~/.ssh/my_key:/root/.ssh/ssh_key.mounted:ro
```

## How It Works

### Entrypoint Process

When the container starts:

1. **Copy SSH keys** - Any `.mounted` files in `/root/.ssh/` are copied and permissions set to 600
2. **Fix permissions** - Config.d directory is set to 700, files to 600 (SSH requires strict permissions)
3. **Create/Include configs** - If no custom config is mounted, a minimal config is created that includes all files in `config.d/`

### SSH Config Hierarchy

The default SSH config includes all files in the `config.d/` directory:

```
/root/.ssh/config:
  Include /root/.ssh/config.d/*
  Host *
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel ERROR
    IdentityFile /root/.ssh/ssh_key
```

Files in `config.d/` are processed in alphabetical order and can override the defaults.

### Jumphost Proxying

When configured with `ProxyJump`, SSH automatically routes connections through the jumphost. This is transparent to the PyATS API - the device connections appear as direct connections but traffic goes through the jumphost.

## Troubleshooting

### SSH Permission Errors

```
Bad owner or permissions on /root/.ssh/config.d/jumphost.conf
```

**Solution:** Mount the `config.d` directory **without** `:ro` flag so the entrypoint can fix permissions:

```yaml
volumes:
  - ./ssh_config.d:/root/.ssh/config.d  # No :ro flag
  - ~/.ssh/my_key:/root/.ssh/ssh_key.mounted:ro
```

### Key Not Found

```
Permission denied (publickey)
```

**Solutions:**
1. Verify key file exists and permissions are 600 in container: `docker exec <container> ls -la /root/.ssh/`
2. Verify SSH config references the correct key path
3. Ensure SSH config has `IdentityFile` set to `/root/.ssh/ssh_key` or your mounted key name

### Config Not Being Read

1. Check that config files are in `/root/.ssh/config.d/`
2. Verify file permissions: `docker exec <container> ls -la /root/.ssh/config.d/`
3. Test SSH config: `docker exec <container> ssh -G hostname` to see resolved config

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SSH_KEY_NAME` | `ssh_key` | Default SSH key name (without extension) |

## See Also

- [Docker Compose Guide](DOCKER_COMPOSE_GUIDE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Examples](examples/)

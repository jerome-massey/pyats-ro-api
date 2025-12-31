#!/bin/bash

# ============================================================================
# DEPRECATED - This file is obsolete as of v0.2.2
# ============================================================================
#
# The jumphost test endpoint and per-device jumphost configuration have been
# removed in v0.2.2. Jumphost routing is now handled transparently via SSH
# config files.
#
# To configure jumphost access in v0.2.2+:
#   1. Configure SSH config file in the container at /root/.ssh/config
#   2. Use ProxyJump directive for target device subnets
#   3. See entrypoint.sh for example configuration
#
# For more information, see the main README.md
#
# ============================================================================

# PyATS Show Command API - Jumphost Testing Examples (DEPRECATED)
# These examples demonstrate the OLD jumphost test endpoint (REMOVED in v0.2.2)

API_URL="http://localhost:8000"

echo "PyATS API - Jumphost Testing Examples"
echo "======================================"
echo ""

# Example 1: Test jumphost with missing SSH key
echo "Example 1: Test jumphost with missing SSH key"
echo "=============================================="
echo ""
echo "Request:"
cat << 'EOF'
curl -X POST http://localhost:8000/api/v1/jumphost/test \
  -H "Content-Type: application/json" \
  -d '{
    "jumphost": {
      "host": "jumphost.example.com",
      "port": 22,
      "username": "jumpuser",
      "key_path": "/home/user/.ssh/id_rsa"
    }
  }'
EOF
echo ""
echo "Response:"
echo '{"host":"jumphost.example.com","port":22,"username":"jumpuser","success":false,"message":"Jumphost connection failed: SSH key not found","error":"SSH key not found: /home/user/.ssh/id_rsa"}'
echo ""
echo ""

# Example 2: Test jumphost with valid config (but unreachable host)
echo "Example 2: Test jumphost with unreachable host"
echo "=============================================="
echo ""
echo "Request:"
cat << 'EOF'
curl -X POST http://localhost:8000/api/v1/jumphost/test \
  -H "Content-Type: application/json" \
  -d '{
    "jumphost": {
      "host": "unreachable-jumphost.internal",
      "port": 22,
      "username": "jumpuser",
      "key_path": "/root/.ssh/jumphost_key"
    }
  }'
EOF
echo ""
echo "Response (in real environment):"
echo '{"host":"unreachable-jumphost.internal","port":22,"username":"jumpuser","success":false,"message":"Jumphost connection failed","error":"[Errno -2] Name or service not known"}'
echo ""
echo ""

# Example 3: Test jumphost validation - invalid port
echo "Example 3: Test jumphost validation - invalid port"
echo "=================================================="
echo ""
echo "Request (port out of range):"
cat << 'EOF'
curl -X POST http://localhost:8000/api/v1/jumphost/test \
  -H "Content-Type: application/json" \
  -d '{
    "jumphost": {
      "host": "jumphost.example.com",
      "port": 99999,
      "username": "jumpuser",
      "key_path": "/root/.ssh/jumphost_key"
    }
  }'
EOF
echo ""
echo "Response:"
echo '{"detail":[{"type":"value_error","loc":["body","jumphost","port"],"msg":"Value error, Port must be between 1 and 65535",...}]}'
echo ""
echo ""

# Example 4: Test jumphost validation - empty username
echo "Example 4: Test jumphost validation - empty username"
echo "==================================================="
echo ""
echo "Request:"
cat << 'EOF'
curl -X POST http://localhost:8000/api/v1/jumphost/test \
  -H "Content-Type: application/json" \
  -d '{
    "jumphost": {
      "host": "jumphost.example.com",
      "port": 22,
      "username": "",
      "key_path": "/root/.ssh/jumphost_key"
    }
  }'
EOF
echo ""
echo "Response:"
echo '{"detail":[{"type":"value_error","loc":["body","jumphost","username"],"msg":"Value error, Username cannot be empty",...}]}'
echo ""
echo ""

# Example 5: Successful jumphost connection
echo "Example 5: Successful jumphost connection (in real environment)"
echo "============================================================="
echo ""
echo "Request (with valid SSH key and reachable jumphost):"
cat << 'EOF'
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
EOF
echo ""
echo "Response (if successful):"
echo '{"host":"jumphost.example.com","port":22,"username":"jumpuser","success":true,"message":"Successfully connected to jumphost jumphost.example.com:22 as user '"'"'jumpuser'"'"'","error":null}'
echo ""
echo ""

# Example 6: Using jumphost test before executing commands
echo "Example 6: Workflow - Test jumphost, then execute commands"
echo "=========================================================="
echo ""
echo "Step 1: Test jumphost configuration"
cat << 'EOF'
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
EOF
echo ""
echo "Step 2: If successful (success=true), execute show commands"
cat << 'EOF'
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [{
      "hostname": "device.internal",
      "username": "admin",
      "password": "password",
      "os": "iosxe",
      "jumphost": {
        "host": "jumphost.example.com",
        "port": 22,
        "username": "jumpuser",
        "key_path": "/root/.ssh/jumphost_key"
      }
    }],
    "commands": [{"command": "show version"}],
    "use_jumphost": false
  }'
EOF
echo ""
echo ""

echo "Use Cases for Jumphost Testing"
echo "=============================="
echo ""
echo "1. Debug SSH key issues"
echo "   - Test if SSH key file exists and is accessible"
echo "   - Get specific error messages about key problems"
echo ""
echo "2. Verify jumphost connectivity"
echo "   - Check if jumphost hostname is resolvable"
echo "   - Verify network reachability to jumphost"
echo "   - Confirm SSH port is open"
echo ""
echo "3. Validate credentials"
echo "   - Confirm username/password combinations"
echo "   - Test different SSH key files"
echo ""
echo "4. Troubleshoot before bulk operations"
echo "   - Test configuration before running show commands on many devices"
echo "   - Avoid failed device connections due to jumphost issues"
echo ""
echo "5. CI/CD pipeline integration"
echo "   - Validate jumphost access in automation workflows"
echo "   - Fail fast if jumphost is unavailable"
echo ""

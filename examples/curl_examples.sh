#!/bin/bash

# Example cURL commands for PyATS Show Command API

API_URL="http://localhost:8000"

echo "PyATS Show Command API - cURL Examples"
echo "========================================"
echo ""

# Example 1: Health Check
echo "1. Health Check"
echo "==============="
echo "curl $API_URL/health"
echo ""
curl -s $API_URL/health | python3 -m json.tool
echo ""
echo ""

# Example 2: Basic show command
echo "2. Basic Show Command (Single Device)"
echo "======================================"
cat << 'EOF'
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
    ]
  }'
EOF
echo ""
echo ""

# Example 3: Multiple commands
echo "3. Multiple Commands"
echo "===================="
cat << 'EOF'
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
      {"command": "show version"},
      {"command": "show ip interface brief"},
      {"command": "show inventory"}
    ]
  }'
EOF
echo ""
echo ""

# Example 4: With pipe include
echo "4. Command with Pipe Include"
echo "============================="
cat << 'EOF'
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
        "command": "show running-config",
        "pipe_option": "include",
        "pipe_value": "interface"
      }
    ]
  }'
EOF
echo ""
echo ""

# Example 5: Multiple devices
echo "5. Multiple Devices"
echo "==================="
cat << 'EOF'
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "hostname": "192.168.1.1",
        "username": "admin",
        "password": "cisco123",
        "os": "iosxe"
      },
      {
        "hostname": "192.168.1.2",
        "username": "admin",
        "password": "cisco123",
        "os": "nxos"
      }
    ],
    "commands": [
      {"command": "show version"}
    ]
  }'
EOF
echo ""
echo ""

# Example 6: With custom timeout
echo "6. With Custom Timeout"
echo "======================"
cat << 'EOF'
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
      {"command": "show tech-support"}
    ],
    "timeout": 120
  }'
EOF
echo ""
echo ""

echo "To run any example, copy and paste the curl command"
echo "Make sure the API server is running: python run.py"

# Examples

Practical examples for using the PyATS Show Command API.

## Table of Contents

- [Basic Examples](#basic-examples)
- [Multiple Devices](#multiple-devices)
- [Pipe Filters](#pipe-filters)
- [Jumphost Examples](#jumphost-examples)
- [Python Client Examples](#python-client-examples)
- [Shell Script Examples](#shell-script-examples)
- [Advanced Use Cases](#advanced-use-cases)

---

## Basic Examples

### Single Device, Single Command

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
    ]
  }'
```

### Single Device, Multiple Commands

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
      {"command": "show version"},
      {"command": "show ip interface brief"},
      {"command": "show ip route summary"}
    ]
  }'
```

### With Enable Password

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### Custom Timeout

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
      {"command": "show tech-support"}
    ],
    "timeout": 120
  }'
```

---

## Multiple Devices

### Same Commands, Multiple Devices

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "hostname": "router1.example.com",
        "username": "admin",
        "password": "password1",
        "os": "iosxe"
      },
      {
        "hostname": "router2.example.com",
        "username": "admin",
        "password": "password2",
        "os": "iosxe"
      },
      {
        "hostname": "switch1.example.com",
        "username": "admin",
        "password": "password3",
        "os": "nxos"
      }
    ],
    "commands": [
      {"command": "show version"},
      {"command": "show ip interface brief"}
    ]
  }'
```

### Different OS Types

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "hostname": "ios-router.example.com",
        "username": "admin",
        "password": "pass1",
        "os": "ios"
      },
      {
        "hostname": "iosxe-router.example.com",
        "username": "admin",
        "password": "pass2",
        "os": "iosxe"
      },
      {
        "hostname": "iosxr-router.example.com",
        "username": "admin",
        "password": "pass3",
        "os": "iosxr"
      },
      {
        "hostname": "nexus-switch.example.com",
        "username": "admin",
        "password": "pass4",
        "os": "nxos"
      },
      {
        "hostname": "firewall.example.com",
        "username": "admin",
        "password": "pass5",
        "os": "asa"
      }
    ],
    "commands": [
      {"command": "show version"}
    ]
  }'
```

---

## Pipe Filters

### Include Filter

Show only lines containing "up":

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
        "command": "show ip interface brief",
        "pipe": {
          "option": "include",
          "pattern": "up"
        }
      }
    ]
  }'
```

### Exclude Filter

Exclude lines containing "down":

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
        "command": "show ip interface brief",
        "pipe": {
          "option": "exclude",
          "pattern": "administratively down"
        }
      }
    ]
  }'
```

### Begin Filter

Start output from first match:

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
        "command": "show running-config",
        "pipe": {
          "option": "begin",
          "pattern": "interface GigabitEthernet"
        }
      }
    ]
  }'
```

### Section Filter

Show configuration section:

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
        "command": "show running-config",
        "pipe": {
          "option": "section",
          "pattern": "router bgp"
        }
      }
    ]
  }'
```

### Multiple Filters

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
      },
      {
        "command": "show ip route",
        "pipe": {
          "option": "exclude",
          "pattern": "variably subnetted"
        }
      }
    ]
  }'
```

---

## Jumphost Examples

### Global Jumphost Configuration

Use global jumphost config (set via environment variables):

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "hostname": "10.0.1.100",
        "username": "admin",
        "password": "cisco123",
        "os": "iosxe"
      }
    ],
    "commands": [
      {"command": "show version"}
    ],
    "use_jumphost": true
  }'
```

### Per-Device Jumphost

Specify jumphost for specific device:

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "hostname": "10.0.1.100",
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
  }'
```

### Test Jumphost Connectivity

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

### Multiple Devices with Different Jumphosts

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "hostname": "10.0.1.100",
        "username": "admin",
        "password": "pass1",
        "os": "iosxe",
        "jumphost": {
          "host": "jumphost1.example.com",
          "port": 22,
          "username": "user1",
          "key_path": "/root/.ssh/key1"
        }
      },
      {
        "hostname": "10.0.2.100",
        "username": "admin",
        "password": "pass2",
        "os": "nxos",
        "jumphost": {
          "host": "jumphost2.example.com",
          "port": 22,
          "username": "user2",
          "key_path": "/root/.ssh/key2"
        }
      }
    ],
    "commands": [
      {"command": "show version"}
    ]
  }'
```

---

## Python Client Examples

### Basic Python Client

```python
import requests
import json

# API endpoint
url = "http://localhost:8000/api/v1/execute"

# Request payload
payload = {
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
        {"command": "show ip interface brief"}
    ]
}

# Make request
response = requests.post(url, json=payload)

# Check response
if response.status_code == 200:
    result = response.json()
    print(json.dumps(result, indent=2))
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

### With Error Handling

```python
import requests
import json

def execute_show_commands(devices, commands, timeout=30):
    """Execute show commands on devices."""
    url = "http://localhost:8000/api/v1/execute"
    
    payload = {
        "devices": devices,
        "commands": commands,
        "timeout": timeout
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API"}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}

# Usage
devices = [
    {
        "hostname": "192.168.1.1",
        "username": "admin",
        "password": "cisco123",
        "os": "iosxe"
    }
]

commands = [
    {"command": "show version"}
]

result = execute_show_commands(devices, commands)
print(json.dumps(result, indent=2))
```

### Batch Processing Multiple Devices

```python
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_device(device_info):
    """Check single device."""
    url = "http://localhost:8000/api/v1/execute"
    
    payload = {
        "devices": [device_info],
        "commands": [
            {"command": "show version"},
            {"command": "show ip interface brief"}
        ],
        "timeout": 30
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return {
            "device": device_info["hostname"],
            "status": "success",
            "result": response.json()
        }
    except Exception as e:
        return {
            "device": device_info["hostname"],
            "status": "failed",
            "error": str(e)
        }

# Device list
devices = [
    {"hostname": "192.168.1.1", "username": "admin", "password": "pass1", "os": "iosxe"},
    {"hostname": "192.168.1.2", "username": "admin", "password": "pass2", "os": "iosxe"},
    {"hostname": "192.168.1.3", "username": "admin", "password": "pass3", "os": "nxos"},
]

# Execute in parallel
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(check_device, device): device for device in devices}
    
    for future in as_completed(futures):
        result = future.result()
        print(f"\nDevice: {result['device']}")
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            print(json.dumps(result['result'], indent=2))
        else:
            print(f"Error: {result['error']}")
```

### Parsing Command Output

```python
import requests
import re

def get_interface_status(hostname, username, password, os="iosxe"):
    """Get interface status and parse output."""
    url = "http://localhost:8000/api/v1/execute"
    
    payload = {
        "devices": [{
            "hostname": hostname,
            "username": username,
            "password": password,
            "os": os
        }],
        "commands": [
            {
                "command": "show ip interface brief",
                "pipe": {
                    "option": "include",
                    "pattern": "up"
                }
            }
        ]
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        output = result["results"][0]["commands"][0]["output"]
        
        # Parse output
        interfaces = []
        for line in output.split('\n'):
            match = re.search(r'(\S+)\s+(\S+)\s+\S+\s+\S+\s+(\S+)\s+(\S+)', line)
            if match:
                interfaces.append({
                    "interface": match.group(1),
                    "ip_address": match.group(2),
                    "status": match.group(3),
                    "protocol": match.group(4)
                })
        
        return interfaces
    else:
        return []

# Usage
interfaces = get_interface_status("192.168.1.1", "admin", "cisco123")
for intf in interfaces:
    print(f"{intf['interface']}: {intf['ip_address']} ({intf['status']}/{intf['protocol']})")
```

---

## Shell Script Examples

### Basic Shell Script

```bash
#!/bin/bash

# execute_command.sh - Execute show commands via API

API_URL="http://localhost:8000/api/v1/execute"
DEVICE_IP="192.168.1.1"
USERNAME="admin"
PASSWORD="cisco123"
OS="iosxe"

# Create JSON payload
PAYLOAD=$(cat <<EOF
{
  "devices": [
    {
      "hostname": "$DEVICE_IP",
      "username": "$USERNAME",
      "password": "$PASSWORD",
      "os": "$OS"
    }
  ],
  "commands": [
    {"command": "show version"},
    {"command": "show ip interface brief"}
  ]
}
EOF
)

# Execute command
RESPONSE=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

# Pretty print response
echo "$RESPONSE" | python3 -m json.tool
```

### Loop Through Multiple Devices

```bash
#!/bin/bash

# check_devices.sh - Check multiple devices

API_URL="http://localhost:8000/api/v1/execute"

# Device list (hostname:username:password:os)
DEVICES=(
  "192.168.1.1:admin:pass1:iosxe"
  "192.168.1.2:admin:pass2:iosxe"
  "192.168.1.3:admin:pass3:nxos"
)

# Loop through devices
for DEVICE in "${DEVICES[@]}"; do
  IFS=':' read -r HOST USER PASS OS <<< "$DEVICE"
  
  echo "Checking $HOST..."
  
  PAYLOAD=$(cat <<EOF
{
  "devices": [{"hostname": "$HOST", "username": "$USER", "password": "$PASS", "os": "$OS"}],
  "commands": [{"command": "show version"}]
}
EOF
)
  
  curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" | python3 -m json.tool
  
  echo "---"
done
```

### Save Output to Files

```bash
#!/bin/bash

# save_outputs.sh - Save command outputs to files

API_URL="http://localhost:8000/api/v1/execute"
OUTPUT_DIR="./outputs"
DEVICE_IP="192.168.1.1"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Get timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Execute commands
PAYLOAD='{
  "devices": [
    {
      "hostname": "'"$DEVICE_IP"'",
      "username": "admin",
      "password": "cisco123",
      "os": "iosxe"
    }
  ],
  "commands": [
    {"command": "show version"},
    {"command": "show running-config"}
  ]
}'

# Get response
RESPONSE=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

# Save raw response
echo "$RESPONSE" > "$OUTPUT_DIR/${DEVICE_IP}_${TIMESTAMP}.json"

# Extract and save individual command outputs
echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for cmd in data['results'][0]['commands']:
    cmd_name = cmd['command'].replace(' ', '_')
    with open('$OUTPUT_DIR/${DEVICE_IP}_${cmd_name}_${TIMESTAMP}.txt', 'w') as f:
        f.write(cmd['output'])
"

echo "Outputs saved to $OUTPUT_DIR/"
```

---

## Advanced Use Cases

### Inventory Check Across Network

```python
import requests
import csv
from datetime import datetime

def inventory_check(devices):
    """Collect inventory information from devices."""
    url = "http://localhost:8000/api/v1/execute"
    
    inventory = []
    
    for device in devices:
        payload = {
            "devices": [device],
            "commands": [
                {"command": "show version"},
                {"command": "show inventory"}
            ]
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                inventory.append({
                    "hostname": device["hostname"],
                    "timestamp": datetime.now().isoformat(),
                    "version": result["results"][0]["commands"][0]["output"],
                    "inventory": result["results"][0]["commands"][1]["output"]
                })
        except Exception as e:
            print(f"Error checking {device['hostname']}: {e}")
    
    return inventory

# Save to CSV
def save_inventory_csv(inventory, filename="inventory.csv"):
    """Save inventory to CSV file."""
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["hostname", "timestamp", "version", "inventory"])
        writer.writeheader()
        writer.writerows(inventory)

# Usage
devices = [
    {"hostname": "router1.example.com", "username": "admin", "password": "pass1", "os": "iosxe"},
    {"hostname": "router2.example.com", "username": "admin", "password": "pass2", "os": "iosxe"}
]

inventory = inventory_check(devices)
save_inventory_csv(inventory)
print(f"Inventory saved with {len(inventory)} devices")
```

---

## Next Steps

- **[API Reference](API-Reference)** - Complete API documentation
- **[MCP Integration](MCP-Integration)** - Use with AI assistants
- **[Troubleshooting](Troubleshooting)** - Common issues

---

**Navigation**: [← MCP Integration](MCP-Integration) | [Home](Home) | [Troubleshooting →](Troubleshooting)

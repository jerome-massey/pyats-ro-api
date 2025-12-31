#!/bin/bash

# Copy and fix permissions for mounted SSH key if it exists
if [ -f "/root/.ssh/jumphost_key.mounted" ]; then
    cp /root/.ssh/jumphost_key.mounted /root/.ssh/jumphost_key
    chmod 600 /root/.ssh/jumphost_key
    echo "SSH key copied and permissions set to 600"
fi

# Create SSH config for jumphost connections
cat > /root/.ssh/config << 'EOF'
# Disable strict host key checking for lab environment
Host *
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel ERROR

# Jumphost configuration
Host jumphost
    HostName 10.0.0.21
    User cisco
    Port 22
    IdentityFile /root/.ssh/jumphost_key

# Route all 10.250.250.* connections through jumphost
Host 10.250.250.*
    ProxyJump jumphost
EOF

chmod 600 /root/.ssh/config
echo "SSH config created"

# Execute the main command
exec "$@"


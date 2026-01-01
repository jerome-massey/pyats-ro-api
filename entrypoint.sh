#!/bin/bash

# Set default SSH key name if not provided
SSH_KEY_NAME=${SSH_KEY_NAME:-ssh_key}

# Copy and fix permissions for any mounted SSH keys
# Supports both specific key name and wildcard for multiple keys
for key_file in /root/.ssh/*.mounted; do
    if [ -f "$key_file" ]; then
        # Get the base name without .mounted extension
        base_name=$(basename "$key_file" .mounted)
        cp "$key_file" "/root/.ssh/$base_name"
        chmod 600 "/root/.ssh/$base_name"
        echo "SSH key $base_name copied and permissions set to 600"
    fi
done

# Also support legacy single key mount via environment variable
if [ -f "/root/.ssh/${SSH_KEY_NAME}.mounted" ]; then
    cp "/root/.ssh/${SSH_KEY_NAME}.mounted" "/root/.ssh/${SSH_KEY_NAME}"
    chmod 600 "/root/.ssh/${SSH_KEY_NAME}"
    echo "SSH key ${SSH_KEY_NAME} copied and permissions set to 600"
fi

# Fix permissions on config files if they exist and are writable
# Note: Mounted read-only config.d directories will stay as-is (SSH can read them)
if [ -d "/root/.ssh/config.d" ] && [ -w "/root/.ssh/config.d" ]; then
    chmod 700 /root/.ssh/config.d
    chmod 600 /root/.ssh/config.d/* 2>/dev/null || true
    echo "Fixed permissions on /root/.ssh/config.d"
fi

# If a custom SSH config is mounted, use it; otherwise create a minimal one
if [ -f "/root/.ssh/config.mounted" ]; then
    cp /root/.ssh/config.mounted /root/.ssh/config
    chmod 600 /root/.ssh/config
    echo "Using mounted SSH config"
else
    # Create config.d directory for additional configs
    mkdir -p /root/.ssh/config.d
    chmod 700 /root/.ssh/config.d
    
    # Create minimal SSH config for security with Include directive
    cat > /root/.ssh/config << 'EOF'
# Include any additional configs from config.d directory
Include /root/.ssh/config.d/*

# Disable strict host key checking for lab environment
Host *
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel ERROR
    IdentityFile /root/.ssh/ssh_key
EOF
    chmod 600 /root/.ssh/config
    echo "Created minimal SSH config with Include directive"
fi

# Execute the main command
exec "$@"


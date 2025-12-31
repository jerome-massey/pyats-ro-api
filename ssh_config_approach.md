# SSH Config File Approach for Jumphost

Create a dynamically generated SSH config file for each connection:

## Implementation:

1. Generate `/tmp/ssh_config_<device>` with:
```
Host target-device
    HostName 10.250.250.1
    User cisco
    ProxyJump cisco@10.0.0.21:22
    IdentityFile /root/.ssh/jumphost_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

2. Pass to Unicon via `ssh_config` or `connect_command` parameter

3. Clean up temp file after connection

## Pros:
- SSH config is standard and well-tested
- Works with all SSH tools including Unicon
- Most reliable approach

## Cons:
- Need to manage temp files
- May need to customize Unicon's connection class

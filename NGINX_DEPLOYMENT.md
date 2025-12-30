# Nginx HTTPS Deployment

This directory contains configuration for deploying the PyATS API with Nginx reverse proxy and HTTPS.

## Quick Start

### 1. Generate SSL Certificates

**Option A: Self-Signed (Development/Testing)**
```bash
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem \
  -subj "/CN=localhost"
```

**Option B: Let's Encrypt (Production)**
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificates (requires domain and port 80 access)
sudo certbot certonly --standalone \
  -d api.yourdomain.com \
  -d mcp.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem
sudo chmod 644 ssl/*.pem
```

### 2. Configure Domains

Edit `nginx.conf` and replace:
- `api.yourdomain.com` with your REST API domain
- `mcp.yourdomain.com` with your MCP SSE domain

Or use the same domain with different paths.

### 3. Start Services

```bash
# Build the image first
docker build -t pyats-unified:latest .

# Create logs directory
mkdir -p logs/nginx logs/api logs/mcp

# Start all services with Nginx
docker-compose -f docker-compose.nginx.yml up -d

# Check status
docker-compose -f docker-compose.nginx.yml ps

# View logs
docker-compose -f docker-compose.nginx.yml logs -f nginx
```

### 4. Test HTTPS

```bash
# REST API
curl -k https://localhost/health

# MCP SSE
curl -k https://localhost:3000/health

# Or with domain names (update /etc/hosts if testing locally)
curl https://api.yourdomain.com/health
curl https://mcp.yourdomain.com/health
```

## Configuration

### Nginx Settings

The `nginx.conf` includes:
- **TLS 1.2 and 1.3** - Modern encryption
- **Security headers** - HSTS, X-Frame-Options, etc.
- **HTTP to HTTPS redirect** - Force secure connections
- **SSE optimization** - Special settings for MCP streaming
- **Upstream load balancing** - Ready for multiple backend instances

### SSL/TLS Best Practices

For production:
1. Use real certificates from Let's Encrypt or a CA
2. Enable OCSP stapling
3. Use strong cipher suites
4. Implement certificate pinning (optional)
5. Set up auto-renewal for Let's Encrypt

### Rate Limiting (Optional)

Add to `nginx.conf` inside `http` block:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=mcp_limit:10m rate=5r/s;

# Then in location blocks:
location / {
    limit_req zone=api_limit burst=20;
    # ... rest of config
}
```

## Advanced: Single Domain with Paths

If you prefer one domain, edit `nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # REST API at /api
    location /api {
        rewrite ^/api(.*)$ $1 break;
        proxy_pass http://pyats_api;
        # ... rest of config
    }
    
    # MCP SSE at /mcp
    location /mcp {
        rewrite ^/mcp(.*)$ $1 break;
        proxy_pass http://pyats_mcp;
        # ... rest of config with SSE settings
    }
}
```

## Troubleshooting

**Certificate errors:**
```bash
# Check certificate
openssl x509 -in ssl/cert.pem -text -noout

# Verify nginx config
docker exec pyats-nginx nginx -t
```

**Connection issues:**
```bash
# Check nginx logs
docker logs pyats-nginx

# Check if ports are accessible
sudo netstat -tlnp | grep -E '80|443'
```

**Backend connection errors:**
```bash
# Test backend directly
docker exec -it pyats-nginx wget -O- http://pyats-api:8000/health
docker exec -it pyats-nginx wget -O- http://pyats-mcp-sse:3000/health
```

## Security Recommendations

1. **Keep certificates secure**: Restrict ssl/ directory permissions
2. **Use strong passwords**: If using password-protected keys
3. **Enable fail2ban**: Protect against brute force
4. **Monitor logs**: Set up log aggregation
5. **Update regularly**: Keep nginx and SSL libraries updated
6. **Use WAF**: Consider adding ModSecurity for additional protection

## Let's Encrypt Auto-Renewal

Add to crontab:
```bash
# Renew certificates monthly
0 0 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/yourdomain.com/*.pem /path/to/ssl/ && docker-compose -f docker-compose.nginx.yml restart nginx
```

# Docker Hub Publishing - Summary of Changes

## Overview

Automated Docker Hub publishing has been configured for the pyats-ro-api project. This allows users to pull pre-built images instead of building locally.

## What Was Added

### 1. GitHub Actions Workflow
**File**: [.github/workflows/docker-publish.yml](.github/workflows/docker-publish.yml)

- Automatically builds and pushes images when you create a GitHub release
- Creates multiple tags: `latest`, `v1.0.0`, `1.0`, `1`
- Supports multi-architecture builds (AMD64 and ARM64)
- Updates Docker Hub description from README.md

### 2. Production Docker Compose Files

#### REST API Only
**File**: [docker-compose.prod.yml](docker-compose.prod.yml)
- Uses published image: `jeromemassey76/pyats-ro-api:latest`
- Simple single-service deployment

#### API + MCP Services
**File**: [docker-compose.mcp.prod.yml](docker-compose.mcp.prod.yml)
- Uses published image for all services
- Runs: REST API (8000), MCP SSE (3000), MCP stdio (on-demand)

### 3. Documentation

#### Docker Hub Deployment Guide
**File**: [DOCKER_HUB.md](DOCKER_HUB.md)
- Complete guide for using published images
- Quick start examples
- Configuration options
- Version pinning strategies
- Troubleshooting

#### GitHub Actions Setup Guide
**File**: [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)
- Step-by-step setup instructions
- How to create Docker Hub access tokens
- How to configure GitHub secrets
- How to create releases
- Troubleshooting

#### README Updates
**File**: [README.md](README.md)
- Added Docker Hub as Option 1 (recommended for production)
- Reorganized installation options
- Added Docker Hub badge
- Simplified deployment instructions

## How It Works

### For End Users (Production)

**Simple deployment:**
```bash
# Pull and run
docker pull jeromemassey76/pyats-ro-api:latest
docker run -d -p 8000:8000 jeromemassey76/pyats-ro-api:latest
```

**Or using compose:**
```bash
curl -O https://raw.githubusercontent.com/jerome-massey/pyats-ro-api/main/docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d
```

**Multi-service (API + MCP):**
```bash
curl -O https://raw.githubusercontent.com/jerome-massey/pyats-ro-api/main/docker-compose.mcp.prod.yml
docker-compose -f docker-compose.mcp.prod.yml up -d
```

### For Developers

**Development (local build):**
```bash
# Still use existing dev compose files
docker-compose -f docker-compose.dev.yml up
docker-compose -f docker-compose.mcp.yml up -d
```

### For Releases

**When you create a GitHub release:**
1. Tag a new version (e.g., `v1.0.0`)
2. Create release on GitHub
3. GitHub Actions automatically:
   - Builds Docker image
   - Pushes to Docker Hub with multiple tags
   - Updates repository description

## File Structure

```
pyats-ro-api/
├── .github/
│   └── workflows/
│       └── docker-publish.yml          # NEW - GitHub Actions workflow
├── docker-compose.yml                   # Existing - local build
├── docker-compose.dev.yml              # Existing - development
├── docker-compose.mcp.yml              # Existing - local build with MCP
├── docker-compose.prod.yml             # NEW - production (Docker Hub)
├── docker-compose.mcp.prod.yml         # NEW - production MCP (Docker Hub)
├── docker-compose.nginx.yml            # Existing - HTTPS setup
├── Dockerfile                          # Existing - production image
├── Dockerfile.dev                      # Existing - development image
├── README.md                           # UPDATED - Docker Hub instructions
├── DOCKER_HUB.md                       # NEW - Docker Hub guide
├── GITHUB_ACTIONS_SETUP.md             # NEW - Setup instructions
└── ... (other files)
```

## Next Steps

### 1. Configure GitHub Secrets (Required)

Before publishing works, you need to:

1. **Create Docker Hub Access Token**:
   - Login to hub.docker.com
   - Account Settings → Security → New Access Token
   - Name: `github-actions-pyats-api`
   - Copy the token

2. **Add GitHub Secrets**:
   - Go to: github.com/jerome-massey/pyats-ro-api/settings/secrets/actions
   - Add `DOCKERHUB_USERNAME` = `jeromemassey76`
   - Add `DOCKERHUB_TOKEN` = (paste token from step 1)

See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) for detailed instructions.

### 2. Create First Release

```bash
# Make sure everything is committed
git add .
git commit -m "Add Docker Hub publishing support"
git push

# Create and push tag
git tag -a v1.0.0 -m "Initial Docker Hub release"
git push origin v1.0.0

# Then on GitHub: Releases → Create release using v1.0.0 tag
```

### 3. Verify Publication

After creating the release:
1. Check GitHub Actions tab for build progress
2. Check hub.docker.com/r/jeromemassey76/pyats-ro-api for image
3. Test: `docker pull jeromemassey76/pyats-ro-api:latest`

## Benefits

### For Users
- ✅ No need to build locally (saves time)
- ✅ Pre-tested images
- ✅ Easy version pinning
- ✅ Multi-architecture support (AMD64, ARM64)
- ✅ Simple one-command deployment

### For Project
- ✅ Professional distribution
- ✅ Automated releases
- ✅ Version control
- ✅ Easier for users to try
- ✅ Standard Docker workflow

## Usage Examples

### REST API Only
```bash
# Production - from Docker Hub
docker-compose -f docker-compose.prod.yml up -d

# Development - local build
docker-compose -f docker-compose.dev.yml up
```

### API + MCP
```bash
# Production - from Docker Hub
docker-compose -f docker-compose.mcp.prod.yml up -d

# Development - local build
docker-compose -f docker-compose.mcp.yml up -d
```

### Direct Docker Run
```bash
# REST API
docker run -d -p 8000:8000 jeromemassey76/pyats-ro-api:latest

# MCP SSE
docker run -d -p 3000:3000 jeromemassey76/pyats-ro-api:latest python mcp_sse.py

# MCP stdio
docker run -it jeromemassey76/pyats-ro-api:latest python mcp_stdio.py
```

## Backward Compatibility

All existing workflows continue to work:
- ✅ `docker-compose.yml` - unchanged
- ✅ `docker-compose.dev.yml` - unchanged
- ✅ `docker-compose.mcp.yml` - unchanged
- ✅ Local builds still work
- ✅ Development workflow unchanged

New production files are additions, not replacements.

## Questions?

- See [DOCKER_HUB.md](DOCKER_HUB.md) for usage
- See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) for setup
- See [README.md](README.md) for general documentation

# GitHub Actions Setup for Docker Hub Publishing

This guide explains how to set up automated Docker image publishing to Docker Hub using GitHub Actions.

## Prerequisites

1. **Docker Hub Account**: You need a Docker Hub account
   - Username: `jeromemassey76`
   - Repository will be: `jeromemassey76/pyats-ro-api`

2. **Docker Hub Access Token**: Required for GitHub Actions to push images

## Step 1: Create Docker Hub Access Token

1. Log in to [Docker Hub](https://hub.docker.com/)
2. Click on your username → **Account Settings**
3. Go to **Security** → **New Access Token**
4. Name it: `github-actions-pyats-api`
5. Set permissions: **Read, Write, Delete**
6. Click **Generate**
7. **Copy the token immediately** (you won't see it again!)

## Step 2: Add Secrets to GitHub Repository

1. Go to your GitHub repository: `https://github.com/jerome-massey/pyats-ro-api`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these two secrets:

### Secret 1: DOCKERHUB_USERNAME
- **Name**: `DOCKERHUB_USERNAME`
- **Secret**: `jeromemassey76`

### Secret 2: DOCKERHUB_TOKEN
- **Name**: `DOCKERHUB_TOKEN`
- **Secret**: (paste the Docker Hub access token you copied in Step 1)

## Step 3: Verify Workflow File

The workflow file has been created at [.github/workflows/docker-publish.yml](.github/workflows/docker-publish.yml).

It will automatically:
- Build the Docker image when you create a GitHub release
- Tag it with version numbers (e.g., `v1.0.0`, `1.0`, `1`, `latest`)
- Push to Docker Hub
- Support both AMD64 and ARM64 architectures
- Update the Docker Hub description from README.md

## Step 4: Create Your First Release

### Option A: Via GitHub Web Interface

1. Go to your repository on GitHub
2. Click **Releases** → **Create a new release**
3. Click **Choose a tag** and type a version (e.g., `v1.0.0`)
4. Click **Create new tag: v1.0.0 on publish**
5. Add a release title: `v1.0.0 - Initial Docker Hub Release`
6. Add release notes describing the features
7. Click **Publish release**

### Option B: Via Git Command Line

```bash
# Make sure you're on main branch and everything is committed
git checkout main
git pull

# Create and push a tag
git tag -a v1.0.0 -m "Initial release with Docker Hub support"
git push origin v1.0.0

# Then create the release on GitHub web interface using this tag
```

## Step 5: Monitor the Build

After creating the release:

1. Go to **Actions** tab in your GitHub repository
2. You should see a workflow run called "Docker Publish"
3. Click on it to see the build progress
4. Wait for all steps to complete (usually 5-10 minutes)

## Step 6: Verify on Docker Hub

1. Go to https://hub.docker.com/r/jeromemassey76/pyats-ro-api
2. You should see your image with tags:
   - `latest`
   - `v1.0.0`
   - `1.0`
   - `1`

## Step 7: Test the Published Image

```bash
# Pull and test the image
docker pull jeromemassey76/pyats-ro-api:latest
docker run -d -p 8000:8000 --name pyats-test jeromemassey76/pyats-ro-api:latest

# Wait a few seconds, then test
curl http://localhost:8000/health

# Clean up
docker stop pyats-test
docker rm pyats-test
```

## Future Releases

For subsequent releases:

1. Make your code changes and commit them
2. Create a new release (e.g., `v1.1.0`, `v1.2.0`, etc.)
3. GitHub Actions will automatically build and push to Docker Hub

### Version Tagging Strategy

Follow [Semantic Versioning](https://semver.org/):
- **v1.0.0** - Initial release
- **v1.0.1** - Patch (bug fixes)
- **v1.1.0** - Minor (new features, backward compatible)
- **v2.0.0** - Major (breaking changes)

Each release automatically creates these Docker tags:
- `v1.2.3` - Exact version
- `1.2` - Major.minor (auto-updates with patches)
- `1` - Major version (auto-updates with minor/patches)
- `latest` - Latest release

## Troubleshooting

### Build Fails: "denied: requested access to the resource is denied"

**Solution**: Check your Docker Hub credentials
1. Verify `DOCKERHUB_USERNAME` matches your Docker Hub username exactly
2. Verify `DOCKERHUB_TOKEN` is a valid access token
3. Regenerate token if needed and update the GitHub secret

### Build Fails: "repository does not exist"

**Solution**: Create the repository on Docker Hub first
1. Go to https://hub.docker.com/
2. Click **Create Repository**
3. Name: `pyats-ro-api`
4. Visibility: Public
5. Click **Create**

### Build Succeeds but No Tags Appear

**Solution**: Check you created a proper release, not just a tag
- Tags alone don't trigger the workflow
- You must create a GitHub Release (via Releases page)

### Want to Manually Trigger a Build

The workflow includes `workflow_dispatch` for manual triggers:
1. Go to **Actions** tab
2. Select "Docker Publish" workflow
3. Click **Run workflow**
4. Select branch and click **Run workflow**

## Manual Testing Before Release

Test the Docker build locally before creating a release:

```bash
# Build with the same context as CI
docker build -t jeromemassey76/pyats-ro-api:test .

# Test the image
docker run -d -p 8000:8000 --name test-api jeromemassey76/pyats-ro-api:test
curl http://localhost:8000/health

# Clean up
docker stop test-api
docker rm test-api
docker rmi jeromemassey76/pyats-ro-api:test
```

## Security Best Practices

1. **Never commit tokens**: Keep tokens in GitHub Secrets only
2. **Rotate tokens regularly**: Create new access tokens every 6-12 months
3. **Use read-only tokens for pulling**: Only use read/write tokens for CI/CD
4. **Monitor Docker Hub**: Check activity log for unauthorized access

## Additional Configuration

### Make Repository Public

Your Docker Hub repository should be public for easy access:
1. Go to your repository on Docker Hub
2. Settings → Make public

### Add Repository Description

The workflow automatically updates the description from README.md, but you can also:
1. Edit short description on Docker Hub
2. Update README.md in GitHub (syncs automatically on next release)

## Support

- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Docker Hub Docs**: https://docs.docker.com/docker-hub/
- **Issues**: https://github.com/jerome-massey/pyats-ro-api/issues

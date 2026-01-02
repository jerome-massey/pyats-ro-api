# Git Workflow Quick Reference

**Project:** PyATS Read-Only API  
**For:** Developers and AI assistants working on features

---

## 🚀 Initial Setup (One Time)

```bash
# Clone the repository
git clone https://github.com/jerome-massey/pyats-ro-api.git
cd pyats-ro-api

# Create develop branch (if it doesn't exist)
git checkout -b develop
git push -u origin develop

# Set up local environment
cp .env.example .env
# Edit .env with your settings
```

---

## 🌳 Starting a New Feature

### 1. Update Your Local Repository
```bash
# Make sure you're on develop and it's up to date
git checkout develop
git pull origin develop
```

### 2. Create Feature Branch
```bash
# Branch naming: feature/descriptive-name
git checkout -b feature/rate-limiting

# Or for bug fixes:
git checkout -b fix/connection-timeout

# Or for documentation:
git checkout -b docs/api-examples
```

### 3. Make Changes
```bash
# Make your code changes
# Save files frequently

# Check what changed
git status
git diff

# Stage changes
git add app/config.py
git add requirements.txt

# Or stage everything
git add .

# Commit with descriptive message
git commit -m "feat: add rate limiting configuration to settings"

# Continue working... commit frequently!
git commit -m "feat: implement rate limiter middleware"
git commit -m "test: add rate limiting tests"
git commit -m "docs: update README with rate limiting info"
```

---

## 💾 Commit Message Guide

### Format
```
<type>: <description>

[optional body]

[optional footer]
```

### Types
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `test:` - Adding or updating tests
- `refactor:` - Code change that neither fixes bug nor adds feature
- `chore:` - Changes to build, dependencies, or tooling
- `perf:` - Performance improvement
- `style:` - Formatting, missing semicolons, etc.

### Examples
```bash
# Good ✅
git commit -m "feat: add rate limiting middleware with slowapi"
git commit -m "fix: handle connection timeout in device manager"
git commit -m "docs: add configuration examples to README"
git commit -m "test: add mock tests for device connection"

# Too vague ❌
git commit -m "update code"
git commit -m "fixes"
git commit -m "changes"
```

### Multi-line Commits (for complex changes)
```bash
git commit -m "feat: implement parallel device processing

- Add asyncio semaphore for concurrency control
- Configure max concurrent devices via settings
- Add error isolation per device
- Update tests for async processing

Closes #23"
```

---

## 🔄 Syncing with Remote

### Push Your Branch
```bash
# First push of new branch
git push -u origin feature/rate-limiting

# Subsequent pushes
git push
```

### Keep Feature Branch Updated
```bash
# If develop branch has new changes while you're working
git checkout develop
git pull origin develop

git checkout feature/rate-limiting
git merge develop

# Or use rebase for cleaner history
git rebase develop
```

---

## 🔀 Merging Your Feature

### Option 1: Via GitHub Pull Request (Recommended)
```bash
# Push your branch
git push origin feature/rate-limiting

# Go to GitHub.com
# Click "Compare & pull request"
# Set: feature/rate-limiting → develop
# Fill out PR template
# Request review (or self-review for solo work)
# Merge when tests pass
```

### Option 2: Local Merge (Quick for solo work)
```bash
# Make sure feature is committed
git checkout feature/rate-limiting
git status  # Should be clean

# Switch to develop and merge
git checkout develop
git merge feature/rate-limiting

# Push to remote
git push origin develop

# Delete feature branch (optional)
git branch -d feature/rate-limiting
git push origin --delete feature/rate-limiting
```

---

## 📦 Creating a Release

### Prepare Release
```bash
# Make sure develop is ready
git checkout develop
git pull origin develop

# Run all tests
pytest

# Update version in files
# - app/main.py (version="0.4.0")
# - docker files
# - README.md

# Commit version bump
git commit -am "chore: bump version to 0.4.0"
git push origin develop
```

### Merge to Main and Tag
```bash
# Merge develop to main
git checkout main
git pull origin main
git merge develop

# Create tag
git tag -a v0.4.0 -m "Release version 0.4.0 - Production Ready

Features:
- Rate limiting
- Enhanced configuration
- Request ID tracking
- Improved documentation"

# Push with tags
git push origin main
git push origin v0.4.0
```

### Build and Push Docker Image
```bash
# Build with version tag
docker build -t jeromemassey76/pyats-ro-api:0.4.0 .
docker build -t jeromemassey76/pyats-ro-api:latest .

# Push to Docker Hub
docker push jeromemassey76/pyats-ro-api:0.4.0
docker push jeromemassey76/pyats-ro-api:latest
```

---

## 🆘 Common Scenarios

### Scenario: Made changes on wrong branch
```bash
# You're on main/develop and made changes (not committed)
git stash save "WIP: rate limiting feature"

# Create proper branch
git checkout -b feature/rate-limiting

# Apply changes
git stash pop
git add .
git commit -m "feat: add rate limiting"
```

### Scenario: Need to undo last commit
```bash
# Keep changes, undo commit
git reset --soft HEAD~1

# Remove changes completely
git reset --hard HEAD~1
```

### Scenario: Want to see what changed
```bash
# See unstaged changes
git diff

# See staged changes
git diff --staged

# See changes in specific file
git diff app/main.py

# Compare branches
git diff develop feature/rate-limiting
```

### Scenario: Merge conflict
```bash
# After git merge or git pull
# Git will mark conflicts in files

# Open conflicted files, look for:
<<<<<<< HEAD
your changes
=======
incoming changes
>>>>>>> feature/rate-limiting

# Edit to keep what you want
# Remove conflict markers

# Mark as resolved
git add app/main.py

# Continue merge
git commit
```

### Scenario: Want to update feature from develop
```bash
# You're on feature/rate-limiting
# develop has new commits you want

git checkout develop
git pull origin develop

git checkout feature/rate-limiting
git merge develop

# Or for cleaner history:
git rebase develop

# If conflicts, resolve then:
git rebase --continue
```

---

## 🔍 Useful Commands

### Check Status
```bash
# What's changed?
git status

# What commits are on this branch?
git log --oneline

# Pretty log with graph
git log --oneline --graph --all --decorate

# Who changed this line?
git blame app/main.py
```

### Branch Management
```bash
# List all branches
git branch -a

# Delete local branch
git branch -d feature/old-feature

# Delete remote branch
git push origin --delete feature/old-feature

# Rename current branch
git branch -m new-branch-name
```

### Cleaning Up
```bash
# Remove untracked files (be careful!)
git clean -n  # Preview what will be deleted
git clean -f  # Actually delete

# Discard changes in file
git checkout -- app/main.py

# Discard all local changes
git reset --hard HEAD
```

---

## 📋 Daily Workflow Checklist

### Starting Your Day
- [ ] `git checkout develop`
- [ ] `git pull origin develop`
- [ ] Create/checkout feature branch
- [ ] Review roadmap for feature requirements

### During Development
- [ ] Make small, logical changes
- [ ] Commit frequently with clear messages
- [ ] Run tests after changes
- [ ] Push to remote regularly

### Ending Your Day
- [ ] `git status` - anything uncommitted?
- [ ] Commit work in progress
- [ ] `git push origin feature/your-feature`
- [ ] Update TODO list for tomorrow

### Finishing a Feature
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Code reviewed (self or peer)
- [ ] Committed with clear messages
- [ ] Pushed to remote
- [ ] Create PR or merge to develop

---

## 🤖 For AI Assistants

When working with git, always:
1. Check current branch: `git branch`
2. Verify clean state: `git status`
3. Pull latest before starting: `git pull`
4. Create feature branch for new work
5. Commit after each logical change
6. Use descriptive commit messages
7. Don't commit to main directly

Example session:
```bash
# Check where we are
git branch
git status

# Create feature branch
git checkout -b feature/rate-limiting

# After implementing code
git add app/config.py requirements.txt
git commit -m "feat: add rate limiting configuration"

# After adding tests
git add tests/test_rate_limiting.py
git commit -m "test: add rate limiting tests"

# Push when ready
git push -u origin feature/rate-limiting
```

---

## 📚 Learn More

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Branch Strategy](https://nvie.com/posts/a-successful-git-branching-model/)

---

**Remember:** Commit early, commit often, push regularly!

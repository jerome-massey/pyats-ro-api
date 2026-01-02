# Feature Implementation TODO Template

**Copy this template when starting a new feature**

---

## Feature: [FEATURE_NAME]
**Version:** v0.X.0  
**Branch:** feature/[feature-name]  
**Started:** [DATE]  
**Roadmap Reference:** Phase X.Y in DEVELOPMENT_ROADMAP.md

---

## Pre-Implementation Checklist
- [ ] Read roadmap section for this feature
- [ ] Understand dependencies (what needs to be done first?)
- [ ] Create feature branch from develop
- [ ] Review existing code patterns
- [ ] Identify files that need changes

---

## Implementation Steps

### Phase 1: Setup
- [ ] Update requirements.txt (if needed)
- [ ] Update app/config.py (if adding settings)
- [ ] Update .env.example (if adding env vars)
- [ ] Create test fixtures (if needed)

### Phase 2: Core Implementation
- [ ] [Specific task 1]
- [ ] [Specific task 2]
- [ ] [Specific task 3]

### Phase 3: Testing
- [ ] Write unit tests
- [ ] Write integration tests (if applicable)
- [ ] Run test suite: `pytest`
- [ ] Check test coverage: `pytest --cov=app`
- [ ] Manual testing with Docker
- [ ] Test error conditions

### Phase 4: Documentation
- [ ] Update docstrings in code
- [ ] Update README.md
- [ ] Update OpenAPI examples (if API changes)
- [ ] Update relevant wiki pages
- [ ] Add CHANGELOG.md entry

### Phase 5: Code Review
- [ ] Self-review all changes
- [ ] Check for security issues
- [ ] Verify no breaking changes
- [ ] Clean up debug code/comments
- [ ] Ensure code follows project style

---

## Files Modified
- [ ] `app/main.py` - [what changed]
- [ ] `app/config.py` - [what changed]
- [ ] `requirements.txt` - [what added]
- [ ] `tests/test_[feature].py` - [what added]
- [ ] `README.md` - [what updated]

---

## Testing Notes

### Test Commands
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_[feature].py

# Run with coverage
pytest --cov=app --cov-report=html

# Run only unit tests (fast)
pytest -m "not integration"
```

### Manual Testing
```bash
# Build Docker image
docker build -t pyats-api-test .

# Run container
docker run -d -p 8000:8000 pyats-api-test

# Test endpoint
curl http://localhost:8000/health

# Check logs
docker logs [container-id]
```

---

## Git Workflow

### Commits Made
```bash
# List your commits for reference
git log --oneline feature/[feature-name]

# Example commits:
# feat: add [feature] configuration
# feat: implement [feature] middleware
# test: add [feature] tests
# docs: update README with [feature] info
```

### Ready to Merge?
```bash
# Ensure all tests pass
pytest

# Ensure clean commit history
git log --oneline

# Push to remote
git push origin feature/[feature-name]

# Create PR or merge to develop
git checkout develop
git merge feature/[feature-name]
git push origin develop
```

---

## Challenges & Solutions

### Challenge 1: [Problem Description]
**Solution:** [How you solved it]

### Challenge 2: [Problem Description]
**Solution:** [How you solved it]

---

## AI Collaboration Notes

### Useful Prompts
```
1. "Review the implementation of [feature] and check for issues"

2. "Write tests for [specific function] in [feature]"

3. "Help me debug this error: [error message]"

4. "Review my commits before I merge to develop"
```

### Context to Provide AI
- Current file contents
- Error messages (full stack trace)
- What you've already tried
- Specific roadmap section

---

## Completion Checklist

Before marking feature as DONE:
- [ ] All implementation steps completed
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] No breaking changes
- [ ] Feature works in Docker
- [ ] Committed with clear messages
- [ ] Pushed to remote
- [ ] Merged to develop (or PR created)
- [ ] TODO updated in roadmap

---

## Notes & Ideas

[Free-form notes about the implementation, things to remember, future improvements, etc.]

---

**Status:** ⏳ In Progress | ✅ Complete | 🚫 Blocked
**Blocked By:** [If blocked, what's blocking it?]
**Estimated Completion:** [Date]
**Actual Completion:** [Date]

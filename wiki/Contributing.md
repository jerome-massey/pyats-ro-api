# Contributing

Thank you for considering contributing to the PyATS Show Command API! This guide will help you get started.

## Code of Conduct

Please be respectful and professional in all issues and pull request comments. We're building a helpful community of network automation enthusiasts.

## Ways to Contribute

### 1. Report Bugs

Found a bug? Please create an issue on GitHub with:
- Clear description of the problem
- Steps to reproduce
- Expected behavior vs actual behavior
- Environment details (Docker version, OS, etc.)
- Relevant logs (with sensitive data removed)

### 2. Suggest Features

Have an idea? Create an issue tagged with "enhancement":
- Describe the feature
- Explain the use case
- Provide examples if possible

### 3. Improve Documentation

Documentation improvements are always welcome:
- Fix typos
- Add examples
- Clarify confusing sections
- Add missing information

### 4. Submit Code

Contributions to code are welcome! See below for the development workflow.

---

## Development Setup

### Prerequisites

- Git
- Docker and Docker Compose
- Python 3.11+ (for local development)
- Text editor or IDE

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
```bash
git clone https://github.com/YOUR-USERNAME/pyats-ro-api.git
cd pyats-ro-api
```

3. Add upstream remote:
```bash
git remote add upstream https://github.com/jerome-massey/pyats-ro-api.git
```

4. Create a branch:
```bash
git checkout -b feat/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Development Environment

**Using Docker (Recommended)**:
```bash
# Start development container with hot-reload
make dev

# Or using docker-compose
docker-compose -f docker-compose.dev.yml up
```

**Using Python Virtual Environment**:
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Run server
python run.py
```

---

## Development Workflow

### 1. Make Your Changes

- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Update documentation if needed

### 2. Test Your Changes

**Run tests**:
```bash
# With Docker
make test

# Or locally
pytest tests/ -v
```

**Manual testing**:
```bash
# Start the API
make dev

# Test endpoint
curl http://localhost:8000/health

# Test your changes
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '...'
```

### 3. Code Quality

**Linting**:
```bash
# Format code with Black
black app/ tests/

# Check with flake8
flake8 app/

# Type checking (if applicable)
mypy app/
```

**Standards**:
- Follow PEP 8 style guide
- Use type hints where appropriate
- Keep functions focused and small
- Write descriptive variable names

### 4. Commit Your Changes

Write clear commit messages:
```bash
git add .
git commit -m "feat: add support for Cisco ASA firewall commands"
# or
git commit -m "fix: resolve jumphost connection timeout issue"
```

**Commit message format**:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or updates
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 5. Push to Your Fork

```bash
git push origin feat/your-feature-name
```

### 6. Create Pull Request

1. Go to GitHub and create a Pull Request from your fork to the main repository
2. Fill out the PR template completely
3. Wait for CI checks to pass
4. Respond to review feedback

---

## Pull Request Guidelines

### Required

- ✅ Clear description of changes
- ✅ Link to related issue (if applicable)
- ✅ Tests added/updated for new functionality
- ✅ Documentation updated
- ✅ All CI checks passing
- ✅ No merge conflicts

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Other (describe):

## Related Issues
Fixes #123
Relates to #456

## Changes Made
- Added feature X
- Fixed bug Y
- Updated documentation for Z

## Testing
- [ ] Tested locally
- [ ] Added unit tests
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No breaking changes (or documented if necessary)
```

---

## Testing Guidelines

### Writing Tests

Tests are located in the `tests/` directory.

**Test structure**:
```python
# tests/test_feature.py
import pytest
from app.models import DeviceCredentials

def test_device_credentials_validation():
    """Test device credentials validation."""
    # Valid credentials
    creds = DeviceCredentials(
        hostname="192.168.1.1",
        username="admin",
        password="cisco123",
        os="iosxe"
    )
    assert creds.hostname == "192.168.1.1"
    
    # Invalid OS should raise validation error
    with pytest.raises(ValidationError):
        DeviceCredentials(
            hostname="192.168.1.1",
            username="admin",
            password="cisco123",
            os="invalid_os"
        )
```

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_models.py

# Specific test
pytest tests/test_models.py::test_device_credentials_validation

# With coverage
pytest --cov=app tests/

# Verbose output
pytest -v
```

### Test Coverage

Aim for high test coverage:
```bash
# Generate coverage report
pytest --cov=app --cov-report=html tests/

# View report
open htmlcov/index.html
```

---

## Security Guidelines

Since this tool interacts with network infrastructure:

### Do's ✅

- **Always validate input** - Use Pydantic models
- **Maintain read-only status** - Only allow show commands
- **Use input sanitization** - Block dangerous patterns
- **Never commit credentials** - Use environment variables
- **Test security features** - Verify command validation works

### Don'ts ❌

- **Don't store credentials** - Always pass per-request
- **Don't allow configuration commands** - Security violation
- **Don't disable validation** - Even for testing
- **Don't commit .env files** - Contains sensitive data
- **Don't skip security tests** - Critical for safety

### Security Checklist

When touching command execution code:
- [ ] Commands are validated (show-only)
- [ ] Input is sanitized (no injection)
- [ ] Credentials are not logged
- [ ] Tests verify security constraints
- [ ] Documentation updated

---

## Adding New Features

### New Device OS Type

1. Update `DeviceOS` enum in `app/models.py`:
```python
class DeviceOS(str, Enum):
    IOS = "ios"
    IOSXE = "iosxe"
    IOSXR = "iosxr"
    NXOS = "nxos"
    ASA = "asa"
    NEW_OS = "new_os"  # Add new OS
```

2. Update documentation
3. Add tests
4. Test with real device (if possible)

### New API Endpoint

1. Add endpoint to `app/main.py`:
```python
@app.post("/api/v1/new-endpoint")
async def new_endpoint(request: NewRequest):
    """Endpoint description."""
    # Implementation
    return {"result": "success"}
```

2. Add request/response models to `app/models.py`
3. Add tests in `tests/test_main.py`
4. Update API documentation
5. Add examples

### New MCP Tool

1. Add tool to `mcp_server.py`:
```python
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # ... existing tools ...
        Tool(
            name="new_tool",
            description="Description of new tool",
            inputSchema={
                "type": "object",
                "properties": {...},
                "required": [...]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    if name == "new_tool":
        # Implementation
        return [TextContent(type="text", text="result")]
```

2. Update MCP documentation
3. Add tests
4. Test with MCP client

---

## Documentation

### Updating Documentation

Documentation includes:
- README.md
- API documentation (docstrings)
- Wiki pages
- Example scripts
- Deployment guides

### Documentation Standards

- Clear and concise language
- Include examples
- Keep up to date with code changes
- Test all command examples

---

## Release Process

Maintainers handle releases, but contributors should:

1. Update version in relevant files
2. Update CHANGELOG.md
3. Ensure all tests pass
4. Verify documentation is current

---

## Getting Help

- **Questions**: Open a GitHub discussion
- **Bugs**: Create an issue
- **Chat**: Join our community (if applicable)
- **Email**: Contact maintainers

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing! 🎉

---

## Additional Resources

- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

**Navigation**: [← Troubleshooting](Troubleshooting) | [Home](Home)

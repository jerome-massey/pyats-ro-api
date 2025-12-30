# Unit Tests

This directory contains unit tests for the PyATS Show Command API.

## Running Tests

### Using Docker (Recommended)

```bash
# Run all tests
docker run --rm -v $(pwd):/app -w /app python:3.11-slim bash -c \
  "pip install -q -r requirements.txt pytest pytest-asyncio && python -m pytest tests/ -v"

# Run just model tests (faster, no heavy dependencies)
docker run --rm -v $(pwd):/app -w /app python:3.11-slim bash -c \
  "pip install -q pytest pydantic && python -m pytest tests/test_models.py -v"
```

### Local Python

```bash
# Install dependencies
pip install -r requirements.txt pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Test Coverage

### ✅ test_models.py (34 tests - ALL PASSING)

Comprehensive tests for Pydantic models:

- **DeviceOS**: Enum validation
- **JumphostConfig**: Host, port, username, key_path validation
- **DeviceCredentials**: All device credential validation including JunOS rejection
- **ShowCommand**: Command validation, pipe options, dangerous character blocking
- **ShowCommandRequest**: Full request validation with multiple devices

### ⚠️ test_api.py (11 tests - Requires full stack)

API endpoint tests - requires full PyATS/Unicon dependencies:

- Health check endpoint  
- Execute endpoint with validation
- Jumphost test endpoint
- OpenAPI documentation

**Note**: API tests currently have dependency version conflicts between httpx/starlette when run in minimal containers. They work when the full application stack is available (via Docker image).

## Test Results

```bash
============================= test session starts ==============================
platform linux -- Python 3.11.14, pytest-9.0.2, pluggy-1.6.0
collected 34 items

tests/test_models.py::TestDeviceOS::test_valid_os_values PASSED          [  2%]
tests/test_models.py::TestJumphostConfig::test_valid_jumphost_config PASSED [  5%]
tests/test_models.py::TestJumphostConfig::test_default_port PASSED       [  8%]
tests/test_models.py::TestJumphostConfig::test_empty_host PASSED         [ 11%]
tests/test_models.py::TestJumphostConfig::test_host_too_long PASSED      [ 14%]
tests/test_models.py::TestJumphostConfig::test_invalid_port_range PASSED [ 17%]
tests/test_models.py::TestJumphostConfig::test_port_zero PASSED          [ 20%]
tests/test_models.py::TestJumphostConfig::test_empty_username PASSED     [ 23%]
tests/test_models.py::TestJumphostConfig::test_username_too_long PASSED  [ 26%]
tests/test_models.py::TestDeviceCredentials::test_valid_device_credentials PASSED [ 29%]
tests/test_models.py::TestDeviceCredentials::test_junos_rejection PASSED [ 32%]
tests/test_models.py::TestDeviceCredentials::test_junos_case_insensitive PASSED [ 35%]
tests/test_models.py::TestDeviceCredentials::test_empty_hostname PASSED  [ 38%]
tests/test_models.py::TestDeviceCredentials::test_hostname_too_long PASSED [ 41%]
tests/test_models.py::TestDeviceCredentials::test_invalid_port PASSED    [ 44%]
tests/test_models.py::TestDeviceCredentials::test_empty_password PASSED  [ 47%]
tests/test_models.py::TestDeviceCredentials::test_password_too_long PASSED [ 50%]
tests/test_models.py::TestDeviceCredentials::test_with_jumphost PASSED   [ 52%]
tests/test_models.py::TestShowCommand::test_valid_show_command PASSED    [ 55%]
tests/test_models.py::TestShowCommand::test_show_command_with_pipe PASSED [ 58%]
tests/test_models.py::TestShowCommand::test_get_full_command_without_pipe PASSED [ 61%]
tests/test_models.py::TestShowCommand::test_get_full_command_with_pipe PASSED [ 64%]
tests/test_models.py::TestShowCommand::test_non_show_command_rejected PASSED [ 67%]
tests/test_models.py::TestShowCommand::test_command_with_semicolon_rejected PASSED [ 70%]
tests/test_models.py::TestShowCommand::test_command_with_pipe_rejected PASSED [ 73%]
tests/test_models.py::TestShowCommand::test_command_with_backtick_rejected PASSED [ 76%]
tests/test_models.py::TestShowCommand::test_command_too_long PASSED      [ 79%]
tests/test_models.py::TestShowCommand::test_empty_command PASSED         [ 82%]
tests/test_models.py::TestShowCommand::test_pipe_value_too_long PASSED   [ 85%]
tests/test_models.py::TestShowCommand::test_pipe_value_with_semicolon PASSED [ 88%]
tests/test_models.py::TestShowCommandRequest::test_valid_request PASSED  [ 91%]
tests/test_models.py::TestShowCommandRequest::test_request_with_jumphost PASSED [ 94%]
tests/test_models.py::TestShowCommandRequest::test_request_custom_timeout PASSED [ 97%]
tests/test_models.py::TestShowCommandRequest::test_request_multiple_devices PASSED [100%]

============================== 34 passed in 0.10s ==============================
```

## Key Test Cases

### JunOS Rejection (Security Feature)
- Tests that JunOS is explicitly rejected with helpful error message
- Case-insensitive validation (junos, JUNOS, JunOS all rejected)
- Explains why JunOS is unsupported (incompatible syntax)

### Command Injection Prevention
- Blocks semicolons, pipes, backticks, dollar signs
- Enforces "show" command prefix
- Validates command length (max 1000 chars)
- Validates pipe values (max 500 chars)

### Input Validation
- Hostname/IP format validation
- Port range (1-65535)
- Username/password length limits
- Empty field rejection

### Pipe Options
- Include, exclude, begin, section
- Full command generation with pipes
- Dangerous character blocking in pipe values

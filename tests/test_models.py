"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError
from app.models import (
    DeviceOS,
    PipeOption,
    DeviceCredentials,
    ShowCommand,
    ShowCommandRequest,
)


class TestDeviceOS:
    """Tests for DeviceOS enum."""
    
    def test_valid_os_values(self):
        """Test all valid OS values."""
        assert DeviceOS.IOS.value == "ios"
        assert DeviceOS.IOSXE.value == "iosxe"
        assert DeviceOS.IOSXR.value == "iosxr"
        assert DeviceOS.NXOS.value == "nxos"
        assert DeviceOS.ASA.value == "asa"


class TestDeviceCredentials:
    """Tests for DeviceCredentials model."""
    
    def test_valid_device_credentials(self):
        """Test valid device credentials."""
        creds = DeviceCredentials(
            hostname="192.168.1.1",
            port=22,
            username="admin",
            password="password123",
            os=DeviceOS.IOS
        )
        assert creds.hostname == "192.168.1.1"
        assert creds.port == 22
        assert creds.username == "admin"
        assert creds.password == "password123"
        assert creds.os == DeviceOS.IOS
    
    def test_junos_rejection(self):
        """Test that JunOS is rejected with helpful message."""
        with pytest.raises(ValidationError) as exc:
            DeviceCredentials(
                hostname="192.168.1.1",
                username="admin",
                password="password123",
                os="junos"
            )
        assert "JunOS is not supported" in str(exc.value)
    
    def test_junos_case_insensitive(self):
        """Test that JunOS rejection is case insensitive."""
        with pytest.raises(ValidationError) as exc:
            DeviceCredentials(
                hostname="192.168.1.1",
                username="admin",
                password="password123",
                os="JUNOS"
            )
        assert "JunOS is not supported" in str(exc.value)
    
    def test_empty_hostname(self):
        """Test that empty hostname is rejected."""
        with pytest.raises(ValidationError) as exc:
            DeviceCredentials(
                hostname="",
                username="admin",
                password="password123",
                os=DeviceOS.IOS
            )
        assert "Hostname cannot be empty" in str(exc.value)
    
    def test_hostname_too_long(self):
        """Test that overly long hostname is rejected."""
        with pytest.raises(ValidationError) as exc:
            DeviceCredentials(
                hostname="a" * 256,
                username="admin",
                password="password123",
                os=DeviceOS.IOS
            )
        assert "Hostname exceeds maximum length" in str(exc.value)
    
    def test_invalid_port(self):
        """Test that invalid port is rejected."""
        with pytest.raises(ValidationError) as exc:
            DeviceCredentials(
                hostname="192.168.1.1",
                port=70000,
                username="admin",
                password="password123",
                os=DeviceOS.IOS
            )
        assert "Port must be between 1 and 65535" in str(exc.value)
    
    def test_empty_password(self):
        """Test that empty password is rejected."""
        with pytest.raises(ValidationError) as exc:
            DeviceCredentials(
                hostname="192.168.1.1",
                username="admin",
                password="",
                os=DeviceOS.IOS
            )
        assert "Password cannot be empty" in str(exc.value)
    
    def test_password_too_long(self):
        """Test that overly long password is rejected."""
        with pytest.raises(ValidationError) as exc:
            DeviceCredentials(
                hostname="192.168.1.1",
                username="admin",
                password="a" * 1025,
                os=DeviceOS.IOS
            )
        assert "Password exceeds maximum length" in str(exc.value)


class TestShowCommand:
    """Tests for ShowCommand model."""
    
    def test_valid_show_command(self):
        """Test valid show command."""
        cmd = ShowCommand(command="show version")
        assert cmd.command == "show version"
        assert cmd.pipe_option is None
        assert cmd.pipe_value is None
    
    def test_show_command_with_pipe(self):
        """Test show command with pipe option."""
        cmd = ShowCommand(
            command="show version",
            pipe_option=PipeOption.INCLUDE,
            pipe_value="Cisco"
        )
        assert cmd.command == "show version"
        assert cmd.pipe_option == PipeOption.INCLUDE
        assert cmd.pipe_value == "Cisco"
    
    def test_get_full_command_without_pipe(self):
        """Test getting full command without pipe."""
        cmd = ShowCommand(command="show version")
        assert cmd.get_full_command() == "show version"
    
    def test_get_full_command_with_pipe(self):
        """Test getting full command with pipe."""
        cmd = ShowCommand(
            command="show version",
            pipe_option=PipeOption.INCLUDE,
            pipe_value="Cisco"
        )
        assert cmd.get_full_command() == "show version | include Cisco"
    
    def test_non_show_command_rejected(self):
        """Test that non-show commands are rejected."""
        with pytest.raises(ValidationError) as exc:
            ShowCommand(command="configure terminal")
        assert "Only 'show' commands are allowed" in str(exc.value)
    
    def test_command_with_semicolon_rejected(self):
        """Test that commands with semicolons are rejected."""
        with pytest.raises(ValidationError) as exc:
            ShowCommand(command="show version; show run")
        assert "disallowed character" in str(exc.value)
    
    def test_command_with_pipe_rejected(self):
        """Test that commands with pipes are rejected."""
        with pytest.raises(ValidationError) as exc:
            ShowCommand(command="show version | include test")
        assert "disallowed character" in str(exc.value)
    
    def test_command_with_backtick_rejected(self):
        """Test that commands with backticks are rejected."""
        with pytest.raises(ValidationError) as exc:
            ShowCommand(command="show version`whoami`")
        assert "disallowed character" in str(exc.value)
    
    def test_command_too_long(self):
        """Test that overly long commands are rejected."""
        with pytest.raises(ValidationError) as exc:
            ShowCommand(command="show " + "a" * 1000)
        assert "exceeds maximum length" in str(exc.value)
    
    def test_empty_command(self):
        """Test that empty commands are rejected."""
        with pytest.raises(ValidationError) as exc:
            ShowCommand(command="")
        assert "Command cannot be empty" in str(exc.value)
    
    def test_pipe_value_too_long(self):
        """Test that overly long pipe values are rejected."""
        with pytest.raises(ValidationError) as exc:
            ShowCommand(
                command="show version",
                pipe_option=PipeOption.INCLUDE,
                pipe_value="a" * 501
            )
        assert "exceeds maximum length" in str(exc.value)
    
    def test_pipe_value_with_semicolon(self):
        """Test that pipe values with semicolons are rejected."""
        with pytest.raises(ValidationError) as exc:
            ShowCommand(
                command="show version",
                pipe_option=PipeOption.INCLUDE,
                pipe_value="test;whoami"
            )
        assert "disallowed character" in str(exc.value)


class TestShowCommandRequest:
    """Tests for ShowCommandRequest model."""
    
    def test_valid_request(self):
        """Test valid command request."""
        req = ShowCommandRequest(
            devices=[
                DeviceCredentials(
                    hostname="192.168.1.1",
                    username="admin",
                    password="password123",
                    os=DeviceOS.IOS
                )
            ],
            commands=[ShowCommand(command="show version")],
            timeout=30
        )
        assert len(req.devices) == 1
        assert len(req.commands) == 1
        assert req.timeout == 30
    
    def test_request_custom_timeout(self):
        """Test request with custom timeout."""
        req = ShowCommandRequest(
            devices=[
                DeviceCredentials(
                    hostname="192.168.1.1",
                    username="admin",
                    password="password123",
                    os=DeviceOS.IOS
                )
            ],
            commands=[ShowCommand(command="show version")],
            timeout=60
        )
        assert req.timeout == 60
    
    def test_request_multiple_devices(self):
        """Test request with multiple devices."""
        req = ShowCommandRequest(
            devices=[
                DeviceCredentials(
                    hostname="192.168.1.1",
                    username="admin",
                    password="password123",
                    os=DeviceOS.IOS
                ),
                DeviceCredentials(
                    hostname="192.168.1.2",
                    username="admin",
                    password="password123",
                    os=DeviceOS.NXOS
                )
            ],
            commands=[ShowCommand(command="show version")]
        )
        assert len(req.devices) == 2

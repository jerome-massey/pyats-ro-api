"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError
from app.models import (
    DeviceOS,
    PipeOption,
    JumphostConfig,
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


class TestJumphostConfig:
    """Tests for JumphostConfig model."""
    
    def test_valid_jumphost_config(self):
        """Test valid jumphost configuration."""
        config = JumphostConfig(
            host="jumphost.example.com",
            port=22,
            username="jumpuser",
            key_path="/root/.ssh/id_rsa"
        )
        assert config.host == "jumphost.example.com"
        assert config.port == 22
        assert config.username == "jumpuser"
        assert config.key_path == "/root/.ssh/id_rsa"
    
    def test_default_port(self):
        """Test default port value."""
        config = JumphostConfig(
            host="jumphost.example.com",
            username="jumpuser",
            key_path="/root/.ssh/id_rsa"
        )
        assert config.port == 22
    
    def test_empty_host(self):
        """Test empty host validation."""
        with pytest.raises(ValidationError) as exc:
            JumphostConfig(
                host="",
                username="jumpuser",
                key_path="/root/.ssh/id_rsa"
            )
        assert "Jumphost host cannot be empty" in str(exc.value)
    
    def test_host_too_long(self):
        """Test host length validation."""
        with pytest.raises(ValidationError) as exc:
            JumphostConfig(
                host="a" * 256,
                username="jumpuser",
                key_path="/root/.ssh/id_rsa"
            )
        assert "exceeds maximum length" in str(exc.value)
    
    def test_invalid_port_range(self):
        """Test port range validation."""
        with pytest.raises(ValidationError) as exc:
            JumphostConfig(
                host="jumphost.example.com",
                port=70000,
                username="jumpuser",
                key_path="/root/.ssh/id_rsa"
            )
        assert "Port must be between 1 and 65535" in str(exc.value)
    
    def test_port_zero(self):
        """Test port 0 validation."""
        with pytest.raises(ValidationError) as exc:
            JumphostConfig(
                host="jumphost.example.com",
                port=0,
                username="jumpuser",
                key_path="/root/.ssh/id_rsa"
            )
        assert "Port must be between 1 and 65535" in str(exc.value)
    
    def test_empty_username(self):
        """Test empty username validation."""
        with pytest.raises(ValidationError) as exc:
            JumphostConfig(
                host="jumphost.example.com",
                username="",
                key_path="/root/.ssh/id_rsa"
            )
        assert "Username cannot be empty" in str(exc.value)
    
    def test_username_too_long(self):
        """Test username length validation."""
        with pytest.raises(ValidationError) as exc:
            JumphostConfig(
                host="jumphost.example.com",
                username="a" * 256,
                key_path="/root/.ssh/id_rsa"
            )
        assert "exceeds maximum length" in str(exc.value)


class TestDeviceCredentials:
    """Tests for DeviceCredentials model."""
    
    def test_valid_device_credentials(self):
        """Test valid device credentials."""
        creds = DeviceCredentials(
            hostname="192.168.1.1",
            username="admin",
            password="cisco123",
            os=DeviceOS.IOSXE
        )
        assert creds.hostname == "192.168.1.1"
        assert creds.port == 22
        assert creds.username == "admin"
        assert creds.password == "cisco123"
        assert creds.os == DeviceOS.IOSXE
    
    def test_junos_rejection(self):
        """Test JunOS is explicitly rejected."""
        with pytest.raises(ValidationError) as exc:
            DeviceCredentials(
                hostname="192.168.1.1",
                username="admin",
                password="cisco123",
                os="junos"
            )
        error_msg = str(exc.value).lower()
        assert "junos" in error_msg
        assert "not supported" in error_msg
    
    def test_junos_case_insensitive(self):
        """Test JunOS rejection is case insensitive."""
        for variant in ["junos", "JUNOS", "JunOS", "Junos"]:
            with pytest.raises(ValidationError) as exc:
                DeviceCredentials(
                    hostname="192.168.1.1",
                    username="admin",
                    password="cisco123",
                    os=variant
                )
            assert "not supported" in str(exc.value).lower()
    
    def test_empty_hostname(self):
        """Test empty hostname validation."""
        with pytest.raises(ValidationError) as exc:
            DeviceCredentials(
                hostname="",
                username="admin",
                password="cisco123",
                os=DeviceOS.IOS
            )
        assert "Hostname cannot be empty" in str(exc.value)
    
    def test_hostname_too_long(self):
        """Test hostname length validation."""
        with pytest.raises(ValidationError) as exc:
            DeviceCredentials(
                hostname="a" * 256,
                username="admin",
                password="cisco123",
                os=DeviceOS.IOS
            )
        assert "exceeds maximum length" in str(exc.value)
    
    def test_invalid_port(self):
        """Test invalid port validation."""
        with pytest.raises(ValidationError) as exc:
            DeviceCredentials(
                hostname="192.168.1.1",
                port=100000,
                username="admin",
                password="cisco123",
                os=DeviceOS.IOS
            )
        assert "Port must be between 1 and 65535" in str(exc.value)
    
    def test_empty_password(self):
        """Test empty password validation."""
        with pytest.raises(ValidationError) as exc:
            DeviceCredentials(
                hostname="192.168.1.1",
                username="admin",
                password="",
                os=DeviceOS.IOS
            )
        assert "Password cannot be empty" in str(exc.value)
    
    def test_password_too_long(self):
        """Test password length validation."""
        with pytest.raises(ValidationError) as exc:
            DeviceCredentials(
                hostname="192.168.1.1",
                username="admin",
                password="a" * 1025,
                os=DeviceOS.IOS
            )
        assert "exceeds maximum length" in str(exc.value)
    
    def test_with_jumphost(self):
        """Test device with jumphost config."""
        jumphost = JumphostConfig(
            host="jumphost.example.com",
            username="jumpuser",
            key_path="/root/.ssh/id_rsa"
        )
        creds = DeviceCredentials(
            hostname="192.168.1.1",
            username="admin",
            password="cisco123",
            os=DeviceOS.IOSXE,
            jumphost=jumphost
        )
        assert creds.jumphost is not None
        assert creds.jumphost.host == "jumphost.example.com"


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
            command="show running-config",
            pipe_option=PipeOption.INCLUDE,
            pipe_value="interface"
        )
        assert cmd.command == "show running-config"
        assert cmd.pipe_option == PipeOption.INCLUDE
        assert cmd.pipe_value == "interface"
    
    def test_get_full_command_without_pipe(self):
        """Test full command without pipe."""
        cmd = ShowCommand(command="show version")
        assert cmd.get_full_command() == "show version"
    
    def test_get_full_command_with_pipe(self):
        """Test full command with pipe."""
        cmd = ShowCommand(
            command="show running-config",
            pipe_option=PipeOption.INCLUDE,
            pipe_value="interface"
        )
        assert cmd.get_full_command() == "show running-config | include interface"
    
    def test_non_show_command_rejected(self):
        """Test non-show commands are rejected."""
        with pytest.raises(ValidationError) as exc:
            ShowCommand(command="configure terminal")
        assert "Only 'show' commands are allowed" in str(exc.value)
    
    def test_command_with_semicolon_rejected(self):
        """Test command with semicolon is rejected."""
        with pytest.raises(ValidationError) as exc:
            ShowCommand(command="show version ; configure")
        assert "disallowed character" in str(exc.value)
    
    def test_command_with_pipe_rejected(self):
        """Test command with pipe character is rejected."""
        with pytest.raises(ValidationError) as exc:
            ShowCommand(command="show version | grep Cisco")
        assert "disallowed character" in str(exc.value)
    
    def test_command_with_backtick_rejected(self):
        """Test command with backtick is rejected."""
        with pytest.raises(ValidationError) as exc:
            ShowCommand(command="show version `whoami`")
        assert "disallowed character" in str(exc.value)
    
    def test_command_too_long(self):
        """Test command length validation."""
        with pytest.raises(ValidationError) as exc:
            ShowCommand(command="show " + "a" * 1000)
        assert "exceeds maximum length" in str(exc.value)
    
    def test_empty_command(self):
        """Test empty command validation."""
        with pytest.raises(ValidationError) as exc:
            ShowCommand(command="")
        assert "Command cannot be empty" in str(exc.value)
    
    def test_pipe_value_too_long(self):
        """Test pipe value length validation."""
        with pytest.raises(ValidationError) as exc:
            ShowCommand(
                command="show running-config",
                pipe_option=PipeOption.INCLUDE,
                pipe_value="a" * 501
            )
        assert "exceeds maximum length" in str(exc.value)
    
    def test_pipe_value_with_semicolon(self):
        """Test pipe value with dangerous character."""
        with pytest.raises(ValidationError) as exc:
            ShowCommand(
                command="show running-config",
                pipe_option=PipeOption.INCLUDE,
                pipe_value="; reload"
            )
        assert "disallowed character" in str(exc.value)


class TestShowCommandRequest:
    """Tests for ShowCommandRequest model."""
    
    def test_valid_request(self):
        """Test valid show command request."""
        request = ShowCommandRequest(
            devices=[
                DeviceCredentials(
                    hostname="192.168.1.1",
                    username="admin",
                    password="cisco123",
                    os=DeviceOS.IOSXE
                )
            ],
            commands=[
                ShowCommand(command="show version")
            ]
        )
        assert len(request.devices) == 1
        assert len(request.commands) == 1
        assert request.use_jumphost is False
        assert request.timeout == 30
    
    def test_request_with_jumphost(self):
        """Test request with jumphost enabled."""
        request = ShowCommandRequest(
            devices=[
                DeviceCredentials(
                    hostname="192.168.1.1",
                    username="admin",
                    password="cisco123",
                    os=DeviceOS.IOSXE
                )
            ],
            commands=[
                ShowCommand(command="show version")
            ],
            use_jumphost=True
        )
        assert request.use_jumphost is True
    
    def test_request_custom_timeout(self):
        """Test request with custom timeout."""
        request = ShowCommandRequest(
            devices=[
                DeviceCredentials(
                    hostname="192.168.1.1",
                    username="admin",
                    password="cisco123",
                    os=DeviceOS.IOSXE
                )
            ],
            commands=[
                ShowCommand(command="show version")
            ],
            timeout=60
        )
        assert request.timeout == 60
    
    def test_request_multiple_devices(self):
        """Test request with multiple devices."""
        request = ShowCommandRequest(
            devices=[
                DeviceCredentials(
                    hostname="192.168.1.1",
                    username="admin",
                    password="cisco123",
                    os=DeviceOS.IOSXE
                ),
                DeviceCredentials(
                    hostname="192.168.1.2",
                    username="admin",
                    password="cisco123",
                    os=DeviceOS.NXOS
                )
            ],
            commands=[
                ShowCommand(command="show version")
            ]
        )
        assert len(request.devices) == 2

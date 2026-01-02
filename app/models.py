"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, ClassVar, Pattern, Any
from enum import Enum
import re


class DeviceOS(str, Enum):
    """Supported device operating systems."""
    IOS = "ios"
    IOSXE = "iosxe"
    IOSXR = "iosxr"
    NXOS = "nxos"
    ASA = "asa"


class PipeOption(str, Enum):
    """Show command pipe options."""
    INCLUDE = "include"
    EXCLUDE = "exclude"
    BEGIN = "begin"
    SECTION = "section"


class OutputFormat(str, Enum):
    """Available output formats for command execution."""
    RAW = "raw"
    PARSED = "parsed"
    BOTH = "both"


class DeviceCredentials(BaseModel):
    """Device credentials."""
    hostname: str = Field(..., description="Device hostname or IP address")
    port: int = Field(default=22, description="SSH port")
    username: str = Field(..., description="Device username")
    password: str = Field(..., description="Device password")
    os: DeviceOS = Field(..., description="Device operating system")
    enable_password: Optional[str] = Field(None, description="Enable password if required")
    
    @field_validator('hostname')
    @classmethod
    def validate_hostname(cls, v):
        """Validate hostname/IP format."""
        if not v or not isinstance(v, str) or len(v) == 0:
            raise ValueError("Hostname cannot be empty")
        if len(v) > 255:
            raise ValueError("Hostname exceeds maximum length")
        # Allow alphanumeric, dots, hyphens, and IPv6 colons
        if not re.match(r'^[a-zA-Z0-9\:][a-zA-Z0-9\.\:\-]*[a-zA-Z0-9]$', v) and not re.match(r'^[a-zA-Z0-9]$', v):
            raise ValueError("Invalid hostname/IP format")
        return v
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v):
        """Validate port range."""
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username format."""
        if not v or len(v) == 0:
            raise ValueError("Username cannot be empty")
        if len(v) > 255:
            raise ValueError("Username exceeds maximum length")
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password."""
        if not v or len(v) == 0:
            raise ValueError("Password cannot be empty")
        if len(v) > 1024:
            raise ValueError("Password exceeds maximum length")
        return v
    
    @field_validator('os', mode='before')
    @classmethod
    def validate_os(cls, v):
        """Validate OS and provide helpful error for unsupported types."""
        if isinstance(v, str) and v.lower() == 'junos':
            raise ValueError(
                "JunOS is not supported. This API only supports Cisco devices (ios, iosxe, iosxr, nxos, asa). "
                "JunOS uses different command syntax (e.g., 'match' instead of 'include') which is incompatible "
                "with the current pipe options implementation."
            )
        return v


class ShowCommand(BaseModel):
    """Show command with optional pipe filters."""
    command: str = Field(..., description="Show command to execute (e.g., 'show version')")
    pipe_option: Optional[PipeOption] = Field(None, description="Pipe option (include, exclude, begin, section)")
    pipe_value: Optional[str] = Field(None, description="Value for the pipe option")
    
    # Regex patterns for command validation - declared as ClassVar to avoid treating as Pydantic fields
    SHOW_COMMAND_PATTERN: ClassVar[Pattern] = re.compile(r'^show\s+[a-zA-Z0-9\s\-_\.]+$', re.IGNORECASE)
    PIPE_VALUE_PATTERN: ClassVar[Pattern] = re.compile(r'^[a-zA-Z0-9\s\-_\.,\(\)]+$')
    DANGEROUS_PATTERNS: ClassVar[List[str]] = [
        r';',           # Command separator
        r'\n',          # Newline
        r'\r',          # Carriage return
        r'`',           # Backtick (command substitution)
        r'\$',          # Dollar sign (variable expansion)
        r'\|',          # Pipe (for commands other than show pipe options)
        r'&&',          # AND operator
        r'\|\|',        # OR operator
        r'>',           # Redirection
        r'<',           # Redirection
        r'&',           # Background
        r'!',           # History expansion
    ]
    
    @field_validator('command')
    @classmethod
    def validate_command(cls, v):
        """Validate show command format and content."""
        if not v or not isinstance(v, str):
            raise ValueError("Command cannot be empty")
        
        # Strip whitespace
        v = v.strip()
        
        if len(v) == 0:
            raise ValueError("Command cannot be empty")
        
        if len(v) > 1000:
            raise ValueError("Command exceeds maximum length of 1000 characters")
        
        # Check if command starts with 'show'
        if not v.lower().startswith('show'):
            raise ValueError("Only 'show' commands are allowed")
        
        # Check for dangerous patterns (basic shell injection prevention)
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, v):
                raise ValueError(f"Command contains disallowed character(s): '{pattern}'")
        
        # Check basic show command format
        if not cls.SHOW_COMMAND_PATTERN.match(v):
            raise ValueError(
                "Command must be 'show' followed by valid parameters. "
                "Only alphanumeric characters, spaces, hyphens, underscores, and dots are allowed."
            )
        
        return v
    
    @field_validator('pipe_value')
    @classmethod
    def validate_pipe_value(cls, v, info):
        """Validate pipe filter value."""
        # If pipe_value is provided, pipe_option must also be provided
        if v is not None:
            if not isinstance(v, str) or len(v) == 0:
                raise ValueError("Pipe value cannot be empty")
            
            if len(v) > 500:
                raise ValueError("Pipe value exceeds maximum length of 500 characters")
            
            # Check for dangerous patterns in pipe value
            for pattern in cls.DANGEROUS_PATTERNS:
                if re.search(pattern, v):
                    raise ValueError(f"Pipe value contains disallowed character(s)")
            
            # Validate pipe value format
            if not cls.PIPE_VALUE_PATTERN.match(v):
                raise ValueError(
                    "Pipe value contains invalid characters. "
                    "Only alphanumeric, spaces, hyphens, underscores, dots, commas, and parentheses are allowed."
                )
        
        return v
    
    def get_full_command(self) -> str:
        """Build the full command with pipe options.
        
        Returns:
            Full command string with pipe options if specified
        """
        if self.pipe_option and self.pipe_value:
            return f"{self.command} | {self.pipe_option.value} {self.pipe_value}"
        return self.command


class ShowCommandRequest(BaseModel):
    """Request to execute show commands on one or more devices."""
    devices: List[DeviceCredentials] = Field(..., description="List of target devices")
    commands: List[ShowCommand] = Field(..., description="List of show commands to execute")
    timeout: int = Field(default=30, description="Command timeout in seconds")
    output_format: OutputFormat = Field(default=OutputFormat.RAW, description="Output format: raw, parsed, or both")


class CommandResult(BaseModel):
    """Result of a single command execution."""
    command: str
    output: str
    success: bool
    parsed: Optional[Any] = None
    parse_error: Optional[str] = None
    error: Optional[str] = None


class DeviceResult(BaseModel):
    """Results for a single device."""
    hostname: str
    success: bool
    commands: List[CommandResult]
    error: Optional[str] = None


class ShowCommandResponse(BaseModel):
    """Response containing results from all devices."""
    results: List[DeviceResult]
    total_devices: int
    successful_devices: int
    failed_devices: int

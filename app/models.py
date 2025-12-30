"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum


class DeviceOS(str, Enum):
    """Supported device operating systems."""
    IOS = "ios"
    IOSXE = "iosxe"
    IOSXR = "iosxr"
    NXOS = "nxos"
    ASA = "asa"
    JUNOS = "junos"


class PipeOption(str, Enum):
    """Show command pipe options."""
    INCLUDE = "include"
    EXCLUDE = "exclude"
    BEGIN = "begin"
    SECTION = "section"


class DeviceCredentials(BaseModel):
    """Device credentials."""
    hostname: str = Field(..., description="Device hostname or IP address")
    port: int = Field(default=22, description="SSH port")
    username: str = Field(..., description="Device username")
    password: str = Field(..., description="Device password")
    os: DeviceOS = Field(..., description="Device operating system")
    enable_password: Optional[str] = Field(None, description="Enable password if required")


class ShowCommand(BaseModel):
    """Show command with optional pipe filters."""
    command: str = Field(..., description="Show command to execute (e.g., 'show version')")
    pipe_option: Optional[PipeOption] = Field(None, description="Pipe option (include, exclude, begin, section)")
    pipe_value: Optional[str] = Field(None, description="Value for the pipe option")
    
    def get_full_command(self) -> str:
        """Build the full command with pipe options."""
        if self.pipe_option and self.pipe_value:
            return f"{self.command} | {self.pipe_option.value} {self.pipe_value}"
        return self.command


class ShowCommandRequest(BaseModel):
    """Request to execute show commands on one or more devices."""
    devices: List[DeviceCredentials] = Field(..., description="List of target devices")
    commands: List[ShowCommand] = Field(..., description="List of show commands to execute")
    use_jumphost: bool = Field(default=False, description="Whether to use SSH jumphost")
    timeout: int = Field(default=30, description="Command timeout in seconds")


class CommandResult(BaseModel):
    """Result of a single command execution."""
    command: str
    output: str
    success: bool
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

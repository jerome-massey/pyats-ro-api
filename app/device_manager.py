"""PyATS/Unicon device connection manager."""

import logging
from typing import Optional, Dict, Any
from unicon.core.errors import ConnectionError, TimeoutError
from unicon import Connection
from app.models import DeviceCredentials, ShowCommand

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manages connections to network devices using PyATS/Unicon."""
    
    def __init__(
        self,
        device_creds: DeviceCredentials,
        timeout: int = 30
    ):
        """Initialize device manager.
        
        Args:
            device_creds: Device credentials and connection info
            timeout: Command timeout in seconds
        """
        self.device_creds = device_creds
        self.timeout = timeout
        self.connection: Optional[Connection] = None
    
    def connect(self) -> Connection:
        """Establish connection to the device.
        
        Jumphost routing is handled transparently by SSH config file in the container.
        The SSH config file contains ProxyJump rules that automatically route connections
        through the jumphost for configured subnet ranges.
        
        Returns:
            Connected Unicon Connection object
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            # Build connection parameters
            connection_args: Dict[str, Any] = {
                "hostname": self.device_creds.hostname,
                "start": [f"sshpass -p '{self.device_creds.password}' ssh {self.device_creds.username}@{self.device_creds.hostname}"],
                "os": self.device_creds.os.value,
                "username": self.device_creds.username,
                "password": self.device_creds.password,
                "port": self.device_creds.port,
                "log_stdout": False,
                "learn_hostname": True,
                "settings": {
                    "EXEC_TIMEOUT": self.timeout,
                    "POST_DISCONNECT_WAIT_SEC": 0,
                }
            }
            
            # Add enable password if provided
            if self.device_creds.enable_password:
                connection_args["enable_password"] = self.device_creds.enable_password
            
            logger.info(f"Connecting to {self.device_creds.hostname}")
            
            # Create and connect
            self.connection = Connection(**connection_args)
            self.connection.connect()
            
            logger.info(f"Successfully connected to {self.device_creds.hostname}")
            return self.connection
            
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Failed to connect to {self.device_creds.hostname}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to {self.device_creds.hostname}: {e}")
            raise
    
    def execute_command(self, command: ShowCommand) -> str:
        """Execute a show command on the device.
        
        Args:
            command: ShowCommand object with command and optional pipe filters
            
        Returns:
            Command output as string
            
        Raises:
            RuntimeError: If device is not connected
            Exception: If command execution fails
        """
        if not self.connection or not self.connection.connected:
            raise RuntimeError(f"Device {self.device_creds.hostname} not connected")
        
        try:
            # Get the full command with pipe options
            full_command = command.get_full_command()
            
            logger.info(f"Executing on {self.device_creds.hostname}: {full_command}")
            
            # Execute command
            output = self.connection.execute(
                full_command,
                timeout=self.timeout
            )
            
            return output
            
        except TimeoutError as e:
            logger.error(f"Command timeout on {self.device_creds.hostname}: {e}")
            raise
        except Exception as e:
            logger.error(f"Command execution failed on {self.device_creds.hostname}: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from the device."""
        if self.connection:
            try:
                logger.info(f"Disconnecting from {self.device_creds.hostname}")
                self.connection.disconnect()
            except Exception as e:
                logger.warning(f"Error during disconnect from {self.device_creds.hostname}: {e}")
            finally:
                self.connection = None
        
        # Close jumphost channel if used
        if self._jumphost_channel:
            try:
                self._jumphost_channel.close()
            except Exception as e:
                logger.warning(f"Error closing jumphost channel: {e}")
            finally:
                self._jumphost_channel = None

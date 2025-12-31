"""PyATS/Unicon device connection manager."""

import logging
from typing import Optional, Dict, Any
from unicon.core.errors import ConnectionError, TimeoutError
from unicon import Connection
from app.models import DeviceCredentials, ShowCommand
from app.jumphost import JumphostManager

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manages connections to network devices using PyATS/Unicon."""
    
    def __init__(
        self,
        device_creds: DeviceCredentials,
        jumphost_manager: Optional[JumphostManager] = None,
        timeout: int = 30
    ):
        """Initialize device manager.
        
        Args:
            device_creds: Device credentials and connection info
            jumphost_manager: Optional jumphost manager for proxy connections
            timeout: Command timeout in seconds
        """
        self.device_creds = device_creds
        self.jumphost_manager = jumphost_manager
        self.timeout = timeout
        self.connection: Optional[Connection] = None
        self._jumphost_channel = None
    
    def connect(self) -> Connection:
        """Establish connection to the device.
        
        Returns:
            Connected Unicon Connection object
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            # Build connection parameters
            connection_args: Dict[str, Any] = {
                "hostname": self.device_creds.hostname,
                "start": ["ssh {}@{}".format(
                    self.device_creds.username,
                    self.device_creds.hostname
                )],
                "os": self.device_creds.os.value,
                "username": self.device_creds.username,
                "password": self.device_creds.password,
                "port": self.device_creds.port,
                "log_stdout": False,  # Disable verbose logging for production
                "learn_hostname": True,  # Learn actual hostname from device
                "settings": {
                    "EXEC_TIMEOUT": self.timeout,
                    "POST_DISCONNECT_WAIT_SEC": 0,
                }
            }
            
            # Add enable password if provided
            if self.device_creds.enable_password:
                connection_args["enable_password"] = self.device_creds.enable_password
            
            # Handle jumphost connection
            if self.jumphost_manager:
                logger.info(f"Connecting to {self.device_creds.hostname} via jumphost")
                # Use sshpass to handle password auth through SSH ProxyJump
                # SSH config file handles ProxyJump automatically for 10.250.250.* hosts
                connection_args["start"] = [
                    f"sshpass -p '{self.device_creds.password}' ssh {self.device_creds.username}@{self.device_creds.hostname}"
                ]
                logger.info(f"Using SSH config with sshpass for jumphost connection")
            else:
                logger.info(f"Connecting directly to {self.device_creds.hostname}")
            
            # Create connection
            self.connection = Connection(**connection_args)
            
            # Connect to device
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

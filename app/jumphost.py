"""SSH Jumphost connection handler using Paramiko."""

import paramiko
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class JumphostManager:
    """Manages SSH jumphost connections for proxying to network devices."""
    
    def __init__(
        self,
        jumphost_host: str,
        jumphost_port: int,
        jumphost_username: str,
        jumphost_key_path: str
    ):
        """Initialize jumphost manager.
        
        Args:
            jumphost_host: Jumphost hostname or IP
            jumphost_port: Jumphost SSH port
            jumphost_username: Jumphost username
            jumphost_key_path: Path to private key for jumphost authentication
        """
        self.jumphost_host = jumphost_host
        self.jumphost_port = jumphost_port
        self.jumphost_username = jumphost_username
        self.jumphost_key_path = jumphost_key_path
        self.client: Optional[paramiko.SSHClient] = None
        
    def connect(self) -> paramiko.SSHClient:
        """Establish connection to jumphost.
        
        Returns:
            Connected Paramiko SSHClient
            
        Raises:
            Exception: If connection fails
        """
        try:
            # Load private key
            key_path = Path(self.jumphost_key_path).expanduser()
            
            if not key_path.exists():
                raise FileNotFoundError(f"SSH key not found: {key_path}")
            
            # Try different key types
            private_key = None
            for key_class in [paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey]:
                try:
                    private_key = key_class.from_private_key_file(str(key_path))
                    break
                except paramiko.SSHException:
                    continue
            
            if private_key is None:
                raise ValueError(f"Unable to load private key from {key_path}")
            
            # Create SSH client
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect to jumphost
            logger.info(f"Connecting to jumphost {self.jumphost_host}:{self.jumphost_port}")
            self.client.connect(
                hostname=self.jumphost_host,
                port=self.jumphost_port,
                username=self.jumphost_username,
                pkey=private_key,
                timeout=10
            )
            
            logger.info("Jumphost connection established")
            return self.client
            
        except Exception as e:
            logger.error(f"Failed to connect to jumphost: {e}")
            raise
    
    def get_transport_channel(self, dest_host: str, dest_port: int):
        """Create a channel through the jumphost to the destination.
        
        Args:
            dest_host: Destination device hostname/IP
            dest_port: Destination device port
            
        Returns:
            Paramiko channel for tunneling
        """
        if not self.client or not self.client.get_transport():
            raise RuntimeError("Jumphost not connected")
        
        try:
            logger.info(f"Creating tunnel to {dest_host}:{dest_port} through jumphost")
            transport = self.client.get_transport()
            channel = transport.open_channel(
                "direct-tcpip",
                (dest_host, dest_port),
                ("127.0.0.1", 0)
            )
            return channel
        except Exception as e:
            logger.error(f"Failed to create channel: {e}")
            raise
    
    def disconnect(self):
        """Close jumphost connection."""
        if self.client:
            logger.info("Disconnecting from jumphost")
            self.client.close()
            self.client = None

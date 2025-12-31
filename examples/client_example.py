#!/usr/bin/env python3
"""
Example Python client for the PyATS Show Command API.

Usage:
    python examples/client_example.py
"""

import requests
import json
from typing import List, Dict, Any


class PyATSAPIClient:
    """Client for PyATS Show Command API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize API client.
        
        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health.
        
        Returns:
            Health status response
        """
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def execute_commands(
        self,
        devices: List[Dict[str, Any]],
        commands: List[Dict[str, Any]],
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Execute show commands on devices.
        
        Args:
            devices: List of device credentials
            commands: List of commands to execute
            timeout: Command timeout in seconds
            
        Returns:
            API response with command results
        """
        payload = {
            "devices": devices,
            "commands": commands,
            "timeout": timeout
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/execute",
            json=payload
        )
        response.raise_for_status()
        return response.json()


def example_basic():
    """Example: Basic show command on single device."""
    print("\n=== Example 1: Basic Show Command ===")
    
    client = PyATSAPIClient()
    
    # Check API health
    health = client.health_check()
    print(f"API Status: {health['status']}")
    
    # Execute command
    result = client.execute_commands(
        devices=[
            {
                "hostname": "192.168.1.1",
                "username": "admin",
                "password": "cisco123",
                "os": "iosxe"
            }
        ],
        commands=[
            {"command": "show version"}
        ]
    )
    
    print(f"\nDevices processed: {result['total_devices']}")
    print(f"Successful: {result['successful_devices']}")
    print(f"Failed: {result['failed_devices']}")
    
    for device_result in result['results']:
        print(f"\n--- Device: {device_result['hostname']} ---")
        print(f"Success: {device_result['success']}")
        
        for cmd_result in device_result['commands']:
            print(f"\nCommand: {cmd_result['command']}")
            print(f"Success: {cmd_result['success']}")
            if cmd_result['success']:
                print(f"Output:\n{cmd_result['output'][:200]}...")
            else:
                print(f"Error: {cmd_result['error']}")


def example_with_pipes():
    """Example: Show commands with pipe filters."""
    print("\n=== Example 2: Commands with Pipe Filters ===")
    
    client = PyATSAPIClient()
    
    result = client.execute_commands(
        devices=[
            {
                "hostname": "192.168.1.1",
                "username": "admin",
                "password": "cisco123",
                "os": "iosxe"
            }
        ],
        commands=[
            {
                "command": "show running-config",
                "pipe_option": "include",
                "pipe_value": "interface"
            },
            {
                "command": "show ip route",
                "pipe_option": "exclude",
                "pipe_value": "local"
            }
        ]
    )
    
    for device_result in result['results']:
        print(f"\n--- Device: {device_result['hostname']} ---")
        for cmd_result in device_result['commands']:
            print(f"\nCommand: {cmd_result['command']}")
            print(f"Output lines: {len(cmd_result['output'].splitlines())}")


def example_multiple_devices():
    """Example: Execute commands on multiple devices."""
    print("\n=== Example 3: Multiple Devices ===")
    
    client = PyATSAPIClient()
    
    result = client.execute_commands(
        devices=[
            {
                "hostname": "192.168.1.1",
                "username": "admin",
                "password": "cisco123",
                "os": "iosxe"
            },
            {
                "hostname": "192.168.1.2",
                "username": "admin",
                "password": "cisco123",
                "os": "nxos"
            }
        ],
        commands=[
            {"command": "show version"},
            {"command": "show ip interface brief"}
        ]
    )
    
    print(f"\nTotal devices: {result['total_devices']}")
    print(f"Successful: {result['successful_devices']}")
    print(f"Failed: {result['failed_devices']}")
    
    for device_result in result['results']:
        print(f"\n--- Device: {device_result['hostname']} ---")
        print(f"Status: {'✓' if device_result['success'] else '✗'}")
        print(f"Commands executed: {len(device_result['commands'])}")


def example_with_enable_password():
    """Example: Show commands with enable password."""
    print("\n=== Example 4: With Enable Password ===")
    
    client = PyATSAPIClient()
    
    result = client.execute_commands(
        devices=[
            {
                "hostname": "192.168.1.1",
                "username": "admin",
                "password": "cisco123",
                "os": "ios",
                "enable_password": "enable123"
            }
        ],
        commands=[
            {"command": "show running-config"}
        ]
    )
    
    print(f"\nDevice processed with enable password!")
    print(f"Devices processed: {result['total_devices']}")


if __name__ == "__main__":
    print("PyATS Show Command API - Client Examples")
    print("=" * 50)
    
    try:
        # Run examples (comment out examples you don't want to run)
        example_basic()
        # example_with_pipes()
        # example_multiple_devices()
        # example_with_enable_password()
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("Make sure the server is running: python run.py")
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ API Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

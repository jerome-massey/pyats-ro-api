#!/usr/bin/env python3
"""Test script to validate model changes and JunOS error handling."""

import sys
from pydantic import ValidationError

# Import the models
from app.models import DeviceCredentials, ShowCommand, ShowCommandRequest

def test_junos_validation():
    """Test that JunOS is rejected with helpful error message."""
    print("Test 1: Testing JunOS validation error...")
    try:
        device = DeviceCredentials(
            hostname="192.168.1.1",
            username="admin",
            password="test123",
            os="junos"
        )
        print("❌ FAILED: JunOS should have been rejected")
        return False
    except ValidationError as e:
        error_msg = str(e)
        if "junos" in error_msg.lower() and "not supported" in error_msg.lower():
            print(f"✅ PASSED: JunOS correctly rejected with message:")
            print(f"   {e.errors()[0]['msg']}")
            return True
        else:
            print(f"❌ FAILED: Wrong error message: {error_msg}")
            return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {e}")
        return False


def test_valid_os_types():
    """Test that valid Cisco OS types still work."""
    print("\nTest 2: Testing valid OS types...")
    valid_os_types = ["ios", "iosxe", "iosxr", "nxos", "asa"]
    results = []
    
    for os_type in valid_os_types:
        try:
            device = DeviceCredentials(
                hostname="192.168.1.1",
                username="admin",
                password="test123",
                os=os_type
            )
            print(f"✅ PASSED: {os_type.upper()} accepted")
            results.append(True)
        except ValidationError as e:
            print(f"❌ FAILED: {os_type.upper()} rejected: {e}")
            results.append(False)
        except Exception as e:
            print(f"❌ FAILED: {os_type.upper()} unexpected error: {e}")
            results.append(False)
    
    return all(results)


def test_show_command_validation():
    """Test that show command validation still works."""
    print("\nTest 3: Testing show command validation...")
    
    # Valid command
    try:
        cmd = ShowCommand(command="show version")
        print("✅ PASSED: Valid show command accepted")
        test1 = True
    except Exception as e:
        print(f"❌ FAILED: Valid command rejected: {e}")
        test1 = False
    
    # Invalid command (not starting with show)
    try:
        cmd = ShowCommand(command="configure terminal")
        print("❌ FAILED: Non-show command should be rejected")
        test2 = False
    except ValidationError as e:
        if "show" in str(e).lower():
            print("✅ PASSED: Non-show command correctly rejected")
            test2 = True
        else:
            print(f"❌ FAILED: Wrong error for non-show command: {e}")
            test2 = False
    
    # Command with pipe
    try:
        cmd = ShowCommand(
            command="show running-config",
            pipe_option="include",
            pipe_value="interface"
        )
        full_cmd = cmd.get_full_command()
        if "| include interface" in full_cmd:
            print(f"✅ PASSED: Pipe command works: {full_cmd}")
            test3 = True
        else:
            print(f"❌ FAILED: Pipe command incorrect: {full_cmd}")
            test3 = False
    except Exception as e:
        print(f"❌ FAILED: Pipe command error: {e}")
        test3 = False
    
    return all([test1, test2, test3])


def test_request_model():
    """Test the full request model."""
    print("\nTest 4: Testing full request model...")
    
    try:
        request = ShowCommandRequest(
            devices=[
                DeviceCredentials(
                    hostname="192.168.1.1",
                    username="admin",
                    password="cisco123",
                    os="ios"
                ),
                DeviceCredentials(
                    hostname="192.168.1.2",
                    username="admin",
                    password="cisco123",
                    os="iosxe",
                    enable_password="enable123"
                )
            ],
            commands=[
                ShowCommand(command="show version"),
                ShowCommand(
                    command="show ip interface brief",
                    pipe_option="include",
                    pipe_value="up"
                )
            ],
            timeout=30
        )
        print("✅ PASSED: Full request model validated successfully")
        print(f"   Devices: {len(request.devices)}")
        print(f"   Commands: {len(request.commands)}")
        return True
    except Exception as e:
        print(f"❌ FAILED: Request model error: {e}")
        return False


def test_junos_case_variations():
    """Test JunOS rejection with different case variations."""
    print("\nTest 5: Testing JunOS case variations...")
    
    test_cases = ["junos", "JUNOS", "JunOS", "Junos"]
    results = []
    
    for os_value in test_cases:
        try:
            device = DeviceCredentials(
                hostname="192.168.1.1",
                username="admin",
                password="test123",
                os=os_value
            )
            print(f"❌ FAILED: '{os_value}' should have been rejected")
            results.append(False)
        except ValidationError as e:
            if "not supported" in str(e).lower():
                print(f"✅ PASSED: '{os_value}' correctly rejected")
                results.append(True)
            else:
                print(f"❌ FAILED: '{os_value}' wrong error: {e}")
                results.append(False)
        except Exception as e:
            print(f"❌ FAILED: '{os_value}' unexpected error: {e}")
            results.append(False)
    
    return all(results)


def main():
    """Run all tests."""
    print("=" * 70)
    print("PyATS API Validation Tests")
    print("=" * 70)
    
    results = []
    
    results.append(test_junos_validation())
    results.append(test_valid_os_types())
    results.append(test_show_command_validation())
    results.append(test_request_model())
    results.append(test_junos_case_variations())
    
    print("\n" + "=" * 70)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 70)
    
    if all(results):
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

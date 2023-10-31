"""
This module provides VPN utility functions for Historical Data Fetching

Imports:
- os: Module for interacting with the operating system.
- re: Module for working with regular expressions.
- subprocess: Module for running shell commands.
- time: Module for working with time.
- pexpect: Library for automating interactive shell applications.
- load_dotenv from dotenv: Library for loading environment variables from a .env file.
- colored from termcolor: Library for adding color to text.
- logger from Historical_Data.log_config: Custom logger for logging messages.

Function: is_ping_successful
- Check if a ping to 'google.com' is successful.
- Returns: True if the ping is successful, False otherwise.

Function: get_current_ip
- Get the current IP address using ProtonVPN.
- Returns: The current IP address or None if it's not found.

Function: vpn_connect
- Connect to ProtonVPN.
- Returns: True if successfully connected, False otherwise.

Function: vpn_disconnect
- Disconnect from ProtonVPN.
- Returns: None

Main Execution:
- Connects to ProtonVPN using vpn_connect function.
- Disconnects from ProtonVPN using vpn_disconnect function.

The code relies on the ProtonVPN command-line tool and the log_config module for logging.
"""


# System and Standard Library Imports
import os
import re
import subprocess
import time

# Third-Party Library Imports
import pexpect
from dotenv import load_dotenv
from termcolor import colored

# Local Imports
from log_config import logger

load_dotenv()
SUDO_VPN = os.environ.get("SUDO_VPN").lower() == "true"
PROTONVPN_CMD = os.environ.get("PROTONVPN_CMD")
logger.info(f"PROTONVPN_CMD: {PROTONVPN_CMD}")


def is_ping_successful() -> bool:
    """
    Check if a ping to 'google.com' is successful.

    Returns:
        bool: True if the ping is successful, False otherwise.
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", "google.com"], capture_output=True, text=True
        )
        # Check the return code to determine if the ping was successful
        if result.returncode == 0:
            return True
        else:
            return False
    except subprocess.SubprocessError:
        return False


def get_current_ip() -> str:
    """
    Get the current IP address using ProtonVPN.

    Returns:
        str: The current IP address or None if it's not found.
    """
    if SUDO_VPN:
        load_dotenv()
        sudo_password = os.environ.get("SUDO_PASSWORD")
        if not sudo_password:
            logger.error("SUDO_PASSWORD Environment Variable not found.")
            return

        connect_command = ["sudo", "-S", PROTONVPN_CMD, "s"]
        result = subprocess.run(
            connect_command,
            input=f"{sudo_password}\n".encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    else:
        connect_command = [PROTONVPN_CMD, "s"]
        result = subprocess.run(
            connect_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    ip_pattern = r"IP:\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    match = re.search(ip_pattern, result.stdout.decode("utf-8"))
    if match:
        logger.success(f"Current IP: {match.group(1)}")
        return match.group(1)
    else:
        logger.error("IP not found")
        return None


def vpn_connect() -> bool:
    """
    Connect to ProtonVPN.

    Returns:
        bool: True if successfully connected, False otherwise.
    """

    print("Rate limit exceeded. Connecting to VPN...")
    logger.warning("Rate limit exceeded. Connecting to VPN...")

    connected = False
    original_ip = get_current_ip()
    logger.info(f"Original IP address: {colored(original_ip, 'yellow')}")

    while not connected:
        try:
            if SUDO_VPN:
                load_dotenv()
                sudo_password = os.environ.get("SUDO_PASSWORD")
                if not sudo_password:
                    logger.error("SUDO_PASSWORD Environment Variable not found.")
                    return
                # Connect to a random ProtonVPN server
                connect_command = ["sudo", "-S", PROTONVPN_CMD, "c", "-r"]
                subprocess.run(
                    connect_command,
                    input=f"{sudo_password}\n".encode("utf-8"),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
            else:
                connect_command = [PROTONVPN_CMD, "c", "-r"]
                subprocess.run(
                    connect_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )

            time.sleep(3)
            new_ip = get_current_ip()
            logger.info(f"\nNew IP address: {colored(new_ip, 'yellow')}")

            if new_ip != original_ip and new_ip is not None and is_ping_successful():
                connected = True
                logger.success(colored("Connected!", "green", attrs=["bold"]))
                print(colored("Connected!", "green", attrs=["bold"]))

        except pexpect.exceptions.ExceptionPexpect as e:
            logger.error(f"Error connecting to ProtonVPN: {e}")
            logger.info("Reconnecting")

            if SUDO_VPN:
                subprocess.check_output(
                    [
                        "echo",
                        f"{sudo_password}",
                        "|",
                        "sudo",
                        "-S",
                        PROTONVPN_CMD,
                        "reconnect",
                    ]
                )
            else:
                subprocess.check_output(
                    [
                        "echo",
                        PROTONVPN_CMD,
                        "reconnect",
                    ]
                )
            logger.info("Reconnected")

    if connected:
        return connected


def vpn_disconnect():
    """
    Disconnect from ProtonVPN.
    """
    logger.info("Disconnecting VPN")

    if SUDO_VPN:
        load_dotenv()
        sudo_password = os.environ.get("SUDO_PASSWORD")
        connect_command = ["sudo", "-S", PROTONVPN_CMD, "d"]
        subprocess.run(
            connect_command,
            input=f"{sudo_password}\n".encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    else:
        connect_command = [PROTONVPN_CMD, "d"]
        subprocess.run(
            connect_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    logger.success("VPN Disconnected!")


if __name__ == "__main__":
    vpn_connect()
    vpn_disconnect()

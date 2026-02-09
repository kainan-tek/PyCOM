"""
Serial port manager module.

This module provides a SerialManager class for managing serial port operations
including opening, closing, and configuring serial ports.
"""

import serial
import serial.tools.list_ports
from typing import Optional

import globalvar as gl
from logwrapper import logger


class SerialManager:
    """
    Manages serial port operations.

    This class encapsulates all serial port related operations including
    port scanning, opening, closing, and configuration.
    """

    def __init__(self) -> None:
        """Initialize the serial manager."""
        self.serial_instance: serial.Serial = serial.Serial()
        self.log = logger.logger

    def scan_ports(self) -> list[str]:
        """
        Scan and return available serial ports.

        Returns:
            List of available port names.
        """
        try:
            ports_list = [port.device for port in serial.tools.list_ports.comports()]
            self.log.info(f"Found {len(ports_list)} serial ports")
            return ports_list
        except Exception as e:
            self.log.error(f"Error scanning ports: {str(e)}")
            return []

    def open_port(
        self,
        port: str,
        baudrate: int = 115200,
        bytesize: int = 8,
        stopbits: int = 1,
        parity: str = "N",
        timeout: float = 0.01,
    ) -> tuple[bool, str]:
        """
        Open a serial port with specified parameters.

        Args:
            port: Port name (e.g., 'COM3', '/dev/ttyUSB0')
            baudrate: Baud rate (default: 115200)
            bytesize: Data bits (default: 8)
            stopbits: Stop bits (default: 1)
            parity: Parity ('N', 'E', 'O') (default: 'N')
            timeout: Read timeout in seconds (default: 0.01)

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not port:
            return False, "No port selected"

        # Configure the serial instance
        self.serial_instance.port = port
        self.serial_instance.baudrate = baudrate
        self.serial_instance.bytesize = bytesize
        self.serial_instance.stopbits = stopbits
        self.serial_instance.parity = parity
        self.serial_instance.timeout = timeout

        # Try to open the port
        if not self.serial_instance.is_open:
            try:
                self.serial_instance.open()
                self.log.info(f"Port {port} opened successfully")
                return True, f"Port {port} opened successfully"
            except (serial.SerialException, OSError, ValueError) as err:
                error_msg = (
                    "The selected port may be occupied."
                    if "Permission" in str(err)
                    else "Cannot open the port with these parameters."
                )
                self.log.error(f"{error_msg} Error: {err}")
                return False, error_msg

        return True, "Port already open"

    def close_port(self) -> tuple[bool, str]:
        """
        Close the serial port.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self.serial_instance.is_open:
            try:
                self.serial_instance.close()
                self.log.info("Serial port closed successfully")
                return True, "Port closed successfully"
            except (serial.SerialException, OSError) as e:
                self.log.error(f"Error closing serial port: {str(e)}")
                return False, f"Error closing port: {str(e)}"

        return True, "Port already closed"

    def is_open(self) -> bool:
        """
        Check if the serial port is open.

        Returns:
            True if port is open, False otherwise.
        """
        return self.serial_instance.is_open

    def write(self, data: bytes) -> int:
        """
        Write data to the serial port.

        Args:
            data: Bytes to write

        Returns:
            Number of bytes written, 0 if failed
        """
        if not self.is_open():
            self.log.warning("Attempted to write but port is not open")
            return 0

        if not data:
            self.log.warning("Attempted to write empty data")
            return 0

        try:
            bytes_written = self.serial_instance.write(data) or 0
            return bytes_written
        except (serial.SerialException, OSError, IOError) as e:
            self.log.error(f"Serial write error: {str(e)}")
            return 0

    def read_all(self) -> bytes:
        """
        Read all available data from the serial port.

        Returns:
            Bytes read from the port, empty bytes if failed
        """
        if not self.is_open():
            return b""

        try:
            return self.serial_instance.readall()
        except (serial.SerialException, OSError, IOError) as e:
            self.log.error(f"Serial read error: {str(e)}")
            return b""

    def get_instance(self) -> serial.Serial:
        """
        Get the underlying serial instance.

        Returns:
            The serial.Serial instance
        """
        return self.serial_instance

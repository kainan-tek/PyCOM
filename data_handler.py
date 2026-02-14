"""
Data handler module.

This module provides classes for handling data operations including conversion,
sending, and receiving data through serial port.
"""

import os
import queue
import string
import threading
from typing import Optional

from PySide6.QtCore import QThread, Signal

from serial_manager import SerialManager
import globalvar as gl
from logwrapper import logger


class DataConverter:
    """
    Handles data format conversions.

    Provides methods for converting between text, hex, and bytes formats.
    """

    def __init__(self, encoding: str = "gbk") -> None:
        """
        Initialize the data converter.

        Args:
            encoding: Default encoding for text conversion (default: "gbk")
        """
        self.encoding = encoding
        self.log = logger.logger
        self.byte_buffer: bytes = b""  # Buffer for incomplete multi-byte characters

    def set_encoding(self, encoding: str) -> None:
        """
        Set the encoding for text conversion.

        Args:
            encoding: Encoding name (e.g., "utf-8", "gbk")
        """
        self.encoding = encoding
        self.log.info(f"Encoding set to: {encoding}")

    def is_valid_hex(self, text: str) -> tuple[bool, str]:
        """
        Check if the text is valid hex and return cleaned hex string.

        Args:
            text: Text to validate

        Returns:
            Tuple of (is_valid: bool, cleaned_hex: str)
        """
        cleaned = text.replace(" ", "")
        is_valid = (len(cleaned) % 2 == 0) and all(c in string.hexdigits for c in cleaned)
        return is_valid, cleaned

    def text_to_bytes(self, text: str, add_newline: bool = False) -> bytes:
        """
        Convert text to bytes.

        Args:
            text: Text to convert
            add_newline: Whether to add newline at the end

        Returns:
            Converted bytes
        """
        try:
            if add_newline:
                text += os.linesep
            return text.encode(self.encoding, "replace")
        except (ValueError, UnicodeEncodeError) as e:
            self.log.error(f"Error converting text to bytes: {e}")
            return b""

    def hex_to_bytes(self, hex_str: str, add_newline: bool = False) -> tuple[bool, bytes]:
        """
        Convert hex string to bytes.

        Args:
            hex_str: Hex string to convert (e.g., "48 65 6C 6C 6F")
            add_newline: Whether to add newline at the end

        Returns:
            Tuple of (success: bool, converted_bytes: bytes)
        """
        is_valid, cleaned_hex = self.is_valid_hex(hex_str)
        if not is_valid:
            self.log.warning(f"Invalid hex format: {hex_str}")
            return False, b""

        try:
            bytes_data = bytes.fromhex(cleaned_hex)
            if add_newline:
                bytes_data += os.linesep.encode(self.encoding, "replace")
            return True, bytes_data
        except (ValueError, UnicodeEncodeError) as e:
            self.log.error(f"Error converting hex to bytes: {e}")
            return False, b""

    def bytes_to_text(self, data: bytes) -> str:
        """
        Convert bytes to text with support for multi-byte characters.
        Handles incomplete multi-byte characters using a buffer.

        Args:
            data: Bytes to convert

        Returns:
            Converted text
        """
        if not data:
            return ""

        # Add new data to buffer
        self.byte_buffer += data

        if self.encoding.lower() in ["utf-8", "utf8"]:
            return self._utf8_bytes_to_text()
        elif self.encoding.lower() in ["gbk", "cp936"]:
            return self._gbk_bytes_to_text()
        else:
            # For other encodings, use simple decode
            try:
                text = self.byte_buffer.decode(self.encoding, "replace")
                self.byte_buffer = b""  # Clear buffer
                return text
            except (ValueError, UnicodeDecodeError) as e:
                self.log.error(f"Error converting bytes to text: {e}")
                self.byte_buffer = b""  # Clear buffer on error
                return ""

    def _utf8_bytes_to_text(self) -> str:
        """
        Convert UTF-8 bytes to text, handling incomplete characters.
        """
        buffer_len = len(self.byte_buffer)
        if buffer_len == 0:
            return ""

        # Find the last complete UTF-8 character boundary
        i = buffer_len - 1
        while i >= 0:
            byte = self.byte_buffer[i]
            # Check if this byte is the start of a UTF-8 character
            if byte < 0x80:  # Single-byte character
                break
            elif (byte & 0xC0) == 0xC0:  # Start of multi-byte character
                # Determine how many bytes this character should have
                if (byte & 0xE0) == 0xC0:  # 2-byte
                    required = 2
                elif (byte & 0xF0) == 0xE0:  # 3-byte
                    required = 3
                elif (byte & 0xF8) == 0xF0:  # 4-byte
                    required = 4
                else:
                    # Invalid UTF-8 leading byte, treat as error
                    i -= 1
                    continue

                # Check if we have enough bytes for this character
                if buffer_len - i >= required:
                    break
                else:
                    # Not enough bytes, move to previous potential start
                    i -= 1
            else:
                # Continuation byte, move back
                i -= 1

        if i < 0:
            # No complete characters
            return ""

        # Split buffer into complete and incomplete parts
        complete_data = self.byte_buffer[: i + 1]
        self.byte_buffer = self.byte_buffer[i + 1 :]

        try:
            return complete_data.decode("utf-8", "replace")
        except (ValueError, UnicodeDecodeError) as e:
            self.log.error(f"Error converting UTF-8 bytes to text: {e}")
            self.byte_buffer = b""  # Clear buffer on error
            return ""

    def _gbk_bytes_to_text(self) -> str:
        """
        Convert GBK bytes to text, handling incomplete characters.
        """
        buffer_len = len(self.byte_buffer)
        if buffer_len == 0:
            return ""

        # Find the last complete GBK character boundary
        i = buffer_len - 1
        while i >= 0:
            byte = self.byte_buffer[i]
            # Check if this byte is the start of a GBK character
            if byte < 0x80:  # Single-byte (ASCII)
                break
            elif 0x81 <= byte <= 0xFE:  # Start of 2-byte GBK
                # Check if we have enough bytes
                if i + 1 < buffer_len:
                    break
                else:
                    # Not enough bytes, move to previous
                    i -= 1
            else:
                # Invalid GBK byte, move back
                i -= 1

        if i < 0:
            # No complete characters
            return ""

        # Split buffer into complete and incomplete parts
        complete_data = self.byte_buffer[: i + 1]
        self.byte_buffer = self.byte_buffer[i + 1 :]

        try:
            return complete_data.decode("gbk", "replace")
        except (ValueError, UnicodeDecodeError) as e:
            self.log.error(f"Error converting GBK bytes to text: {e}")
            self.byte_buffer = b""  # Clear buffer on error
            return ""

    def bytes_to_hex(self, data: bytes, separator: str = " ") -> str:
        """
        Convert bytes to hex string.

        Args:
            data: Bytes to convert
            separator: Separator between hex values (default: " ")

        Returns:
            Hex string
        """
        try:
            return data.hex(separator)
        except Exception as e:
            self.log.error(f"Error converting bytes to hex: {e}")
            return ""

    def text_to_hex(self, text: str) -> str:
        """
        Convert text to hex string.

        Args:
            text: Text to convert

        Returns:
            Hex string with space separator
        """
        try:
            return text.encode(self.encoding, "replace").hex(" ")
        except (ValueError, UnicodeEncodeError) as e:
            self.log.error(f"Error converting text to hex: {e}")
            return ""

    def hex_to_text(self, hex_str: str) -> tuple[bool, str]:
        """
        Convert hex string to text.

        Args:
            hex_str: Hex string to convert

        Returns:
            Tuple of (success: bool, converted_text: str)
        """
        is_valid, cleaned_hex = self.is_valid_hex(hex_str)
        if not is_valid:
            return False, ""

        try:
            text = bytes.fromhex(cleaned_hex).decode(self.encoding, "replace")
            return True, text
        except (ValueError, UnicodeDecodeError) as e:
            self.log.error(f"Error converting hex to text: {e}")
            return False, ""

    def prepare_send_data(
        self, text: str, is_hex: bool, add_newline: bool = False
    ) -> tuple[bool, bytes]:
        """
        Prepare data for sending based on format.

        Args:
            text: Text or hex string to prepare
            is_hex: Whether the input is hex format
            add_newline: Whether to add newline at the end

        Returns:
            Tuple of (success: bool, prepared_bytes: bytes)
        """
        if is_hex:
            return self.hex_to_bytes(text, add_newline)
        else:
            bytes_data = self.text_to_bytes(text, add_newline)
            return len(bytes_data) > 0, bytes_data


class DataSender:
    """
    Handles data sending operations.

    This class manages sending data through serial port with support for
    text, hex, and file formats.
    """

    def __init__(
        self, serial_manager: SerialManager, data_converter: Optional[DataConverter] = None
    ) -> None:
        """
        Initialize the data sender.

        Args:
            serial_manager: Serial port manager instance
            data_converter: Data converter instance (optional)
        """
        self.serial_manager = serial_manager
        self.data_converter = data_converter or DataConverter()
        self.log = logger.logger
        self.total_sent = 0

    def send_text(self, text: str, add_newline: bool = False) -> tuple[bool, int]:
        """
        Send text data.

        Args:
            text: Text to send
            add_newline: Whether to add newline at the end

        Returns:
            Tuple of (success: bool, bytes_sent: int)
        """
        if not text:
            self.log.warning("Attempted to send empty text")
            return False, 0

        if not self.serial_manager.is_open():
            self.log.warning("Cannot send: port is not open")
            return False, 0

        bytes_data = self.data_converter.text_to_bytes(text, add_newline)
        if not bytes_data:
            return False, 0

        bytes_sent = self.serial_manager.write(bytes_data)
        if bytes_sent > 0:
            self.total_sent += bytes_sent
            return True, bytes_sent

        return False, 0

    def send_hex(self, hex_str: str, add_newline: bool = False) -> tuple[bool, int]:
        """
        Send hex data.

        Args:
            hex_str: Hex string to send (e.g., "48 65 6C 6C 6F")
            add_newline: Whether to add newline at the end

        Returns:
            Tuple of (success: bool, bytes_sent: int)
        """
        if not hex_str:
            self.log.warning("Attempted to send empty hex")
            return False, 0

        if not self.serial_manager.is_open():
            self.log.warning("Cannot send: port is not open")
            return False, 0

        success, bytes_data = self.data_converter.hex_to_bytes(hex_str, add_newline)
        if not success or not bytes_data:
            self.log.warning("Invalid hex format")
            return False, 0

        bytes_sent = self.serial_manager.write(bytes_data)
        if bytes_sent > 0:
            self.total_sent += bytes_sent
            return True, bytes_sent

        return False, 0

    def send_data(self, text: str, is_hex: bool, add_newline: bool = False) -> tuple[bool, int]:
        """
        Send data in specified format.

        Args:
            text: Text or hex string to send
            is_hex: Whether the input is hex format
            add_newline: Whether to add newline at the end

        Returns:
            Tuple of (success: bool, bytes_sent: int)
        """
        if is_hex:
            return self.send_hex(text, add_newline)
        else:
            return self.send_text(text, add_newline)

    def send_bytes(self, data: bytes) -> tuple[bool, int]:
        """
        Send raw bytes.

        Args:
            data: Bytes to send

        Returns:
            Tuple of (success: bool, bytes_sent: int)
        """
        if not data:
            self.log.warning("Attempted to send empty bytes")
            return False, 0

        if not self.serial_manager.is_open():
            self.log.warning("Cannot send: port is not open")
            return False, 0

        bytes_sent = self.serial_manager.write(data)
        if bytes_sent > 0:
            self.total_sent += bytes_sent
            return True, bytes_sent

        return False, 0

    def send_file_content(self, content: str) -> tuple[bool, int]:
        """
        Send file content.

        Args:
            content: File content to send

        Returns:
            Tuple of (success: bool, bytes_sent: int)
        """
        return self.send_text(content, add_newline=False)

    def get_total_sent(self) -> int:
        """
        Get total bytes sent.

        Returns:
            Total bytes sent
        """
        return self.total_sent

    def reset_counter(self) -> None:
        """Reset the sent bytes counter."""
        self.total_sent = 0
        self.log.debug("Sent bytes counter reset")


class DataReceiver(QThread):
    """
    Receives data from serial port in a separate thread.

    This class runs in a separate thread to continuously read data from
    the serial port without blocking the UI.

    Signals:
        port_closed: Emitted when port is closed
    """

    port_closed = Signal()

    def __init__(self, serial_manager: SerialManager, parent=None) -> None:
        """
        Initialize the data receiver.

        Args:
            serial_manager: Serial port manager instance
            parent: Parent QObject (optional)
        """
        super().__init__(parent)
        self.serial_manager = serial_manager
        self.receive_queue = queue.Queue(gl.RECEIVE_QUEUE_SIZE)
        self.close_port_flag = False
        self.total_received = 0
        self.total_dropped = 0  # Track dropped data
        self.log = logger.logger

    def run(self) -> None:
        """
        Run the receive thread.

        This method continuously reads data from the serial port and
        emits signals when data is received.
        """
        threading.current_thread().name = "DataReceiverThread"
        self.log.info("Data receiver thread started")

        while not self.isInterruptionRequested():
            # Handle port closed state
            if not self.serial_manager.is_open():
                self.msleep(100)
                continue

            # Read data from serial port
            try:
                data = self.serial_manager.read_all()
                if data:
                    try:
                        self.receive_queue.put_nowait(data)
                        self.total_received += len(data)
                    except queue.Full:
                        self.total_dropped += len(data)
                        self.log.error(f"Receive queue is full, dropped {len(data)} bytes")
            except Exception as e:
                self.log.error(f"Error reading from serial port: {str(e)}")
                self.close_port_flag = True
                self.msleep(100)

            # Handle port closing request
            if self.close_port_flag:
                success, msg = self.serial_manager.close_port()
                if success:
                    self.close_port_flag = False
                    self.port_closed.emit()
                    self.log.info("Port closed by receiver thread")
                else:
                    self.log.error(f"Failed to close port: {msg}")

            # Small sleep to prevent CPU overuse
            self.msleep(10)

        self.log.info("Data receiver thread stopped")

    def request_close_port(self) -> None:
        """Request to close the serial port."""
        self.close_port_flag = True
        self.log.debug("Port close requested")

    def get_data_from_queue(self) -> list[bytes]:
        """
        Get all data from the receive queue.

        Returns:
            List of received data chunks
        """
        data_list = []
        while not self.receive_queue.empty():
            try:
                data = self.receive_queue.get_nowait()
                data_list.append(data)
            except queue.Empty:
                break
        return data_list

    def get_total_received(self) -> int:
        """
        Get total bytes received.

        Returns:
            Total bytes received
        """
        return self.total_received

    def get_total_dropped(self) -> int:
        """
        Get total bytes dropped due to queue full.

        Returns:
            Total bytes dropped
        """
        return self.total_dropped

    def reset_counter(self) -> None:
        """Reset the received bytes counter."""
        self.total_received = 0
        self.total_dropped = 0
        self.log.debug("Received bytes counter reset")

    def clear_queue(self) -> None:
        """Clear the receive queue."""
        while not self.receive_queue.empty():
            try:
                self.receive_queue.get_nowait()
            except queue.Empty:
                break
        self.log.debug("Receive queue cleared")

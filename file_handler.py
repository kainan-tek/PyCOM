"""
File handler module.

This module provides utilities for handling file operations including
reading, encoding detection, and JSON processing.
"""

import os
import string
from typing import Optional

import chardet

from jsonparser import JsonParser, JsonFlag
from data_handler import DataConverter
from logwrapper import logger


class FileHandler:
    """
    Handles file operations for serial communication.

    This class provides methods for reading files, detecting encoding,
    and processing JSON configuration files.
    """

    def __init__(self, data_converter: Optional[DataConverter] = None) -> None:
        """
        Initialize the file handler.

        Args:
            data_converter: Data converter instance (optional)
        """
        self.data_converter = data_converter or DataConverter()
        self.log = logger.logger

    def predict_encoding(self, file_path: str) -> str:
        """
        Predict the encoding of a file.

        Args:
            file_path: Path to the file

        Returns:
            Detected encoding name (default: "utf-8")
        """
        try:
            with open(file_path, "rb") as f:
                sample_size = min(1024 * 1024, os.path.getsize(file_path))
                encode_info = chardet.detect(f.read(sample_size))
            encoding = encode_info.get("encoding") or "utf-8"
            self.log.info(f"Detected encoding: {encoding} for file: {file_path}")
            return encoding
        except (OSError, IOError) as e:
            self.log.error(f"Encoding prediction failed: {e}")
            return "utf-8"

    def read_text_file(self, file_path: str, encoding: Optional[str] = None) -> tuple[bool, str]:
        """
        Read a text file.

        Args:
            file_path: Path to the file
            encoding: File encoding (auto-detect if None)

        Returns:
            Tuple of (success: bool, content: str)
        """
        if not os.path.exists(file_path):
            self.log.error(f"File not found: {file_path}")
            return False, ""

        if encoding is None:
            encoding = self.predict_encoding(file_path)

        try:
            with open(file_path, mode="r", encoding=encoding, newline="") as fp:
                content = fp.read()
            self.log.info(f"Successfully read file: {file_path}")
            return True, content
        except (OSError, IOError, UnicodeDecodeError) as e:
            self.log.error(f"Error reading file: {e}")
            return False, ""

    def read_json_file(
        self, file_path: str, encoding: Optional[str] = None
    ) -> tuple[bool, Optional[dict]]:
        """
        Read and parse a JSON file.

        Args:
            file_path: Path to the JSON file
            encoding: File encoding (auto-detect if None)

        Returns:
            Tuple of (success: bool, json_data: dict or None)
        """
        if not os.path.exists(file_path):
            self.log.error(f"File not found: {file_path}")
            return False, None

        if encoding is None:
            encoding = self.predict_encoding(file_path)

        json_parser = JsonParser(file_path)
        flag, json_dict = json_parser.file_read(encoding)

        if flag != JsonFlag.SUCCESS:
            self.log.error(f"Error reading JSON file: {flag.name}")
            return False, None

        self.log.info(f"Successfully read JSON file: {file_path}")
        return True, json_dict

    def process_json_send_data(self, json_data: dict) -> tuple[bool, list[list]]:
        """
        Process JSON data for sending.

        Args:
            json_data: JSON data dictionary with 'cycle_ms', 'hexmode', 'datas'

        Returns:
            Tuple of (success: bool, send_list: list)
            send_list format: [[select, hexmode, sent_flag, data_bytes], ...]
        """
        try:
            cycle_time = json_data.get("cycle_ms", 0)
            hex_mode = json_data.get("hexmode", 0)
            datas = json_data.get("datas", [])

            if not datas:
                self.log.warning("No data items in JSON file")
                return False, []

            send_list = []

            for item in datas:
                data_str = item.get("data", "")
                select = item.get("select", 0)

                if hex_mode:
                    # Validate and convert hex data
                    cleaned_data = data_str.replace(" ", "")
                    if not all(c in string.hexdigits for c in cleaned_data):
                        self.log.error(f"Invalid hex data: {data_str}")
                        return False, []
                    data_bytes = bytes.fromhex(cleaned_data)
                else:
                    # Convert text data
                    data_bytes = data_str.encode(self.data_converter.encoding, "ignore")

                # Format: [select, hexmode, sent_flag, data_bytes]
                send_list.append([select, hex_mode, 0, data_bytes])

            self.log.info(f"Processed {len(send_list)} items from JSON")
            return True, send_list

        except (KeyError, TypeError, ValueError) as e:
            self.log.error(f"Error processing JSON data: {e}")
            return False, []

    def get_file_type(self, file_path: str) -> str:
        """
        Get file type based on extension.

        Args:
            file_path: Path to the file

        Returns:
            File type: "json", "txt", or "unknown"
        """
        basename = os.path.basename(file_path).lower()
        if "json" in basename:
            return "json"
        elif basename.endswith((".txt", ".log")):
            return "txt"
        else:
            return "unknown"

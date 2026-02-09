import os
import platform
import queue
import re
import string
import sys

from PySide6.QtCore import QEvent, QMutex, QObject, QThread, QTimer, Qt, Signal
from PySide6.QtGui import QCloseEvent, QIcon, QIntValidator, QKeyEvent, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
)
import chardet
import serial
import serial.tools.list_ports

from about import About
import globalvar as gl
from jsonparser import JsonFlag, JsonParser
from logwrapper import logger
from togglebt import ToggleButton
from ui.mainwindow_ui import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        """
        Initialize the main window class.
        """
        super().__init__()
        self.log = logger.logger
        self.log.info("PyCOM application starting")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.about = About()
        self.initialize_variables()
        self.initialize_gui()
        self.scan_serial_ports()

    def initialize_variables(self) -> None:
        """
        Initialize variables and objects for the main window.
        """
        # Initialize send/receive size tracking
        self.total_send_size: int = 0
        self.total_receive_size: int = 0
        self.received_data_file: str = ""

        # Initialize data encoding settings
        self.encode_info: str = "gbk"

        # Initialize data structures for sending
        self.multi_dict: dict = {}
        self.json_send_list: list = []

        # Initialize serial communication components
        self.mutex: QMutex = QMutex()
        self.message_box: QMessageBox = QMessageBox()
        self.serial_instance: serial.Serial = serial.Serial()

        # Initialize timers
        self.send_timer: QTimer = QTimer()
        self.send_timer.timeout.connect(self._timer_data_send)
        self.file_send_timer: QTimer = QTimer()
        self.file_send_timer.timeout.connect(self._timer_json_file_data_send)

        # Initialize and start the receive thread
        self.receive_thread: ReceiveThread = ReceiveThread(self.serial_instance, self)
        self.receive_thread.data_rec_signal.connect(self._update_receive_ui)
        self.receive_thread.port_closed_signal.connect(self._post_close_port)
        self.receive_thread.start()

        # Initialize keyboard limits for hex mode input validation
        self.key_limits = {
            *[getattr(Qt.Key, f"Key_{c}") for c in "0123456789ABCDEF"],
            Qt.Key.Key_Space,
            Qt.Key.Key_Backspace,
            Qt.Key.Key_Delete,
            Qt.Key.Key_Right,
            Qt.Key.Key_Left,
            Qt.Key.Key_Up,
            Qt.Key.Key_Down,
            Qt.Key.Key_Control,
            Qt.Key.Key_Shift,
        }

    def initialize_gui(self) -> None:
        """
        Initialize GUI components and set up event connections.
        """
        self._setup_window()
        self._setup_toggle_button()
        self._setup_menu_connections()
        self._setup_serial_controls()
        self._setup_receive_controls()
        self._setup_single_send_controls()
        self._setup_multi_send_controls()
        self._setup_file_send_controls()
        self._setup_guide()
        self._setup_status_bar()
        self._set_components_state(False)

    def _setup_window(self) -> None:
        """
        Set up window title and icon.
        """
        self.setWindowTitle(f"{gl.GUI_INFO['proj']} {gl.GUI_INFO['version']}")
        self.setWindowIcon(QIcon(":/icons/pycom"))

    def _setup_toggle_button(self) -> None:
        """
        Set up toggle button for port control.
        """
        self.toggle_btn = ToggleButton(self.ui.groupBox)
        self.toggle_btn.setGeometry(85, 265, 80, 30)
        self.toggle_btn.toggled.connect(self.port_toggle)

    def _setup_menu_connections(self) -> None:
        """
        Set up menu action connections.
        """
        self.ui.actionOpen_File.triggered.connect(self.action_open_file)
        self.ui.actionExit.triggered.connect(self.action_exit)
        self.ui.actionAbout.triggered.connect(self.action_about)
        self.ui.actionASCII.triggered.connect(lambda: self.action_encoding("ascii"))
        self.ui.actionUTF_8.triggered.connect(lambda: self.action_encoding("utf-8"))
        self.ui.actionUTF_16.triggered.connect(lambda: self.action_encoding("utf-16"))
        self.ui.actionUTF_32.triggered.connect(lambda: self.action_encoding("utf-32"))
        self.ui.actionGBK_GB2312.triggered.connect(lambda: self.action_encoding("gbk"))

    def _setup_serial_controls(self) -> None:
        """
        Set up serial port controls.
        """
        self.ui.comboBox_BRate.addItems(gl.SERIAL_INFO["baudrate"])
        self.ui.comboBox_BRate.setCurrentText("115200")
        self.ui.comboBox_BSize.addItems(gl.SERIAL_INFO["bytesize"])
        self.ui.comboBox_BSize.setCurrentText("8")
        self.ui.comboBox_SBit.addItems(gl.SERIAL_INFO["stopbit"])
        self.ui.comboBox_SBit.setCurrentText("1")
        self.ui.comboBox_PBit.addItems(gl.SERIAL_INFO["paritybit"])
        self.ui.comboBox_PBit.setCurrentText("None")
        self.ui.pushButton_Check.clicked.connect(self.scan_serial_ports)

    def _setup_receive_controls(self) -> None:
        """
        Set up receive options controls.
        """
        self.ui.pushButton_RClear.clicked.connect(self.receive_clear)
        self.ui.pushButton_RSave.clicked.connect(self.receive_save)
        self.ui.checkBox_RHexmode.clicked.connect(self.set_receive_hex_mode)

    def _setup_single_send_controls(self) -> None:
        """
        Set up single send options controls.
        """
        self.ui.pushButton_sSend.clicked.connect(self.single_data_send)
        self.ui.pushButton_sClear.clicked.connect(self.single_send_clear)
        self.ui.checkBox_sHexmode.clicked.connect(self.set_single_hex_mode)
        self.ui.checkBox_sCycle.clicked.connect(self.set_single_cycle_mode)
        self.ui.textEdit_sSend.installEventFilter(self)
        self.ui.lineEdit_sCycle.setValidator(QIntValidator())

    def _setup_multi_send_controls(self) -> None:
        """
        Set up multiple send options controls.
        """
        for i in range(1, gl.MAX_MULTI_SEND_CHANNELS + 1):
            getattr(self.ui, f"pushButton_m{i}").clicked.connect(
                lambda checked, seq=f"m{i}": self.multi_common_send(seq)
            )
        self.ui.checkBox_mCycle.clicked.connect(self.set_multi_cycle_mode)
        self.ui.lineEdit_mCycle.setValidator(QIntValidator())

    def _setup_file_send_controls(self) -> None:
        """
        Set up file send options controls.
        """
        self.ui.pushButton_fSelect.clicked.connect(self.file_send_select)
        self.ui.pushButton_fSend.clicked.connect(self.file_send)

    def _setup_guide(self) -> None:
        """
        Set up guide information text.
        """
        self.ui.plainTextEdit_Guide.setPlainText(gl.GUIDE_INFO)

    def _setup_status_bar(self) -> None:
        """
        Set up status bar with data size information.
        """
        self.label_rwsize = QLabel("")
        self.label_rwsize.setStyleSheet("color:blue")
        self.ui.statusbar.addPermanentWidget(self.label_rwsize, stretch=0)
        self._update_rwsize_status()

    ########################## port function ############################

    def _check_port_open(self, show_message: bool = True) -> bool:
        """
        Check if the serial port is open.
        """
        if not self.serial_instance.is_open:
            if show_message:
                self.message_box.information(self, "Info", "Please open a serial port first")
            return False
        return True

    def scan_serial_ports(self) -> bool:
        """
        Scan the serial ports and add them to the combo box.
        """
        self.ui.comboBox_SPort.clear()
        try:
            ports_list: list[str] = [
                port.device for port in serial.tools.list_ports.comports()
            ]
            self.ui.comboBox_SPort.addItems(ports_list)
            return True
        except Exception as e:
            self.log.error(f"Error scanning ports: {str(e)}")
            self.message_box.warning(self, "Warning", f"Failed to enumerate ports: {str(e)}")
            return False

    def port_toggle(self) -> None:
        """Toggle the serial port open and close."""
        if self.toggle_btn.isChecked():
            self.open_port()
        else:
            self.close_port()

    def _set_components_state(self, state: bool) -> None:
        """
        Set the state of the UI components based on the port state.
        """
        widgets_list1 = [
            self.ui.pushButton_Check,
            self.ui.comboBox_BRate,
            self.ui.comboBox_BSize,
            self.ui.comboBox_SBit,
            self.ui.comboBox_PBit,
            self.ui.comboBox_SPort,
        ]
        widgets_list2 = [
            self.ui.pushButton_sSend,
            self.ui.checkBox_sCycle,
            self.ui.checkBox_mCycle,
            self.ui.pushButton_m1,
            self.ui.pushButton_m2,
            self.ui.pushButton_m3,
            self.ui.pushButton_m4,
            self.ui.pushButton_m5,
            self.ui.pushButton_m6,
            self.ui.pushButton_fSend,
        ]
        for widget in widgets_list1:
            widget.setEnabled(not state)
        for widget in widgets_list2:
            widget.setEnabled(state)

    def open_port(self) -> bool:
        """
        Open the serial port with the parameters set in the UI.
        """
        port = self.ui.comboBox_SPort.currentText().strip()
        if not port:
            if self.toggle_btn.isChecked():
                self.toggle_btn.setChecked(False)
            self.message_box.warning(self, "Info", "No port selected")
            return False

        # Configure the serial instance
        self.serial_instance.port = port
        self.serial_instance.baudrate = int(self.ui.comboBox_BRate.currentText().strip())
        self.serial_instance.bytesize = int(self.ui.comboBox_BSize.currentText().strip())
        self.serial_instance.stopbits = int(self.ui.comboBox_SBit.currentText().strip())
        self.serial_instance.parity = self.ui.comboBox_PBit.currentText().strip()[0]
        self.serial_instance.timeout = gl.SERIAL_INFO["timeout"]

        if not self.serial_instance.is_open:
            try:
                self.serial_instance.open()
            except (serial.SerialException, OSError, ValueError) as err:
                if self.toggle_btn.isChecked():
                    self.toggle_btn.setChecked(False)
                msg = (
                    "The selected port may be occupied."
                    if "Permission" in str(err)
                    else "Cannot open the port with these parameters."
                )
                self.log.error(f"{msg} Error: {err}")
                self.message_box.critical(self, "Error", msg)
                return False

        if self.serial_instance.is_open:
            self._set_components_state(True)
            self.log.info(f"Port {port} opened successfully")
        return True

    def close_port(self) -> None:
        """
        Close the serial port.
        """
        self.log.info("Closing serial port")
        # Check and deactivate cycle send if active
        if self.ui.checkBox_sCycle.isChecked():
            self.ui.checkBox_sCycle.click()
        if self.ui.checkBox_mCycle.isChecked():
            self.ui.checkBox_mCycle.click()

        # Stop the file send timer
        self.file_send_timer.stop()

        # Check if the serial instance is open
        if self.serial_instance.is_open:
            # Trigger the serial close function in receive thread
            self.receive_thread.request_close_port()

    def _post_close_port(self) -> None:
        """
        Post processing after closing the serial port.
        """
        if not self.serial_instance.is_open:
            if self.toggle_btn.isChecked():
                self.toggle_btn.setChecked(False)
            self._set_components_state(False)

    ########################## single and multi send function ############################

    def _timer_data_send(self) -> bool:
        """
        Send data based on the current state of single and multi cycle sends.
        """
        # Check if both single and multi cycle sends are activated
        if self.ui.checkBox_sCycle.isChecked() and self.ui.checkBox_mCycle.isChecked():
            # Deactivate both cycle sends
            self.ui.checkBox_sCycle.click()
            self.ui.checkBox_mCycle.click()
            msg: str = (
                "Both single cycle send and multi cycle send are activated.\n\n"
                "Deactivate them all, please try again"
            )
            self.log.error(msg)
            self.message_box.warning(self, "Warning", msg)
            return False

        # Check if single cycle send is activated
        if self.ui.checkBox_sCycle.isChecked():
            self._single_cycle_send()
        # Check if multi cycle send is activated
        elif self.ui.checkBox_mCycle.isChecked():
            self._multi_cycle_send()
        return True

    def _is_valid_hex(self, text: str) -> tuple[bool, str]:
        """
        Check if the text is valid hex and return cleaned hex string.
        """
        cleaned = text.replace(" ", "")
        is_valid = (len(cleaned) % 2 == 0) and all(
            c in string.hexdigits for c in cleaned
        )
        return is_valid, cleaned

    def _send_bytes(self, data_bytes: bytes) -> int:
        """Send bytes through serial port and update statistics."""
        if not self._check_port_open(show_message=False):
            self.log.warning("Attempted to send data but port is not open")
            return 0
        if not data_bytes:
            self.log.warning("Attempted to send empty data")
            return 0
        try:
            send_size = self.serial_instance.write(data_bytes) or 0
            self.total_send_size += send_size
            self._update_rwsize_status()
            return send_size
        except (serial.SerialException, OSError, IOError) as e:
            self.log.error(f"Serial send error: {str(e)}")
            self.message_box.warning(self, "Error", "Error of sending data")
            return 0

    ########################## single send function ############################

    def single_send_clear(self) -> None:
        """
        Clear the single send text edit widget and reset the total send size.
        """
        self.ui.textEdit_sSend.clear()
        self.ui.textEdit_sSend.moveCursor(QTextCursor.MoveOperation.Start)
        self.total_send_size = 0
        self._update_rwsize_status()

    def _single_cycle_send(self) -> None:
        success = self.single_data_send()
        if not success and self.ui.checkBox_sCycle.isChecked():
            self.ui.checkBox_sCycle.click()
            return

    def single_data_send(self) -> bool:
        """
        Send data from the single send text edit widget to the serial port.
        """
        text = self.ui.textEdit_sSend.toPlainText()
        newline_state = self.ui.checkBox_sNewline.isChecked()
        is_hex = self.ui.checkBox_sHexmode.isChecked()

        if not self._check_port_open():
            return False
        if not text:
            return False

        bytes_text = self._prepare_data_for_sending(
            text, is_hex, newline_state, "single"
        )
        if not bytes_text:
            return False

        self._send_bytes(bytes_text)
        return True

    def set_single_cycle_mode(self) -> bool:
        """
        Set the cycle mode of the send text edit widget.
        """
        return self._set_cyclemode(
            self.ui.checkBox_sCycle,
            self.ui.lineEdit_sCycle,
            self.ui.textEdit_sSend.toPlainText(),
        )

    def set_single_hex_mode(self) -> None:
        """
        Set the hex mode of the send text edit widget.
        """
        hexmode_state = self.ui.checkBox_sHexmode.isChecked()
        text = self.ui.textEdit_sSend.toPlainText()
        if not text:
            return

        try:
            if hexmode_state:
                str_text = text.encode(self.encode_info, "replace").hex(" ")
            else:
                is_valid, _ = self._is_valid_hex(text)
                if not is_valid:
                    self.message_box.warning(
                        self,
                        "Warning",
                        "Incorrect hex format data, can't convert to text format",
                    )
                    self.ui.checkBox_sHexmode.setChecked(True)
                    return
                str_text = bytes.fromhex(text.replace(" ", "")).decode(
                    self.encode_info, "replace"
                )

            self.ui.textEdit_sSend.clear()
            self.ui.textEdit_sSend.insertPlainText(str_text)
        except (UnicodeDecodeError, ValueError) as e:
            self.log.error(f"Error converting hex mode: {e}")
            self.message_box.warning(self, "Error", "Failed to convert data format")
            self.ui.checkBox_sHexmode.setChecked(not hexmode_state)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        Event filter for the text edit widget in hex mode.
        """
        if (
            event.type() == QEvent.Type.KeyPress
            and obj is self.ui.textEdit_sSend
            and self.ui.checkBox_sHexmode.isChecked()
        ):
            key_event = event if isinstance(event, QKeyEvent) else None
            if key_event:
                # Allow Ctrl+V for paste operation
                if (
                    key_event.key() == Qt.Key.Key_V
                    and key_event.modifiers() == Qt.KeyboardModifier.ControlModifier
                ):
                    return super().eventFilter(obj, event)

                # Check if key is valid for hex input
                if key_event.key() not in self.key_limits:
                    self.message_box.warning(
                        self, "Warning", "Hex mode now!\nPlease input 0-9, a-f, A-F"
                    )
                    return True

        return super().eventFilter(obj, event)

    ########################## multi send function ############################

    def multi_common_send(self, seq: str) -> bool:
        """
        Send data based on the sequence provided (e.g., "m1", "m2").
        """
        if not self._check_port_open():
            return False

        line_edit = getattr(self.ui, f"lineEdit_{seq}", None)
        if line_edit is None:
            self.log.error(f"LineEdit for {seq} not found")
            return False

        text = line_edit.text()
        if not text:
            return False

        newline_state = self.ui.checkBox_mNewLine.isChecked()
        is_hex_mode = self.ui.checkBox_mHexMode.isChecked()

        bytes_text = self._prepare_data_for_sending(
            text, is_hex_mode, newline_state, seq
        )
        if not bytes_text:
            return False

        # Format hex display if needed
        if is_hex_mode and hasattr(line_edit, "insertPlainText"):
            formatted_text = " ".join(re.findall(r".{2}", text.replace(" ", "")))
            if formatted_text != text:
                line_edit.clear()
                line_edit.insert(formatted_text)

        self._send_bytes(bytes_text)
        return True

    def _multi_cycle_send(self) -> None:
        """
        Send the data in the text edit widget if the button is checked and the
        text edit is not empty.
        """
        # multi_dict: {"m{x}": [0, 0]}, first 0 means checked status, second 0 means send status
        for i in range(1, gl.MAX_MULTI_SEND_CHANNELS + 1):
            key = f"m{i}"
            is_checked = getattr(self.ui, f"checkBox_{key}").isChecked()
            has_text = bool(getattr(self.ui, f"lineEdit_{key}").text().strip())
            # Only add the entry if both conditions: checked and has text
            self.multi_dict[key][0] = 1 if is_checked and has_text else 0

        # Check if at least one item in multi_dict is checked (i.e., the first element is 1)
        if not any(item[0] for item in self.multi_dict.values()):
            self.message_box.information(self, "Info", "No item checked or no data input")
            self.ui.checkBox_mCycle.setChecked(False)
            return

        for item in self.multi_dict:
            if self.multi_dict[item][0] == 1 and self.multi_dict[item][1] == 0:
                success = self.multi_common_send(item)
                if not success and self.ui.checkBox_mCycle.isChecked():
                    self.ui.checkBox_mCycle.click()
                    return
                self.multi_dict[item][1] = 1
                break

        if all(item[1] for item in self.multi_dict.values() if item[0]):
            for item in self.multi_dict.values():
                item[1] = 0

    def set_multi_cycle_mode(self) -> bool:
        """
        Set the cycle mode for the multi send feature.
        """
        if self.ui.checkBox_mCycle.isChecked():
            # Initialize multi_dict
            self.multi_dict = {f"m{i}": [0, 0] for i in range(1, gl.MAX_MULTI_SEND_CHANNELS + 1)}

        return self._set_cyclemode(
            self.ui.checkBox_mCycle, self.ui.lineEdit_mCycle, "multi"
        )

    ########################## file send function ############################

    def file_send_select(self) -> bool:
        """
        Open a file dialog to select a file to send.
        """
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        dialog.setWindowTitle("Open File")
        dialog.setNameFilter("TXT File(*.txt *.json)")
        if not dialog.exec():
            return False
        file_name: str = dialog.selectedFiles()[0]
        if not file_name:
            return False
        self.log.info(f"send file: {file_name}")
        self.ui.lineEdit_fFile.setText(file_name)
        return True

    def _predict_encoding(self, file: str) -> str:
        """
        Predict the encoding of the file.
        """
        try:
            with open(file, "rb") as f:
                sample_size = min(1024 * 1024, os.path.getsize(file))
                encodeinfo = chardet.detect(f.read(sample_size))
            return encodeinfo.get("encoding") or "utf-8"
        except (OSError, IOError) as e:
            self.log.error(f"Encoding prediction failed: {e}")
            return "utf-8"

    def file_send(self) -> bool:
        """
        Send data from a file to the serial port.
        """
        if not self._check_port_open():
            return False

        selected_file: str = self.ui.lineEdit_fFile.text()
        if not selected_file or not os.path.exists(selected_file):
            self.message_box.information(self, "Info", "the file is not existed")
            return False
        encode: str = self._predict_encoding(selected_file)

        basename: str = os.path.basename(selected_file)
        self.json_send_list.clear()

        if "json" in basename.lower():
            return self._process_json_file(selected_file, encode)
        else:
            return self._process_text_file(selected_file, encode)

    def _process_json_file(self, file_path: str, encoding: str) -> bool:
        """
        Process a JSON file and send its content to the serial port.
        """
        try:
            json_parser = JsonParser(file_path)
            ret = json_parser.file_read(encoding)
            if ret[0] != JsonFlag.SUCCESS:
                error_msg = f"Error reading JSON file: {ret[0].name}"
                self.log.error(error_msg)
                self.message_box.critical(self, "Error", error_msg)
                return False

            json_dict = ret[1]
            cycle_time = json_dict["cycle_ms"]
            hex_mode = json_dict["hexmode"]
            datas = json_dict["datas"]

            if hex_mode:
                for item in datas:
                    str_data = item["data"].replace(" ", "")
                    if not all(c in string.hexdigits for c in str_data):
                        self.message_box.critical(
                            self, "Error", "Not every item is hex digit, please check."
                        )
                        return False
                    bytes_data = bytes.fromhex(str_data)
                    item["data"] = bytes_data
            else:
                for item in datas:
                    item["data"] = item["data"].encode(self.encode_info, "ignore")

            # generate send list
            self.json_send_list = [
                [item["select"], hex_mode, 0, item["data"]] for item in datas
            ]

            # different way to send data according to cycle time
            if cycle_time > 0:
                self.file_send_timer.start(cycle_time)
            else:
                for item in self.json_send_list:
                    if item[0] == 1:
                        self._send_bytes(item[3]) if item[3] else None
            return True
        except (KeyError, TypeError, ValueError) as e:
            error_msg = f"Failed to process JSON file: {str(e)}"
            self.log.error(error_msg)
            self.message_box.critical(self, "Error", error_msg)
            return False

    def _process_text_file(self, file_path: str, encoding: str) -> bool:
        """
        Process a text file and send its content to the serial port.
        """
        try:
            with open(file_path, mode="r", encoding=encoding, newline="") as fp:
                send_text = fp.read()
        except (OSError, IOError, UnicodeDecodeError) as e:
            self.log.error(f"Error opening file: {e}")
            self.message_box.critical(self, "Error", "Error of opening file")
            return False

        if self.serial_instance.is_open:
            data_bytes = send_text.encode(self.encode_info, "ignore")
            self._send_bytes(data_bytes)
        return True

    def _timer_json_file_data_send(self) -> None:
        """
        Send the data in the json_send_list.
        """
        for item in self.json_send_list:
            if item[0] == 1 and item[2] == 0:
                self._send_bytes(item[3]) if item[3] else None
                item[2] = 1
                break
        if all(item[2] == 1 for item in self.json_send_list if item[0] == 1):
            self.file_send_timer.stop()

    ########################## receive function ############################

    def set_receive_hex_mode(self) -> bool:
        """
        Toggle hex mode for the receive text edit widget.
        """
        self.mutex.lock()
        try:
            hexmode_state = self.ui.checkBox_RHexmode.isChecked()
            text = self.ui.textEdit_Receive.toPlainText()
            if not text:
                return False

            try:
                str_text = (
                    text.encode(self.encode_info, "replace").hex(" ") + " "
                    if hexmode_state
                    else bytes.fromhex(text).decode(self.encode_info, "replace")
                )
                self.ui.textEdit_Receive.clear()
                self.ui.textEdit_Receive.insertPlainText(str_text)
                self.ui.textEdit_Receive.moveCursor(QTextCursor.MoveOperation.End)
                return True
            except (ValueError, UnicodeDecodeError) as e:
                self.log.error(f"Error converting receive data: {e}")
                self.ui.checkBox_RHexmode.setChecked(not hexmode_state)
                return False
        finally:
            self.mutex.unlock()

    def _prepare_data_for_sending(
        self, text: str, is_hex: bool, newline_state: bool, source: str
    ) -> bytes:
        """
        Common data preparation logic for all send functions.
        """
        try:
            if is_hex:
                is_valid, cleaned_hex = self._is_valid_hex(text)
                if not is_valid:
                    msg = f"Not correct hex format in {source}"
                    self.log.warning(msg)
                    self.message_box.warning(self, "Warning", msg)
                    return b""

                bytes_text = bytes.fromhex(cleaned_hex)
                if newline_state:
                    bytes_text += os.linesep.encode(self.encode_info, "replace")
            else:
                if newline_state:
                    text += os.linesep
                bytes_text = text.encode(self.encode_info, "replace")

            return bytes_text
        except (ValueError, UnicodeEncodeError) as e:
            self.log.error(f"Error preparing data for {source}: {e}")
            self.message_box.warning(self, "Error", f"Failed to prepare send data: {e}")
            return b""

    def _set_cyclemode(self, check_box, line_edit, send_source) -> bool:
        """
        Common cycle mode setting logic.
        """
        if not check_box.isChecked():
            self.send_timer.stop()
            line_edit.setEnabled(True)
            return True

        cycle_text = line_edit.text()
        if not cycle_text:
            self.message_box.information(self, "Info", "Please set cycle time first")
            check_box.setChecked(False)
            return False

        if cycle_text == "0":
            self.message_box.information(
                self, "Info", "Cycle send time should be greater than 0"
            )
            check_box.setChecked(False)
            return False

        if send_source != "multi" and not send_source:
            self.message_box.information(self, "Info", "Please fill send datas first")
            check_box.setChecked(False)
            return False

        if not self._check_port_open():
            check_box.setChecked(False)
            return False

        self.send_timer.start(int(cycle_text.strip()))
        line_edit.setEnabled(False)
        return True

    def _update_receive_ui(self) -> None:
        """
        Update receive text edit widget with data from the receive queue.
        """
        self.mutex.lock()
        try:
            while not self.receive_thread.receive_queue.empty():
                received_data = self.receive_thread.receive_queue.get_nowait()
                receive_size: int = len(received_data)
                hex_status: bool = self.ui.checkBox_RHexmode.isChecked()
                received_data_str: str = (
                    received_data.hex(" ")
                    if hex_status
                    else received_data.decode(self.encode_info, "replace")
                )
                self.ui.textEdit_Receive.moveCursor(QTextCursor.MoveOperation.End)
                self.ui.textEdit_Receive.insertPlainText(received_data_str)
                if hex_status:
                    self.ui.textEdit_Receive.insertPlainText(" ")
                self.ui.textEdit_Receive.moveCursor(QTextCursor.MoveOperation.End)
                self.total_receive_size += receive_size
                self._update_rwsize_status()
        finally:
            self.mutex.unlock()

    def receive_save(self) -> bool:
        """
        Save received data to a file.
        """
        self.log.info("Saving received data to file")
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        dialog.setNameFilter("TXT File(*.txt)")
        if not dialog.exec():
            return False
        self.received_data_file = dialog.selectedFiles()[0]
        if not self.received_data_file:
            self.log.info("No file be selected to save the received datas")
            return False
        self.log.info(f"file: {self.received_data_file}")
        text = self.ui.textEdit_Receive.toPlainText()
        try:
            with open(self.received_data_file, "w+", encoding="utf-8") as fp:
                fp.write(text)
            self.log.info(f"Successfully saved received data to {self.received_data_file}")
        except (OSError, IOError) as e:
            self.log.error(f"Error writing data to file: {str(e)}")
            self.message_box.critical(self, "Error", "Error writing data into file")
            return False
        return True

    def receive_clear(self) -> None:
        """
        Clear the receive text edit widget.
        """
        self.ui.textEdit_Receive.clear()
        self.total_receive_size = 0
        self._update_rwsize_status()


    def _update_rwsize_status(self) -> None:
        datasize_text = (
            f"  Send: {self.total_send_size}  |  Receive: {self.total_receive_size}  "
        )
        self.label_rwsize.setText(datasize_text)

    ########################## menu function ############################

    def action_open_file(self) -> bool:
        """
        Open the file dialog to select a file to open.
        """
        if not hasattr(self, "received_data_file") or not os.path.exists(self.received_data_file):
            self.message_box.information(
                self, "Info", "Please save a receive datas file first"
            )
            return False

        directory = os.path.dirname(self.received_data_file)
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(directory)
            elif system in ("Linux", "Darwin"):
                command = "xdg-open" if system == "Linux" else "open"
                os.system(f"{command} {directory}")
        except (OSError, AttributeError) as e:
            self.log.error(f"Failed to open directory: {directory}, error: {e}")
            self.message_box.critical(
                self, "Error", f"Failed to open directory: {directory}\n{e}"
            )
            return False
        return True

    def action_exit(self) -> None:
        """
        Exit the application.
        """
        self._cleanup_and_exit()
        sys.exit()

    def action_about(self) -> None:
        """Show the about dialog."""
        self.about.show()

    def action_encoding(self, encode: str) -> None:
        """
        Set the encoding for the text in the send and receive text edit widgets.
        """
        actions = {
            "ascii": self.ui.actionASCII,
            "utf-8": self.ui.actionUTF_8,
            "utf-16": self.ui.actionUTF_16,
            "utf-32": self.ui.actionUTF_32,
            "gbk": self.ui.actionGBK_GB2312,
        }
        for key, action in actions.items():
            action.setChecked(key == encode)
        self.encode_info = encode

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle the close event for the main window.
        """
        self._cleanup_and_exit()
        # Call parent implementation
        super().closeEvent(event)

    def _cleanup_and_exit(self) -> None:
        """
        cleanup resources and exit
        """
        self.log.info("Cleaning up resources and exiting application")
        if hasattr(self, "receive_thread") and self.receive_thread.isRunning():
            self.receive_thread.requestInterruption()
            self.receive_thread.quit()
            self.receive_thread.wait(gl.THREAD_WAIT_TIMEOUT_MS)

        if hasattr(self, "serial_instance") and self.serial_instance.is_open:
            try:
                self.serial_instance.close()
            except (serial.SerialException, OSError) as e:
                self.log.error(f"Error closing serial port: {str(e)}")

        if hasattr(self, "receive_thread"):
            self.receive_thread.deleteLater()
        if hasattr(self, "about"):
            self.about.close()


########################## Sub-thread for receiving data ############################


class ReceiveThread(QThread):
    data_rec_signal = Signal()
    port_closed_signal = Signal()

    def __init__(self, ser: serial.Serial, parent=None) -> None:
        """
        Initialize the ReceiveThread with a serial instance and a parent widget.
        """
        super().__init__(parent)
        self.ser = ser
        self.close_port_flag = False
        self.receive_queue = queue.Queue(gl.RECEIVE_QUEUE_SIZE)

    def run(self) -> None:
        """
        Run the receive thread.
        """
        import threading

        threading.current_thread().name = "ReceiveThread"

        while not self.isInterruptionRequested():
            # Handle port closed state first
            if not self.ser.is_open:
                self.msleep(100)
                continue

            # Process serial data
            try:
                datas = self.ser.readall()
                if datas:
                    try:
                        self.receive_queue.put_nowait(datas)
                    except queue.Full:
                        logger.logger.warning("Receive queue is full, dropping data")
                        self.data_rec_signal.emit()

                # Emit signal if data is available
                if not self.receive_queue.empty():
                    self.data_rec_signal.emit()
            except (serial.SerialException, OSError, IOError) as e:
                logger.logger.error(f"Serial read error: {str(e)}")
                self.close_port_flag = True
                self.msleep(100)

            # Handle port closing
            if self.close_port_flag:
                try:
                    self.ser.close()
                    self.close_port_flag = False
                    self.port_closed_signal.emit()
                except (serial.SerialException, OSError) as e:
                    logger.logger.error(f"Error closing serial port: {str(e)}")

            # Small sleep to prevent CPU overuse
            self.msleep(10)

        logger.logger.info("Receive thread stopped")

    def request_close_port(self) -> None:
        """Request to close the serial port."""
        self.close_port_flag = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())

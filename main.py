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
from logwrapper import log_inst
from togglebt import ToggleButton
from ui.mainwindow_ui import Ui_MainWindow

# from togglebt_bk import ToggleButton


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        """
        Initialize the main window class.
        """
        super().__init__()
        self.log = log_inst.logger
        self.log.info("PyCOM application starting")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.about = About()
        self.var_init()
        self.gui_init()
        self.parse_ports()

    def var_init(self) -> None:
        """
        Initialize variables and objects for the main window.
        """
        # Initialize send/receive size tracking
        self.total_sendsize: int = 0  # The total send size
        self.total_recsize: int = 0  # The total received size
        self.recdatas_file: str = ""  # The file name of the received data

        # Initialize data encoding settings
        self.encode_info: str = "gbk"  # The encoding of the received data

        # Initialize data structures for sending
        self.multi_dict: dict = {}  # The dictionary of the multiple send data
        self.js_send_list: list = []  # The list of the json file data

        # Initialize serial communication components
        self.mutex: QMutex = QMutex()  # The mutex for the data sending
        self.msgbox: QMessageBox = QMessageBox()  # The message box instance
        self.ser_instance: serial.Serial = serial.Serial()  # The serial port instance

        # Initialize timers
        self.send_timer: QTimer = QTimer()  # The timer for the data sending
        self.send_timer.timeout.connect(self.timer_data_send)
        self.fsend_timer: QTimer = QTimer()  # The timer for the json file data sending
        self.fsend_timer.timeout.connect(self.timer_jsfile_data_send)

        # Initialize and start the receive thread
        self.recthread: ReceiveThread = ReceiveThread(self.ser_instance, self)
        self.recthread.data_rec_signal.connect(self.update_receive_ui)
        self.recthread.port_closed_signal.connect(self.post_close_port)
        self.recthread.start()

        # Initialize keyboard limits for hex mode input validation
        self.key_limits: list = [
            Qt.Key.Key_0,
            Qt.Key.Key_1,
            Qt.Key.Key_2,
            Qt.Key.Key_3,
            Qt.Key.Key_4,
            Qt.Key.Key_5,
            Qt.Key.Key_6,
            Qt.Key.Key_7,
            Qt.Key.Key_8,
            Qt.Key.Key_9,
            Qt.Key.Key_A,
            Qt.Key.Key_B,
            Qt.Key.Key_C,
            Qt.Key.Key_D,
            Qt.Key.Key_E,
            Qt.Key.Key_F,
            Qt.Key.Key_Space,
            Qt.Key.Key_Backspace,
            Qt.Key.Key_Delete,
            Qt.Key.Key_Right,
            Qt.Key.Key_Left,
            Qt.Key.Key_Up,
            Qt.Key.Key_Down,
            Qt.Key.Key_Control,
            Qt.Key.Key_Shift,
        ]

    def gui_init(self) -> None:
        """
        Initialize GUI components and set up event connections.
        """
        # Set window title and icon
        self.setWindowTitle(f"{gl.GuiInfo['proj']} {gl.GuiInfo['version']}")
        self.setWindowIcon(QIcon(":/icons/pycom"))

        self.toggltBtn = ToggleButton(self.ui.groupBox)
        self.toggltBtn.setGeometry(85, 265, 80, 30)
        self.toggltBtn.toggled.connect(self.port_toggle)

        # Menu setup: connect actions to corresponding functions
        self.ui.actionOpen_File.triggered.connect(self.action_open_file)
        self.ui.actionExit.triggered.connect(self.action_exit)
        self.ui.actionASCII.triggered.connect(lambda: self.action_encoding("ascii"))
        self.ui.actionUTF_8.triggered.connect(lambda: self.action_encoding("utf-8"))
        self.ui.actionUTF_16.triggered.connect(lambda: self.action_encoding("utf-16"))
        self.ui.actionUTF_32.triggered.connect(lambda: self.action_encoding("utf-32"))
        self.ui.actionGBK_GB2312.triggered.connect(lambda: self.action_encoding("gbk"))
        self.ui.actionAbout.triggered.connect(self.action_about)

        # Serial port setup: configure serial port options
        self.ui.comboBox_BRate.addItems(gl.SerialInfo["baudrate"])
        self.ui.comboBox_BRate.setCurrentText("115200")
        self.ui.comboBox_BSize.addItems(gl.SerialInfo["bytesize"])
        self.ui.comboBox_BSize.setCurrentText("8")
        self.ui.comboBox_SBit.addItems(gl.SerialInfo["stopbit"])
        self.ui.comboBox_SBit.setCurrentText("1")
        self.ui.comboBox_PBit.addItems(gl.SerialInfo["paritybit"])
        self.ui.comboBox_PBit.setCurrentText("None")
        self.ui.pushButton_Check.clicked.connect(self.parse_ports)

        # Receive setup: connect receive options
        self.ui.pushButton_RClear.clicked.connect(self.receive_clear)
        self.ui.pushButton_RSave.clicked.connect(self.receive_save)
        self.ui.checkBox_RHexmode.clicked.connect(self.receive_set_hexmode)

        # Single send setup: connect single send options
        self.ui.pushButton_sSend.clicked.connect(self.single_data_send)
        self.ui.pushButton_sClear.clicked.connect(self.single_send_clear)
        self.ui.checkBox_sHexmode.clicked.connect(self.single_send_set_hexmode)
        self.ui.checkBox_sCycle.clicked.connect(self.single_send_set_cyclemode)
        self.ui.textEdit_sSend.installEventFilter(self)
        self.ui.lineEdit_sCycle.setValidator(QIntValidator())

        # Multiple send setup: connect multiple send options
        self.ui.pushButton_m1.clicked.connect(lambda: self.multi_common_send("m1"))
        self.ui.pushButton_m2.clicked.connect(lambda: self.multi_common_send("m2"))
        self.ui.pushButton_m3.clicked.connect(lambda: self.multi_common_send("m3"))
        self.ui.pushButton_m4.clicked.connect(lambda: self.multi_common_send("m4"))
        self.ui.pushButton_m5.clicked.connect(lambda: self.multi_common_send("m5"))
        self.ui.pushButton_m6.clicked.connect(lambda: self.multi_common_send("m6"))
        # self.ui.checkBox_mHexMode.clicked.connect(self.multi_send_set_hexmode)  # TODO
        self.ui.checkBox_mCycle.clicked.connect(self.multi_send_set_cyclemode)
        self.ui.lineEdit_mCycle.setValidator(QIntValidator())

        # File send setup: connect file send options
        self.ui.pushButton_fSelect.clicked.connect(self.file_send_select)
        self.ui.pushButton_fSend.clicked.connect(self.file_send)

        # Guide setup: set guide information text
        self.ui.plainTextEdit_Guide.setPlainText(gl.GuideInfo)

        # Status bar setup: initialize and add data size status
        self.label_rwsize = QLabel("")
        self.label_rwsize.setStyleSheet("color:blue")
        self.ui.statusbar.addPermanentWidget(self.label_rwsize, stretch=0)
        self.update_rwsize_status()

        # Set up the initial state of the UI components
        self.set_components_state(False)

    ########################## port function ############################

    def parse_ports(self) -> bool:
        """
        Parse the serial ports and add them to the combo box.
        """
        self.ui.comboBox_SPort.clear()
        try:
            ports_list: list[str] = [
                port.device for port in serial.tools.list_ports.comports()
            ]
            self.ui.comboBox_SPort.addItems(ports_list)
            return True
        except Exception as e:
            self.log.error(f"Error parsing ports: {str(e)}")
            self.msgbox.warning(self, "Warning", f"Failed to enumerate ports: {str(e)}")
            return False

    def port_toggle(self) -> None:
        """Toggle the serial port open and close."""
        if self.toggltBtn.isChecked():
            self.open_port()
        else:
            self.close_port()

    def set_components_state(self, state: bool) -> None:
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
        Optimize by structuring the setup and error handling.
        """
        # Retrieve settings from UI components
        port = self.ui.comboBox_SPort.currentText().strip()
        if not port:
            # Reset toggle button state if checked
            if self.toggltBtn.isChecked():
                self.toggltBtn.setChecked(False)
            self.msgbox.warning(self, "Info", "No port selected")
            return False

        # Configure the serial instance
        self.ser_instance.port = port
        self.ser_instance.baudrate = int(self.ui.comboBox_BRate.currentText().strip())
        self.ser_instance.bytesize = int(self.ui.comboBox_BSize.currentText().strip())
        self.ser_instance.stopbits = int(self.ui.comboBox_SBit.currentText().strip())
        self.ser_instance.parity = self.ui.comboBox_PBit.currentText().strip()[0]
        self.ser_instance.timeout = gl.SerialInfo["timeout"]

        # Check if the port is not open and attempt to open
        if not self.ser_instance.is_open:
            try:
                self.ser_instance.open()
            except serial.SerialException as err:
                # Reset toggle state on failure
                if self.toggltBtn.isChecked():
                    self.toggltBtn.setChecked(False)
                # Handle different types of errors
                if "Permission" in str(err):
                    msg = "The selected port may be occupied."
                else:
                    msg = "Cannot open the port with these parameters."
                self.log.error(f"{msg} Error: {err}")
                self.msgbox.critical(self, "Error", msg)
                return False

        # If open, update UI accordingly
        if self.ser_instance.is_open:
            self.set_components_state(True)
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
        self.fsend_timer.stop()

        # Check if the serial instance is open
        if self.ser_instance.is_open:
            # Trigger the serial close function in receive thread
            self.recthread.rec_close_port()
            # Note: Closing the serial directly here may cause a crash
            # self.ser_instance.close()

    def post_close_port(self) -> None:
        """
        Post processing after closing the serial port.
        """
        if not self.ser_instance.is_open:
            if self.toggltBtn.isChecked():
                self.toggltBtn.setChecked(False)
            self.set_components_state(False)

    ########################## single and multi send function ############################

    def timer_data_send(self) -> bool:
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
            self.msgbox.warning(self, "Warning", msg)
            return False

        # Check if single cycle send is activated
        if self.ui.checkBox_sCycle.isChecked():
            self.single_cycle_send()
        # Check if multi cycle send is activated
        elif self.ui.checkBox_mCycle.isChecked():
            self.multi_cycle_send()
        return True

    def is_valid_hex(self, text: str) -> tuple[bool, str]:
        """
        Check if the text is valid hex and return cleaned hex string.
        """
        cleaned = text.replace(" ", "")
        is_valid = (len(cleaned) % 2 == 0) and all(
            c in string.hexdigits for c in cleaned
        )
        return is_valid, cleaned

    def _send_bytes(self, data_bytes: bytes) -> int:
        if not data_bytes or not self.ser_instance.is_open:
            if not self.ser_instance.is_open:
                self.log.warning("Attempted to send data but port is not open")
            return 0
        try:
            sendsize = self.ser_instance.write(data_bytes) or 0
            self.total_sendsize += sendsize
            self.update_rwsize_status()
            return sendsize
        except Exception as e:
            error_type = (
                "Serial" if isinstance(e, serial.SerialException) else "Unexpected"
            )
            self.log.error(f"{error_type} send error: {str(e)}")
            self.msgbox.warning(self, "Error", "Error of sending data")
            return 0

    ########################## single send function ############################

    def single_send_clear(self) -> None:
        """
        Clear the single send text edit widget and reset the total send size.
        """
        self.ui.textEdit_sSend.clear()
        self.ui.textEdit_sSend.moveCursor(QTextCursor.MoveOperation.Start)
        self.total_sendsize = 0
        self.update_rwsize_status()

    def single_cycle_send(self) -> None:
        success = self.single_data_send()
        if not success and self.ui.checkBox_sCycle.isChecked():
            self.ui.checkBox_sCycle.click()
            return

    def single_data_send(self) -> bool:
        """
        Send data from the single send text edit widget to the serial port.
        """
        try:
            text = self.ui.textEdit_sSend.toPlainText()
            newline_state = self.ui.checkBox_sNewline.isChecked()
            is_hex = self.ui.checkBox_sHexmode.isChecked()

            if not self.ser_instance.is_open:
                self.msgbox.information(self, "Info", "Please open a serial port first")
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
        except Exception as e:
            self.log.error(f"Error in single_data_send: {str(e)}")
            self.msgbox.warning(self, "Error", f"Failed to send data: {str(e)}")
            return False

    def single_send_set_cyclemode(self) -> bool:
        """
        Set the cycle mode of the send text edit widget.
        """
        return self._set_cyclemode(
            self.ui.checkBox_sCycle,
            self.ui.lineEdit_sCycle,
            self.ui.textEdit_sSend.toPlainText(),
        )

    def single_send_set_hexmode(self) -> None:
        """
        Set the hex mode of the send text edit widget.
        """
        hexmode_state: bool = self.ui.checkBox_sHexmode.isChecked()
        text: str = self.ui.textEdit_sSend.toPlainText()
        if not text:
            return

        if hexmode_state:
            str_text: str = text.encode(self.encode_info, "replace").hex(" ")
        else:
            is_valid, _ = self.is_valid_hex(text)
            if not is_valid:
                self.msgbox.warning(
                    self,
                    "Warning",
                    "Incorrect hex format data, can't convert to text format",
                )
                self.ui.checkBox_sHexmode.setChecked(True)
                return  # incorrect hex format
            str_text: str = bytes.fromhex(text.replace(" ", "")).decode(
                self.encode_info, "replace"
            )

        self.ui.textEdit_sSend.clear()
        self.ui.textEdit_sSend.insertPlainText(str_text)

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
                    self.msgbox.warning(
                        self, "Warning", "Hex mode now!\nPlease input 0-9, a-f, A-F"
                    )
                    return True

        return super().eventFilter(obj, event)

    ########################## multi send function ############################

    def multi_common_send(self, seq: str) -> bool:
        """
        Send data based on the sequence provided (e.g., "m1", "m2").
        """
        if not self.ser_instance.is_open:
            self.msgbox.information(self, "Info", "Please open a serial port first")
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

    def multi_cycle_send(self) -> None:
        """
        Send the data in the text edit widget if the button is checked and the
        text edit is not empty.
        """
        # multi_dict: {"m{x}": [0, 0]}, first 0 means checked status, second 0 means send status
        for i in range(1, 7):
            key = f"m{i}"
            is_checked = getattr(self.ui, f"checkBox_{key}").isChecked()
            has_text = bool(getattr(self.ui, f"lineEdit_{key}").text().strip())
            # Only add the entry if both conditions: checked and has text
            self.multi_dict[key][0] = 1 if is_checked and has_text else 0

        # Check if at least one item in multi_dict is checked (i.e., the first element is 1)
        if not any(item[0] for item in self.multi_dict.values()):
            self.msgbox.information(self, "Info", "No item checked or no data input")
            self.ui.checkBox_mCycle.setChecked(False)
            return

        for item in self.multi_dict:
            if self.multi_dict[item][0] == 1 and self.multi_dict[item][1] == 0:
                success = self.multi_common_send(item)
                if not success and self.ui.checkBox_mCycle.isChecked():
                    self.ui.checkBox_mCycle.click()
                    return
                self.multi_dict[item][1] = 1  # Set send status to 1
                break  # for timer, send next data in next timer event

        if all(item[1] for item in self.multi_dict.values() if item[0]):
            for item in self.multi_dict.values():
                item[1] = 0  # Reset send status to 0

    def multi_send_set_cyclemode(self) -> bool:
        """
        Set the cycle mode for the multi send feature.
        """
        if self.ui.checkBox_mCycle.isChecked():
            # Initialize multi_dict
            self.multi_dict = {f"m{i}": [0, 0] for i in range(1, 7)}

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

    def predict_encoding(self, file: str) -> str:
        """
        Predict the encoding of the file.
        """
        try:
            with open(file, "rb") as f:
                # only read 1MB data to predict encoding
                sample_size = min(1024 * 1024, os.path.getsize(file))  # 1MB
                encodeinfo = chardet.detect(f.read(sample_size))
            return encodeinfo.get("encoding") or "utf-8"
        except Exception as e:
            self.log.error(f"Encoding prediction failed: {e}")
            return "utf-8"

    def file_send(self) -> bool:
        """
        Send data from a file to the serial port.
        """
        if not self.ser_instance.is_open:
            self.msgbox.information(self, "Info", "Please open serial port first")
            return False

        sfile: str = self.ui.lineEdit_fFile.text()
        if not sfile or not os.path.exists(sfile):
            self.msgbox.information(self, "Info", "the file is not existed")
            return False
        encode: str = self.predict_encoding(sfile)

        basename: str = os.path.basename(sfile)
        self.js_send_list.clear()

        if "json" in basename.lower():
            return self._process_json_file(sfile, encode)
        else:
            return self._process_text_file(sfile, encode)

    def _process_json_file(self, file_path: str, encoding: str) -> bool:
        """
        Process a JSON file and send its content to the serial port.
        """
        try:
            jsparser: JsonParser = JsonParser(file_path)
            ret: tuple[JsonFlag, dict] = jsparser.file_read(encoding)
            if ret[0] != JsonFlag.SUCCESS:
                error_msg: str = f"Error reading JSON file: {ret[0].name}"
                self.log.error(error_msg)
                self.msgbox.critical(self, "Error", error_msg)
                return False

            js_dict: dict = ret[1]
            cycle_time: int = js_dict["cycle_ms"]
            hex_mode: int = js_dict["hexmode"]
            datas: list[dict] = js_dict["datas"]

            if hex_mode:
                for item in datas:
                    str_data: str = item["data"].replace(" ", "")
                    if not all(c in string.hexdigits for c in str_data):
                        self.msgbox.critical(
                            self, "Error", "Not every item is hex digit, please check."
                        )
                        return False
                    bytes_data = bytes.fromhex(str_data)
                    item["data"] = bytes_data
            else:
                for item in datas:
                    item["data"] = item["data"].encode(self.encode_info, "ignore")

            # generate send list
            self.js_send_list = [
                [item["select"], hex_mode, 0, item["data"]] for item in datas
            ]

            # different way to send data according to cycle time
            if cycle_time > 0:
                self.fsend_timer.start(cycle_time)
            else:
                # Send all selected items immediately if no cycle time is specified
                for item in self.js_send_list:
                    if item[0] == 1:  # selected
                        self._send_bytes(item[3]) if item[3] else None
            return True
        except Exception as e:
            error_msg: str = f"Failed to process JSON file: {str(e)}"
            self.log.error(error_msg)
            self.msgbox.critical(self, "Error", error_msg)
            return False

    def _process_text_file(self, file_path: str, encoding: str) -> bool:
        """
        Process a text file and send its content to the serial port.
        """
        try:
            with open(file_path, mode="r", encoding=encoding, newline="") as fp:
                send_text = fp.read()
        except Exception as e:
            self.log.error(f"Error opening file: {e}")
            self.msgbox.critical(self, "Error", "Error of opening file")
            return False

        if self.ser_instance.is_open:
            data_bytes = send_text.encode(self.encode_info, "ignore")
            self._send_bytes(data_bytes)
        return True

    def timer_jsfile_data_send(self) -> None:
        """
        Send the data in the js_send_list.
        """
        for item in self.js_send_list:
            if item[0] == 1 and item[2] == 0:  # selected and not sent
                self._send_bytes(item[3]) if item[3] else None
                item[2] = 1  # mark as sent
                break
        if all(item[2] == 1 for item in self.js_send_list if item[0] == 1):
            self.fsend_timer.stop()

    ########################## receive function ############################

    def receive_set_hexmode(self) -> bool:
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
            except Exception as e:
                self.log.error(f"Error converting receive data: {e}")
                self.ui.checkBox_RHexmode.setChecked(not hexmode_state)  # Revert
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
                is_valid, cleaned_hex = self.is_valid_hex(text)
                if not is_valid:
                    msg = f"Not correct hex format in {source}"
                    self.log.warning(msg)
                    self.msgbox.warning(self, "Warning", msg)
                    return b""

                bytes_text = bytes.fromhex(cleaned_hex)
                if newline_state:
                    bytes_text += os.linesep.encode(self.encode_info, "replace")
            else:
                if newline_state:
                    text += os.linesep
                bytes_text = text.encode(self.encode_info, "replace")

            return bytes_text
        except Exception as e:
            self.log.error(f"Error preparing data for {source}: {e}")
            self.msgbox.warning(self, "Error", f"Failed to prepare send data: {e}")
            return b""

    def _set_cyclemode(self, check_box, line_edit, send_source) -> bool:
        """
        Common cycle mode setting logic.
        """
        if check_box.isChecked():
            cycle_text = line_edit.text()

            # Check preconditions
            if not self.ser_instance.is_open:
                self.msgbox.information(self, "Info", "Please open a port first")
                check_box.setChecked(False)
                return False
            elif not cycle_text:
                self.msgbox.information(self, "Info", "Please set cycle time first")
                check_box.setChecked(False)
                return False
            elif cycle_text == "0":
                self.msgbox.information(
                    self, "Info", "Cycle send time should be greater than 0"
                )
                check_box.setChecked(False)
                return False
            elif send_source != "multi" and not send_source:
                self.msgbox.information(self, "Info", "Please fill send datas first")
                check_box.setChecked(False)
                return False

            self.send_timer.start(int(cycle_text.strip()))
            line_edit.setEnabled(False)
        else:
            self.send_timer.stop()
            line_edit.setEnabled(True)
        return True

    def update_receive_ui(self) -> None:
        """
        Update receive text edit widget with data from the receive queue.
        """
        self.mutex.lock()
        try:
            while not self.recthread.recqueue.empty():
                recdatas = self.recthread.recqueue.get_nowait()
                recsize: int = len(recdatas)
                hex_status: bool = self.ui.checkBox_RHexmode.isChecked()
                recdatas_str: str = (
                    recdatas.hex(" ")
                    if hex_status
                    else recdatas.decode(self.encode_info, "replace")
                )
                self.ui.textEdit_Receive.moveCursor(QTextCursor.MoveOperation.End)
                self.ui.textEdit_Receive.insertPlainText(recdatas_str)
                if hex_status:
                    self.ui.textEdit_Receive.insertPlainText(" ")
                self.ui.textEdit_Receive.moveCursor(QTextCursor.MoveOperation.End)
                self.total_recsize += recsize
                self.update_rwsize_status()
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
        self.recdatas_file = dialog.selectedFiles()[0]
        if not self.recdatas_file:
            self.log.info("No file be selected to save the received datas")
            return False
        self.log.info(f"file: {self.recdatas_file}")
        text: str = self.ui.textEdit_Receive.toPlainText()
        try:
            with open(self.recdatas_file, "w+", encoding="utf-8") as fp:
                fp.write(text)
            self.log.info(f"Successfully saved received data to {self.recdatas_file}")
        except Exception as e:
            self.log.error(f"Error writing data to file: {str(e)}")
            self.msgbox.critical(self, "Error", "Error writing data into file")
            return False
        return True

    def receive_clear(self) -> None:
        """
        Clear the receive text edit widget.
        """
        self.ui.textEdit_Receive.clear()
        self.total_recsize = 0
        self.update_rwsize_status()

    def update_rwsize_status(self) -> None:
        datasize_text = (
            f"  Send: {self.total_sendsize}  |  Receive: {self.total_recsize}  "
        )
        self.label_rwsize.setText(datasize_text)

    ########################## menu function ############################

    def action_open_file(self) -> bool:
        """
        Open the file dialog to select a file to open.
        """
        # Check if the received data file exists
        if not hasattr(self, "recdatas_file") or not os.path.exists(self.recdatas_file):
            self.msgbox.information(
                self, "Info", "Please save a receive datas file first"
            )
            return False

        directory = os.path.dirname(self.recdatas_file)
        try:
            # Use platform-specific commands to open the directory
            system = platform.system()
            if system == "Windows":
                os.startfile(directory)
            elif system in ("Linux", "Darwin"):
                command = "xdg-open" if system == "Linux" else "open"
                os.system(f"{command} {directory}")
        except Exception as e:
            self.log.error(f"Failed to open directory: {directory}, error: {e}")
            self.msgbox.critical(
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

    def action_about(self):
        # self.msgbox.information(self, "About", gl.AboutInfo)
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
        if hasattr(self, "recthread") and self.recthread.isRunning():
            self.recthread.requestInterruption()
            self.recthread.quit()
            self.recthread.wait(500)

        if hasattr(self, "ser_instance") and self.ser_instance.is_open:
            try:
                self.ser_instance.close()
            except Exception as e:
                self.log.error(f"Error closing serial port: {str(e)}")

        if hasattr(self, "recthread"):
            self.recthread.deleteLater()
        if hasattr(self, "about"):
            self.about.destroy()


########################## Sub-thread for receiving data ############################


class ReceiveThread(QThread):
    data_rec_signal = Signal()
    port_closed_signal = Signal()

    def __init__(self, ser: serial.Serial, parent=None) -> None:
        """
        Initialize the WorkerThread with a serial instance and a parent widget.
        """
        super().__init__(parent)
        self.ser = ser
        self.close_port_flag = False
        self.recqueue = queue.Queue(50)  # Limit queue size to 50

    def run(self) -> None:
        """
        Run the receive thread.
        """
        import threading

        threading.current_thread().name = "ReceiveThread"

        while not self.isInterruptionRequested():
            # Handle port closed state first
            if not self.ser.is_open:
                self.msleep(100)  # Sleep longer when port is closed to reduce CPU usage
                continue

            # Process serial data
            try:
                datas = self.ser.readall()
                if datas:
                    try:
                        self.recqueue.put_nowait(datas)
                    except queue.Full:
                        log_inst.logger.warning("Receive queue is full, dropping data")

                # Emit signal if data is available
                if not self.recqueue.empty():
                    self.data_rec_signal.emit()
            except Exception as e:
                log_inst.logger.error(f"Serial read error: {str(e)}")
                self.close_port_flag = True
                self.msleep(100)

            # Handle port closing
            if self.close_port_flag:
                try:
                    self.ser.close()
                    self.close_port_flag = False
                    self.port_closed_signal.emit()
                except Exception as e:
                    log_inst.logger.error(f"Error closing serial port: {str(e)}")

            # Small sleep to prevent CPU overuse
            self.msleep(10)

        log_inst.logger.info("Receive thread stopped")

    def rec_close_port(self):
        """Request to close the serial port."""
        self.close_port_flag = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())

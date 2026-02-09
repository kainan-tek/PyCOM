import os
import platform
import sys

from PySide6.QtCore import QEvent, QMutex, QObject, QTimer, Qt
from PySide6.QtGui import QCloseEvent, QIcon, QIntValidator, QKeyEvent, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
)

from about import About
import globalvar as gl
from serial_manager import SerialManager
from data_handler import DataConverter, DataSender, DataReceiver
from file_handler import FileHandler
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
        # Initialize received data file path
        self.received_data_file: str = ""

        # Initialize data structures for sending
        self.multi_dict: dict = {}
        self.json_send_list: list = []

        # Initialize core components
        self.mutex: QMutex = QMutex()
        self.message_box: QMessageBox = QMessageBox()
        self.serial_manager = SerialManager()
        self.data_converter = DataConverter("gbk")  # Default encoding
        self.data_sender = DataSender(self.serial_manager, self.data_converter)
        self.file_handler = FileHandler(self.data_converter)

        # Initialize and start the receive thread
        self.data_receiver = DataReceiver(self.serial_manager, self)
        self.data_receiver.data_received.connect(self._update_receive_ui)
        self.data_receiver.port_closed.connect(self._post_close_port)
        self.data_receiver.start()

        # Initialize timers
        self.send_timer: QTimer = QTimer()
        self.send_timer.timeout.connect(self._timer_data_send)
        self.file_send_timer: QTimer = QTimer()
        self.file_send_timer.timeout.connect(self._timer_json_file_data_send)

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
        self.ui.checkBox_mHexMode.clicked.connect(self.set_multi_hex_mode)
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

    def scan_serial_ports(self) -> bool:
        """
        Scan the serial ports and add them to the combo box.
        """
        self.ui.comboBox_SPort.clear()
        ports_list = self.serial_manager.scan_ports()
        if ports_list:
            self.ui.comboBox_SPort.addItems(ports_list)
            return True
        else:
            self.message_box.warning(self, "Warning", "Failed to enumerate ports")
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

        # Get parameters from UI
        baudrate = int(self.ui.comboBox_BRate.currentText().strip())
        bytesize = int(self.ui.comboBox_BSize.currentText().strip())
        stopbits = int(self.ui.comboBox_SBit.currentText().strip())
        parity = self.ui.comboBox_PBit.currentText().strip()[0]
        timeout = gl.SERIAL_INFO["timeout"]

        # Open port using SerialManager
        success, msg = self.serial_manager.open_port(
            port, baudrate, bytesize, stopbits, parity, timeout
        )

        if not success:
            if self.toggle_btn.isChecked():
                self.toggle_btn.setChecked(False)
            self.message_box.critical(self, "Error", msg)
            return False

        self._set_components_state(True)
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
        if self.serial_manager.is_open():
            # Trigger the serial close function in receive thread
            self.data_receiver.request_close_port()

    def _post_close_port(self) -> None:
        """
        Post processing after closing the serial port.
        """
        if not self.serial_manager.is_open():
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

    ########################## single send function ############################

    def single_send_clear(self) -> None:
        """
        Clear the single send text edit widget and reset the total send size.
        """
        self.ui.textEdit_sSend.clear()
        self.ui.textEdit_sSend.moveCursor(QTextCursor.MoveOperation.Start)
        self.data_sender.reset_counter()
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

        if not self.serial_manager.is_open():
            self.message_box.information(self, "Info", "Please open a serial port first")
            return False
        if not text:
            return False

        # Use DataSender to send data
        success, bytes_sent = self.data_sender.send_data(text, is_hex, newline_state)
        if success:
            self._update_rwsize_status()
        return success

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
                # Convert text to hex
                str_text = self.data_converter.text_to_hex(text)
            else:
                # Convert hex to text
                success, str_text = self.data_converter.hex_to_text(text)
                if not success:
                    self.message_box.warning(
                        self,
                        "Warning",
                        "Incorrect hex format data, can't convert to text format",
                    )
                    self.ui.checkBox_sHexmode.setChecked(True)
                    return

            self.ui.textEdit_sSend.clear()
            self.ui.textEdit_sSend.insertPlainText(str_text)
        except Exception as e:
            self.log.error(f"Error converting hex mode: {e}")
            self.message_box.warning(self, "Error", "Failed to convert data format")
            self.ui.checkBox_sHexmode.setChecked(not hexmode_state)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        Event filter for the text edit widget in hex mode.
        """
        try:
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
        except Exception as e:
            self.log.error(f"Error in eventFilter: {e}")
            return super().eventFilter(obj, event)

    ########################## multi send function ############################

    def multi_common_send(self, seq: str) -> bool:
        """
        Send data based on the sequence provided (e.g., "m1", "m2").
        """
        if not self.serial_manager.is_open():
            self.message_box.information(self, "Info", "Please open a serial port first")
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

        # Use DataSender to send data
        success, bytes_sent = self.data_sender.send_data(text, is_hex_mode, newline_state)
        if success:
            self._update_rwsize_status()
        return success

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

        return self._set_cyclemode(self.ui.checkBox_mCycle, self.ui.lineEdit_mCycle, "multi")

    def set_multi_hex_mode(self) -> None:
        """
        Set the hex mode for multi send and convert between text and hex.
        Similar to single send hex mode - converts display format.
        """
        hex_mode_state = self.ui.checkBox_mHexMode.isChecked()

        if hex_mode_state:
            # Convert text to hex when enabling hex mode
            for i in range(1, gl.MAX_MULTI_SEND_CHANNELS + 1):
                line_edit = getattr(self.ui, f"lineEdit_m{i}")
                text = line_edit.text().strip()

                if text:
                    # Convert text to hex
                    hex_str = self.data_converter.text_to_hex(text)
                    line_edit.clear()
                    line_edit.insert(hex_str)
        else:
            # Convert hex to text when disabling hex mode
            invalid_items = []
            for i in range(1, gl.MAX_MULTI_SEND_CHANNELS + 1):
                line_edit = getattr(self.ui, f"lineEdit_m{i}")
                text = line_edit.text().strip()

                if text:
                    success, text_str = self.data_converter.hex_to_text(text)
                    if success:
                        line_edit.clear()
                        line_edit.insert(text_str)
                    else:
                        invalid_items.append(f"m{i}")

            # If any field has invalid hex data, show warning and revert
            if invalid_items:
                items_str = ", ".join(invalid_items)
                self.message_box.warning(
                    self,
                    "Warning",
                    f"The following fields contain invalid hex format data:\n{items_str}\n\n"
                    "Cannot convert to text format.",
                )
                self.ui.checkBox_mHexMode.setChecked(True)

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

    def file_send(self) -> bool:
        """
        Send data from a file to the serial port.
        """
        if not self.serial_manager.is_open():
            self.message_box.information(self, "Info", "Please open a serial port first")
            return False

        selected_file: str = self.ui.lineEdit_fFile.text()
        if not selected_file or not os.path.exists(selected_file):
            self.message_box.information(self, "Info", "the file is not existed")
            return False

        file_type = self.file_handler.get_file_type(selected_file)

        if file_type == "json":
            return self._process_json_file(selected_file)
        else:
            return self._process_text_file(selected_file)

    def _process_json_file(self, file_path: str) -> bool:
        """
        Process a JSON file and send its content to the serial port.
        """
        # Read JSON file
        success, json_data = self.file_handler.read_json_file(file_path)
        if not success or not json_data:
            self.message_box.critical(self, "Error", "Error reading JSON file")
            return False

        # Process JSON data for sending
        success, send_list = self.file_handler.process_json_send_data(json_data)
        if not success:
            self.message_box.critical(self, "Error", "Not every item is hex digit, please check.")
            return False

        self.json_send_list = send_list
        cycle_time = json_data.get("cycle_ms", 0)

        # Send data according to cycle time
        if cycle_time > 0:
            self.file_send_timer.start(cycle_time)
        else:
            for item in self.json_send_list:
                if item[0] == 1:  # if selected
                    success, _ = self.data_sender.send_bytes(item[3])
                    if success:
                        self._update_rwsize_status()
        return True

    def _process_text_file(self, file_path: str) -> bool:
        """
        Process a text file and send its content to the serial port.
        """
        success, content = self.file_handler.read_text_file(file_path)
        if not success:
            self.message_box.critical(self, "Error", "Error of opening file")
            return False

        if self.serial_manager.is_open():
            success, _ = self.data_sender.send_file_content(content)
            if success:
                self._update_rwsize_status()
            return success
        return False

    def _timer_json_file_data_send(self) -> None:
        """
        Send the data in the json_send_list.
        """
        for item in self.json_send_list:
            if item[0] == 1 and item[2] == 0:  # selected and not sent
                success, _ = self.data_sender.send_bytes(item[3])
                if success:
                    self._update_rwsize_status()
                item[2] = 1  # mark as sent
                break

        # Check if all selected items have been sent
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
                if hexmode_state:
                    # Convert text to hex
                    str_text = self.data_converter.text_to_hex(text) + " "
                else:
                    # Convert hex to text
                    success, str_text = self.data_converter.hex_to_text(text)
                    if not success:
                        self.log.error("Error converting receive data")
                        self.ui.checkBox_RHexmode.setChecked(not hexmode_state)
                        return False

                self.ui.textEdit_Receive.clear()
                self.ui.textEdit_Receive.insertPlainText(str_text)
                self.ui.textEdit_Receive.moveCursor(QTextCursor.MoveOperation.End)
                return True
            except Exception as e:
                self.log.error(f"Error converting receive data: {e}")
                self.ui.checkBox_RHexmode.setChecked(not hexmode_state)
                return False
        finally:
            self.mutex.unlock()

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
            self.message_box.information(self, "Info", "Cycle send time should be greater than 0")
            check_box.setChecked(False)
            return False

        if send_source != "multi" and not send_source:
            self.message_box.information(self, "Info", "Please fill send datas first")
            check_box.setChecked(False)
            return False

        if not self.serial_manager.is_open():
            self.message_box.information(self, "Info", "Please open a serial port first")
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
            data_list = self.data_receiver.get_data_from_queue()
            for received_data in data_list:
                hex_status: bool = self.ui.checkBox_RHexmode.isChecked()

                if hex_status:
                    received_data_str = self.data_converter.bytes_to_hex(received_data)
                else:
                    received_data_str = self.data_converter.bytes_to_text(received_data)

                self.ui.textEdit_Receive.moveCursor(QTextCursor.MoveOperation.End)
                self.ui.textEdit_Receive.insertPlainText(received_data_str)
                if hex_status:
                    self.ui.textEdit_Receive.insertPlainText(" ")
                self.ui.textEdit_Receive.moveCursor(QTextCursor.MoveOperation.End)

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
        self.data_receiver.reset_counter()
        self._update_rwsize_status()

    def _update_rwsize_status(self) -> None:
        """
        Update the status bar with send/receive data size.
        """
        total_send = self.data_sender.get_total_sent()
        total_receive = self.data_receiver.get_total_received()
        datasize_text = f"  Send: {total_send}  |  Receive: {total_receive}  "
        self.label_rwsize.setText(datasize_text)

    ########################## menu function ############################

    def action_open_file(self) -> bool:
        """
        Open the file dialog to select a file to open.
        """
        if not hasattr(self, "received_data_file") or not os.path.exists(self.received_data_file):
            self.message_box.information(self, "Info", "Please save a receive datas file first")
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
            self.message_box.critical(self, "Error", f"Failed to open directory: {directory}\n{e}")
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
        # Update encoding in data converter
        self.data_converter.set_encoding(encode)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle the close event for the main window.
        """
        self._cleanup_and_exit()
        # Call parent implementation
        super().closeEvent(event)

    def _cleanup_and_exit(self) -> None:
        """
        Cleanup resources and exit.
        """
        self.log.info("Cleaning up resources and exiting application")

        # 1. Stop timers first
        if hasattr(self, "send_timer"):
            self.send_timer.stop()
        if hasattr(self, "file_send_timer"):
            self.file_send_timer.stop()

        # 2. Stop receive thread
        if hasattr(self, "data_receiver") and self.data_receiver.isRunning():
            self.data_receiver.requestInterruption()
            self.data_receiver.quit()
            self.data_receiver.wait(gl.THREAD_WAIT_TIMEOUT_MS)

        # 3. Close serial port
        if hasattr(self, "serial_manager") and self.serial_manager.is_open():
            self.serial_manager.close_port()

        # 4. Clean up objects
        if hasattr(self, "data_receiver"):
            self.data_receiver.deleteLater()
        if hasattr(self, "about"):
            self.about.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())

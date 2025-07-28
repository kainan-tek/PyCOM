import os
import queue
import re
import string
import sys
import time

import chardet
import serial
import serial.tools.list_ports
from PySide6.QtCore import QEvent, QMutex, QThread, QTimer, Signal, QObject, Qt
from PySide6.QtGui import QIcon, QIntValidator, QTextCursor, QKeyEvent, QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QLineEdit,
)

import globalvar as gl
from about import About
from jsonparser import JsonFlag, JsonParser
from logwrapper import log_inst
from ui.mainwindow_ui import Ui_MainWindow
from togglebt import ToggleButton


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        """
        Initialize the MainWindow class.

        This function initializes the UI by calling the setupUi method of the
        Ui_MainWindow class. It also initializes some variables and objects for
        the MainWindow class.

        Args:
            None

        Returns:
            None
        """
        super(MainWindow, self).__init__()
        self.log = log_inst.logger
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.about = About()
        self.var_init()
        self.gui_init()
        self.parse_ports()

    def var_init(self) -> None:
        """
        Initialize various variables and objects for the MainWindow class.

        Sets up initial values for send/receive sizes, data encoding, and UI components.
        Also sets up timers and threads for data sending and receiving.

        Args:
            None

        Returns:
            None
        """
        self.togglebt_enable: bool = True  # Flag to enable/disable toggle button
        self.total_sendsize: int = 0  # The total send size
        self.total_recsize: int = 0  # The total received size
        self.datasize_text: str = ""  # The text to show the send/receive size
        self.recdatas_file: str = ""  # The file name of the received data
        self.encode_info: str = "gbk"  # The encoding of the received data
        self.multi_dict: dict = {}  # The dictionary of the multiple send data
        self.js_send_list: list = []  # The list of the json file data
        self.mutex: QMutex = QMutex()  # The mutex for the data sending
        self.msgbox: QMessageBox = QMessageBox()  # The message box instance
        self.ser_instance: serial.Serial = serial.Serial()  # The serial port instance
        self.send_timer: QTimer = QTimer()  # The timer for the data sending
        self.send_timer.timeout.connect(self.data_send)
        self.fsend_timer: QTimer = QTimer()  # The timer for the json file data sending
        self.fsend_timer.timeout.connect(self.jsfile_data_send)
        self.recthread: WorkerThread = WorkerThread(self.ser_instance)
        self.recthread.data_rec_signal.connect(self.update_receive_ui)
        self.recthread.port_closed_signal.connect(self.post_close_port)
        self.recthread.start()

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
        Initialize the GUI components

        Set up the window title and icon, configure the serial port options,
        connect the actions to corresponding functions, and set up the single
        and multiple send options.

        Args:
            None

        Returns:
            None
        """
        # Set window title and icon
        self.setWindowTitle(f"{gl.GuiInfo['proj']} {gl.GuiInfo['version']}")
        self.setWindowIcon(QIcon(":/icons/pycom"))

        if self.togglebt_enable:
            # enable toggle button
            self.ui.pushButton_Open.setHidden(True)
            self.ui.pushButton_Close.setHidden(True)
            self.toggltBtn = ToggleButton(self.ui.groupBox)
            self.toggltBtn.setGeometry(85, 265, 90, 30)
            self.toggltBtn.toggled.connect(self.port_toggle)
        else:
            # disable toggle button
            self.ui.label_togglebt.setHidden(True)
            self.ui.pushButton_Open.clicked.connect(self.open_port)
            self.ui.pushButton_Close.clicked.connect(self.close_port)
            self.ui.pushButton_Open.setEnabled(True)
            self.ui.pushButton_Close.setDisabled(True)

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

        # Single send setup: connect single send options
        self.ui.pushButton_sSend.clicked.connect(self.single_data_send)
        self.ui.pushButton_sClear.clicked.connect(self.send_clear)
        self.ui.pushButton_RClear.clicked.connect(self.receive_clear)
        self.ui.pushButton_RSave.clicked.connect(self.receive_save)
        self.ui.checkBox_sHexmode.clicked.connect(self.send_set_hexmode)
        self.ui.checkBox_RHexmode.clicked.connect(self.receive_set_hexmode)
        self.ui.checkBox_sCycle.clicked.connect(self.send_set_cyclemode)
        self.ui.textEdit_sSend.installEventFilter(self)
        self.ui.lineEdit_sCycle.setValidator(QIntValidator())

        # Multiple send setup: connect multiple send options
        self.ui.pushButton_m1.clicked.connect(lambda: self.multi_common_send("m1"))
        self.ui.pushButton_m2.clicked.connect(lambda: self.multi_common_send("m2"))
        self.ui.pushButton_m3.clicked.connect(lambda: self.multi_common_send("m3"))
        self.ui.pushButton_m4.clicked.connect(lambda: self.multi_common_send("m4"))
        self.ui.pushButton_m5.clicked.connect(lambda: self.multi_common_send("m5"))
        self.ui.pushButton_m6.clicked.connect(lambda: self.multi_common_send("m6"))
        self.ui.checkBox_mCycle.clicked.connect(self.multi_send_set_cyclemode)
        self.ui.lineEdit_mCycle.setValidator(QIntValidator())

        # File send setup: connect file send options
        self.ui.pushButton_fSelect.clicked.connect(self.file_send_select)
        self.ui.pushButton_fSend.clicked.connect(self.file_send)

        # Guide setup: set guide information text
        self.ui.plainTextEdit_Guide.setPlainText(gl.GuideInfo)

        # Status bar setup: initialize and add data size status
        self.datasize_text = "  Send: 0  |  Receive: 0  "
        self.label_rwsize = QLabel(self.datasize_text)
        self.label_rwsize.setStyleSheet("color:blue")
        self.ui.statusbar.addPermanentWidget(self.label_rwsize, stretch=0)

        # Set up the initial state of the UI components
        self.ui.pushButton_sSend.setDisabled(True)
        self.ui.checkBox_sCycle.setDisabled(True)
        self.ui.checkBox_mCycle.setDisabled(True)
        self.ui.pushButton_m1.setDisabled(True)
        self.ui.pushButton_m2.setDisabled(True)
        self.ui.pushButton_m3.setDisabled(True)
        self.ui.pushButton_m4.setDisabled(True)
        self.ui.pushButton_m5.setDisabled(True)
        self.ui.pushButton_m6.setDisabled(True)
        self.ui.pushButton_fSend.setDisabled(True)

    ########################## port function ############################

    def parse_ports(self) -> bool:
        """
        Parse the serial ports and add them to the combo box.

        Args:
            None

        Returns:
            bool: Always returns True after parsing and adding ports.
        """
        self.ui.comboBox_SPort.clear()
        ports_list: list[str] = [
            port.device for port in serial.tools.list_ports.comports()
        ]
        self.ui.comboBox_SPort.addItems(ports_list)
        return True

    # if enable toggle button
    def port_toggle(self) -> None:
        """Toggle the serial port open and close."""
        if self.toggltBtn.isChecked():
            self.open_port()
        else:
            self.close_port()

    def set_components_state(self, state: bool) -> None:
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
        Open the serial port.

        This function opens the serial port according to the settings in the combo boxes.

        Args:
            None

        Returns:
            bool: True if the port is opened successfully, False otherwise
        """
        self.ser_instance.port = self.ui.comboBox_SPort.currentText().strip()
        self.ser_instance.baudrate = int(self.ui.comboBox_BRate.currentText().strip())
        self.ser_instance.bytesize = int(self.ui.comboBox_BSize.currentText().strip())
        self.ser_instance.stopbits = int(self.ui.comboBox_SBit.currentText().strip())
        self.ser_instance.parity = self.ui.comboBox_PBit.currentText().strip()[0]
        self.ser_instance.timeout = gl.SerialInfo["timeout"]

        if not self.ser_instance.port:
            self.msgbox.warning(self, "Info", "No port be selected")
            if self.togglebt_enable and self.toggltBtn.isChecked():
                self.toggltBtn.setChecked(False)
            return False

        if not self.ser_instance.is_open:
            try:
                self.ser_instance.open()
            except Exception as err:
                msg = (
                    "The selected port may be occupied."
                    if "Permission" in str(err)
                    else "Cannot open the port with these params."
                )
                self.log.error(msg + f" Error: {str(err)}")
                self.msgbox.critical(self, "Error", msg)
                if self.togglebt_enable and self.toggltBtn.isChecked():
                    self.toggltBtn.setChecked(False)
                return False
        if self.ser_instance.is_open:
            if not self.togglebt_enable:
                self.ui.pushButton_Open.setDisabled(True)
                self.ui.pushButton_Close.setEnabled(True)
            self.set_components_state(True)
        return True

    def close_port(self) -> None:
        """
        Close the serial port.

        Check and deactivate single cycle send and multi cycle send if active.
        Stop the file send timer and trigger the serial close function in the receive thread.

        Args:
            None

        Returns:
            None
        """
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
        Post close the serial port.

        This function takes no arguments and returns no value.

        Args:
            None

        Returns:
            None
        """
        if not self.ser_instance.is_open:
            if self.togglebt_enable:
                if self.toggltBtn.isChecked():
                    self.toggltBtn.setChecked(False)
            else:
                self.ui.pushButton_Open.setEnabled(True)
                self.ui.pushButton_Close.setDisabled(True)
            self.set_components_state(False)

    ########################## single and multi send function ############################

    def data_send(self) -> bool:
        """
        Send data to the serial port.

        Checks if single cycle send or multi cycle send is activated, and calls
        the corresponding function to send the data.

        If both single cycle send and multi cycle send are activated, deactivates
        them all, logs an error, and shows a warning message.

        Args:
            None

        Returns:
            bool: True if the data is sent successfully, False otherwise
        """
        # Check if both single and multi cycle sends are activated
        if self.ui.checkBox_sCycle.isChecked() and self.ui.checkBox_mCycle.isChecked():
            # Deactivate both cycle sends
            self.ui.checkBox_sCycle.click()
            self.ui.checkBox_mCycle.click()
            msg: str = (
                "Both single cycle send and multi cycle send are activated\nDeactivate them all, please try again"
            )
            self.log.error(msg)
            self.msgbox.warning(self, "Warning", msg)
            return False

        # Check if single cycle send is activated
        if self.ui.checkBox_sCycle.isChecked():
            self.single_data_send()
        # Check if multi cycle send is activated
        elif self.ui.checkBox_mCycle.isChecked():
            self.multi_cycle_send()
        return True

    def is_send_hex_mode(self, text: str) -> bool:
        """
        Check if the given text string is a valid hex string.

        A valid hex string should have an even number of characters, and all
        characters should be hex digits.

        Args:
            text (str): the text string to be checked

        Returns:
            bool: True if the text string is a valid hex string, False otherwise
        """
        post_text: str = text.replace(" ", "")
        if not len(post_text) % 2 == 0:
            return False
        if not all(item in string.hexdigits for item in post_text):
            return False
        return True

    def _send_bytes(self, data_bytes: bytes) -> int:
        if not self.ser_instance.is_open:
            return 0
        try:
            sendsize_raw = self.ser_instance.write(data_bytes)
            sendsize: int = sendsize_raw if sendsize_raw is not None else 0
            self.total_sendsize += sendsize
            self.update_rwsize_status()
            return sendsize
        except Exception as e:
            self.log.error(f"Send data error: {str(e)}")
            self.msgbox.warning(self, "Error", "Error of sending data")
            return 0

    ########################## single send function ############################

    def send_clear(self) -> None:
        """
        Clear the send text edit widget.

        This function takes no arguments and returns nothing.

        Args:
            None

        Returns:
            None
        """
        self.ui.textEdit_sSend.clear()
        self.ui.textEdit_sSend.moveCursor(QTextCursor.MoveOperation.Start)
        self.total_sendsize = 0
        self.update_rwsize_status()

    def single_data_send(self) -> bool:
        """
        Send single data from the text edit widget.

        Read the data from the text edit widget, convert it to bytes and send it
        to the serial port. If the checkbox is checked, send the data in hexadecimal
        format with the newline character.

        Args:
            None

        Returns:
            bool: False if the serial port is not open, otherwise returns nothing.
        """
        NEWLINE_BYTES = [13, 10]
        int_list: list[int] = []
        text: str = self.ui.textEdit_sSend.toPlainText()
        newline_state: bool = self.ui.checkBox_sNewline.isChecked()
        is_hex = self.ui.checkBox_sHexmode.isChecked()

        if not self.ser_instance.is_open:
            self.msgbox.information(self, "Info", "Please open a serial port first")
            return False
        if not text and not newline_state:
            return False

        if is_hex:
            if text:
                if not self.is_send_hex_mode(text):
                    if self.ui.checkBox_sCycle.isChecked():
                        self.ui.checkBox_sCycle.click()
                    msg: str = "Not correct hex format datas"
                    self.log.warning(msg)
                    self.msgbox.warning(self, "Warning", msg)
                    return False
                text_list: list[str] = re.findall(".{2}", text.replace(" ", ""))
                str_text: str = " ".join(text_list)
                if not str_text == text:
                    self.ui.textEdit_sSend.clear()
                    self.ui.textEdit_sSend.insertPlainText(str_text)
                int_list = [int(item, 16) for item in text_list]
            if newline_state:
                int_list.extend(NEWLINE_BYTES)
            bytes_text: bytes = bytes(int_list)
        else:
            if newline_state:
                text = text + "\r\n"
            bytes_text: bytes = text.encode(self.encode_info, "replace")

        self._send_bytes(bytes_text)
        return True

    def send_set_cyclemode(self) -> bool:
        """
        Set the cycle mode of the single send feature.

        If the cycle mode checkbox is checked, start the timer with the cycle time
        set in the line edit widget. Otherwise, stop the timer. If the conditions
        are not met, show an information message box and return False.

        Args:
            None

        Returns:
            bool: False if the conditions are not met, otherwise returns True
        """
        if self.ui.checkBox_sCycle.isChecked():
            msg: str = ""
            cycle_text = self.ui.lineEdit_sCycle.text()
            send_text = self.ui.textEdit_sSend.toPlainText()
            if not self.ser_instance.is_open:
                msg = "Please open a port first"
            elif not cycle_text:
                msg = "Please set cycle time first"
            elif cycle_text == "0":
                msg = "Cycle send time should be greater than 0"
            elif not send_text:
                msg = "Please fill send datas first"
            if msg:
                self.msgbox.information(self, "Info", msg)
                self.ui.checkBox_sCycle.setChecked(False)
                return False
            self.send_timer.start(int(cycle_text.strip()))
            self.ui.lineEdit_sCycle.setEnabled(False)
        else:
            self.send_timer.stop()
            self.ui.lineEdit_sCycle.setEnabled(True)
        return True

    def send_set_hexmode(self) -> None:
        """
        Toggle the hex mode for the send text edit widget.

        Converts the text to hexadecimal format if the hex mode is enabled,
        otherwise converts it back to text format.

        Args:
            None

        Returns:
            None
        """
        hexmode_state: bool = self.ui.checkBox_sHexmode.isChecked()
        text: str = self.ui.textEdit_sSend.toPlainText()

        if not text:
            return

        if hexmode_state:
            str_text: str = text.encode(self.encode_info, "replace").hex(" ")
        else:
            if not self.is_send_hex_mode(text):
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
        Override the event filter function to intercept key press events on the send text edit widget when the hex mode is enabled.

        If the hex mode is enabled and the key pressed is not a valid hexadecimal digit (0-9, a-f, A-F) or Ctrl+V, show a warning message box and return True to intercept the event.

        Args:
            obj (QObject): The object that triggered the event.
            event (QEvent): The event object containing information about the event.

        Returns:
            bool: True if the event is intercepted, False otherwise.
        """
        if (
            event.type() == QEvent.Type.KeyPress
            and obj is self.ui.textEdit_sSend
            and self.ui.checkBox_sHexmode.isChecked()
        ):
            key_event = event if isinstance(event, QKeyEvent) else None
            if key_event:
                if key_event.key() not in self.key_limits and not (
                    key_event.modifiers() == Qt.KeyboardModifier.ControlModifier
                    and key_event.key() == Qt.Key.Key_V
                ):
                    self.msgbox.warning(
                        self, "Warning", "Hex mode now!\nPlease input 0-9, a-f, A-F"
                    )
                    return True
        return super().eventFilter(obj, event)

    ########################## multi send function ############################

    def multi_common_send(self, seq: str) -> bool:
        """
        Set the checked status of the send buttons and text edits to the
        dictionary, and send the data if the button is checked and the text
        edit is not empty.

        Args:
            seq (str): Sequence number of the text edit.
            line_edit (QLineEdit): The text edit to read the data from.

        Returns:
            bool: True if the data is sent successfully, False otherwise.
        """
        int_list: list[int] = []
        line_edit: QLineEdit = getattr(self.ui, f"lineEdit_{seq}")
        text = line_edit.text()
        newline_state = self.ui.checkBox_mNewLine.isChecked()

        if not self.ser_instance.is_open:
            self.msgbox.information(self, "Info", "Please open a serial port first")
            return False
        if not text and not newline_state:
            return False

        if self.ui.checkBox_mHexMode.isChecked():
            if text:
                if not self.is_send_hex_mode(text):
                    if self.ui.checkBox_mCycle.isChecked():
                        self.ui.checkBox_mCycle.click()
                    self.msgbox.warning(
                        self, "Warning", f"Not correct hex format in Edit {seq}"
                    )
                    return False
                text_list: list[str] = re.findall(".{2}", text.replace(" ", ""))
                str_text: str = " ".join(text_list)
                if not str_text == text:
                    line_edit.clear()
                    line_edit.insert(str_text)
                int_list = [int(item, 16) for item in text_list]
            if newline_state:
                int_list.extend([13, 10])
            bytes_text = bytes(int_list)
        else:
            if newline_state:
                text = text + "\r\n"
            bytes_text = text.encode(self.encode_info, "replace")

        self._send_bytes(bytes_text)
        return True

    def multi_cycle_send(self) -> None:
        """
        Set the checked status of the send buttons and text edits to the
        dictionary, and send the data if the button is checked and the text
        edit is not empty.

        Args:
            None

        Returns:
            None
        """
        for i in range(1, 7):
            key = f"m{i}"
            self.multi_dict[key][0] = (
                1
                if getattr(self.ui, f"checkBox_{key}").isChecked()
                and getattr(self.ui, f"lineEdit_{key}").text()
                else 0
            )

        for item in self.multi_dict:
            if self.multi_dict[item][0] == 1 and self.multi_dict[item][1] == 0:
                self.multi_common_send(item)
                self.multi_dict[item][1] = 1
                break

        if all(
            self.multi_dict[item][1]
            for item in self.multi_dict
            if self.multi_dict[item][0]
        ):
            for item in self.multi_dict:
                self.multi_dict[item][1] = 0

    def multi_send_set_cyclemode(self) -> bool:
        """
        If the check box is checked, set the timer to send the data with
        the cycle time. If the check box is unchecked, stop the timer.

        Args:
            None

        Returns:
            bool: False if any validation fails, otherwise returns nothing
        """
        if self.ui.checkBox_mCycle.isChecked():
            msg: str = ""
            cycle_text = self.ui.lineEdit_mCycle.text()
            if not self.ser_instance.is_open:
                msg = "Please open a port first"
            elif not cycle_text:
                msg = "Please set cycle time first"
            if msg:
                self.msgbox.information(self, "Info", msg)
                self.ui.checkBox_mCycle.setChecked(False)
                return False
            # [0,0] first 0 means checked status, second 0 means send status
            self.multi_dict = {f"m{i + 1}": [0, 0] for i in range(6)}
            self.send_timer.start(int(cycle_text.strip()))
            self.ui.lineEdit_mCycle.setEnabled(False)
        else:
            self.send_timer.stop()
            self.ui.lineEdit_mCycle.setEnabled(True)
        return True

    ########################## file send function ############################

    def file_send_select(self) -> bool:
        """
        This function takes no arguments and returns a boolean indicating success or failure.

        Args:
            None

        Returns:
            bool: True if a file is selected successfully, False otherwise

        """
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        dialog.setWindowTitle("Open File")
        dialog.setNameFilter("TXT File(*.txt *.json)")
        if not dialog.exec():
            return False
        file_name: str = dialog.selectedFiles()[0]
        # file_name,_ = self.dialog.getOpenFileName(
        #     self, 'Open File', '', 'TXT File(*.txt *.json)', '', QFileDialog.DontUseNativeDialog)
        if not file_name:
            return False
        self.log.info(f"send file: {file_name}")
        self.ui.lineEdit_fFile.setText(file_name)
        return True

    def predict_encoding(self, file: str) -> str:
        try:
            with open(file, "rb") as f:
                encodeinfo = chardet.detect(f.read())
            return encodeinfo.get("encoding") or "utf-8"
        except Exception as e:
            self.log.error(f"Encoding prediction failed: {e}")
            return "utf-8"

    def file_send(self) -> bool:
        """
        This function takes no arguments and returns a boolean indicating success or failure.

        Args:
            None

        Returns:
            bool: True if the file is sent successfully, False otherwise
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
        if "json" in basename:
            # for json file
            jsparser: JsonParser = JsonParser(sfile)
            ret: tuple[JsonFlag, dict] = jsparser.file_read(encode)
            if not ret[0].value == JsonFlag.SUCCESS.value:
                msgtext: str = f"Error of reading json fie, err: {ret[0].name}"
                self.log.error(msgtext)
                self.msgbox.critical(self, "Error", msgtext)
                return False
            js_dict: dict = ret[1]
            cycle_time: int = js_dict["cycle_ms"]
            hex_mode: int = js_dict["hexmode"]
            if hex_mode:
                for i in range(len(js_dict["datas"])):
                    str_data: str = js_dict["datas"][i]["data"].replace(" ", "")
                    if not all(item in string.hexdigits for item in str_data):
                        self.msgbox.critical(
                            self, "Error", "Not every item is hex digit, please check."
                        )
                        return False
                    text_lst: list[str] = re.findall(".{2}", str_data)
                    int_lst: list[int] = [int(item, 16) for item in text_lst]
                    js_dict["datas"][i]["data"] = bytes(int_lst)
                self.js_send_list = [
                    [js_dict["datas"][i]["select"], 1, 0, js_dict["datas"][i]["data"]]
                    for i in range(len(js_dict["datas"]))
                ]
            else:
                # self.js_send_list[[is_select, is_hexmode, is_sent, data]...]
                self.js_send_list = [
                    [js_dict["datas"][i]["select"], 0, 0, js_dict["datas"][i]["data"]]
                    for i in range(len(js_dict["datas"]))
                ]
            if cycle_time > 0:
                self.fsend_timer.start(cycle_time)
            else:
                for item in self.js_send_list:
                    if item[0] == 1:  # selected
                        sendsize_raw = (
                            self.ser_instance.write(item[3])
                            if item[1] == 1  # hex mode
                            else self.ser_instance.write(
                                item[3].encode(self.encode_info, "ignore")
                            )
                        )
                        sendsize: int = sendsize_raw if sendsize_raw is not None else 0
                        self.total_sendsize += sendsize
                        self.update_rwsize_status()
        else:
            # for txt file
            try:
                with open(sfile, mode="r", encoding=encode, newline="") as fp:
                    send_text: str = fp.read()
            except Exception as e:
                msgtext: str = "Error of opening file"
                self.log.error(f"{msgtext}, err: {e}")
                self.msgbox.critical(self, "Error", msgtext)
                return False
            if self.ser_instance.is_open:
                sendsize_raw = self.ser_instance.write(
                    send_text.encode(self.encode_info, "ignore")
                )
                sendsize: int = sendsize_raw if sendsize_raw is not None else 0
                self.total_sendsize += sendsize
                self.update_rwsize_status()
        return True

    def jsfile_data_send(self) -> None:
        """
        This function iterates through the json send list and sends the selected data
        through the serial instance. It updates the send status of each data item and
        the total send size. If all selected data items have been sent, it stops the
        file send timer.

        Args:
            None

        Returns:
            None
        """
        for item in self.js_send_list:
            if item[0] == 1 and item[2] == 0:  # selected and not sent
                sendsize_raw = (
                    self.ser_instance.write(item[3])
                    if item[1] == 1  # hex mode
                    else self.ser_instance.write(
                        item[3].encode(self.encode_info, "ignore")
                    )
                )
                sendsize: int = sendsize_raw if sendsize_raw is not None else 0
                item[2] = 1  # mark as sent
                self.total_sendsize += sendsize
                self.update_rwsize_status()
                break
        if all(item[2] == 1 for item in self.js_send_list if item[0] == 1):
            self.fsend_timer.stop()

    ########################## receive function ############################

    def receive_set_hexmode(self) -> bool:
        """
        Set the hex mode for the receive text edit widget.
        """
        self.mutex.lock()
        try:
            hexmode_state: bool = self.ui.checkBox_RHexmode.isChecked()
            text: str = self.ui.textEdit_Receive.toPlainText()
            if not text:
                return False
            str_text = (
                text.encode(self.encode_info, "replace").hex(" ") + " "
                if hexmode_state
                else bytes.fromhex(text).decode(self.encode_info, "replace")
            )
            self.ui.textEdit_Receive.clear()
            self.ui.textEdit_Receive.insertPlainText(str_text)
            self.ui.textEdit_Receive.moveCursor(QTextCursor.MoveOperation.End)
            return True
        finally:
            self.mutex.unlock()

    def update_receive_ui(self) -> None:
        """
        Update the receive text edit widget with the data from the receive queue.
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
        Save the received data to a file.
        This function opens a file dialog to select the file to save the received data.
        If the dialog is canceled, it returns False. Otherwise, it saves the received data
        to the selected file and returns True.

        Args:
            None

        Returns:
            bool: True if the received data is saved successfully, False otherwise.
        """
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
        except Exception:
            self.log.error("Error of writing datas into file.")
            self.msgbox.critical(self, "Error", "Error of writing datas into file")
            return False
        return True

    def receive_clear(self) -> None:
        """
        Clear the receive text edit widget and reset the total received size.
        This function takes no arguments and returns nothing.

        Args:
            None

        Returns:
            None
        """
        self.ui.textEdit_Receive.clear()
        self.total_recsize = 0
        self.update_rwsize_status()

    def update_rwsize_status(self) -> None:
        self.datasize_text = (
            f"  Send: {self.total_sendsize}  |  Receive: {self.total_recsize}  "
        )
        self.label_rwsize.setText(self.datasize_text)

    ########################## menu function ############################

    def action_open_file(self) -> bool:
        """
        Open the directory where the receive datas file is saved.
        This function checks if the receive datas file exists, and if it does,
        it opens the directory using the appropriate command for the current
        operating system.

        Args:
            None

        Returns:
            bool: True if the directory is opened successfully, False otherwise
        """
        if not os.path.exists(self.recdatas_file):
            self.msgbox.information(
                self, "Info", "Please save a receive datas file first"
            )
            return False
        if "nt" in os.name:
            os.startfile(os.path.dirname(self.recdatas_file))
        else:
            os.system(f"xdg-open {os.path.dirname(self.recdatas_file)}")
        return True

    def action_exit(self) -> None:
        """
        Exit the application.
        This function checks if the receive thread is running, requests
        interruption, quits the thread, and waits for it to finish.

        Args:
            None

        Returns:
            None
        """
        if self.recthread.isRunning():
            self.recthread.requestInterruption()
            self.recthread.quit()
            self.recthread.wait()
        sys.exit()

    def action_about(self):
        # self.msgbox.information(self, "About", gl.AboutInfo)
        self.about.show()

    def action_encoding(self, encode: str) -> None:
        """
        Set the encoding for the text in the send and receive text edit widgets.
        This function will check the encoding and set the corresponding action
        menu item to be checked.

        Args:
            encode (str): The encoding to be set.

        Returns:
            None
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
        Handle the close event of the main window.
        This function will stop the receive thread if it is running, close the serial port,
        and then exit the application.

        Args:
            event (QCloseEvent): The close event.

        Returns:
            None
        """
        if self.recthread.isRunning():
            self.recthread.requestInterruption()
            self.recthread.quit()
            self.recthread.wait()
        # sys.exit()
        self.recthread.deleteLater()
        self.about.destroy()
        super(MainWindow, self).closeEvent(event)


########################## Sub-thread for receiving data ############################


class WorkerThread(QThread):
    data_rec_signal: Signal = Signal()
    port_closed_signal: Signal = Signal()

    def __init__(self, ser: serial.Serial, parent=None) -> None:
        """
        Initialize the WorkerThread with a serial port instance.
        Args:
            ser (serial.Serial): The serial port instance.
            parent (QWidget): The parent widget.
        Returns:
            None
        """
        super(WorkerThread, self).__init__(parent)
        self.ser: serial.Serial = ser
        self.close_port_flag: bool = False
        self.recqueue: queue.Queue[bytes] = queue.Queue(50)

    def run(self) -> None:
        """
        Run the thread to continuously read data from the serial port.
        This method will run in a loop, reading all available data from the serial port.
        If the serial port is closed, it will emit a signal to notify that the port is closed.
        If the thread is interrupted, it will break the loop and stop reading data.
        If there is data in the queue, it will emit a signal to notify that data has been received.
        If the close port flag is set, it will close the serial port and emit a signal to notify that the port is closed.
        Args:
            None
        Returns:
            None
        """
        while True:
            if self.ser.is_open:
                try:
                    datas: bytes = self.ser.readall()
                    if datas:
                        self.recqueue.put_nowait(datas)
                except Exception as e:
                    log_inst.logger.error(f"Serial read error: {str(e)}")
                    self.close_port_flag = True
            if self.isInterruptionRequested():
                break
            if not self.recqueue.empty():
                self.data_rec_signal.emit()
            if self.close_port_flag:
                self.ser.close()
                self.close_port_flag = False
                self.port_closed_signal.emit()
            time.sleep(0.01)

    def rec_close_port(self):
        self.close_port_flag = True


def main() -> int:
    """
    Main function to run the application.

    Returns:
        int: The exit code of the application.
    """
    app: QApplication = QApplication(sys.argv)  # create a QApplication object
    window: MainWindow = MainWindow()  # create a MainWindow object
    window.show()  # show the main window
    return app.exec()  # run the event loop and exit with the app's exit code


if __name__ == "__main__":
    sys.exit(main())

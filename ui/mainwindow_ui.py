# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGroupBox, QLabel, QLineEdit, QMainWindow,
    QMenu, QMenuBar, QPlainTextEdit, QPushButton,
    QSizePolicy, QStatusBar, QTabWidget, QTextEdit,
    QWidget)
import resrc.resource_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(750, 530)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(750, 530))
        MainWindow.setMaximumSize(QSize(750, 530))
        font = QFont()
        font.setPointSize(10)
        MainWindow.setFont(font)
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionOpen_File = QAction(MainWindow)
        self.actionOpen_File.setObjectName(u"actionOpen_File")
        self.actionUTF_8 = QAction(MainWindow)
        self.actionUTF_8.setObjectName(u"actionUTF_8")
        self.actionUTF_8.setCheckable(True)
        self.actionASCII = QAction(MainWindow)
        self.actionASCII.setObjectName(u"actionASCII")
        self.actionASCII.setCheckable(True)
        self.actionUTF_16 = QAction(MainWindow)
        self.actionUTF_16.setObjectName(u"actionUTF_16")
        self.actionUTF_16.setCheckable(True)
        self.actionUTF_32 = QAction(MainWindow)
        self.actionUTF_32.setObjectName(u"actionUTF_32")
        self.actionUTF_32.setCheckable(True)
        self.actionGBK_GB2312 = QAction(MainWindow)
        self.actionGBK_GB2312.setObjectName(u"actionGBK_GB2312")
        self.actionGBK_GB2312.setCheckable(True)
        self.actionGBK_GB2312.setChecked(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(5, 3, 186, 306))
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(False)
        self.groupBox.setFont(font1)
        self.groupBox.setAutoFillBackground(False)
        self.groupBox.setFlat(False)
        self.comboBox_SPort = QComboBox(self.groupBox)
        self.comboBox_SPort.setObjectName(u"comboBox_SPort")
        self.comboBox_SPort.setGeometry(QRect(80, 65, 91, 26))
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 65, 66, 26))
        self.label.setFont(font1)
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 105, 66, 26))
        self.label_2.setFont(font1)
        self.comboBox_BRate = QComboBox(self.groupBox)
        self.comboBox_BRate.setObjectName(u"comboBox_BRate")
        self.comboBox_BRate.setGeometry(QRect(80, 105, 91, 26))
        self.comboBox_BSize = QComboBox(self.groupBox)
        self.comboBox_BSize.setObjectName(u"comboBox_BSize")
        self.comboBox_BSize.setGeometry(QRect(80, 145, 91, 26))
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 145, 66, 26))
        self.label_3.setFont(font1)
        self.comboBox_SBit = QComboBox(self.groupBox)
        self.comboBox_SBit.setObjectName(u"comboBox_SBit")
        self.comboBox_SBit.setGeometry(QRect(80, 185, 91, 26))
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 185, 66, 26))
        self.label_4.setFont(font1)
        self.comboBox_PBit = QComboBox(self.groupBox)
        self.comboBox_PBit.setObjectName(u"comboBox_PBit")
        self.comboBox_PBit.setGeometry(QRect(80, 225, 91, 26))
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(10, 225, 66, 26))
        self.label_5.setFont(font1)
        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(10, 25, 66, 26))
        self.label_7.setFont(font1)
        self.pushButton_Check = QPushButton(self.groupBox)
        self.pushButton_Check.setObjectName(u"pushButton_Check")
        self.pushButton_Check.setGeometry(QRect(80, 25, 91, 26))
        self.pushButton_Check.setMouseTracking(False)
        self.pushButton_Check.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.pushButton_Check.setAutoFillBackground(False)
        self.pushButton_Check.setStyleSheet(u"")
        self.pushButton_Check.setAutoDefault(True)
        self.pushButton_Check.setFlat(False)
        self.pushButton_Open = QPushButton(self.groupBox)
        self.pushButton_Open.setObjectName(u"pushButton_Open")
        self.pushButton_Open.setGeometry(QRect(15, 265, 71, 31))
        font2 = QFont()
        font2.setPointSize(11)
        font2.setBold(False)
        self.pushButton_Open.setFont(font2)
        self.pushButton_Open.setMouseTracking(False)
        self.pushButton_Open.setTabletTracking(False)
        self.pushButton_Open.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.pushButton_Open.setAcceptDrops(False)
        self.pushButton_Open.setAutoFillBackground(False)
        self.pushButton_Open.setStyleSheet(u"")
        self.pushButton_Open.setCheckable(False)
        self.pushButton_Open.setAutoRepeat(False)
        self.pushButton_Open.setAutoExclusive(False)
        self.pushButton_Open.setAutoDefault(True)
        self.pushButton_Open.setFlat(False)
        self.pushButton_Close = QPushButton(self.groupBox)
        self.pushButton_Close.setObjectName(u"pushButton_Close")
        self.pushButton_Close.setGeometry(QRect(100, 265, 71, 31))
        self.pushButton_Close.setFont(font2)
        self.pushButton_Close.setMouseTracking(False)
        self.pushButton_Close.setAutoDefault(True)
        self.label_togglebt = QLabel(self.groupBox)
        self.label_togglebt.setObjectName(u"label_togglebt")
        self.label_togglebt.setGeometry(QRect(10, 265, 66, 30))
        self.label_togglebt.setFont(font1)
        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(5, 315, 741, 162))
        self.groupBox_2.setAutoFillBackground(False)
        self.groupBox_2.setFlat(False)
        self.SendTab = QTabWidget(self.groupBox_2)
        self.SendTab.setObjectName(u"SendTab")
        self.SendTab.setGeometry(QRect(2, 20, 736, 140))
        self.SendTab.setAutoFillBackground(False)
        self.SendTab.setStyleSheet(u"alternate-background-color: rgb(241, 241, 241);")
        self.single = QWidget()
        self.single.setObjectName(u"single")
        self.textEdit_sSend = QTextEdit(self.single)
        self.textEdit_sSend.setObjectName(u"textEdit_sSend")
        self.textEdit_sSend.setGeometry(QRect(0, 0, 541, 111))
        self.textEdit_sSend.setStyleSheet(u"background-color: rgb(199, 237, 204);")
        self.textEdit_sSend.setFrameShape(QFrame.Shape.Panel)
        self.textEdit_sSend.setFrameShadow(QFrame.Shadow.Sunken)
        self.textEdit_sSend.setAcceptRichText(False)
        self.checkBox_sCycle = QCheckBox(self.single)
        self.checkBox_sCycle.setObjectName(u"checkBox_sCycle")
        self.checkBox_sCycle.setGeometry(QRect(550, 80, 81, 26))
        self.lineEdit_sCycle = QLineEdit(self.single)
        self.lineEdit_sCycle.setObjectName(u"lineEdit_sCycle")
        self.lineEdit_sCycle.setGeometry(QRect(640, 80, 81, 26))
        self.lineEdit_sCycle.setStyleSheet(u"")
        self.checkBox_sNewline = QCheckBox(self.single)
        self.checkBox_sNewline.setObjectName(u"checkBox_sNewline")
        self.checkBox_sNewline.setGeometry(QRect(640, 5, 81, 26))
        self.checkBox_sHexmode = QCheckBox(self.single)
        self.checkBox_sHexmode.setObjectName(u"checkBox_sHexmode")
        self.checkBox_sHexmode.setGeometry(QRect(640, 45, 85, 26))
        self.pushButton_sSend = QPushButton(self.single)
        self.pushButton_sSend.setObjectName(u"pushButton_sSend")
        self.pushButton_sSend.setGeometry(QRect(550, 5, 71, 26))
        self.pushButton_sSend.setAutoDefault(True)
        self.pushButton_sClear = QPushButton(self.single)
        self.pushButton_sClear.setObjectName(u"pushButton_sClear")
        self.pushButton_sClear.setGeometry(QRect(550, 45, 71, 26))
        self.pushButton_sClear.setAutoDefault(True)
        self.SendTab.addTab(self.single, "")
        self.multi = QWidget()
        self.multi.setObjectName(u"multi")
        self.checkBox_m1 = QCheckBox(self.multi)
        self.checkBox_m1.setObjectName(u"checkBox_m1")
        self.checkBox_m1.setGeometry(QRect(10, 6, 21, 26))
        self.lineEdit_m1 = QLineEdit(self.multi)
        self.lineEdit_m1.setObjectName(u"lineEdit_m1")
        self.lineEdit_m1.setGeometry(QRect(30, 6, 211, 26))
        self.lineEdit_m1.setAutoFillBackground(False)
        self.lineEdit_m1.setStyleSheet(u"")
        self.lineEdit_m1.setFrame(True)
        self.lineEdit_m2 = QLineEdit(self.multi)
        self.lineEdit_m2.setObjectName(u"lineEdit_m2")
        self.lineEdit_m2.setGeometry(QRect(30, 43, 211, 26))
        self.lineEdit_m2.setStyleSheet(u"")
        self.checkBox_m2 = QCheckBox(self.multi)
        self.checkBox_m2.setObjectName(u"checkBox_m2")
        self.checkBox_m2.setGeometry(QRect(10, 43, 21, 26))
        self.lineEdit_m3 = QLineEdit(self.multi)
        self.lineEdit_m3.setObjectName(u"lineEdit_m3")
        self.lineEdit_m3.setGeometry(QRect(30, 80, 211, 26))
        self.lineEdit_m3.setStyleSheet(u"")
        self.lineEdit_m3.setFrame(True)
        self.checkBox_m3 = QCheckBox(self.multi)
        self.checkBox_m3.setObjectName(u"checkBox_m3")
        self.checkBox_m3.setGeometry(QRect(10, 80, 21, 26))
        self.pushButton_m1 = QPushButton(self.multi)
        self.pushButton_m1.setObjectName(u"pushButton_m1")
        self.pushButton_m1.setGeometry(QRect(250, 6, 41, 26))
        self.pushButton_m1.setAutoFillBackground(False)
        self.pushButton_m1.setAutoDefault(True)
        self.pushButton_m2 = QPushButton(self.multi)
        self.pushButton_m2.setObjectName(u"pushButton_m2")
        self.pushButton_m2.setGeometry(QRect(250, 43, 41, 26))
        self.pushButton_m2.setAutoDefault(True)
        self.pushButton_m3 = QPushButton(self.multi)
        self.pushButton_m3.setObjectName(u"pushButton_m3")
        self.pushButton_m3.setGeometry(QRect(250, 80, 41, 26))
        self.pushButton_m3.setAutoDefault(True)
        self.pushButton_m4 = QPushButton(self.multi)
        self.pushButton_m4.setObjectName(u"pushButton_m4")
        self.pushButton_m4.setGeometry(QRect(560, 6, 41, 26))
        self.pushButton_m4.setAutoDefault(True)
        self.checkBox_m5 = QCheckBox(self.multi)
        self.checkBox_m5.setObjectName(u"checkBox_m5")
        self.checkBox_m5.setGeometry(QRect(320, 43, 21, 26))
        self.pushButton_m5 = QPushButton(self.multi)
        self.pushButton_m5.setObjectName(u"pushButton_m5")
        self.pushButton_m5.setGeometry(QRect(560, 43, 41, 26))
        self.pushButton_m5.setAutoDefault(True)
        self.pushButton_m6 = QPushButton(self.multi)
        self.pushButton_m6.setObjectName(u"pushButton_m6")
        self.pushButton_m6.setGeometry(QRect(560, 80, 41, 26))
        self.pushButton_m6.setAutoDefault(True)
        self.checkBox_m6 = QCheckBox(self.multi)
        self.checkBox_m6.setObjectName(u"checkBox_m6")
        self.checkBox_m6.setGeometry(QRect(320, 80, 21, 26))
        self.checkBox_m4 = QCheckBox(self.multi)
        self.checkBox_m4.setObjectName(u"checkBox_m4")
        self.checkBox_m4.setGeometry(QRect(320, 6, 21, 26))
        self.lineEdit_m6 = QLineEdit(self.multi)
        self.lineEdit_m6.setObjectName(u"lineEdit_m6")
        self.lineEdit_m6.setGeometry(QRect(340, 80, 211, 26))
        self.lineEdit_m6.setStyleSheet(u"")
        self.lineEdit_m4 = QLineEdit(self.multi)
        self.lineEdit_m4.setObjectName(u"lineEdit_m4")
        self.lineEdit_m4.setGeometry(QRect(340, 6, 211, 26))
        self.lineEdit_m4.setStyleSheet(u"")
        self.lineEdit_m5 = QLineEdit(self.multi)
        self.lineEdit_m5.setObjectName(u"lineEdit_m5")
        self.lineEdit_m5.setGeometry(QRect(340, 43, 211, 26))
        self.lineEdit_m5.setStyleSheet(u"")
        self.checkBox_mNewLine = QCheckBox(self.multi)
        self.checkBox_mNewLine.setObjectName(u"checkBox_mNewLine")
        self.checkBox_mNewLine.setGeometry(QRect(630, 0, 91, 26))
        self.checkBox_mHexMode = QCheckBox(self.multi)
        self.checkBox_mHexMode.setObjectName(u"checkBox_mHexMode")
        self.checkBox_mHexMode.setGeometry(QRect(630, 30, 91, 26))
        self.lineEdit_mCycle = QLineEdit(self.multi)
        self.lineEdit_mCycle.setObjectName(u"lineEdit_mCycle")
        self.lineEdit_mCycle.setGeometry(QRect(630, 82, 81, 21))
        self.checkBox_mCycle = QCheckBox(self.multi)
        self.checkBox_mCycle.setObjectName(u"checkBox_mCycle")
        self.checkBox_mCycle.setGeometry(QRect(630, 60, 91, 21))
        self.SendTab.addTab(self.multi, "")
        self.file = QWidget()
        self.file.setObjectName(u"file")
        self.lineEdit_fFile = QLineEdit(self.file)
        self.lineEdit_fFile.setObjectName(u"lineEdit_fFile")
        self.lineEdit_fFile.setGeometry(QRect(50, 20, 401, 31))
        self.lineEdit_fFile.setStyleSheet(u"")
        self.label_6 = QLabel(self.file)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(10, 20, 36, 31))
        self.pushButton_fSelect = QPushButton(self.file)
        self.pushButton_fSelect.setObjectName(u"pushButton_fSelect")
        self.pushButton_fSelect.setGeometry(QRect(460, 20, 61, 31))
        self.pushButton_fSelect.setStyleSheet(u"")
        self.pushButton_fSelect.setAutoDefault(True)
        self.pushButton_fSend = QPushButton(self.file)
        self.pushButton_fSend.setObjectName(u"pushButton_fSend")
        self.pushButton_fSend.setGeometry(QRect(530, 20, 61, 31))
        self.pushButton_fSend.setStyleSheet(u"")
        self.pushButton_fSend.setAutoDefault(True)
        self.label_8 = QLabel(self.file)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(50, 70, 351, 21))
        self.SendTab.addTab(self.file, "")
        self.guide = QWidget()
        self.guide.setObjectName(u"guide")
        self.plainTextEdit_Guide = QPlainTextEdit(self.guide)
        self.plainTextEdit_Guide.setObjectName(u"plainTextEdit_Guide")
        self.plainTextEdit_Guide.setGeometry(QRect(0, 0, 731, 111))
        self.plainTextEdit_Guide.setFont(font)
        self.plainTextEdit_Guide.setStyleSheet(u"background-color: rgb(231,234,237);")
        self.plainTextEdit_Guide.setFrameShape(QFrame.Shape.StyledPanel)
        self.plainTextEdit_Guide.setFrameShadow(QFrame.Shadow.Plain)
        self.plainTextEdit_Guide.setReadOnly(True)
        self.SendTab.addTab(self.guide, "")
        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(200, 3, 546, 306))
        self.groupBox_3.setAutoFillBackground(False)
        self.groupBox_3.setFlat(False)
        self.textEdit_Receive = QTextEdit(self.groupBox_3)
        self.textEdit_Receive.setObjectName(u"textEdit_Receive")
        self.textEdit_Receive.setGeometry(QRect(5, 20, 536, 251))
        self.textEdit_Receive.setStyleSheet(u"background-color: rgb(199, 237, 204);")
        self.textEdit_Receive.setFrameShape(QFrame.Shape.Panel)
        self.textEdit_Receive.setFrameShadow(QFrame.Shadow.Sunken)
        self.textEdit_Receive.setLineWidth(1)
        self.textEdit_Receive.setReadOnly(True)
        self.checkBox_RHexmode = QCheckBox(self.groupBox_3)
        self.checkBox_RHexmode.setObjectName(u"checkBox_RHexmode")
        self.checkBox_RHexmode.setGeometry(QRect(270, 275, 85, 26))
        self.pushButton_RClear = QPushButton(self.groupBox_3)
        self.pushButton_RClear.setObjectName(u"pushButton_RClear")
        self.pushButton_RClear.setGeometry(QRect(370, 275, 71, 26))
        self.pushButton_RClear.setMouseTracking(False)
        self.pushButton_RClear.setAutoDefault(True)
        self.pushButton_RSave = QPushButton(self.groupBox_3)
        self.pushButton_RSave.setObjectName(u"pushButton_RSave")
        self.pushButton_RSave.setGeometry(QRect(455, 275, 71, 26))
        self.pushButton_RSave.setMouseTracking(False)
        self.pushButton_RSave.setAutoDefault(True)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 750, 33))
        self.menubar.setFont(font)
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuFile.setFont(font)
        self.menuAbout = QMenu(self.menubar)
        self.menuAbout.setObjectName(u"menuAbout")
        self.menuAbout.setFont(font1)
        self.menuSetting = QMenu(self.menubar)
        self.menuSetting.setObjectName(u"menuSetting")
        self.menuSetting.setFont(font)
        self.menuEncoding_Type = QMenu(self.menuSetting)
        self.menuEncoding_Type.setObjectName(u"menuEncoding_Type")
        font3 = QFont()
        font3.setPointSize(9)
        font3.setBold(False)
        self.menuEncoding_Type.setFont(font3)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSetting.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())
        self.menuFile.addAction(self.actionOpen_File)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuAbout.addAction(self.actionAbout)
        self.menuSetting.addAction(self.menuEncoding_Type.menuAction())
        self.menuEncoding_Type.addAction(self.actionASCII)
        self.menuEncoding_Type.addSeparator()
        self.menuEncoding_Type.addAction(self.actionUTF_8)
        self.menuEncoding_Type.addSeparator()
        self.menuEncoding_Type.addAction(self.actionUTF_16)
        self.menuEncoding_Type.addSeparator()
        self.menuEncoding_Type.addAction(self.actionUTF_32)
        self.menuEncoding_Type.addSeparator()
        self.menuEncoding_Type.addAction(self.actionGBK_GB2312)

        self.retranslateUi(MainWindow)

        self.pushButton_Check.setDefault(False)
        self.pushButton_Open.setDefault(False)
        self.pushButton_Close.setDefault(False)
        self.SendTab.setCurrentIndex(0)
        self.pushButton_sSend.setDefault(False)
        self.pushButton_sClear.setDefault(False)
        self.pushButton_RClear.setDefault(False)
        self.pushButton_RSave.setDefault(False)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionOpen_File.setText(QCoreApplication.translate("MainWindow", u"Open File", None))
        self.actionUTF_8.setText(QCoreApplication.translate("MainWindow", u"UTF-8", None))
        self.actionASCII.setText(QCoreApplication.translate("MainWindow", u"ASCII", None))
        self.actionUTF_16.setText(QCoreApplication.translate("MainWindow", u"UTF-16", None))
        self.actionUTF_32.setText(QCoreApplication.translate("MainWindow", u"UTF-32", None))
        self.actionGBK_GB2312.setText(QCoreApplication.translate("MainWindow", u"GBK/GB2312", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"SerialPort", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"BaudRate", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"ByteSize", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"StopBits", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"ParityBits ", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"CheckPort", None))
        self.pushButton_Check.setText(QCoreApplication.translate("MainWindow", u"Check", None))
        self.pushButton_Open.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.pushButton_Close.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.label_togglebt.setText(QCoreApplication.translate("MainWindow", u"ON/OFF", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Send", None))
        self.textEdit_sSend.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Microsoft YaHei UI'; font-size:10pt; color:#0000ff;\">https://github.com/kainan-tek/PyCom</span></p></body></html>", None))
        self.checkBox_sCycle.setText(QCoreApplication.translate("MainWindow", u"Cycle(ms)", None))
        self.lineEdit_sCycle.setText(QCoreApplication.translate("MainWindow", u"1000", None))
        self.checkBox_sNewline.setText(QCoreApplication.translate("MainWindow", u"NewLine", None))
        self.checkBox_sHexmode.setText(QCoreApplication.translate("MainWindow", u"HexMode", None))
        self.pushButton_sSend.setText(QCoreApplication.translate("MainWindow", u"Send", None))
        self.pushButton_sClear.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.SendTab.setTabText(self.SendTab.indexOf(self.single), QCoreApplication.translate("MainWindow", u"Single", None))
        self.checkBox_m1.setText("")
        self.checkBox_m2.setText("")
        self.checkBox_m3.setText("")
        self.pushButton_m1.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.pushButton_m2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.pushButton_m3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.pushButton_m4.setText(QCoreApplication.translate("MainWindow", u"4", None))
        self.checkBox_m5.setText("")
        self.pushButton_m5.setText(QCoreApplication.translate("MainWindow", u"5", None))
        self.pushButton_m6.setText(QCoreApplication.translate("MainWindow", u"6", None))
        self.checkBox_m6.setText("")
        self.checkBox_m4.setText("")
        self.checkBox_mNewLine.setText(QCoreApplication.translate("MainWindow", u"NewLine", None))
        self.checkBox_mHexMode.setText(QCoreApplication.translate("MainWindow", u"HexMode", None))
        self.lineEdit_mCycle.setText(QCoreApplication.translate("MainWindow", u"1000", None))
        self.checkBox_mCycle.setText(QCoreApplication.translate("MainWindow", u"Cycle(ms)", None))
        self.SendTab.setTabText(self.SendTab.indexOf(self.multi), QCoreApplication.translate("MainWindow", u"Multi", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u" File:", None))
        self.pushButton_fSelect.setText(QCoreApplication.translate("MainWindow", u"Select", None))
        self.pushButton_fSend.setText(QCoreApplication.translate("MainWindow", u"Send", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"support: 1. txt file   2. customized json file", None))
        self.SendTab.setTabText(self.SendTab.indexOf(self.file), QCoreApplication.translate("MainWindow", u"File", None))
        self.SendTab.setTabText(self.SendTab.indexOf(self.guide), QCoreApplication.translate("MainWindow", u"Guide", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Receive", None))
        self.checkBox_RHexmode.setText(QCoreApplication.translate("MainWindow", u"HexMode", None))
        self.pushButton_RClear.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.pushButton_RSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuAbout.setTitle(QCoreApplication.translate("MainWindow", u"About", None))
        self.menuSetting.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.menuEncoding_Type.setTitle(QCoreApplication.translate("MainWindow", u"Encoding Set", None))
    # retranslateUi


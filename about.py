from PySide6.QtGui import QTextCursor, QIcon
from PySide6.QtWidgets import QWidget

import globalvar as gl
from ui.about_ui import Ui_About


class About(QWidget):
    def __init__(self) -> None:
        """
        Initialize the About window class.
        """
        super(About, self).__init__()

        self.ui = Ui_About()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(":/icons/pycom"))

        self.ui_init()

    def ui_init(self) -> None:
        """
        Initialize the About window UI.
        """
        self.ui.textEdit_About.moveCursor(QTextCursor.MoveOperation.Start)
        self.ui.textEdit_About.insertPlainText(gl.AboutInfo)
        self.ui.textEdit_About.moveCursor(QTextCursor.MoveOperation.Start)

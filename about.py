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

        # Set up the UI
        self.ui: Ui_About = Ui_About()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(":/icons/pycom"))

        # Initialize the About window
        self.ui_init()

    def ui_init(self) -> None:
        """
        Initialize the About window UI.
        """
        # Move the cursor to the start of the text.
        self.ui.textEdit_About.moveCursor(QTextCursor.MoveOperation.Start)
        # Insert the text into the text edit widget.
        self.ui.textEdit_About.insertPlainText(gl.AboutInfo)  # type: str
        # Move the cursor back to the start of the text.
        self.ui.textEdit_About.moveCursor(
            QTextCursor.MoveOperation.Start
        )  # type: QTextCursor

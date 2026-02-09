from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget
from PySide6.QtCore import QPropertyAnimation, QRect, QEasingCurve, QByteArray


class ToggleButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self._btn_width = 80
        self._btn_height = 30
        self.setFixedSize(self._btn_width, self._btn_height)

        # Initialize button and thumb dimensions
        self.thumb_margin = 4
        self.thumb_size = self._btn_height - 2 * self.thumb_margin
        self.thumb_radius = self.thumb_size / 2
        self.btn_radius = self._btn_height / 2
        self.thumb_start_x = self.thumb_margin
        self.thumb_end_x = self._btn_width - self.thumb_size - self.thumb_margin

        # Create thumb widget
        self.thumb = QWidget(self)
        self.thumb.setGeometry(
            self.thumb_start_x, self.thumb_margin, self.thumb_size, self.thumb_size
        )

        # Setup initial style and animation
        self._init_style()
        self._init_animation()

        # Default text and signal connection
        self.setText("OFF")
        self.toggled.connect(self.animate_thumb)

    def _init_style(self) -> None:
        """
        Initialize the style for the toggle button and thumb.
        """
        self.thumb.setStyleSheet(
            f"""
            background-color: white;
            border-radius: {self.thumb_radius}px;
            border: 0px solid #d0d0d0;
            """
        )

        # Calculate font size based on button height
        font_size = max(10, int(self._btn_height * 0.4))

        # Set style for main button
        self.setStyleSheet(
            f"""
            QPushButton {{
            border-radius: {self.btn_radius}px;
            background-color: #e0e0e0;
            border: 0px solid #d0d0d0;
            font-weight: bold;
            color: #666666;
            font-size: {font_size}px;
            }}
            QPushButton:checked {{
            background-color: #0795FF;
            color: #f5f5f5;
            }}
            """
        )

    def _init_animation(self) -> None:
        """
        Initialize the animation for the thumb movement.
        """
        self.animation = QPropertyAnimation(self.thumb, QByteArray(b"geometry"))
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.finished.connect(self._animation_finished)

    def animate_thumb(self, checked):
        """
        Animate the thumb position when the button is toggled.
        """
        if self.animation.state() == QPropertyAnimation.State.Running:
            return

        # Update text based on checked state
        self.setText("ON" if checked else "OFF")

        # Set start and end positions for the animation
        if checked:
            start_rect = QRect(
                self.thumb_start_x, self.thumb_margin, self.thumb_size, self.thumb_size
            )
            end_rect = QRect(self.thumb_end_x, self.thumb_margin, self.thumb_size, self.thumb_size)
        else:
            start_rect = QRect(
                self.thumb_end_x, self.thumb_margin, self.thumb_size, self.thumb_size
            )
            end_rect = QRect(
                self.thumb_start_x, self.thumb_margin, self.thumb_size, self.thumb_size
            )

        # Start the animation
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.start()

    def _animation_finished(self):
        """
        This function is called when the animation finishes.
        """
        pass


if __name__ == "__main__":
    app = QApplication([])
    window = QMainWindow()
    window.setWindowTitle("Toggle Button Demo")
    window.setFixedSize(400, 200)

    toggle = ToggleButton()
    window.setCentralWidget(toggle)
    window.show()

    app.exec()

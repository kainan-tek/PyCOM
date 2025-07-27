from PySide6.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout
from PySide6.QtCore import QPropertyAnimation, QRect, QEasingCurve, QByteArray


class ToggleButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        # toggle button size
        self.btn_width = 80
        self.btn_height = 30
        self.setFixedSize(self.btn_width, self.btn_height)

        # size and position of the thumb
        thumb_margin = 3
        self.thumb_size = self.btn_height - 2 * thumb_margin
        self.thumb_radius = self.thumb_size / 2
        self.btn_radius = self.btn_height / 2
        self.thumb_start_x = thumb_margin
        self.thumb_end_x = self.btn_width - self.thumb_size - thumb_margin

        self._is_animating = False

        # button style  bg: #e0e0e0 #D4D7DC   #4CAF50 #0795FF
        self.setStyleSheet(f"""
            QPushButton {{
                border-radius: {self.btn_radius}px;
                background-color: #e0e0e0;
                border: 1px solid #d0d0d0;
                font-weight: bold;
                color: #666666;
                font-size: {max(10, int(self.btn_height * 0.4))}px;
            }}
            QPushButton:checked {{
                background-color: #0795FF;
                color: #f5f5f5;
            }}
        """)

        # create the thumb widget
        self.thumb = QWidget(self)
        self.thumb.setGeometry(
            self.thumb_start_x, thumb_margin, self.thumb_size, self.thumb_size
        )
        self.thumb.setStyleSheet(f"""
            background-color: white; 
            border-radius: {self.thumb_radius}px;
            border: 1px solid #d0d0d0;
        """)
        # self.thumb.update()

        # create the animation
        self.animation = QPropertyAnimation(self.thumb, QByteArray(b"geometry"))
        self.animation.setDuration(200)  # duration of the animation in milliseconds
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)  # InQuad InCubic OutBack OutCubic
        # self.animation.valueChanged.connect(lambda: self.thumb.update())
        self.animation.finished.connect(self._animation_finished)
        self.toggled.connect(self.animate_thumb)

        self.setText("OFF")

    def animate_thumb(self, checked):
        if self._is_animating:
            return

        self._is_animating = True
        self.animation.stop()

        if checked:
            self.setText("ON")
            self.animation.setStartValue(
                QRect(self.thumb_start_x, 3, self.thumb_size, self.thumb_size)
            )
            self.animation.setEndValue(
                QRect(self.thumb_end_x, 3, self.thumb_size, self.thumb_size)
            )
        else:
            self.setText("OFF")
            self.animation.setStartValue(
                QRect(self.thumb_end_x, 3, self.thumb_size, self.thumb_size)
            )
            self.animation.setEndValue(
                QRect(self.thumb_start_x, 3, self.thumb_size, self.thumb_size)
            )

        self.animation.start()

    def _animation_finished(self):
        self._is_animating = False


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.btn = ToggleButton()
        layout.addWidget(self.btn)
        self.setLayout(layout)

        self.setWindowTitle("Toggle Button Example")
        self.setStyleSheet("background-color: #f0f0f0;")
        self.resize(400, 200)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

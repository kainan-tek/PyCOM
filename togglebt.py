from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property, QRectF, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtCore import Qt


class ToggleButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        # Remove fixed size, use sizeHint and responsive drawing
        # self.setFixedSize(80, 30)

        # Initialize animation related properties
        self._thumb_position = 0.0  # 0.0 = OFF, 1.0 = ON
        self.thumb_margin = 3
        self.animation_duration = 200

        # Define colors
        self.bg_color_off = QColor("#e0e0e0")
        self.bg_color_on = QColor("#0795FF")
        self.thumb_color = QColor("white")
        self.border_color = QColor("#d0d0d0")
        self.text_color_off = QColor("#666666")
        self.text_color_on = QColor("#f5f5f5")

        # Create animation object, animate the custom property thumbPosition
        self.animation = QPropertyAnimation(self, b"thumbPosition")
        self.animation.setDuration(self.animation_duration)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Connect signals
        self.toggled.connect(self.on_toggled)

    # def sizeHint(self):
    #     """Return the recommended size for the widget"""
    #     return QSize(80, 30)

    def on_toggled(self, checked):
        """当按钮被切换时触发动画"""
        if self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()  # Stop if animation is already running

        # Set the start and end values for the animation
        self.animation.setStartValue(self._thumb_position)
        self.animation.setEndValue(1.0 if checked else 0.0)
        self.animation.start()

    def get_thumb_position(self):
        """Getter for the thumb position property"""
        return self._thumb_position

    def set_thumb_position(self, pos):
        """Setter for the thumb position property"""
        # Ensure the value is between 0.0 and 1.0
        self._thumb_position = max(0.0, min(1.0, pos))
        self.update()  # Trigger repaint

    # Use Property decorator to register the custom property, making it animatable by QPropertyAnimation
    thumbPosition = Property(float, get_thumb_position, set_thumb_position)

    def paintEvent(self, event):
        """Override paintEvent to draw the toggle button"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # Antialiasing
        painter.setPen(Qt.PenStyle.NoPen)

        rect = self.rect()
        h = rect.height()
        w = rect.width()

        # Calculate the track rectangle
        track_rect = QRectF(0, 0, w, h)

        # Set background color based on checked state
        if self.isChecked():
            painter.setBrush(self.bg_color_on)
        else:
            painter.setBrush(self.bg_color_off)

        # Draw the rounded rectangle track
        track_radius = h / 2.0
        painter.drawRoundedRect(track_rect, track_radius, track_radius)

        # Calculate the size and position of the thumb
        thumb_size = h - 2 * self.thumb_margin
        # Interpolate the X coordinate of the thumb based on _thumb_position
        thumb_x = (
            self.thumb_margin
            + (w - thumb_size - 2 * self.thumb_margin) * self._thumb_position
        )
        thumb_rect = QRectF(thumb_x, self.thumb_margin, thumb_size, thumb_size)
        thumb_radius = thumb_size / 2.0

        # Draw the thumb
        painter.setBrush(self.thumb_color)
        painter.setPen(QPen(self.border_color, 1))
        painter.drawEllipse(thumb_rect)

        # Draw the text
        font = painter.font()
        font.setBold(True)
        font.setPointSizeF(max(6, h * 0.3))  # Adjust font size based on height
        painter.setFont(font)

        if self.isChecked():
            painter.setPen(self.text_color_on)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "ON")
        else:
            painter.setPen(self.text_color_off)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "OFF")


# --- Example Code ---
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Toggle Button Demo")
    window.resize(400, 200)

    toggle = ToggleButton()
    # You can set different sizes to test responsiveness
    # toggle.setFixedSize(100, 40)

    window.setCentralWidget(toggle)
    window.show()

    sys.exit(app.exec())

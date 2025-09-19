from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QPropertyAnimation, QEvent


class AnimatedButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
        """)
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(120)

    def enterEvent(self, event: QEvent):
        rect = self.geometry()
        self.anim.stop()
        self.anim.setStartValue(rect)
        self.anim.setEndValue(rect.adjusted(-2, -2, 2, 2))  # expand
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        rect = self.geometry()
        self.anim.stop()
        self.anim.setStartValue(rect)
        self.anim.setEndValue(rect.adjusted(2, 2, -2, -2))  # shrink
        self.anim.start()
        super().leaveEvent(event)

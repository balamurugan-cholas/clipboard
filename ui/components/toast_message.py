from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation

class ToastMessage(QWidget):
    active_toasts = []  # Class-level list to track active toasts

    def __init__(self, message, parent=None, duration=2000):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.ToolTip
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Label for message
        self.label = QLabel(message, self)
        self.label.setStyleSheet("""
            background-color: rgba(50, 50, 50, 220);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
        """)
        self.label.adjustSize()
        self.resize(self.label.size())

        # Duration timer
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_toast)
        self.timer.start(duration)

        # Fade-in animation
        self.anim_in = QPropertyAnimation(self, b"windowOpacity")
        self.anim_in.setDuration(300)
        self.setWindowOpacity(0)
        self.anim_in.setStartValue(0)
        self.anim_in.setEndValue(1)
        self.anim_in.start()

        # Add to active toast list for stacking
        ToastMessage.active_toasts.append(self)

    def show_toast(self):
        self.update_position()
        self.show()

    def update_position(self):
        """Stack toasts above each other at bottom-left."""
        screen_geom = QApplication.primaryScreen().availableGeometry()
        x = 20
        # Position above existing toasts
        y = screen_geom.height() - self.height() - 20
        for t in ToastMessage.active_toasts[:-1]:
            y -= t.height() + 10  # spacing between toasts
        self.move(x, y)

    def hide_toast(self):
        # Fade-out animation
        self.anim_out = QPropertyAnimation(self, b"windowOpacity")
        self.anim_out.setDuration(300)
        self.anim_out.setStartValue(1)
        self.anim_out.setEndValue(0)
        self.anim_out.finished.connect(self.close_toast)
        self.anim_out.start()

    def close_toast(self):
        if self in ToastMessage.active_toasts:
            ToastMessage.active_toasts.remove(self)
        self.close()

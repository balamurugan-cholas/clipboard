from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import Qt, pyqtSignal

class TopBar(QWidget):
    # Signal to emit search text to parent/main window
    search_triggered = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # App name
        app_name = QLabel("NeuroDesk")
        app_name.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(app_name, alignment=Qt.AlignmentFlag.AlignVCenter)

        layout.addStretch()

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.setFixedSize(260, 32)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 5px 10px;
                font-size: 14px;
                background: #fff;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
        """)
        layout.addWidget(self.search_bar, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addStretch()

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setColor(QColor("#2196F3"))
        shadow.setOffset(0, 0)
        self.search_bar.setGraphicsEffect(shadow)

        # Settings button
        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(QIcon("ui/resources/icons/setting.png"))
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                background: #f0f0f0;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.settings_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Connect Enter key to search
        self.search_bar.returnPressed.connect(self.emit_search)

    def emit_search(self):
        text = self.search_bar.text().strip()
        self.search_triggered.emit(text)

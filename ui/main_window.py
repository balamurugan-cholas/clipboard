from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget,
    QSystemTrayIcon, QMenu, QApplication, QStyle
)
from PyQt6.QtCore import Qt
from ui.components.clipboard_list import ClipboardList
from ui.components.bottom_bar import BottomBar
from ui.components.top_bar import TopBar
from ui.components.settings_window import SettingsWindow
import json, os
import keyboard  # global hotkey

SETTINGS_FILE = "settings.json"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeuroDesk")
        self.resize(700, 500)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top bar
        self.top_bar = TopBar()
        layout.addWidget(self.top_bar)

        # Clipboard list
        self.clipboard_list = ClipboardList()
        layout.addWidget(self.clipboard_list)

        # Bottom bar
        self.bottom_bar = BottomBar(self.clipboard_list)
        layout.addWidget(self.bottom_bar)

        # Settings window
        self.settings_window = SettingsWindow(parent=self)
        self.settings_visible = False

        # Connect settings button
        self.top_bar.settings_btn.clicked.connect(self.toggle_settings)

        # Connect search bar signal to highlight text in clipboard list
        self.top_bar.search_triggered.connect(self.clipboard_list.highlight_search)

        # Load saved settings
        self.apply_saved_settings()

        # --- System Tray Setup ---
        tray_icon = QApplication.instance().style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.setWindowIcon(tray_icon)

        self.tray_icon = QSystemTrayIcon(tray_icon, self)
        self.tray_icon.setToolTip("NeuroDesk")

        # Tray menu
        tray_menu = QMenu()
        restore_action = tray_menu.addAction("Restore")
        restore_action.triggered.connect(self.show_from_hotkey)
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.instance().quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # --- Global Hotkey ---
        keyboard.add_hotkey('ctrl+alt+e', lambda: self.show_from_hotkey())

    def toggle_settings(self):
        if self.settings_visible:
            self.settings_window.slide_out()
        else:
            self.settings_window.slide_in()
        self.settings_visible = not self.settings_visible

    def apply_saved_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                always_on_top = data.get("always_on_top", False)
                self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, always_on_top)
                self.show()
                self.settings_window.always_on_top.setChecked(always_on_top)
            except Exception:
                pass

    def closeEvent(self, event):
        """Minimize to tray instead of closing."""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "NeuroDesk",
            "Application minimized to tray.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def on_tray_icon_activated(self, reason):
        """Restore window on double-click."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_from_hotkey()

    def show_from_hotkey(self):
        """Show the app from tray or hotkey."""
        self.showNormal()
        self.raise_()
        self.activateWindow()

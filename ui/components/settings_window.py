# ui/components/settings_window.py
import json
import os
import sys
import shutil
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect

try:
    import winshell  # optional, makes shortcut easier
except ImportError:
    winshell = None

SETTINGS_FILE = "settings.json"


class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.is_animating = False

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setFixedWidth(250)
        self.setStyleSheet("background-color: #f9f9f9; border-left: 1px solid #ccc;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Always on top
        self.always_on_top = QCheckBox("Always on top")
        self.always_on_top.stateChanged.connect(self.toggle_always_on_top)
        layout.addWidget(self.always_on_top)

        # Launch on startup
        self.launch_startup = QCheckBox("Launch on startup")
        self.launch_startup.stateChanged.connect(self.toggle_launch_startup)
        layout.addWidget(self.launch_startup)

        layout.addStretch()

        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.setFixedHeight(28)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
        """)
        self.close_btn.clicked.connect(self.slide_out)
        layout.addWidget(self.close_btn)

        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        if self.parent_window:
            parent_geom = self.parent_window.geometry()
            self.setGeometry(QRect(parent_geom.width(), 0, self.width(), parent_geom.height()))

        self.hide()
        self.load_settings()

    # ---------------- Settings persistence ----------------
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.always_on_top.setChecked(data.get("always_on_top", False))
                self.launch_startup.setChecked(data.get("launch_on_startup", False))
                self.apply_always_on_top(data.get("always_on_top", False))
            except Exception:
                pass
        else:
            self.always_on_top.setChecked(False)
            self.launch_startup.setChecked(False)

    def save_settings(self):
        data = {
            "always_on_top": self.always_on_top.isChecked(),
            "launch_on_startup": self.launch_startup.isChecked()
        }
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass

    # ---------------- Always on top ----------------
    def toggle_always_on_top(self, state):
        flag_on = state == Qt.CheckState.Checked.value
        self.apply_always_on_top(flag_on)
        self.save_settings()

    def apply_always_on_top(self, flag_on: bool):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, flag_on)
        if self.parent_window:
            self.parent_window.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, flag_on)
            self.parent_window.show()
        self.show()

    # ---------------- Launch on startup ----------------
    def toggle_launch_startup(self, state):
        enable = state == Qt.CheckState.Checked.value
        if enable:
            self.enable_startup()
        else:
            self.disable_startup()
        self.save_settings()

    def enable_startup(self):
        startup_dir = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
        exe_path = sys.argv[0]  # when compiled, this will be your .exe path
        shortcut_path = os.path.join(startup_dir, "NeuroDesk.lnk")

        try:
            if winshell:  # with winshell
                with winshell.shortcut(shortcut_path) as link:
                    link.path = exe_path
                    link.description = "NeuroDesk Autostart"
            else:  # fallback - copy exe if no winshell
                if os.path.exists(exe_path):
                    shutil.copy(exe_path, shortcut_path)
        except Exception as e:
            print("Failed to set startup:", e)

    def disable_startup(self):
        startup_dir = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
        shortcut_path = os.path.join(startup_dir, "NeuroDesk.lnk")
        try:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
        except Exception as e:
            print("Failed to disable startup:", e)

    # ---------------- Slide animation ----------------
    def slide_in(self):
        if self.isVisible() or self.is_animating or not self.parent_window:
            return
        self.is_animating = True
        self.show()

        parent_geom = self.parent_window.geometry()
        start_rect = QRect(parent_geom.width(), 0, self.width(), parent_geom.height())
        end_rect = QRect(parent_geom.width() - self.width(), 0, self.width(), parent_geom.height())

        self.anim.stop()
        try:
            self.anim.finished.disconnect()
        except Exception:
            pass

        self.setGeometry(start_rect)
        self.anim.setStartValue(start_rect)
        self.anim.setEndValue(end_rect)

        def on_finished():
            self.is_animating = False

        self.anim.finished.connect(on_finished)
        self.anim.start()

    def slide_out(self):
        if not self.isVisible() or self.is_animating or not self.parent_window:
            return
        self.is_animating = True
        start_rect = self.geometry()
        end_rect = QRect(self.parent_window.width(), 0, self.width(), self.parent_window.height())

        self.anim.stop()
        try:
            self.anim.finished.disconnect()
        except Exception:
            pass

        self.anim.setStartValue(start_rect)
        self.anim.setEndValue(end_rect)

        def on_finished():
            self.hide()
            self.is_animating = False
            self.save_settings()

        self.anim.finished.connect(on_finished)
        self.anim.start()
# backend/clipboard_manager.py
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QApplication


class ClipboardManager(QObject):
    def __init__(self, app: QApplication, clipboard_list):
        super().__init__()
        self.app = app
        self.clipboard_list = clipboard_list
        self.clipboard = app.clipboard()
        self.suppress_next = False  # avoid self-triggered additions
        self._paused = False       # pause/resume flag

        # Connect clipboard change
        self.clipboard.dataChanged.connect(self.handle_clipboard_change)

    def handle_clipboard_change(self):
        """Called whenever the system clipboard changes."""
        if self._paused:
            return  # skip monitoring if paused

        text = self.clipboard.text()
        if not text:
            return

        # Suppress own clipboard sets
        if self.suppress_next:
            self.suppress_next = False
            return

        # Add text to UI
        self.clipboard_list.add_clipboard_entry(text)

    def set_clipboard_text(self, text: str):
        """Copy text to clipboard without creating a duplicate row."""
        self.suppress_next = True
        self.clipboard.setText(text)

    def set_paused(self, paused: bool):
        """Pause or resume clipboard monitoring."""
        self._paused = paused

    @property
    def paused(self):
        return self._paused

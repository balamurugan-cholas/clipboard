# ui/components/bottom_bar.py
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog, QApplication


class BottomBar(QWidget):
    def __init__(self, clipboard_list):
        """
        clipboard_list: instance of ClipboardList to perform actions on
        """
        super().__init__()
        self.clipboard_list = clipboard_list
        self.monitoring_active = True  # initial monitoring status

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # Left: Monitoring status
        self.status_label = QLabel("Monitoring: Active")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Pause/Resume button
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setFixedHeight(28)
        self.pause_btn.setStyleSheet(self._button_style())
        self.pause_btn.clicked.connect(self.toggle_monitoring)
        layout.addWidget(self.pause_btn)

        # Clear All button
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setFixedHeight(28)
        self.clear_btn.setStyleSheet(self._button_style())
        self.clear_btn.clicked.connect(self.clear_all)
        layout.addWidget(self.clear_btn)

        # Export button
        self.export_btn = QPushButton("Export")
        self.export_btn.setFixedHeight(28)
        self.export_btn.setStyleSheet(self._button_style())
        self.export_btn.clicked.connect(self.export_clipboard)
        layout.addWidget(self.export_btn)

    def toggle_monitoring(self):
        """Toggle monitoring state and update UI text."""
        self.monitoring_active = not self.monitoring_active
        if self.monitoring_active:
            self.pause_btn.setText("Pause")
            self.status_label.setText("Monitoring: Active")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.pause_btn.setText("Resume")
            self.status_label.setText("Monitoring: Paused")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

        # Inform clipboard_manager if exists
        app = QApplication.instance()
        if app and hasattr(app, "clipboard_manager"):
            app.clipboard_manager.set_paused(not self.monitoring_active)

    def clear_all(self):
        """Clear all rows in the clipboard list."""
        if self.clipboard_list:
            self.clipboard_list.table.setRowCount(0)

    def export_clipboard(self):
        """Export all clipboard entries to a text file via file dialog."""
        if not self.clipboard_list or self.clipboard_list.table.rowCount() == 0:
            return  # nothing to export

        # Open file dialog to choose save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Clipboard History",
            "",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                for row in range(self.clipboard_list.table.rowCount()):
                    text_item = self.clipboard_list.table.item(row, 0)
                    date_item = self.clipboard_list.table.item(row, 1)
                    time_item = self.clipboard_list.table.item(row, 2)
                    line = f"[{date_item.text()} {time_item.text()}] {text_item.text()}\n"
                    f.write(line)

    def _button_style(self) -> str:
        return """
            QPushButton {
                background: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
        """

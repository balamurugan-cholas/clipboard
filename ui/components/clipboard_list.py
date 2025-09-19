from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QHBoxLayout,
    QPushButton,
    QApplication,
)
from PyQt6.QtCore import QDateTime, QTimer
from PyQt6.QtGui import QColor
from ui.components.view_window import ViewWindow
from ui.components.toast_message import ToastMessage  # import toast


class ClipboardList(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Text", "Date", "Time", "Actions"])
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                font-size: 13px;
                gridline-color: #ddd;
            }
            QTableWidget::item:hover {
                background: #f0f8ff;
            }
            QHeaderView::section {
                background: #f5f5f5;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)

    def add_clipboard_entry(self, text: str):
        # Ignore duplicate text
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text() == text:
                return  # Do not add duplicate

        # Insert new row at bottom
        row = self.table.rowCount()
        self.table.insertRow(row)

        now = QDateTime.currentDateTime()
        date_str = now.toString("yyyy-MM-dd")
        time_str = now.toString("HH:mm:ss")

        text_item = QTableWidgetItem(text)
        text_item.setFlags(text_item.flags())
        self.table.setItem(row, 0, text_item)
        self.table.setItem(row, 1, QTableWidgetItem(date_str))
        self.table.setItem(row, 2, QTableWidgetItem(time_str))

        self.add_actions(row, text)

    def add_actions(self, row, text):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        view_btn = QPushButton("View")
        view_btn.setFixedSize(60, 26)
        view_btn.setStyleSheet(self._btn_style())
        view_btn.clicked.connect(lambda _, t=text: self.open_view_window(t))
        layout.addWidget(view_btn)

        copy_btn = QPushButton("Copy")
        copy_btn.setFixedSize(60, 26)
        copy_btn.setStyleSheet(self._btn_style())
        copy_btn.clicked.connect(lambda _, t=text, b=copy_btn: self.copy_to_clipboard(t, b))
        layout.addWidget(copy_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setFixedSize(60, 26)
        delete_btn.setStyleSheet(self._btn_style())
        delete_btn.clicked.connect(lambda _, r=row: self.delete_row(r))
        layout.addWidget(delete_btn)

        container = QWidget()
        container.setLayout(layout)
        self.table.setCellWidget(row, 3, container)

    def delete_row(self, row: int):
        if 0 <= row < self.table.rowCount():
            self.table.removeRow(row)

    def delete_row_by_button(self, btn):
        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 3)
            if cell_widget and btn in cell_widget.findChildren(QPushButton):
                self.table.removeRow(row)
                break

    def open_view_window(self, text):
        view_win = ViewWindow(text)
        view_win.exec()

    def copy_to_clipboard(self, text, btn):
        QApplication.clipboard().setText(text)

        # Button feedback
        old_text = btn.text()
        old_style = btn.styleSheet()
        try:
            btn.setText("Copied")
            btn.setEnabled(False)
            btn.setStyleSheet(old_style + "background: #dff0d8; color: #2a7a2a; border-color: #c3e6cb;")
        except RuntimeError:
            pass

        def restore():
            try:
                if btn:
                    btn.setText(old_text)
                    btn.setEnabled(True)
                    btn.setStyleSheet(old_style)
            except RuntimeError:
                pass

        QTimer.singleShot(1000, restore)

        # Show toast
        toast = ToastMessage("Copied!", parent=self.window())
        toast.show_toast()

    def highlight_search(self, search_text: str):
        """Highlight all table rows that match the search text."""
        search_text = search_text.strip()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                if search_text and search_text.lower() in item.text().lower():
                    item.setBackground(QColor("#fff59d"))  # yellow highlight
                else:
                    item.setBackground(QColor("white"))  # remove highlight

    def _btn_style(self):
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

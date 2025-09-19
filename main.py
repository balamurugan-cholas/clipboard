import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from backend.clipboard_manager import ClipboardManager

def main():
    app = QApplication(sys.argv)

    # Create main window
    window = MainWindow()

    # Create clipboard manager, pass the window's clipboard_list
    clipboard_manager = ClipboardManager(app, window.clipboard_list)
    app.clipboard_manager = clipboard_manager  # optional, if you need global access

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

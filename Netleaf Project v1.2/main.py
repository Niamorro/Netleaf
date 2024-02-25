# main.py
import sys
from PySide6.QtWidgets import QApplication
from gui import DeviceScanner
import qdarktheme

if __name__ == '__main__':
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()
    scanner = DeviceScanner()
    sys.exit(app.exec())

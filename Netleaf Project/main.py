import sys
from PyQt5.QtWidgets import QApplication
from gui import DeviceScanner

if __name__ == '__main__':
    app = QApplication(sys.argv)
    scanner = DeviceScanner()
    sys.exit(app.exec_())

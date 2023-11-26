import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QProgressBar, QHBoxLayout, QFormLayout,
    QGroupBox, QCheckBox, QRadioButton, QButtonGroup, QDialog,
    QDialogButtonBox, QMainWindow, QAction, QMenuBar, QFileDialog, QComboBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QColor, QPalette, QIcon
import csv
from datetime import datetime
import configparser
from scanner import ScannerThread
from settings_window import SettingsWindow

class DeviceScanner(QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings = configparser.ConfigParser()

        if os.path.exists('settings.cfg'):
            self.settings.read('settings.cfg')
        else:
            self.create_default_settings()

        self.scan_count = 0
        self.init_ui()

    def init_ui(self):
        self.devices_label = QLabel('Connected Devices:')
        self.devices_info = QTextEdit()
        self.devices_info.setReadOnly(True)

        self.scan_button = QPushButton('Scan Devices')
        self.scan_button.clicked.connect(self.start_scanning)

        self.ip_range_label = QLabel('IP Range:')
        self.ip_range_start = QLineEdit('192.168.1.1')
        self.ip_range_end = QLineEdit('192.168.1.255')

        self.console_label = QLabel('Console:')
        self.console = QTextEdit()
        self.console.setReadOnly(True)

        self.progress_bar = QProgressBar()

        self.save_action = QAction('Save to File', self)
        self.save_action.triggered.connect(self.save_to_file)

        self.settings_menu = self.menuBar().addMenu('File')
        self.settings_menu.addAction(self.save_action)

        self.settings_menu = self.menuBar().addMenu('Settings')
        self.settings_action = QAction('Open Settings', self)
        self.settings_action.triggered.connect(self.show_settings)
        self.settings_menu.addAction(self.settings_action)

        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.devices_label)
        left_layout.addWidget(self.devices_info)
        left_layout.addWidget(self.ip_range_label)
        left_layout.addWidget(self.ip_range_start)
        left_layout.addWidget(self.ip_range_end)
        left_layout.addWidget(self.scan_button)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.console_label)
        right_layout.addWidget(self.console)
        right_layout.addWidget(self.progress_bar)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Netleaf')

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        self.scanner_thread = ScannerThread("", "")
        self.scanner_thread.result_signal.connect(self.update_results)

        self.setStyle(QApplication.setStyle('Fusion'))

        if self.settings.getboolean('Appearance', 'DarkMode'):
            self.set_theme('Dark')
        else:
            self.set_theme('Light')

        self.show()

    def set_theme(self, theme):
        palette = self.palette()
        if theme == 'Dark':
            dark_palette = QPalette()
            dark_palette.setColor(dark_palette.Window, QColor(53, 53, 53))
            dark_palette.setColor(dark_palette.WindowText, Qt.white)
            dark_palette.setColor(dark_palette.Base, QColor(25, 25, 25))
            dark_palette.setColor(dark_palette.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(dark_palette.ToolTipBase, Qt.white)
            dark_palette.setColor(dark_palette.ToolTipText, Qt.white)
            dark_palette.setColor(dark_palette.Text, Qt.white)
            dark_palette.setColor(dark_palette.Button, QColor(53, 53, 53))
            dark_palette.setColor(dark_palette.ButtonText, Qt.white)
            dark_palette.setColor(dark_palette.BrightText, Qt.red)
            dark_palette.setColor(dark_palette.Link, QColor(42, 130, 218))
            dark_palette.setColor(dark_palette.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(dark_palette.HighlightedText, Qt.black)
            self.setPalette(dark_palette)
        else:
            self.setPalette(QApplication.palette())

    def start_scanning(self):
        self.progress_bar.setValue(0)

        ip_start = self.ip_range_start.text()
        ip_end = self.ip_range_end.text()

        self.scanner_thread.ip_start = ip_start
        self.scanner_thread.ip_end = ip_end

        if not self.scanner_thread.isRunning():
            self.scan_count += 1
            self.scanner_thread.start()

    def update_results(self, ip, status, progress):
        if ip == "progress":
            self.progress_bar.setValue(progress)
        else:
            if "active" in status:
                self.devices_info.setTextColor(Qt.green)
            elif "inactive" in status:
                self.devices_info.setTextColor(Qt.red)
            elif "timeout" in status:
                self.devices_info.setTextColor(QColor (255,140,0))

            self.devices_info.append(f'{ip} - {status}')
            self.log(f'{ip} - {status}')

            self.write_to_file(f'{ip} - {status}')

    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f'[{timestamp}] {message}'
        self.console.append(log_message)

    def save_to_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'CSV Files (*.csv);;All Files (*)')
        if file_name:
            with open(file_name, 'w', newline='') as file:
                writer = csv.writer(file)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow(['Timestamp', 'Message'])
                writer.writerow([timestamp, 'Results saved to file.'])

    def write_to_file(self, message):
        file_name = f'scan_results_{self.scan_count}.csv'

        with open(file_name, 'a', newline='') as file:
            writer = csv.writer(file)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if os.path.getsize(file_name) == 0:
                writer.writerow(['Timestamp', 'Message'])

            log_message = f'[{timestamp}] {message}'
            writer.writerow([timestamp, message])

    def show_settings(self):
        settings_window = SettingsWindow(self)
        if settings_window.exec_() == QDialog.Accepted:
            theme_index = settings_window.dark_theme_combobox.currentIndex()
            theme = 'Dark' if theme_index == 1 else 'Light'
            self.set_theme(theme)

    def create_default_settings(self):
        self.settings['Appearance'] = {'DarkMode': 'False'}

        with open('settings.cfg', 'w') as configfile:
            self.settings.write(configfile)

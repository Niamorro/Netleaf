import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QProgressBar, QDialog,
    QMainWindow, QFileDialog, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QAction
from datetime import datetime
from scanner import ScannerThread
from settings_window import SettingsWindow
from port_scanner import PortScannerThread
import qdarktheme
import csv

class DeviceScanner(QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings = self.load_settings()
        self.scan_count = 0
        self.scan_results = []
        self.init_ui()

    def init_ui(self):
        self.devices_label = QLabel('Connected Devices:')
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(4)
        self.devices_table.setHorizontalHeaderLabels(['IP', 'Status', 'MAC', 'Response Time'])
        self.devices_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.devices_table.verticalHeader().setVisible(False)  # Добавьте эту строку

        self.scan_button = QPushButton('Scan Devices')
        self.scan_button.clicked.connect(self.start_scanning)

        self.ip_range_label = QLabel('IP Range:')
        self.ip_range_start = QLineEdit('192.168.1.1')
        self.ip_range_end = QLineEdit('192.168.1.255')

        self.progress_bar = QProgressBar()

        self.filter_label = QLabel('Filter:')
        self.filter_combobox = QComboBox()
        self.filter_combobox.addItems(['All', 'Active', 'Timeout', 'Inactive'])
        self.filter_combobox.setCurrentText('All')
        self.filter_combobox.currentIndexChanged.connect(self.apply_filter)

        self.save_action = QAction('Save to File', self)
        self.save_action.triggered.connect(self.save_to_file)

        self.settings_menu = self.menuBar().addMenu('File')
        self.settings_menu.addAction(self.save_action)

        self.settings_menu = self.menuBar().addMenu('Settings')
        self.settings_action = QAction('Open Settings', self)
        self.settings_action.triggered.connect(self.show_settings)
        self.settings_menu.addAction(self.settings_action)

        main_layout = QVBoxLayout()

        ip_scan_layout = QVBoxLayout()
        ip_scan_layout.addWidget(self.devices_label)
        ip_scan_layout.addWidget(self.devices_table)
        ip_scan_layout.addWidget(self.ip_range_label)
        ip_scan_layout.addWidget(self.ip_range_start)
        ip_scan_layout.addWidget(self.ip_range_end)
        ip_scan_layout.addWidget(self.scan_button)
        ip_scan_layout.addWidget(self.filter_label)
        ip_scan_layout.addWidget(self.filter_combobox)

        # port scan
        port_scan_layout = QVBoxLayout()
        self.port_ip_label = QLabel('IP Address:')
        self.port_ip_input = QLineEdit()
        self.port_range_label = QLabel('Port Range:')
        self.port_start_input = QLineEdit('1')
        self.port_end_input = QLineEdit('1024')
        self.port_scan_button = QPushButton('Scan Ports')
        self.port_scan_button.clicked.connect(self.start_port_scanning)
        self.port_results_table = QTableWidget()
        self.port_results_table.setColumnCount(4)
        self.port_results_table.setHorizontalHeaderLabels(['IP', 'Port', 'Status', 'Service'])
        self.port_results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        port_scan_layout.addWidget(self.port_ip_label)
        port_scan_layout.addWidget(self.port_ip_input)
        port_scan_layout.addWidget(self.port_range_label)
        port_scan_layout.addWidget(self.port_start_input)
        port_scan_layout.addWidget(self.port_end_input)
        port_scan_layout.addWidget(self.port_scan_button)
        port_scan_layout.addWidget(self.port_results_table)

        self.scan_type_tabs = QTabWidget()
        ip_scan_widget = QWidget()
        ip_scan_widget.setLayout(ip_scan_layout)
        self.scan_type_tabs.addTab(ip_scan_widget, "IP Scan")
        port_scan_widget = QWidget()
        port_scan_widget.setLayout(port_scan_layout)
        self.scan_type_tabs.addTab(port_scan_widget, "Port Scan")

        main_layout.addWidget(self.scan_type_tabs)
        main_layout.addWidget(self.progress_bar)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Netleaf')

        icon_path = 'icon.png'
        self.setWindowIcon(QIcon(icon_path))

        self.scanner_thread = ScannerThread("", "", "")
        self.scanner_thread.result_signal.connect(self.update_results)

        self.set_theme(self.settings.get('Appearance', {}).get('Theme', 'Light'))

        self.show()

    def load_settings(self):
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                return json.load(f)
        else:
            return self.create_default_settings()

    def create_default_settings(self):
        settings = {
            'Appearance': {'Theme': 'Light'},
            'Logging': {'CreateLogs': False},
            'Scanning': {
                'Attempts': 3,
                'Protocols': {
                    'ICMP': True,
                    'TCP': False,
                    'UDP': False,
                    'ARP': False
                },
                'TCPPorts': [80, 443, 22, 21],
                'ICMPTimeout': 2000,
                'GeneralTimeout': 3
            }
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)
        return settings

    def set_theme(self, theme):
        if theme == 'Dark':
            qdarktheme.setup_theme("dark")
        else:
            qdarktheme.setup_theme("light")

    def start_scanning(self):
        self.progress_bar.setValue(0)
        self.devices_table.setRowCount(0)

        ip_start = self.ip_range_start.text()
        ip_end = self.ip_range_end.text()

        self.scanner_thread = ScannerThread(ip_start, ip_end, self.settings)
        self.scanner_thread.result_signal.connect(self.update_results)

        if not self.scanner_thread.isRunning():
            self.scan_count += 1
            self.scanner_thread.start()

    def update_results(self, ip, status, mac, response_time, progress):
        if ip == "progress":
            self.progress_bar.setValue(progress)
        else:
            row_position = self.devices_table.rowCount()
            self.devices_table.insertRow(row_position)
            self.devices_table.setItem(row_position, 0, QTableWidgetItem(ip))
            
            status_item = QTableWidgetItem(status)
            status_color = self.get_status_color(status)
            status_item.setBackground(status_color)
            self.devices_table.setItem(row_position, 1, status_item)
            
            self.devices_table.setItem(row_position, 2, QTableWidgetItem(mac))
            self.devices_table.setItem(row_position, 3, QTableWidgetItem(str(response_time)))

            result_text = f'{ip} - {status} - {mac} - {response_time}'
            self.scan_results.append(result_text)

            if self.settings.get('Logging', {}).get('CreateLogs', False):
                self.write_to_file(result_text)

            current_filter = self.filter_combobox.currentText()
            self.filter_devices(current_filter)

    def start_port_scanning(self):
        ip = self.port_ip_input.text()
        start_port = int(self.port_start_input.text())
        end_port = int(self.port_end_input.text())
        
        self.port_results_table.setRowCount(0)
        self.progress_bar.setValue(0)
        
        self.port_scanner_thread = PortScannerThread(ip, start_port, end_port, self.settings)
        self.port_scanner_thread.scanner.result_signal.connect(self.update_port_results)
        self.port_scanner_thread.scanner.progress_signal.connect(self.update_progress)
        self.port_scanner_thread.finished.connect(self.port_scan_finished)
        
        self.port_scanner_thread.run()

    def update_port_results(self, ip, port, status, service):
        row = self.port_results_table.rowCount()
        self.port_results_table.insertRow(row)
        self.port_results_table.setItem(row, 0, QTableWidgetItem(ip))
        self.port_results_table.setItem(row, 1, QTableWidgetItem(str(port)))
        self.port_results_table.setItem(row, 2, QTableWidgetItem(status))
        self.port_results_table.setItem(row, 3, QTableWidgetItem(service))

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def port_scan_finished(self):
        print("Port scan finished")

    def save_to_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'CSV Files (*.csv);;All Files (*)')
        if file_name:
            with open(file_name, 'w', newline='') as file:
                writer = csv.writer(file)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow(['Timestamp', 'IP', 'Status', 'MAC', 'Response Time'])
                for row in range(self.devices_table.rowCount()):
                    ip = self.devices_table.item(row, 0).text()
                    status = self.devices_table.item(row, 1).text()
                    mac = self.devices_table.item(row, 2).text()
                    response_time = self.devices_table.item(row, 3).text()
                    writer.writerow([timestamp, ip, status, mac, response_time])

    def write_to_file(self, message):
        file_name = f'scan_results_{self.scan_count}.csv'

        with open(file_name, 'a', newline='') as file:
            writer = csv.writer(file)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if os.path.getsize(file_name) == 0:
                writer.writerow(['Timestamp', 'Message'])

            writer.writerow([timestamp, message])

    def show_settings(self):
        settings_window = SettingsWindow(self.settings)
        if settings_window.exec_() == QDialog.Accepted:
            self.settings = settings_window.get_settings()
            self.save_settings()
            self.set_theme(self.settings['Appearance']['Theme'])

    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f, indent=4)

    def apply_filter(self):
        current_filter = self.filter_combobox.currentText()
        self.filter_devices(current_filter)

    def filter_devices(self, filter):
        for row in range(self.devices_table.rowCount()):
            status = self.devices_table.item(row, 1).text()
            if filter == 'All' or filter.lower() in status.lower():
                self.devices_table.setRowHidden(row, False)
            else:
                self.devices_table.setRowHidden(row, True)

    def get_status_color(self, status):
        if status.lower() == "active":
            return QColor(Qt.green)
        elif status.lower() == "inactive":
            return QColor(Qt.red)
        elif status.lower() == "timeout":
            return QColor(255, 255, 0)  # Yellow
        else:
            return QColor(Qt.white)
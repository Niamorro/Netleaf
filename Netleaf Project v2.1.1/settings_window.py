from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QDialog, QComboBox, QGroupBox, QCheckBox, QSpinBox, QDialogButtonBox
)

class SettingsWindow(QDialog):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Appearance
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QVBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(self.settings['Appearance']['Theme'])
        appearance_layout.addWidget(QLabel("Theme:"))
        appearance_layout.addWidget(self.theme_combo)
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)

        # Logging
        logging_group = QGroupBox("Logging")
        logging_layout = QVBoxLayout()
        self.create_logs_check = QCheckBox("Create Logs")
        self.create_logs_check.setChecked(self.settings['Logging']['CreateLogs'])
        logging_layout.addWidget(self.create_logs_check)
        logging_group.setLayout(logging_layout)
        layout.addWidget(logging_group)

        # Scanning
        scanning_group = QGroupBox("Scanning")
        scanning_layout = QVBoxLayout()
        
        # Attempts
        attempts_layout = QHBoxLayout()
        attempts_layout.addWidget(QLabel("Number of attempts:"))
        self.attempts_spinbox = QSpinBox()
        self.attempts_spinbox.setRange(1, 10)
        self.attempts_spinbox.setValue(self.settings['Scanning']['Attempts'])
        attempts_layout.addWidget(self.attempts_spinbox)
        scanning_layout.addLayout(attempts_layout)

        # Protocols
        protocols_group = QGroupBox("Protocols")
        protocols_layout = QVBoxLayout()
        self.protocol_checkboxes = {}
        for protocol in self.settings['Scanning']['Protocols']:
            checkbox = QCheckBox(protocol)
            checkbox.setChecked(self.settings['Scanning']['Protocols'][protocol])
            self.protocol_checkboxes[protocol] = checkbox
            protocols_layout.addWidget(checkbox)
        protocols_group.setLayout(protocols_layout)
        scanning_layout.addWidget(protocols_group)

        # TCP Ports
        tcp_ports_layout = QHBoxLayout()
        tcp_ports_layout.addWidget(QLabel("TCP Ports (comma-separated):"))
        self.tcp_ports_edit = QLineEdit(','.join(map(str, self.settings['Scanning']['TCPPorts'])))
        tcp_ports_layout.addWidget(self.tcp_ports_edit)
        scanning_layout.addLayout(tcp_ports_layout)

        # ICMP Timeout
        icmp_timeout_layout = QHBoxLayout()
        icmp_timeout_layout.addWidget(QLabel("ICMP Timeout (ms):"))
        self.icmp_timeout_spinbox = QSpinBox()
        self.icmp_timeout_spinbox.setRange(100, 10000)
        self.icmp_timeout_spinbox.setValue(self.settings['Scanning']['ICMPTimeout'])
        icmp_timeout_layout.addWidget(self.icmp_timeout_spinbox)
        scanning_layout.addLayout(icmp_timeout_layout)

        # General Timeout
        general_timeout_layout = QHBoxLayout()
        general_timeout_layout.addWidget(QLabel("General Timeout (s):"))
        self.general_timeout_spinbox = QSpinBox()
        self.general_timeout_spinbox.setRange(1, 30)
        self.general_timeout_spinbox.setValue(self.settings['Scanning']['GeneralTimeout'])
        general_timeout_layout.addWidget(self.general_timeout_spinbox)
        scanning_layout.addLayout(general_timeout_layout)

        scanning_group.setLayout(scanning_layout)
        layout.addWidget(scanning_group)

        #threads
        threads_layout = QHBoxLayout()
        threads_layout.addWidget(QLabel("Number of threads:"))
        self.threads_spinbox = QSpinBox()
        self.threads_spinbox.setRange(1, 1000)
        self.threads_spinbox.setValue(self.settings.get('Scanning', {}).get('Threads', 100))
        threads_layout.addWidget(self.threads_spinbox)
        scanning_layout.addLayout(threads_layout)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def accept(self):
        self.settings['Appearance']['Theme'] = self.theme_combo.currentText()
        self.settings['Logging']['CreateLogs'] = self.create_logs_check.isChecked()
        self.settings['Scanning']['Attempts'] = self.attempts_spinbox.value()
        for protocol, checkbox in self.protocol_checkboxes.items():
            self.settings['Scanning']['Protocols'][protocol] = checkbox.isChecked()
        self.settings['Scanning']['TCPPorts'] = list(map(int, self.tcp_ports_edit.text().split(',')))
        self.settings['Scanning']['ICMPTimeout'] = self.icmp_timeout_spinbox.value()
        self.settings['Scanning']['GeneralTimeout'] = self.general_timeout_spinbox.value()
        self.settings['Scanning']['Threads'] = self.threads_spinbox.value()
        super().accept()

    def get_settings(self):
        return self.settings
# settings_window.py
from PySide6.QtWidgets import QDialog, QComboBox, QDialogButtonBox, QFormLayout, QVBoxLayout
from PySide6.QtCore import QSize
import os
import configparser

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.settings = configparser.ConfigParser()

        if os.path.exists('settings.cfg'):
            self.settings.read('settings.cfg')
        else:
            self.create_default_settings()

        self.dark_theme_combobox = QComboBox()
        self.dark_theme_combobox.addItems(['Light', 'Dark'])
        current_theme = 'Dark' if self.settings.getboolean('Appearance', 'DarkMode') else 'Light'
        self.dark_theme_combobox.setCurrentText(current_theme)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QFormLayout()
        layout.addRow('Theme:', self.dark_theme_combobox)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)
        self.setWindowTitle('Settings')

        self.setMinimumSize(QSize(300, 200))

    def accept(self):
        theme_index = self.dark_theme_combobox.currentIndex()
        self.settings.set('Appearance', 'DarkMode', str(theme_index == 1))

        with open('settings.cfg', 'w') as configfile:
            self.settings.write(configfile)

        super().accept()

    def create_default_settings(self):
        self.settings['Appearance'] = {'DarkMode': 'False'}

        with open('settings.cfg', 'w') as configfile:
            self.settings.write(configfile)

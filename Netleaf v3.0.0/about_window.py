# about_window.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, 
    QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Netleaf")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        title_container = QHBoxLayout()
        title_container.setAlignment(Qt.AlignCenter)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("app_icon.png")
        scaled_pixmap = logo_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        
        # Title
        title_label = QLabel("Netleaf")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        # Add logo and title to container
        title_container.addWidget(logo_label)
        title_container.addWidget(title_label)
        
        # Add container to main layout
        layout.addLayout(title_container)
        
        # Add some spacing
        layout.addSpacing(20)
        
        # Links
        links_layout = QVBoxLayout()
        
        github_button = QPushButton("GitHub Repository")
        github_button.clicked.connect(lambda: self.open_url("https://github.com/Niamorro/Netleaf"))
        
        website_button = QPushButton("Official Website")
        website_button.clicked.connect(lambda: self.open_url("https://niamorro.github.io/Netleaf/"))
        
        donate_button = QPushButton("Support Development")
        donate_button.clicked.connect(lambda: self.open_url("https://boosty.to/niamorro"))
        
        links_layout.addWidget(github_button)
        links_layout.addWidget(website_button)
        links_layout.addWidget(donate_button)
        
        layout.addLayout(links_layout)
        
        # Developer info
        developer_info = QLabel(
            "Developed by Niamorro\n"
            "Version: 3.0.0"
        )
        developer_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(developer_info)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
    
    def open_url(self, url):
        QDesktopServices.openUrl(QUrl(url))
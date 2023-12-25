# interfaces/sidebar/settings_page.py
from PyQt5.QtWidgets import QWidget, QLabel


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        label = QLabel("This is the Settings Page.", self)

# interfaces/sidebar/profile_page.py
from PyQt5.QtWidgets import QWidget, QLabel

class ProfilePage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        label = QLabel("This is the Profile Page.", self)
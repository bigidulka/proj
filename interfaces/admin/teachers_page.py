# interfaces/admin/teachers_page.py
from PyQt5.QtWidgets import QWidget, QLabel

class TeachersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        label = QLabel('Manage Teachers', self)

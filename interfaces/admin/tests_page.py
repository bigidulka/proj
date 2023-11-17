# interfaces/admin/tests_page.py
from PyQt5.QtWidgets import QWidget, QLabel

class TestsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        label = QLabel('Manage Tests', self)

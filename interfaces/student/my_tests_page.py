# interfaces/student/my_tests_page.py
from PyQt5.QtWidgets import QWidget, QLabel

class MyTestsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        label = QLabel('My Tests', self)

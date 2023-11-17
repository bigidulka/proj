# interfaces/teacher/tests_page.py
from PyQt5.QtWidgets import QWidget, QLabel

class TeacherTestsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        label = QLabel('Manage Tests', self)

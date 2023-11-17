# interfaces/admin/students_page.py
from PyQt5.QtWidgets import QWidget, QLabel

class StudentsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        label = QLabel('Manage Students', self)

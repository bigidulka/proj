# interfaces/teacher/students_page.py
from PyQt5.QtWidgets import QWidget, QLabel

class TeacherStudentsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        label = QLabel('Manage Students', self)

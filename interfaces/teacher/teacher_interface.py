# interfaces/teacher/teacher_interface.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QStackedWidget
from interfaces.sidebar import SidebarMenu
from .students_page import TeacherStudentsPage
from .tests_page import TeacherTestsPage

class TeacherWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window =main_window
        self.initUI()

    def initUI(self):
        upper_buttons = ['Ученики', 'Тесты']
        self.stack = QStackedWidget()
        self.stack.addWidget(TeacherStudentsPage())
        self.stack.addWidget(TeacherTestsPage())

        self.sidebar = SidebarMenu(upper_buttons, self.stack, self.main_window)

        layout = QHBoxLayout()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)

        self.setLayout(layout)
        self.connectButtons()

    def connectButtons(self):
        self.sidebar.connectStack()

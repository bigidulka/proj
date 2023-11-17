# interfaces/student/student_interface.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QStackedWidget
from interfaces.sidebar import SidebarMenu
from .my_tests_page import MyTestsPage

class StudentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        upper_buttons = ['Мои тесты']
        self.stack = QStackedWidget()
        self.stack.addWidget(MyTestsPage())

        self.sidebar = SidebarMenu(upper_buttons, self.stack)

        layout = QHBoxLayout()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)

        self.setLayout(layout)
        self.connectButtons()

    def connectButtons(self):
        self.sidebar.connectStack()
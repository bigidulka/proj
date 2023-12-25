# interfaces\student\student_interface.py

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QStackedWidget
from interfaces.sidebar import SidebarMenu
from .my_tests_page import MyTestsPage
from ..reports_page import ReportsWindow


class StudentWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        upper_buttons = ["Мои тесты", "Мои результаты"]
        self.stack = QStackedWidget()

        self.tests_page = MyTestsPage(self, self.main_window)
        self.stack.addWidget(self.tests_page)
        self.stack.addWidget(ReportsWindow(self.main_window))

        self.sidebar = SidebarMenu(upper_buttons, self.stack, self.main_window)

        layout = QHBoxLayout()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)

        self.setLayout(layout)
        self.connectButtons()

    def connectButtons(self):
        self.sidebar.connectStack()

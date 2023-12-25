# interfaces\teacher\teacher_interface.py

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QStackedWidget
from interfaces.sidebar import SidebarMenu
from ..students_page import StudentsPage
from ..tests_page import TestsPage
from ..reports_page import ReportsWindow


class TeacherWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        upper_buttons = ['Ученики', 'Тесты', 'Отчеты']
        self.stack = QStackedWidget()

        self.stack.addWidget(StudentsPage(self.main_window))
        self.test_page = TestsPage(self)
        self.stack.addWidget(self.test_page)
        self.stack.addWidget(ReportsWindow(self.main_window))

        self.sidebar = SidebarMenu(upper_buttons, self.stack, self.main_window)

        layout = QHBoxLayout()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)

        self.setLayout(layout)
        self.connectButtons()

    def connectButtons(self):
        self.sidebar.connectStack()

# interfaces/admin/admin_interface.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QStackedWidget
from interfaces.sidebar import SidebarMenu
from .users_page import UsersPage
from .students_page import StudentsPage
from .teachers_page import TeachersPage
from .tests_page import TestsPage

class AdminWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        upper_buttons = ['Пользователи', 'Ученики', 'Учителя', 'Тесты']
        self.stack = QStackedWidget()

        self.stack.addWidget(UsersPage())
        self.stack.addWidget(StudentsPage())
        self.stack.addWidget(TeachersPage())
        self.stack.addWidget(TestsPage(self))

        self.sidebar = SidebarMenu(upper_buttons, self.stack, self.main_window)
        
        layout = QHBoxLayout()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)

        self.setLayout(layout)
        self.connectButtons()

    def connectButtons(self):
        self.sidebar.connectStack()
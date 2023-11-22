# interfaces/sidebar.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QStackedWidget
from ..utility import load_stylesheet
from .profile_page import ProfilePage
from .settings_page import SettingsPage

class SidebarMenu(QWidget):
    def __init__(self, upper_buttons, stack, main_window, parent=None):
        super().__init__(parent)
        self.stack = stack
        self.main_window = main_window
        self.initUI(upper_buttons)

    def initUI(self, upper_buttons):
        layout = QVBoxLayout()
        self.buttons = []

        for button_name in upper_buttons:
            button = QPushButton(button_name)
            layout.addWidget(button)
            self.buttons.append(button)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        self.profile_button = QPushButton('Мой профиль')
        self.settings_button = QPushButton('Настройки')
        self.logout_button = QPushButton('Выйти из аккаунта')

        layout.addWidget(self.profile_button)
        layout.addWidget(self.settings_button)
        layout.addWidget(self.logout_button)
        
        self.logout_button.clicked.connect(self.logout)
        
        self.setLayout(layout)

        self.profile_page = ProfilePage()
        self.settings_page = SettingsPage()
        self.stack.addWidget(self.profile_page)
        self.stack.addWidget(self.settings_page)

        style = load_stylesheet("resources/styles/main_style.css")
        self.setStyleSheet(style)

    def connectStack(self):
        for i, button in enumerate(self.buttons):
            button.clicked.connect(lambda _, b=i: self.stack.setCurrentIndex(b))

        # Connect the Profile and Settings buttons
        self.profile_button.clicked.connect(lambda: self.stack.setCurrentIndex(len(self.buttons)))
        self.settings_button.clicked.connect(lambda: self.stack.setCurrentIndex(len(self.buttons) + 1))

        
    def logout(self):
        # Очищаем поля ввода (если нужно)
        self.main_window.login_window.username_input.clear()
        self.main_window.login_window.password_input.clear()
        
        self.main_window.login_window.reg_username_input.clear()
        self.main_window.login_window.reg_password_input.clear()
        self.main_window.login_window.reg_name_input.clear()
        self.main_window.login_window.reg_password_retry_input.clear()

        # Переключаем на экран входа
        self.main_window.central_widget.setCurrentWidget(self.main_window.login_window)
# interfaces/login.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QFormLayout, QCheckBox, QFrame, QMessageBox)
from PyQt5.QtCore import Qt
from database import authenticate_user

class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        form_layout = QFormLayout()

        # Removed the duplicate line for 'Ваш логин'
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow('Логин', self.username_input)
        form_layout.addRow('Ваш пароль', self.password_input)

        self.login_button = QPushButton('Войти')
        self.login_button.clicked.connect(self.login)

        self.remember_me_checkbox = QCheckBox('У меня нет аккаунта')

        # Aligning the widgets
        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.remember_me_checkbox)
        layout.addWidget(self.login_button)

        frame = QFrame()
        frame.setLayout(layout)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(frame, alignment=Qt.AlignCenter)  # Corrected line

        self.setLayout(main_layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        role = authenticate_user(username, password)
        if role:
            if role[0] == 'ADMIN':
                self.main_window.central_widget.setCurrentWidget(self.main_window.admin_window)
            elif role[0] == 'TEACHER':
                self.main_window.central_widget.setCurrentWidget(self.main_window.teacher_window)
            elif role[0] == 'STUDENT':
                self.main_window.central_widget.setCurrentWidget(self.main_window.student_window)
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')
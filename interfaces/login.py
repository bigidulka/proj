# interfaces/login.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QFormLayout, QCheckBox, QFrame, QMessageBox, QStackedWidget, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from database import authenticate_user, add_user, check_existing_user

class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        # Создаем стек для переключения между формами
        self.stack = QStackedWidget()

        # Создаем формы для входа и регистрации
        self.login_form_widget = self.createLoginForm()
        self.register_form_widget = self.createRegisterForm()

        # Добавляем формы в стек
        self.stack.addWidget(self.login_form_widget)
        self.stack.addWidget(self.register_form_widget)

        # Создаем кнопки для переключения между формами
        self.login_button_top = QPushButton('Вход')
        self.register_button_top = QPushButton('Регистрация')
        self.login_button_top.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.register_button_top.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        # Создаем верхний лейаут для кнопок
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.login_button_top)
        top_layout.addWidget(self.register_button_top)

        # Создаем рамку вокруг стека для стилизации
        frame = QFrame()
        frame_layout = QVBoxLayout()
        frame_layout.addLayout(top_layout)  # Добавляем кнопки в верхнюю часть рамки
        frame_layout.addWidget(self.stack)
        frame.setLayout(frame_layout)

        # Основной макет с пространствами для центрирования формы
        main_layout = QVBoxLayout()
        spacer_top = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        spacer_bottom = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer_top)
        main_layout.addWidget(frame, alignment=Qt.AlignCenter)
        main_layout.addItem(spacer_bottom)

        self.setLayout(main_layout)

    def createLoginForm(self):
        form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow('Логин', self.username_input)
        form_layout.addRow('Пароль', self.password_input)

        login_button = QPushButton('Войти')
        login_button.clicked.connect(self.login)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(login_button)  # Только кнопка Войти

        frame = QFrame()
        frame.setLayout(layout)

        return frame
    
    def createRegisterForm(self):
        form_layout = QFormLayout()
        self.reg_name_input = QLineEdit()
        self.reg_username_input = QLineEdit()
        self.reg_password_input = QLineEdit()
        self.reg_password_input.setEchoMode(QLineEdit.Password)
        self.reg_password_retry_input = QLineEdit()
        self.reg_password_retry_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow('ФИО', self.reg_name_input)
        form_layout.addRow('Логин', self.reg_username_input)
        form_layout.addRow('Пароль', self.reg_password_input)
        form_layout.addRow('Повторите пароль', self.reg_password_retry_input)

        register_button = QPushButton('Зарегистрироваться')
        register_button.clicked.connect(self.register)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(register_button)  # Только кнопка Зарегистрироваться

        frame = QFrame()
        frame.setLayout(layout)

        return frame

    def switchToRegister(self):
        self.stack.setCurrentIndex(1)

    def switchToLogin(self):
        self.stack.setCurrentIndex(0)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        user_info = authenticate_user(username, password)
        if user_info:
            user_id, role = user_info
            self.main_window.logged_in_user_id = user_id
            self.main_window.user_role = role
            self.main_window.user_id = user_id

            if role == 'ADMIN':
                self.main_window.initAdminWindow()
                self.main_window.central_widget.setCurrentWidget(self.main_window.admin_window)
            elif role == 'TEACHER':
                self.main_window.initTeacherWindow()
                self.main_window.central_widget.setCurrentWidget(self.main_window.teacher_window)
            elif role == 'STUDENT':
                self.main_window.initStudentWindow()
                self.main_window.central_widget.setCurrentWidget(self.main_window.student_window)
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')


    def register(self):
        name = self.reg_name_input.text().strip()
        username = self.reg_username_input.text().strip()
        password = self.reg_password_input.text()
        retry_password = self.reg_password_retry_input.text()

        if not all([name, username, password, retry_password]):
            QMessageBox.warning(self, 'Ошибка', 'Все поля должны быть заполнены')
            return

        if password != retry_password:
            QMessageBox.warning(self, 'Ошибка', 'Пароли не совпадают')
            return

        # Проверка на существование пользователя
        if check_existing_user(username):
            QMessageBox.warning(self, 'Ошибка', 'Пользователь с таким логином уже существует')
            return

        # Добавляем пользователя в базу данных
        add_user(name, username, password, 'STUDENT')
        QMessageBox.information(self, 'Успех', 'Регистрация прошла успешно')
        self.switchToLogin()
        
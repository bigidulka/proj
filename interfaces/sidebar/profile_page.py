# interfaces/sidebar/profile_page.py
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
import database

class ProfilePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        # Create the main layout
        main_layout = QVBoxLayout(self)

        # Create the form layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(0)  # Set the spacing between widgets to 0

        # Name
        self.name_label = QLabel("ФИО:", self)
        self.name_edit = QLineEdit(self)
        form_layout.addWidget(self.name_label)
        form_layout.addWidget(self.name_edit)

        # Username
        self.username_label = QLabel("Логин:", self)
        self.username_edit = QLineEdit(self)
        form_layout.addWidget(self.username_label)
        form_layout.addWidget(self.username_edit)

        # Password
        self.password_label = QLabel("Пароль:", self)
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.Password)
        # Show Password Button
        self.show_password_button = QPushButton(QIcon("resources/icons/eye-icon.png"), "", self)
        self.show_password_button.clicked.connect(self.toggle_password_visibility)
        # Password Layout
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_edit)
        password_layout.addWidget(self.show_password_button)
        # Adding Password Widgets
        form_layout.addWidget(self.password_label)
        form_layout.addLayout(password_layout)

        # Save Button
        self.save_button = QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.update_user_info)
        form_layout.addWidget(self.save_button)

        # Add form layout to main layout
        main_layout.addLayout(form_layout)

        # Add spacer to main layout to push everything to the top
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer)

        self.load_user_info()

    def load_user_info(self):
        # Load the current user info from the database
        user_info = database.get_user_info(self.main_window.user_id)
        if user_info:
            self.name_edit.setText(user_info['name'])
            self.username_edit.setText(user_info['username'])
            self.password_edit.setText(user_info['password'])  # Load password

    def update_user_info(self):
        # Update user info in the database
        name = self.name_edit.text()
        username = self.username_edit.text()
        password = self.password_edit.text()

        if not name or not username or not password:
            QMessageBox.warning(self, "Предупреждение", "Все поля обязательны для заполнения.")
            return

        database.update_user_info(self.main_window.user_id, name, username, password)
        QMessageBox.information(self, "Успех", "Информация о пользователе успешно обновленаy.")

    def toggle_password_visibility(self):
        if self.password_edit.echoMode() == QLineEdit.Password:
            self.password_edit.setEchoMode(QLineEdit.Normal)
            QTimer.singleShot(3000, lambda: self.password_edit.setEchoMode(QLineEdit.Password))
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)
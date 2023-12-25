# interfaces\admin\users_page.py

from PyQt5.QtWidgets import (QWidget, QPushButton, QTableView, QVBoxLayout, QMessageBox, QDialog,
                             QLineEdit, QHBoxLayout, QFormLayout, QComboBox, QStyledItemDelegate, QTextEdit, QHeaderView)
from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
import database


class CustomStandardItemModel(QStandardItemModel):
    def __init__(self, rows, columns):
        super().__init__(rows, columns)

    def flags(self, index):
        flags = super().flags(index)
        if index.column() not in [1, 4]:
            flags &= ~Qt.ItemIsEditable
        return flags


class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить нового пользователя")
        self.layout = QFormLayout(self)

        self.name = QLineEdit(self)
        self.username = QLineEdit(self)
        self.password = QLineEdit(self)

        self.role = QComboBox(self)
        self.role.addItems(["ADMIN", "TEACHER", "STUDENT"])

        self.layout.addRow("ФИО:", self.name)
        self.layout.addRow("Логин:", self.username)
        self.layout.addRow("Пароль:", self.password)
        self.layout.addRow("Роль:", self.role)

        self.buttons = QHBoxLayout()
        self.addButton = QPushButton("Добавить", self)
        self.addButton.clicked.connect(self.accept)
        self.cancelButton = QPushButton("Отмена", self)
        self.cancelButton.clicked.connect(self.reject)
        self.buttons.addWidget(self.addButton)
        self.buttons.addWidget(self.cancelButton)

        self.layout.addRow(self.buttons)

    def get_inputs(self):
        return {
            "name": self.name.text(),
            "username": self.username.text(),
            "password": self.password.text(),
            "role": self.role.currentText(),
        }


class CustomDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.button_icon = QIcon("resources/icons/eye-icon.png")
        self.show_password = {}
        self.timer = QTimer()
        self.timer.timeout.connect(self.hide_password)
        self.roles = ["ADMIN", "STUDENT", "TEACHER"]

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        if index.column() == 3:
            password = index.data(Qt.DisplayRole)
            show = self.show_password.get(index, False)
            painter.eraseRect(option.rect)
            if password is not None:
                if show:
                    painter.drawText(option.rect, Qt.AlignVCenter, password)
                else:
                    masked_password = "*" * len(password)
                    painter.drawText(
                        option.rect, Qt.AlignVCenter, masked_password)
            button_rect = option.rect.adjusted(
                option.rect.width() - 20, 0, 0, 0)
            painter.drawPixmap(button_rect, self.button_icon.pixmap(20, 20))

    def editorEvent(self, event, model, option, index):
        if index.column() == 3 and event.type() == QEvent.MouseButtonRelease:
            button_rect = option.rect.adjusted(
                option.rect.width() - 20, 0, 0, 0)
            if button_rect.contains(event.pos()):
                self.show_password[index] = not self.show_password.get(
                    index, False)
                model.dataChanged.emit(index, index)
                if self.show_password[index]:
                    self.timer.start(3000)
                else:
                    self.timer.stop()
                return True
        return super().editorEvent(event, model, option, index)

    def hide_password(self):
        for index in self.show_password.keys():
            self.show_password[index] = False
            index.model().dataChanged.emit(index, index)

    def createEditor(self, parent, option, index):
        if index.column() == 1:
            editor = QTextEdit(parent)
            return editor
        elif index.column() == 4:
            editor = QComboBox(parent)
            editor.addItems(self.roles)
            return editor
        else:
            return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if index.column() == 1:
            editor.setPlainText(index.data())
        elif index.column() == 4:
            editor.setCurrentText(index.data())
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if index.column() == 1:
            new_name = editor.toPlainText()
            old_name = index.data()
            if new_name != old_name:
                model.setData(index, new_name)
                username_index = model.index(index.row(), 2)
                username = model.data(username_index)
                database.update_name(username, new_name)
        elif index.column() == 4:
            new_role = editor.currentText()
            old_role = index.data()
            if new_role != old_role:
                model.setData(index, new_role)
                username_index = model.index(index.row(), 2)
                username = model.data(username_index)
                database.update_role(username, new_role)

        model.dataChanged.emit(index, index)


class UsersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        self.tableView = QTableView(self)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.tableView)

        self.header_map = {
            "ID": "id",
            "ФИО (Edit)": "name",
            "Логин": "username",
            "Пароль": "password",
            "Роль (Edit)": "role",
        }
        self.users = database.get_all_users_as_dicts()
        self.tableModel = CustomStandardItemModel(
            len(self.users), len(self.header_map))
        self.tableModel.setHorizontalHeaderLabels(self.header_map.keys())
        self.tableView.setModel(self.tableModel)
        self.tableView.horizontalHeader().setStretchLastSection(True)

        self.custom_delegate = CustomDelegate()
        self.tableView.setItemDelegate(self.custom_delegate)

        for row, user in enumerate(self.users):
            for col, field in enumerate(self.header_map.values()):
                item = QStandardItem(str(user.get(field, "")))
                if field in ["name", "role"]:
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.tableModel.setItem(row, col, item)

        self.addButton = QPushButton("Добавить пользователя", self)
        self.addButton.clicked.connect(self.add_user)
        self.layout.addWidget(self.addButton)

        self.deleteButton = QPushButton("Удалить пользователя", self)
        self.deleteButton.clicked.connect(self.delete_user)
        self.layout.addWidget(self.deleteButton)

        self.refreshButton = QPushButton("Обновить данные", self)
        self.refreshButton.clicked.connect(self.refresh_table)
        self.layout.addWidget(self.refreshButton)

    def add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            user_data = dialog.get_inputs()
            if user_data["username"] in [user["username"] for user in self.users]:
                QMessageBox.warning(
                    self,
                    "Имя пользователя существует",
                    "Пользователь с таким именем пользователя уже существует.",
                )
            else:
                database.add_user(**user_data)
                self.refresh_table()

    def delete_user(self):
        selected_indexes = self.tableView.selectionModel().selectedRows()
        if selected_indexes:
            row = selected_indexes[0].row()
            username_index = self.tableModel.index(row, 2)
            username = self.tableModel.data(username_index, Qt.DisplayRole)

            reply = QMessageBox.question(
                self,
                "Подтвердить удаление",
                f'Вы хотите удалить пользователя с именем пользователя "{username}"?',
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                database.delete_user(username)
                self.refresh_table()
        else:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Пожалуйста, выберите пользователя для удаления.",
            )

    def refresh_table(self):
        self.users = database.get_all_users_as_dicts()
        self.tableModel.setRowCount(len(self.users))
        for row, user in enumerate(self.users):
            for col, field in enumerate(self.header_map.values()):
                item = QStandardItem(str(user.get(field, "")))
                self.tableModel.setItem(row, col, item)

# interfaces/admin/users_page.py
import os
import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QTableView, QVBoxLayout,
    QMessageBox, QDialog, QLineEdit, QHBoxLayout, QFormLayout,
    QComboBox, QAbstractItemView, QItemDelegate, QStyle, QStyleOptionButton,
    QApplication, QHeaderView, QFrame, QStyledItemDelegate, QToolButton, QTextEdit
)
from PyQt5.QtCore import Qt, QModelIndex, pyqtSignal, QAbstractTableModel, QEvent, QSize, QSortFilterProxyModel, QRect, QTimer
from PyQt5.QtGui import QIcon, QFont
from ..table_models import TableModel
import database

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add New User')
        self.layout = QFormLayout(self)

        # User input fields
        self.name = QLineEdit(self)
        self.username = QLineEdit(self)
        self.password = QLineEdit(self)

        self.role = QComboBox(self)
        self.role.addItems(["ADMIN", "TEACHER", "STUDENT"])

        self.layout.addRow('Name:', self.name)
        self.layout.addRow('Username:', self.username)
        self.layout.addRow('Password:', self.password)
        self.layout.addRow('Role:', self.role)

        # Buttons
        self.buttons = QHBoxLayout()
        self.addButton = QPushButton('Add', self)
        self.addButton.clicked.connect(self.accept)
        self.cancelButton = QPushButton('Cancel', self)
        self.cancelButton.clicked.connect(self.reject)
        self.buttons.addWidget(self.addButton)
        self.buttons.addWidget(self.cancelButton)

        self.layout.addRow(self.buttons)

    def get_inputs(self):
        return self.name.text(), self.username.text(), self.password.text(), self.role.currentText()
        
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
            if show:
                painter.drawText(option.rect, Qt.AlignVCenter, password)
            else:
                masked_password = '*' * len(password)
                painter.drawText(option.rect, Qt.AlignVCenter, masked_password)
            button_rect = option.rect.adjusted(option.rect.width() - 20, 0, 0, 0)
            painter.drawPixmap(button_rect, self.button_icon.pixmap(20, 20))

    def editorEvent(self, event, model, option, index):
        if index.column() == 3 and event.type() == QEvent.MouseButtonRelease:
            button_rect = option.rect.adjusted(option.rect.width() - 20, 0, 0, 0)
            if button_rect.contains(event.pos()):
                self.show_password[index] = not self.show_password.get(index, False)
                model.dataChanged.emit(index, index)
                if self.show_password[index]:
                    self.timer.start(3000)  # Start timer for 3 seconds
                else:
                    self.timer.stop()  # Stop the timer
                return True
        return super().editorEvent(event, model, option, index)

    def hide_password(self):
        for index in self.show_password.keys():
            self.show_password[index] = False
            index.model().dataChanged.emit(index, index)

    def createEditor(self, parent, option, index):
        if index.column() == 1:  # Column "Name"
            editor = QTextEdit(parent)
            return editor
        elif index.column() == 4:  # Column "Role"
            editor = QComboBox(parent)
            editor.addItems(self.roles)
            return editor
        else:
            return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if index.column() == 1:  # Column "Name"
            editor.setPlainText(index.data())
        elif index.column() == 4:  # Column "Role"
            editor.setCurrentText(index.data())
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if index.column() == 1:  # Column "Name"
            new_name = editor.toPlainText()
            old_name = index.data()
            if new_name != old_name:
                model.setData(index, new_name)
                username_index = model.index(index.row(), 2)
                username = model.data(username_index)
                database.update_name(username, new_name)
        elif index.column() == 4:  # Column "Role(Edit)"
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

        columns = ["ID", "Name(Edit)", "Username", "Password", "Role(Edit)"]
        editable_columns = [1, 4]
        self.users = database.get_all_users()

        self.tableModel = TableModel(columns, self.users, sortable_columns=[0, 4], editable_columns=editable_columns)
        self.tableView = self.tableModel.create_table_view()

        custom_delegate = CustomDelegate()
        self.tableView.setItemDelegate(custom_delegate)

        self.layout.addWidget(self.tableView)

        self.addButton = QPushButton('Add User', self)
        self.addButton.clicked.connect(self.add_user)
        self.layout.addWidget(self.addButton)

        self.deleteButton = QPushButton('Delete User', self)
        self.deleteButton.clicked.connect(self.delete_user)
        self.layout.addWidget(self.deleteButton)

        self.refreshButton = QPushButton('Refresh', self)
        self.refreshButton.clicked.connect(self.refresh_table)
        self.layout.addWidget(self.refreshButton)

    def add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, username, password, role = dialog.get_inputs()

            existing_usernames = [user[2] for user in self.users]  # Извлеките существующие имена пользователей

            if username in existing_usernames:
                QMessageBox.warning(self, "Username Exists", "A user with this username already exists.")
            else:
                # Вместо добавления пользователя в базу данных, добавьте его в модель
                self.tableModel.add_data((len(self.users) + 1, name, username, password, role))

    def delete_user(self):
        selected = self.tableView.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            username = self.tableModel.data(self.tableModel.index(row, 2), Qt.DisplayRole)  # Получите имя пользователя из таблицы

            reply = QMessageBox.question(self, 'Confirm Deletion', f'Do you want to delete the user with username "{username}"?', QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                # Вместо удаления пользователя из базы данных, удалите его из модели
                self.tableModel.remove_data(row)
        else:
            QMessageBox.warning(self, "Warning", "Please select a user to delete.")


    def refresh_table(self):
        self.users = database.get_all_users()
        self.tableModel.load_data(self.users)
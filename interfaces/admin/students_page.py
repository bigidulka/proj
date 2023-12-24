# interfaces/admin/students_page.py
from PyQt5.QtWidgets import QWidget, QLabel

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QTableView, 
    QHBoxLayout, QDialog, QLineEdit, QStyledItemDelegate, QPushButton, QApplication, QStyle, QInputDialog, QMessageBox, QStyleOptionButton, QHeaderView, QCheckBox, QComboBox, QStyleOptionComboBox
)
from PyQt5.QtCore import Qt, QModelIndex, QRect, pyqtSignal, QAbstractTableModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt, QTimer, QEvent


import database

class GroupManagementDialog(QDialog):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        # Create a QStandardItemModel for the table
        self.groupsModel = QStandardItemModel()
        self.groupsModel.setHorizontalHeaderLabels(["Имя группы"])
        
        # Table for groups
        self.groupsTable = QTableView(self)
        self.groupsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.groupsTable.setModel(self.groupsModel)
        self.layout.addWidget(self.groupsTable)

        # Button for adding a new group
        self.addGroupButton = QPushButton('Добавить группу', self)
        self.addGroupButton.clicked.connect(self.add_group)
        self.layout.addWidget(self.addGroupButton)

        # Button for deleting a group
        self.deleteGroupButton = QPushButton('Удалить группу', self)
        self.deleteGroupButton.clicked.connect(self.delete_group)
        self.layout.addWidget(self.deleteGroupButton)

        # Button for assigning a test to a group
        self.assignTestButton = QPushButton('Назначить тест на группу', self)
        self.assignTestButton.clicked.connect(self.assign_test_to_group)
        self.layout.addWidget(self.assignTestButton)

        # Button for refreshing data
        self.refreshButton = QPushButton('Обновить данные', self)
        self.refreshButton.clicked.connect(self.load_groups)
        self.layout.addWidget(self.refreshButton)

        self.setWindowTitle("Управление группами")
        self.setGeometry(300, 300, 400, 300)  # Adjust size and position as needed

        # Load group data when initializing the dialog
        self.load_groups()

    def add_group(self):
        text, ok = QInputDialog.getText(self, 'Добавление группы', 'Введите название группы:')
        if ok and text:
            # Check if the group name already exists
            existing_groups = [item.text() for item in self.groupsModel.findItems(text)]
            if existing_groups:
                QMessageBox.warning(self, 'Группа уже существует', 'Группа уже существует.')
            else:
                # Assuming you have a method in your database module to add a group
                database.add_group(text)
                self.load_groups()  # Refresh the data after adding

    def delete_group(self):
        # You may want to select a group from the table to delete
        selected = self.groupsTable.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            group_item = self.groupsModel.item(row)
            group_name = group_item.text()
            # Assuming you have a method in your database module to delete a group
            database.delete_group(group_name)
            self.load_groups()  # Refresh the data after deletion

    def assign_test_to_group(self):
        selected = self.groupsTable.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, 'Группа не выбрана', 'Пожалуйста, выберите группу, чтобы назначить заданиеst.')
            return

        row = selected[0].row()
        group_item = self.groupsModel.item(row)
        group_name = group_item.text()
        group_id = database.get_group_id_by_name(group_name)  # Make sure this function exists in your database module
        if group_id is not None:
            dialog = AssignTestToGroupDialog(group_id, self.main_window.user_id, self)
            dialog.exec_()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Невозможно найти выбранную группу в базе данных.')

    def load_groups(self):
        # Fetch updated groups data from the database
        groups = database.get_all_groups()

        # Clear the existing data in the model
        self.groupsModel.clear()
        self.groupsModel.setHorizontalHeaderLabels(["Имя группы"])

        # Add the updated data to the model
        for group in groups:
            group_name = group['name']
            item = QStandardItem(group_name)
            self.groupsModel.appendRow(item)

class StudentsTableModel(QAbstractTableModel):
    def __init__(self, students_data):
        super().__init__()
        self.students_data = students_data  # Переименовали атрибут
        self.header = ["ФИО", "Группа", "Назначенные тесты"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.students_data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.header)

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole or role == Qt.EditRole:
            row = index.row()
            col = index.column()
            student = self.students_data[row]
            if col == 0:
                return student['name']
            elif col == 1:
                return student['group']  # Убедитесь, что здесь отображается название группы
            elif col == 2:
                return student['tests']
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.header[section]
        return None
    

    def setData(self, index, value, role):
        if role == Qt.EditRole and index.column() == 1:  # Group column
            dialog = GroupSelectionDialog()
            if dialog.exec_():
                selected_group_ids = dialog.selected_groups()
                student_id = self.students_data[index.row()]['id']
                database.set_student_groups(student_id, selected_group_ids)
                self.students_data[index.row()]['group'] = ','.join([str(group_id) for group_id in selected_group_ids])
                self.dataChanged.emit(index, index)
                return True
        return False
    
    def get_group_dropdown_data(self):
        groups = database.get_all_groups()
        return {group['id']: group['name'] for group in groups}
    
    def flags(self, index):
        if index.column() == 1:  # Для столбца "Group"
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return super().flags(index)

class GroupSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Выбор группы")  # Устанавливаем заголовок окна
        self.layout = QVBoxLayout(self)
        self.groupComboBox = QComboBox(self)
        for group in database.get_all_groups():
            self.groupComboBox.addItem(group['name'], group['id'])
        self.layout.addWidget(self.groupComboBox)
        self.assignButton = QPushButton('Сохранить', self)
        self.assignButton.clicked.connect(self.accept)
        self.layout.addWidget(self.assignButton)

    def selected_group_id(self):
        return self.groupComboBox.currentData()


class StudentsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        # Fetch students data from the database
        students_data = database.get_all_students()

        # Create a table model with the students data
        self.studentsModel = StudentsTableModel(students_data)

        # Create a table view and set the model
        self.studentsTable = QTableView()
        self.studentsTable.setModel(self.studentsModel)
        self.studentsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.studentsTable.setSelectionBehavior(QTableView.SelectRows)
        self.studentsTable.setSelectionMode(QTableView.SingleSelection)
        
        self.groupDelegate = GroupColumnDelegate(self)
        self.studentsTable.setItemDelegateForColumn(1, self.groupDelegate)  # Привязка делегата к столбцу "Group"
        
        # Связывание сигналов делегата с методами обработки
        self.groupDelegate.assign_group.connect(self.assign_group)
        self.groupDelegate.remove_group.connect(self.remove_group)

        self.layout.addWidget(self.studentsTable)

        self.manageGroupsButton = QPushButton('Управление группами', self)
        self.manageGroupsButton.clicked.connect(self.open_group_management)
        self.layout.addWidget(self.manageGroupsButton)

        self.assignTestStudentButton = QPushButton('Назначить тест студенту', self)
        self.assignTestStudentButton.clicked.connect(self.assign_test_to_student)
        self.layout.addWidget(self.assignTestStudentButton)

        self.refreshButton = QPushButton('Обновить данные', self)
        self.refreshButton.clicked.connect(self.refresh_students)
        self.layout.addWidget(self.refreshButton)

    def open_group_management(self):
        dialog = GroupManagementDialog(self.main_window)
        dialog.exec_()

    def assign_test_to_student(self):
        selected = self.studentsTable.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            student_id = self.studentsModel.students_data[row]['id']
            # Open dialog to assign test
            AssignTestDialog(student_id, self.main_window.user_id, self).exec_()
    
    def refresh_students(self):
        students_data = database.get_all_students()  # Получение обновленных данных студентов
        self.studentsModel.students_data = students_data  # Обновление данных в модели
        self.studentsModel.layoutChanged.emit()  # Сообщение модели о том, что ее содержимое изменилось
        self.studentsTable.viewport().update()  # Обновление отображения таблицы
        
    def assign_group(self, row):
        dialog = GroupSelectionDialog(self)
        if dialog.exec_():
            group_id = dialog.selected_group_id()
            student_id = self.studentsModel.students_data[row]['id']
            database.set_student_group(student_id, group_id)
            self.refresh_students()  # Обновление данных студентов и таблицы

    def remove_group(self, row):
        student_id = self.studentsModel.students_data[row]['id']
        database.reset_student_group(student_id)
        self.refresh_students()  # Обновление данных студентов и таблицы

class GroupColumnDelegate(QStyledItemDelegate):
    assign_group = pyqtSignal(int)  # Сигнал для назначения группы
    remove_group = pyqtSignal(int)  # Сигнал для удаления группы

    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        # Получение и отображение назначенной группы
        group_name = index.model().data(index, Qt.DisplayRole)
        painter.drawText(option.rect.adjusted(5, 0, -30, 0), Qt.AlignVCenter, group_name)  # Отображение названия группы с отступом

        # Загрузка иконок
        assign_icon = QIcon("resources/icons/assign.png")
        remove_icon = QIcon("resources/icons/close.png")

        # Расчёт положения иконок
        icon_size = 16
        right_edge = option.rect.right()
        remove_icon_rect = QRect(right_edge - icon_size, option.rect.top(), icon_size, icon_size)
        assign_icon_rect = QRect(right_edge - icon_size * 2 - 5, option.rect.top(), icon_size, icon_size)  # Добавлен отступ между иконками

        # Отрисовка иконок
        painter.drawPixmap(assign_icon_rect, assign_icon.pixmap(icon_size, icon_size))
        painter.drawPixmap(remove_icon_rect, remove_icon.pixmap(icon_size, icon_size))

    def editorEvent(self, event, model, option, index):
        if not index.isValid():
            return False

        icon_size = 16
        right_edge = option.rect.right()

        # Область нажатия для кнопки "Assign"
        assign_button_rect = QRect(right_edge - icon_size * 2 - 5, option.rect.top(), icon_size, option.rect.height())
        # Область нажатия для кнопки "Remove"
        remove_button_rect = QRect(right_edge - icon_size, option.rect.top(), icon_size, option.rect.height())

        if assign_button_rect.contains(event.pos()):
            self.assign_group.emit(index.row())  # Отправка сигнала с индексом строки
            return True
        elif remove_button_rect.contains(event.pos()):
            self.remove_group.emit(index.row())  # Отправка сигнала с индексом строки
            return True

        return False
        
class AssignTestDialog(QDialog):
    def __init__(self, student_id, user_id, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.user_id = user_id  # Добавляем user_id
        self.assigned_tests = set(database.get_tests_for_student(student_id)) 
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.tests = database.get_all_tests_as_dict()

        for test_id, test_name in self.tests:
            checkBox = QCheckBox(test_name, self)
            checkBox.test_id = test_id
            checkBox.setChecked(test_id in self.assigned_tests)  # Pre-check if test is assigned
            self.layout.addWidget(checkBox)

        self.assignButton = QPushButton('Сохранить', self)
        self.assignButton.clicked.connect(self.assign_selected_tests)
        self.layout.addWidget(self.assignButton)

    def assign_selected_tests(self):
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox):
                if widget.isChecked() and widget.test_id not in self.assigned_tests:
                    database.assign_test_to_student(widget.test_id, self.student_id, self.user_id)
                elif not widget.isChecked() and widget.test_id in self.assigned_tests:
                    database.remove_test_from_student(widget.test_id, self.student_id)  # Need to write this function
        self.accept()
        
class AssignTestToGroupDialog(QDialog):
    def __init__(self, group_id, user_id, parent=None):
        super().__init__(parent)
        self.group_id = group_id
        self.user_id = user_id  # Добавляем user_id
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.tests = database.get_all_tests_as_dict()

        self.testCheckBoxes = []
        for test_id, test_name in self.tests:
            checkBox = QCheckBox(test_name, self)
            checkBox.test_id = test_id
            self.testCheckBoxes.append(checkBox)
            self.layout.addWidget(checkBox)

        self.assignButton = QPushButton('Назначить выбранные тесты на группу', self)
        self.assignButton.clicked.connect(self.assign_tests)
        self.layout.addWidget(self.assignButton)

        self.removeButton = QPushButton('Отозвать выбранные тесты на группу', self)
        self.removeButton.clicked.connect(self.remove_tests)
        self.layout.addWidget(self.removeButton)

    def assign_tests(self):
        for checkBox in self.testCheckBoxes:
            if checkBox.isChecked():
                database.assign_test_to_group_students(checkBox.test_id, self.group_id, self.user_id)
        QMessageBox.information(self, 'Тесты назначены', 'Выбранные тесты были назначены группе.')
        self.accept()

    def remove_tests(self):
        for checkBox in self.testCheckBoxes:
            if checkBox.isChecked():
                database.remove_test_assignment_from_group(checkBox.test_id, self.group_id)
        QMessageBox.information(self, 'Тесты удалены', 'Выбранные тесты были удалены из группы.')
        self.accept()

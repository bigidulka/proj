# interfaces/admin/students_page.py
from PyQt5.QtWidgets import QWidget, QLabel

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QTableView, 
    QHBoxLayout, QDialog, QLineEdit, QStyledItemDelegate, QPushButton, QApplication, QStyle, QInputDialog, QMessageBox, QHeaderView, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt, QModelIndex, QRect, pyqtSignal, QAbstractTableModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem

import database
            
class AssignTestToGroupDialog(QDialog):
    def initUI(self):
        self.layout = QVBoxLayout(self)

        self.groupComboBox = QComboBox(self)
        for group in database.get_all_groups():
            self.groupComboBox.addItem(group['name'], group['id'])
        self.layout.addWidget(self.groupComboBox)

        self.testComboBox = QComboBox(self)
        for test_id, test_name in database.get_all_tests_as_dict():
            self.testComboBox.addItem(test_name, test_id)
        self.layout.addWidget(self.testComboBox)

        self.assignButton = QPushButton('Assign Test to Selected Group', self)
        self.assignButton.clicked.connect(self.assign_test)
        self.layout.addWidget(self.assignButton)

    def assign_test(self):
        group_id = self.groupComboBox.currentData()
        test_id = self.testComboBox.currentData()
        database.assign_test_to_group_students(group_id, test_id)
        self.accept()


class GroupManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        # Create a QStandardItemModel for the table
        self.groupsModel = QStandardItemModel()
        self.groupsModel.setHorizontalHeaderLabels(["Group Name"])
        
        # Table for groups
        self.groupsTable = QTableView(self)
        self.groupsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.groupsTable.setModel(self.groupsModel)
        self.layout.addWidget(self.groupsTable)

        # Button for adding a new group
        self.addGroupButton = QPushButton('Add Group', self)
        self.addGroupButton.clicked.connect(self.add_group)
        self.layout.addWidget(self.addGroupButton)

        # Button for deleting a group
        self.deleteGroupButton = QPushButton('Delete Group', self)
        self.deleteGroupButton.clicked.connect(self.delete_group)
        self.layout.addWidget(self.deleteGroupButton)

        # Button for assigning a test to a group
        self.assignTestButton = QPushButton('Assign Test to Group', self)
        self.assignTestButton.clicked.connect(self.assign_test_to_group)
        self.layout.addWidget(self.assignTestButton)

        # Button for refreshing data
        self.refreshButton = QPushButton('Refresh', self)
        self.refreshButton.clicked.connect(self.load_groups)
        self.layout.addWidget(self.refreshButton)

        self.setWindowTitle("Manage Groups")
        self.setGeometry(300, 300, 400, 300)  # Adjust size and position as needed

        # Load group data when initializing the dialog
        self.load_groups()

    def add_group(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter group name:')
        if ok and text:
            # Check if the group name already exists
            existing_groups = [item.text() for item in self.groupsModel.findItems(text)]
            if existing_groups:
                QMessageBox.warning(self, 'Group Already Exists', 'The group already exists.')
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
        AssignTestToGroupDialog(self).exec_()

    def load_groups(self):
        # Fetch updated groups data from the database
        groups = database.get_all_groups()

        # Clear the existing data in the model
        self.groupsModel.clear()
        self.groupsModel.setHorizontalHeaderLabels(["Group Name"])

        # Add the updated data to the model
        for group in groups:
            group_name = group['name']
            item = QStandardItem(group_name)
            self.groupsModel.appendRow(item)

class StudentsTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.header = ["Name", "Group", "Tests"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.header)

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole or role == Qt.EditRole:
            row = index.row()
            col = index.column()
            student = self.data[row]
            if col == 1:  # Assuming column 1 is for groups
                # Use 'group' as the key
                return student.get('group', 'N/A')  # Using get to avoid KeyError
            # Handle other columns
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.header[section]
        return None
    
    def setData(self, index, value, role):
        if role == Qt.EditRole:
            row = index.row()
            if index.column() == 1:  # Group assignment
                student_id = self.data[row]['id']
                database.set_student_group(student_id, value)
                return True
        return False
    
    def get_group_dropdown_data(self):
        groups = database.get_all_groups()
        return {group['id']: group['name'] for group in groups}
    
    def flags(self, index):
        if index.column() == 1:  # Group column is editable
            return Qt.ItemIsEditable | super().flags(index)
        return super().flags(index)

class StudentsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        # Fetch students data from the database
        students_data = database.get_all_students()

        # Create a table model with the students data
        self.studentsModel = StudentsTableModel(students_data)

        # Create a table view and set the model
        self.studentsTable = QTableView()
        self.studentsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.studentsTable.setItemDelegateForColumn(1, GroupDropdownDelegate(self))
        self.studentsTable.setModel(self.studentsModel)
        self.studentsTable.setSelectionBehavior(QTableView.SelectRows)
        self.studentsTable.setSelectionMode(QTableView.SingleSelection)
        self.layout.addWidget(self.studentsTable)

        self.manageGroupsButton = QPushButton('Manage Groups', self)
        self.manageGroupsButton.clicked.connect(self.open_group_management)
        self.layout.addWidget(self.manageGroupsButton)

        self.assignTestStudentButton = QPushButton('Assign Test to Student', self)
        self.assignTestStudentButton.clicked.connect(self.assign_test_to_student)
        self.layout.addWidget(self.assignTestStudentButton)

        self.refreshButton = QPushButton('Refresh', self)
        self.refreshButton.clicked.connect(self.refresh_students)
        self.layout.addWidget(self.refreshButton)

    def open_group_management(self):
        dialog = GroupManagementDialog(self)
        dialog.exec_()

    def assign_test_to_student(self):
        selected = self.studentsTable.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            student_id = self.studentsModel.data[row]['id']
            # Open dialog to assign test
            AssignTestDialog(student_id, self).exec_()
    


    def refresh_students(self):
        # Fetch updated students data from the database and update the model
        students_data = database.get_all_students()
        self.studentsModel = StudentsTableModel(students_data)
        self.studentsTable.setModel(self.studentsModel)
        
class GroupDropdownDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        groups = index.model().get_group_dropdown_data()
        for group_id, group_name in groups.items():
            editor.addItem(group_name, group_id)
        return editor

    def setEditorData(self, editor, index):
        if not index.isValid():
            return

        # Get the group ID from the model
        group_id = index.model().data(index, Qt.EditRole)

        # Set the current index of the editor to match the group ID
        idx = editor.findData(group_id)
        if idx >= 0:
            editor.setCurrentIndex(idx)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentData(), Qt.EditRole)
        
class AssignTestDialog(QDialog):
    def __init__(self, student_id, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.assigned_tests = set(database.get_tests_for_student(student_id))  # Fetch assigned tests for the student
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.tests = database.get_all_tests_as_dict()

        for test_id, test_name in self.tests:
            checkBox = QCheckBox(test_name, self)
            checkBox.test_id = test_id
            checkBox.setChecked(test_id in self.assigned_tests)  # Pre-check if test is assigned
            self.layout.addWidget(checkBox)

        self.assignButton = QPushButton('Assign Selected Tests', self)
        self.assignButton.clicked.connect(self.assign_selected_tests)
        self.layout.addWidget(self.assignButton)

    def assign_selected_tests(self):
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox):
                if widget.isChecked() and widget.test_id not in self.assigned_tests:
                    database.assign_test_to_student(widget.test_id, self.student_id)
                elif not widget.isChecked() and widget.test_id in self.assigned_tests:
                    database.remove_test_from_student(widget.test_id, self.student_id)  # Need to write this function
        self.accept()
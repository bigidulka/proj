# interfaces/admin/teachers_page.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableView, QPushButton, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog, QListView, QHBoxLayout, QMessageBox

import database

class TeachersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        # Create a table model for displaying teachers and their tests
        self.teachersTestsModel = QStandardItemModel()
        self.teachersTestsModel.setHorizontalHeaderLabels(["Имя учителя", "Название теста"])

        # Create a table view and set the model
        self.teachersTestsTable = QTableView(self)
        self.teachersTestsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.teachersTestsTable.setModel(self.teachersTestsModel)
        self.teachersTestsTable.setSelectionBehavior(QTableView.SelectRows)
        self.teachersTestsTable.setSelectionMode(QTableView.SingleSelection)
        self.teachersTestsTable.setEditTriggers(QTableView.NoEditTriggers)  # Disable editing
        self.layout.addWidget(self.teachersTestsTable)

        self.refreshButton = QPushButton('Refresh', self)
        self.refreshButton.clicked.connect(self.refresh_data)
        self.layout.addWidget(self.refreshButton)
        
        self.viewTestsButton = QPushButton('View Tests', self)
        self.viewTestsButton.clicked.connect(self.view_tests)
        self.layout.addWidget(self.viewTestsButton)

        # Fetch and display teacher-test data when initializing the page
        self.refresh_data()

    def refresh_data(self):
        # Updated to display all tests created by each teacher
        teachers_tests_data = database.get_teachers_tests()
        self.teachersTestsModel.clear()
        self.teachersTestsModel.setHorizontalHeaderLabels(["Имя учителя", "Созданные тесты"])
        for data in teachers_tests_data:
            teacher_name = data["teacher_name"]
            tests = data["tests"]
            teacher_item = QStandardItem(teacher_name)
            tests_item = QStandardItem(tests)
            self.teachersTestsModel.appendRow([teacher_item, tests_item])

    def view_tests(self):
        selected_index = self.teachersTestsTable.currentIndex()
        if not selected_index.isValid():
            QMessageBox.warning(self, "Selection Required", "Please select a teacher.")
            return
        teacher_name = self.teachersTestsModel.item(selected_index.row(), 0).text()
        tests = database.get_tests_by_teacher(teacher_name)
        self.show_tests_dialog(tests)

    def show_tests_dialog(self, tests):
        dialog = QDialog(self)
        dialog.setWindowTitle("View Tests")
        layout = QVBoxLayout(dialog)

        for test in tests:
            test_btn = QPushButton(f"View Test: {test['name']}", dialog)
            test_btn.clicked.connect(lambda: self.view_test_details(test['id']))
            layout.addWidget(test_btn)

        dialog.exec_()

    def view_test_details(self, test_id):
        # Implement logic to show test details
        test_details = database.get_test_with_questions_and_answers(test_id)
        # Show test details in a new dialog or window
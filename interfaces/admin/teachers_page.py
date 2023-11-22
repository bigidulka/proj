# interfaces/admin/teachers_page.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableView, QPushButton, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import database

class TeachersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        # Create a table model for displaying teachers and their tests
        self.teachersTestsModel = QStandardItemModel()
        self.teachersTestsModel.setHorizontalHeaderLabels(["Teacher Name", "Test Name"])

        # Create a table view and set the model
        self.teachersTestsTable = QTableView(self)
        self.teachersTestsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.teachersTestsTable.setModel(self.teachersTestsModel)
        self.teachersTestsTable.setSelectionBehavior(QTableView.SelectRows)
        self.teachersTestsTable.setSelectionMode(QTableView.SingleSelection)
        self.layout.addWidget(self.teachersTestsTable)

        self.refreshButton = QPushButton('Refresh', self)
        self.refreshButton.clicked.connect(self.refresh_data)
        self.layout.addWidget(self.refreshButton)

        # Fetch and display teacher-test data when initializing the page
        self.refresh_data()

    def refresh_data(self):
        # Fetch updated data from the database and update the model
        teachers_tests_data = database.get_teachers_tests()
        self.teachersTestsModel.clear()
        self.teachersTestsModel.setHorizontalHeaderLabels(["Teacher Name", "Test Name"])
        for data in teachers_tests_data:
            teacher_name = data["teacher_name"]
            test_name = data["test_name"]
            teacher_item = QStandardItem(teacher_name)
            test_item = QStandardItem(test_name)
            self.teachersTestsModel.appendRow([teacher_item, test_item])

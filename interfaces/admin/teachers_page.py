# interfaces\admin\teachers_page.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableView, QPushButton,
                             QHeaderView, QDialog, QMessageBox)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import database


class TeachersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        self.teachersTestsModel = QStandardItemModel()
        self.teachersTestsModel.setHorizontalHeaderLabels(
            ["Имя учителя", "Название теста"])

        self.teachersTestsTable = QTableView(self)
        self.teachersTestsTable.setModel(self.teachersTestsModel)
        self.teachersTestsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.teachersTestsTable.setSelectionBehavior(QTableView.SelectRows)
        self.teachersTestsTable.setSelectionMode(QTableView.SingleSelection)
        self.teachersTestsTable.setEditTriggers(QTableView.NoEditTriggers)
        self.layout.addWidget(self.teachersTestsTable)

        self.refreshButton = QPushButton("Обновить данные", self)
        self.refreshButton.clicked.connect(self.refresh_data)
        self.layout.addWidget(self.refreshButton)

        self.refresh_data()

    def refresh_data(self):
        teachers_tests_data = database.get_teachers_tests()
        self.teachersTestsModel.clear()
        self.teachersTestsModel.setHorizontalHeaderLabels(
            ["Имя учителя", "Созданные тесты"])
        for data in teachers_tests_data:
            teacher_name = data["teacher_name"]
            tests = data["tests"]
            teacher_item = QStandardItem(teacher_name)
            tests_item = QStandardItem(tests)
            self.teachersTestsModel.appendRow([teacher_item, tests_item])

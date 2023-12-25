# interfaces\student\my_tests_page.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableView, QPushButton, QHeaderView, QMessageBox)
from PyQt5.QtGui import QStandardItem, QStandardItemModel
import database
from ..test_page import TakeTestPage


class MyTestsPage(QWidget):
    def __init__(self, student_window, main_window):
        super().__init__()
        self.student_window = student_window
        self.main_window = main_window
        self.test_ids = {}
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        self.tableView = QTableView()
        self.model = QStandardItemModel(self.tableView)
        self.tableView.setModel(self.model)

        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.setSelectionMode(QTableView.SingleSelection)
        self.tableView.setEditTriggers(QTableView.NoEditTriggers)

        layout.addWidget(self.tableView)

        take_test_button = QPushButton("Пройти тест")
        take_test_button.clicked.connect(self.takeSelectedTest)
        layout.addWidget(take_test_button)

        refresh_button = QPushButton("Обновить таблицу")
        refresh_button.clicked.connect(self.loadTestData)
        layout.addWidget(refresh_button)

        self.loadTestData()

    def loadTestData(self):
        self.model.clear()
        self.model.setColumnCount(5)
        self.model.setHorizontalHeaderLabels(
            ["Название", "Описание", "Количество ост. попыток",
                "Кто создал", "Кто назначил"]
        )

        tests = database.get_assigned_tests_for_student(
            self.main_window.user_id)
        self.model.setRowCount(len(tests))

        for row, test in enumerate(tests):
            self.model.setItem(row, 0, QStandardItem(test["name"]))
            self.model.setItem(row, 1, QStandardItem(test["description"]))
            self.model.setItem(
                row, 2, QStandardItem(str(test["remaining_attempts"]))
            )
            self.model.setItem(row, 3, QStandardItem(test["creator_name"]))
            self.model.setItem(row, 4, QStandardItem(test["assigner_name"]))
            self.test_ids[row] = test["id"]

        self.adjustColumnWidths()

    def takeSelectedTest(self):
        selected_rows = self.tableView.selectionModel().selectedRows()
        if selected_rows:
            selected_row = selected_rows[0].row()
            if selected_row in self.test_ids:
                test_id = self.test_ids[selected_row]

                test_details_list = database.get_assigned_tests_for_student(
                    self.main_window.user_id)

                test_details = next(
                    (item for item in test_details_list if item["id"] == test_id), None)

                if test_details is None:
                    QMessageBox.warning(
                        self, "Ошибка", "Ошибка при получении информации о тесте.")
                    return

                if test_details["remaining_attempts"] <= 0:
                    QMessageBox.warning(
                        self, "Ошибка", "У вас не осталось попыток для этого теста.")
                    return

                response = QMessageBox.warning(
                    self,
                    "Предупреждение",
                    "Вы собираетесь начать тест. Вы не сможете вернуться к другим разделам, пока не завершите тест. Вы уверены, что хотите продолжить?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,)
                if response == QMessageBox.Yes:
                    self.startTest(test_id)
        else:
            QMessageBox.warning(
                self, "Ошибка", "Пожалуйста, выберите тест для прохождения.")

    def adjustColumnWidths(self):
        column_count = self.model.columnCount()
        total_width = self.tableView.viewport().width()
        column_width = total_width // column_count

        for column in range(column_count):
            self.tableView.setColumnWidth(column, column_width)

    def startTest(self, test_id):
        self.student_window.sidebar.setEnabled(False)
        self.take_test_page = TakeTestPage(
            test_id, self.main_window, self.student_window)
        self.student_window.stack.addWidget(self.take_test_page)
        self.student_window.stack.setCurrentWidget(self.take_test_page)

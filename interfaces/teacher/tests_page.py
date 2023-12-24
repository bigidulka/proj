# tests_page.py
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget, QFormLayout, 
                             QLineEdit, QSpinBox, QTextEdit, QComboBox, QScrollArea, QGroupBox, 
                             QApplication, QRadioButton, QCheckBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from database import get_all_tests, delete_test
import json
import database

from ..test_page import CreateTestPage, ViewTestPage


class TestsPage(QWidget):
    def __init__(self, admin_window):
        super().__init__()
        self.admin_window = admin_window
        self.current_tab_index = 0 
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        self.tableWidget = QTableWidget(self)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setColumnCount(3)  # Columns: Test Name, Characteristics, Created By
        self.tableWidget.setHorizontalHeaderLabels(["Название Теста", "Описание", "Сделан"])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.cellChanged.connect(self.onDescriptionEdited)
        self.load_tests()
        layout.addWidget(self.tableWidget)

        # Buttons
        button_layout = QHBoxLayout()
        create_button = QPushButton('Создать тест', self)
        create_button.clicked.connect(self.create_test)
        button_layout.addWidget(create_button)

        view_button = QPushButton('Посмотреть тест', self)
        view_button.clicked.connect(self.view_test)
        button_layout.addWidget(view_button)

        delete_button = QPushButton('Удалить тест', self)
        delete_button.clicked.connect(self.delete_test)
        button_layout.addWidget(delete_button)

        refresh_button = QPushButton('Обновить данные', self)
        refresh_button.clicked.connect(self.refresh_tests)
        button_layout.addWidget(refresh_button)

        layout.addLayout(button_layout)
        
    def view_test(self):
        selected_rows = self.tableWidget.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка выбора", "Пожалуйста, выберите тест для просмотра.")
            return
        row = selected_rows[0].row()
        test_name = self.tableWidget.item(row, 0).text()
        view_test_page = ViewTestPage(self, test_name)
        self.admin_window.stack.addWidget(view_test_page)
        self.admin_window.stack.setCurrentWidget(view_test_page)

    def load_tests(self):
        tests = self.loadTest()
        self.tableWidget.setRowCount(len(tests))
        for row, test in enumerate(tests):
            # Создаем нередактируемые ячейки для имени и создателя
            name_item = QTableWidgetItem(test['name'])
            name_item.setData(Qt.UserRole, test['id'])  # Установка UserRole с ID теста
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.tableWidget.setItem(row, 0, name_item)

            # Создаем редактируемую ячейку для описания
            description_item = QTableWidgetItem(test['description'])
            self.tableWidget.setItem(row, 1, description_item)

            created_by_item = QTableWidgetItem(test['created_by'])
            created_by_item.setFlags(created_by_item.flags() & ~Qt.ItemIsEditable)
            self.tableWidget.setItem(row, 2, created_by_item)

    def onDescriptionEdited(self, row, column):
        if column == 1:  # Проверяем, что изменена ячейка описания
            test_id = self.tableWidget.item(row, 0).data(Qt.UserRole)  # Предполагаем, что ID теста хранится в UserRole первой ячейки строки
            new_description = self.tableWidget.item(row, column).text()
            database.updateTestDescription(test_id, new_description)
            
    def loadTest(self):
        test_details = None
        if self.admin_window.main_window.user_role == 'ADMIN':
            test_details = database.get_all_tests()
        elif self.admin_window.main_window.user_role == 'TEACHER':
            test_details = database.get_tests_by_teacher_id(self.admin_window.main_window.user_id)

        return test_details
            
    def create_test(self):
        self.current_tab_index = self.admin_window.stack.currentIndex()
        logged_in_user_id = self.admin_window.main_window.logged_in_user_id
        create_test_dialog = CreateTestPage(self, logged_in_user_id)
        self.create_test_dialog = create_test_dialog
        self.admin_window.stack.addWidget(create_test_dialog)
        self.admin_window.stack.setCurrentWidget(create_test_dialog)

    def return_to_previous_tab(self):
        self.admin_window.stack.setCurrentIndex(self.current_tab_index)
        
    def delete_test(self):
        selected_rows = self.tableWidget.selectedItems()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        test_name = self.tableWidget.item(row, 0).text()
        delete_test(test_name)
        self.tableWidget.removeRow(row)

    def refresh_tests(self):
        # Reload and refresh the list of tests
        self.load_tests()
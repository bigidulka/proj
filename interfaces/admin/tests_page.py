# tests_page.py
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget, QFormLayout, 
                             QLineEdit, QSpinBox, QTextEdit, QComboBox, QScrollArea, QGroupBox, 
                             QApplication, QRadioButton, QCheckBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from database import get_all_tests, delete_test
import json

from ..test_page import CreateTestPage, ViewTestPage


class TestsPage(QWidget):
    def __init__(self, admin_window):
        super().__init__()
        self.admin_window = admin_window
        self.current_tab_index = 0 
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        label = QLabel('Manage Tests', self)
        layout.addWidget(label)

        self.tableWidget = QTableWidget(self)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setColumnCount(3)  # Columns: Test Name, Characteristics, Created By
        self.tableWidget.setHorizontalHeaderLabels(["Test Name", "Characteristics", "Created By"])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.load_tests()
        layout.addWidget(self.tableWidget)

        # Buttons
        button_layout = QHBoxLayout()
        create_button = QPushButton('Create Test', self)
        create_button.clicked.connect(self.create_test)
        button_layout.addWidget(create_button)

        view_button = QPushButton('View Test', self)
        view_button.clicked.connect(self.view_test)
        button_layout.addWidget(view_button)

        delete_button = QPushButton('Delete Test', self)
        delete_button.clicked.connect(self.delete_test)
        button_layout.addWidget(delete_button)

        refresh_button = QPushButton('Refresh', self)
        refresh_button.clicked.connect(self.refresh_tests)
        button_layout.addWidget(refresh_button)

        layout.addLayout(button_layout)
        
    def view_test(self):
        selected_rows = self.tableWidget.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a test to view.")
            return
        row = selected_rows[0].row()
        test_name = self.tableWidget.item(row, 0).text()
        view_test_page = ViewTestPage(self, test_name)
        self.admin_window.stack.addWidget(view_test_page)
        self.admin_window.stack.setCurrentWidget(view_test_page)

    def load_tests(self):
        tests = get_all_tests()
        self.tableWidget.setRowCount(len(tests))
        for row, test in enumerate(tests):
            self.tableWidget.setItem(row, 0, QTableWidgetItem(test['name']))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(test['attempts']))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(test['created_by']))
            
    def create_test(self):
        self.current_tab_index = self.admin_window.stack.currentIndex()
        logged_in_user_id = self.get_logged_in_user_id()
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
        
    def get_logged_in_user_id(self):
        return self.admin_window.main_window.logged_in_user_id
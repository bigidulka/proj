# interfaces\reports_page.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QAbstractItemView, QPushButton, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
import database


class TestAttemptDetailsWindow(QWidget):
    def __init__(self, student_id, test_id, attempt_id):
        super().__init__()
        self.student_id = student_id
        self.test_id = test_id
        self.attempt_id = attempt_id
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        self.questionsTable = QTableWidget()
        self.questionsTable.setColumnCount(2)  # Question and Answer columns
        self.questionsTable.setHorizontalHeaderLabels(['Вопрос', 'Ответ'])
        self.questionsTable.verticalHeader().setVisible(False)
        self.questionsTable.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.questionsTable)

        self.loadAttemptDetails()

    def loadAttemptDetails(self):
        attempt_details = database.get_attempt_details(
            self.student_id, self.test_id, self.attempt_id)

        self.questionsTable.setRowCount(len(attempt_details))
        for row, (question, student_answer, correct_answer) in enumerate(attempt_details):
            question_item = QTableWidgetItem(question)
            answer_item = QTableWidgetItem(student_answer)

            if student_answer == correct_answer:
                answer_item.setBackground(
                    QColor(0, 255, 0))
            else:
                answer_item.setBackground(
                    QColor(255, 0, 0))

            self.questionsTable.setItem(row, 0, question_item)
            self.questionsTable.setItem(row, 1, answer_item)


class ReportsWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        self.studentsListView = QTableView()
        self.studentsModel = StudentsTableModel()
        self.studentsListView.setModel(self.studentsModel)
        self.studentsListView.verticalHeader().setVisible(False)
        self.studentsListView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.studentsListView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.studentsListView.clicked.connect(self.onStudentSelected)
        self.layout.addWidget(self.studentsListView)

        self.testsTableView = QTableView()
        self.testsTableModel = TestsTableModel()
        self.testsTableView.setModel(self.testsTableModel)
        self.testsTableView.verticalHeader().setVisible(False)
        self.testsTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.testsTableView.clicked.connect(self.onTestSelected)
        self.testsTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.layout.addWidget(self.testsTableView)

        self.studentAttemptsTableModel = QStandardItemModel()
        self.studentAttemptsTableView = QTableView()
        self.studentAttemptsTableView.setModel(self.studentAttemptsTableModel)
        self.studentAttemptsTableView.verticalHeader().setVisible(False)
        self.studentAttemptsTableView.horizontalHeader(
        ).setSectionResizeMode(QHeaderView.Stretch)
        self.studentAttemptsTableView.setEditTriggers(
            QAbstractItemView.NoEditTriggers)
        self.layout.addWidget(self.studentAttemptsTableView)

        self.viewDetailsButton = QPushButton("Просмотреть ответы")
        self.viewDetailsButton.clicked.connect(self.onViewDetails)
        self.layout.addWidget(self.viewDetailsButton)

        self.updateButton = QPushButton("Обновить данные")
        self.updateButton.clicked.connect(self.populateStudentsList)
        self.layout.addWidget(self.updateButton)

        self.populateStudentsList()

    def onViewDetails(self):
        selected_attempt_index = self.studentAttemptsTableView.currentIndex()
        if not selected_attempt_index.isValid():
            return

        attempt_id = self.studentAttemptsTableModel.data(
            selected_attempt_index, Qt.UserRole)

        self.detailsWindow = TestAttemptDetailsWindow(
            self.selected_student_id, self.selected_test_id, attempt_id)
        self.detailsWindow.show()

    def populateStudentsList(self):
        students = database.get_all_students()
        self.studentsModel.setStudents(students)

    def onStudentSelected(self, index: QModelIndex):
        student_id = self.studentsModel.data(index, Qt.UserRole)
        self.studentAttemptsTableModel.clear()
        self.loadStudentTests(student_id)

    def loadStudentTests(self, student_id):
        tests = database.get_tests_by_student(student_id)
        self.testsTableModel.setTests(tests)

    def onTestSelected(self, index: QModelIndex):
        test_id = self.testsTableModel.testId(index)
        student_id = self.studentsListView.currentIndex().data(Qt.UserRole)
        self.updateTestAttempts(student_id, test_id)

    def updateTestAttempts(self, student_id, test_id):
        attempts_data = database.get_student_test_attempt_results(
            student_id, test_id)
        self.studentAttemptsTableModel.clear()
        self.studentAttemptsTableModel.setHorizontalHeaderLabels(
            ['Номер попытки', 'Результат'])

        attempt_results = {}
        for test_result_id, is_correct, _ in attempts_data:
            if test_result_id not in attempt_results:
                attempt_results[test_result_id] = {'total': 0, 'correct': 0}
            attempt_results[test_result_id]['total'] += 1
            if is_correct:
                attempt_results[test_result_id]['correct'] += 1

        for attempt_number, result in enumerate(attempt_results.values(), start=1):
            result_str = f"{result['correct']}/{result['total']}"
            row = [QStandardItem(str(attempt_number)),
                   QStandardItem(result_str)]
            self.studentAttemptsTableModel.appendRow(row)


class TestsTableModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels(['Название теста'])
        self.testData = []

    def setTests(self, tests):
        self.clear()
        self.setHorizontalHeaderLabels(['Название теста'])
        self.testData = tests
        for test in tests:
            row = [QStandardItem(test['name'])]
            self.appendRow(row)

    def testId(self, index):
        if 0 <= index.row() < len(self.testData):
            return self.testData[index.row()]['id']
        return None


class StudentsTableModel(QStandardItemModel):
    def __init__(self, students=None):
        super().__init__()
        self.students = students or []

    def setStudents(self, students):
        self.students = students
        self.clear()
        self.setHorizontalHeaderLabels(['Ученики'])
        self.setColumnCount(1)
        self.setRowCount(len(self.students))

        for row, student in enumerate(self.students):
            item = QStandardItem(student["name"])
            self.setItem(row, 0, item)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.UserRole:
            return self.students[index.row()]["id"]

        return super().data(index, role)

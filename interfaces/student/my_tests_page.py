# interfaces/student/my_tests_page.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QHeaderView
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QFormLayout, QLabel, QLineEdit, 
                             QSpinBox, QTextEdit, QComboBox, QPushButton, QScrollArea, QGroupBox, QHBoxLayout, QApplication, QRadioButton, QCheckBox, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import database

class MyTestsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Create the table for displaying the tests
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(5)  # Specify the number of columns
        self.tableWidget.setHorizontalHeaderLabels(["Название", "Описание", "Количество ост. попыток", "Кто создал", "Кто назначил"])
        self.tableWidget.horizontalHeader().setStretchLastSection(False)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.tableWidget)
        
        # Button for taking the test
        take_test_button = QPushButton('Пройти тест')
        take_test_button.clicked.connect(self.takeSelectedTest)
        layout.addWidget(take_test_button)

        # Button for refreshing the table data
        refresh_button = QPushButton('Обновить таблицу')
        refresh_button.clicked.connect(self.loadTestData)
        layout.addWidget(refresh_button)

        # Load initial test data
        self.loadTestData()

    def loadTestData(self):
        # Clear the existing data
        self.tableWidget.setRowCount(0)

        # Fetch new data
        tests = database.get_assigned_tests_for_student(self.main_window.user_id)
        self.tableWidget.setRowCount(len(tests))

        # Populate the table with the data
        for row, test in enumerate(tests):
            self.tableWidget.setItem(row, 0, QTableWidgetItem(test['name']))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(test['description']))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(test['attempts'])))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(test['creator_name']))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(test['assigner_name']))

        # Adjust the column widths
        self.adjustColumnWidths()
        
    def takeSelectedTest(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row != -1:
            test_name = self.tableWidget.item(selected_row, 0).text()
            self.takeTest(test_name)
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите тест для прохождения.")
            
    def takeTest(self, test_name):
        self.take_test_page = TakeTestPage(test_name)
        self.take_test_page.show()


    def adjustColumnWidths(self):
        # Adjust column widths to fit content
        for column in range(self.tableWidget.columnCount()):
            self.tableWidget.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeToContents)





class TakeTestPage(QWidget):
    def __init__(self, test_name):
        super().__init__()
        self.test_name = test_name
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        label = QLabel(f'Пройти тест: {self.test_name}', self)
        layout.addWidget(label)

        self.scrollArea = QScrollArea(self)
        self.questionsWidget = QWidget()
        self.questionsLayout = QVBoxLayout(self.questionsWidget)
        self.scrollArea.setWidget(self.questionsWidget)
        self.scrollArea.setWidgetResizable(True)
        layout.addWidget(self.scrollArea)

        submit_button = QPushButton('Отправить тест')
        submit_button.clicked.connect(self.submitTest)
        layout.addWidget(submit_button)

        self.loadTest()

    def loadTest(self):
        test_details = database.get_test_details(self.test_name)
        
        for question in test_details['questions']:
            self.addQuestion(question)

    def addQuestion(self, question):
        group_box = QGroupBox()
        group_box.setStyleSheet("QGroupBox { border: 2px solid gray; border-radius: 10px; margin-top: 10px; padding-top: 10px; }")
        group_box_layout = QVBoxLayout(group_box)

        if question.get('image_path'):
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignCenter)
            pixmap = QPixmap(question['image_path'])
            image_label.setPixmap(pixmap)
            image_label.setFixedSize(200, 200)
            group_box_layout.addWidget(image_label)

        question_label = QLabel(question['text'])
        group_box_layout.addWidget(question_label)

        answer_widgets = []
        if question['type'] == 'Единственный правильный ответ':
            for answer in question['answers']:
                answer_widget = QRadioButton(answer['text'])
                group_box_layout.addWidget(answer_widget)
                answer_widgets.append(answer_widget)
        else:
            for answer in question['answers']:
                answer_widget = QCheckBox(answer['text'])
                group_box_layout.addWidget(answer_widget)
                answer_widgets.append(answer_widget)

        # Сохраняем виджеты с ответами для использования при отправке теста
        question['answer_widgets'] = answer_widgets
        self.questionsLayout.addWidget(group_box)

    def submitTest(self):
        # Сбор и обработка данных теста
        answers = []
        for question in self.test_details['questions']:
            selected_answers = []
            for widget in question['answer_widgets']:
                if widget.isChecked():
                    selected_answers.append(widget.text())

            answers.append({'question_id': question['id'], 'selected_answers': selected_answers})

        # Отправка данных теста
        self.sendTestResults(answers)

    def sendTestResults(self, answers):
        # Функция для отправки результатов теста
        # Здесь должен быть код для обработки и отправки ответов на сервер или в базу данных
        pass
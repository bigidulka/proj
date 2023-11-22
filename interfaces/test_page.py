from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QFormLayout, QLabel, QLineEdit, 
                             QSpinBox, QTextEdit, QComboBox, QPushButton, QScrollArea, QGroupBox, QHBoxLayout, QApplication, QRadioButton, QCheckBox, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from database import save_test_to_database, get_test_details

class ViewTestPage(QWidget):
    def __init__(self, tests_page, test_name):
        super().__init__()
        self.test_name = test_name
        self.tests_page = tests_page
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        label = QLabel(f'View Test: {self.test_name}', self)
        layout.addWidget(label)

        self.scrollArea = QScrollArea(self)
        self.questionsWidget = QWidget()
        self.questionsLayout = QVBoxLayout(self.questionsWidget)
        self.scrollArea.setWidget(self.questionsWidget)
        self.scrollArea.setWidgetResizable(True)
        layout.addWidget(self.scrollArea)

        close_button = QPushButton('Close')
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.loadTest()

    def loadTest(self):
        test_details = get_test_details(self.test_name)
        
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

        question_text_edit = QTextEdit(question['text'])
        question_text_edit.setReadOnly(True)
        group_box_layout.addWidget(question_text_edit)

        for answer in question['answers']:
            if question['type'] == 'Single Correct Answer':
                answer_widget = QRadioButton(answer['text'])
            else:
                answer_widget = QCheckBox(answer['text'])
            answer_widget.setChecked(answer['is_correct'])
            answer_widget.setEnabled(False)
            group_box_layout.addWidget(answer_widget)

        self.questionsLayout.addWidget(group_box)

class CreateTestPage(QWidget):
    def __init__(self, tests_page, creator_id):
        super().__init__()
        self.answer_widgets = {}
        self.tests_page = tests_page
        self.creator_id = creator_id  # Store the creator's ID
        self.initUI()
        
    def save_test(self):
        if not self.validate_test():
            return
        test_name = self.test_name.text()
        attempts = self.attempts_spinbox.value()
        questions = []

        for group_box, answer_widgets in self.answer_widgets.items():
            question_text = group_box.findChild(QTextEdit).toPlainText()
            question_type = answer_widgets['type']
            answers = []
            for answer_info in answer_widgets['answers']:
                answer_text = answer_info['input'].text()
                is_correct = answer_info['correct'].isChecked()
                answers.append({'text': answer_text, 'is_correct': is_correct})

            questions.append({'text': question_text, 'type': question_type, 'answers': answers})

        save_test_to_database(test_name, attempts, questions, self.creator_id)
        QMessageBox.information(self, 'Success', 'Test saved successfully.')
        self.tests_page.return_to_previous_tab()  # Return to the previous page
        
    def closeEvent(self, event):
        # Вызываем метод возвращения к предыдущей вкладке через tests_page
        self.tests_page.return_to_previous_tab()
        event.accept()
        
    def validate_test(self):
        if not self.test_name.text():
            QMessageBox.warning(self, 'Validation Error', 'Test name is required.')
            return False

        if self.attempts_spinbox.value() <= 0:
            QMessageBox.warning(self, 'Validation Error', 'Number of attempts must be greater than 0.')
            return False

        if len(self.answer_widgets) < 1:
            QMessageBox.warning(self, 'Validation Error', 'At least one question is required.')
            return False

        for group_box, answer_widgets in self.answer_widgets.items():
            question_text = group_box.findChild(QTextEdit).toPlainText()
            if not question_text:
                QMessageBox.warning(self, 'Validation Error', 'Each question must have a title.')
                return False
            if not answer_widgets['answers']:
                QMessageBox.warning(self, 'Validation Error', 'Each question must have at least one answer option.')
                return False
            
            if len(answer_widgets['answers']) < 2:
                QMessageBox.warning(self, 'Validation Error', 'Each question must have at least two answer options.')
                return False
            
            if not any(info['correct'].isChecked() for info in answer_widgets['answers']):
                QMessageBox.warning(self, 'Validation Error', 'Each question must have at least one correct answer marked.')
                return False

        return True

    def initUI(self):
        self.setStyleSheet("QLabel { font-size: 14px; } QPushButton { font-size: 12px; }")

        layout = QVBoxLayout(self)

        label = QLabel('Create Test', self)
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)

        self.tabWidget = QTabWidget(self)
        layout.addWidget(self.tabWidget)
        
        buttons_layout = QHBoxLayout()
        close_button = QPushButton('Close Editor')
        close_button.clicked.connect(self.close)
        save_button = QPushButton('Save Test')
        save_button.clicked.connect(self.save_test)

        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(close_button)

        layout.addLayout(buttons_layout)

        self.createManualTab()
        self.createTemplateTab()

    def createManualTab(self):
        self.manualTab = QWidget()
        self.manualLayout = QVBoxLayout(self.manualTab)

        self.test_name = QLineEdit(self)
        self.attempts_spinbox = QSpinBox(self)
        
        self.question_counter_label = QLabel('Questions: 0')
        add_question_button = QPushButton('Add Question')
        add_question_button.clicked.connect(self.addNewQuestion)

        test_info_layout = QFormLayout()
        test_info_layout.addRow('Test Name:', self.test_name)
        test_info_layout.addRow('Attempts:', self.attempts_spinbox)
        test_info_layout.addRow(self.question_counter_label, add_question_button)

        self.manualLayout.addLayout(test_info_layout)
        self.tabWidget.addTab(self.manualTab, 'Manual Creation')

        self.scrollArea = QScrollArea(self)
        self.questionsWidget = QWidget()
        self.questionsLayout = QVBoxLayout(self.questionsWidget)
        self.scrollArea.setWidget(self.questionsWidget)
        self.scrollArea.setWidgetResizable(True)
        self.manualLayout.addWidget(self.scrollArea)

    def addNewQuestion(self):
        self.addQuestion()
        self.updateQuestionCounter()
        
    def addQuestion(self):
        group_box = QGroupBox()
        group_box.setStyleSheet(
            "QGroupBox { border: 2px solid gray; border-radius: 10px; margin-top: 10px; padding-top: 10px; }"
        )
        group_box_layout = QVBoxLayout(group_box)
        
        

        # Добавляем QLabel для отображения изображения
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setFixedSize(200, 200)  # Устанавливаем фиксированный размер
        image_label.setVisible(False)

        header_layout = QHBoxLayout()
        
        # Добавляем кнопку для загрузки изображения
        add_image_button = QPushButton("Add Image")
        add_image_button.clicked.connect(lambda: self.addImageToQuestion(image_label))
        header_layout.addWidget(add_image_button)

        remove_image_button = QPushButton("Remove Image")
        remove_image_button.clicked.connect(lambda: self.removeImageFromQuestion(image_label))
        header_layout.addWidget(remove_image_button)

        delete_question_button = QPushButton('Delete Question')
        delete_question_button.clicked.connect(lambda _, gb=group_box: self.removeQuestion(gb))
        header_layout.addStretch(1)
        header_layout.addWidget(delete_question_button)
        group_box_layout.addLayout(header_layout)

        group_box_layout.addWidget(image_label)
        # Добавляем QTextEdit для текстового вопроса
        question_text_edit = QTextEdit()
        question_text_edit.setPlaceholderText("Enter your question text here...")
        group_box_layout.addWidget(question_text_edit)

        question_type = QComboBox()
        question_type.addItems(["Single Correct Answer", "Multiple Correct Answers"])
        question_type.currentTextChanged.connect(lambda qtype, gb=group_box: self.changeAnswerType(gb, qtype))
        group_box_layout.addWidget(question_type)

        answers_layout = QVBoxLayout()
        group_box_layout.addLayout(answers_layout)

        self.questionsLayout.addWidget(group_box)

        add_answer_button = QPushButton('Add Answer Option')
        add_answer_button.clicked.connect(lambda: self.addAnswerOption(group_box, answers_layout))
        group_box_layout.addWidget(add_answer_button)

        # Use group_box itself as the key for answer widgets tracking
        self.answer_widgets[group_box] = {'layout': answers_layout, 'type': 'Single Correct Answer', 'answers': []}
        
    def addImageToQuestion(self, image_label):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select an image file", "", "Images (*.png *.jpg *.bmp *.gif *.jpeg);;All Files (*)", options=options)

        if file_name:
            pixmap = QPixmap(file_name)
            image_label.setPixmap(pixmap)
            image_label.setFixedSize(200, 200)
            image_label.setVisible(True)  # Показываем изображение

    def removeImageFromQuestion(self, image_label):
        image_label.clear()  # Очищаем изображение
        image_label.setVisible(False)
            
    def changeAnswerType(self, group_box, question_type):
        # Get the list of answer widgets for this question
        answer_info_list = self.answer_widgets[group_box]['answers']
        
        # Update the type in the tracking dictionary
        self.answer_widgets[group_box]['type'] = question_type
        
        # Loop through each answer widget set
        for answer_info in answer_info_list:
            # Remove the old widget for marking correct answers
            correct_widget = answer_info['correct']
            answer_info['layout'].removeWidget(correct_widget)
            correct_widget.deleteLater()  # Explicit deletion

            # Create the new correct answer input based on the question type
            if question_type == 'Single Correct Answer':
                correct_widget = QRadioButton()
            else:
                correct_widget = QCheckBox()
            
            answer_info['correct'] = correct_widget
            answer_info['layout'].insertWidget(0, correct_widget) 

    def addAnswerOption(self, group_box, layout):
        answer_widgets = self.answer_widgets[group_box]['answers']
        answer_layout = QHBoxLayout()
        
        # Create the correct answer input based on the type of question
        if self.answer_widgets[group_box]['type'] == 'Single Correct Answer':
            correct_answer_input = QRadioButton()
        else:
            correct_answer_input = QCheckBox()

        answer_label = QLabel(f"Answer {len(answer_widgets) + 1}:")
        answer = QLineEdit()
        delete_answer_button = QPushButton('X')
        delete_answer_button.clicked.connect(lambda: self.removeAnswerOption(group_box, layout, answer_layout))

        answer_layout.addWidget(correct_answer_input)
        answer_layout.addWidget(answer_label)
        answer_layout.addWidget(answer)
        answer_layout.addWidget(delete_answer_button)

        layout.addLayout(answer_layout)
        answer_widgets.append({'layout': answer_layout, 'input': answer, 'correct': correct_answer_input})

    def removeAnswerOption(self, group_box, parent_layout, answer_layout):
        # Remove all widgets from the layout
        while answer_layout.count():
            item = answer_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Remove the layout reference from the answer widgets tracking
        answer_info_list = self.answer_widgets[group_box]['answers']
        self.answer_widgets[group_box]['answers'] = [info for info in answer_info_list if info['layout'] != answer_layout]

        # Update the numbering of the remaining answers
        self.updateAnswerOptionNumbers(group_box)
            
    def updateAnswerOptionNumbers(self, group_box):
        # Retrieve the answers list from the dictionary
        answers_list = self.answer_widgets[group_box]['answers']
        
        # Update the numbering of the remaining answer options
        for i, answer_info in enumerate(answers_list, start=1):
            # Update the label text to reflect the new numbering
            answer_label = answer_info['layout'].itemAt(1).widget()
            if isinstance(answer_label, QLabel):
                answer_label.setText(f"Answer {i}:")



    def removeQuestion(self, group_box):
        self.questionsLayout.removeWidget(group_box)
        group_box.deleteLater()
        
        # Retrieve and remove the associated answer widgets info
        if group_box in self.answer_widgets:
            for answer_info in self.answer_widgets[group_box]['answers']:
                # Explicitly delete the layout and its widgets
                while answer_info['layout'].count():
                    item = answer_info['layout'].takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
            del self.answer_widgets[group_box]

        self.updateQuestionCounter()
        
    def updateQuestionCounter(self):
        question_count = len(self.questionsLayout.children())
        self.question_counter_label.setText(f'Questions: {question_count}')

    def createTemplateTab(self):
        templateTab = QWidget()
        templateLayout = QVBoxLayout(templateTab)
        templateLabel = QLabel('Template Tab (Empty)', templateTab)
        templateLayout.addWidget(templateLabel)
        self.tabWidget.addTab(templateTab, 'Template')
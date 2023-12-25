# interfaces\test_page.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QFormLayout, QLabel, QLineEdit, QSpinBox, QTextEdit,
                             QComboBox, QPushButton, QScrollArea, QGroupBox, QHBoxLayout, QRadioButton, QCheckBox, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import database


class ViewTestPage(QWidget):
    def __init__(self, tests_page, test_id, admin_window):
        super().__init__()
        self.test_id = test_id
        self.tests_page = tests_page
        self.test_details = database.get_test_details(self.test_id)
        self.test_name = self.test_details["name"]
        self.admin_window = admin_window
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        label = QLabel(f"Тест: {self.test_name}", self)
        layout.addWidget(label)

        self.scrollArea = QScrollArea(self)
        self.questionsWidget = QWidget()
        self.questionsLayout = QVBoxLayout(self.questionsWidget)
        self.scrollArea.setWidget(self.questionsWidget)
        self.scrollArea.setWidgetResizable(True)
        layout.addWidget(self.scrollArea)

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.close_view)
        layout.addWidget(close_button)

        self.loadTest()

    def close_view(self):
        self.close()
        self.admin_window.stack.setCurrentWidget(self.admin_window.test_page)

    def loadTest(self):
        test_details = database.get_test_details(self.test_id)
        for question in test_details["questions"]:
            self.addQuestion(question)

    def addQuestion(self, question):
        group_box = QGroupBox()
        group_box_layout = QVBoxLayout(group_box)

        if question.get("image_path"):
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignCenter)
            pixmap = QPixmap(question["image_path"])
            image_label.setPixmap(pixmap)
            image_label.setFixedSize(200, 200)
            group_box_layout.addWidget(image_label)

        question_text_edit = QTextEdit(question["text"])
        question_text_edit.setReadOnly(True)
        group_box_layout.addWidget(question_text_edit)

        for answer in question["answers"]:
            if question["type"] == "Единственный правильный ответ":
                answer_widget = QRadioButton(answer["text"])
            else:
                answer_widget = QCheckBox(answer["text"])

            answer_widget.setProperty("answer_id", answer["id"])

            if answer["is_correct"]:
                answer_widget.setChecked(True)

            answer_widget.setDisabled(True)

            group_box_layout.addWidget(answer_widget)

        self.questionsLayout.addWidget(group_box)


class CreateTestPage(QWidget):
    def __init__(self, tests_page, creator_id, refresh_tests):
        super().__init__()
        self.answer_widgets = {}
        self.tests_page = tests_page
        self.creator_id = creator_id
        self.refresh_tests = refresh_tests
        self.initUI()

    def save_test(self):
        if not self.validate_test():
            return
        test_name = self.test_name.text()
        attempts = self.attempts_spinbox.value()
        questions = []

        for group_box, answer_widgets in self.answer_widgets.items():
            question_text = group_box.findChild(QTextEdit).toPlainText()
            question_type = answer_widgets["type"]
            answers = []
            for answer_info in answer_widgets["answers"]:
                answer_text = answer_info["input"].text()
                is_correct = answer_info["correct"].isChecked()
                answers.append({"text": answer_text, "is_correct": is_correct})

            questions.append(
                {"text": question_text, "type": question_type, "answers": answers}
            )

        database.save_test_to_database(
            test_name, attempts, questions, self.creator_id)
        QMessageBox.information(self, "Успех", "Тест успешно сохранен..")
        self.tests_page.return_to_previous_tab()
        self.refresh_tests()

    def closeEvent(self, event):
        self.tests_page.return_to_previous_tab()
        event.accept()

    def validate_test(self):
        if not self.test_name.text():
            QMessageBox.warning(self, "Ошибка проверки",
                                "Укажите название теста.")
            return False

        if self.attempts_spinbox.value() <= 0:
            QMessageBox.warning(
                self, "Ошибка проверки", "Количество попыток должно быть больше 0.")
            return False

        if len(self.answer_widgets) < 1:
            QMessageBox.warning(
                self, "Ошибка проверки", "Требуется хотя бы один вопрос.")
            return False

        for group_box, answer_widgets in self.answer_widgets.items():
            question_text = group_box.findChild(QTextEdit).toPlainText()
            if not question_text:
                QMessageBox.warning(
                    self, "Ошибка проверки", "Каждый вопрос должен иметь заголовок.")
                return False

            if len(answer_widgets["answers"]) < 2:
                QMessageBox.warning(
                    self,
                    "Ошибка проверки",
                    "Каждый вопрос должен иметь не менее двух вариантов ответа.",)
                return False

            if not any(info["correct"].isChecked() for info in answer_widgets["answers"]):
                QMessageBox.warning(
                    self,
                    "Ошибка проверки",
                    "В каждом вопросе должен быть отмечен хотя бы один правильный ответ.",)
                return False

            for answer_info in answer_widgets["answers"]:
                answer_text = answer_info["input"].text()
                if not answer_text:
                    QMessageBox.warning(
                        self,
                        "Ошибка проверки",
                        "Каждый вариант ответа должен быть заполнен.")
                    return False

        return True

    def initUI(self):
        layout = QVBoxLayout(self)

        label = QLabel("Создание теста", self)
        layout.addWidget(label)

        self.tabWidget = QTabWidget(self)
        layout.addWidget(self.tabWidget)

        buttons_layout = QHBoxLayout()
        close_button = QPushButton("Закрыть редактор")
        close_button.clicked.connect(self.close)
        save_button = QPushButton("Сохранить тест")
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

        self.question_counter_label = QLabel("Вопросы: 0")
        add_question_button = QPushButton("Добавить вопрос")
        add_question_button.clicked.connect(self.addNewQuestion)

        test_info_layout = QFormLayout()
        test_info_layout.addRow("Название теста:", self.test_name)
        test_info_layout.addRow("Попытки:", self.attempts_spinbox)
        test_info_layout.addRow(
            self.question_counter_label, add_question_button)

        self.manualLayout.addLayout(test_info_layout)
        self.tabWidget.addTab(self.manualTab, "Ручное создание")

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
        group_box_layout = QVBoxLayout(group_box)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setFixedSize(200, 200)
        image_label.setVisible(False)

        header_layout = QHBoxLayout()

        add_image_button = QPushButton("Добавить изображениеe")
        add_image_button.clicked.connect(
            lambda: self.addImageToQuestion(image_label))
        header_layout.addWidget(add_image_button)

        remove_image_button = QPushButton("Удалить изображение")
        remove_image_button.clicked.connect(
            lambda: self.removeImageFromQuestion(image_label))
        header_layout.addWidget(remove_image_button)

        delete_question_button = QPushButton("Удалить вопрос")
        delete_question_button.clicked.connect(
            lambda _, gb=group_box: self.removeQuestion(gb))
        header_layout.addStretch(1)
        header_layout.addWidget(delete_question_button)
        group_box_layout.addLayout(header_layout)

        group_box_layout.addWidget(image_label)

        question_text_edit = QTextEdit()
        question_text_edit.setPlaceholderText(
            "Введите сюда текст вашего вопроса...")
        group_box_layout.addWidget(question_text_edit)

        question_type = QComboBox()
        question_type.addItems(
            ["Единственный правильный ответ", "Несколько правильных ответов"])
        question_type.currentTextChanged.connect(
            lambda qtype, gb=group_box: self.changeAnswerType(gb, qtype))
        group_box_layout.addWidget(question_type)

        answers_layout = QVBoxLayout()
        group_box_layout.addLayout(answers_layout)

        self.questionsLayout.addWidget(group_box)

        add_answer_button = QPushButton("Добавить вариант ответа")
        add_answer_button.clicked.connect(
            lambda: self.addAnswerOption(group_box, answers_layout))
        group_box_layout.addWidget(add_answer_button)

        self.answer_widgets[group_box] = {
            "layout": answers_layout,
            "type": "Единственный правильный ответ",
            "answers": [],
        }

    def addImageToQuestion(self, image_label):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select an image file",
            "",
            "Images (*.png *.jpg *.bmp *.gif *.jpeg);;All Files (*)",
            options=options,
        )

        if file_name:
            pixmap = QPixmap(file_name)
            image_label.setPixmap(pixmap)
            image_label.setFixedSize(200, 200)
            image_label.setVisible(True)

    def removeImageFromQuestion(self, image_label):
        image_label.clear()
        image_label.setVisible(False)

    def changeAnswerType(self, group_box, question_type):
        answer_info_list = self.answer_widgets[group_box]["answers"]

        self.answer_widgets[group_box]["type"] = question_type

        for answer_info in answer_info_list:
            correct_widget = answer_info["correct"]
            answer_info["layout"].removeWidget(correct_widget)
            correct_widget.deleteLater()

            if question_type == "Единственный правильный ответ":
                correct_widget = QRadioButton()
            else:
                correct_widget = QCheckBox()

            answer_info["correct"] = correct_widget
            answer_info["layout"].insertWidget(0, correct_widget)

    def addAnswerOption(self, group_box, layout):
        answer_widgets = self.answer_widgets[group_box]["answers"]
        answer_layout = QHBoxLayout()

        if self.answer_widgets[group_box]["type"] == "Единственный правильный ответ":
            correct_answer_input = QRadioButton()
        else:
            correct_answer_input = QCheckBox()

        answer_label = QLabel(f"Ответ {len(answer_widgets) + 1}:")
        answer = QLineEdit()
        delete_answer_button = QPushButton("X")
        delete_answer_button.clicked.connect(
            lambda: self.removeAnswerOption(group_box, layout, answer_layout))

        answer_layout.addWidget(correct_answer_input)
        answer_layout.addWidget(answer_label)
        answer_layout.addWidget(answer)
        answer_layout.addWidget(delete_answer_button)

        layout.addLayout(answer_layout)
        answer_widgets.append(
            {"layout": answer_layout, "input": answer, "correct": correct_answer_input})

    def removeAnswerOption(self, group_box, parent_layout, answer_layout):
        while answer_layout.count():
            item = answer_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        answer_info_list = self.answer_widgets[group_box]["answers"]
        self.answer_widgets[group_box]["answers"] = [
            info for info in answer_info_list if info["layout"] != answer_layout]

        self.updateAnswerOptionNumbers(group_box)

    def updateAnswerOptionNumbers(self, group_box):
        answers_list = self.answer_widgets[group_box]["answers"]

        for i, answer_info in enumerate(answers_list, start=1):
            answer_label = answer_info["layout"].itemAt(1).widget()
            if isinstance(answer_label, QLabel):
                answer_label.setText(f"Ответ {i}:")

    def removeQuestion(self, group_box):
        self.questionsLayout.removeWidget(group_box)
        group_box.deleteLater()

        if group_box in self.answer_widgets:
            for answer_info in self.answer_widgets[group_box]["answers"]:
                while answer_info["layout"].count():
                    item = answer_info["layout"].takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
            del self.answer_widgets[group_box]

        self.updateQuestionCounter()

    def updateQuestionCounter(self):
        question_count = len(self.questionsLayout.children())
        self.question_counter_label.setText(f"Вопросы: {question_count}")

    def createTemplateTab(self):
        templateTab = QWidget()
        templateLayout = QVBoxLayout(templateTab)
        templateLabel = QLabel("Вкладка «Шаблон» (пустая)", templateTab)
        templateLayout.addWidget(templateLabel)
        self.tabWidget.addTab(templateTab, "Шаблон")


class TakeTestPage(QWidget):
    def __init__(self, test_id, main_window, student_window):
        super().__init__()
        self.test_id = test_id
        self.main_window = main_window
        self.student_window = student_window
        self.test_submitted = False
        self.test_details = database.get_test_details(self.test_id)
        self.test_name = self.test_details["name"]
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        label = QLabel(f"Тест: {self.test_name}", self)
        layout.addWidget(label)

        self.scrollArea = QScrollArea(self)
        self.questionsWidget = QWidget()
        self.questionsLayout = QVBoxLayout(self.questionsWidget)
        self.scrollArea.setWidget(self.questionsWidget)
        self.scrollArea.setWidgetResizable(True)
        layout.addWidget(self.scrollArea)

        submit_button = QPushButton("Отправить тест")
        submit_button.clicked.connect(self.submitTest)
        layout.addWidget(submit_button)

        self.loadTest()

    def loadTest(self):
        self.test_details = database.get_test_details(self.test_id)

        for question in self.test_details["questions"]:
            self.addQuestion(question)

    def addQuestion(self, question):
        group_box = QGroupBox()
        group_box_layout = QVBoxLayout(group_box)

        if question.get("image_path"):
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignCenter)
            pixmap = QPixmap(question["image_path"])
            image_label.setPixmap(pixmap)
            image_label.setFixedSize(200, 200)
            group_box_layout.addWidget(image_label)

        question_label = QLabel(question["text"])
        group_box_layout.addWidget(question_label)

        answer_widgets = []
        for answer in question["answers"]:
            if question["type"] == "Единственный правильный ответ":
                answer_widget = QRadioButton(answer["text"])
            else:
                answer_widget = QCheckBox(answer["text"])

            answer_widget.setProperty("answer_id", answer["id"])
            group_box_layout.addWidget(answer_widget)
            answer_widgets.append(answer_widget)

        question["answer_widgets"] = answer_widgets
        self.questionsLayout.addWidget(group_box)

    def submitTest(self):
        answers = []
        for question in self.test_details["questions"]:
            selected_answers = []
            for widget in question["answer_widgets"]:
                if widget.isChecked():
                    selected_answers.append(widget.property("answer_id"))

            if not selected_answers:
                selected_answers.append(None)

            answers.append(
                {"question_id": question["id"], "selected_answers": selected_answers})

        self.sendTestResults(answers)
        self.updateTestAttempts()
        self.test_submitted = True
        self.student_window.sidebar.setEnabled(True)
        self.switchToMainMenu()

    def switchToMainMenu(self):
        self.student_window.stack.setCurrentWidget(
            self.student_window.tests_page)

    def updateTestAttempts(self):
        student_id = self.main_window.user_id
        test_id = self.test_id

        attempts_left = database.get_remaining_attempts(student_id, test_id)
        if attempts_left <= 0:
            QMessageBox.information(
                self, "Тест завершен", "Вы исчерпали все попытки для этого теста.")

    def sendTestResults(self, answers):
        student_id = self.main_window.user_id
        test_id = self.test_details["id"]
        database.record_test_results(student_id, test_id, answers)
        QMessageBox.information(self, "Тест отправлен",
                                "Ваши ответы были успешно сохранены.")

    def closeEvent(self, event):
        if not self.test_submitted:
            self.submitTest()

        self.student_window.sidebar.setEnabled(True)
        event.accept()

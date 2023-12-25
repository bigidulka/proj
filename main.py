# main.py

from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
import sys
from interfaces import LoginWindow, AdminWindow, TeacherWindow, StudentWindow
import database


def load_stylesheet(path):
    with open(path, "r") as f:
        return f.read()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logged_in_user_id = None
        self.user_role = None
        self.user_id = None
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        style = load_stylesheet("resources/styles/main_style.css")
        self.setStyleSheet(style)

        self.login_window = LoginWindow(self)
        self.central_widget.addWidget(self.login_window)

        self.setGeometry(300, 300, 1024, 768)
        self.setWindowTitle("Система управления тестами и результатами")
        self.central_widget.setCurrentWidget(self.login_window)

    def initAdminWindow(self):
        self.admin_window = AdminWindow(self)
        self.central_widget.addWidget(self.admin_window)

    def initTeacherWindow(self):
        self.teacher_window = TeacherWindow(self)
        self.central_widget.addWidget(self.teacher_window)

    def initStudentWindow(self):
        self.student_window = StudentWindow(self)
        self.central_widget.addWidget(self.student_window)


if __name__ == "__main__":
    database.setup_database()
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

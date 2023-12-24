# main.py
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
import sys
from interfaces import LoginWindow, AdminWindow, TeacherWindow, StudentWindow
from database import setup_database


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logged_in_user_id = None
        self.user_role = None
        self.user_id = None
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.login_window = LoginWindow(self)
        self.central_widget.addWidget(self.login_window)

        self.setGeometry(300, 300, 1024, 768)
        self.setWindowTitle('Test Management System')
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


if __name__ == '__main__':
    setup_database()
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
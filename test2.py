import sys
from PyQt5.QtCore import Qt, QEvent, QTimer, QModelIndex, QAbstractTableModel
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableView, QStyledItemDelegate, QTextEdit, QComboBox, QPushButton

class CustomTableModel(QAbstractTableModel):
    def __init__(self, data, headers, editable_columns=None):
        super().__init__()
        self._data = data
        self._headers = headers
        self._editable_columns = editable_columns or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            return str(self._data[row][col])
        elif role == Qt.EditRole:
            return self._data[row][col]

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False

        row = index.row()
        col = index.column()

        self._data[row][col] = value
        self.dataChanged.emit(index, index)
        return True

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headers[section]
            elif orientation == Qt.Vertical:
                return str(section + 1)  # Display row numbers in the vertical header

    def flags(self, index):
        if index.column() in self._editable_columns:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

class CustomDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.button_icon = QIcon("resources/icons/eye-icon.png")
        self.show_password = {}
        self.timer = QTimer()
        self.timer.timeout.connect(self.hide_password)
        self.roles = ["ADMIN", "STUDENT", "TEACHER"]

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        if index.column() == 3:
            password = index.data(Qt.DisplayRole)
            show = self.show_password.get(index, False)
            painter.eraseRect(option.rect)
            if show:
                painter.drawText(option.rect, Qt.AlignVCenter, password)
            else:
                masked_password = '*' * len(password)
                painter.drawText(option.rect, Qt.AlignVCenter, masked_password)
            button_rect = option.rect.adjusted(option.rect.width() - 20, 0, 0, 0)
            painter.drawPixmap(button_rect, self.button_icon.pixmap(20, 20))

    def editorEvent(self, event, model, option, index):
        if index.column() == 3 and event.type() == QEvent.MouseButtonRelease:
            button_rect = option.rect.adjusted(option.rect.width() - 20, 0, 0, 0)
            if button_rect.contains(event.pos()):
                self.show_password[index] = not self.show_password.get(index, False)
                model.dataChanged.emit(index, index)
                if self.show_password[index]:
                    self.timer.start(3000)  # Start timer for 3 seconds
                else:
                    self.timer.stop()  # Stop the timer
                return True
        return super().editorEvent(event, model, option, index)

    def hide_password(self):
        for index in self.show_password.keys():
            self.show_password[index] = False
            index.model().dataChanged.emit(index, index)

    def createEditor(self, parent, option, index):
        if index.column() == 1:  # Column "Name"
            editor = QTextEdit(parent)
            return editor
        elif index.column() == 4:  # Column "Role"
            editor = QComboBox(parent)
            editor.addItems(self.roles)
            return editor
        else:
            return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if index.column() == 1:  # Column "Name"
            editor.setPlainText(index.data())
        elif index.column() == 4:  # Column "Role"
            editor.setCurrentText(index.data())
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if index.column() == 1:  # Column "Name"
            model.setData(index, editor.toPlainText())
        elif index.column() == 4:  # Column "Role"
            model.setData(index, editor.currentText())
        else:
            super().setModelData(editor, model, index)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.tableView = QTableView(self)
        self.layout.addWidget(self.tableView)

        columns = ["ID", "Name", "Username", "Password", "Role"]
        data = [
            [1, "John", "john123", "password1", "ADMIN"],
            [2, "Alice", "alice456", "password2", "STUDENT"],
            [3, "Bob", "bob789", "password3", "TEACHER"],
        ]

        editable_columns = [1, 3, 4]  # Columns "Name", "Password", and "Role" are editable
        self.model = CustomTableModel(data, columns, editable_columns)
        self.tableView.setModel(self.model)
        self.tableView.setItemDelegate(CustomDelegate())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Table View Example")
    window.setGeometry(100, 100, 800, 400)
    window.show()
    sys.exit(app.exec_())

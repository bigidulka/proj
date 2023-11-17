from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QTableView, QVBoxLayout, 
                             QMessageBox, QDialog, QLineEdit, QHBoxLayout, QFormLayout, QComboBox,
                             QAbstractItemView, QItemDelegate, QStyle, QStyleOptionButton, QApplication, QHeaderView, QFrame, QStyledItemDelegate)
from PyQt5.QtCore import Qt, QModelIndex, pyqtSignal, QAbstractTableModel, QEvent, QSize, QSortFilterProxyModel
from PyQt5.QtGui import QIcon

class TableModel(QAbstractTableModel):
    def __init__(self, columns, data, sortable_columns=None, editable_columns=None):
        super().__init__()
        self.load_data(data)
        self.columns = columns
        self.sortable_columns = sortable_columns if sortable_columns is not None else []
        self._editable_columns = editable_columns or []

        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.proxyModel.setSourceModel(self)
        self.proxyModel.sort(0, Qt.AscendingOrder)

    def load_data(self, data):
        self._data = [list(item) for item in data]
        
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            row = index.row()
            col = index.column()
            if 0 <= row < len(self._data) and 0 <= col < len(self.columns):
                self._data[row][col] = value
                self.dataChanged.emit(index, index)
                return True
        return False

    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        return len(self.columns)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            return str(self._data[row][col])
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.columns[section]
        return None

    def flags(self, index):
        if index.column() in self._editable_columns:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def set_sortable_columns(self, sortable_columns):
        self.sortable_columns = sortable_columns

    def add_data(self, data):
        # Добавьте данные в модель и оповестите таблицу о изменениях
        self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
        self._data.append(data)
        self.endInsertRows()

    def remove_data(self, row):
        # Удалите данные из модели и оповестите таблицу о изменениях
        self.beginRemoveRows(QModelIndex(), row, row)
        del self._data[row]
        self.endRemoveRows()
    
    def create_table_view(self):
        self.tableView = QTableView()
        self.tableView.setModel(self.proxyModel)  # Set the proxy model as the view's model
        self.tableView.horizontalHeader().setSortIndicatorShown(True)
        self.tableView.horizontalHeader().sectionClicked.connect(self.headerClicked)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.setMouseTracking(True)
        return self.tableView

    def headerClicked(self, logicalIndex):
        if logicalIndex in self.sortable_columns:
            currentOrder = self.proxyModel.sortOrder()
            self.proxyModel.sort(logicalIndex, not currentOrder)
            self.tableView.horizontalHeader().setSortIndicatorShown(True)
            self.tableView.horizontalHeader().setSortIndicator(logicalIndex, currentOrder)
        else:
            self.tableView.horizontalHeader().setSortIndicatorShown(False)

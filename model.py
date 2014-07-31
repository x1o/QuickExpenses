from PyQt4.QtCore import *
from PyQt4.QtSql import *

__author__ = 'xio'

SECT_NUM = 5
EID, DATE, AMOUNT, NAME, COMMENT = range(SECT_NUM)
SECT_NAMES = {
    EID: 'Id',
    DATE: 'Date',
    AMOUNT: 'Amount',
    NAME: 'Name',
    COMMENT: 'Comment',
}
FORMAT = {
    0: '%Y',
    1: '%Y-%m',
    2: '%Y-%m-%d'
}


class ExpTreeItem(object):
    def __init__(self, data=None, parent=None):
        self.itemData = data
        self.parentItem = parent
        self.childItems = []

    def __repr__(self):
        return ('%s = %s') % tuple(self.itemData)

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row_idx):
        return self.childItems[row_idx]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        # return len(self.itemData)
        return 2

    def data(self, column_idx):
        return self.itemData[column_idx]

    def row(self):
        return self.parentItem.childItems.index(self) if self.parentItem else 0

    def parent(self):
        return self.parentItem if self.parentItem else 0


class ExpTreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(ExpTreeModel, self).__init__(parent)
        # self.table = QSqlTableModel(self)
        # self.table.setTable(tableName)
        # self.table.setEditStrategy(QSqlTableModel.OnFieldChange)
        # self.table.select()
        self.setFilter('')
        self._buildTree()

    def index(self, row, column, parent=QModelIndex()):
        branch = parent.internalPointer() if parent.isValid() else self.rootItem
        return self.createIndex(row, column, branch.child(row))

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem or parentItem == 0:
            return QModelIndex()
        else:
            return self.createIndex(parentItem.row(), 0, parentItem)

    def flags(self, index):
        if not index.isValid():
            return 0
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        # if not index.isValid() or role != Qt.DisplayRole:
        #     return QVariant()
        if index.isValid() and role == Qt.DisplayRole:
            return index.internalPointer().data(index.column())

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        header = ['Year/Month/Day/Exp.', 'Amount']
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return header[section]
        # else:
        #     return QVariant()

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        return parentItem.childCount()

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def setFilter(self, filter):
        if not filter:
            self.filter = "eId glob '*'"
        else:
            self.filter = filter
        print(self.filter)
        self._buildTree()
        self.emit(SIGNAL('dataChanged'))

    def _exql(self, query):
        q = QSqlQuery(query)
        q.next()
        return q

    def _buildTree(self):
        self.rootItem = ExpTreeItem()
        # FIXME: ugly
        year_q = QSqlQuery("""select distinct strftime('%%Y', date) from Expense
                              where %s
                              order by date""" % self.filter)
        year_q.exec_()
        while year_q.next():
            year = year_q.value(0)
            aggrAmount = self._exql("""select sum(amount) from Expense
                                       where strftime('%%Y', date) = '%s'
                                       and %s
                                       order by date""" % (year, self.filter)).value(0)
            yearItem = ExpTreeItem([year, aggrAmount], self.rootItem)
            print(yearItem)
            self.rootItem.appendChild(yearItem)
            month_q = QSqlQuery("""select distinct strftime('%%m', date) from Expense
                                   where strftime('%%Y', date) = '%s'
                                   and %s
                                   order by date""" % (year, self.filter))
            month_q.exec_()
            while month_q.next():
                month = month_q.value(0)
                aggrAmount = self._exql("""select sum(amount) from Expense
                                           where strftime('%%Y-%%m', date) = '%s-%s'
                                           and %s
                                           order by date""" % (year, month, self.filter)).value(0)
                monthItem = ExpTreeItem([month, aggrAmount], yearItem)
                print('  %s' % monthItem)
                yearItem.appendChild(monthItem)
                day_q = QSqlQuery("""select distinct strftime('%%d', date) from Expense
                                     where strftime('%%Y-%%m', date) = '%s-%s'
                                     and %s
                                     order by date""" % (year, month, self.filter))
                day_q.exec_()
                while day_q.next():
                    day = day_q.value(0)
                    aggrAmount = self._exql("""select sum(amount) from Expense
                                               where strftime('%%Y-%%m-%%d', date) = '%s-%s-%s'
                                               and %s
                                               order by date""" % (year, month, day, self.filter)).value(0)
                    dayItem = ExpTreeItem([day, aggrAmount], monthItem)
                    print('    %s' % dayItem)
                    monthItem.appendChild(dayItem)
                    exp_q = QSqlQuery("""select name, amount from Expense
                                         where date = '%s-%s-%s'
                                         and %s
                                         order by date""" % (year, month, day, self.filter))
                    exp_q.exec_()
                    while exp_q.next():
                        name = exp_q.value(0)
                        amount = exp_q.value(1)
                        expItem = ExpTreeItem([name, amount], dayItem)
                        print('      %s' % expItem)
                        dayItem.appendChild(expItem)

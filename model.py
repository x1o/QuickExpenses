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

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row_idx):
        return self.childItems[row_idx]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

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
        self.rootItem = ExpTreeItem()
        self._buildTree(self.rootItem)

    def flags(self, index):
        if not index.isValid():
            return 0
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid() or role != Qt.DisplayRole:
            return QVariant()
        query = "select sum(amount) from Expense where strftime('%s') = '%s'"
        q = QSqlQuery(query % (FORMAT[index['lvl']], index['name']))
        q.exec_()
        q.next()
        return q.value(0)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        return self.table.headerData(section, orientation, role)

    def rowCount(self, parent=QModelIndex()):
        query = "select count(distinct strftime('%s', date)) from Expense"
        level = parent.internalPointer()['lvl'] + 1 if parent.isValid() else 0
        q = QSqlQuery(query % FORMAT[level])
        q.exec_()
        q.next()
        return q.value(0)

    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return self.table.columnCount(parent, *args, **kwargs)

    def index(self, row, column, parent=QModelIndex()):
        query = "select distinct strftime('%s', date) from Expense order by date"
        level = parent.internalPointer()['lvl'] + 1 if parent.isValid() else 0
        parentName = parent.internalPointer()['name'] if parent.isValid() else ''
        q = QSqlQuery(query % FORMAT[level])
        q.exec_()
        q.next()
        for _ in range(row):
            q.next()
        return self.createIndex(row, column, {'lvl': level,
                                              'name': '%s-%s' %
                                                      (parentName, q.value(0)),
                                              'parent': parent,
                                              'row': row})

    def parent(self, index=QModelIndex()):
        if index.internalPointer()['lvl'] == 0:
            return QModelIndex()
        else:
            return self.createIndex(index['parent']['row'], 0, index['parent'])

    def _exql(self, query):
        q = QSqlQuery(query)
        q.next()
        return q

    def _buildTree(self, rootItem):
        # self.table.select()
        # for row_idx in range(self.table.rowCount()):
        #     data = self.table.data(self.createIndex(row_idx, ))
        # FIXME: ugly
        year_q = QSqlQuery("select distinct strftime('%Y', date) from Expense")
        year_q.exec_()
        while year_q.next():
            year = year_q.value(0)
            print(year)
            aggrAmount = self._exql("""select sum(amount) from Expense
                                       where strftime('%%Y', date) = '%s'""" % year).value(0)
            print(aggrAmount)
            yearItem = ExpTreeItem([year, aggrAmount], rootItem)
            rootItem.appendChild(yearItem)
            month_q = QSqlQuery("""select distinct strftime('%%m', date) from Expense
                                   where strftime('%%Y', date) = '%s'""" % year)
            month_q.exec_()
            while month_q.next():
                month = month_q.value(0)
                aggrAmount = self._exql("""select sum(amount) from Expense
                                           where strftime('%%Y-%%m', date) = '%s-%s'""" % (year,month)).value(0)
                monthItem = ExpTreeItem([month, aggrAmount], yearItem)
                yearItem.appendChild(monthItem)
                day_q = QSqlQuery("""select distinct strftime('%%d', date) from Expense
                                   where strftime('%%Y-%%m', date) = '%s-%s'""" % (year, month))
                day_q.exec_()
                while day_q.next():
                    day = day_q.value(0)
                    aggrAmount = self._exql("""select sum(amount) from Expense
                            where strftime('%%Y-%%m-%%d', date) = '%s-%s-%s'""" % (year, month, day)).value(0)
                    dayItem = ExpTreeItem([day, aggrAmount], monthItem)
                    monthItem.appendChild(dayItem)
                    exp_q = QSqlQuery("select name, amount from Expense where date = '%s-%s-%s'" % (year, month, day))
                    exp_q.exec_()
                    while exp_q.next():
                        name = exp_q.value(0)
                        amount = exp_q.value(1)
                        expItem = ExpTreeItem([name, amount], dayItem)
                        dayItem.appendChild(expItem)

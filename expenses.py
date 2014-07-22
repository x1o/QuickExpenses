from PyQt4.QtCore import *
from PyQt4.QtSql import *

SECT_NUM = 5
EID, DATE, AMOUNT, NAME, COMMENT = range(SECT_NUM)
SECT_NAMES = {
    EID: 'Id',
    DATE: 'Date',
    AMOUNT: 'Amount',
    NAME: 'Name',
    COMMENT: 'Comment',
}

__author__ = 'Dmitry Zotikov'


class Expense(object):
    def __init__(self, eid, date, amount, name=None, tags=None, comment=None):
        self.eid = eid
        self.date = date
        self.amount = amount    # everything is stored in RURs internally
        self.name = name
        self.tags = tags
        self.comment = comment

    def __repr__(self):
        return '%s: %s (%s)' % (self.date, self.amount, self.name)

    def __lt__(self, other):
        # return self.date < other.date
        return self.eid < other.eid


class Tag(object):
    def __init__(self, name):
        self.name = name

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        return self.name == other

    def __repr__(self):
        return self.name

    def __hash__(self):
        return super(Tag, self).__hash__()


class ExpenseModel(QAbstractTableModel):
    def __init__(self):
        super(ExpenseModel, self).__init__()
        self.expenses = []
        self.tags = set()

    def sortByAttr(self, attr):
        self.expenses = sorted(self.expenses, key=lambda el: getattr(el, attr))
        self.reset()    # populates the table

    def load(self):
        self.expenses = []
        self.tags = set()

        query = QSqlQuery('select name from Tag')
        while query.next():
            self.tags.add(Tag(query.value(0)))

        query = QSqlQuery('select eId, date, amount, name, comments from Expense')
        while query.next():
            eid = query.value(EID)
            date = QDate(*[int(field) for field in query.value(DATE).split('-')])
            amount = query.value(AMOUNT)
            name = query.value(NAME) or ''
            comment = query.value(COMMENT) or ''
            tags = set()
            subq = QSqlQuery('select name from TaggedExpense where eId = %s' % eid)
            while subq.next():
                tag = subq.value(0)
                tags.add()
                self.tags.add(tag)
            self.expenses.append(Expense(eid, date, amount, name, tags, comment))

        self.dirty = False

    # --- Reading ---

    def data(self, index, role=Qt.DisplayRole):
        if (not index.isValid() or
            not (0 <= index.row() < len(self.expenses))):
            print('Invalid index!')
            return None
        expense = self.expenses[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            if column == EID:
                return expense.eid
            elif column == DATE:
                return expense.date.toString('dd.MM.yyyy')
            elif column == AMOUNT:
                return expense.amount
            elif column == NAME:
                return expense.name
            elif column == COMMENT:
                return expense.comment
            # elif column == TAGS:
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignLeft|Qt.AlignVCenter)
            return int(Qt.AlignRight|Qt.AlignVCenter)
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return SECT_NAMES[section]
        return int(section + 1)

    def rowCount(self, index=QModelIndex()):
        return len(self.expenses)

    def columnCount(self, index=QModelIndex()):
        return SECT_NUM

    # --- Writing ---

    # def flags(self, index=QModelIndex()):
    #     raise NotImplementedError

    def setData(self, QModelIndex, p_object, int_role=None):
        raise NotImplementedError

    def insertRows(self, p_int, p_int_1, QModelIndex_parent=None, *args, **kwargs):
        raise NotImplementedError

    def removeRows(self, p_int, p_int_1, QModelIndex_parent=None, *args, **kwargs):
        raise NotImplementedError

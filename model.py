from PyQt4.QtCore import *

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
    def __init__(self, tableModel, parent=None):
        super(ExpTreeModel, self).__init__(parent)
        self.table = tableModel
        self.buildTree()

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

    def buildTree(self):
        def buildTreeDict():
            treeDict = {}
            for row_idx in range(self.table.rowCount()):
                item = []
                for col_idx in (DATE, AMOUNT, NAME):
                    item.append(self.table.data(self.createIndex(row_idx, col_idx)))
                dict_ptr = treeDict
                for period in item[0].split('-'):
                    if not period in dict_ptr:
                        dict_ptr[period] = [{}, item[1]]
                    else:
                        dict_ptr[period][1] += item[1]
                    dict_ptr = dict_ptr[period][0]
                dict_ptr[item[2]] = item[1]
            return treeDict

        def processTreeDict(treeDict, parent, level):
            for period in sorted(treeDict):
                amount = treeDict[period] if level == 0 else treeDict[period][1]
                item = ExpTreeItem([period, amount], parent)
                parent.appendChild(item)
                if level != 0:
                    processTreeDict(treeDict[period][0], item, level-1)

        self.rootItem = ExpTreeItem()
        processTreeDict(buildTreeDict(), self.rootItem, 3)

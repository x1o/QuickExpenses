# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/dbdisplayform.ui'
#
# Created: Thu Jul 31 16:42:13 2014
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_dbDisplayForm(object):
    def setupUi(self, dbDisplayForm):
        dbDisplayForm.setObjectName(_fromUtf8("dbDisplayForm"))
        dbDisplayForm.resize(673, 441)
        self.gridLayout_3 = QtGui.QGridLayout(dbDisplayForm)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.splitter = QtGui.QSplitter(dbDisplayForm)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setContentsMargins(-1, -1, 9, 0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.dbDisplayTabWidget = QtGui.QTabWidget(self.layoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dbDisplayTabWidget.sizePolicy().hasHeightForWidth())
        self.dbDisplayTabWidget.setSizePolicy(sizePolicy)
        self.dbDisplayTabWidget.setObjectName(_fromUtf8("dbDisplayTabWidget"))
        self.treeViewTab = QtGui.QWidget()
        self.treeViewTab.setObjectName(_fromUtf8("treeViewTab"))
        self.gridLayout = QtGui.QGridLayout(self.treeViewTab)
        self.gridLayout.setContentsMargins(-1, -1, 9, 9)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.expensesTreeView = QtGui.QTreeView(self.treeViewTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.expensesTreeView.sizePolicy().hasHeightForWidth())
        self.expensesTreeView.setSizePolicy(sizePolicy)
        self.expensesTreeView.setObjectName(_fromUtf8("expensesTreeView"))
        self.expensesTreeView.header().setCascadingSectionResizes(True)
        self.gridLayout.addWidget(self.expensesTreeView, 0, 0, 1, 1)
        self.dbDisplayTabWidget.addTab(self.treeViewTab, _fromUtf8(""))
        self.tableViewTab = QtGui.QWidget()
        self.tableViewTab.setObjectName(_fromUtf8("tableViewTab"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tableViewTab)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.expensesTableView = QtGui.QTableView(self.tableViewTab)
        self.expensesTableView.setAlternatingRowColors(True)
        self.expensesTableView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.expensesTableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.expensesTableView.setObjectName(_fromUtf8("expensesTableView"))
        self.gridLayout_2.addWidget(self.expensesTableView, 1, 0, 1, 1)
        self.dbDisplayTabWidget.addTab(self.tableViewTab, _fromUtf8(""))
        self.verticalLayout_2.addWidget(self.dbDisplayTabWidget)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.deselectAllExpensesButton = QtGui.QPushButton(self.layoutWidget)
        self.deselectAllExpensesButton.setObjectName(_fromUtf8("deselectAllExpensesButton"))
        self.horizontalLayout.addWidget(self.deselectAllExpensesButton)
        self.selectAllExpensesButton = QtGui.QPushButton(self.layoutWidget)
        self.selectAllExpensesButton.setObjectName(_fromUtf8("selectAllExpensesButton"))
        self.horizontalLayout.addWidget(self.selectAllExpensesButton)
        self.deleteButton = QtGui.QPushButton(self.layoutWidget)
        self.deleteButton.setObjectName(_fromUtf8("deleteButton"))
        self.horizontalLayout.addWidget(self.deleteButton)
        self.filterButton = QtGui.QPushButton(self.layoutWidget)
        self.filterButton.setCheckable(True)
        self.filterButton.setChecked(True)
        self.filterButton.setObjectName(_fromUtf8("filterButton"))
        self.horizontalLayout.addWidget(self.filterButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.tagsGroupBox = QtGui.QGroupBox(self.splitter)
        self.tagsGroupBox.setFlat(True)
        self.tagsGroupBox.setObjectName(_fromUtf8("tagsGroupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.tagsGroupBox)
        self.verticalLayout.setContentsMargins(-1, -1, -1, 0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tagsListView = QtGui.QListView(self.tagsGroupBox)
        self.tagsListView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tagsListView.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.tagsListView.setSelectionRectVisible(True)
        self.tagsListView.setObjectName(_fromUtf8("tagsListView"))
        self.verticalLayout.addWidget(self.tagsListView)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.deselectAllTagsButton = QtGui.QPushButton(self.tagsGroupBox)
        self.deselectAllTagsButton.setObjectName(_fromUtf8("deselectAllTagsButton"))
        self.horizontalLayout_2.addWidget(self.deselectAllTagsButton)
        self.selectAllTagsButton = QtGui.QPushButton(self.tagsGroupBox)
        self.selectAllTagsButton.setObjectName(_fromUtf8("selectAllTagsButton"))
        self.horizontalLayout_2.addWidget(self.selectAllTagsButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout_3.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(dbDisplayForm)
        self.dbDisplayTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(dbDisplayForm)

    def retranslateUi(self, dbDisplayForm):
        dbDisplayForm.setWindowTitle(_translate("dbDisplayForm", "Form", None))
        self.dbDisplayTabWidget.setTabText(self.dbDisplayTabWidget.indexOf(self.treeViewTab), _translate("dbDisplayForm", "Tree view", None))
        self.dbDisplayTabWidget.setTabText(self.dbDisplayTabWidget.indexOf(self.tableViewTab), _translate("dbDisplayForm", "Table view", None))
        self.deselectAllExpensesButton.setText(_translate("dbDisplayForm", "Deselect All", None))
        self.selectAllExpensesButton.setText(_translate("dbDisplayForm", "Select All", None))
        self.deleteButton.setText(_translate("dbDisplayForm", "Delete", None))
        self.filterButton.setText(_translate("dbDisplayForm", "Filter...", None))
        self.tagsGroupBox.setTitle(_translate("dbDisplayForm", "Tags to filter by:", None))
        self.deselectAllTagsButton.setText(_translate("dbDisplayForm", "Deselect All", None))
        self.selectAllTagsButton.setText(_translate("dbDisplayForm", "Select All", None))


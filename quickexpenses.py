import os
import sys
import logging as log
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
import model_old
import model
import ui.ui_inputdlg as ui_inputdlg
import ui.ui_dbdisplayform as ui_dbdisplayform

__author__ = 'Dmitry Zotikov'
__version__ = (0.1, 'alpha')
__app_name__ = 'QuickExpenses'
__organization__ = 'Priyatniye Melochi Soft'

DB_FILENAME = 'expenses.db'
INIT_DB_FILENAME = 'db_create.sql'

# TODO:
# * import / export csv; actions
# * custom delegate in table to edit tags
# * remember selections?
# * customize shortcuts
# * customize deletion warnings
# * add tags to the existing records
# * automatically suggest tags for the given name
# * drag and drop tags

# * same header for tree and table

# clear comment field on discard / add new
# add 'approx.' db field / checkbox?


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


class ExpTreeModel(QSqlTableModel):
    def __init__(self, data=None, parent=None):
        super(ExpTreeModel, self).__init__(parent)
        self.rootItem = ExpTreeItem(['ha', 'ho'])
        self._setupModelData(data.split('\n'), self.rootItem)

    def data(self, index, role):
        if not index.isValid() or role != Qt.DisplayRole:
            return QVariant()
        return index.internalPointer().data(index.column())

    def flags(self, index):
        if not index.isValid():
            return 0
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data(section)
        else:
            return QVariant()

    def index(self, row, column, parent=QModelIndex()):
        branch = parent.internalPointer() if parent.isValid() else self.rootItem
        return self.createIndex(row, column, branch.child(row))

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()
        else:
            return self.createIndex(parentItem.row(), 0, parentItem)

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
            self.rootItem.columnCount()

    def _setupModelData(self, lines, parent):
        pass


class InputDlg(QDialog, ui_inputdlg.Ui_inputDialog):
    def __init__(self, parent=None):
        super(InputDlg, self).__init__(parent)
        self.setupUi(self)
        self.expensesDateEdit.setDate(QDate.currentDate())
        self.commentsGroupBox.setVisible(False)

    @pyqtSignature('double')
    def on_amountDoubleSpinBox_valueChanged(self):
        self.addButton.setEnabled(self.amountDoubleSpinBox.value() > 0)

    @pyqtSignature('')
    def on_commentsButton_clicked(self):
        self.commentsGroupBox.setVisible(not self.commentsGroupBox.isVisible())

    @pyqtSignature('')
    def on_USDRadioButton_clicked(self):
        self.amountDoubleSpinBox.setPrefix('$ ')

    @pyqtSignature('')
    def on_RUBRadioButton_clicked(self):
        self.amountDoubleSpinBox.setPrefix('P ')

    @pyqtSignature('')
    def on_selectAllTagsButton_clicked(self):
        self.tagsListView.selectAll()
        self.tagsListView.setFocus()

    @pyqtSignature('')
    def on_deselectAllTagsButton_clicked(self):
        self.tagsListView.clearSelection()

    @pyqtSignature('')
    def on_discardButton_clicked(self):
        self.expensesDateEdit.setDate(QDate.currentDate())
        self.amountDoubleSpinBox.setValue(0)
        self.amountDoubleSpinBox.setPrefix('P ')
        self.RUBRadioButton.setChecked(True)
        self.nameLineEdit.clear()
        self.on_deselectAllTagsButton_clicked()
        self.commentsPlainTextEdit.clear()
        self.amountDoubleSpinBox.setFocus()


class DBDisplayForm(QDialog, ui_dbdisplayform.Ui_dbDisplayForm):
    def __init__(self, parent=None):
        super(DBDisplayForm, self).__init__(parent)
        self.setupUi(self)

    @pyqtSignature('')
    def on_filterButton_clicked(self):
        self.tagsGroupBox.setVisible(not self.tagsGroupBox.isVisible())

    @pyqtSignature('')
    def on_selectAllTagsButton_clicked(self):
        self.tagsListView.selectAll()
        self.tagsListView.setFocus()

    @pyqtSignature('')
    def on_deselectAllTagsButton_clicked(self):
        self.tagsListView.clearSelection()

    @pyqtSignature('')
    def on_selectAllExpensesButton_clicked(self):
        self.expensesTableView.selectAll()
        self.expensesTableView.setFocus()

    @pyqtSignature('')
    def on_deselectAllExpensesButton_clicked(self):
        self.expensesTableView.clearSelection()


class QuickExpensesForm(QMainWindow):
    def __init__(self, parent=None):
        super(QuickExpensesForm, self).__init__(parent)

        self.is_dirty = False

        self.tagsModel = QSqlTableModel(self)
        self.tagsModel.setTable('Tag')
        self.tagsModel.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.tagsModel.select()

        self.expTableModel = QSqlTableModel(self)
        self.expTableModel.setTable('Expense')
        self.expTableModel.select()
        self.expTableModel.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.expTableModel.setSort(0, Qt.AscendingOrder)
        for section in model_old.SECT_NAMES:
            self.expTableModel.setHeaderData(section, Qt.Horizontal,
                                        model_old.SECT_NAMES[section])

        self.expTreeModel = model.ExpTreeModel('Expense', self)

        self.taggedExpModel = QSqlTableModel(self)
        self.taggedExpModel.setTable('TaggedExpense')
        self.taggedExpModel.select()

        self.inputDialog = InputDlg()
        self.inputDialog.tagsListView.setModel(self.tagsModel)
        self.connect(self.inputDialog.addButton,
                     SIGNAL('clicked()'), self.addRecord)
        self.connect(self.inputDialog.newTagButton,
                     SIGNAL('clicked()'), self.addTag)
        self.connect(self.inputDialog.deleteTagButton,
                     SIGNAL('clicked()'), self.deleteTag)

        self.dbDisplayForm = DBDisplayForm()
        self.dbDisplayForm.tagsListView.setModel(self.tagsModel)
        self.dbDisplayForm.expensesTableView.setModel(self.expTableModel)
        # self.dbDisplayForm.tagsListView.selectAll()
        self.dbDisplayForm.expensesTableView.hideColumn(model_old.EID)
        self.dbDisplayForm.expensesTableView.horizontalHeader().setStretchLastSection(True)
        self.dbDisplayForm.expensesTableView.horizontalHeader().setSortIndicatorShown(True)

        self.dbDisplayForm.expensesTreeView.setModel(self.expTreeModel)
        treeHeader = QHeaderView(Qt.Horizontal)
        treeHeader.setStretchLastSection(True)
        treeHeader.setSortIndicatorShown(True)
        self.dbDisplayForm.expensesTreeView.setHeader(treeHeader)
        for column in (model_old.EID, model_old.DATE, model_old.COMMENT):
            self.dbDisplayForm.expensesTreeView.hideColumn(column)
        self.dbDisplayForm.expensesTreeView.header().moveSection(model_old.NAME, model_old.AMOUNT)

        # self.dbDisplayForm.expensesTreeView.setModel()
        # self.dbDisplayForm.expensesTreeView.setSelectionModel(
        #     self.dbDisplayForm.expensesTableView.selectionModel()
        # )

        self.connect(self.dbDisplayForm.expensesTableView.horizontalHeader(),
                     SIGNAL('sectionClicked(int)'),
                     self.sortTable)
        self.connect(self.dbDisplayForm.deleteButton,
                     SIGNAL('clicked()'), self.deleteRecords)
        self.connect(self.dbDisplayForm.tagsListView.selectionModel(),
                     SIGNAL('selectionChanged(QItemSelection, QItemSelection)'),
                     lambda: self.filterBySelection(self.dbDisplayForm.tagsListView))
        self.connect(self.dbDisplayForm.expensesTableView.selectionModel(),
                     SIGNAL('selectionChanged(QItemSelection, QItemSelection)'),
                     self.updateStatusBarAmount)

        # self.mapper = QDataWidgetMapper(self)
        # self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        # self.mapper.setModel(self.model)
        # self.mapper.addMapping(self.inputDialog.nameLineEdit, expenses.NAME)
        # self.mapper.toFirst()

        self.connect(QShortcut(QKeySequence('Shift+Return'), self),
                     SIGNAL('activated()'),
                     self.addRecord)

        # --- Actions ---

        quitAction = self.createAction('&Quit', self.close, QKeySequence.Quit,
                                       QIcon.fromTheme('edit-undo'),
                                       'Quit the application')
        helpAboutAction = self.createAction('A&bout',self.helpAbout,
                                            icon=QIcon.fromTheme('application-exit'),
                                            tip='About the application')

        # --- Menubars ---

        fileMenu = self.menuBar().addMenu('&File')
        fileMenu.addAction(quitAction)

        helpMenu = self.menuBar().addMenu('&Help')
        helpMenu.addAction(helpAboutAction)

        # --- Toolbar ---

        # fileToolBar = self.addToolBar('File')
        # fileToolBar.setObjectName('FileToolBar')
        # fileToolBar.addAction(quitAction)
        #
        # helpToolBar = self.addToolBar('Help')
        # helpToolBar.setObjectName('HelpToolBar')
        # helpToolBar.addAction(hel pAboutAction)

        self.status = self.statusBar()
        self.status.showMessage('Ready')

        self.filterBySelection(self.dbDisplayForm.tagsListView)

        self.mainSplitter = QSplitter(Qt.Horizontal)
        self.mainSplitter.addWidget(self.inputDialog)
        self.mainSplitter.addWidget(self.dbDisplayForm)
        self.setCentralWidget(self.mainSplitter)
        self.setWindowTitle('%s v. %s' % (__app_name__, version(True)))
        self.restore_settings()
        # QTimer.singleShot(0, self.initialLoad) # and proceed to form.show(); when it's done, keep loading.

    def filterBySelection(self, view):
        tags = ','.join("'%s'" % index.data() for index in view.selectedIndexes())
        if not tags:
            filter_expr = ''
        else:
            q = QSqlQuery()
            q.exec_('select distinct eId from TaggedExpense where name in (%s)' % tags)
            eids = []
            while q.next():
                eids.append(str(q.value(0)))
            filter_expr = 'eId in (%s)' % ','.join(eids)
        self.expTableModel.setFilter(filter_expr)
        self.resizeColumns()

    def updateStatusBarAmount(self):
        view = self.dbDisplayForm.expensesTableView
        totalAmount = sum(index.data() for index in view.selectedIndexes()
                          if index.column() == model_old.AMOUNT)
        self.status.showMessage('Total amount selected: %s' % totalAmount)

    def resizeColumns(self):
        for column in (model_old.EID, model_old.DATE, model_old.AMOUNT,
                       model_old.NAME, model_old.COMMENT):
            self.dbDisplayForm.expensesTableView.resizeColumnToContents(column)

        for column in (model_old.AMOUNT, model_old.NAME):
            self.dbDisplayForm.expensesTreeView.resizeColumnToContents(column)

    def sortTable(self, section):
        self.expTableModel.sort(section, Qt.AscendingOrder)
        # self.resizeColumns()

    def addRecord(self):
        if self.inputDialog.amountDoubleSpinBox.value() == 0:
            return None
        class DBInsertRowError(Exception): pass

        record_dict = {}
        record_dict['date'] = (self.inputDialog.expensesDateEdit.date(),
                               QVariant.Date)
        record_dict['amount'] = (self.inputDialog.amountDoubleSpinBox.value(),
                                 QVariant.Double)
        record_dict['name'] = (self.inputDialog.nameLineEdit.text(),
                               QVariant.String)
        record_dict['comments'] = (self.inputDialog.commentsPlainTextEdit.document().toPlainText(),
                                   QVariant.String)

        record = QSqlRecord()
        for index in record_dict:
            record.append(QSqlField(index, record_dict[index][1]))
            record.setValue(index, record_dict[index][0])

        if not self.expTableModel.insertRecord(-1, record):
            raise(DBInsertRowError)

        # FIXME: this is not thread-safe I guess...
        q = QSqlQuery('select max(eId) from %s' % self.expTableModel.tableName())
        q.next()
        eId = q.value(0)
        tags = [tag.data() for tag in self.inputDialog.tagsListView.selectedIndexes()]
        for tag in tags:
            record = QSqlRecord()
            record.append(QSqlField('name', QVariant.String))
            record.append(QSqlField('eId', QVariant.Int))
            record.setValue('name', tag)
            record.setValue('eId', eId)
            if not self.taggedExpModel.insertRecord(-1, record):
                raise(DBInsertRowError)

        self.resizeColumns()
        self.inputDialog.nameLineEdit.clear()
        self.inputDialog.amountDoubleSpinBox.setFocus()

    def deleteRecords(self):
        if QMessageBox.question(self, 'Delete records',
                             '''<p>Selected records will be <b>permanently</b>
                             deleted from the database
                             <p> Delete selected records?''',
                             QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            sm = self.dbDisplayForm.expensesTableView.selectionModel()
            i = 0
            for index in sm.selectedRows():
                self.expTableModel.removeRows(index.row() - i, 1)
                i += 1

    def addTag(self):
        q = QSqlQuery('select count(*) from %s where name is null' %
                      self.tagsModel.tableName())
        q.next()
        if q.value(0) > 0:
            self.status.showMessage('Already added an unnamed tag! '
                                    'Please, rename it instead.')
        else:
            record = QSqlRecord()
            record.append(QSqlField('name', QVariant.String))
            record.setValue('name', '')
            self.tagsModel.insertRecord(-1, record)
        self.inputDialog.tagsListView.edit(self.tagsModel.index(0, 0))

    def deleteTag(self):
        tag_rows = [tag_idx.row() for tag_idx in self.inputDialog.tagsListView.selectedIndexes()]
        i = 0
        for row in sorted(tag_rows):
            self.tagsModel.removeRows(row - i, 1)
            i += 1

    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal='triggered()'):
        action = QAction(text, self)
        # see http://standards.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
        # if icon is not None:
        #     action.setIcon(QIcon(":/{}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def helpAbout(self):
        QMessageBox.about(self, __app_name__,
                '''<b>%s</b> version %s
                <p>(\u2184) %s, 2014
                <p>May the Force be with you.''' % (__app_name__,
                                                   version(True),
                                                   __author__))

    def restore_settings(self):
        settings = QSettings()
        self.restoreGeometry(settings.value('MainWindow/Geometry', QByteArray()))
        self.restoreState(settings.value('MainWindow/State', QByteArray()))
        self.mainSplitter.restoreState(settings.value('mainSplitter', QByteArray()))
        self.dbDisplayForm.splitter.restoreState(settings.value('splitter',
                                                                         QByteArray()))

    def save_settings(self):
        settings = QSettings()
        settings.setValue('MainWindow/Geometry', self.saveGeometry())
        settings.setValue('MainWindow/State', self.saveState())
        settings.setValue('mainSplitter', self.mainSplitter.saveState())
        settings.setValue('splitter',
                          self.dbDisplayForm.splitter.saveState())

    def closeEvent(self, event):
        # FIXME: quitting the app should be handled via event interception
        if self.okToContinue():
            self.save_settings()
            event.accept()
        else:
            event.ignore()

    def okToContinue(self):
        if self.is_dirty:
            reply = QMessageBox.question(self,
                                         'Really quit?',
                                         'Edit in progress -- still exit?',
                                         QMessageBox.Yes | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                return True
            elif reply == QMessageBox.Cancel:
                return False
        else:
            return True


def create_db(fn):
    query = QSqlQuery()
    for init_query in (s.strip() for s in open(fn, 'r').read().split(';')):
        if init_query and not init_query.startswith('--'):
            if not query.exec_(init_query):
                log.warning('Query failed: %s' % init_query)
    return True


def version(label=False):
    if label:
        return '-'.join([str(el) for el in __version__])
    else:
        return __version__[0]


if __name__ == '__main__':
    log.basicConfig(level=log.INFO)

    app = QApplication(sys.argv)

    app.setApplicationName(__app_name__)
    app.setOrganizationName(__organization__)
    app.setApplicationVersion(version(True))

    db_filename = os.path.join(os.path.dirname(__file__), DB_FILENAME)
    db_create = not QFile.exists(db_filename)
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(db_filename)
    if not db.open():
        QMessageBox.warning(None, __app_name__,
                            'Database error: %s' % db.lastError().text)
        sys.exit(1)

    if db_create:
        if create_db(INIT_DB_FILENAME):
            log.info('Initial DB created.')
        else:
            msg = 'Failed to create DB.'
            QMessageBox.warning(None, __app_name__, msg)
            log.critical()
            sys.exit(1)

    q = QSqlQuery()
    q.exec_('pragma foreign_keys = on')

    form = QuickExpensesForm()
    form.show()
    app.exec_()

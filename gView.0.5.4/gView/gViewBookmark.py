import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
import json
import os
import uuid
import mari

mari_icon_path = mari.resources.path(mari.resources.ICONS)
bookmarkpref = '/usr/tmp/bkmrkFile.pref'

class MyTreeItem(QtGui.QTreeWidgetItem):
    def __init__(self, name):
        super(MyTreeItem, self).__init__()
        self.setText(0, name)
        self.setFlags(
                            QtCore.Qt.ItemIsEditable
                          | QtCore.Qt.ItemIsEnabled
                          | QtCore.Qt.ItemIsSelectable
                          | QtCore.Qt.ItemIsDropEnabled
                          | QtCore.Qt.ItemIsDragEnabled
                          )
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            pass

class MyDialog(QtGui.QTreeWidget):
    pathAdded = QtCore.Signal(str)
    itemMoved = QtCore.Signal()
    currentItems = []
    pathList = []
    def __init__(self):
        super(MyDialog, self).__init__()
        self.setMaximumWidth(250)

        self.setDragDropMode(self.InternalMove)
        self.installEventFilter(self)
        self.setColumnCount(1)
        self.setAlternatingRowColors(True)
        self.setIndentation(10)
        self.setHeaderHidden(True)
        self.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked)
        self.setDragEnabled(True)
        self.setSelectionMode(self.ExtendedSelection)
        self.itemChanged.connect(self.sortAllItems)
        self.itemMoved.connect(self.restoreExpandedState)
        #Style
        self.setStyleSheet("\
        QTreeWidget { alternate-background-color: rgb(105, 105, 105); } \
        ")

        #Context Menu
        self.menu = QtGui.QMenu()
        self.importAction = self.menu.addAction(QtGui.QIcon('%s/Palette.16x16.png' % mari_icon_path), 'New Group')
        #Connections
        self.importAction.triggered.connect(self.makeBlankItem)

    def eventFilter(self, sender, event):
        '''Detects when an item moves'''
        if (event.type() == QtCore.QEvent.ChildRemoved):
            self.itemMoved.emit()
        if (event.type() == QtCore.QEvent.ChildAdded):
            self.itemMoved.emit()
        return False # don't actually interrupt anything

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.removeBookmark()

    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

    def removeBookmark(self):
        for item in self.selectedItems():
            if not item.parent():
                index = self.indexOfTopLevelItem(item)
                self.takeTopLevelItem(index)
            else:
                index = item.parent().indexOfChild(item)
                item.parent().takeChild(index)

    def sortAllItems(self):
        self.sortItems(0, QtCore.Qt.AscendingOrder)

    def buildFromPath(self, path=None, mode='multi'):
        #path = self.customPath.text()
        pathList = []
        itemList = []

        #Top Directory
        rootName = os.path.basename(path)
        rootPath = path
        rootItem = MyTreeItem(rootName)
        rootItem.setData(0, 32, [None, rootName, rootPath])
        itemList.append(rootItem)
        self.addTopLevelItem(rootItem)

        if mode is 'multi':
            self.pathAdded.emit(rootPath)
            #Sub Directories
            for root, dirs, files in os.walk(path):
                for name in dirs:
                    if not name.startswith('.'):
                        parent = root
                        fullpath = os.path.join(root, name)
                        bookmarkData = [parent, name, fullpath]
                        parentItem = self.findParentItem(parent)
                        if parentItem:
                            newItem = MyTreeItem(name)
                            newItem.setData(0, 32, bookmarkData)
                            parentItem.insertChild(0, newItem)
                            itemList.append(newItem)
                        self.pathAdded.emit(fullpath)
        #Build IDs
        self.setItemUUID(itemList)
        self.setParentUUID()

        #Sort and Expand
        self.sortAllItems()

    def makeBlankItem(self):
        inputText, ok = QtGui.QInputDialog.getText(self, 'Create New Group', 'Enter name:')

        if ok:
            #Keep Hierarchy
            for item in self.selectedItems():
                if item.childCount() >= 1:
                    for index in range(item.childCount()):
                        childItem = item.child(index)
                        childItem.setSelected(False)

            #"Blank" Item
            name = str(inputText)
            UUID = uuid.uuid4().hex
            bookmarkData = [None, name, UUID, None, True]
            blankItem = MyTreeItem(name)
            blankItem.setData(0, 32, bookmarkData)
            self.addTopLevelItem(blankItem)

            #Group Items
            for item in self.selectedItems():
                if item.parent():
                    item.parent().removeChild(item)
                else:
                    self.invisibleRootItem().removeChild(item)
                blankItem.insertChild(0, item)

    def findParentItem(self, itemParent):
        it = QtGui.QTreeWidgetItemIterator(self)
        while it.value():
            item = it.value()
            itemData = item.data(0, 32)
            if itemData[2] == itemParent:
                return item
            it += 1

    def setItemUUID(self, itemList):
        for item in itemList:
            name = item.text(0)
            parentUUID = None
            UUID = uuid.uuid4().hex
            fullPath = item.data(0, 32)[2]
            item.setData(0, 32, [parentUUID, name, UUID, fullPath, None])
            item.setExpanded(True)

    def setParentUUID(self):
        it = QtGui.QTreeWidgetItemIterator(self)
        while it.value():
            item = it.value()
            name = item.text(0)
            UUID = item.data(0, 32)[2]
            fullPath = item.data(0, 32)[3]
            expandState = item.isExpanded()
            try:
                parentItem = item.parent()
                parentUUID = parentItem.data(0, 32)[2]
            except:
                parentUUID = None
            item.setData(0, 32, [parentUUID, name, UUID, fullPath, expandState])
            it += 1

    def restoreExpandedState(self):
        it = QtGui.QTreeWidgetItemIterator(self)
        while it.value():
            item = it.value()
            expandState = item.data(0, 32)[4]
            item.setExpanded(expandState)
            it += 1

    def buildTreeItems(self):
        json_data = open(bookmarkpref)
        data = json.load(json_data)

        for item in data:
            parentUUID = item[0]
            name = item[1]
            UUID = item[2]
            fullPath = item[3]
            expandState = item[4]
            bookmarkData = [parentUUID, name, UUID, fullPath, expandState]
            parentItem = self.findParentItem(parentUUID)
            if parentItem:
                newItem = MyTreeItem(name)
                newItem.setData(0, 32, bookmarkData)
                parentItem.insertChild(0, newItem)
                newItem.setExpanded(expandState)
            else:
                rootItem = MyTreeItem(name)
                rootItem.setData(0, 32, bookmarkData)
                self.addTopLevelItem(rootItem)
                rootItem.setExpanded(expandState)
            if fullPath:
                self.pathAdded.emit(fullPath)

        #Sort
        self.sortAllItems()

    def printPath(self, path):
        print path

    def saveBookmarkFile(self):
        self.setParentUUID()
        dataList = []
        it = QtGui.QTreeWidgetItemIterator(self)
        while it.value():
            item = it.value()
            itemData = item.data(0, 32)
            dataList.append(itemData)
            it += 1

        with open(bookmarkpref, 'w') as outfile:
            json.dump(dataList, outfile)

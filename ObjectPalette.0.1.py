#Object Palette 2.0

import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
import mari


activeBrush = QtGui.QBrush(QtGui.QColor(55,125,35,100))
unactiveBrush = QtGui.QBrush(QtGui.QColor(255,255,255,0))
mari_icon_path = mari.resources.path(mari.resources.ICONS)

def setMariGeo(name):
    global mariGeo
    mariGeo = mari.geo.find(name)

    
#class HoverButton(QtGui.QToolButton):
    #def __init__(self, iconpath):
        #super(HoverButton, self).__init__()
        #self.icon = QtGui.QIcon(iconpath)
        #self.setIcon(self.icon)
        
    #def enterEvent(self,event):
        ##print("Enter")
        ##self.setStyleSheet("background-color:#45b545;")
        #self.icon.Disabled
        #self.icon.Off

    #def leaveEvent(self,event):
        #self.setStyleSheet("background-color:yellow;")
        ##print("Leave") 

class ObjectVersions(QtGui.QTreeWidget):
    def __init__(self):
        super(ObjectVersions, self).__init__()

        self.setHeaderHidden(True)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

    def contextMenuEvent(self, event):
        if event.reason() == event.Mouse:
            pos = event.globalPos()
            item = self.itemAt(event.pos())
        if pos is not None and item:
            menu = QtGui.QMenu()
            if len(self.selectedItems()) < self.topLevelItemCount():
                removeAction = menu.addAction('Remove')
                removeAction.triggered.connect(self.removeItem)
            if self.topLevelItemCount() > 1 and len(self.selectedItems()) == 1:
                setCurrentAction = menu.addAction("Set Current")
                setCurrentAction.triggered.connect(self.setVersionCurrent)
            menu.exec_(pos)
        event.accept()

    def getCurrentItemName(self):
        return self.currentItem().text(0)

    def setVersionCurrent(self):
        versionName = self.getCurrentItemName()
        mariGeo.setCurrentVersion(versionName)
        self.setActiveItem()

    def removeItem(self):
        items = self.selectedItems()
        for selitem in items:
            versionName = selitem.text(0)
            mariGeo.removeVersion(versionName)
            index = self.indexOfTopLevelItem(selitem)
            self.takeTopLevelItem(index)
        self.setActiveItem()

    def setActiveItem(self):
        currentVersionName = mariGeo.currentVersion().name()
        it = QtGui.QTreeWidgetItemIterator(self)
        while it.value():
            item = it.value()
            itemName = item.text(0)
            if itemName == currentVersionName:
                item.setBackground(0, activeBrush)
            else:
                item.setBackground(0, unactiveBrush)
            it += 1

class ObjectList(QtGui.QWidget):
    def __init__(self):
        super(ObjectList, self).__init__()

        #Layouts
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        sortLayout = QtGui.QGridLayout()
        sortLayout.setColumnStretch(1, 1)
        objectToolbarLayout = QtGui.QHBoxLayout()
        self.setLayout(mainLayout)

        #Widgets
        sortedByLabel = QtGui.QLabel("Sorted by")
        sortedByCombo = QtGui.QComboBox()
        sortedByCombo.addItems(["None", "Name", "Version"])
        self.objectTree = QtGui.QTreeWidget()
        self.objectTree.setHeaderHidden(True)
        self.objectInfo = QtGui.QTreeWidget()
        self.objectInfo.setColumnCount(2)
        self.objectInfo.setHeaderHidden(True)
        self.objectVersions = ObjectVersions()
        objectAddBtn = QtGui.QToolButton()
        testIcon = QtGui.QIcon()
        testIcon.addPixmap(QtGui.QPixmap("%s/AddObject.png" % mari_icon_path, mode=testIcon.Disabled))
        #testIcon.addFile("%s/AddObject.png" % mari_icon_path, mode = QtGui.QIcon.Disabled, state = QtGui.QIcon.Off)
        objectAddBtn.setIcon(testIcon)
        #objectAddBtn.setIcon(QtGui.QIcon("%s/AddObject.png" % mari_icon_path, ))
        objectRemoveBt = QtGui.QToolButton()
        objectRemoveBt.setIcon(QtGui.QIcon("%s/RemoveObject.png" % mari_icon_path))

        #Populate Widgets
        sortLayout.addWidget(sortedByLabel, 0, 0)
        sortLayout.addWidget(sortedByCombo, 0, 1)
        objectToolbarLayout.addStretch()
        objectToolbarLayout.addWidget(objectAddBtn)
        objectToolbarLayout.addWidget(objectRemoveBt)
        mainLayout.addLayout(sortLayout)
        mainLayout.addWidget(self.objectTree)
        mainLayout.addLayout(objectToolbarLayout)

        #Connections
        objectAddBtn.clicked.connect(self.buildObjectInfo)
        self.objectTree.itemClicked.connect(self.showObjectInfo)
        self.objectTree.itemClicked.connect(self.showObjectVersions)

    def getSelectedItemInfo(self):
        item = self.objectTree.currentItem()
        name = item.text(0)
        metadata = item.data(0, 32)
        return item, name, metadata

    def buildObjectInfo(self):
        '''Creates item for each object in scene'''
        for geo in mari.geo.list():
            geoName = geo.name()

            #Get metadata
            metadata = {}
            metadataNames = geo.metadataNames()
            for name in metadataNames:
                value = geo.metadata(name)
                metadata[name] = value

            #Build and add items
            newTreeItem = QtGui.QTreeWidgetItem()
            newTreeItem.setText(0, geoName)
            newTreeItem.setData(0, 32, metadata)
            self.objectTree.addTopLevelItem(newTreeItem)

    def showObjectInfo(self):
        '''Displays currently selected objects attributes'''
        self.objectInfo.clear()
        selectedItem, selectedName, metadata = self.getSelectedItemInfo()
        setMariGeo(selectedName)
        mari.geo.setCurrent(mariGeo)
        for name, value in metadata.iteritems():
            newInfoItem = QtGui.QTreeWidgetItem()
            newInfoItem.setText(0, name)
            newInfoItem.setText(1, str(value))
            self.objectInfo.addTopLevelItem(newInfoItem)
        self.objectInfo.resizeColumnToContents(0)

    def showObjectVersions(self):
        '''Displays currently selected objects versions'''
        self.objectVersions.clear()
        selectedName = self.getSelectedItemInfo()[1]
        currentVersion = mariGeo.currentVersion().name()
        geoVersionList = mariGeo.versionList()

        for version in geoVersionList:
            versionName = version.name()
            newVersionItem = QtGui.QTreeWidgetItem()
            newVersionItem.setText(0, versionName)
            self.objectVersions.addTopLevelItem(newVersionItem)
            if versionName == currentVersion:
                newVersionItem.setBackground(0, activeBrush)


class ObjectPalette(QtGui.QWidget):
    def __init__(self):
        super(ObjectPalette, self).__init__()

        #Layouts
        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

        #Widgets
        infoSplitter = QtGui.QSplitter(self)
        infoSplitter.setOrientation(QtCore.Qt.Vertical)
        self.objectList = ObjectList()
        objectInfoTab = QtGui.QTabWidget()
        objectInfoTab.addTab(self.objectList.objectInfo, "Attributes")
        objectInfoTab.addTab(self.objectList.objectVersions, "Versions")
        infoSplitter.addWidget(self.objectList)
        infoSplitter.addWidget(objectInfoTab)

        #Populate Layouts
        mainLayout.addWidget(infoSplitter)

objPal = ObjectPalette()
newPalette = mari.palettes.create("TEST", objPal)

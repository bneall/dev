import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
import glob
import os
import mari

path = "C:\\temp\\gViewThumbnails\\C\\Users\\ben\\Documents\\Textures"
maxColumns = 6
itemHPad = 20
itemVPad = 10
itemSize = 210

class GScene(QtGui.QGraphicsScene):
    def __init__(self):
        super(GScene, self).__init__()
        #Background Color
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(95, 95, 95)))
        #Context Menu
        self.menu = QtGui.QMenu()
        self.importAction = self.menu.addAction("Import")

    def contextMenuEvent(self, event):
        self.menu.exec_(event.screenPos())

class GRectItem(QtGui.QGraphicsRectItem):
    def __init__(self, image_path):
        super(GRectItem, self).__init__()
        #Attributes
        self.setFlags(self.flags() | QtGui.QGraphicsItem.ItemIsSelectable)
        self.setToolTip(image_path)

        #Rect Settings
        self.setRect(0, 0, itemSize, itemSize)
        self.rectBrush = QtGui.QBrush(QtGui.QColor(100, 100, 100))
        self.rectPenBrush = QtGui.QBrush(QtGui.QColor(51, 51, 51))
        self.rectPen = QtGui.QPen(self.rectPenBrush, 1)
        self.setBrush(self.rectBrush)
        self.setPen(self.rectPen)
        
        #Pad Rect Settings
        self.setRect(0, 0, itemSize, itemSize)
        padRect = QtGui.QGraphicsRectItem()
        padRect.setPen(QtGui.QPen(self.rectPenBrush, 20))
        padRect.setParentItem(self)

        #Thumb Title Item
        thumbTitle = os.path.basename(image_path)
        #Title Size Check
        if len(thumbTitle) >= 36:
            thumbTitle = thumbTitle[:34]+'...'
        thumbTitleItem = QtGui.QGraphicsSimpleTextItem(thumbTitle)
        thumbTitleItem.setBrush(QtGui.QBrush(QtGui.QColor(200, 200, 200)))
        thumbTitleItem.setPos(0, itemSize)
        thumbTitleItem.setParentItem(self)

        #Thumb Image Item
        thumbImage = QtGui.QPixmap(image_path)
        thumbImgItem = QtGui.QGraphicsPixmapItem(thumbImage)
        thumbWidth = thumbImgItem.pixmap().width()
        thumbHeight = thumbImgItem.pixmap().height()
        thumbHOffset = (itemSize-thumbWidth)/2
        thumbVOffset = (itemSize-thumbHeight)/2
        thumbImgItem.setPos(thumbHOffset, thumbVOffset)
        thumbImgItem.setParentItem(self)

    def itemChange(self, change, value):
        '''Detect Selection'''
        if change == QtGui.QGraphicsItem.ItemSelectedChange:
            if value == True:
                self.setHighlite()
            if value == False:
                self.removeHighlite()
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
        '''Right Click Override'''
        if event.button() == QtCore.Qt.RightButton:
            pass

    def setHighlite(self):
        highlitePenBrush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        highlitePen = QtGui.QPen(highlitePenBrush, 3)
        self.setPen(highlitePen)

    def removeHighlite(self):
        self.setPen(self.rectPen)

class GView(QtGui.QWidget):
    vSceneSize = 0
    hSceneSize = 0
    items = 0
    def __init__(self):
        super(GView, self).__init__()
        self.setMinimumSize(1000,1000)

        layout = QtGui.QVBoxLayout()
        hlayout = QtGui.QHBoxLayout()
        self.setLayout(layout)

        self.gviewer = QtGui.QGraphicsView()
        self.gscene = GScene()
        self.gviewer.setInteractive(True)
        self.gviewer.setScene(self.gscene)
        self.gviewer.setAlignment( QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft )

        self.searchLine = QtGui.QLineEdit()
        self.columnSpin = QtGui.QSpinBox()
        self.button = QtGui.QPushButton('Add')
        self.button2 = QtGui.QPushButton('Fit')

        layout.addWidget(self.gviewer)
        layout.addLayout(hlayout)
        hlayout.addWidget(self.button2)
        hlayout.addWidget(self.searchLine)
        hlayout.addWidget(self.columnSpin)
        hlayout.addWidget(self.button)

        self.button.clicked.connect(self.createItems)
        self.button2.clicked.connect(self.fitColumnsMari)
        self.searchLine.textChanged.connect(self.sortItems)
        self.columnSpin.valueChanged.connect(self.setColumns)
        self.gscene.importAction.triggered.connect(self.importImages)

    def createItems(self):
        fileList =  sorted(glob.glob('%s/*' % path))
        for image in fileList:
            bgRectItem = GRectItem(image)
            self.gscene.addItem(bgRectItem)
            self.items += 1
            self.setPositions(bgRectItem)
        self.fitColumnsMari()

    def setPositions(self, item):
        item.setPos(self.hSceneSize, self.vSceneSize)
        if self.items % maxColumns:
            self.hSceneSize += itemSize+itemVPad
        else:
            self.vSceneSize += itemSize+itemHPad
            self.hSceneSize = 0
            
    def setColumns(self):
        global maxColumns
        maxColumns = self.columnSpin.value()
        self.sortItems()
    
    def fitColumnsMari(self):
        available_area = mari.app.canvasWidth()
        global maxColumns
        maxColumns = int(round(available_area/(itemSize+itemHPad)))
        self.columnSpin.setValue(maxColumns)
        self.sortItems()
    
    def sortItems(self):
        #Reset
        self.items = 0
        self.hSceneSize = 0
        self.vSceneSize = 0

        #List of Parent Items
        groupItems = []
        for item in self.gscene.items():
            if item.childItems():
                groupItems.append(item)
                item.setVisible(False)
                item.setPos(0,0)

        ##Reverse Group List
        groupItems = groupItems[::-1]
        #Display Only Items Matching Search
        for item in groupItems:
            searchText = self.searchLine.text()
            titleItem = item.childItems()[1]
            thumbName = titleItem.text().split(".")[0]
            if searchText.lower() in thumbName.lower():
                item.setVisible(True)
                self.items += 1
                self.setPositions(item)

        #Resize Scene
        autoRect = self.gscene.itemsBoundingRect()
        self.gscene.setSceneRect(autoRect)
        ##Scroll to top
        self.gviewer.ensureVisible(0.0,0.0,0.0,0.0)

        #Refresh UI
        self.gscene.update()
        QtCore.QCoreApplication.processEvents()

    def importImages(self):
        print 'fart'

gviewWidget = GView()
mari.app.addTab('gView', gviewWidget)

# GView().exec_()

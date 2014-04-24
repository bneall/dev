import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
import glob
import os

path = "/home/bneall/Pictures/test"
maxColumns = 4
itemPad = 20
itemSize = 210

class GScene(QtGui.QGraphicsScene):
    def __init__(self):
        super(GScene, self).__init__()
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(95, 95, 95)))
        self.menu = QtGui.QMenu()
        importAction = self.menu.addAction("Import")

    def printShit(self):
        print 'shit'

    def contextMenuEvent(self, event):
        try:
            selectedAction = self.menu.exec_(event.screenPos())
            selectedAction.triggered.connect(self.printShit)
        except:
            pass


class GRectItem(QtGui.QGraphicsRectItem):
    def __init__(self, image_path):
        super(GRectItem, self).__init__()
        self.setFlags(self.flags() | QtGui.QGraphicsItem.ItemIsSelectable | QtGui.QGraphicsItem.ItemIgnoresParentOpacity)
        self.setRect(0,0,itemSize,itemSize)
        self.rectBrush = QtGui.QBrush(QtGui.QColor(100, 100, 100))
        self.rectPenBrush = QtGui.QBrush(QtGui.QColor(80, 80, 80))
        self.rectPen = QtGui.QPen(self.rectPenBrush, 1)
        self.setBrush(self.rectBrush)
        self.setPen(self.rectPen)

        name = os.path.basename(image_path)
        thumbTitleItem = QtGui.QGraphicsSimpleTextItem(name)
        thumbTitleItem.setPos(0, itemSize)
        thumbTitleItem.setParentItem(self)

        image = QtGui.QPixmap(image_path)
        thumbImgItem = QtGui.QGraphicsPixmapItem(image)
        width = thumbImgItem.pixmap().width()
        height = thumbImgItem.pixmap().height()
        hoffset = (itemSize-width)/2
        voffset = (itemSize-height)/2
        thumbImgItem.setPos(hoffset, voffset)
        thumbImgItem.setParentItem(self)

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemSelectedChange:
            if value == True:
                self.setHighlite()
            if value == False:
                self.removeHighlite()
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    #def contextMenuEvent(self, event):
        #menu = QtGui.QMenu()
        #removeAction = menu.addAction("Remove")
        #markAction = menu.addAction("Mark")
        #selectedAction = menu.exec_(event.screenPos())

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            pass

    def setHighlite(self):
        highlitePenBrush = QtGui.QBrush(QtGui.QColor(221, 96, 0))
        highlitePen = QtGui.QPen(highlitePenBrush, 3)
        self.setPen(highlitePen)

    def removeHighlite(self):
        self.setPen(self.rectPen)

class GView(QtGui.QDialog):
    vSceneSize = 0
    hSceneSize = 0
    items = 0

    def __init__(self):
        super(GView, self).__init__()
        self.setMinimumSize(1000,1000)

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        self.gviewer = QtGui.QGraphicsView()
        self.gscene = GScene()
        self.gviewer.setInteractive(True)
        #self.gscene = QtGui.QGraphicsScene()
        self.gviewer.setScene(self.gscene)

        self.searchLine = QtGui.QLineEdit()
        self.button = QtGui.QPushButton('Add')
        self.button1 = QtGui.QPushButton('Filter')

        layout.addWidget(self.gviewer)
        layout.addWidget(self.searchLine)
        layout.addWidget(self.button)
        layout.addWidget(self.button1)

        self.button.clicked.connect(self.createItems)
        self.button1.clicked.connect(self.filterItems)
        self.searchLine.textChanged.connect(self.filterItems)


    def createItems(self):
        fileList =  sorted(glob.glob('%s/*' % path))
        for image in fileList:
            self.createItem(image)

    def createItem(self, image_path):
        #Thumbnail Container
        bgRectItem = GRectItem(image_path)
        self.gscene.addItem(bgRectItem)

        ##Thumbnail Image
        #name = os.path.basename(image_path)
        #image = QtGui.QPixmap(image_path)
        #thumbImgItem = QtGui.QGraphicsPixmapItem(image)

        ##Thumbnail Title
        #thumbTitleItem = QtGui.QGraphicsSimpleTextItem(name)
        #width = thumbImgItem.pixmap().width()
        #height = thumbImgItem.pixmap().height()
        #hoffset = (itemSize-width)/2
        #voffset = (itemSize-height)/2
        #thumbImgItem.setPos(hoffset, voffset)
        #thumbTitleItem.setPos(0, itemSize)

        ##Adding Thumbnail Group Item
        #thumbGrpItem = self.gscene.createItemGroup([bgRectItem, thumbImgItem, thumbTitleItem])
        #thumbGrpItem.setData(32, image_path)
        #thumbGrpItem.setFlags(thumbGrpItem.flags() | QtGui.QGraphicsItem.ItemIsSelectable)

        self.items += 1
        self.setPositions(bgRectItem, itemSize, itemSize)

    def setPositions(self, item, hoffset, voffset):
        item.setPos(self.hSceneSize, self.vSceneSize)

        if self.items % maxColumns:
            self.hSceneSize += hoffset+itemPad
        else:
            self.vSceneSize += voffset+itemPad
            self.hSceneSize = 0

    def filterItems(self):
        self.items = 0
        self.hSceneSize = 0
        self.vSceneSize = 0

        groupItems = []
        for item in self.gscene.items():
            if not item.group():
                groupItems.append(item)
                item.setVisible(False)
                item.setPos(0,0)

        #Reverse group list
        groupItems = groupItems[::-1]

        for item in groupItems:
            thumbItem = item.childItems()[1]
            titleItem = item.childItems()[2]
            hoffset = thumbItem.pixmap().width()
            voffset = thumbItem.pixmap().height()
            searchText = self.searchLine.text()
            thumbName = titleItem.text().split(".")[0]
            if searchText.lower() in thumbName.lower():
                item.setVisible(True)
                self.items += 1
                self.setPositions(item, itemSize, itemSize)

        QtCore.QCoreApplication.processEvents()

    def diagnostic(self):
        print "group items", self.items
        print "vertical scene size:", self.vSceneSize
        print "horizontal scene size", self.hSceneSize

GView().exec_()

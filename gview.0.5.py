import PySide.QtGui as QtGui

name = 'Dumb'
path = "C:\\Users\\ben\\Pictures\\dru10.jpg"
maxColumns = 4
itemPad = 20

class GThumbItem(QtGui.QGraphicsPixmapItem):
    def __init__(self, image):
        QtGui.QGraphicsPixmapItem.__init__(self)
        self.setPixmap(image)

    def mouseDoubleClickEvent(self, mouseEvent):
        self.setSelected(True)
        print 'fart'

class GView(QtGui.QDialog):
    vSceneSize = 0
    hSceneSize = 0
    items = 0

    def __init__(self):
        super(GView, self).__init__()
        
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        
        self.gviewer = QtGui.QGraphicsView()
        self.gviewer.setInteractive(True)
        self.gscene = QtGui.QGraphicsScene()
        self.gviewer.setScene(self.gscene)
        
        
        self.button = QtGui.QPushButton('Add')
        self.button1 = QtGui.QPushButton('Print')
        self.button2 = QtGui.QPushButton('ReList')
        
        layout.addWidget(self.gviewer)
        layout.addWidget(self.button)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        
        self.button.clicked.connect(self.createItem)
        self.button1.clicked.connect(self.diagnostic)
        self.button2.clicked.connect(self.reListItems)
    
    def createItem(self):
        #Thumbnail Image
        image = QtGui.QPixmap(path)
        thumbImgItem = GThumbItem(image)
        #Thumbnail Title
        thumbTitleItem = QtGui.QGraphicsSimpleTextItem(name)
        hoffset = thumbImgItem.pixmap().width()
        voffset = thumbImgItem.pixmap().height()
        thumbTitleItem.setPos(hoffset/2, voffset)
        #Adding Thumbnail Group Item
        thumbGrpItem = self.gscene.createItemGroup([thumbImgItem, thumbTitleItem])
        thumbGrpItem.setPos(self.hSceneSize, self.vSceneSize)
        thumbGrpItem.setFlags(thumbGrpItem.flags() | QtGui.QGraphicsItem.ItemIsSelectable)
        self.items += 1
        self.layoutControl(hoffset, voffset)

    def layoutControl(self, hoffset, voffset):
        #Column Control
        if self.items % maxColumns:
            self.hSceneSize += hoffset+itemPad
        else:
            self.vSceneSize += voffset+itemPad
            self.hSceneSize = 0
            
    def reListItems(self):
        self.items = 0
        for item in self.gscene.items():
            if not item.group():
                item.setPos(0,0)
                if not item.isSelected():
                    item.setVisible(False)
        
    def diagnostic(self):
        # count = 0
        # for item in self.gscene.items():
            # if not item.group():
                # count += 1
        # print "group items:", count
        print "group items", self.items
        print "vertical scene size:", self.vSceneSize
        print "horizontal scene size", self.hSceneSize

GView().exec_()

import PythonQt.QtGui as QtGui
import os

class BnGraphicsItem(QtGui.QGraphicsPixmapItem):
    '''Class for creating QGraphics items, accepts single arg (i.e. file path)'''
    def __init__(self, image):
        QtGui.QGraphicsPixmapItem.__init__(self)
        #Image
        self.image = image
        self.setFlags(self.flags() | QtGui.QGraphicsItem.ItemIsSelectable | QtGui.QGraphicsItem.ItemIsMovable )
        self.thumb = QtGui.QPixmap(self.image).scaled(200,200)
        self.setPixmap(self.thumb)
        self.setData(32, self.image)
        self.hsize = self.thumb.height()
        self.wsize = self.thumb.width()

    def mousePressEvent(self, mouseEvent):
        self.setSelected(True)
        print self.data(32)

class BnGraphicsViewer(QtGui.QGraphicsView):
    '''Graphics Viewer'''
    def __init__(self):
        QtGui.QGraphicsView.__init__(self)
        self.setInteractive(False)
        self.gscene = QtGui.QGraphicsScene()
        self.setScene(self.gscene)

    def addImage(self, image, vertPos, horzPos):
        imgitem = BnGraphicsItem(image)
        pixel_pad = 4
        offset = imgitem.wsize + pixel_pad
        imgitem.setPos(offset*horzPos, offset*vertPos)
        self.gscene.addItem(imgitem)

class BnGraphicsDialog(QtGui.QDialog):
    '''Image browser GUI'''
    def __init__(self):
        super(BnGraphicsDialog, self).__init__()
        vlayout = QtGui.QVBoxLayout()
        self.setWindowTitle('Test')
        self.setMinimumSize(800,800)
        self.setLayout(vlayout)
        self.gview = BnGraphicsViewer()
        self.addBtn = QtGui.QPushButton('Load')
        self.imgInput = QtGui.QLineEdit()

        vlayout.addWidget(self.gview)
        vlayout.addWidget(self.imgInput)
        vlayout.addWidget(self.addBtn)

        self.addBtn.connect("clicked()", self.addItems)
    
    def getImages(self):
        img_path = self.imgInput.text
        image_list = []
        for (dirpath, dirnames, filenames) in os.walk(img_path):
            for file in filenames:
                image_list.append(dirpath+"/"+file)
            break
        return image_list

    def addItems(self):
        self.gview.gscene.clear()
        vertPos = 0
        horzPos = 0
        for image in self.getImages():
            self.gview.addImage(image, vertPos, horzPos)
            #Column and row control
            if vertPos < 3:
                vertPos += 1
            elif vertPos >= 3:
                vertPos = 0
                horzPos +=1
            QtGui.QApplication.processEvents()

#gdialog = GraphicsD()
#gdialog.show()

BnGraphicsDialog().exec_()

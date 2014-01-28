import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
import os
import glob
import time
import threading

#import_list = []

class BnThumbnailer(QtCore.QThread):
    '''Generates thumbnails to disc'''
    thumbGen = QtCore.pyqtSignal(str)
    def __init__(self, files):
        super(BnThumbnailer, self).__init__()
        self.files = files

    def run(self):
        for file in self.files:
            fileName = file.split('/')[-1]
            fileOUT = '%s/thumbs' % os.path.dirname(file)
            fileOUT_full = '%s/%s' % (fileOUT, fileName)
            if os.path.exists(fileOUT_full):
                self.thumbGen.emit(fileOUT_full)
                continue
            image = QtGui.QImage(file)
            thumbnail = image.scaled(200,200)
            thumbnail.save(fileOUT_full)
            self.thumbGen.emit(fileOUT_full)
            time.sleep(1)

class BnGraphicsItem(QtGui.QGraphicsPixmapItem):
    '''Class for creating QGraphics items, accepts single arg (i.e. file path)'''
    def __init__(self, image):
        QtGui.QGraphicsPixmapItem.__init__(self)
        #Thumbnail Item
        self.image = image
        self.imageName = self.image.split("/")[-1]
        self.setFlags(self.flags() | QtGui.QGraphicsItem.ItemIsSelectable)
        self.thumb = QtGui.QPixmap(self.image)
        self.setPixmap(self.thumb)
        self.wsize = self.thumb.width()
        self.hsize = self.thumb.height()

    def mousePressEvent(self, mouseEvent):
        self.setSelected(True)
        print self.imageName
        #import_list.append(self.imageName)

class BnGraphicsViewer(QtGui.QGraphicsView):
    '''Graphics Viewer'''
    def __init__(self):
        QtGui.QGraphicsView.__init__(self)
        self.setInteractive(True)
        self.gscene = QtGui.QGraphicsScene()
        self.setScene(self.gscene)

    def addItem(self, image):
        imgitem = BnGraphicsItem(image)
        pixel_pad = 4
        offset = len(self.items())*imgitem.wsize+pixel_pad
        imgitem.setPos(offset, 0)
        self.gscene.addItem(imgitem)

class BnBrowserGUI(QtGui.QDialog):
    '''Main image browser UI'''
    def __init__(self):
        super(BnBrowserGUI, self).__init__()
        #Layout
        vlayout = QtGui.QVBoxLayout()
        #Widgets
        self.setWindowTitle('Test')
        self.setMinimumSize(800,400)
        self.setLayout(vlayout)
        self.timerLabel = QtGui.QLabel('Waiting...')
        self.pathLine = QtGui.QLineEdit('/jobs/scratch_texture/common/images/ref/Ben/Stencils')
        self.startBtn = QtGui.QPushButton('Start')
        self.loadBtn = QtGui.QPushButton('Load')
        self.viewer = BnGraphicsViewer()
        vlayout.addWidget(self.timerLabel)
        vlayout.addWidget(self.viewer)
        vlayout.addWidget(self.pathLine)
        vlayout.addWidget(self.startBtn)
        vlayout.addWidget(self.loadBtn)
        #Connections
        self.startBtn.clicked.connect(self.startThumbs)
        #self.loadBtn.clicked.connect(self.load)

    def initFiles(self):
        '''Initializes images files to thumbnail'''
        path = self.pathLine.text()
        filelist = glob.glob('%s/*.*' % path)
        pathOUT = '%s/thumbs' % path
        if not os.path.exists(pathOUT):
            os.mkdir(pathOUT)
        return filelist

    def updateFiles(self):
        '''Updates instance'''
        files = self.initFiles()
        self.thumbnailer = BnThumbnailer(files)

    def status(self, name):
        '''Updates browser'''
        self.timerLabel.setText(name)
        self.viewer.addItem(name)

    def startThumbs(self):
        '''Starts thumbnail generation'''
        self.updateFiles()
        self.thumbnailer.thumbGen.connect(self.status)
        self.thumbnailer.start()

    #def load(self):
        #for item in import_list:
            #print item

newDialog = BnBrowserGUI()
newDialog.show()

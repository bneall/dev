import PySide.QtGui as PyQtGui
import PySide.QtCore as PyQtCore
import os
import glob
import threading
import mari

#Thumbnail mirror location
#WARNING: Must have unique dir currently, same dir will stomp data. WIP
tmpPath = '/usr/tmp/thumbnails'

class BnFileDialog(PyQtGui.QFileDialog):
    """File Dialog: Directory Mode"""
    def __init__(self, path = None):
        super(BnFileDialog, self).__init__()
        self.setFileMode(PyQtGui.QFileDialog.Directory)
        self.setReadOnly(False)
        self.setDirectory(path)

class BnThumbnailer(PyQtCore.QThread):
    '''Generates thumbnails to disk'''
    thumbGen = PyQtCore.Signal(str)
    def __init__(self, files):
        super(BnThumbnailer, self).__init__()
        self.files = files

    def run(self):
        '''Creates thumbnail files into new folder
        Note: skips if already found.
        '''
        for file in self.files:
            fileName = file.split('/')[-1]
            dirOUT = os.path.dirname(file)
            pathOUT = '%s/%s' % (tmpPath, dirOUT)
            fileOUT_full = '%s/%s/%s' % (tmpPath, dirOUT, fileName)

            if os.path.exists(fileOUT_full):
                self.thumbGen.emit(fileOUT_full)
                continue
            if not os.path.exists(pathOUT):
                os.makedirs(pathOUT)

            image = PyQtGui.QImage(file)
            thumbnail = image.scaled(200,200, PyQtCore.Qt.KeepAspectRatio, PyQtCore.Qt.SmoothTransformation)
            thumbnail.save(fileOUT_full)
            self.thumbGen.emit(fileOUT_full)

class BnGraphicsItem(PyQtGui.QGraphicsPixmapItem):
    '''Class for creating QGraphics items, accepts single arg (i.e. file path)'''
    def __init__(self, image):
        PyQtGui.QGraphicsPixmapItem.__init__(self)
        #Thumbnail Item
        self.image = image
        self.sourceImage = image.replace('/thumbs/', '/')
        self.setFlags(self.flags() | PyQtGui.QGraphicsItem.ItemIsSelectable)
        self.thumb = PyQtGui.QPixmap(self.image)
        self.setPixmap(self.thumb)
        self.wsize = self.thumb.width()
        self.hsize = self.thumb.height()

    def mouseDoubleClickEvent(self, mouseEvent):
        '''Loads image into image manager on double click'''
        self.setSelected(True)
        mari.images.load(self.sourceImage)

class BnGraphicsViewer(PyQtGui.QGraphicsView):
    '''Graphics Viewer'''
    def __init__(self):
        PyQtGui.QGraphicsView.__init__(self)
        self.setInteractive(True)
        self.gscene = PyQtGui.QGraphicsScene()
        self.setScene(self.gscene)

    def addItem(self, image):
        '''Adds new QGraphicsItem to the QGraphicsScene
        Note: Currently locked to 4 across, no dynamic scaling
        '''
        sceneSize = len(self.items())
        imgitem = BnGraphicsItem(image)
        hpad = 3
        wpad = 3
        #hsize = imgitem.hsize + hpad
        #wsize= imgitem.wsize + wpad
        hsize = 200 + hpad
        wsize= 200 + wpad
        columnSize = 4
        hoffset = (sceneSize/columnSize)*hsize
        woffset = (sceneSize*wsize)-(hoffset*columnSize)
        imgitem.setPos(woffset, hoffset)
        self.gscene.addItem(imgitem)
        #PyQtCore.QCoreApplication.processEvents()
        mari.app.processEvents()

class BnBookmarkManager(PyQtGui.QListWidget):
    '''Bookmark manager list widget'''
    def __init__(self):
        super(BnBookmarkManager, self).__init__()

    def initBookmarks(self):
        '''Read Bookmarks if they exist'''
        try:
            favoriteConfig = open('/home/%s/Mari/imgBrowser.prefs' % os.getenv('LOGNAME'), 'r').readlines()
            for bookmark in favoriteConfig:
                bookmark = bookmark.strip("\n")
                self.addFavorite(bookmark)
        except:
                print 'No config file found'
                return

    def favoriteList(self):
        '''Returns current GUI's list of bookmarks'''
        nameList = []
        pathList = []
        for index in range(self.count()):
            item = self.item(index)
            nameList.append(item.text())
            pathList.append(item.data(32))
        return pathList

    def updateBookmark(self, favorites = None):
        '''Updates bookmark pref file with current bookmark list'''
        favoriteConfig = open('/home/%s/Mari/imgBrowser.prefs' % os.getenv('LOGNAME'), 'w')
        favoriteConfig.write("\n".join(favorites))
        favoriteConfig.close()

    def addFavorite(self, bookmark = None, current = None):
        '''Adds a new bookmark to the GUI'''
        if bookmark == None:
            bookmark = current
        bookmarkName = os.path.basename(os.path.normpath(bookmark))
        if self.findItems(bookmarkName, PyQtCore.Qt.MatchExactly):
            return
        newItem = PyQtGui.QListWidgetItem(bookmarkName)
        newItem.setData(32, bookmark)
        self.addItem(newItem)
        #Update pref file
        self.updateBookmark(self.favoriteList())

    def remFavorite(self):
        '''Removes a bookmark from the GUI'''
        for selectedItem in self.selectedItems():
                removeItem = self.takeItem(self.row(selectedItem))
                removeItem = 0
        #Update pref file
        self.updateBookmark(self.favoriteList())

class BnBrowserGUI(PyQtGui.QDialog):
    '''Main image browser UI'''
    def __init__(self):
        super(BnBrowserGUI, self).__init__()
        #self.setModal(True)
        self.setWindowTitle('Image Loader')
        self.setMinimumSize(1060,800)
        self.setMaximumSize(1060,800)
        #Layout
        vlayoutMAIN = PyQtGui.QVBoxLayout()
        hlayoutMAIN = PyQtGui.QHBoxLayout()
        vlayoutFAV = PyQtGui.QVBoxLayout()
        hlayoutOPTION = PyQtGui.QHBoxLayout()
        hlayoutMAIN.addLayout(vlayoutFAV)
        vlayoutMAIN.addLayout(hlayoutMAIN)
        vlayoutMAIN.addLayout(hlayoutOPTION)
        self.setLayout(vlayoutMAIN)
        #Widgets
        self.pathLine = PyQtGui.QLineEdit('/jobs/scratch_texture/common/images/ref/Ben/Stencils')
        self.loadBtn = PyQtGui.QPushButton('Load')
        self.browseBtn = PyQtGui.QPushButton('Browse')
        self.viewer = BnGraphicsViewer()
        #---- Favorite Bar
        self.favWidget = BnBookmarkManager()
        self.favWidget.setMaximumWidth(200)
        self.addFavBtn = PyQtGui.QPushButton('Add')
        self.remFavBtn = PyQtGui.QPushButton('Remove')
        #Populate Widgets
        vlayoutFAV.addWidget(self.favWidget)
        hlayoutMAIN.addWidget(self.viewer)
        vlayoutFAV.addWidget(self.addFavBtn)
        vlayoutFAV.addWidget(self.remFavBtn)
        hlayoutOPTION.addWidget(self.pathLine)
        hlayoutOPTION.addWidget(self.browseBtn)
        hlayoutOPTION.addWidget(self.loadBtn)
        #Connections
        self.loadBtn.clicked.connect(self.startThumbs)
        self.addFavBtn.clicked.connect(self.addFavorite)
        self.remFavBtn.clicked.connect(self.remFavorite)
        self.browseBtn.clicked.connect(self.customPath)
        self.favWidget.itemDoubleClicked.connect(self.setPath)

        #Init bookmarks
        self.favWidget.initBookmarks()

    def addFavorite(self):
        '''Runs fav widget add method'''
        self.favWidget.addFavorite(self.pathLine.text())

    def remFavorite(self):
        '''Runs fav widget remove method'''
        self.favWidget.remFavorite()

    def setPath(self):
        '''Sets path to doubleclicked list item'''
        selectedItem = self.favWidget.selectedItems()[0]
        path = selectedItem.data(32)
        self.pathLine.setText(path)
        self.startThumbs()

    def customPath(self):
        """Selects a custom directory path"""
        openPath = '/home/%s' % os.getenv('LOGNAME')
        exportDirDialog = BnFileDialog(path = openPath)
        if exportDirDialog.exec_():
            browsedExportPath = exportDirDialog.directory().path()
            self.pathLine.setText(browsedExportPath)

    def initFiles(self):
        '''Initializes images files to thumbnail'''
        path = self.pathLine.text()
        filelist = glob.glob('%s/*.*' % path)
        return filelist

    def status(self, name):
        '''Updates browser'''
        newThread = threading.Thread(target=self.viewer.addItem(name))
        newThread.start()

    def updateFiles(self):
        '''Updates instance'''
        files = self.initFiles()
        self.thumbnailer = BnThumbnailer(files)

    def startThumbs(self):
        '''Starts thumbnail generation'''
        self.viewer.gscene.clear()
        self.updateFiles()
        self.thumbnailer.thumbGen.connect(self.status)
        self.thumbnailer.run()

#BnBrowserGUI().exec_()
newDialog = BnBrowserGUI()
newDialog.show()

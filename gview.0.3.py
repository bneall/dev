import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
import threading
import os
import glob
import mari
import json

class CustomFileDialog(QtGui.QFileDialog):
    """File Dialog: Directory Mode"""
    def __init__(self, path = None):
        super(CustomFileDialog, self).__init__()
        self.setFileMode(QtGui.QFileDialog.Directory)
        self.setReadOnly(False)
        self.setDirectory(path)
        self.setModal(True)

class CustomTHUMB(QtCore.QThread):
    '''This class generates thumbnails to disc'''
    thumbGen = QtCore.Signal()
    genFinished = QtCore.Signal()
    def __init__(self, files=None):
        super(CustomTHUMB, self).__init__()
        self.files = files

    def run(self):
        fileOUT_list = []
        supportedFormats = QtGui.QImageReader.supportedImageFormats()
        for file in self.files:
            fileName = file.split('/')[-1]
            pathOUT = '%s/gViewThumbs' % os.path.dirname(file)
            fileOUT_full = '%s/%s' % (pathOUT, fileName)
            if os.path.exists(fileOUT_full):
                continue
            image = QtGui.QImage(file)
            ##Bad or Unsupported File thumbnail
            #if image.format() == QtGui.QImage.Format.Format_Invalid:
                #image = QtGui.QImage('/tools/apps/mari/current/Media/Icons/NoIcon.png')
            thumbnail = image.scaled(200,200, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            thumbnail.save(fileOUT_full)
            fileOUT_list.append(fileOUT_full)
            self.thumbGen.emit()
        self.genFinished.emit()

class CustomITEM(QtGui.QStandardItem):
    '''This class creates thumbnail item'''
    def __init__(self, file, fullPath):
        super(CustomITEM, self).__init__()
        name = os.path.basename(file)
        pixmap = QtGui.QPixmap(file)
        icon = QtGui.QIcon(pixmap)
        self.setIcon(icon)
        self.setToolTip(name)
        self.setEditable(False)
        self.setData(fullPath, 32)

class CustomVIEW(QtGui.QTableView):
    '''This class is the tableview for thumbnail items'''
    def __init__(self):
        super(CustomVIEW, self).__init__()
        self.model = QtGui.QStandardItemModel()
        self.setModel(self.model)
        self.setIconSize(QtCore.QSize(200,200))
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.setGridStyle(QtCore.Qt.NoPen)
        self.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

class CustomDIALOG(QtGui.QDialog):
    '''This class is custom dialog for interacting thumbnail items'''
    def __init__(self):
        super(CustomDIALOG, self).__init__()
        vlayout = QtGui.QVBoxLayout()
        listLayout = QtGui.QHBoxLayout()
        thumbLayout = QtGui.QVBoxLayout()
        loadLayout = QtGui.QHBoxLayout()
        optionLayout = QtGui.QHBoxLayout()
        bookmarkLayout = QtGui.QVBoxLayout()
        bookmarkoptionLayout = QtGui.QHBoxLayout()

        self.setMinimumSize(1120, 700)
        self.setModal(True)
        self.setLayout(vlayout)
        self.view = CustomVIEW()

        self.bookmarkList = QtGui.QListWidget()
        self.bookmarkList.setMaximumWidth(250)
        self.addBtn = QtGui.QPushButton('Add')
        self.removeBtn = QtGui.QPushButton('Remove')
        self.pathLine = QtGui.QLineEdit('/jobs/scratch_texture/common/images/ref/Ben/Stencils')
        bookmarkoptionLayout.addWidget(self.removeBtn)
        bookmarkoptionLayout.addWidget(self.addBtn)
        bookmarkLayout.addWidget(self.bookmarkList)
        bookmarkLayout.addLayout(bookmarkoptionLayout)

        self.cancelBtn = QtGui.QPushButton('Cancel')
        self.loadBtn = QtGui.QPushButton('Load')
        self.importBtn = QtGui.QPushButton('Import')
        self.browseBtn = QtGui.QPushButton('Browse')
        self.progBar = QtGui.QProgressBar()
        self.progBar.setHidden(True)

        listLayout.addLayout(bookmarkLayout)
        listLayout.addLayout(thumbLayout)
        thumbLayout.addWidget(self.view)
        vlayout.addLayout(listLayout)
        vlayout.addWidget(self.progBar)
        loadLayout.addWidget(self.pathLine)
        loadLayout.addWidget(self.browseBtn)
        loadLayout.addWidget(self.loadBtn)
        thumbLayout.addLayout(loadLayout)
        optionLayout.addWidget(self.cancelBtn)
        optionLayout.addWidget(self.importBtn)
        vlayout.addLayout(optionLayout)

        self.cancelBtn.clicked.connect(self.close)
        self.loadBtn.clicked.connect(self.loadThumbs)
        self.importBtn.clicked.connect(self.importImages)
        self.browseBtn.clicked.connect(self.customPath)

        self.bookmarkList.itemDoubleClicked.connect(self.retrieveBookmark)
        self.addBtn.clicked.connect(self.addBookmark)
        self.removeBtn.clicked.connect(self.removeBookmark)

        self.loadBookmarks()

    def retrieveBookmark(self):
        currentItem = self.bookmarkList.currentItem()
        bookmarkPath = currentItem.data(32)
        self.loadThumbs(bookmarkPath)

    def writeBookmarks(self):
        bookmarkDict = {}
        for index in range(self.bookmarkList.count()):
            item = self.bookmarkList.item(index)
            name = item.text()
            path = item.data(32)
            bookmarkDict[name]=path
        #Write prefs
        data = bookmarkDict
        with open('/usr/tmp/data.txt', 'w') as outfile:
            json.dump(data, outfile)

    def loadBookmarks(self):
        try:
            json_data=open('/usr/tmp/data.txt')
            data = json.load(json_data)
            for name, path in data.iteritems():
                self.addBookmark(name, path, mode = 'load')
        except:
            pass

    def addBookmark(self, name = None, path = None, mode = 'new'):
        if not path:
            path = self.pathLine.text()
        if not name:
            name = os.path.basename(path)
        newItem = QtGui.QListWidgetItem(name)
        newItem.setData(32, path)
        for index in range(self.bookmarkList.count()):
            item = self.bookmarkList.item(index)
            if item.text() == name:
                return
        self.bookmarkList.addItem(newItem)
        #Write prefs
        if mode != 'load':
            self.writeBookmarks()

    def removeBookmark(self):
        for selectedItem in self.bookmarkList.selectedItems():
            removeItem = self.bookmarkList.takeItem(self.bookmarkList.row(selectedItem))
            removeItem = 0
        #Write prefs
        self.writeBookmarks()

    def customPath(self):
        """Sets up a custom path"""
        path = self.pathLine.text()
        exportDirDialog = CustomFileDialog(path = path)
        if exportDirDialog.exec_():
            browsedExportPath = exportDirDialog.directory().path()
            self.pathLine.setText(browsedExportPath)

    def loadThumbs(self, path = None):
        '''Starts thumbnail generation'''
        if not path:
            path = self.pathLine.text()
        self.filelist = glob.glob('%s/*.*' % path)
        self.filelist = sorted(self.filelist)
        pathOUT = '%s/gViewThumbs' % path
        if not os.path.exists(pathOUT):
            os.mkdir(pathOUT)
        self.thumbnailer = CustomTHUMB(self.filelist)
        self.thumbnailer.thumbGen.connect(self.updateProgress)
        self.thumbnailer.genFinished.connect(self.finishThumbs)
        self.thumbnailer.run()

    def updateProgress(self):
        '''Updates thumbnail generation progress'''
        self.progBar.setHidden(False)
        currentValue = self.progBar.value()
        self.progBar.setMaximum(len(self.filelist))
        self.progBar.setValue(currentValue+1)
        QtCore.QCoreApplication.processEvents()

    def finishThumbs(self):
        '''Runs thread for adding items once thumbnails are finished being generated'''
        self.progBar.setHidden(True)
        self.view.model.clear()
        newThread = threading.Thread(target=self.addThumbs())
        newThread.start()

    def addThumbs(self):
        '''Adds thumbnail items to the model/view'''
        columnMax = 3
        row = 0
        column = 0
        for file in self.filelist:
            fileName = os.path.basename(file)
            filePath = os.path.dirname(file)
            sourceIMAGE = os.path.join(filePath, fileName)
            thumbIMAGE = os.path.join(filePath, 'gViewThumbs', fileName)
            newItem = CustomITEM(thumbIMAGE, sourceIMAGE)
            self.view.model.setItem(row, column, newItem)
            self.view.setColumnWidth(column, 205)
            self.view.setRowHeight(row, 205)
            self.view.resizeRowToContents(row)
            #Layout Control
            if column == columnMax:
                column = 0
                row += 1
            else:
                column += 1

    def importImages(self):
        '''Imports selected images into image managers'''
        selected = self.view.selectedIndexes()
        for item in selected:
            realitem = self.view.model.itemFromIndex(item)
            imagePath = realitem.data(32)
            mari.images.load(imagePath)

customWindow = CustomDIALOG()
customWindow.show()

## gView: Thumbnail viewer
## Description: A simple thumbnail viewer for loading images in Mari.
## Author: Ben Neall
## Requirements: Mari 2.6.x

import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
import threading
import os
import glob
import mari
import json

#-------Common------------------------------------------------------------------------------------------------------------------------
thumbnailDirName = 'gViewThumbs'
prefsFileName = 'gViewBookmark.prefs'
prefsFilePath = mari.resources.path(mari.resources.USER)
prefsFile = os.path.join(prefsFilePath, prefsFileName)
iconSize = 200
columnMax = 4


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

#--------------------------------------------------------------------------------------------------------------------------------------------
class CustomFileDialog(QtGui.QFileDialog):
    """File Dialog: Directory Mode"""
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, path = None):
        super(CustomFileDialog, self).__init__()
        self.setFileMode(QtGui.QFileDialog.Directory)
        self.setModal(True)
        self.setReadOnly(False)
        self.setDirectory(path)


#--------------------------------------------------------------------------------------------------------------------------------------------
class CustomTHUMB(QtCore.QThread):
    '''This class generates thumbnails to disc'''
    #Signals
    thumbGen = QtCore.Signal(str)
    finishGen = QtCore.Signal()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, files=None):
        super(CustomTHUMB, self).__init__()
        self.files = files

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def run(self):
        for file in self.files:
            fileDir, fileName = os.path.split(file)
            thumbnailPath = os.path.join(fileDir, thumbnailDirName, fileName)
            # Check if thumbnail already exists
            if os.path.exists(thumbnailPath):
                self.thumbGen.emit(file)
                continue
            sourceImage = QtGui.QImage(file)
            thumbImage = sourceImage.scaled(iconSize,iconSize, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            thumbImage.save(thumbnailPath)
            self.thumbGen.emit(file)
        self.finishGen.emit()


#--------------------------------------------------------------------------------------------------------------------------------------------#
class CustomITEM(QtGui.QStandardItem):
    '''This class creates thumbnail item'''
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, thumbFile, sourcePath):
        super(CustomITEM, self).__init__()
        self.thumbFile = thumbFile
        self.sourcePath = sourcePath
        fileName = os.path.basename(self.thumbFile)
        thumbPixmap = QtGui.QPixmap(self.thumbFile)
        thumbIcon = QtGui.QIcon(thumbPixmap)
        self.setIcon(thumbIcon)
        self.setToolTip(fileName)
        self.setData(self.sourcePath, 32)
        self.setEditable(False)


#--------------------------------------------------------------------------------------------------------------------------------------------#
class CustomVIEW(QtGui.QTableView):
    '''This class is the tableview for thumbnail items'''
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self):
        super(CustomVIEW, self).__init__()
        self.smodel = QtGui.QStandardItemModel()
        self.setModel(self.smodel)
        self.setIconSize(QtCore.QSize(iconSize,iconSize))

        #Hide Table Elements
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.setGridStyle(QtCore.Qt.NoPen)

        #Smooth Scroll
        self.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)


#--------------------------------------------------------------------------------------------------------------------------------------------#
class CustomWIDGET(QtGui.QWidget):
    '''This class is custom dialog for interacting thumbnail items'''
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self):
        super(CustomWIDGET, self).__init__()
        vlayout = QtGui.QVBoxLayout()
        listLayout = QtGui.QHBoxLayout()
        thumbLayout = QtGui.QVBoxLayout()
        loadLayout = QtGui.QHBoxLayout()
        optionLayout = QtGui.QHBoxLayout()
        bookmarkLayout = QtGui.QVBoxLayout()
        bookmarkoptionLayout = QtGui.QHBoxLayout()
        self.setLayout(vlayout)

        self.view = CustomVIEW()
        self.bookmarkList = QtGui.QListWidget()
        self.bookmarkList.setMaximumWidth(250)
        self.addBtn = QtGui.QPushButton('Add Favorite')
        self.removeBtn = QtGui.QPushButton('Remove Favorite')
        self.pathLine = QtGui.QLineEdit()
        bookmarkoptionLayout.addWidget(self.removeBtn)
        bookmarkoptionLayout.addWidget(self.addBtn)
        bookmarkLayout.addLayout(bookmarkoptionLayout)
        bookmarkLayout.addWidget(self.bookmarkList)

        self.loadBtn = QtGui.QPushButton('Load')
        self.importBtn = QtGui.QPushButton('Send To Image Manager')
        self.browseBtn = QtGui.QPushButton('Browse')
        self.progBar = QtGui.QProgressBar()
        self.progBar.setHidden(True)

        listLayout.addLayout(bookmarkLayout)
        listLayout.addLayout(thumbLayout)
        vlayout.addLayout(listLayout)
        vlayout.addWidget(self.progBar)
        loadLayout.addWidget(self.pathLine)
        loadLayout.addWidget(self.browseBtn)
        loadLayout.addWidget(self.loadBtn)
        thumbLayout.addLayout(loadLayout)
        thumbLayout.addWidget(self.view)
        optionLayout.addStretch()
        optionLayout.addWidget(self.importBtn)
        vlayout.addLayout(optionLayout)

        self.loadBtn.clicked.connect(self.loadThumbs)
        self.importBtn.clicked.connect(self.importImages)
        self.browseBtn.clicked.connect(self.customPath)

        self.bookmarkList.itemDoubleClicked.connect(self.retrieveBookmark)
        self.addBtn.clicked.connect(self.addBookmark)
        self.removeBtn.clicked.connect(self.removeBookmark)

        self.loadBookmarks()
        self.clearList()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def clearList(self):
        self.view.smodel.clear()
        self.row = 0
        self.column = 0

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def addItemThread(self, file):
        newThread = threading.Thread(target=self.addSingleItem(file))
        newThread.start()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def addSingleItem(self, file):
        fileName = os.path.basename(file)
        filePath = os.path.dirname(file)
        sourceIMAGE = os.path.join(filePath, fileName)
        thumbIMAGE = os.path.join(filePath, thumbnailDirName, fileName)
        newItem = CustomITEM(thumbIMAGE, sourceIMAGE)
        self.view.smodel.setItem(self.row, self.column, newItem)
        self.view.setColumnWidth(self.column, iconSize)
        self.view.setRowHeight(self.row, iconSize)
        self.view.resizeRowToContents(self.row)
        if self.column == columnMax:
            self.column = 0
            self.row += 1
        else:
            self.column += 1

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def retrieveBookmark(self):
        '''Loads bookmark'''
        currentItem = self.bookmarkList.currentItem()
        bookmarkPath = currentItem.data(32)
        self.loadThumbs(bookmarkPath)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def writeBookmarks(self):
        '''Write bookmarks to prefs file'''
        bookmarkDict = {}
        for index in range(self.bookmarkList.count()):
            item = self.bookmarkList.item(index)
            name = item.text()
            path = item.data(32)
            bookmarkDict[name]=path
        #Write prefs
        data = bookmarkDict
        with open(prefsFile, 'w') as outfile:
            json.dump(data, outfile)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def loadBookmarks(self):
        '''Loads bookmarks from prefs'''
        try:
            json_data=open(prefsFile)
            data = json.load(json_data)
            for name, path in data.iteritems():
                self.addBookmark(name, path, mode = 'load')
        except:
            pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def addBookmark(self, name = None, path = None, mode = 'new'):
        '''Adds bookmark from input path'''
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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def customPath(self):
        '''Sets up a custom path'''
        path = self.pathLine.text()
        exportDirDialog = CustomFileDialog(path = path)
        if exportDirDialog.exec_():
            browsedExportPath = exportDirDialog.directory().path()
            self.pathLine.setText(browsedExportPath)
            self.loadThumbs()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def loadThumbs(self, path = None):
        '''Starts thumbnail generation'''

        self.clearList()

        if not path:
            path = self.pathLine.text()
        self.fullFileList = glob.glob(os.path.join(path, '*.*'))
        self.fileList = []

        #Check for thumbnail directory
        thumbsPath = os.path.join(path, thumbnailDirName)
        if not os.path.exists(thumbsPath):
            os.mkdir(thumbsPath)

        #Create valid image list
        supportedFormats = PySide.QtGui.QImageWriter.supportedImageFormats()
        for file in self.fullFileList:
            fileName, fileExtension = os.path.splitext(file)
            cleanExt = fileExtension.strip(".")
            if cleanExt.lower() in supportedFormats:
                self.fileList.append(file)
        #Sort list
        self.fileList = sorted(self.fileList)

        #Run thumbnail generation
        self.thumbnailer = CustomTHUMB(self.fileList)
        self.thumbnailer.thumbGen.connect(self.addItemThread)
        self.thumbnailer.thumbGen.connect(self.updateProgress)
        self.thumbnailer.finishGen.connect(self.finishThumbs)
        self.thumbnailer.run()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateProgress(self):
        '''Updates thumbnail generation progress'''
        currentValue = self.progBar.value()
        self.progBar.setHidden(False)
        self.progBar.setMaximum(len(self.fileList))
        self.progBar.setValue(currentValue+1)
        QtCore.QCoreApplication.processEvents()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def finishThumbs(self):
        '''Misc tasks after thumbs are finished generating'''
        self.progBar.setHidden(True)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def addThumbs(self):
        '''Adds thumbnail items to the model/view'''
        columnMax = 3
        row = 0
        column = 0
        for file in self.fileList:
            fileName = os.path.basename(file)
            filePath = os.path.dirname(file)
            sourceIMAGE = os.path.join(filePath, fileName)
            thumbIMAGE = os.path.join(filePath, thumbnailDirName, fileName)
            newItem = CustomITEM(thumbIMAGE, sourceIMAGE)
            self.view.smodel.setItem(row, column, newItem)
            self.view.setColumnWidth(column, iconSize)
            self.view.setRowHeight(row, iconSize)
            self.view.resizeRowToContents(row)
            #Layout Control
            if column == columnMax:
                column = 0
                row += 1
            else:
                column += 1

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def importImages(self):
        '''Imports selected images into image managers'''
        selected = self.view.selectedIndexes()
        for item in selected:
            realitem = self.view.smodel.itemFromIndex(item)
            imagePath = realitem.data(32)
            mari.images.load(imagePath)


## MARI GUI
gviewWidget = CustomWIDGET()
mari.app.addTab('gView', gviewWidget)

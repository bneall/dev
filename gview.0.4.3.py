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

#-------Common--------------------------------------------------------------------------------------
mari_icon_path = mari.resources.path(mari.resources.ICONS)
gview_bmarkPref = 'gViewBookmark.prefs'
gview_configPref = 'gViewConfig.prefs'
gview_prefsDir = mari.resources.path(mari.resources.USER)
gview_bmarkFile = os.path.join(gview_prefsDir, gview_bmarkPref)
gview_configFile = os.path.join(gview_prefsDir, gview_configPref)


#-------Preferences---------------------------------------------------------------------------------
try:
    #Load Prefs
    configFile = open(gview_configFile)
    config = json.load(configFile)
    gview_tempDir = config['gview_tempDir']
    gview_thumbDir = config['gview_thumbDir']
    gview_thumbSize = config['gview_thumbSize']
    gview_thumbFormat = config['gview_thumbFormat']
    gview_columnCount = config['gview_columnCount']
except:
    #Set Defaults
    if mari.app.version().isLinux():
        gview_tempDir = '/usr/tmp'
    if mari.app.version().isWindows():
        gview_tempDir = 'C:\temp'
    gview_thumbDir = 'gViewThumbnails'
    gview_thumbSize = '200'
    gview_thumbFormat = 'jpg'
    gview_columnCount = '4'


class CustomPrefsDialog(QtGui.QDialog):
    '''Preferences Dialog'''
    def __init__(self):
        super(CustomPrefsDialog, self).__init__()
        self.setWindowTitle('gView Preferences')
        layout = QtGui.QGridLayout()
        self.setLayout(layout)

        self.tempDirLabel = QtGui.QLabel('Thumbnail Location')
        self.tempDir = QtGui.QLineEdit(gview_tempDir)
        layout.addWidget(self.tempDirLabel, 0, 0)
        layout.addWidget(self.tempDir, 0, 1)

        self.thumbDirLabel = QtGui.QLabel('Thumbnail Directory Name')
        self.thumbDir = QtGui.QLineEdit(gview_thumbDir)
        layout.addWidget(self.thumbDirLabel, 1, 0)
        layout.addWidget(self.thumbDir, 1, 1)

        self.thumbSizeLabel = QtGui.QLabel('Thumbnail File Size')
        self.thumbSize = QtGui.QLineEdit(gview_thumbSize)
        layout.addWidget(self.thumbSizeLabel, 2, 0)
        layout.addWidget(self.thumbSize, 2, 1)

        self.thumbFormatLabel = QtGui.QLabel('Thumbnail Format')
        self.thumbFormat = QtGui.QLineEdit(gview_thumbFormat)
        layout.addWidget(self.thumbFormatLabel, 3, 0)
        layout.addWidget(self.thumbFormat, 3, 1)

        self.columnCountLabel = QtGui.QLabel('Max Columns')
        self.columnCount = QtGui.QLineEdit(gview_columnCount)
        layout.addWidget(self.columnCountLabel, 4, 0)
        layout.addWidget(self.columnCount, 4, 1)

        self.cancelBtn = QtGui.QPushButton('Cancel')
        layout.addWidget(self.cancelBtn, 5, 0)
        self.saveBtn = QtGui.QPushButton('Save')
        layout.addWidget(self.saveBtn, 5, 1)

        self.cancelBtn.clicked.connect(self.reject)
        self.saveBtn.clicked.connect(self.savePrefs)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def savePrefs(self):
        prefData = {}

        global gview_tempDir
        gview_tempDir = self.tempDir.text()
        prefData['gview_tempDir']=gview_tempDir

        global gview_thumbDir
        gview_thumbDir = self.thumbDir.text()
        prefData['gview_thumbDir']=gview_thumbDir

        global gview_thumbSize
        gview_thumbSize = self.thumbSize.text()
        prefData['gview_thumbSize']=gview_thumbSize

        global gview_thumbFormat
        gview_thumbFormat = self.thumbFormat.text()
        prefData['gview_thumbFormat']=gview_thumbFormat

        global gview_columnCount
        gview_columnCount = self.columnCount.text()
        prefData['gview_columnCount']=gview_columnCount

        #Write config prefs
        with open(gview_configFile, 'w') as outfile:
            json.dump(prefData, outfile)

        self.accept()
        rebuildWidget()


class CustomFileDialog(QtGui.QFileDialog):
    """File Dialog: Directory Mode"""
    def __init__(self, path = None):
        super(CustomFileDialog, self).__init__()
        self.setFileMode(QtGui.QFileDialog.Directory)
        self.setModal(True)
        self.setReadOnly(False)
        self.setDirectory(path)


class CustomTHUMB(QtCore.QThread):
    '''This class generates thumbnails to disc'''

    thumbGen = QtCore.Signal()
    finishGen = QtCore.Signal()

    def __init__(self, files=None):
        super(CustomTHUMB, self).__init__()
        self.files = files

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def run(self):
        for thumb, source in self.files.items():
            #Check if thumbnail already exists
            if os.path.isfile(thumb):
                continue
            sourceImage = QtGui.QImage(source)
            thumbImage = sourceImage.scaled(int(gview_thumbSize),int(gview_thumbSize), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            thumbImage.save(str(thumb), str(gview_thumbFormat), 75)
            self.thumbGen.emit()
        self.finishGen.emit()


class CustomITEM(QtGui.QStandardItem):
    '''This class creates thumbnail item'''
    def __init__(self, thumbFile, sourcePath):
        super(CustomITEM, self).__init__()
        fileName = os.path.basename(thumbFile)
        thumbPixmap = QtGui.QPixmap(thumbFile)
        thumbIcon = QtGui.QIcon(thumbPixmap)
        self.setIcon(thumbIcon)
        self.setToolTip(fileName)
        self.setData(sourcePath, 32)
        self.setEditable(False)


class CustomVIEW(QtGui.QTableView):
    '''This class is the tableview for thumbnail items'''
    def __init__(self):
        super(CustomVIEW, self).__init__()
        self.smodel = QtGui.QStandardItemModel()
        self.setModel(self.smodel)
        self.setIconSize(QtCore.QSize(int(gview_thumbSize),int(gview_thumbSize)))

        #Hide Table Elements
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.setGridStyle(QtCore.Qt.NoPen)

        #Smooth Scroll
        self.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)


class CustomWIDGET(QtGui.QWidget):
    '''This Class is custom widget for interacting thumbnail items'''
    def __init__(self):
        super(CustomWIDGET, self).__init__()

        #Layouts
        vlayout = QtGui.QVBoxLayout()
        gridLayout = QtGui.QGridLayout()
        self.setLayout(vlayout)

        optionLayout = QtGui.QHBoxLayout()
        loadLayout = QtGui.QHBoxLayout()
        bottomLayout  = QtGui.QHBoxLayout()

        #Bookmark widgets
        self.view = CustomVIEW()
        self.bookmarkList = QtGui.QListWidget()
        self.bookmarkList.setMaximumWidth(250)
        self.addBtn = QtGui.QToolButton()
        self.addBtn.setIcon(QtGui.QIcon('%s/Plus.png' % mari_icon_path))
        self.removeBtn = QtGui.QToolButton()
        self.removeBtn.setIcon(QtGui.QIcon('%s/Minus.png' % mari_icon_path))

        #Load widgets
        self.pathLine = QtGui.QLineEdit()
        self.loadBtn = QtGui.QPushButton('Load')
        self.prefsBtn = QtGui.QToolButton()
        self.importBtn = QtGui.QPushButton('Import')
        self.prefsBtn.setIcon(QtGui.QIcon('%s/Preference.png' % mari_icon_path))
        self.browseBtn = QtGui.QPushButton('Browse')
        self.progStatus = QtGui.QLabel()
        self.progBar = QtGui.QProgressBar()
        self.progBar.setHidden(True)
        self.progStatus.setHidden(True)

        optionLayout.addWidget(self.prefsBtn)
        optionLayout.addSpacing(120)
        optionLayout.addWidget(self.removeBtn)
        optionLayout.addWidget(self.addBtn)

        loadLayout.addWidget(self.pathLine)
        loadLayout.addWidget(self.browseBtn)
        loadLayout.addWidget(self.loadBtn)

        bottomLayout.addWidget(self.progBar)
        bottomLayout.addWidget(self.progStatus)
        bottomLayout.addStretch()
        bottomLayout.addWidget(self.importBtn)

        #Populate
        gridLayout.addLayout(optionLayout, 0, 0)
        gridLayout.addLayout(loadLayout, 0, 1)
        gridLayout.addWidget(self.bookmarkList, 1, 0)
        gridLayout.addWidget(self.view, 1, 1)
        vlayout.addLayout(gridLayout)
        vlayout.addLayout(bottomLayout)

        #Connections
        self.loadBtn.clicked.connect(self.loadThumbs)
        self.prefsBtn.clicked.connect(self.setPrefs)
        self.importBtn.clicked.connect(self.importImages)
        self.browseBtn.clicked.connect(self.customPath)
        self.bookmarkList.itemClicked.connect(self.retrieveBookmark)
        self.addBtn.clicked.connect(self.addBookmark)
        self.removeBtn.clicked.connect(self.removeBookmark)

        #Init
        self.loadBookmarks()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setPrefs(self):
        CustomPrefsDialog().exec_()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def makePaths(self, path):
        supportedFormats = QtGui.QImageWriter.supportedImageFormats()
        self.fileDict = {}

        for dirName, subdirList, fileList in os.walk(path, topdown=False):
            for file in fileList:
                #OS weirdness
                if mari.app.version().isWindows():
                    cleanDirName = dirName.replace(':','')
                    thumbnailPath = os.path.join(gview_tempDir, gview_thumbDir, cleanDirName)
                if mari.app.version().isLinux():
                    thumbnailPath = '%s/%s%s' % (gview_tempDir, gview_thumbDir, dirName)

                #Build thumbnail directories
                if not os.path.exists(thumbnailPath):
                    os.makedirs(thumbnailPath)

                #File paths
                thumbFile = '%s.%s' % (os.path.splitext(file)[0], gview_thumbFormat)
                thumbFile = os.path.join(thumbnailPath, thumbFile)
                sourceFile = os.path.join(dirName, file)

                #Format check:
                fileExtension = file.split(".")[-1]
                if fileExtension.lower() in supportedFormats:
                    #Build file dict
                    self.fileDict[thumbFile]=sourceFile

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def addAllItems(self):
        column = 0
        row = 0
        '''Add single thumbnail item'''
        for thumb, source in self.fileDict.items():
            newItem = CustomITEM(thumb, source)
            self.view.smodel.setItem(row, column, newItem)
            self.view.setColumnWidth(column, int(gview_thumbSize))
            self.view.setRowHeight(row, int(gview_thumbSize))
            self.view.resizeRowToContents(row)
            if column == int(gview_columnCount):
                column = 0
                row += 1
            else:
                column += 1

    def addAllItemsThread(self):
        newThread = threading.Thread(target=self.addAllItems)
        newThread.run()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def retrieveBookmark(self):
        '''Loads bookmark'''
        currentItem = self.bookmarkList.currentItem()
        bookmarkPath = currentItem.data(32)
        self.loadThumbs(bookmarkPath)
        self.pathLine.setText(bookmarkPath)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
        with open(gview_bmarkPref, 'w') as outfile:
            json.dump(data, outfile)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def loadBookmarks(self):
        '''Loads bookmarks from prefs'''
        try:
            json_data=open(gview_bmarkPref)
            data = json.load(json_data)
            for name, path in data.iteritems():
                self.addBookmark(name, path, mode='load')
        except:
            pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def addBookmark(self, name=None, path=None, mode='new'):
        '''Adds bookmark from input path'''
        if not path:
            path = self.pathLine.text()
        if not name:
            name = os.path.basename(path)
        newItem = QtGui.QListWidgetItem(name)
        newItem.setData(32, path)
        newItem.setIcon(QtGui.QIcon('%s/Palette.16x16.png' % mari_icon_path))
        for index in range(self.bookmarkList.count()):
            item = self.bookmarkList.item(index)
            if item.text() == name:
                return
        self.bookmarkList.addItem(newItem)

        #Write prefs
        if mode != 'load':
            self.writeBookmarks()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def removeBookmark(self):
        '''Remove selected bookmark'''
        for selectedItem in self.bookmarkList.selectedItems():
            removeItem = self.bookmarkList.takeItem(self.bookmarkList.row(selectedItem))
            removeItem = 0

        #Write prefs
        self.writeBookmarks()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def customPath(self):
        '''Sets up a custom path'''
        path = self.pathLine.text()
        exportDirDialog = CustomFileDialog(path = path)
        if exportDirDialog.exec_():
            browsedExportPath = exportDirDialog.directory().path()
            #Windows fix
            if mari.app.version().isWindows():
                browsedExportPath = browsedExportPath.replace("/", "\\")
            self.pathLine.setText(browsedExportPath)
            self.loadThumbs()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def loadThumbs(self, path=None):
        '''Starts thumbnail generation'''

        self.view.smodel.clear()

        if not path:
            path = self.pathLine.text()

        self.makePaths(path)

        #Run thumbnail generation
        self.thumbnailer = CustomTHUMB(self.fileDict)
        self.thumbnailer.thumbGen.connect(self.updateProgress)
        self.thumbnailer.finishGen.connect(self.finishThumbs)
        self.thumbnailer.run()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateProgress(self):
        '''Updates thumbnail generation progress'''
        currentValue = self.progBar.value()
        totalImages = len(self.fileDict)
        self.progBar.setHidden(False)
        self.progStatus.setHidden(False)
        self.progBar.setMaximum(totalImages)
        self.progBar.setValue(currentValue+1)
        self.progStatus.setText('%s/%s' % (currentValue, totalImages))
        QtCore.QCoreApplication.processEvents()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def finishThumbs(self):
        '''Misc tasks after thumbs are finished generating'''
        self.progBar.setHidden(True)
        self.progStatus.setHidden(True)
        self.addAllItemsThread()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

def rebuildWidget():
    mari.app.removeTab('gView')
    gviewWidget = None
    gviewWidget = CustomWIDGET()
    mari.app.addTab('gView', gviewWidget)
    mari.app.setActiveTab('gView')

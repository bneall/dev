#-------------------------------------------------------------------------------------------------#
# Bake Selected Tool
#-------------------------------------------------------------------------------------------------#
#Description:
#Tool for selectively baking combinations of UDIMs and Layers.
#
#Author:
#Ben Neall - ben.neall@methodstudios.com
#-------------------------------------------------------------------------------------------------#

import PySide.QtGui as QtGui
import mari

mari_icon_path = mari.resources.path(mari.resources.ICONS)

if mari.app.version().isWindows():
    tempDir = 'C:\\temp'
if mari.app.version().isLinux():
    tempDir = '/usr/tmp'
if mari.app.version().isMac():
    tempDir = '/tmp'

#---------------------------------------------------
#                Options GUI
#---------------------------------------------------
class BakeSelectedDialog(QtGui.QDialog):

    currentGeo = mari.current.geo()
    currentChannel = mari.current.channel()
    selectedPatches =  currentGeo.selectedPatches()

    def __init__(self):
        super(BakeSelectedDialog, self).__init__()
        self.setMinimumWidth(500)
        self.setWindowTitle('Bake %s' % self.currentChannel.name())

        mainLayout = QtGui.QVBoxLayout()
        nameLayout = QtGui.QGridLayout()
        optionsLayout = QtGui.QHBoxLayout()
        option1Layout = QtGui.QVBoxLayout()
        option2Layout = QtGui.QVBoxLayout()
        outputLayout = QtGui.QGridLayout()
        buttonLayout = QtGui.QHBoxLayout()
        mainLayout.addLayout(nameLayout)
        mainLayout.addLayout(optionsLayout)
        mainLayout.addLayout(outputLayout)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

        self.channGroupBox = QtGui.QGroupBox('As New Channel')
        self.channGroupBox.setCheckable(True)
        self.channGroupBox.setLayout(option1Layout)
        self.layerGroupBox = QtGui.QGroupBox('As New Layer')
        self.layerGroupBox.setCheckable(True)
        self.layerGroupBox.setLayout(option2Layout)

        optionsLayout.addWidget(self.channGroupBox)
        optionsLayout.addWidget(self.layerGroupBox)

        self.customNameLabel = QtGui.QLabel('New Name: ')
        self.customName = QtGui.QLineEdit()
        self.channelComboLabel = QtGui.QLabel('Choose Channel:')
        self.channelCombo = QtGui.QComboBox()
        self.channelBitDepthLabel = QtGui.QLabel('Bit Depth:')
        self.channelBitDepthOptionCombo = QtGui.QComboBox()
        self.channelBitDepthOptionCombo.addItems(['Source', '8', '16', '32'])
        self.customDirLabel = QtGui.QLabel('Location: ')
        self.customDir = QtGui.QLineEdit(tempDir)
        self.bakeBtn = QtGui.QPushButton('Bake')
        self.cancelBtn = QtGui.QPushButton('Cancel')

        nameLayout.addWidget(self.customNameLabel, 1, 0)
        nameLayout.addWidget(self.customName, 1, 1)
        nameLayout.setColumnStretch(1, 0)
        option1Layout.addWidget(self.channelBitDepthLabel)
        option1Layout.addWidget(self.channelBitDepthOptionCombo)
        option2Layout.addWidget(self.channelComboLabel)
        option2Layout.addWidget(self.channelCombo)
        outputLayout.addWidget(self.customDirLabel, 1, 0)
        outputLayout.addWidget(self.customDir, 1, 1)
        outputLayout.setColumnStretch(1, 0)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.cancelBtn)
        buttonLayout.addWidget(self.bakeBtn,)

        self.channGroupBox.toggled.connect(self.toggleLayerOption)
        self.layerGroupBox.toggled.connect(self.toggleChannelOption)
        self.cancelBtn.clicked.connect(self.close)
        self.bakeBtn.clicked.connect(self.bakeSelected)

        self.init()

    def init(self):
        self.layerGroupBox.setChecked(False)
        self.customName.setText('%s_bake' % self.currentChannel.name())
        for channel in self.currentGeo.channelList():
            self.channelCombo.addItem(channel.name(), channel)

    def toggleLayerOption(self):
        if self.channGroupBox.isChecked():
            self.layerGroupBox.setChecked(False)

    def toggleChannelOption(self):
        if self.layerGroupBox.isChecked():
            self.channGroupBox.setChecked(False)

    def bakeSelected(self):
        uv_index = [i.uvIndex() for i in self.selectedPatches]
        if not uv_index:
            uv_index = [i.uvIndex() for i in self.currentGeo.patchList()]

        #Manage layer visibility
        visibleLayers = []
        selectedLayers = []
        for layer in self.currentChannel.layerList():
            if layer.isVisible():
                visibleLayers.append(layer)
            if layer.isSelected():
                selectedLayers.append(layer)

        #Hide unselected layers for bake
        if selectedLayers:
            for layer in self.currentChannel.layerList():
                if layer in selectedLayers:
                    layer.setVisibility(True)
                else:
                    layer.setVisibility(False)
        else:
            pass

        #Temp location
        temp_dir = self.customDir.text()

        #New Channel Name
        customName = self.customName.text()
        customTemplate = '%s/%s.$UDIM.tif' % (temp_dir, customName)

        mari.history.startMacro('Bake Selected')
        #-------------------------------------------------------------------------------------------------------------------------------------------
        #Bake selected to tmp
        self.currentChannel.exportImagesFlattened(customTemplate, 0, uv_index)

        #New Channel
        bitDepth = self.channelBitDepthOptionCombo.currentText()
        if bitDepth == 'Source':
            bitDepth = self.currentChannel.depth()
        else:
            bitDepth = int(bitDepth)
        if self.channGroupBox.isChecked():
            destinationChannel = self.currentGeo.createChannel(customName, 4096, 4096, bitDepth)
            destinationChannel.importImages(customTemplate, 0, 0, 0, uv_index)
        elif self.layerGroupBox.isChecked():
            destinationChannel = self.channelCombo.itemData(self.channelCombo.currentIndex(), 32)
            newLayer = destinationChannel.createPaintableLayer(customName)
            newLayer.importImages(customTemplate, 0, uv_index)
        #-------------------------------------------------------------------------------------------------------------------------------------------
        mari.history.stopMacro()

        #Show all layers
        for layer in self.currentChannel.layerList():
            if layer in visibleLayers:
                layer.setVisibility(True)
            else:
                layer.setVisibility(False)
        self.close()

#----------------------------------------------------------------------
# GUI
#----------------------------------------------------------------------
bakeSelectedITEM = mari.actions.create('Bake Selected', 'mari.utils.execDialog(BakeSelectedDialog())')
bakeSelectedITEM.setIconPath('%s/Bake.png' % mari_icon_path)
mari.menus.addAction(bakeSelectedITEM, 'MainWindow/Channels', 'Flatten')
#bakeSelectedITEM.setEnabled(False)

## Activation
def activation():
    if mari.projects.current():
        bakeSelectedITEM.setEnabled(True)
    else:
        bakeSelectedITEM.setEnabled(False)

mari.utils.connect(mari.projects.opened, activation)
mari.utils.connect(mari.projects.closed, activation)

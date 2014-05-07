#-------------------------------------------------------------------------------------------------#
# Bake Selected Tool
#-------------------------------------------------------------------------------------------------#
#Description:
#Tool for selectively baking combinations of UDIMs and Layers.
#
#Author:
#Ben Neall - ben.neall@methodstudios.com
#-------------------------------------------------------------------------------------------------#

import PythonQt.QtGui as QtGui
import mari
import os

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
    def __init__(self):
        super(BakeSelectedDialog, self).__init__()
        self.setMinimumWidth(500)

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
        self.scaleOptionLabel = QtGui.QLabel('Scale: ')
        self.scaleOptionCombo = QtGui.QComboBox()
        self.scaleOptionCombo.addItems(['Source', 'Target'])
        self.customDir = QtGui.QLineEdit(tempDir)
        self.bakeBtn = QtGui.QPushButton('Bake')
        self.cancelBtn = QtGui.QPushButton('Cancel')

        nameLayout.addWidget(self.customNameLabel, 1, 0)
        nameLayout.addWidget(self.customName, 1, 1)
        nameLayout.setColumnStretch(1, 0)
        option1Layout.addWidget(self.channelBitDepthLabel)
        option1Layout.addWidget(self.channelBitDepthOptionCombo)
        option1Layout.addStretch()
        option2Layout.addWidget(self.channelComboLabel)
        option2Layout.addWidget(self.channelCombo)
        option2Layout.addWidget(self.scaleOptionLabel)
        option2Layout.addWidget(self.scaleOptionCombo)
        option2Layout.addStretch()
        outputLayout.addWidget(self.customDirLabel, 1, 0)
        outputLayout.addWidget(self.customDir, 1, 1)
        outputLayout.setColumnStretch(1, 0)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.cancelBtn)
        buttonLayout.addWidget(self.bakeBtn,)

        self.channGroupBox.connect("toggled (bool)", self.toggleLayerOption)
        self.layerGroupBox.connect("toggled (bool)", self.toggleChannelOption)
        self.cancelBtn.connect("clicked()", self.close)
        self.bakeBtn.connect("clicked()", self.bakeSelected)

        self.init()

    def init(self):
        currentGeo = mari.geo.current()
        currentChannel = mari.geo.current().currentChannel()
        self.layerGroupBox.setChecked(False)
        self.setWindowTitle('Bake %s' % currentChannel.name())
        self.customName.setText('%s_bake' % currentChannel.name())

        #Sort
        chanList = []
        for channel in currentGeo.channelList():
            chanList.append(channel.name())
        chanList = sorted(chanList)

        #Add
        for channel in chanList:
            mchan = currentGeo.findChannel(channel)
            self.channelCombo.addItem(channel, mchan)

    def toggleLayerOption(self):
        if self.channGroupBox.isChecked():
            self.layerGroupBox.setChecked(False)

    def toggleChannelOption(self):
        if self.layerGroupBox.isChecked():
            self.channGroupBox.setChecked(False)

    def hideLayers(self, currentChannel):
        '''Hides unselected layers for bake'''
        mari.history.startMacro('Bake Selected (Hide Layers)')

        self.visibleLayers = []
        self.selectedLayers = []

        for layer in currentChannel.layerList():
            if layer.isVisible():
                self.visibleLayers.append(layer)
            if layer.isSelected():
                self.selectedLayers.append(layer)

        if len(self.selectedLayers) > 1:
            for layer in currentChannel.layerList():
                if layer in self.selectedLayers:
                    layer.setVisibility(True)
                else:
                    layer.setVisibility(False)
        else:
            self.selectedLayers = currentChannel.layerList()

        mari.history.stopMacro()

    def showLayers(self, currentChannel):
        '''Returns Layer visiblity'''
        mari.history.startMacro('Bake Selected (Show Layers)')

        for layer in currentChannel.layerList():
            if layer in self.visibleLayers:
                layer.setVisibility(True)
            else:
                layer.setVisibility(False)

        mari.history.stopMacro()

    def bakeSelected(self):
        currentGeo = mari.geo.current()
        currentChannel = mari.geo.current().currentChannel()
        selectedPatches = currentGeo.selectedPatches()

        self.hideLayers(currentChannel)

        uv_index = [i.uvIndex() for i in selectedPatches]
        if not uv_index:
            uv_index = [i.uvIndex() for i in currentGeo.patchList()]

        #Temp location
        temp_dir = self.customDir.text

        #New Channel Name
        customName = self.customName.text
        customPath = os.path.join(temp_dir, customName)
        customTemplate = '%s.$UDIM.tif' % customPath

        #-------------------------------------------------------------------------------------------
        #Bake selected to tmp
        currentChannel.exportImagesFlattened(customTemplate, 0, uv_index)

        bitDepth = self.channelBitDepthOptionCombo.currentText
        if bitDepth == 'Source':
            bitDepth = currentChannel.depth()
        else:
            bitDepth = int(bitDepth)
        #New Channel
        if self.channGroupBox.isChecked():
            destinationChannel = currentGeo.createChannel(customName, 4096, 4096, bitDepth)
            destinationChannel.importImages(customTemplate, 0, 0, 0, uv_index)
        #New Layer
        elif self.layerGroupBox.isChecked():
            destinationChannel = self.channelCombo.itemData(self.channelCombo.currentIndex, 32)
            newLayer = destinationChannel.createPaintableLayer(customName)
            newLayer.importImages(customTemplate, 0, uv_index)
        #-------------------------------------------------------------------------------------------

        self.showLayers(currentChannel)
        self.close()

#----------------------------------------------------------------------
# GUI
#----------------------------------------------------------------------
bakeSelectedITEM = mari.actions.create('Bake Selected', 'mari.utils.execDialog(bnBakeSelected.BakeSelectedDialog())')
bakeSelectedITEM.setIconPath('%s/Bake.png' % mari_icon_path)
mari.menus.addAction(bakeSelectedITEM, 'MainWindow/Channels', 'Flatten')
bakeSelectedITEM.setEnabled(False)

## Activation
def activation():
    if mari.projects.current():
        bakeSelectedITEM.setEnabled(True)
    else:
        bakeSelectedITEM.setEnabled(False)

mari.utils.connect(mari.projects.opened, activation)
mari.utils.connect(mari.projects.closed, activation)

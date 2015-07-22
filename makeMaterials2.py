## Make Material
from PySide import QtGui,QtCore
import mari

CSS_tree = "\\QTreeWidget { background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #404040, stop: 1 transparent); alternate-background-color: rgba(255, 255, 255, 3%);} \\"
CSS_colorButton = "background-color: rgba(%s, %s, %s, %s); border: 1px solid; border-radius: 3px;"

#=================================================================
def getActiveShaderInputs():
    '''Get list of active shader inputs
    '''
    mariGeo = mari.current.geo()

    for shader in mariGeo.shaderList():
        if shader.hasMetadata("isMaterialShader"):
            input_list = []
            for input_item in shader.inputList():
                inputChannel = input_item[1]
                inputName = input_item[0]
                if inputChannel:
                    input_list.append(input_item)
            return input_list
        else:
            continue

#=================================================================
def getMaterialChannels(material):
    '''Get Material Channels
    '''
    mariGeo = mari.current.geo()

    materialChannels = set()
    for channel in mariGeo.channelList():
        if channel.hasMetadata("material"):
            if channel.metadata("material") == material:
                materials.add(channel.name())

    return materialChannels


#=================================================================
def createColorLayer(layerstack, color):
    '''Create Color Procedural Layer
    '''
    r, g, b, a = color
    layer = layerstack.createProceduralLayer("Color", "Basic/Color")
    layer.setProceduralParameter("Color", mari.Color(r,g,b,a))
    layer.setMetadata("baseColor", True)
    layer.setMetadataFlags("baseColor", 16)

    return layer


#=================================================================
def setChannelMetadata(channel, materialName, channelType):
    '''Set Channel Metadata
    '''
    channel.setMetadata("material", materialName)
    channel.setMetadata("materialType", channelType)
    channel.setMetadataFlags("material", 1 | 16)
    channel.setMetadataFlags("materialType", 1 | 16)


#=================================================================
def createMaskChannel(materialName, channelType, element=False):
    '''Create Material Mask Channel
    '''

    mariGeo = mari.current.geo()

    maskChannelName = "%s_%s" % (materialName, channelType)
    newMaskChannel = mariGeo.createChannel(maskChannelName, 4096, 4096, 8)

    #Metadata
    if element:
        channelType = "element.%s" % channelType
    setChannelMetadata(newMaskChannel, materialName, channelType)

    #Base Layer
    color = [0.0, 0.0, 0.0, 1.0]
    createColorLayer(newMaskChannel, color)

    return newMaskChannel

#=================================================================
def createMaterialChannel(maskChannel, materialName, inputName, color):
    '''Create Material Channel
    '''
    mariGeo = mari.current.geo()

    customName = "m%s" % inputName
    materialChannelName = "%s_%s" % (materialName, customName)
    baseChannel = mariGeo.channel(customName)
    newChannel = mariGeo.createChannel(materialChannelName, 4096, 4096, 8)

    #Metadata
    setChannelMetadata(newChannel, materialName, inputName)

    #Base Layer
    createColorLayer(newChannel, color)

    #Create and link mask
    if baseChannel.findLayer("mGroup"):
        groupStack = baseChannel.layer("mGroup").groupStack()
    else:
        newGroup = baseChannel.createGroupLayer("mGroup")
        newGroup.setMetadata("materialGroup", True)
        newGroup.setMetadataFlags("materialGroup", 16)
        groupStack = newGroup.groupStack()

    linkLayer = groupStack.createChannelLayer(materialChannelName, newChannel)
    linkLayer.setMetadata("material", materialName)
    linkLayer.setMetadataFlags("material", 16)
    maskStack = linkLayer.makeMaskStack()
    maskStack.removeLayers(maskStack.layerList())

    maskStack.createChannelLayer(maskChannel.name(), maskChannel)

    return newChannel


#________________________________________________________________
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class CreateMaterial(QtGui.QDialog):
    materialCreated = QtCore.Signal()
    def __init__(self):
        super(CreateMaterial, self).__init__()

        #Layouts
        mainLayout = QtGui.QVBoxLayout()
        nameLayout = QtGui.QHBoxLayout()
        buttonLayout = QtGui.QHBoxLayout()
        self.setLayout(mainLayout)

        #Widgets
        materialNameLabel = QtGui.QLabel("Name:")
        self.materialName = QtGui.QLineEdit("New Material")
        self.materialTree = QtGui.QTreeWidget()
        cancelBtn = QtGui.QPushButton("Cancel")
        createBtn = QtGui.QPushButton("Create All")
        #--- tree settings
        self.materialTree.setColumnCount(3)
        self.materialTree.setHeaderHidden(True)
        self.materialTree.setRootIsDecorated(False)
        self.materialTree.setSelectionMode(self.materialTree.NoSelection)
        self.materialTree.setFocusPolicy(QtCore.Qt.NoFocus)
        self.materialTree.setAlternatingRowColors(True)
        self.materialTree.setStyleSheet(CSS_tree)

        #Populate Layouts
        buttonLayout.addWidget(cancelBtn)
        buttonLayout.addWidget(createBtn)
        nameLayout.addWidget(materialNameLabel)
        nameLayout.addWidget(self.materialName)
        mainLayout.addLayout(nameLayout)
        mainLayout.addWidget(self.materialTree)
        mainLayout.addLayout(buttonLayout)

        #Connections
        cancelBtn.clicked.connect(self.reject)
        createBtn.clicked.connect(self.makeMaterial)

        self.getInputs()

     #--------------------------------------------------------------------------------------------
    def getInputs(self):
        '''Create new items from active shader inputs
        '''

        inputChannels = getActiveShaderInputs()
        for pinput in inputChannels:
            inputName = pinput[0]
            inputChannel = pinput[1]
            if inputChannel:
                newItem = QtGui.QTreeWidgetItem()
                newItem.setText(0, inputName)
                newItem.setData(0, 32, inputChannel)
                newItem.setData(2, 32, [1.0, 1.0, 1.0, 1.0])
                self.materialTree.addTopLevelItem(newItem)
                self.makeColorButton(newItem)

        self.materialTree.resizeColumnToContents(0)
        self.materialTree.setColumnWidth(1, 85)
        self.materialTree.setColumnWidth(2, 45)

    #--------------------------------------------------------------------------------------------
    def makeColorButton(self, item):
        '''Makes Color Picker Button
        '''

        def getColor():
            color = mari.colors.pick(mari.colors.foreground())
            byteRGB = QtGui.QColor.fromRgbF(color.r(), color.g(), color.b(), a=color.a())
            colorButton.setStyleSheet(CSS_colorButton % (byteRGB.red(), byteRGB.green(), byteRGB.blue(), byteRGB.alpha()))
            data = [color.r(), color.g(), color.b(), color.a()]
            item.setData(2, 32, data)

        colorButton = QtGui.QPushButton(self)
        colorButton.setStyleSheet(CSS_colorButton % (255, 255, 255, 30))
        colorButton.setToolTip("Choose Base Color")
        colorButton.clicked.connect(getColor)

        colorWidget = QtGui.QWidget(self.materialTree)
        layout = QtGui.QHBoxLayout(colorWidget)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.addWidget(colorButton)
        colorWidget.setLayout(layout)

        self.materialTree.setItemWidget(item, 2, colorWidget)

    #--------------------------------------------------------------------------------------------
    def makeMaterial(self):
        '''Make material from specified settings
        '''

        materialName = self.materialName.text()

        #Make material mask channel
        maskChannel = createMaskChannel(materialName, "Mask")

        for index in range(self.materialTree.topLevelItemCount()):
            inputItem = self.materialTree.topLevelItem(index)
            inputName = inputItem.text(0)
            targetChannel = inputItem.data(0, 32)
            color = inputItem.data(2, 32)

            #Make material channel
            createMaterialChannel(maskChannel, materialName, inputName, color)

diag = CreateMaterial()
diag.show()

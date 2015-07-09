# Create Shader
from PySide import QtGui, QtCore
import mari

#________________________________________________________________
class CreateChannels(QtGui.QDialog):
    def __init__(self, parent):
        super(CreateChannels, self).__init__(parent)

        self.setParent(parent)

        #Common
        self.mariGeo = mari.current.geo()
        for shader in self.mariGeo.shaderList():
            if shader.hasMetadata("isMaterialShader"):
                self.mariShader = shader

        #Layouts
        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

        #Widgets
        self.inputList = QtGui.QListWidget()
        createChannelsBtn = QtGui.QPushButton("Create Channels")

        #Populate Layouts
        mainLayout.addWidget(self.inputList)
        mainLayout.addWidget(createChannelsBtn)

        #Connections
        createChannelsBtn.clicked.connect(self.createChannels)

        self.populateShaderInputs()

    #--------------------------------------------------------------------------------------------
    def populateShaderInputs(self):
        '''Detect available shader inputs
        '''

        self.inputList.clear()
        for input_item in self.mariShader.inputList():
            inputChannel = input_item[1]
            inputName = input_item[0]
            if not inputChannel:
                inputItem = QtGui.QListWidgetItem(inputName)
                inputItem.setCheckState(QtCore.Qt.Unchecked)
                self.inputList.addItem(inputItem)

    #--------------------------------------------------------------------------------------------
    def createChannels(self):
        '''Create channels and connect them to the shader
        '''

        #Build list of selected inputs
        input_list = []
        for index in range(self.inputList.count()):
            item = self.inputList.item(index)
            if item.checkState() == QtCore.Qt.Checked:
                input_list.append(item.text())

        #Build channels
        for input_name in input_list:
            custom_name = "m%s" % input_name
            newChannel = self.mariGeo.createChannel(custom_name, 4096, 4096, 8)
            newChannel.setMetadata("isMaterialChannel", True)
            newChannel.setMetadataFlags("isMaterialChannel", 1 | 16)
            baseLyr = newChannel.createProceduralLayer("Base", "Basic/Color")
            baseLyr.setProceduralParameter("Color", mari.Color(0.0, 0.0, 0.0))
            self.mariShader.setInput(input_name, newChannel)

        self.close()

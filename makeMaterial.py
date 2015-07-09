# Create Material
from PySide import QtGui,QtCore
import mari
import pickle

class CreateMaterial(QtGui.QDialog):
    def __init__(self, parent):
        super(CreateMaterial, self).__init__(parent)

        self.setParent(parent)

        #Layouts
        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

        #Widgets
        self.material_name = QtGui.QLineEdit()
        self.custom_elements = QtGui.QLineEdit()
        addBtn = QtGui.QPushButton("Add")

        #Populate Layouts
        mainLayout.addWidget(self.material_name)
        mainLayout.addWidget(self.custom_elements)
        mainLayout.addWidget(addBtn)

        #Connections
        addBtn.clicked.connect(self.createMaterial)

    #--------------------------------------------------------------------------------------------
    def createMaterial(self):
        '''Creates all elements of a Material
        '''

        mariGeo = mari.current.geo()
        materialName = self.material_name.text()

        #Find the valid shader
        for shader in mariGeo.shaderList():
            if shader.hasMetadata("isMaterialShader"):
                mariShader = shader

        #Attach material metadata (nees to be serialized)
        if not shader.hasMetadata("materials"):
            metadata = pickle.dumps([materialName])
            shader.setMetadata("materials", metadata)
            shader.setMetadataFlags("materials", 16)
        else:
            metadata = shader.metadata("materials")
            metadata = pickle.loads(str(metadata))
            metadata.append(materialName)
            metadata = pickle.dumps(metadata)
            shader.setMetadata("materials", metadata)

        ### Material Mask
        mask_name = "%s_%s" % (materialName, "Mask")
        #Create Channel
        maskChannel = mariGeo.createChannel(mask_name, 4096, 4096, 8)
        #Metadata
        maskChannel.setMetadata("material", materialName)
        maskChannel.setMetadata("materialType", "Mask")
        maskChannel.setMetadataFlags("material", 1 | 16)
        maskChannel.setMetadataFlags("materialType", 1 | 16)
        #Base Layer
        mskBaseLyr = maskChannel.createProceduralLayer("Base", "Basic/Color")
        mskBaseLyr.setProceduralParameter("Color", mari.Color(0.0,0.0,0.0))

        ### For each active channel input, create unique material channel
        for input_item in mariShader.inputList():
            inputChannel = input_item[1]
            inputName = input_item[0]
            if inputChannel:
                customName = "m%s" % inputName
                mat_channel_name = "%s_%s" % (materialName, customName)
                baseChannel = mariGeo.channel(customName)
                #Create Channel
                newChannel = mariGeo.createChannel(mat_channel_name, 4096, 4096, 8)
                #Metadata
                newChannel.setMetadata("material", materialName)
                newChannel.setMetadata("materialType", inputName)
                newChannel.setMetadataFlags("material", 1 | 16)
                newChannel.setMetadataFlags("materialType", 1 | 16)
                #Base Layer
                newBaseLyr = newChannel.createProceduralLayer("Base", "Basic/Color")
                newBaseLyr.setProceduralParameter("Color", mari.Color(0.0,0.0,0.0))
                #Create and link mask
                link_layer = baseChannel.createChannelLayer(mat_channel_name, newChannel)
                mask_stack = link_layer.makeMaskStack()
                mask_stack.createChannelLayer(mask_name, maskChannel)

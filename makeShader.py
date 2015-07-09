# Create Shader
from PySide import QtGui, QtCore
import mari

#________________________________________________________________
class ChooseShader(QtGui.QDialog):
    def __init__(self, parent):
        super(ChooseShader, self).__init__(parent)

        self.setParent(parent)
        self.setWindowTitle("Create Material Shader")

        #Common
        self.mariGeo = mari.current.geo()
        diffshaders = self.mariGeo.shaderDiffuseTypeList()
        specshaders = self.mariGeo.shaderSpecularTypeList()

        #Layouts
        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

        #Widgets
        self.diffshaderCombo = QtGui.QComboBox()
        self.specshaderCombo = QtGui.QComboBox()
        self.createShaderBtn = QtGui.QPushButton("Create Shader")
        #-----
        self.diffshaderCombo.addItems(diffshaders)
        self.specshaderCombo.addItems(specshaders)

        #Populate Layouts
        mainLayout.addWidget(self.diffshaderCombo)
        mainLayout.addWidget(self.specshaderCombo)
        mainLayout.addWidget(self.createShaderBtn)

        #Connections
        self.createShaderBtn.clicked.connect(self.createShader)


    #--------------------------------------------------------------------------------------------
    def createShader(self):
        '''Create a Material shader
        '''

        diffshader = self.diffshaderCombo.currentText()
        specshader = self.specshaderCombo.currentText()

        #Create Shader
        shader = self.mariGeo.createShader("mBeauty", diffshader, specshader)
        shader.setInput("DiffuseColor", None)
        self.mariGeo.setCurrentShader(shader)

        #Tag Shader
        shader.setMetadata("isMaterialShader", True)
        shader.setMetadataFlags("isMaterialShader", 16)

        self.close()

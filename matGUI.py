# Create Shader
from PySide import QtGui, QtCore

import sys
sys.path.append("/home/bneall/python/materialMaker")
import makeChannels
reload(makeChannels)
import makeMaterial
reload(makeMaterial)
import makeShader
reload(makeShader)


#________________________________________________________________
class MaterialGUI(QtGui.QDialog):
    def __init__(self):
        super(MaterialGUI, self).__init__()

        self.setWindowTitle("Materials")
        #self.setParent(parent)

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

        makeShaderBtn = QtGui.QPushButton("Make Shader")
        makeChannelsBtn = QtGui.QPushButton("Make Channels")
        makeMaterialBtn = QtGui.QPushButton("Make Material")

        mainLayout.addWidget(makeShaderBtn)
        mainLayout.addWidget(makeChannelsBtn)
        mainLayout.addWidget(makeMaterialBtn)

        makeShaderBtn.clicked.connect(self.makeShaderDiag)
        makeChannelsBtn.clicked.connect(self.makeChannelsDiag)
        makeMaterialBtn.clicked.connect(self.makeMaterialDiag)

    def makeShaderDiag(self):
        diag = makeShader.ChooseShader(self)
        diag.show()

    def makeChannelsDiag(self):
        diag = makeChannels.CreateChannels(self)
        diag.show()

    def makeMaterialDiag(self):
        diag = makeMaterial.CreateMaterial(self)
        diag.show()

diag = MaterialGUI()
diag.show()

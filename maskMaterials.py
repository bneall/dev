from PySide import QtGui, QtCore
import mari
import uuid

class maskMaterialWizard(QtGui.QDialog):
	def __init__(self):
		super(maskMaterialWizard, self).__init__()

		self.setWindowTitle("Mask Material Wizard")
		
		mainLayout = QtGui.QVBoxLayout()
		self.setLayout(mainLayout)

		self.maskControler = QtGui.QComboBox()
		self.destChannel = QtGui.QComboBox()
		self.setBtn = QtGui.QPushButton("set")
		
		mainLayout.addWidget(self.maskControler)
		mainLayout.addWidget(self.destChannel)
		mainLayout.addWidget(self.setBtn)
		
		for channel in mari.current.geo().channelList():
			self.maskControler.addItem(channel.name())
			self.destChannel.addItem(channel.name())

		self.setBtn.clicked.connect(self.setChannelMetadata)

	def setChannelMetadata(self):
		#Channel Names
		dest_channel_name = self.destChannel.currentText()
		mask_channel_name = self.maskControler.currentText()
		
		#Channel IDs
		dest_channel_ID = "%s_%s" % (dest_channel_name, uuid.uuid4())
		mask_channel_ID = "%s_%s" % (mask_channel_name, uuid.uuid4())

		#Channel Objects
		dest_channel = mari.current.geo().findChannel(dest_channel_name)
		mask_channel = mari.current.geo().findChannel(mask_channel_name)
		
		#Set Channel Metadata
		try:
			dest_channel.setMetadata("MM_dest", dest_channel_ID)
			mask_channel.setMetadata("MM_mask", mask_channel_ID)
			dest_channel.setMetadataFlags("MM_dest", 1 | 16 )
			mask_channel.setMetadataFlags("MM_mask", 1 | 16 )
		except:
			pass
		
		self.createMaskGroup(mask_channel, dest_channel)

	def createMaskGroup(self, mask_channel, dest_channel):
		maskGroup_name = mask_channel.name()
		maskGroup = dest_channel.createGroupLayer(maskGroup_name)
		maskGroup.setMetadata("MM_mask", mask_channel.metadata("MM_mask"))
		
		#Connect Mask as Layer Channel
		maskGroup_maskStack = maskGroup.makeMaskStack()
		maskGroup_maskStack.createChannelLayer(mask_channel.name(), mask_channel)
		
		#Create Layer Structure
		constant_base = maskGroup.layerStack().createProceduralLayer("Constant", "Basic/Constant")
		custom_group = maskGroup.layerStack().createGroupLayer("Custom")
		multiplier = maskGroup.layerStack().createProceduralLayer("Multiplier", "Basic/Color")
		multiplier.setProceduralParameter("Color", mari.Color(1,1,1))
		multiplier.setBlendMode(multiplier.MULTIPLY)
		custom_group.setBlendMode(custom_group.MULTIPLY)

class maskMaterialControler(QtGui.QDialog):
	def __init__(self):
		super(maskMaterialControler, self).__init__()
		
		mainLayout = QtGui.QVBoxLayout()
		self.setLayout(mainLayout)
		
		for channel in mari.current.geo().channelList():
			if channel.hasMetadata("MM_mask"):
				label = QtGui.QLabel(channel.name())
				slider = QtGui.QSlider(self)
				mainLayout.addWidget(label)
				mainLayout.addWidget(slider)
			
		
		
		#self.custom_mask_slider = QtGui.QSlider()
		#mainLayout.addWidget(self.custom_mask_slider)


#diag = maskMaterialWizard()
#diag.show()

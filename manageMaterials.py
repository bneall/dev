#Manage Materials

class MaterialWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(MaterialWidget, self).__init__(parent)

        self.setParent(parent)

        
        

#________________________________________________________________
class MaterialManager(QtGui.QDialog):
    def __init__(self):
        super(MaterialManager, self).__init__()

        self.setWindowTitle("Materials")

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)


diag = MaterialManager()
diag.show()

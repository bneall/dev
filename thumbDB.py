import PySide.QtSql as QtSql
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
import sqlite3
import glob
import time

input_path = '/home/bneall/Pictures/Stencils'
temp_path = '/usr/tmp/test'
pathList = glob.glob('%s/*' % input_path)

class CustomTHUMB(QtCore.QThread):
    '''This class generates thumbnails to disc'''

    #thumbGen = QtCore.Signal()
    #finishGen = QtCore.Signal()

    def __init__(self, filePath=None):
        super(CustomTHUMB, self).__init__()
        self.filePath = filePath

    def run(self):
        sourceImage = QtGui.QImage(filePath)
        thumbImage = sourceImage.scaled(int(gview_thumbSize),int(gview_thumbSize), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        thumbImage.save("%s/%s" % (temp_path, filePath), 'png', 75)
        #self.finishGen.emit()

def createTable():
    conn = sqlite3.connect('/usr/tmp/thumbs.db')
    conn.execute('''CREATE TABLE THUMBNAILS
                        (ID INT PRIMARY   KEY,
                        NAME                  TEXT,
                        SOURCEPATH       TEXT,
                        THUMBPATH        TEXT,
                        SOURCEDATE       TEXT,
                        THUMBDATE         TEXT
                        );''')

def insertRecord():
    conn = sqlite3.connect('/usr/tmp/thumbs.db')
    IDcounter = 0
    for path in pathList:
        imageID = IDcounter
        imageName = os.path.basename(path)
        sourcePath = path
        thumbPath = "%s/%s" % (temp_path, sourcePath)
        sourceDate = os.path.getmtime(sourcePath)
        thumbDate = None

        #GENERATE THUMBNAILS
        if os.path.exists(thumbPath):
            thumbDate = os.path.getmtime(thumbPath)
            if sourceDate > thumbDate:
                CustomTHUMB(sourcePath).exec_()
        else:
            os.makedirs(thumbPath)
            CustomTHUMB(sourcePath).exec_()
            thumbDate = time.time()

        sql = '''INSERT INTO THUMBNAILS
                (ID, NAME, SOURCEPATH, THUMBPATH, SOURCEDATE, THUMBDATE)
                VALUES (?, ?, ?, ?, ?, ?);'''
        conn.execute(sql,[imageID, imageName, sourcePath, thumbPath, sourceDate, thumbDate])
        conn.commit()
        IDcounter += 1
    conn.close()











#__________________________________________________________________________________________

def retrieveRecords():
    conn = sqlite3.connect('/usr/tmp/thumbs.db')
    cursor = conn.execute("SELECT id, name, path from DIRECTORY")
    for row in cursor:
        print "ID = ", row[0]
        print "NAME = ", row[1]
        print "PATH = ", row[2], "\n"
    conn.close()

def updateRecord():
    conn = sqlite3.connect('/usr/tmp/thumbs.db')
    conn.execute("UPDATE DIRECTORY set NAME = 'POOP' where ID=1")
    conn.commit()
    print "Total number of rows update: ", conn.total_changes
    conn.close()

    retrieveRecords()

def deleteRecord():
    conn = sqlite3.connect('/usr/tmp/thumbs.db')
    conn.execute("DELETE from DIRECTORY where ID=2")
    conn.commit()
    print "Total number of rows update: ", conn.total_changes
    conn.close()

    retrieveRecords()
    

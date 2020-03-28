""" ChikonEye Version 3.0 """

"""
1. OpenCV Video feed in GUI - done
2. Face Recognition 
2. Floating Buttons -done (needs work)
3. Button Callback functions 
                           0. Default Password
                           i. Training - password
                           ii. Password to QUIT
                           iii. Settings Menu - Set / Change Password

4. Adjust GUI size according to the Camera Frame H/W - nope
5. 
"""

""" Import All the necessary Libraries"""
import PyQt5  #QT GUI Library for python3
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtWidgets import *      #import everything
from PyQt5.QtGui import QPixmap, QIcon, QImage, QFont
import sys    #necessary fro QT applications
import cv2    #Open Source Computer Vision Library
import os


#get the path where the code is saved
pathz = os.path.dirname(os.path.abspath(__file__))
print(pathz)

#create dataset directory/folder
dir_path = f"{pathz}\\dataSet"
try:
    os.mkdir(dir_path)
except OSError:
    print("Folder exists or Error!")
else:
    print("created")


#classifier for face detection
face_cascade = cv2.CascadeClassifier(f'{pathz}\\haarcascade_frontalface_alt2.xml')

#Button Icon paths
x = f"{pathz}\\cam.png"
sett = f"{pathz}\\settings.png"
close = f"{pathz}\\exit.png"


"""needs to be set inside"""
# font 
font = cv2.FONT_HERSHEY_SIMPLEX 
# org 
org = (30, 20) 
# fontScale 
fontScale = 0.7
# Blue color in BGR 
color = (255, 255, 255)  
# Line thickness of 2 px 
thickness = 2


class ChikonEye(QWidget):
    """Main class that contains everything"""

    def __init__(self):
        super().__init__()

        self.f_width = 640   #frame width
        self.f_height = 375  #frame height

        #Load the Icons
        self.rec_icon = QIcon(x)
        self.settings_icon = QIcon(sett)
        self.close_icon = QIcon(close)

        self.timer = QTimer() #start timer
        self.timer.timeout.connect(self.view_cam)

        #disable close and maximize buttons on title bar
        #self.setWindowFlags(Qt.CustomizeWindowHint) #hide title bar
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint & ~Qt.WindowCloseButtonHint)
        #self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        
        
        self.ui()


    def ui(self):
        """User Interface section"""
        self.setWindowTitle("ChikonEye")
        self.setStyleSheet("Background-color: gray")
        self.setFixedSize(640, 376)

        #image viewer section
        self.imgl = QLabel(self)
        self.imgl.setGeometry(0,0, self.f_width, self.f_height)
        self.imgl.setStyleSheet("background-color: black; color: black; border-style: outset; border-width: 1px")


        if not self.timer.isActive():
            print("getting image")        #just to debug
            self.cap = cv2.VideoCapture(0) #Start getting frames
            self.timer.start(20)           #start timer

        self.notif = QLabel(self)
        self.notif.setText("yalalalalla")
        self.notif.move(50, 50)

        #button section
        self.but = QPushButton(self)
        self.but.setIcon(self.rec_icon)
        self.but.setStyleSheet('''background: transparent;
                                 border-top: 3px transparent;
                                 border-bottom: 3px transparent;
                                 border-right: 10px transparent;
                                 border-left: 10px transparent;
                                 ''')
        self.but.setIconSize(QSize(70, 70))
        self.but.setGeometry(570, 150, 70, 70)
        self.but.clicked.connect(self.kisu_na)

        self.close_but = QPushButton(self)
        self.close_but.setIcon(self.close_icon)
        self.close_but.setStyleSheet('''background: transparent; 
                                 border-top: 3px transparent;
                                 border-bottom: 3px transparent;
                                 border-right: 10px transparent;
                                 border-left: 10px transparent;
                                 ''')
        self.close_but.setIconSize(QSize(40, 40))
        self.close_but.setGeometry(600, 5, 40, 40)
        self.close_but.clicked.connect(self.exit)

        self.settings_but = QPushButton(self)
        self.settings_but.setIcon(self.settings_icon)
        self.settings_but.setStyleSheet('''background: transparent; 
                                 border-top: 3px transparent;
                                 border-bottom: 3px transparent;
                                 border-right: 10px transparent;
                                 border-left: 10px transparent;
                                 ''')
        self.settings_but.setIconSize(QSize(35, 35))
        self.settings_but.setGeometry(600, 330, 35, 35)
        self.settings_but.clicked.connect(self.settings_fun)




        self.show()



    def view_cam(self):
        """adds frame to QLabel"""
        ret, self.frame = self.cap.read()

        #try finding faces
        try:
            gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor = 1.5, minNeighbors = 5)
            for(x, y, w, h) in faces:
                #print(x, y, w, h)             
                self.roi_gray = gray[y: y+h, x: x+w]  #region of interest is face
                #*** Drawing Rectangle ***
                color = (255, 0, 0)
                stroke = 2
                end_cord_x = x+w
                end_cord_y = y+h
                cv2.rectangle(self.frame, (x,y), (end_cord_x, end_cord_y), color, stroke)

        except:
            pass



        #cv2.putText(self.frame, self.notificatin_text, (30, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255),  2, cv2.LINE_AA)
 
        #prepare image for QT
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        h, w, ch, = frame.shape
        step = ch * w
        q_frame = QImage(frame.data, w, h, step,QImage.Format_RGB888)

        self.imgl.setPixmap(QPixmap.fromImage(q_frame))
        self.notif.setText("Keya yaar")


    def train(self):
        """train the model using face roi and new ID"""
        id, okPressed = QInputDialog.getInt(self, "Enter ID name and Look at the camera","ID")
        if okPressed and id != 0:
            print(id)
        return

    def recognize(self, frame):
        """recognize faces based on pretrained .yml file"""
        return

    def kisu_na(self):
        pass

    def exit(self):
        """ check for password before closing the app"""
        i, okPressed = QInputDialog.getText(self, "Exit ChikonEye?","Password:", QLineEdit.Normal, "")
        #i, okPressed = QInputDialog.getInt(self, "Exit ChikonEye?","Password:")
        if okPressed:
            print(i)
            self.cap.release()
            self.close()


    def settings_fun(self):
        items = ("Train","Change Password","About Developer")

        #QInputDialog.setStyleSheet(self,"self{background-color: black;}" "QInputDialog {background-color: white ;}")
        item, okPressed = QInputDialog.getItem(self, "Settings","Select:", items, 0, False)
        
        if okPressed and item:
            print(item)
            if item == 'Train':
                self.train()   #start training
        


def main():
    app = QApplication(sys.argv)
    win = ChikonEye()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()  

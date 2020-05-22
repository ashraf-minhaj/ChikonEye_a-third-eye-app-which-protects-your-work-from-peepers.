""" ChikonEye Version 2.0.1 """

"""
License : GNU GENERAL PUBLIC LICENSE Version 3
© Author: Ashraf Minhaj
Email   : ashraf_minhaj@yahoo.com
Blog    : ashrafminhajfb.blogspot.com
"""
#Extending features


""" Import All the necessary Libraries"""
import PyQt5                               #QT GUI Library for python3
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtWidgets import *              #import everything
from PyQt5.QtGui import QPixmap, QIcon, QImage, QFont
import sys                                 #necessary fro QT applications
import cv2                                 #Open Source Computer Vision Library
import os
import datetime                            #to extract date and time
import numpy as np                         #to convert images into numpy array
from PIL import Image                      #Pillow for image operation
import subprocess



"""change lock code according to your OS"""
LOCK_CODE = "rundll32.exe user32.dll, LockWorkStation"  #for windows

"""Declare all static variables and DIR/Files"""
PARENT_PATH = os.path.dirname(os.path.abspath(__file__)) #get the path where the code is saved
#print(PARENT_PATH)

ICON_DIR = f"{PARENT_PATH}\\Icon"    #Contains icons, comes with the app
DATASET_DIR = "dataSet"              #contains face sample images, (created by sw)
VIDEO_RECORD_DIR = "Records"         #recorded videos will be saved in this directory/folder (sw)
DOC_FILE = "doc.txt"                 #file to save password (sw)
DEFAULT_PASSWORD = "6251"            #Default password of this app
TRAINED_FILE = "TrainData.yml"       #contains trained data, created after training (sw)
ID_FILE = f"{PARENT_PATH}\\ids.txt"  #id and corresponding names will be saved in it (sw)

FPS = 10                          #frames per second
DELAY_INTERVAL = 20               #to update frame after 20 ms
MAX_SAMPLE_COLLECTION_NUM = 50    #number of images to take for training
CONFIDENCE_THRESHOLD = 70         #face recognition confidence threshold

"""classifier for face detection"""
FACE_CASCADE = cv2.CascadeClassifier(f'{PARENT_PATH}\\haarcascade_frontalface_alt2.xml')
RECOGNIZER = cv2.face.LBPHFaceRecognizer_create()      #Local Binary Pattern Histograms

"""Button Icon Images"""
RECORD_ICON   = f"{ICON_DIR}\\cam.png"
SETTINGS_ICON = f"{ICON_DIR}\\settings.png"
CLOSE_ICON    = f"{ICON_DIR}\\exit.png"



"""create dataset directory/folder and document text file
   *looks for file & directory , if doesn't exist creates a new one
   *creating only occurs when the code runs for first time
   **if the folder/file deleted, will be created over again (empty)
"""
try:                                         #try statement -in case of err, code won't hault
    os.mkdir(f"{PARENT_PATH}\\{DATASET_DIR}")              #create directory/folder
except OSError:                              #if error found/file found
    print("Folder exists or Error!")
else:                                        #if not found at all                       
    """create necessary document folder for the first time"""
    document_file = open(f"{PARENT_PATH}\\{DOC_FILE}", 'w') #open in writing mode
    document_file.write(DEFAULT_PASSWORD")        #write default password
    document_file.close()                         #close to save file
    f = open(f"{ID_FILE}", 'w')
    f.close()
    print("created") 

"""Try to read trained file, it is not found before training any model"""
try:
    RECOGNIZER.read(f"{PARENT_PATH}\\{TRAINED_FILE}")
except:
    pass

"""make video record directory"""
try:                                         #try statement -in case of err, code won't hault
    os.mkdir(f"{PARENT_PATH}\\{VIDEO_RECORD_DIR}")              #create directory/folder
except OSError:                              #if error found/file found
    print("Folder exists or Error!")
    pass




class ChikonEye(QWidget):
    """Main class that contains everything"""

    def __init__(self):
        """this is where we initialize everything, runs only one time."""
        super().__init__()   #if any change occurs, it occurs to the mother too

        self.f_width = 640   #frame width
        self.f_height = 375  #frame height

        #Load the Icon images as QIcon for Qt
        self.rec_icon = QIcon(RECORD_ICON)
        self.settings_icon = QIcon(SETTINGS_ICON)
        self.close_icon = QIcon(CLOSE_ICON)

        self.timer = QTimer() #start timer
        self.timer.timeout.connect(self.camera_operation)  #connect function to call by timer

        #disable close and maximize buttons on title bar
        #self.setWindowFlags(Qt.CustomizeWindowHint) #hide title bar
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint & ~Qt.WindowCloseButtonHint)
        #self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        """ *Flags are changed by software, not hard coded"""
        self.RECORD_FLAG = False    #if True, records video
        self.TRAIN_FLAG  = False    #if True, takes face images, trains model
        self.FACE_FOUND  = False    #true if face found 
        self.RECOGNIZE_FLAG = True  #if true starts recognizing, false in training mode
        
        self.sample_num = 0   #training sample number
        self.counter    = 0   #counter for roi saving interval

        self.name_list()   #get list of trained names

        self.ui()       #run user interface


    def ui(self):
        """User Interface section"""
        self.setWindowTitle("ChikonEye")              #window title
        self.setStyleSheet("Background-color: gray")  #window background color
        self.setFixedSize(640, 376)                   #fixed window size 

        #image viewer section_____________
        #imgl label contains current frame and changes after a timer cycle,
        #thus we get a video feed
        self.imgl = QLabel(self)
        self.imgl.setGeometry(0,0, self.f_width, self.f_height)     #fill it to window
        self.imgl.setStyleSheet("background-color: black; color: black; border-style: outset; border-width: 1px")

        #if a timer cycle is complete
        if not self.timer.isActive():
            print("getting image")            #just to debug
            self.cap = cv2.VideoCapture(0)    #Start getting frames
            self.timer.start(DELAY_INTERVAL)  #start timer


        #_______________________________________button section_____________________________________________________

        #button to record video
        self.record_but = QPushButton(self)
        self.record_but.setIcon(self.rec_icon)
        self.record_but.setStyleSheet('''background: transparent;
                                 border-top: 3px transparent;
                                 border-bottom: 3px transparent;
                                 border-right: 10px transparent;
                                 border-left: 10px transparent;
                                 ''')
        self.record_but.setIconSize(QSize(70, 70))
        self.record_but.setGeometry(570, 150, 70, 70)
        #self.record_but.setCheckable(True)
        #self.record_but.toggled.connect(self.record_button_action)  
        self.record_but.clicked.connect(self.record_button_action)  #connect with callback function

        #close/exit button
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
        self.close_but.clicked.connect(self.exit)                  #callback function

        #settings button
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
        self.settings_but.clicked.connect(self.settings_fun)       #callback function


        self.show()        #Show the User Interface



    def camera_operation(self):
        """adds frame to QLabel"""
        ret, self.frame = self.cap.read()  #get frame/ read from camera

        #try finding faces
        try:
            gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor = 1.5, minNeighbors = 5)
            #print(faces)
            for(x, y, w, h) in faces:
                #print(x, y, w, h)             
                self.roi_gray = gray[y: y+h, x: x+w]  #region of interest is face
                #Drawing Rectangle
                color = (255, 0, 0)
                stroke = 2
                end_cord_x = x+w
                end_cord_y = y+h
                cv2.rectangle(self.frame, (x,y), (end_cord_x, end_cord_y), color, stroke)
                self.FACE_FOUND = True

                """While training if more than one face detected"""
                if (self.TRAIN_FLAG == True) and (len(faces) > 1):
                    self.pop_window(title="Warning", msg="Training takes only one face. \nMultiple face detected.")
                    self.FACE_FOUND = False

                """recognize faces, show with name"""
                if self.RECOGNIZE_FLAG == True:
                    Id, confidence = RECOGNIZER.predict(self.roi_gray)
                    print(confidence)
                
                    name = self.names[Id-1] #get corresponding name

                    """if id not found, lock the screen"""
                    if (confidence > CONFIDENCE_THRESHOLD) and (self.RECOGNIZE_FLAG == True):
                        subprocess.call(LOCK_CODE)
                        print("Unknown")

                """put name with face bouding box"""
                #if confidence value less than threshold value,
                #the smalller the value the better the accuracy
                if (name in self.names) and (confidence < CONFIDENCE_THRESHOLD) and (self.TRAIN_FLAG == False):
                    cv2.putText(self.frame, name, (x, y+w+20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (250, 250, 250))
                    print(Id)



                    
        except:
            #self.FACE_FOUND = False
            pass #run anyway
        

        #_______________________Check record flag____________________________________
        #print(self.RECORD_FLAG)
        if self.RECORD_FLAG == True:
            print("Recording man!")
            self.video_writer.write(self.frame)
            #notify on image about recording
            cv2.putText(self.frame, "Recording..", (5, 380), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

        #_______________________Train model with new face____________________________
        #print(self.TRAIN_FLAG)
        if self.TRAIN_FLAG == True:
            #print("Training Mode")
            #notify about Training
            cv2.putText(self.frame, "Training Mode", (5, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            #put sample number on screen
            cv2.putText(self.frame, str(self.sample_num), (10, 300), cv2.FONT_HERSHEY_COMPLEX, 4, (255, 255, 255), 2, cv2.LINE_AA)
            
            self.counter += 1    #start counter
            #print(self.counter)
            
            if self.sample_num == MAX_SAMPLE_COLLECTION_NUM:  #reached max sample number
                cv2.putText(self.frame, "Training, wait!", (10, 350), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 255, 255), 1, cv2.LINE_AA)
                self.update_img_label(self.frame)
                self.sample_num = 0                           #set sample number to zero
                self.TRAIN_FLAG = False                       #stop saving
                self.pop_window(title="INFO", msg="Sample images collected, Train?")

                self.train()


            elif (self.counter == 12) and (self.FACE_FOUND == True): #after 1 sec and if face found
                print("saving roi")
                self.sample_num += 1       #increment sample number
                cv2.imwrite(f"{PARENT_PATH}\\{DATASET_DIR}\\user.{self.id}.{self.sample_num}.jpg", self.roi_gray)
                
                self.counter = 0           #make it zero
                self.FACE_FOUND = False    #False, wait for next face confirmation

            elif self.counter == 12:
                print("Waiting for face")
                self.counter = 0
            

        
        #_______________set current frame in QLabel___________________
        self.update_img_label(self.frame)


    def update_img_label(self, f):
        """update image label"""
        #prepare image for QT
        #cv2.putText(f, 'ChikonEye', (10, 300), cv2.FONT_HERSHEY_COMPLEX, 4, (255, 0, 255), 2, cv2.LINE_AA)
        img = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)   #convert BGR to RGB for QT
        h, w, ch, = img.shape        #get frame shape
        step = ch * w
        q_frame = QImage(img.data, w, h, step,QImage.Format_RGB888)
        self.imgl.setPixmap(QPixmap.fromImage(q_frame))  #set image to label
        return

    def settings_fun(self):
        items = ("Train", "Change Password", "About Developer")

        #QInputDialog.setStyleSheet(self,"self{background-color: black;}" "QInputDialog {background-color: white ;}")
        item, okPressed = QInputDialog.getItem(self, "Settings","Select:", items, 0, False)
        
        if okPressed and item:
            print(item)
            if item == 'Train':
                self.capture_samples()   #start training procedure
            if item == 'Change Password':
                self.change_password()
            if item == "About Developer":
                self.about_developer()
        return

    def capture_samples(self):
        """capture_samples  with new ID"""
        self.RECOGNIZE_FLAG = False    #stop recognizing
        input_pass, okPressed = QInputDialog.getText(self, "Enter Password", "Password:", QLineEdit.Normal, "")

        if not okPressed:
            self.RECOGNIZE_FLAG = True    #start recognizing
            return

        elif okPressed:
            doc =  open(f"{PARENT_PATH}\\{DOC_FILE}", 'r') #open in read mode
            current_pass = doc.read() #read the password
            doc.close()

            if current_pass == input_pass:
                pass
            else:
                self.RECOGNIZE_FLAG = True    #start recognizing
                return

        self.id, okPressed = QInputDialog.getInt(self, "Enter ID (1, 2, 3 etc.)", "ID:")
        if okPressed and self.id != 0:
            print(self.id)
            name, ok = QInputDialog.getText(self, "Enter ID name and Look at the camera", "Name:")

            if ok:
                print(name)
                """save the new name to file"""
                id_f = open(ID_FILE, 'a')
                id_f.write(f"{name},")
                id_f.close()

            self.name_list()
            self.TRAIN_FLAG = True
        else:
            self.RECOGNIZE_FLAG = True
        return

    def name_list(self):
        """reads the id file and generates a name list for python"""        
        id_f = open(ID_FILE, 'r')
        names = id_f.read()
        self.names = names.split(',')
        id_f.close()                   #close the file to save
        print(self.names)

        return


    def change_password(self):
        """change password"""
        input_pass, okPressed = QInputDialog.getText(self, "Change Password?", "Old Password:", QLineEdit.Normal, "")

        if not okPressed:
            return

        elif okPressed:
            doc =  open(f"{PARENT_PATH}\\{DOC_FILE}", 'r') #open in read mode
            current_pass = doc.read() #read the password
            new_pass, okPressed = QInputDialog.getText(self, "Change Password?", "New Password:", QLineEdit.Normal, "")

            if current_pass == input_pass:
                doc =  open(f"{PARENT_PATH}\\{DOC_FILE}", 'w') #open in append mode
                doc.write(new_pass)                            #write the new password
                doc.close()                                    #close the file to save
                print("Right bro")
                self.pop_window(title="Successful", msg="Password changed successfully.")
            
            else:
                try:
                    doc.close()  #close the file to save
                except:
                    pass
                self.pop_window(title="Password Error", msg="Ivalid Password!\tTry again.")
        
        return

    def about_developer(self):
        """something about the developer"""
        self.pop_window(title="About", 
        msg="ChikonEye Version: 2.0.1 \nDeveloper Info:\nName    : Ashraf Minhaj \nEmail   : ashraf_minhaj@yahoo.com \nsite    : ashrafminhajfb.blogspot.com \nyouTube : fusebatti")

    def train(self):
        """after taking images, train a model and generate .yml file"""
        faces = []  #empty list for faces
        Ids = []    #empty list for Id's
        path = f"{PARENT_PATH}\\{DATASET_DIR}"    #dataset path

        #join each and every image paths
        image_paths = [os.path.join(path, i) for i in os.listdir(path)]
        #print(image_paths)

        for image in image_paths:
            face_img = Image.open(image).convert('L')        #Pillow Image
            np_face = np.array(face_img, 'uint8')            #into numpy array - usigned 8 bit -1byte
            Id = int(os.path.split(image)[-1].split('.')[1]) #get id from image path
            #print(Id)
            faces.append(np_face)     #append in faces array/list
            Ids.append(Id)            #append in Ids list/array

        RECOGNIZER.train(faces, np.array(Ids))  #train model using faces and Id (numpy arrays)
        RECOGNIZER.save(f"{PARENT_PATH}\\{TRAINED_FILE}")

        self.pop_window(title="Restart Needed!", msg="Training Successful.\nRestart the app Now.")
        return


    def exit(self):
        """ check for password before closing the app"""
        i, okPressed = QInputDialog.getText(self, "Exit ChikonEye?", "Password: ", QLineEdit.Normal, "")
        #i, okPressed = QInputDialog.getInt(self, "Exit ChikonEye?","Password:")
        if okPressed:
            #open doc.txt to cross check the password
            doc =  open(f"{PARENT_PATH}\\{DOC_FILE}", 'r') #open in read mode
            password = doc.read() #read the password
            doc.close()

            if password:  #if file read is successful
                if i == password:
                    print("Macthed")
                    self.cap.release()
                    self.close()
                    return

        elif not okPressed:
            return
          
        self.pop_window(title="Error", msg="Password did not Match!")


    def pop_window(self, title="ERROR", msg="Something is wrong!", icon=QMessageBox.Critical):
        """show error message"""
        msg_box = QMessageBox()                       #QMessagebox pops up
        msg_box.setDefaultButton(QMessageBox.Close)   #Set button
        msg_box.setWindowTitle(title)                 #title
        msg_box.setText(msg)                          #inside message
        msg_box.setIcon(icon)                         #Icon
        msg_box.exec_()                               #run it untill user quits/clicks button

        return

    def record_button_action(self):
        """change record flag, set filename"""
        #on button click Stop/Start recording
        if self.RECORD_FLAG == True:   #if recording
            self.RECORD_FLAG = False   #stop recording
            return  #and quit
        
        #frame height width
        size = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        
        # ** filename - 'date_time.avi'
        #get time date
        dt = datetime.datetime.now()
        # %b month - %Y year - day %d - %H Hour - %M minute - %S second
        # *Zero padded
        str_dt = (str(dt.strftime('%b')) 
                + str(dt.strftime('%Y')) 
                + str(dt.strftime('%d'))
                + "_"
                + str(dt.strftime('%H'))
                + str(dt.strftime('%M'))
                + str(dt.strftime('%S'))
                 )
        #print(str_dt)

        self.video_writer = cv2.VideoWriter(
            f"{PARENT_PATH}//{VIDEO_RECORD_DIR}//rec{str_dt}.avi",
            cv2.VideoWriter_fourcc('I', '4', '2', '0'),
            FPS, size)

        self.RECORD_FLAG = True   #start recording
        return

def main():
    app = QApplication(sys.argv)
    win = ChikonEye()

    sys.exit(app.exec_())

#run the application
if __name__ == '__main__':
    main()  

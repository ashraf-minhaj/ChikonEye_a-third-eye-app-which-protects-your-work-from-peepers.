"""
ChikonEye literally watches your back.
preventing others who peeps your computer from seeing your valuable secret works.
Now your works are safe and secure.

Chikon eye uses your laptop(primary = 0 or secondary = 1, 2 so on) camera to see how 
many people are watching at the computer screen. If some1 unauthorized tries to see 
it automatically locks the computer screen.

developed by Ashraf Minhaj
mail me at- ashraf_minhaj@yahoo.com
"""

"""
Version: Completely in testing period.
I'll make and executable .exe file so that this can be run on any computer.
right now it can be used by the people who has python, numpy, opencv pyautogui
installed in their pc. Don't worry exe is coming soon.
"""
"""
This is the recognizer code, after creating dataset and training the model
you can use this. Other associated files and codes will be uploaded soon
"""

import numpy as np  #numpy library as np
import cv2       #openCv library
import pyautogui  #pyautogui 
from time import sleep  #time library 

pyautogui.FAILSAFE = False   #pyautogui failsafe to false (see doc)

#location of opencv haarcascade <change according to your file location>
face_cascade = cv2.CascadeClassifier('F:\\opencv\\sources\\data\\haarcascades\\haarcascade_frontalface_alt2.xml') 
cap = cv2.VideoCapture(0)   # 0 = main camera , 1 = extra connected webcam and so on.
rec = cv2.face.LBPHFaceRecognizer_create()


rec.read("C:\\Users\\HP\\cv_practice\\attempt2\\trainData.yml")  #yml file location <change as yours>
id = 0  #set id variable to zero

font = cv2.FONT_HERSHEY_COMPLEX 
col = (255, 0, 0)
strk = 2 
while True:  #This is a forever loop
    ret, frame = cap.read() #Capture frame by frame 
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #change color from BGR to Gray
    faces = face_cascade.detectMultiScale(gray, scaleFactor = 1.5, minNeighbors = 5)

    #print(faces)
    for(x, y, w, h) in faces:
        #print(x, y, w, h)
        roi_gray = gray[y: y+h, x: x+w]  #region of interest is face

        #*** Drawing Rectangle ***
        color = (255, 0, 0)
        stroke = 2
        end_cord_x = x+w
        end_cord_y = y+h
        cv2.rectangle(frame, (x,y), (end_cord_x, end_cord_y), color, stroke)

        #***detect
        id, conf = rec.predict(roi_gray)
        #cv2.putText(np.array(roi_gray), str(id), font, 1, col, strk)
        print(id) #prints the id's
        
        #if sees unauthorized person
        if id != 1 and id != 5 and id == 2 or id == 3 or id == 4 or id == 6 or id == 7: 
            #execute lock command
            pyautogui.hotkey('win', 'r')   #win + run key combo
            pyautogui.typewrite("cmd\n")   # type cmd and 'Enter'= '\n'
            sleep(0.500)       #a bit delay <needed!>
            #windows lock code to command prompt and hit 'Enter'
            pyautogui.typewrite("rundll32.exe user32.dll, LockWorkStation\n") 

        elif id == 1 or id == 5:      #if authorized person (me & my Brother Siam)
            print("Authorized Person\n") #do nothing

        
    
    cv2.imshow('ChikonEye', frame)

    #check if user wants to quit the program (pressing 'q')
    if cv2.waitKey(10) == ord('q'):
        x = pyautogui.confirm("Close the Program 'ChikonEye'?") 
        if x == 'OK':
            break

cap.release()
cv2.destroyAllWindows() #remove all windows we have created

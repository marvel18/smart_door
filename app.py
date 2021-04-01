import streamlit as st
import pandas as pd
import cv2
from FaceRecognition.face_reco import FaceRecognition
import os
import numpy as np
import time
class App:
    DATE_COLUMN = 'date and time'
    DATA_URL = 'data.csv'
    
    def  __init__(self):
        pass
    def load_data(self , nrows):
        data = pd.read_csv(self.DATA_URL, nrows=nrows)
        lowercase = lambda x: str(x).lower()
        data.rename(lowercase, axis='columns', inplace=True)
        data[self.DATE_COLUMN] = pd.to_datetime(data[self.DATE_COLUMN])
        return data
    def home(self):
        f = st.empty()
        data = self.load_data(10000)
        f.subheader('LOGIN IN DATA')
        f.table(data[['name' , 'confidence' , 'temperature' , 'fever' , 'date and time']])
        st.button('refresh')    
    def live_cam(self):
        cam =cv2.VideoCapture(0)
        fr = FaceRecognition()
        with st.spinner("Training Model"):
            fr.train()
            fr.load()
        st.balloons()    
        st.subheader('Live Cam')
        frame = st.image([])
        while True:
            ret  , img = cam.read()
            name , confidence , img  = fr.predict(img)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            frame.image(img)        
    def settings(self):
        my_expander = st.beta_expander("Add Face Data", expanded=False)
        with my_expander :
            name = st.text_input('Enter Name :')
            if(name != ''):
                options = st.multiselect('get facedata from ',['upload' , 'picamera'])
                cwd = os.path.abspath(os.path.dirname(__file__))
                path = os.path.abspath(os.path.join(cwd, "FaceRecognition/dataset"))
                face_detector = cv2.CascadeClassifier('FaceRecognition/haarcascade_frontalface_default.xml')
                picamera= st.beta_container()
                if 'picamera' in options:
                        info = picamera.info("Look at the camera for some time")
                        frame = picamera.image([])
                        cam =cv2.VideoCapture(0)
                        count = 0
                        progress_bar1= picamera.progress(0)
                        while count<30:
                            ret , img  = cam.read()
                            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                            faces = face_detector.detectMultiScale(gray, 1.3, 5)
                            for (x,y,w,h) in faces:
                                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
                                count += 1
                                progress_bar1.progress((count/30))
                                loc = str(path) + "/User." + str(name) + '.' + str(count) + ".jpg"
                                cv2.imwrite(loc, gray[y:y+h,x:x+w])
                            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)    
                            frame.image(img)
                        progress_bar1.empty()
                        info.empty()    
                        picamera.success(name + 's face added successfully')
                        frame.image([])
                upload_expand = st.beta_container()            
                if 'upload' in options:
                    uploaded_files = st.file_uploader("Choose a image file", type="jpg",accept_multiple_files=True)
                    progress_bar2= st.progress(0)
                    c=0
                    count = 0
                    for file in uploaded_files:
                        file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
                        st.write("filename:", file.name)
                        img= cv2.imdecode(file_bytes, 1)
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        faces = face_detector.detectMultiScale(gray, 1.3, 5)
                        c=c+1
                        progress_bar2.progress(c/len(uploaded_files))
                        time.sleep(0.1)
                        for (x,y,w,h) in faces:
                                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
                                count += 1
                                loc = str(path) + "/User." + str(name) + '.' + str(count) + ".jpg"
                                cv2.imwrite(loc, gray[y:y+h,x:x+w])
                    uploaded_files = []            
                    if c!=0 :
                        progress_bar2.empty()            
                        st.success(name + 's facedata uploaded successfully')
                                            
    def main(self):
        st.title("Smart Door")
        nav  = st.sidebar.radio("Navigation" , ["Home" , "Sensor" , "Camera",'Settings'])
        if nav == "Home":
            self.home()
        elif nav == "Sensor" :
            st.write("Sensor data")    
        elif nav=='Camera' :
            self.live_cam()
        elif( nav == 'Settings'):
            self.settings()    
            
            
if __name__ == "__main__":
    App().main()
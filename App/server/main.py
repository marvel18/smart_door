import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from configparser import ConfigParser
import cv2
from FaceRecognition.face_reco import FaceRecognition
from client import Video_Stream
import os
import PIL
import numpy as np
import time
class App:
    DATE_COLUMN = 'date and time'
    #PATH = "/data/"
    PATH = ""
    DATA_URL = PATH+'data.csv'
    def  __init__(self):
        self.conf = ConfigParser()
        self.conf.read(self.PATH+'config.ini')
        if(self.authenticate()):
            self.main() 
    @st.cache(suppress_st_warning=True)        
    def authenticate(self):
        login_page = st.empty()
        password = login_page.text_input('Enter password',type = 'password')
        if(self.conf['LOGIN']['password'] == password):
            login_page.empty()
            return True
        elif(password != ''):
            st.warning('incorrect password')
        st.caching.clear_cache()
        return False   
    def load_data(self , nrows):
        try:    
            data = pd.read_csv(self.DATA_URL, nrows=nrows)
        except :
            data =pd.DataFrame(columns=  ["Date and Time" , "Name" ,"Confidence" , "Temperature" ,"fever" ])    
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
        vid_st = Video_Stream()
        if not vid_st.connect() :
            st.error("could not connect to pi")
            return  
        st.subheader('Live Cam')
        frame = st.empty()
        while True:
            img = vid_st.get_frame()
            #name , confidence , img  = fr.predict(img)
            img = cv2.resize(img, (0,0), fx = 0.5, fy = 0.5)
            #img = cv2.resize(img, (320, 320))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            frame.image(img)
    def settings(self):
        add_face_expander = st.expander(label  = "Add Face Data", expanded=False)
        with add_face_expander :
            name = st.text_input('Enter Name :')
            if(name != ''):
                options = st.multiselect('get facedata from ',['upload' , 'picamera'])
                cwd = os.path.abspath(os.path.dirname(__file__))
                path = os.path.abspath(os.path.join(cwd,self.PATH+"/dataset/"))
                face_detector = cv2.CascadeClassifier('FaceRecognition/haarcascade_frontalface_default.xml')
                picamera= st.container()
                if 'picamera' in options:
                        info = picamera.info("Look at the camera for some time")
                        frame = picamera.image([])
                        cam =cv2.VideoCapture(0)
                        count = 0
                        progress_bar1= picamera.progress(0)
                        while count<30:
                            ret , img  = cam.read()
                            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                            faces = face_detector.detectMultiScale(gray, 1.5, 5)
                            if(len(faces)!=0):
                                x,y,w,h = faces[0]
                                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
                                count += 1
                                progress_bar1.progress((count/30))
                                loc = str(path) + "/User." + str(name) + '.' + str(count) + ".jpg"
                                cv2.imwrite(loc, gray[y:y+h,x:x+w])
                            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)    
                            frame.image(img)
                            cv2.waitKey(1)
                        progress_bar1.empty()
                        info.empty()    
                        picamera.success(name + 's face added successfully')
                        frame.image([])
                        cv2.waitKey(1)       
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
        ce= st.expander("Configurations" , expanded = False)
        with ce :
            ce.subheader("FACE RECOGNITION")
            face_config = self.conf['RECO_CONF']
            face_config['min_confidence'] =str(ce.slider('THRESHOLD CONFIDENCE' , 0 , 100 , int(face_config['min_confidence'])))
            face_config['no_face'] = str(ce.number_input('NO FACES DETECT AT A TIME ',value = int(face_config['no_face'])))
            ce.subheader("SENSORS")
            sensor_config = self.conf['SENSOR_CONF']
            sensor_config['max_temp'] =str(ce.slider('THRESHOLD TEMPERATURE' , 0 , 150, int(sensor_config['max_temp'])))
            pump_config = self.conf['PUMP_CONF']
            pump_config['pump_time'] = str(ce.number_input('MOTOR PUMP TIME(s)',value = int(pump_config['pump_time'])))
            pump_config['pump_pin'] = str(ce.number_input('MOTOR PUMP PIN',value = int(pump_config['pump_pin'])))
            lock_config = self.conf['LOCK_CONF']
            lock_config['lock_pin'] = str(ce.number_input('LOCK PIN',value = int(lock_config['lock_pin'])))
            distance_sensor_config = self.conf['DISTANCE_SENSOR']
            distance_sensor_config['min_dist'] = str(ce.slider('MINIMUM DISTANCE(cm)' , 0 , 100 , int(distance_sensor_config['min_dist'])))
            distance_sensor_config['trig_pin'] = str(ce.number_input('TRIGGER PIN ',value = int(distance_sensor_config['trig_pin'])))
            distance_sensor_config['echo_pin'] = str(ce.number_input('ECHO PIN ',value = int(distance_sensor_config['echo_pin'])))
        se=st.expander("Security Settings" , expanded = False)
        with se :
            login_config = self.conf['LOGIN']
            password = str(se.text_input('Enter Password ',type='password',value = ''))
            if( password == login_config['password'] ):
                newpass = str(se.text_input('Enter New Password ',type='password'))
                retype_newpass = str(se.text_input('Retype New Password ',type='password'))
                if(se.button('submit') and newpass == retype_newpass):
                    login_config['password'] = newpass
                    se.success("Password changed succesfully")
            elif(password != ''):
                se.warning("incorrect password")        
        with open('config.ini' , 'w') as conf :
            self.conf.write(conf)
                                                               
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
        if(st.sidebar.button("logout")):
            st.caching.clear_cache()
if __name__ == "__main__":
    App()   
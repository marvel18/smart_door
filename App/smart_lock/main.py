import pandas as pd
from FaceRecognition.face_reco import FaceRecognition
import cv2
from datetime import datetime
from configparser import ConfigParser
import RPi.GPIO as GPIO
import time
from threading import Thread

class LOCK():
    def __init__(self):
        self.running = True
        self.locked = False
        self.save_data = True
        self.load_data()
        self.fr = FaceRecognition()
        self.conf = ConfigParser()
        self.conf.read('/usr/src/appdata/config.ini')
        self.init_RPi()
    def init_RPi(self):
        self.lock_conf = self.conf['LOCK_CONF']
        self.lock_pin  = int(self.lock_conf['lock_pin'])
        self.lock_in_pin  = int(self.lock_conf['lock_in_pin'])
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.lock_pin,GPIO.OUT)
        GPIO.output(self.lock_pin,GPIO.LOW)
        GPIO.setup(self.lock_in_pin,GPIO.IN)    
    def load_data(self):
        try:
            self.df = pd.read_csv("/usr/src/appdata/data.csv",index_col=0)
        except :
            self.df =pd.DataFrame(columns=  ["Date and Time" , "Name" ,"Confidence" , "Temperature" ,"fever" ])
    def run(self):
        if not self.train():
            print("training error")
            exit()
        self.start_camera()        
        self.recogonize()
    def stop(self):
        self.running = False        
    def start_camera(self):
        self.cam = cv2.VideoCapture(0)
    def stop_camera(self):
        self.cam.release()
    def train(self):
        if not self.fr.train():
            return False
        self.fr.load()
        self.fr.stopcam()
        return True
    def saveData(self,name , confidence):
        if not self.save_data :
            return
        print(name , confidence)
        now = datetime.now()
        self.df = self.df.append({"Date and Time":now , 'Name' :name  , 'Confidence' : confidence},ignore_index=True)
        print(self.df)
        self.df.to_csv("data.csv")
    def unlock(self):
        self.locked=False
        GPIO.output(self.lock_pin,GPIO.LOW)
    def lock(self):
        self.locked = True
        GPIO.output(self.lock_pin,GPIO.HIGH)
    def recogonize(self):
        print("looking for faces")
        start_time = 0    
        while(self.running):
            ret  , img = self.cam.read()
            name , confidence , img  = self.fr.predict(img)
            if(GPIO.input(self.lock_in_pin)==1):
                if(start_time==0):
                    start_time = time.time()
                if(self.locked is False):
                    if(time.time() - start_time > 10):
                        self.lock()
                elif((name != None ) and (name !="unknown")):
                    self.saveData(name,confidence)
                    self.unlock()
                    start_time = 0
            elif(start_time!=0):
                start_time = 0
            cv2.waitKey(1)
        return False    
  
if __name__ == '__main__':
    LOCK().run()
    
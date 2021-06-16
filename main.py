import pandas as pd
from FaceRecognition.face_reco import FaceRecognition
import cv2
from datetime import datetime
from configparser import ConfigParser
import Rpi.GPIO as GPIO
import time
from threading import Thread

GPIO.setmode(GPIO.BCM)

class LOCK(Thread):
    def __init__(self):
        self.running = True
        self.save_data = True
        self.load_data()
        self.fr = FaceRecognition()
        self.conf = ConfigParser()
        self.conf.read('config.ini')
        self.init_RPi()
    def init_RPi(self):
        self.lock_conf = self.conf['LOCK_CONF']
        self.lock_pin  = self.lock['lock_pin']
        self.lock_in_pin  = self.lock['lock_in_pin']
        GPIO.setup(self.lock_pin,GPIO.OUT)
        GPIO.setup(self.lock_in_pin,GPIO.IN)    
    def load_data(self):
        try:
            self.df = pd.read_csv("data.csv",index_col=0)
        except :
            self.df =pd.DataFrame(columns=  ["Date and Time" , "Name" ,"Confidence" , "Temperature" ,"fever" ])
    def run(self):
        self.train()
        self.start_camera()        
        self.recogonize()
    def stop(self):
        self.running = False        
    def start_camera(self):
        self.cam = cv2.VideoCapture(0)
    def stop_camera(self):
        self.cam.release()
    def train(self):
           self.fr.train()
           self.fr.load()
    def saveData(self,name , confidence):
        if not self.save_data :
            return
        print(name , confidence)
        now = datetime.now()
        self.df = self.df.append({"Date and Time":now , 'Name' :name  , 'Confidence' : confidence},ignore_index=True)
        print(self.df)
        self.df.to_csv("data.csv")
    def unlock(self):
        GPIO.output(self.lock_pin,GPIO.HIGH)
        while GPIO.input(self.lock_in_pin)==0:
            pass
        time.sleep(5)
        GPIO.output(self.lock_pin,GPIO.LOW)
        self.recogonize()
    def recogonize(self):     
        while(self.running):
            ret  , img = self.cam.read()
            name , confidence , img  = self.fr.predict(img)
            if(name  != None and name !="unknown"):
                self.saveData(name,confidence)
                self.unlock()
            if cv2.waitKey(10) == 27:
                return False
            cv2.imshow("camera " , img)
        return False    
  
class Sanitize(Thread):
    def __init__(self):
        self.conf = ConfigParser()
        self.conf.read('config.ini')
        self.init_RPi()
    def init_RPi(self):
        self.dist_sensor_conf = self.conf['DISTANCE_SENSOR']
        self.trig_pin = self.dist_sensor_conf['trig_pin']
        self.echo_pin = self.dist_sensor_conf['echo_pin']
        self.min_dist = self.dist_sensor_conf['min_dist']
        self.pump_conf = self.conf['PUMP_CONF']
        self.pump_time = self.pump_conf['pump_time']
        self.pump_pin = self.pump_conf['pump_pin']
        GPIO.setup(self.pump_pin,GPIO.OUT)
        GPIO.setup(self.echo_pin,GPIO.OUT)
        GPIO.setup(self.trig_pin,GPIO.OUT)
    def run(self):
        self.running = True
        self.check_distance()
    def stop(self):
        self.running = False
    def sanitize(self):
        GPIO.output(self.pump_pin , GPIO.HIGH)
        time.sleep(self.pump_time)
        GPIO.output(self.pump_pin,GPIO.LOW)
        self.check_distance()    
    def check_distance(self):
        while(self.running):
            GPIO.output(GPIO_TRIG, GPIO.HIGH)
            time.sleep(0.00001) 
            GPIO.output(GPIO_TRIG, GPIO.LOW) 
            while GPIO.input(GPIO_ECHO)==0: 
                start_time = time.time() 
            while GPIO.input(GPIO_ECHO)==1: 
                Bounce_back_time = time.time() 

            pulse_duration = Bounce_back_time - start_time 
            if(round(pulse_duration * 17150, 2)<=self.min_dist):
                self.sanitize()
                return True
        return False          
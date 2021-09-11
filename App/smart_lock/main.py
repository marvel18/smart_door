import pandas as pd
from FaceRecognition.face_reco import FaceRecognition
import cv2
from datetime import datetime
from smbus2 import SMBus
from mlx90614 import MLX90614
from configparser import ConfigParser
import RPi.GPIO as GPIO
import time
class LOCK:
    path = "/data/"
    def __init__(self):
        self.running = True
        self.locked = False
        self.save_data = True
        self.load_data()
        self.fr = FaceRecognition()
        self.conf = ConfigParser()
        self.conf.read(self.path+'config.ini')
        self.init_RPi()
    def init_RPi(self):
        self.lock_conf = self.conf['LOCK_CONF']
        self.lock_pin  = int(self.lock_conf['lock_pin'])
        self.lock_in_pin  = int(self.lock_conf['lock_in_pin'])
        self.sensor_conf = self.conf['SENSOR_CONF']
        self.max_temp = int(self.sensor_conf['max_temp'])
        bus = SMBus(1)
        self.temp_sensor = MLX90614(bus, address=0x5A)
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.lock_pin,GPIO.OUT)
        GPIO.output(self.lock_pin,GPIO.LOW)
        GPIO.setup(self.lock_in_pin,GPIO.IN)    
    def load_data(self):
        try:
            self.df = pd.read_csv(self.path+"/data.csv",index_col=0)
        except :
            self.df =pd.DataFrame(columns=  ["Date and Time" , "Name" ,"Confidence" , "Temperature" ,"fever" ])
    def run(self):
        if not self.fr.train():
            print("training error")
        self.start_camera()      
        self.recogonize()
    def stop(self):
        self.running = False        
    def start_camera(self):
        self.cam = cv2.VideoCapture(0)
    def stop_camera(self):
        self.cam.release()
    def saveData(self,name , confidence,temp):
        if not self.save_data:
            return
        print(name , confidence)
        now = datetime.now()
        self.df = self.df.append({"Date and Time":now , 'Name' :name  , 'Confidence' : confidence,"Temperature":temp},ignore_index=True)
        print(self.df)
        self.df.to_csv(self.path+"data.csv")
    def unlock(self):
        self.locked=False
        print("unlocked")
        GPIO.output(self.lock_pin,GPIO.LOW)
    def lock(self):
        self.locked = True
        print("locked")
        GPIO.output(self.lock_pin,GPIO.HIGH)
    def tempOK(self):
        for i in range(5):
            ambient_temp = self.temp_sensor.get_ambient()
            current_temp  = self.temp_sensor.get_object_1()
            if(ambient_temp<current_temp):
                temp =  (current_temp*9/5) + 32
                print(temp)
                if temp>self.max_temp:
                    return False
                return temp
            time.sleep(1)
        return False
    def recogonize(self):
        print("looking for faces")
        start_time = 0    
        while(self.running):
            ret  , img = self.cam.read()
            name , confidence , img  = self.fr.predict(img)
            if(GPIO.input(self.lock_in_pin)==1):
                if(start_time==0):
                    start_time = time.time()
                if(not self.locked):
                    if(time.time() - start_time > 10):
                        self.lock()
                elif((name != None ) and (name !="unknown")):
                    temp = self.tempOK()
                    print(name,confidence,temp)
                    if temp:
                        self.saveData(name,confidence,temp)
                        self.unlock()
                        start_time = 0
                    else:
                        print("temperature exceeded")
            elif(start_time!=0):
                start_time = 0
            cv2.waitKey(1)
        return False    
  
if __name__ == '__main__':
    LOCK().run()
    
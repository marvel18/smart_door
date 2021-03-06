from configparser import ConfigParser
import RPi.GPIO as GPIO
import time
class Sanitize():
    path  = "/data/"
    def __init__(self):
        self.conf = ConfigParser()
        self.conf.read(self.path + 'config.ini')
        self.init_RPi()
    def init_RPi(self):
        self.dist_sensor_conf = self.conf["DISTANCE_SENSOR"]
        self.trig_pin = int(self.dist_sensor_conf['trig_pin'])
        self.echo_pin = int(self.dist_sensor_conf['echo_pin'])
        self.min_dist = int(self.dist_sensor_conf['min_dist'])
        self.pump_conf = self.conf['PUMP_CONF']
        self.pump_time = int(self.pump_conf['pump_time'])
        self.pump_pin = int(self.pump_conf['pump_pin'])
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.setupRpiPin(self.pump_pin)
        self.setupRpiPin(self.trig_pin)
        self.setupRpiPin(self.echo_pin,GPIO.IN)
    def setupRpiPin(self,pin,method=GPIO.OUT,setvalue=GPIO.LOW):
        GPIO.setup(pin,method)
        if method==GPIO.OUT :
            GPIO.output(pin,setvalue)    
    def run(self):
        self.running = True
        self.check_distance()
    def stop(self):
        self.running = False
    def sanitize(self):
        print("pump start")
        GPIO.output(self.pump_pin , GPIO.HIGH)
        time.sleep(self.pump_time)
        print("pump stop")
        GPIO.output(self.pump_pin,GPIO.LOW)
        time.sleep(2)
    def check_distance(self):
        print("checking distance")
        print(self.trig_pin,self.echo_pin)
        while(self.running):
            GPIO.output(self.trig_pin, GPIO.HIGH)
            time.sleep(0.00001) 
            GPIO.output(self.trig_pin, GPIO.LOW) 
            while GPIO.input(self.echo_pin)==0: 
                start_time = time.time() 
            while GPIO.input(self.echo_pin)==1: 
                Bounce_back_time = time.time() 
            pulse_duration = Bounce_back_time - start_time 
            dist = round(pulse_duration * 17150, 2)
            if(dist<=self.min_dist):
                print(dist)
                self.sanitize()
            time.sleep(.1)       
        return False          
   
if __name__ == '__main__':
    Sanitize().run()
        
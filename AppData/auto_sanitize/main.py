from configparser import ConfigParser
import RPi.GPIO as GPIO
import time
class Sanitize():
    def __init__(self):
        self.conf = ConfigParser()
        self.conf.read('/usr/src/appdata/config.ini')
        self.init_RPi()
    def init_RPi(self):
        self.dist_sensor_conf = self.conf['DISTANCE_SENSOR']
        self.trig_pin = int(self.dist_sensor_conf['trig_pin'])
        self.echo_pin = int(self.dist_sensor_conf['echo_pin'])
        self.min_dist = int(self.dist_sensor_conf['min_dist'])
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
            GPIO.output(self.trig_pin, GPIO.HIGH)
            time.sleep(0.00001) 
            GPIO.output(self.trig_pin, GPIO.LOW) 
            while GPIO.input(self.echo_pin)==0: 
                start_time = time.time() 
            while GPIO.input(self.echo_pin)==1: 
                Bounce_back_time = time.time() 

            pulse_duration = Bounce_back_time - start_time 
            if(round(pulse_duration * 17150, 2)<=self.min_dist):
                self.sanitize()
                return True
        return False          
   
if __name__ == '__main__':
    Sanitize().run()
        
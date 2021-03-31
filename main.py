import pandas as pd
from FaceRecognition.face_reco import FaceRecognition
import cv2
from datetime import datetime
class Main:
    def __init__(self):
        self.running = True
        self.save_data = True
        self.load_data()
        self.fr = FaceRecognition()
    def load_data(self):
        try:
            self.df = pd.read_csv("data.csv",index_col=0)
        except :
            self.df =pd.DataFrame(columns=  ["Date and Time" , "Name" ,"Confidence" , "Temperature" ,"fever" ])
    def run(self):
        self.train()
        self.start_camera()        
        self.recogonize()    
    def start_camera(self):
        self.cam = cv2.VideoCapture(0)
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
    def recogonize(self):     
        while(self.running):
            ret  , img = self.cam.read()
            name , confidence , img  = self.fr.predict(img)
            if(name  != None and name !="unknown"):
                self.saveData(name,confidence)
                return True
            if cv2.waitKey(10) == 27:
                return False
            cv2.imshow("camera " , img)
        return False    
     
     
if __name__ == "__main__":
    app = Main()
    app.run()
                
import cv2
import numpy as np
from PIL import Image
import os
import pickle
class FaceRecognition:
    path = 'dataset'
    font = cv2.FONT_HERSHEY_SIMPLEX
    name = dict()
    train_data = dict() 
    names = dict()
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        self.cam.set(3, 640) 
        self.cam.set(4, 480)
        self.detector = cv2.CascadeClassifier('FaceRecognition/haarcascade_frontalface_default.xml') 
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
    def getImagesAndLabels(self , path):
    
        imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
        faceSamples=[]
        data = dict()
        ids = []
        id = 0
        for imagePath in imagePaths:
            print(imagePath)
            PIL_img = Image.open(imagePath).convert('L') 
            img_numpy = np.array(PIL_img,'uint8')
            name= int(os.path.split(imagePath)[-1].split(".")[1])
            if name not in data.values():
                data[id] = name
                id = id+1
            faces = self.detector.detectMultiScale(img_numpy)
            for (x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                ids.append(id)

        return faceSamples,ids , data
    def train(self , path = 'FaceRecognition/dataset'):
        print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
        faces,ids , data = self.getImagesAndLabels(path)
        self.recognizer.train(faces, np.array(ids))
        pickle.dump(data  , open("FaceRecognition/train/data.pkl" , "wb"))
        self.recognizer.write("FaceRecognition/train/train_data.yml")
        print("Training completed")
    def load(self):
       self.names = pickle.load(open("FaceRecognition/train/data.pkl" , "rb"))
       self.recognizer.read('FaceRecognition/train/trainer.yml')     
    def predict(self,img):
        names = self.names
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces = self.detector.detectMultiScale( 
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
        )

        for(x,y,w,h) in faces:

            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

            id, confidence = self.recognizer.predict(gray[y:y+h,x:x+w])
            value = 'unknown'
            if (confidence < 100):
                confidence = "  {0}%".format(round(100 - confidence))
                value = names[id] 
            else:
                confidence = "  {0}%".format(round(100 - confidence)) 
            cv2.putText(img, str(id), (x+5,y-5), self.font, 1, (255,255,255), 2)
            cv2.putText(img, str(confidence), (x+5,y+h-5), self.font, 1, (255,255,0), 1)  
            return value , confidence , img
        return None,None,img 
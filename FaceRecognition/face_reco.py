import cv2
import numpy as np
from PIL import Image
import os
import pickle
class FaceRecognition:
    path = 'dataset'
    name = dict()
    train_data = dict() 
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        self.cam.set(3, 640) 
        self.cam.set(4, 480)
        self.face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') 
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
    def getImagesAndLabels(self , path):
    
        imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
        faceSamples=[]
        data = dict()
        ids = []
        id = 0
        for imagePath in imagePaths:

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
    def train(self , path = 'dataset'):
        print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
        faces,ids , data = self.getImagesAndLabels(path)
        self.recognizer.train(faces, np.array(ids))
        pickle.dump(data  , open("train/data.pkl" , "w"))
        self.recognizer.write("train/train_data.yml")
        print("Training completed")
    def predict(self,img):
        self.recognizer.read('train/trainer.yml')
        names = pickle.load(open("train/data.pkl" , "rb"))
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale( 
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
        )

        for(x,y,w,h) in faces:

            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

            id, confidence = self.recognizer.predict(gray[y:y+h,x:x+w])

            if (confidence < 100):
                confidence = "  {0}%".format(round(100 - confidence))
                return names[id] , confidence
            else:
                confidence = "  {0}%".format(round(100 - confidence))
                return "unknown" , confidence
        return None    
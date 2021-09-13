
# This is server code to send video frames over UDP
import cv2, socket
import numpy as np
import base64
import threading
class Stream_Cam(threading.Thread):
    BUFF_SIZE = 65536
    client_addr = None
    WIDTH=400
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,self.BUFF_SIZE)
        host_name = socket.gethostname()
        host_ip = 'localhost'#  socket.gethostbyname(host_name)
        print(host_ip)
        port = 9999
        socket_address = (host_ip,port)
        self.server_socket.bind(socket_address)
        print('Listening at:',socket_address)
        super().__init__()
    def run(self):
        while True:
            msg,self.client_addr = self.server_socket.recvfrom(self.BUFF_SIZE)
            print('GOT connection from ',self.client_addr)
    def exit(self):
        self.server_socket.close()
        self.client_addr = None
    def send(self,frame):
        if self.client_addr:
            frame = cv2.resize(frame,(640, 400))
            encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
            message = base64.b64encode(buffer)
            self.server_socket.sendto(message,self.client_addr)
            key = cv2.waitKey(1) & 0xFF

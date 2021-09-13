import cv2, socket
import numpy as np
import time
import base64
class Video_Stream:
    BUFF_SIZE = 65536
    client_socket = None
    def __init__(self) :
        pass
    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,self.BUFF_SIZE)
        host_name = socket.gethostname()
        host_ip = 'localhost'#  socket.gethostbyname(host_name)
        print(host_ip)
        port = 9999
        message = b'Hello'
        self.client_socket.sendto(message,(host_ip,port))
        return True
    def exit(self):
        self.client_socket = None
        self.server_socket.close()
    def get_frame(self):
        if self.client_socket:
            packet,_ = self.client_socket.recvfrom(self.BUFF_SIZE)
            data = base64.b64decode(packet,' /')
            npdata = np.fromstring(data,dtype=np.uint8)
            frame = cv2.imdecode(npdata,1)
            key = cv2.waitKey(1) & 0xFF
            return frame
        return None
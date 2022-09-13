from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from threading import Thread
from queue import Queue

import time
import sys
import cv2

class Window(QWidget):

    def __init__(self, converted):
        super().__init__()
        self.frames = 0
        self.initUI(converted)

    def initUI(self, converted):
        self.hbox = QHBoxLayout(self)
        self.pixmap = QPixmap(converted)
        self.lbl = QLabel(self)
        self.lbl.setPixmap(self.pixmap)
        self.hbox.addWidget(self.lbl)
        self.setLayout(self.hbox)
        self.move(300, 200)
        self.setWindowTitle('Live Video Capture')
        self.show()
        
    def update_frame(self, q):
        while True:
            image = q.get()
            self.pixmap = QPixmap(image)
            self.lbl.setPixmap(self.pixmap)
            self.frames += 1
            
    def fps_thread(self):
        last = 0
        while True:
            print(self.frames - last, "FPS")
            last = self.frames
            time.sleep(1)
        
def stop_capturing():
    if cv2.waitKey(1) & 0xFF == ord("q"):
        return True
    return False

def get_live_video(out_q):
    vid_object = cv2.VideoCapture(0)
    while True:
        
        ret, frame = vid_object.read()
        if stop_capturing(): break
        convert = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format.Format_BGR888)    
        out_q.put(convert)
    vid_object.release()
    
def create_frame(q):
    image = q.get()
    ex = Window(image)
    return ex    

def main():
    app = QApplication(sys.argv)
    q = Queue()
    t1 = Thread(target=get_live_video, args = (q,))
    t1.start()
    ex = create_frame(q)
    t2 = Thread(target=ex.update_frame, args=(q,))
    t2.start()
    t3 = Thread(target=ex.fps_thread,args=())
    t3.start()
    sys.exit(app.exec())
        
if __name__ == '__main__': main()

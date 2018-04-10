#!/usr/bin/python3
from time import sleep
import numpy as np
import pyqtgraph as pg
import time, sys, os, cv2
import argparse, datetime, imutils
import threading
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from threading import Thread, Timer
from PIL import Image
from RawImageWidget import RawImageWidget
from MyGif import MyGif
from MyThread import MyThread, MyThread2 
from MyTimer import MyTimer
from MyArduino import MyArduino

from RawImageWidget import RawImageWidget
from pyqtgraph.Qt import QtCore, QtGui, QtOpenGL
import serial



class MyQtWidget(QtGui.QWidget):
    def __init__(self):
        super(MyQtWidget, self).__init__()
        
        self.initUI()
    
    
    def initUI(self):      
        self.move(0,0)
        self.resize(1000,800)
        self.show()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            
            
    def load_picture(self):
        file_path = '/Users/virginiarutten/Documents/deep_fish/assets/pavlov_dog.jpg'
        self.bkImage = np.array(Image.open(file_path)).T
            
            
            
class MyVideoRecorder(object):
    
    def __init__(self, opt = 1):        
        
        
        ####################
        #### args
        ####################
        self.ap = argparse.ArgumentParser()
        self.default_path =  '/Users/virginiarutten/Documents/deep_fish/videos'
        self.ap.add_argument("-v", "--video", \
                             default = self.default_path, help="path to the video file")
        self.ap.add_argument("-f", "--fps", type = str, default=str(10), help="fps")
        
        self.ap.add_argument("-p", "--path", type = str, \
                             default=self.default_path, help="path to which to save videos")
        file_name = 'test_delete'
        self.ap.add_argument("-n", "--name", type=str, default=file_name, help="filename")
        self.ap.add_argument("-r", "--resize", type=bool, default=True, help="filename")
        
        
        self.ap.add_argument("-c", "--cam", type=int, default=1, help="camera number")
        self.ap.add_argument("-t", "--max_time", type=int, default=10, help="camera number")
        self.ap.add_argument("-w", "--wait_time", type=int, default=100, help="camera number")
        
        
        if opt ==1:
            self.args = vars(self.ap.parse_args())
        else:
            self.args = vars(self.ap.parse_known_args()[0])
            
            
            
        self.wait_time = self.args['wait_time']/1000
        self.dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")[2:]
        self.output = self.args['path'] +'/' + self.args['name'] + self.dt + '.avi'
        #self.fps = int(self.args['fps'])
        self.fps = np.ceil(1/self.wait_time)
        self.cam = self.args['cam']
        self.resize = self.args['resize']
        self.max_time = self.args['max_time']
        print('output file:{0}'.format(self.output))
        
        
        #################
        ### settings
        ###############
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.imH = int(360/2)
        self.imW = int(640/2)
        self.recording = False
        
        
        
        self.initialiseCap()
        self.initialiseWriter()
        time.sleep(.2)     
        self.grabFrame()
        self.initialise_window()
        self.show_frame()
        
        self.recording = True
        self.recordingThread = MyThread(self.start_recording,self.wait_time)
        self.recordingThread.start()
        
 
        self.count = 0
        self.Timer = MyTimer()
        self.Timer.restart()
        
        
        
    def initialise_window(self): 
        
        self.app = QtGui.QApplication([])
        self.win = MyQtWidget()
        self.win.load_picture()
        title='deep fish detection'
        self.win.setWindowTitle(title)
        self.imv1 = RawImageWidget(scaled=True)
        self.imv1.setImage(self.win.bkImage)
        
        self.layout = QtGui.QGridLayout()
        self.win.setLayout(self.layout)
        self.layout.addWidget(self.imv1)
        self.win.show()
        
        
    def show_frame(self):
        tmp = self.frame.swapaxes(0,1)[:,:,::-1]
        self.imv1.setImage(tmp)
    
    
    def convert2gif(self):
        self.gif = MyGif(self.output, array, fps=self.fps, scale=1.0)
    
    def start_recording(self):
        while self.recording:
            self.record_loop()
        
    def pause(self):
        self.recording= False
        
    def initialiseCap(self):
        self.cap = cv2.VideoCapture(self.cam)
    
    def initialiseWriter(self):
        self.writer =  cv2.VideoWriter(self.output,fourcc = self.fourcc,\
                                       fps = self.fps, \
                                       frameSize = (self.imW,self.imH))
        
    def record_loop(self):
        tmp = self.Timer.get_time()
        if tmp>self.max_time:
            print('time limit reached')
            print(self.Timer.get_time())
            self.recording=False
            self.stop()
        else:
            self.grabFrame()
            if self.ret:
                self.count+=1
                if self.count % 100==0:
                    print(self.count)
                    print(self.Timer.get_time())
                self.writer.write(self.frame)
                self.show_frame()
                    
    
    def grabFrame(self):
        self.ret, self.frame = self.cap.read()
        if self.ret:
            self.frame = cv2.resize(self.frame, (self.imW, self.imH)).astype('uint8')
        else:
            print('no frame captured')
            pass
    
    def releaseCap(self):
        self.cap.release()
        
    
    def stop(self):
        print('stop function has been called')
        print('total time = {0}'.format(self.Timer.get_time()))
        print('total frames = {0}'.format(self.count))
        print('approx fps = {0}'.format(int(self.count/self.Timer.get_time())))
        self.recording= False
        self.writer.release()
        self.releaseCap()
        print('\nfile saved at:\n{0}'.format(self.output))
        
        
def main():
    print('starting')
    V = MyVideoRecorder()
    sys.exit(V.app.exec_())
   
if __name__ == '__main__':
    main()
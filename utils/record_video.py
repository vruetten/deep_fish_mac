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

from MyGif import MyGif
from MyThread import MyThread
from MyTimer import MyTimer
from MyArduino import MyArduino

from RawImageWidget import RawImageWidget
from pyqtgraph.Qt import QtCore, QtGui, QtOpenGL
import serial


class MyVideoRecorder(object):
    
    def __init__(self, cam = 1):        
        
        self.ap = argparse.ArgumentParser()
        self.ap.add_argument("-v", "--video", default = './videos', help="path to the video file")
        self.ap.add_argument("-f", "--fps", type=int, default=10, help="fps")
        
        self.ap.add_argument("-p", "--path", type=str, default='./videos', help="path to which to save videos")
        file_name = 'test' +  str(np.random.randint(100))
        self.ap.add_argument("-n", "--name", type=str, default=file_name, help="filename")
        self.ap.add_argument("-r", "--resize", type=bool, default=True, help="filename")
        
        
        self.ap.add_argument("-c", "--cam", type=int, default=1, help="csamera number")
        
        
        
        self.args = vars(self.ap.parse_args())
        
        self.output = self.args['path'] +'/' + self.args['name']
        self.fps = self.args['fps']
        self.cam = self.args['cam']
        self.resize = self.args['resize']
        print(self.output)
        
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.imH = int(360/2)
        self.imW = int(640/2)
        
        
        self.recording = False
        
        
        self.initialiseCap()
        self.initialiseWriter()
        self.recordingThread = MyThread(self.record)
        self.recordingThread.start()
        self.Timer = MyTimer() 
        self.Timer.restart()

        
    def convert2gif(self):
        self.gif = MyGif(self.output, array, fps=self.fps, scale=1.0)
        
    
    def start(self):
        self.recording = True
        
    def pause(self):
        self.recording= False
        
        
    def initialiseCap(self):
        self.cap = cv2.VideoCapture(self.cam)
    
    def initialiseWriter(self):
        self.writer =  cv2.VideoWriter(self.output,fourcc = self.fourcc,\
                                       fps = self.fps, \
                                       frameSize = (self.imW,self.imH))
        time.sleep(1.0)
        
        
    def record(self):
        while self.recording:
            self.grabFrame()
            self.writer.write(self.frame)
            cv2.imshow("Frame", self.frame)
            self.key = cv2.waitKey(1) & 0xFF
            if self.key == ord("q"):
                self.recording = False
                self.stop()
    
    def grabFrame(self):
        ret, self.frame = self.cap.read()
        if ret:
            self.frame = self.frame.swapaxes(0,1)[:,:,::-1]
            if self.resize:
                self.frame = cv2.resize(self.frame, (self.imH, self.imW)).astype('uint8')
        
    
    
    def releaseCap(self):
        self.cap.release()
        
    
    def stop(self):
        self.recording= False
        self.releaseCap()
        self.writer.release()
        print('file saved at:\n{0}'.format(self.output))
        cv2.destroyAllWindows()
        self.recordingThread.stop()
        

        
def main():
    print('starting')
    V = MyVideoRecorder()
    V.start()
   
   
if __name__ == '__main__':
    main()
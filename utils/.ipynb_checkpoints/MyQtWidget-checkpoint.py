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
from pyqtgraph.Qt import QtCore, QtGui
import serial



class MyQtWidget(QWidget):
    def __init__(self):
        super(MyQtWidget, self).__init__()
        
        self.title='go fish'
        self.initUI()
    
    
    def initUI(self):   
        self.setWindowTitle(self.title)
        self.move(0,0)
        self.resize(1000,800)
        self.show()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
            
       
    
class MyVideoRecorder(object):
    
    def __init__(self, cameraport = 1, path = 'test.avi', imH = int(360/2),imW = int(640/2), fps = 8):   
        
        self.cameraPort = cameraport
        self.path = path
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.imH = imH
        self.imW = imW
        self.fps = fps
        
        #self.init()
        
    
    def init(self):      
        self.initialise_camera()
        self.initialise_writer()

    
    def initialise_camera(self):
        self.camera = cv2.VideoCapture(self.cameraPort) 
        print('connecting to camera {0}...'.format(self.cameraPort))
        if self.camera.grab()==False:
            if self.cameraPort==1:
                self.cameraPort=0
                print('no camera detected... camera changed')
            
            
    def initialise_writer(self):
        print('writer being initialised to: \n{0}...'.format(self.path))
        self.writer =  cv2.VideoWriter(self.path,fourcc = self.fourcc,\
                                       fps = self.fps, \
                                       frameSize = (self.imW,self.imH), isColor =False)
        
        
    def save_frame(self, frame):
        self.writer.write(frame)
        
        
    def release_writer(self):
        self.writer.release()
    def release_camera(self):
        self.camera.release()
    
        

       
        
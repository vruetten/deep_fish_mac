#!/usr/bin/python3
from time import sleep
import numpy as np
import time, cv2

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
        # self.initialise_writer()


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
        try:
            self.writer.write(frame)
        except:
            print('couldn\'t write - no writer - feature has been disabled')

    def release_writer(self):
        try:
            self.writer.release()
        except:
            print('couldn\'t release writer - no writer - feature has been disabled')
    def release_camera(self):
        self.camera.release()

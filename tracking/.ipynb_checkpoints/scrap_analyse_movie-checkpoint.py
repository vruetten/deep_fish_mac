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
from MyThread import MyThread, MyThread2 
from MyTimer import MyTimer
from glob import glob
from pyqtgraph.Qt import QtCore, QtGui, QtOpenGL







def my_run():
    
    default_path = '/Users/virginiarutten/Documents/deep_fish/videos'
    files = glob(default_path+'/*')
    print(files)
    file = files[2]
    print(file)

    cap = cv2.VideoCapture(file)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)

    print('length: {0}, \nwidth: {1}, \nheight: {2}, \nfps:{3}'.format(\
                length, width, height, fps))
    
    
    while(cap.isOpened()):
      # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
        # Display the resulting frame
            cv2.imshow('Frame',frame)

        # Press Q on keyboard to  exit
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        
        
    cap.release() 
# Closes all the frames
    cv2.destroyAllWindows()


        
def main():
    print('starting')
    my_run()
   
if __name__ == '__main__':
    main()
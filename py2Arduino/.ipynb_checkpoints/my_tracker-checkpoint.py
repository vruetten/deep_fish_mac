#!/usr/bin/python3


import matplotlib.pyplot as pl
from time import sleep
import numpy as np
import argparse
import datetime
import imutils
import threading
from threading import Thread
import time
import cv2
from threading import Timer


class MyThread(Thread):
    
    def __init__(self, function):
        super(MyThread,self).__init__()
        self._stop_event = threading.Event()
        self.function = function
        
    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
    
    def run(self):
        while not self._stop_event.wait(2000):
            print("my thread")
            self.function()
            # call a function   
            

            
            
class MyTracker(object):
    
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.key = cv2.waitKey(1) & 0xFF

        self.recording = False
        
        self.firstFrame = None
        self.imwidth = 500
        self.text = None
        
        self.ap = argparse.ArgumentParser()
        self.ap.add_argument("-v", "--video", help="path to the video file")
        self.ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
        self.ap.add_argument("-p", "--path", type=str, default='./videos', help="path to which to save videos")
    
    
        self.recordingThread = MyThread(self.start_recording)
        self.recordingThread.start()
    
    def kill_threads(self):
        self.recording = False
        self.recordingThread.stop()
        
    
    def start_recording(self):
        self.recording = True
        
        while self.recording:
            #check for kill
            if self.key == ord("q"):
                print('quit detected')
                self.recording==False 
                self.camera.release()
                cv2.destroyAllWindows()  
                
                
            #if self.key ==ord("k"):
            self.grab_frame()
            self.process_frame()
            self.get_frame_contours()
            self.show_frame()
            
    def grab_frame(self):
        try:
            (grabbed, frame) = self.camera.read()
            self.frame = imutils.resize(frame, width=self.imwidth)
            print('frame grabbed')
        except:
            print('couldn\'t grab frame')
            pass  
        
    def process_frame(self):
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.gray = cv2.GaussianBlur(gray, (21, 21), 0)
        print('frame processed')
        if self.firstFrame is None:
            self.firstFrame = self.gray
             
    def get_frame_contours(self):
            # compute the absolute difference between the current frame and
        # first frame
        self.frameDelta = cv2.absdiff(self.firstFrame, self.gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        _, cnts, _ = cv2.findContours(image = thresh.copy(), mode = cv2.RETR_EXTERNAL,
            method = cv2.CHAIN_APPROX_SIMPLE)

        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < args["min_area"]:
                pass

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            self.text = "Occupied"
        
            # draw the text and timestamp on the frame
        cv2.putText(self.frame, "Room Status: {}".format(self.text), (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(self.frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
            (10, self.frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        print('contours acquired')
        
    def show_frame(self):
        print('show frames')
            # show the frame and record if the user presses a key
        cv2.imshow("raw video", self.frame)
        cv2.imshow("Thresholded", self.thresh)
        cv2.imshow("Frame Delta", self.frameDelta)
        
        
        
        
def main():
    T = MyTracker()
    print('starting')
    T.start_recording()
    
    
if __name__ == '__main__':
    print('hello')
    main()
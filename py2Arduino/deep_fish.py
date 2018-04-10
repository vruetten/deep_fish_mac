#!/usr/bin/python3

import numpy as np
import treading
from threading import Thread
import serial
from time import sleep
from threading import Timer
import pyqtgraph as pg
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from collections import deque
import matplotlib.pyplot as pl
from MyThread import MyThread
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from PIL import Image

from PyQt5.QtCore import pyqtSlot
import sys, re

class Communicate(QtCore.QObject):
    signal = QtCore.pyqtSignal(str)
     
class myApp(QtGui.QWidget):
   
    def __init__(self):
        super(myApp, self).__init__()
        
        # initialise gui
        self.initUI()
        
        # initialise bools
        self.measuring = False #reading from  arduino
        self.trialOn = False #trial loo
        
        ## trial thread
        self.trial_thread = MyThread(self.trial_loop)
        self.trial_thread.start()
        
        
        self.ard_thread = MyThread(self.read_ard)
        self.ard_thread.start()
        
        # try to connect to arduino
        try:
            self.get_serial()
        except:
            pass

        try:
            self.load_picture()
        except:
            pass
        
        
        
    def initUI(self):
        
        self.maxLen = 300
        # data buffer
        self.yvals = deque([0.0]*self.maxLen)


        #####################################
        ## standard buttons
        #####################################
        ## start flow button
        self.start_btn = QtGui.QPushButton('start',self)
        self.start_btn.clicked.connect(self.on_start)

        ## stop flow button
        self.stop_btn = QtGui.QPushButton('stop',self)
        self.stop_btn.clicked.connect(self.on_stop)

        ## quit app button
        self.qbtn = QtGui.QPushButton('exit',self)
        # quit threads if running **************
        self.qbtn.clicked.connect(self.on_quit)
        # quit app
        self.qbtn.clicked.connect(QtCore.QCoreApplication.instance().quit)


        #####################################
        ## set flow rate button
        #####################################
        self.slider = QtGui.QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        # change value
        self.slider.valueChanged.connect(self.slidervaluechange)

        #####################################
        ## labels to show current flow rate
        #####################################
        ## text - data sent from Arduino
        self.text_ard = QtGui.QLineEdit('arduino sent:')
        self.label_ard = QLabel()
        self.label_ard.setText('arduino sent:')
        # communication signal to write to gui
        self.comm_ard = Communicate()
        self.comm_ard.signal.connect(self.text_ard.setText)
        

        #
        ## text - data written to Arduino
        self.text_rate= QtGui.QLineEdit('PC sent:')
        self.label_rate = QLabel()
        self.label_rate.setText('PC sent:')
        # communication signal to write to gui
        self.comm_rate = Communicate()
        self.comm_rate.signal.connect(self.text_rate.setText)        


        
        self.plot = pg.PlotWidget()

        
        #####################################
        ## stimulus display
        #####################################
        
        ## start trial
        self.trial_btn= QtGui.QPushButton('start trial',self)
        self.trial_btn.clicked.connect(self.on_startTrial)
        self.trialOff_btn= QtGui.QPushButton('stop trial',self)
        self.trialOff_btn.clicked.connect(self.on_stopTrial)
        # communication signal to write to gui
        self.comm_trial = Communicate()
        self.comm_trial.signal.connect(self.text_rate.setText)           
        

        self.figure = pl.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.stim_btn = QtGui.QPushButton('show stimulus',self)
        self.stim_btn.clicked.connect(self.plot_picture)
        self.stimOff_btn  = QtGui.QPushButton('hide stimulus',self)
        self.stimOff_btn.clicked.connect(self.clear_picture)
        
        #####################################
        ## layout
        #####################################v
        layout = QtGui.QGridLayout()
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)

        layout.addWidget(self.start_btn, 0, 0, 1, 1)   # button goes in upper-left
        layout.addWidget(self.stop_btn, 1, 0, 1, 1)   # button goes in upper-left
        layout.addWidget(self.qbtn, 2, 0, 1, 1)   # button goes in upper-left   

        layout.addWidget(self.label_ard, 0, 1, 1, 1)   # button goes in upper-left 
        layout.addWidget(self.text_ard, 0, 2, 1, 1)   # button goes in upper-left 

        layout.addWidget(self.label_rate, 1, 1, 1, 1)   # button goes in upper-left 
        layout.addWidget(self.text_rate, 1, 2, 1, 1)   # button goes in upper-left 

        layout.addWidget(self.slider, 3, 0, 1, 1)   # button goes in upper-left 
        layout.addWidget(self.stim_btn, 2, 2, 1, 1)   # button goes in upper-left 
        layout.addWidget(self.stimOff_btn, 2, 3, 1, 1)   # button goes in upper-left 
        layout.addWidget(self.trial_btn, 3, 2, 1, 1)   # button goes in upper-left 
        layout.addWidget(self.trialOff_btn, 3, 3, 1, 1)   # button goes in upper-left 


        layout.addWidget(self.plot, 4, 0, 3, 5)  # plot goes on right side, spanning 3 rows
        layout.addWidget(self.canvas, 4, 5, 3, 5)


        self.setLayout(layout)
        self.setWindowTitle('DeepFish') 
        self.show()

        
    def load_picture(self):
        file_path = '../assets/pp.png'
        self.im = np.asarray(Image.open(file_path))

    def clear_picture(self): 
        try:
            ax
            ax.set_axis_off()
        except:
            ax = self.figure.add_subplot(111)
            ax.set_axis_off()
        ax.clear()
        ax.set_axis_off()
        ax.set_frame_on(False)
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        self.canvas.draw()
        
    
    def plot_picture(self): 
        try:
            ax
        except:
            ax = self.figure.add_subplot(111)
            ax.axes.get_xaxis().set_visible(False)
            ax.axes.get_yaxis().set_visible(False)
            ax.set_axis_off()
        ax.clear()
        ax.imshow(self.im)
        ax.set_frame_on(False)
        self.canvas.draw()  
        
    def test_plot(self):
        tmp_data = np.arange(20)
        ax = self.figure.add_subplot(111)
        ax.set_axis_off()
        ax.clear()
        ax.imshow(self.im)
        ax.set_axis_off()
        ax.set_frame_on(False)
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        #ax.plot(tmp_data, 'o-')
        self.canvas.draw()
        
    
    def slidervaluechange(self):
        rate = self.slider.value()
        self.send_ard(rate)
        
    def send_ard(self, var):
        self.ser.write(bytes(var))

    def go_cue(self):
        self.plot_picture()
        
        
    def trial_loop(self):
        self.trial_time = 10
        t = Timer(self.trial_time, self.go_cue)
        while self.trialOn:
            pass
            #t.start()
       
            #self.test_plot()
            
          
    def read_ard(self):
        while self.measuring:
            self.incoming_data = self.ser.readline().decode("utf-8")
            sleep(0.1)
            if self.incoming_data.find('ard')>-1:
                numbers = ''.join(re.findall('[0-9]',self.incoming_data))
                self.comm_ard.signal.emit(self.incoming_data)
                # add data point to plot
                self.addToBuf( self.yvals,numbers)
                
                sys.stdout.write(numbers+ '\n')
                #sys.stdout.write("ard found")
            elif self.incoming_data.find('PC')>-1:
                numbers = ''.join(re.findall('[0-9]',self.incoming_data))
                self.comm_rate.signal.emit(self.incoming_data) 
                sys.stdout.write(numbers + '\n')
        
    def get_serial(self):
        self.ser = serial.Serial('/dev/cu.usbmodem14311', 9600,timeout=.05)

    
    def startTrial(self):
        if not self.trialOn:
            self.trialOn=True

    def stopTrial(self):
        if self.trialOn:
            self.trialOn=False

       
    ##################
    ### measure rate
    ################
    
    def startMeasuring(self):
        if not self.measuring:
            self.measuring=True
            
    def stopMeasuring(self):
        if self.measuring:
            self.measuring=False
            
            
    def print_to_screen(self):
        while self.measuring:
            sleep(0.1)
            data = self.ser.readline().decode("utf-8") 
            self.comm.signal.emit(data)
          
        
    # add to buffer
    def addToBuf(self, buf, val):
        if len(buf) < self.maxLen:
            buf.append(val)
        else:
            buf.pop()
            buf.appendleft(val)
            
        
    ###################
    #### slots
    ###################
    @pyqtSlot()
    def on_startTrial(self):
        print('starting trial')
        self.startTrial()
  
    @pyqtSlot()
    def on_stopTrial(self):
        print('stop trial')
        self.stopTrial()

        
    @pyqtSlot()
    def on_start(self):
        print('start to measuring')
        self.startMeasuring()
        
    @pyqtSlot()
    def on_stop(self):
        print('stop measuring')
        self.stopMeasuring() 
        
        
    @pyqtSlot()
    def on_quit(self):
        print('kill all threads')
        self.ard_thread.stop()
        self.trial_thread.stop()
        

def main():
    app = QtGui.QApplication([])
    ex = myApp()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    print('staring...')
    main()
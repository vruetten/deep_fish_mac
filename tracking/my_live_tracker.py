#!/usr/bin/python3
import numpy as np
import time, sys, os, cv2, serial
from time import sleep
import argparse, datetime, imutils, threading
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QFormLayout, QGroupBox, \
QSlider, QLabel, QComboBox, QGridLayout, \
QWidget, QLineEdit, QApplication, QSpinBox
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtCore import *
from PIL import Image
from MyThread import MyThread
from MyArduino import MyArduino
from MyTimer import MyTimer
from MyQtWidget import MyQtWidget
from MyVideoRecorder import MyVideoRecorder
from MyRealTimeTracker import MyRealTimeTracker
from RawImageWidget import RawImageWidget
import pyqtgraph as pg


class MyLiveTracker(object):
    def __init__(self,opt=1):

        ##########################
        ##### default saving directory
        ##########################
        self.default_path = '/Users/virginiarutten/Documents/deep_fish/videos'
        self.filename = 'test'
        self.ext = '.avi'

        self.dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")[2:]
        self.foldername = self.default_path +'/' +  self.dt[:6]
        self.path = self.get_path()
        self.check_dir()


        self.save = False
        self.cameraPort = 1
        self.width = 950
        self.height = 700

        self.recording = False
        self.trialOn = False
        self.flowOn = False
        self.ARD = False


        self.trialTime = 10
        self.trialSleepTime = 10

        ##########################
        ##### Arduino settings
        ##########################
        self.flowOffDelay = 1
        self.flowOnDelay = 1


        self.imW = int(640/2)
        self.imH = int(360/2)
        self.imfps = 25

        self.trialTimer = MyTimer()
        self.trialTimer.restart()

        self.frameTimer = MyTimer()
        self.frameTimer.restart()

        self.ite = 0


        self.args = self.initialise_tracking_variables()
        self.win = self.initialise_window()
        self.recorder = self.initialise_videorecorder()
        self.Tracker = self.initialise_tracker()

        ##########################
        ##### Arduino
        ##########################
        self.ARDPort = self.ArdPortComboBox.currentData()
        self.Ard = self.initialise_Ard()

        ##########################
        ##### Threads
        ##########################
        self.recordingThread = MyThread(self.start_recording, wait_time = 0.02)
        self.recordingThread.start()
        self.trialThread = MyThread(self.start_trial, wait_time = 0.001)
        self.trialThread.start()
        self.recording = True

    def check_dir(self):
        ''' check that directory of the day exisits
        and that filename is unique'''
        if not os.path.isdir(self.foldername):
            print('creating directory...')
            os.mkdir(self.foldername)
        file_num = 1
        while os.path.exists(self.path):
            print('file already exisits...\nrenaming')
            print(self.path)
            self.filename = self.filename + str(file_num)
            file_num +=1
            self.path = self.get_path()

    def initialise_tracker(self):
        self.Tracker = MyRealTimeTracker(self.args)
        return self.Tracker

    def initialise_tracking_variables(self):
        ''' default values '''

        self.keypoints = {}
        self.mvAvgFrame = None
        self.fishNum = 4
        self.area_mn = 35
         ## threshold mask value
        self.pVal = 180
        self.pVal_mx = 255
        self.text = None

        self.pre_frames = 0

        self.args = {}
        self.args['pVal'] = self.pVal
        self.args['pVal_mx'] = self.pVal_mx
        self.args['fishNum'] = self.fishNum
        self.args['area_mn'] = self.area_mn
        self.args['keypoints'] = self.keypoints
        self.args['pre_frames'] = self.pre_frames
        return self.args





    def get_path(self):
        return self.foldername + '/' + self.dt + self.filename + self.ext



    def initialise_videorecorder(self):
        ''' initialises recorder'''
        self.num_saved_frame = 0
        self.cameraPort = self.cameraComboBox.currentIndex()
        self.check_dir()
        if self.path[-3:]!='avi':
            print('please check extension')

        print('initialising recording...\noutput file:{0}'.\
             format(self.path))

        self.recorder = MyVideoRecorder(cameraport = self.cameraPort,\
                                        path = self.path,\
                                        imH = self.imH,\
                                        imW = self.imW,\
                                       fps = self.imfps)

        wasrecording = False
        if self.recording:
            wasrecording = True
            self.recording = False


        self.recorder.initialise_camera()   ### reinitialise camera
        self.camera = self.recorder.camera   ### test camera works
        if self.camera.grab()==False:
            if self.cameraPort==1:
                self.cameraPort=0
                self.cameraComboBox.setCurrentIndex(self.cameraPort)
                print('no camera detected... camera changed')
        if wasrecording:
            self.recording = True
        else:
            self.recording = False
            wasrecording = False

        return self.recorder


    def initialise_Ard(self):
        try:
            self.Ard = MyArduino()
            self.ARDport = self.Ard.port
            self.ARD = True
        except:
            print('no valid port found \nplease check')
            self.Ard = None
            self.ARD = False
        return self.Ard


    def load_picture(self):
        file_path = '/Users/virginiarutten/Documents/deep_fish/assets/pavlov_dog.jpg'
        self.bkImage = np.array(Image.open(file_path)).T


    def initialise_window(self):
        self.load_picture()
        self.app = QApplication([])
        title = 'go fish'
        self.win = MyQtWidget(width=self.width, height=self.height, title=title)

        #####################################
        ## Layout
        #####################################
        self.layout = QGridLayout()
        self.win.setLayout(self.layout)


        self.createRecordGroupBox()
        self.createDefaultGroupBox()
        self.createImageGroupBox()
        self.createSwitchFormGroupBox()
        self.createCalibrationFormGroupBox()
        self.createParamGroupBox()
        self.createPumpGroupBox()
        self.createTextGroupBox()
        self.resetPath()

        self.layout.addWidget(self.imageForm,0,0,1,3)

        self.layout.addWidget(self.textForm,0,4,1,3)

        self.layout.addWidget(self.paramForm,2,0,1,1)
        self.layout.addWidget(self.calibrationForm,2,1,1,1)
        self.layout.addWidget(self.pumpForm,2,2,1,1)

        self.layout.addWidget(self.switchForm,3,1,1,1)
        self.layout.addWidget(self.defaultForm,3,2,1,1)
        self.layout.addWidget(self.recordForm,3,0,1,1)

        self.win.show()
        return self.win

    def createImageGroupBox(self):
        self.imageForm = QGroupBox('Imaging')
        self.imageLayout = QGridLayout()

        ##raw image
        self.imv1 = RawImageWidget(scaled=True)
        ## tracking
        self.imv2 = RawImageWidget(scaled=True)
        ## mask
        self.imv3 = RawImageWidget(scaled=True)
        ## avergae
        self.imv4 = RawImageWidget(scaled=True)

        ## set background image
        self.imv1.setImage(self.bkImage)

        self.imageLayout.addWidget(QLabel("Raw:"),0,0,1,1)
        self.imageLayout.addWidget(QLabel("Detection:"),0,1,1,1)
        self.imageLayout.addWidget(self.imv1,1,0,1,1)
        self.imageLayout.addWidget(self.imv2,1,1,1,1)
        self.imageLayout.addWidget(QLabel("Mask:"),2,0,1,1)
        self.imageLayout.addWidget(QLabel("Moving average:"),2,1,1,1)
        self.imageLayout.addWidget(self.imv3,3,0,1,1)
        self.imageLayout.addWidget(self.imv4,3,1,1,1)

        self.imageForm.setLayout(self.imageLayout)

    def createTextGroupBox(self):
        self.textForm = QGroupBox('Imaging')
        self.textLayout =  QFormLayout()

        ## parameters
        self.maxArea_box = QtGui.QLineEdit()
        self.num_detected_box = QtGui.QLineEdit()
        self.maxArea_box.setText('0')
        self.num_detected_box.setText('0')

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QLabel("max area:"))
        hbox.addWidget(self.maxArea_box)
        hboxD = QtGui.QHBoxLayout()
        hboxD.addWidget(QLabel("fish #:"))
        hboxD.addWidget(self.num_detected_box)

        self.textLayout.addRow(hbox)
        self.textLayout.addRow(hboxD)

        self.textForm.setLayout(self.textLayout)



    def createSwitchFormGroupBox(self):
        self.switchForm = QGroupBox("Controller")
        self.switchLayout = QFormLayout()

        ######################
        #### Trial/Lights
        #####################

        self.lightOn_btn = QtGui.QPushButton('Light On',self.win)
        self.lightOn_btn.clicked.connect(self.on_lightOn)

        self.lightOff_btn = QtGui.QPushButton('Light Off',self.win)
        self.lightOff_btn.clicked.connect(self.on_lightOff)

        self.trialOn_btn = QtGui.QPushButton('Start Trial',self.win)
        self.trialOn_btn.clicked.connect(self.on_trialOn)

        self.trialOff_btn = QtGui.QPushButton('Stop Trial',self.win)
        self.trialOff_btn.clicked.connect(self.on_trialOff)
        self.switchLayout.addRow(self.lightOn_btn, self.lightOff_btn)
        self.switchLayout.addRow(self.trialOn_btn, self.trialOff_btn)

        self.switchForm.setLayout(self.switchLayout)


    def createCalibrationFormGroupBox(self):
        self.calibrationForm = QGroupBox("Image Calibration")
        self.calibrationLayout = QFormLayout()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(255)
        self.slider.setValue(self.pVal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.valueChanged.connect(self.on_slidervaluechange)
        self.textSlider = QtGui.QLineEdit(str(self.pVal))

        hbox_mn = QtGui.QHBoxLayout()
        hbox_mn.addWidget(self.slider)
        hbox_mn.addWidget(self.textSlider)


        self.slider2 = QSlider(Qt.Horizontal)
        self.slider2.setMinimum(0)
        self.slider2.setMaximum(255)
        self.slider2.setValue(self.pVal_mx)
        self.slider2.setTickPosition(QSlider.TicksBelow)
        self.slider2.setTickInterval(10)
        self.slider2.valueChanged.connect(self.on_slider2valuechange)
        self.textSlider2 = QtGui.QLineEdit(str(self.pVal_mx),self.win)

        hbox_mx = QtGui.QHBoxLayout()
        hbox_mx.addWidget(self.slider2)
        hbox_mx.addWidget(self.textSlider2)

        self.ROIslider= QSlider(Qt.Horizontal)
        self.ROIslider.setMinimum(0)
        self.ROIslider.setMaximum(1000)
        self.ROIslider.setValue(self.area_mn)
        self.ROIslider.setTickPosition(QSlider.TicksBelow)
        self.ROIslider.setTickInterval(100)
        self.ROIslider.valueChanged.connect(self.on_ROIslidervaluechange)
        self.ROItextSlider = QLineEdit(str(self.area_mn))

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.ROIslider)
        hbox.addWidget(self.ROItextSlider)

        self.calibrationLayout.addRow(QLabel("ROI max area:"),hbox)
        self.calibrationLayout.addRow(QLabel("px min:"), hbox_mn)
        self.calibrationLayout.addRow(QLabel("px max:"), hbox_mx)

        self.calibrationForm.setLayout(self.calibrationLayout)


    def createPumpGroupBox(self):
        self.pumpForm = QGroupBox("Pump settings")
        self.pumpFormLayout = QFormLayout()

        self.flowOff1_btn = QtGui.QPushButton('Increase')
        self.flowOff0_btn = QtGui.QPushButton('Decrease')

        self.flowOn1_btn = QtGui.QPushButton('Increase')
        self.flowOn0_btn = QtGui.QPushButton('Decrease')

        self.flowOn1_btn.clicked.connect(self.on_flowOn1)
        self.flowOn0_btn.clicked.connect(self.on_flowOn0)
        self.flowOff1_btn.clicked.connect(self.on_flowOff1)
        self.flowOff0_btn.clicked.connect(self.on_flowOff0)

        self.ardReset_btn = QtGui.QPushButton('reset flow')
        self.ardReset_btn.clicked.connect(self.on_ARDreset)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.flowOn0_btn)
        hbox.addWidget(self.flowOn1_btn)

        hboxOff = QtGui.QHBoxLayout()
        hboxOff.addWidget(self.flowOff0_btn)
        hboxOff.addWidget(self.flowOff1_btn)

        self.pumpFormLayout.addRow(QLabel("On time:"), hbox)
        self.pumpFormLayout.addRow(QLabel("Off time:"), hboxOff)
        self.pumpFormLayout.addRow(self.ardReset_btn)
        self.pumpForm.setLayout(self.pumpFormLayout)



    def createParamGroupBox(self):
        self.paramForm = QGroupBox("Trial parameters")
        self.paramFormLayout = QFormLayout()

        self.Timer_tbox = QtGui.QLineEdit()

        self.trialTime_tbox = QtGui.QLineEdit()
        self.trialTime_tbox.textChanged.connect(self.on_trialTime_changed)
        self.trialSleepTime_tbox = QtGui.QLineEdit()
        self.trialSleepTime_tbox.textChanged.connect(self.on_trialSleepTime_changed)
        self.trialTime_tbox.setText(str(self.trialTime))
        self.trialSleepTime_tbox.setText(str(self.trialSleepTime))
        self.Timer_tbox.setText(str(0))

        self.paramFormLayout.addRow(QLabel("Trial time:"), self.trialTime_tbox)
        self.paramFormLayout.addRow(QLabel("Stimulus time:"), self.trialSleepTime_tbox)

        self.paramFormLayout.addRow(QLabel("Time left:"), self.Timer_tbox)

        self.paramFormLayout.addRow(QLabel("Time:"), QSpinBox())
        self.paramForm.setLayout(self.paramFormLayout)



    def createDefaultGroupBox(self):
        self.defaultForm = QtGui.QGroupBox("Video capture")
        self.defaultFormLayout = QFormLayout()


        self.ArdPortComboBox = QComboBox()
        self.ArdPortComboBox.addItem("Port 14511",'/dev/cu.usbmodem14511')
        self.ArdPortComboBox.addItem("Port 14311",'/dev/cu.usbmodem14311')
        self.ArdPortComboBox.addItem("Port 1461",'/dev/cu.usbmodem1461')
        self.ArdPortComboBox.currentIndexChanged.connect(self.on_setARDport)

        self.cameraComboBox = QComboBox()
        self.cameraComboBox.addItem("0",'0')
        self.cameraComboBox.addItem("1",'1')
        self.cameraComboBox.currentIndexChanged.connect(self.on_setcameraport)

        self.start_btn = QtGui.QPushButton('start')
        self.start_btn.clicked.connect(self.on_start)

        ## stop flow button
        self.stop_btn = QtGui.QPushButton('stop')
        self.stop_btn.clicked.connect(self.on_stop)

        ## quit app button
        self.qbtn = QtGui.QPushButton('exit')
        self.qbtn.clicked.connect(self.on_quit)
        self.qbtn.clicked.connect(QtCore.QCoreApplication.instance().quit)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.start_btn)
        hbox.addWidget(self.stop_btn)
        hbox.addWidget(self.qbtn)

        self.defaultFormLayout.addRow(hbox)

        self.defaultFormLayout.addRow(QLabel("Arduino Port:"),\
                                     self.ArdPortComboBox)

        self.defaultFormLayout.addRow(QLabel("camera:"),\
                                     self.cameraComboBox)

        self.defaultForm.setLayout(self.defaultFormLayout)


    def createRecordGroupBox(self):
        self.recordForm = QtGui.QGroupBox("Video capture")
        self.recordFormLayout = QFormLayout()

        self.path_bx = QtGui.QLineEdit()
        self.resetPath()

        self.file_btn = QtGui.QPushButton("save to")
        self.file_btn.clicked.connect(self.on_getfile)

        self.file_bx = QtGui.QLineEdit()
        self.file_bx.textChanged.connect(self.on_fileChange)
        self.file_bx.setText(self.filename)


        self.save_btn = QtGui.QCheckBox()
        self.save_btn.setChecked(self.save)
        self.save_btn.stateChanged.connect(self.on_saveClick)


        hbox = QtGui.QHBoxLayout()
        self.recordFormLayout.addRow(self.file_btn, self.file_bx)
        self.recordFormLayout.addRow(QLabel("path:"), self.path_bx)
        self.recordFormLayout.addRow(QLabel("save:"), self.save_btn)


        self.recordForm.setLayout(self.recordFormLayout)


    #################
    ### slots
    ################




    @pyqtSlot()
    def on_getfile(self):
        self.foldername = QtGui.QFileDialog.getExistingDirectory()
        self.resetPath()

    @pyqtSlot()
    def on_fileChange(self):
        self.filename = self.file_bx.text()
        self.resetPath()

    @pyqtSlot()
    def on_setcameraport(self):
        self.initialise_videorecorder()

    @pyqtSlot()
    def on_trialTime_changed(self):
        try:
            self.trialTime = int(self.trialTime_tbox.text())

        except:
            self.trialTime_tbox.setText(str(1))
            print('only integrs valid')

    @pyqtSlot()
    def on_trialSleepTime_changed(self):
        try:
            self.trialSleepTime = int(self.trialSleepTime_tbox.text())
        except:
            self.trialSleepTime_tbox.setText(str(1))
            print('only integrs valid')

    @pyqtSlot()
    def on_setARDport(self):
        pass
      #  if self.ARD:
      #      self.ARDPort = self.ArdPortComboBox.currentData()
      #      print('ARD port set to ={0}'.format(self.ARDPort))
      #  else:
      #      print('no ARD detected')


    @pyqtSlot()
    def on_trialOn(self):
        print('trial starting')
        self.flowOn = False
        self.resetARD()
        self.trialTimer.restart()
        self.trialOn = True


    @pyqtSlot()
    def on_trialOff(self):
        print('trial ended')
        self.trialTimer.restart()
        self.trialOn = False
        self.flowOn = False
        self.resetARD()


    @pyqtSlot()
    def on_ARDreset(self):
        print('resetting ARD')
        self.resetFlowRate()


    @pyqtSlot()
    def on_flowOn1(self):
        print('changing flow rate')
        try:
            self.Ard.sendChar('u')
            self.resetARD()
        except:
            pass


    @pyqtSlot()
    def on_flowOn0(self):
        print('changing flow rate')
        try:
            self.Ard.sendChar('d')
            self.resetARD()
        except:
            pass

    @pyqtSlot()
    def on_flowOff1(self):
        print('changing flow rate')
        try:
            self.Ard.sendChar('k')
            self.resetARD()
        except:
            pass

    @pyqtSlot()
    def on_flowOff0(self):
        print('changing flow rate')
        try:
            self.Ard.sendChar('j')
            self.resetARD()
        except:
            pass


    @pyqtSlot()
    def on_lightOn(self):
        self.flowOn = True
        self.resetARD()

    @pyqtSlot()
    def on_lightOff(self):
        self.flowOn = False
        self.resetARD()


    @pyqtSlot()
    def on_slidervaluechange(self):
        self.pVal = int(self.slider.value())
        self.Tracker.pVal = self.pVal
        self.textSlider.setText(str(self.pVal))

    @pyqtSlot()
    def on_slider2valuechange(self):
        self.pVal_mx = int(self.slider2.value())
        self.Tracker.pVal_mx = self.pVal_mx
        self.textSlider2.setText(str(self.pVal_mx))

    @pyqtSlot()
    def on_ROIslidervaluechange(self):
        self.area_mn = int(self.ROIslider.value())
        self.Tracker.area_mn = self.area_mn
        self.ROItextSlider.setText(str(self.area_mn))


    @pyqtSlot()
    def on_start(self):
        if self.recording:
            print('current recording being stopping...')
            print('number of previously saved frames:\n{0}'.\
                  format(self.num_saved_frame))

            self.recording = False
            sleep(0.01)
            try:
                self.recorder.release_writer()
            except:
                pass
            sleep(0.01)
        print('new recording starting...')
        self.initialise_videorecorder()
        self.recording = True


    @pyqtSlot()
    def on_saveClick(self):
        self.on_start()
        if self.save_btn.isChecked():
            try:
                self.recorder.initialise_writer()
                print('writer initialised')
                sleep(0.02)
                self.save = self.save_btn.isChecked()
            except:
                print('couldn\'t initialise writer')
        else:
            try:
                self.recorder.release_writer()
            except:
                print('couldn\'t release writer')
                pass


    @pyqtSlot()
    def on_stop(self):
        print('current recording being stopping...')
        print('number of previously saved frames:\n{0}'.\
                  format(self.num_saved_frame))
        self.recording = False
        self.save = False
        self.save_btn.setChecked(self.save)

        try:
            self.recorder.release_writer()
            self.num_saved_frame = 0
        except:
            pass

    @pyqtSlot()
    def on_ROIinit(self):
        print('initiliase ROI')
        self.initialise_ROI()

    @pyqtSlot()
    def on_quit(self):
        print('stopping threads...')
        self.flowOn = False
        self.resetARD()
        self.recording = False
        self.trialOn = False
        sleep(0.5)
        print('number saved frames:\n{0}'.\
                  format(self.num_saved_frame))
        try:
            self.recorder.release_writer()
        except:
            pass
        try:
            self.recorder.release_camera()
        except:
            pass

        self.recordingThread.stop()
        self.trialThread.stop()


    def resetARD(self):
        if self.flowOn == False:
            if self.ARD:
                print('0')
                self.Ard.sendChar('0')
        if self.flowOn == True:
            if self.ARD:
                self.Ard.sendChar('1')

    def resetFlowRate(self):
        if self.ARD:
            self.Ard.sendChar('r')
            self.resetARD()

    def resetPath(self):
        self.dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")[2:]
        self.path =self.get_path()
        self.path_bx.setText(self.path)



    def kill_threads(self):
        self.recording = False
        self.trialOn = False


    def start_recording(self):
        if self.recording:
            self.frame_loop()

    def start_trial(self):
        if self.trialOn:
            self.trial_loop()



    ##########################
    ##### Thread functions
    ##########################
    def trial_loop(self):
        time_ = self.trialTimer.get_time()
        self.time_left = self.trialTime - int(time_)
        self.Timer_tbox.setText(str(self.time_left))
        if time_>self.trialTime:
            print('new trial')
            self.flowOn = True
            self.resetARD()
            sleep(int(self.trialSleepTime))
            self.flowOn = False
            self.resetARD()
            self.trialTimer.restart()


    def frame_loop(self):
        self.gray = self.grab_frame()
        self.blur = self.Tracker.blur_frame(self.gray)
        self.mvAvgFrame = self.update_avg()
        self.fD = self.Tracker.delta_frame(self.mvAvgFrame,self.blur)

        self.mask, self.masked = self.Tracker.mask_frame(self.fD, pVal=self.pVal, pVal_mx=self.pVal_mx)

        self.fD_, self.keypoints, self.num_fish_detected, self.max_a\
        = self.Tracker.get_frame_contours(self.masked, self.fD)


        self.maxArea_box.setText(str(self.max_a))
        self.num_detected_box.setText(str(self.num_fish_detected))

        if self.save:
            self.num_saved_frame +=1
            try:
                self.recorder.save_frame(self.gray)
            except:
                print('couldn\'t save file')
        self.show_frame()


    ##########################
    ##### detection functions
    ##########################

    def grab_frame(self):
        try:
            (grabbed, frame) = self.camera.read()
            self.frame = cv2.resize(frame, (self.imW,self.imH))
            self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            #self.frame = cv2.cvtColor(self.frame , cv2.COLOR_BGR2HSV)[:,:,1] # saturation
        except:
            print('couldn\'t grab frame')
            pass
        return self.gray


    def update_avg(self):
        if self.mvAvgFrame is None:
            self.mvAvgFrame = self.blur
        else:
            self.ite+=1
            fr = self.ite
            if fr>10000:
                print('reset')
                self.ite = 1
                self.mvAvgFrame = self.mvAvgFrame
            else:
                self.mvAvgFrame = self.mvAvgFrame*(fr/(fr+1)) + self.blur/(fr+1)
        return self.mvAvgFrame


    def show_frame(self):
        self.period = 100
        if self.ite % 4 ==1:
            self.imv1.setImage(self.gray.T)
        elif self.ite % self.period == 1:
            print('fps:{0}'.format(self.frameTimer.get_time()/self.period))
            self.frameTimer.restart()
            self.imv4.setImage(self.mvAvgFrame.T.astype('uint8'))
            print('frame #:{0}'.format(self.ite))
        elif self.ite % 4 ==2:
            self.imv2.setImage(self.fD_.swapaxes(0,1))
        elif self.ite % 4 ==3:
            self.imv3.setImage(self.mask.T)


def main():
    print('starting')
    T = MyLiveTracker()
    sys.exit(T.app.exec_())


if __name__ == '__main__':
    main()

#!/usr/bin/python3
from time import sleep
import numpy as np
import pyqtgraph as pg
import time, sys, os, cv2, serial
import argparse, datetime, imutils, threading
from PyQt5.QtGui import QApplication
from MyQtWidget import MyQtWidget


def main():
    app =  QApplication([])
    win = MyQtWidget()
    #tmp = QtGui.QCheckBox()
    sys.exit(app.exec_())



if __name__ =='__main__':
    main()
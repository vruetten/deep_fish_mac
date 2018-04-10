#!/usr/bin/python3
from PyQt5 import QtGui, QtCore

class MyQtWidget(QtGui.QWidget):
    def __init__(self, width = 1000, height = 800, title = 'go fish', x = 0, y = 0):
        super(MyQtWidget, self).__init__()
        self.title='go fish'
        self.title=title
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.move(self.x,self.y)
        self.resize(self.width,self.height)
        self.show()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

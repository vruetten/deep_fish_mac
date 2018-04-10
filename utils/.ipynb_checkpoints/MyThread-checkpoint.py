#!/usr/bin/python3
import threading

class MyThread(threading.Thread): 
    def __init__(self, function, wait_time= 0.01):
        super(MyThread,self).__init__()
        self._stop_event = threading.Event()
        self.function = function
        self.wait_time = wait_time
        
    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
    
    def run(self):
        while not self._stop_event.wait(self.wait_time):
            self.function()
            
            
class MyThread2(threading.Thread):
    def __init__(self, function, name = 'name'):
        threading.Thread.__init__(self)
        self.function = function
        self.name = name
        
    def run(self):
        print ("Starting" + self.name)
        self.function()
        print ("Exiting" + self.name)

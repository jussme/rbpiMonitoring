import picamera#the inconsitency is bothering me but.. whatever?
from gpiozero import MotionSensor
from datetime import datetime
from time import sleep
import threading
from time import time
import sys
import logging
import socket

pir = MotionSensor(17, queue_len = 1, threshold = 0.2, sample_rate = 50)
camera = picamera.PiCamera()

camera.annotate_background = picamera.Color('black')

connection = socket.socket()
connection.connect(('192.168.100.16', 60000))

timeout = 15 if len(sys.argv) == 1 else sys.argv[1]

dateFormat = '%d%m%Y_%H%M%S'

try:
    logging.basicConfig(filename='logFile.log', level=logging.INFO)
except PermissionError:
    print('Permissions unsufficient to create a log file in pwd')

def logWithDate(message):
    logging.info(datetime.now().strftime(dateFormat) + '\t' + message)

logWithDate('\n\nStarting program')

class State:
    def __init__(self):
        self._currentlyRecording = False
        self._currentlyRecordingLock = threading.Lock()

    def getCurrentlyRecording(self):#prob doesnt do much, a change can slip in
        logWithDate('getCurrentlyRecording returns ' + str(self._currentlyRecording))
        self._currentlyRecordingLock.acquire()
        currentlyRecording = self._currentlyRecording
        self._currentlyRecordingLock.release()
        return currentlyRecording
    
    def setCurrentlyRecording(self, state):
        logWithDate('setCurrentlyRecording to ' + str(state))
        self._currentlyRecordingLock.acquire()
        self._currentlyRecording = state
        self._currentlyRecordingLock.release()
    
state = State()

def stopRecording():
    camera.stop_recording()
    state.setCurrentlyRecording(False)
    logWithDate('Stopped recording')
    camera.annotate_text = 'Stopped recording'

class Counter:
    def _count(self):
        logWithDate('Starting the countdown')
        while self.readCounter() > 0:
            sleep(1)
            self.decrementCounter()
        if(state.getCurrentlyRecording()):
            stopRecording()
        else:
            logWithDate('Not recording, nothing to stop')
    
    def __init__(self, startingVal):
        self._counterStartingVal = startingVal
        self._counterLock = threading.Lock()
        self._thread = threading.Thread(target = self._count)
        logWithDate('Attempting to stop recording, in a dedicated thread')
    
    def getCurrentlyCounting(self):
        return True if self._thread.is_alive() else False
    
    def start(self):
        #if not self._thread.is_alive(): i trust my code x) start is called only in one function,
        #replaced with a dedicated function and a condition in an 'if' 
        self._counter = self._counterStartingVal
        self._thread = threading.Thread(target = self._count)
        self._thread.start()
    
    def decrementCounter(self):
        self._counterLock.acquire()
        self._counter = self._counter - 1
        self._counterLock.release()
        logWithDate('Counter decremented to ' + str(self._counter))
    
    def readCounter(self):
        self._counterLock.acquire()
        counterState = self._counter
        self._counterLock.release()
        return counterState
    
    def refreshCounter(self):
        logWithDate('Refreshing counter from ' + str(self._counter) + ' to ' + str(self._counterStartingVal))
        self._counterLock.acquire()
        self._counter = self._counterStartingVal
        self._counterLock.release()  
    
counter = Counter(timeout)
    
def startRecording(device):
    logWithDate('Movement detected..')
    if not state.getCurrentlyRecording():        
        filenameRep = datetime.now().strftime(dateFormat)
        try:
            camera.start_recording(connection, filenameRep + '.h264')
        except PermissionError:
            logWithDate('Permissions unsufficient to create a video file in pwd')
        state.setCurrentlyRecording(True)
        logWithDate('Recording ' + filenameRep)
    else:
        counter.refreshCounter()
    camera.annotate_text = 'movement: ' + datetime.now().strftime(dateFormat)

def stopRecording(device):
    camera.annotate_text = 'movement stopped: ' + datetime.now().strftime(dateFormat)
    logWithDate('Movement stopped')
    if state.getCurrentlyRecording() and not counter.getCurrentlyCounting():
        counter.start()
    else:
        logWithDate('Not starting the counter')

pir.when_motion = startRecording
pir.when_no_motion = stopRecording

input('Press Enter to exit the script')

connection.close()

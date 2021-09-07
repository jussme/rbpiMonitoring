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

timeout = 15
serverIP = ''
serverPort = 0

if len(sys.argv) == 3:
    serverIP = sys.argv[1]
    serverPort = int(sys.argv[2])
else:
    if len(sys.argv) == 4:
        timeout = int(sys.argv[3])
    else:
        print('Invalid arguments\n<serverIP> <serverPort> <OPTIONAL timeout>')
        exit()

dateFormat = '%d%m%Y_%H%M%S'

try:
    logging.basicConfig(filename='logFile.log', level=logging.INFO)
except:
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

class Counter:
    def _stopRecording(self, camera):
        camera.stop_recording()
        #connectionFile.flush()
        state.setCurrentlyRecording(False)
        logWithDate('Stopped recording')
        camera.annotate_text = 'Stopped recording'
    
    def _count(self, camera):
        logWithDate('Starting the countdown')
        while self._readCounter() > 0:
            sleep(1)
            self._decrementCounter()
        if(state.getCurrentlyRecording()):
            self._stopRecording(camera)
        else:
            logWithDate('Not recording, nothing to stop')
    
    def __init__(self, startingVal):
        self._counterStartingVal = startingVal
        self._counterLock = threading.Lock()
        self._thread = threading.Thread(target = self._count)#not going to be started
    
    def getCurrentlyCounting(self):
        counting = True if self._thread.is_alive() else False
        logWithDate('getCurrentlyCounting returns ' + str(counting))
        return counting
    
    def start(self, camera):
        #if not self._thread.is_alive(): i trust my code x) start is called only in one function,
        #replaced with a dedicated function and a condition in an 'if' 
        self._counter = self._counterStartingVal
        self._thread = threading.Thread(target = self._count, args = (camera,))
        self._thread.start()
    
    def _decrementCounter(self):
        self._counterLock.acquire()
        self._counter = self._counter - 1
        self._counterLock.release()
        logWithDate('Counter decremented to ' + str(self._counter))
    
    def _readCounter(self):
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
    
def startCameraRecording(camera, serverIP, serverPort):
    connectionSocket = socket.socket()
    connectionSocket.connect((serverIP, serverPort))
    connectionFile = connectionSocket.makefile('wb')
    camera.start_recording(connectionFile, 'h264')
    
def startRecording(device):
    logWithDate('Movement detected..')
    if not state.getCurrentlyRecording():        
        filenameRep = datetime.now().strftime(dateFormat)
        try:
            startCameraRecording(camera, serverIP, serverPort)
        except Exception as e:
            logWithDate('startRecording(device) exception:\n' + str(e))
        state.setCurrentlyRecording(True)
        logWithDate('Recording ' + filenameRep)
    else:
        counter.refreshCounter()
    camera.annotate_text = 'movement: ' + datetime.now().strftime(dateFormat)

def stopRecording(device):
    camera.annotate_text = 'movement stopped: ' + datetime.now().strftime(dateFormat)
    logWithDate('Movement stopped')
    if state.getCurrentlyRecording() and not counter.getCurrentlyCounting():
        counter.start(camera)
    else:
        logWithDate('Not starting the counter')

pir.when_motion = startRecording
pir.when_no_motion = stopRecording

input('Press Enter to exit the script')

connectionFile.close()
connectionSocket.close()

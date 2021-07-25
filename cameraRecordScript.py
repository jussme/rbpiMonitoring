from picamera import PiCamera
from gpiozero import MotionSensor
from datetime import datetime
from time import sleep
import threading
from time import time
import sys
import logging

pir = MotionSensor(17, queue_len = 1, threshold = 0.2, sample_rate = 50)
camera = PiCamera()

timeout = 15 if len(sys.argv) == 1 else sys.argv[1]

try:
    logging.basicConfig(filename='logFile.log', level=logging.INFO)
except PermissionError:
    print('Permissions unsufficient to create a log file in pwd')

def logWithDate(message):
    logging.info(datetime.now().strftime('%H%M%S_%d%m%Y') + '\t' + message)

logWithDate('\n\nStarting program')

class State:
    def __init__(self):
        self._latestTimeStamp = 10
        self._currentlyRecording = False
        self._timeStampLock = threading.Lock()
        self._currentlyRecordingLock = threading.Lock()
    
    def getLatestTimeStamp(self):
        logWithDate('getLatestTimeStamp returns' + str(self._latestTimeStamp))
        self._timeStampLock.acquire()
        latestTimeStamp = self._latestTimeStamp
        self._timeStampLock.release()
        return latestTimeStamp
    
    def setLatestTimeStamp(self, timeStamp):
        logWithDate('setLatestTimeStamp to ' + str(timeStamp))
        self._timeStampLock.acquire()
        self._latestTimeStamp = timeStamp
        self._timeStampLock.release()
        
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

def startRecording(device):
    logWithDate('Movement detected..')
    if not state.getCurrentlyRecording():        
        filenameRep = datetime.now().strftime('%H%M%S_%d%m%Y')
        try:
            camera.start_recording(filenameRep + '.h264')
        except PermissionError:
            logWithDate('Permissions unsufficient to create a video file in pwd')
        state.setCurrentlyRecording(True)
        logWithDate('Recording ' + filenameRep)
    state.setLatestTimeStamp(int(time()))

def attemptToStopRecording():
    logWithDate('Attempting to stop recording, in a dedicated thread')
    sleep(timeout)
    if int(time()) - state.getLatestTimeStamp() >= timeout:
        logWithDate('Timeout passed before ' + int(time()) + ' with ' + state.getLatestTimeStamp())
        if state.getCurrentlyRecording:
            camera.stop_recording()
            state.setCurrentlyRecording(False)
        logWithDate('Stopped recording')
    logWithDate('Attempt finished')

def stopRecording(device):
    logWithDate('No movement is being detected')
    state.setLatestTimeStamp(int(time()))
    threading.Thread(target = attemptToStopRecording).start()

pir.when_motion = startRecording
pir.when_no_motion = stopRecording

input('Press Enter to exit the script')
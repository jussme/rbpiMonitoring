from picamera import PiCamera
from gpiozero import MotionSensor
from datetime import datetime
from time import sleep
import threading
from time import time
import sys

pir = MotionSensor(17, queue_len = 1, threshold = 0.2, sample_rate = 50)
camera = PiCamera()

timeout = 15 if len(sys.argv) == 1 else sys.argv[1]

timeStampLock = threading.Lock()
currentlyRecordingLock = threading.Lock()

currentlyRecording = False

currentTimeStamp = 10

def dummyFunc():
    for x in range(0, 2):
        y = x+2

recordingThread = threading.Thread(target = dummyFunc)

def startRecording(device):
    global currentlyRecording
    global currentTimeStamp
    print('Movement detected..')
    currentlyRecordingLock.acquire()
    if not currentlyRecording:        
        now = datetime.now()
        filenameRep = now.strftime('%H%M%S_%d%m%Y')
        camera.start_recording('./' + filenameRep + '.h264')
        currentlyRecording = True
        currentlyRecordingLock.release()
        print('Recording' + filenameRep)
    else:
        currentlyRecordingLock.release()
    timeStampLock.acquire()
    currentTimeStamp = int(time())
    timeStampLock.release()

def attemptToStopRecording():
    global currentlyRecording
    global currentTimeStamp
    print('Attempting to stop recording')
    sleep(timeout)
    timeStampLock.acquire()
    if int(time()) - currentTimeStamp >= timeout:
        timeStampLock.release()
        currentlyRecordingLock.acquire()
        if currentlyRecording:
            camera.stop_recording()
            currentlyRecording = False
        currentlyRecordingLock.release()
        print('Stopped recording')
    else:
        timeStampLock.release()
    print('Attempt finished')

def stopRecording(device):
    print('No movement is being detected')
    timeStampLock.acquire()
    currentTimeStamp = int(time())
    timeStampLock.release()
    threading.Thread(target = attemptToStopRecording).start()

pir.when_motion = startRecording
pir.when_no_motion = stopRecording

while True:
    sleep(100)
    #print(('YES' if pir.motion_detected else 'nope')
    #+ ', val:' +  str(pir.value))
    #pir.wait_for_motion()

import picamera
from gpiozero import MotionSensor
from datetime import datetime
from time import sleep
import threading
from time import time
import sys
import logging
import socket

def setupLogging():
    try:
        logging.basicConfig(filename='logFile.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
    except PermissionError:
        print('Permissions unsufficient to create a log file in pwd')

class Counter:
    def _stopRecording(self, camera):
        camera.annotate_text = 'Stopped recording'
        try:
            camera.stop_recording()
            logging.info('Stopped recording')
        except Exception as e:
            logging.exception(e)
    
    def _count(self, camera):
        logging.info('Starting the countdown')
        while self._counter > 0:
            sleep(1)
            self._counter = self._counter - 1
            logging.info('Decremented from ' + str(self._counter+1) + ' to ' + str(self._counter))
        if camera.recording:
            self._stopRecording(camera)
        else:
            logging.info('Not recording, nothing to stop')
    
    def __init__(self, startingVal):
        self._counterStartingVal = startingVal
        self._counterLock = threading.Lock()
        self._thread = threading.Thread(target = self._count)#not going to be started
    
    def getCurrentlyCounting(self):
        counting = True if self._thread.is_alive() else False
        logging.info('getCurrentlyCounting returns ' + str(counting))
        return counting
    
    def start(self, camera): 
        self._counter = self._counterStartingVal
        self._thread = threading.Thread(target = self._count, args = (camera,))
        self._thread.start()
    
    def refreshCounter(self):
        logging.info('Refreshing counter from ' + str(self._counter) + ' to ' + str(self._counterStartingVal))
        self._counter = self._counterStartingVal
    
def startCameraRecording(camera, serverIP, serverPort):
    connectionSocket = socket.socket()
    connectionSocket.connect((serverIP, serverPort))
    connectionFile = connectionSocket.makefile('wb')
    camera.start_recording(connectionFile, 'h264')
    camera.vflip = flip
    camera.hflip = flip
    
def startRecording(device):
    logging.info('Movement detected..')
    if not camera.recording:        
        filenameRep = datetime.now().strftime(dateFormat)
        try:
            startCameraRecording(camera, serverIP, serverPort)
        except Exception as e:
            logging.exception(e)
        logging.info('Recording ' + filenameRep)
    else:
        counter.refreshCounter()
    camera.annotate_text = 'movement: ' + datetime.now().strftime(dateFormat)

def stopRecording(device):
    camera.annotate_text = 'movement stopped: ' + datetime.now().strftime(dateFormat)
    logging.info('Movement stopped')
    if camera.recording and not counter.getCurrentlyCounting():
        counter.start(camera)
    else:
        logging.info('Not starting the counter')

def main():
    setupLogging()
    logging.info('Starting program')
    
    pir.when_motion = startRecording
    pir.when_no_motion = stopRecording

    input('Press Enter to exit the script')

    connectionFile.close()
    connectionSocket.close()
    
if __name__ == '__main__':
    pir = MotionSensor(17, queue_len = 1, threshold = 0.2, sample_rate = 50)
    camera = picamera.PiCamera()
    camera.annotate_background = picamera.Color('black')

    timeout = 15
    serverIP = None
    serverPort = None

    if len(sys.argv) == 4:
        serverIP = sys.argv[1]
        serverPort = int(sys.argv[2])
        flip = sys.argv[3] == 'True'
    else:
        if len(sys.argv) == 5:
            timeout = int(sys.argv[4])
        else:
            print('Invalid arguments\n<serverIP> <serverPort> <horizontalFlipBoolean> <OPTIONAL timeout>')
            exit(1)

    dateFormat = '%d%m%Y_%H%M%S'
    counter = Counter(timeout)
    
    main()

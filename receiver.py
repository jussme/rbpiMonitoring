import socket
import os
import threading
import logging
from datetime import datetime

dateFormat = '%d%m%Y_%H%M%S'
timeoutSecs = 10

try:
    logging.basicConfig(filename='logFile.log', level=logging.INFO)
except PermissionError:
    print('Permissions unsufficient to create a log file in pwd')

def logWithDate(message):
    logging.info(datetime.now().strftime(dateFormat) + '\t' + message)

logWithDate('\n\nStarting program')

def createFile(filePath):
    if not os.path.isfile(filePath):
        try:
            open(filePath, "x")
        except Exception as e:
            print(str(e))
            exit(1);

serverSocket = socket.socket()
serverSocket.bind(('0.0.0.0', 60000))
serverSocket.listen(0)

def readFile(connectionSocket):
    logWithDate('Reading...')
    connectionSocket.settimeout(timeoutSecs)
    connectionFile = connectionSocket.makefile('rb')
    filenameRep = "R" + datetime.now().strftime(dateFormat) + ".h264"
    createFile(filenameRep)
    with open(filenameRep, 'wb') as recordingFile:
        try:
            while True:
                data = connectionFile.read(1024)
                if not data:
                    break
                recordingFile.write(data)
        except Exception as e:
            logWithDate(str(e))
    
    connectionFile.close()
    
    logWithDate('File has been saved')

logWithDate('Listening...')

def readFiles(serverSocket):
    while True:
        try:
            connectionSocket = serverSocket.accept()[0]
        finally:
            #doesnt intercept the exit() exception?
            #consumed somewhere lower?
            serverSocket.close()
        readFile(connectionSocket)
        connectionSocket.close()

threading.Thread(target = readFiles, args = (serverSocket,)).start()

input('Press enter to exit')

serverSocket.close()


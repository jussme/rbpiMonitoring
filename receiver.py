import socket
import os
import sys
import threading
import logging
from datetime import datetime
import quickstart

def readFile(connectionSocket, recordingsDir):
    logWithDate('Reading...')
    connectionSocket.settimeout(15)
    connectionFile = connectionSocket.makefile('rb')
    if not recordingsDir.endswith('/'):
        recordingsDir = recordingsDir + '/'
    fileName = "R" + datetime.now().strftime(dateFormat) + ".h264"
    filePath = recordingsDir + fileName
    createFile(filePath)
    with open(filePath, 'wb') as recordingFile:
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
    
    return filePath

def readFiles(serverSocket, recordingsDir):
        logWithDate('Listening...')
        while True:
            try:
                connectionSocket = serverSocket.accept()[0]
                filePath = readFile(connectionSocket, recordingsDir)
                connectionSocket.close()
                consumeFile(filePath)
            except Exception as e:
                #doesnt intercept the exit() exception?
                #consumed somewhere lower?
                logWithDate('readFiles exception: ' + str(e))
    
def consumeFile(filePath):
    folderName = datetime.now().strftime("%d%m%Y") 
    folderID = quickstart.createFolder(folderName)
    threading.Thread(target=targetF, args=(filePath, folderID)).start()
    
def setupLogging(dateFormat):
    try:
        logging.basicConfig(filename='logFile.log', level=logging.DEBUG)
    except PermissionError:
        print('Permissions unsufficient to create a log file in pwd')
        
#method wrapping logging, cant do "enums"
def logWithDate(message, logType='info'):
    logMessage = datetime.now().strftime(dateFormat) + '\t' + message
    if logType == 'info':
        logging.info(logMessage)
    else:
        if logType == 'exception':
            logging.exception(message)
    
def main():
    dateFormat='%d%m%Y_%H%M%S'
    setupLogging(dateFormat)
    logWithDate('\n\nStarting program')
    
    #create recordings dir if doesnt exist
    try:
        os.mkdir(recFolder)
        logWithDate('recordings dir created')
    except FileExistsError:
        logWithDate('recordings dir existed')

    def createFile(filePath):
        if not os.path.isfile(filePath):
            try:
                open(filePath, "x")
            except Exception as e:
                logWithDate(e,logType='exception')
                exit(1);

    #launch
    serverSocket = socket.socket()
    serverSocket.bind(('0.0.0.0', serverLocalPort))
    serverSocket.listen(0)
    
    if deleteLocal:
        targetF = quickstart.moveFileOnline
    else:
        targetF = quickstart.uploadFile
    
    readFiles(serverSocket, recFolder)

    serverSocket.close()

if __name__ == "__main__":
    if len(sys.argv) == 4:
        recFolder = sys.argv[1]
        serverLocalPort = int(sys.argv[2])
        deleteLocal = bool(sys.argv[3])
        main()
    else:
        print('Invalid arguments\n<recordingDirPath> <serverLocalPort> <deleteLocalFiles>')
else:
    recFolder = input("recordingDirPath: ")
    serverLocalPort = int(input("serverLocalPort: "))

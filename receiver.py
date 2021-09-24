import socket
import os
import sys
import threading
import logging
from datetime import datetime
import quickstart

def readFile(connectionSocket, recordingsDir):
    logging.info('Reading...')
    connectionSocket.settimeout(15)
    connectionFile = connectionSocket.makefile('rb')
    if not recordingsDir.endswith('/'):
        recordingsDir = recordingsDir + '/'
    fileName = "R" + datetime.now().strftime('%d%m%Y_%H%M%S') + ".h264"
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
            logging.exception(e)
    
    connectionFile.close()
    
    logging.info('File has been saved')
    
    return filePath

def readFiles(serverSocket, recordingsDir):
        logging.info('Listening...')
        while True:
            try:
                connectionSocket = serverSocket.accept()[0]
                filePath = readFile(connectionSocket, recordingsDir)
                connectionSocket.close()
                consumeFile(filePath)
            except Exception as e:
                #doesnt intercept the exit() exception?
                #consumed somewhere lower?
                logging.exception(e)
    
def consumeFile(filePath):
    folderName = datetime.now().strftime("%d%m%Y") 
    folderID = quickstart.mkDirOnline(folderName)
    if deleteLocal:
        targetF = quickstart.moveFileOnline
    else:
        targetF = quickstart.uploadFile
    threading.Thread(target=targetF, args=(filePath, folderID)).start()
    
def setupLogging():
    try:
        logging.basicConfig(filename='logFile.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
    except PermissionError:
        print('Permissions unsufficient to create a log file in pwd')
        
#method wrapping logging, cant do "enums"
def logWithDate(message, logType='info'):
    if logType == 'info':
        logging.info(logMessage)
    else:
        if logType == 'exception':
            logging.exception(message)

def createFile(filePath):
        if not os.path.isfile(filePath):
            try:
                open(filePath, "x")
            except Exception as e:
                logging.exception(e)
                exit(1);

def main():
    setupLogging()
    logging.info("Starting program...")
    
    #create recordings dir if doesnt exist
    try:
        os.mkdir(recFolder)
        logging.info('recordings dir created')
    except FileExistsError:
        logging.info('recordings dir existed')

    

    #launch
    serverSocket = socket.socket()
    serverSocket.bind(('0.0.0.0', serverLocalPort))
    serverSocket.listen(0)
    
    readFiles(serverSocket, recFolder)

    serverSocket.close()
    del dateFormat
    
if __name__ == "__main__":
    if len(sys.argv) == 4:
        recFolder = sys.argv[1]
        serverLocalPort = int(sys.argv[2])
        deleteLocal = bool(sys.argv[3])
        main()
    else:
        print('Invalid arguments\n<recordingDirPath> <serverLocalPort> <deleteLocalFilesBoolean>')
else:
    recFolder = input("recordingDirPath: ")
    serverLocalPort = int(input("serverLocalPort: "))
    deleteLocal = bool(input("deleteLocalFileBoolean: "))

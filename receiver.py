import socket
import os
from datetime import datetime

def createFile(filePath):
    if not os.path.isfile(filePath):
        try:
            open(filePath, "ax")
        except:
            print("Cannot create file")
            exit(1);

serverSocket = socket.socket()
serverSocket.bind('0.0.0.0', 60000)
serverSocket.listen(0)

connection = serverSocket.accept()[0]

createFile("recording")
dateFormat = '%d%m%Y_%H%M%S'
filenameRep = datetime.now().strftime(dateFormat)
with open(filenameRep + ".mkv") as recordingFile:
    while True :
       data = connection.read(1024)
       if not data:
           break
       recordingFile.write(data)
       
serverSocket.close()
connection.close()
from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime

    #returns gdrive service object
def authorizeDriveService():
    # If modifying these scopes, delete the file token.json.
    #only app created files
    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    #disabled the cache, throws errors; isnt used anyway?
    return build('drive', 'v3', credentials=creds, cache_discovery=False)

folderProperty = "pirecordingsfolder"
mimeTypeFolder = "application/vnd.google-apps.folder"
def fileResourceMatchesTemplate(fileRes, template):
    for key in template:
        if str(template.get(key)) != str(fileRes.get(key)):
            return False
    return True

def findFileRes(filesRes, resTemplate):
    for fileRes in filesRes:
        if fileResourceMatchesTemplate(fileRes, resTemplate):
            return fileRes
    return None

def findFolderIDByName(drive, folderName):
    resTemplate = {
        "name": folderName,
        "trashed": "False",
    }
    nextPageToken = None
    while True:
        response = drive.files().list(q="mimeType = 'application/vnd.google-apps.folder'", pageToken=nextPageToken, fields="nextPageToken, files(id,name,trashed)").execute()
        folderRes = findFileRes(response.get("files", []), resTemplate)
        if folderRes:
            return folderRes.get("id")
        if not nextPageToken:
            break
    
    return None

    #returns folder id
def mkDirOnline(folderName, parentID=None):
    drive = authorizeDriveService()
    folderID = findFolderIDByName(drive, folderName)
    if not folderID:
        folderData = {
            "name": folderName,
            "mimeType": mimeTypeFolder
        }
        if parentID:
            folderData["parents"] = [parentID]
        folder = drive.files().create(body=folderData, fields="id").execute()
        folderID = folder.get("id")
    
    return folderID
    
def uploadFile(filePath, parentFolderID):
    drive = authorizeDriveService()
    fileData = {
        "name": os.path.basename(filePath),
        "parents": [parentFolderID]
    }
    media = MediaFileUpload(filePath, resumable=True)
    drive.files().create(body=fileData, media_body=media).execute()
      

import json
import os

import requests
from thefuzz import fuzz
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from io import BytesIO

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'C:/Users/Nahom tamirat.DESKTOP-O0JRFDT\Desktop\PROJECT\Flask\market-place\evaluator\service_account.json'
PARENT_FOLDER_ID = '1IOR4Yu2xydWWd_khNcM8diP2SLT8UqUO'

def similarity_test(ans_list, ans_given):
  result = []
  score = 0
  
  for x in range(len(ans_given)):
    if type(ans_given[x]) is str:
      similarity = fuzz.ratio(ans_given[x], ans_list[x])
      if similarity >= 75:
        result.append(ans_given[x])
        score += 1
        
    elif type(ans_given[x]) is list:
      for y in ans_given[x]:
        similarity = fuzz.ratio(y, ans_list[x])
        if similarity >= 75:
          result.append(y)
          score += 1

  return result, score

def text_detection4(img_data_bytes):
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNDg1NzMwODUtZDA2Yi00ZTg1LWIyZWYtOTQ0Njk2ODRiYzlkIiwidHlwZSI6ImFwaV90b2tlbiJ9.ShuKVYOyi53B3CYhhWJLzqlAJ7YRayjGalUaGLq9if8"}
    url = "https://api.edenai.run/v2/ocr/ocr"
    data = {"providers": "google", "language": "en"}
    files = {"file": ('image.jpg', img_data_bytes)}  # Using a tuple to provide filename and bytes data
    response = requests.post(url, data=data, files=files, headers=headers)
    print(response, data)
    result = json.loads(response.text)
    print(result["google"]["text"], type(result["google"]["text"]))
    return result["google"]["text"]


def authenticate():
  creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
  return creds


def upload_exam(file_path, exam_name, upload_file, school_folder):
  creds = authenticate()
  service = build('drive', 'v3', credentials=creds)
  
  file_metadata = {
    'name': exam_name,
    'parents': [school_folder]
  }

  media = MediaFileUpload(file_path, mimetype=upload_file.content_type)
  file = service.files().create(
    body=file_metadata,
    media_body=media
  ).execute()


# CREATE FOLDER
def create_folder(folder_name):
  try:
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {
      'name': folder_name,
      'mimeType': 'application/vnd.google-apps.folder',
      'parents': [PARENT_FOLDER_ID]
    }
    
    # pylint: disable=maybe-no-member
    file = service.files().create(body=file_metadata, fields='id'
    ).execute()
    print(F'Folder ID: "{file.get("id")}".')
    return file.get('id')
  except Exception as error:
    print(F'An error occurred: {error}')
    return None


# SEARCH FILE
def search_file(target_name):
  try:
    creds = authenticate()
    
    # create drive api client
    service = build('drive', 'v3', credentials=creds)
    target_file_name = []
    target_file_id = ''
    page_token = None
    while True:
      query = f"'{PARENT_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder'"
      response = service.files().list(q=query,
        spaces='drive',
        fields='nextPageToken, '
               'files(id, name)',
        pageToken=page_token
      ).execute()
      
      for file in response.get('files', []):
        if file.get("name") == target_name:
          target_file_name.append(file.get("name"))
          target_file_id += file.get("id")
          
      page_token = response.get('nextPageToken', None)
      if page_token is None:
        break
    return target_file_name, target_file_id
  except Exception as error:
    print(error, 'error search')
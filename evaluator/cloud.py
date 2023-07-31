import json

import requests
from thefuzz import process, fuzz

def similarity_test(ans_list, ans_given):
  result = {}
  score = 0
  for x in range(len(ans_list)):
    similarity = fuzz.ratio(ans_list[x], ans_given[x])
    result.update({ans_list[x]: similarity})
    if similarity >= 75:
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
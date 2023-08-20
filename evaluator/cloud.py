import json

import requests
from thefuzz import fuzz

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
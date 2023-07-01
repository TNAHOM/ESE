import boto3
from thefuzz import process
import time

def upload_img(img):
	start = time.time()
	
	s3 = boto3.resource('s3')
	bucket = s3.Bucket('first-textract')
	# replace the key value to the name of the worksheet owner
	bucket.upload_file(Key='textract2.jpg', Filename=img)
	end = time.time()
	print('textract', end - start)

def to_textract(img_path):
	start = time.time()
	textract = boto3.client('textract')
	# # Call the Textract API to detect text in the image
	# with open(img_path, 'rb') as image:
	response = textract.detect_document_text(Document={'Bytes': img_path})
	items = []
	for item in response["Blocks"]:
		if item["BlockType"]=="LINE":
			items.append(item["Text"])
	end = time.time()
	print('textract', end-start)
	return items

def similarity_test(answer, correct_list):
	result = process.extractOne(answer, correct_list)
	return result

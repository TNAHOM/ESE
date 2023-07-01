import io
import json
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from thefuzz import process

credential_file = 'evaluator/credential.json'

credential = json.load(open(credential_file))
API_KEY, ENDPOINT = credential['API_KEY'], credential['ENDPOINT']

# Create a Computer Vision client
cv_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(API_KEY))


def text_detection(image_path):
	answer = []
	response = cv_client.read_in_stream(io.BytesIO(image_path), raw=True)
	
	operation_location = response.headers['Operation-Location']
	operation_id = operation_location.split('/')[-1]
	
	status = OperationStatusCodes.running
	
	while status==OperationStatusCodes.running:
		result = cv_client.get_read_result(operation_id)
		status = result.status
		
		# Check if the operation succeeded
		if status==OperationStatusCodes.succeeded:
			if result.analyze_result is not None:
				read_result = result.analyze_result.read_results
				for analyze_result in read_result:
					# print(analyze_result, 'ana')
					for line in analyze_result.lines:
						answer.append(line.text)
			else:
				print('Analyze result is None.')
		
		elif status==OperationStatusCodes.failed:
			print('Error incounterd, it could be connectivity or timeout.')
			return 'Failed'
		
	answer = [item.replace('-', '') for item in answer if item.replace('-', '')!='']
	return answer


def similarity_test(answer, correct_list):
	result = process.extractOne(answer, correct_list)
	return result

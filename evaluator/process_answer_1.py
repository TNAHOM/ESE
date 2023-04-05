import cv2
from evaluator import utlis
import numpy as np
from pyzbar.pyzbar import decode
from pdf417decoder import PDF417Decoder
from PIL import Image as PIL
from pyzbar.pyzbar import ZBarSymbol


class General:
	def __init__(self, img, answer=None, questions=None, choices=None):
		self.answer = answer
		self.img = img
		self.grade = []
		self.questions = questions
		self.choices = choices
	
	def func_choose(self):
		imgWrapGray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
		imgThresh = cv2.threshold(imgWrapGray, 137, 250, cv2.THRESH_BINARY_INV)[1]
		boxes = utlis.splitBoxes(imgThresh, self.questions, self.choices)

		# GETTING NO ZERO PIXEL VALUES OF EACH BOX
		myPixelVal = np.zeros((self.questions, self.choices))
		countC = 0
		countR = 0
		
		for image in boxes:
			totalPixels = cv2.countNonZero(image)
			myPixelVal[countR][countC] = totalPixels
			countC += 1
			if countC==self.choices: countR += 1;countC = 0

		new_boxes = []
		for x in myPixelVal:
			ind = 0
			new_list = np.delete(x, ind)
			for box in new_list:
				new_boxes.append(box)
		
		new_shape = np.reshape(new_boxes, (self.questions, self.choices-1))
		# print('new_shape', new_shape)
		new_list = np.delete(new_shape, 0, 0)
		new_shape2 = np.reshape(new_list, (self.questions-1, self.choices-1))
		# print(new_shape2)
		
		# FINDING INDEX VALUES OF MARKING
		myIndex = []
		# print(len(new_shape2))
		
		disqualified_ans = []
		for x in range(self.questions-1):
			# sort for the higher darken choose
			arr = new_shape2[x]
			sorted_arr = sorted(arr)
			# print(sorted_arr)
			
			# arr[3] = because the [3] is the second most colored
			# possible 2 answer
			if sorted_arr[3] > 1500:
				myIndex.append(9)
				sorted_index_value = list(np.argsort(arr)[-2:])
				# print(sorted_index_value, 'sorted')
				disqualified_ans.append(sorted_index_value)
				
			else:
				myIndexVal = np.where(arr==np.amax(arr))
				# print(myIndexVal[0])
				myIndex.append(myIndexVal[0][0])
		# print(disqualified_ans, 'incorrect index')

		incorrect_ans=[]
		# print(self.questions, len(myIndex))
		for x in range(self.questions-1):
			if self.answer[x]==myIndex[x]:
				self.grade.append(1)
			# possible two answers
			elif myIndex[x] == 9:
				self.grade.append(2)
			else:
				self.grade.append(0)
				incorrect_ans.append(myIndex[x])
		# print(incorrect_ans, 'inc_ans')
		disqualified_que = []
		incorrect_que = []

		total_sum = []
		for x in range(0, len(self.grade)):
			if self.grade[x] == 1:
				total_sum.append(self.grade[x])
			elif self.grade[x] == 0:
				incorrect_que.append(x+1)
			elif self.grade[x] == 2:
				disqualified_que.append(x+1)
		# print(incorrect_que, 'popo')
		imgResult = self.img.copy()
		imgResult = utlis.showAnswers(imgResult, myIndex, self.grade, self.answer, self.questions, self.choices)
	
		return sum(total_sum), self.questions, imgResult, imgThresh, disqualified_que, incorrect_que, incorrect_ans
	
	def func_tf(self):
		imgWrapGray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
		imgThresh = cv2.threshold(imgWrapGray, 137, 250, cv2.THRESH_BINARY_INV)[1]
		boxes = utlis.splitBoxes(imgThresh, self.questions, self.choices)
		# GETTING NO ZERO PIXEL VALUES OF EACH BOX
		myPixelVal = np.zeros((self.questions, self.choices))
		countC = 0
		countR = 0
		
		for image in boxes:
			totalPixels = cv2.countNonZero(image)
			myPixelVal[countR][countC] = totalPixels
			countC += 1
			if countC==self.choices: countR += 1;countC = 0
		
		new_list = np.delete(myPixelVal, 0, 0)
		# for x in new_list:
		# 	print(x, 'pixel')

		# new_shape2 = np.reshape(new_list, (self.questions - 1, self.choices))
		# FINDING INDEX VALUES OF MARKING
		myIndex = []

		for x in range(0, self.questions - 1):
			arr = new_list[x]
			# print(x, arr)
			sorted_arr = sorted(arr)
			# print('sorted', sorted_arr)
			
			if sorted_arr[0] > 6000:
				myIndex.append(9)
			else:
				myIndexVal = np.where(arr==np.amax(arr))
				myIndex.append(myIndexVal[0][0])
		# print(myIndex, 'myIndex')
		for x in range(0, self.questions - 1):
			print(self.answer[x], myIndex[x])
			if self.answer[x]==myIndex[x]:
				self.grade.append(1)
			elif myIndex[x]==9:
				self.grade.append(2)
			else:
				self.grade.append(0)
		# print(self.grade, 'self.grade')
		total_sum = []
		disqualified_que = []
		no_answer_given = []
		for x in range(0, len(self.grade)):
			if self.grade[x]==1:
				total_sum.append(self.grade[x])
			elif self.grade[x]==2:
				disqualified_que.append(x + 1)
			elif self.grade[x]==3:
				no_answer_given.append(x + 1)
		

		imgResult = self.img.copy()
		imgResult = utlis.showAnswers_tf(imgResult, myIndex, self.grade, self.answer, self.questions, self.choices)
		# cv2.imshow('qw', imgResult)
		
		# will allow to print by the number of question
		# cv2.imshow('ko', imgResult)
		return sum(total_sum), self.questions, imgResult, imgThresh, disqualified_que, no_answer_given
	
	
	def qrcode_reader(self):
		# decoder = PDF417Decoder(self.img)
		# print(decoder.decode())
		# if (decoder.decode() > 0):
		# 	decoded = decoder.barcode_data_index_to_string(0)
		# 	print(decoded)
		# decode(self.img, symbols=[ZBarSymbol.QRCODE])
		# qcode = decode(self.img, symbols=[ZBarSymbol.QRCODE])
		# for x in qcode:
		# 	print(x.data.decode('utf-8'))
		try:
			qrcode = decode(self.img, symbols=[ZBarSymbol.QRCODE])
			for x in qrcode:
				myData = x.data.decode('utf-8')
				return myData
		except Exception as ed:
			print('process_answer qr', ed)
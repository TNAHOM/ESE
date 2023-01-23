import cv2
from evaluator import utlis
import numpy as np
from pyzbar.pyzbar import decode


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
		# print('----')
		
		new_list = np.delete(new_shape, 0, 0)
		new_shape2 = np.reshape(new_list, (self.questions-1, self.choices-1))
		# print(new_shape2)
		
	
		# FINDING INDEX VALUES OF MARKING
		myIndex = []
		# print(len(new_shape2))
		for x in range(0, self.questions-1):
			arr = new_shape2[x]
			# print('-', arr)
			sorted_arr = sorted(arr)
			# print(sorted_arr)
			
			# .append(8) = no answer was given
			# if sorted_arr[4] < 900:
			# 	myIndex.append(8)
			
			# arr[3] = because the [3] is the second most colored
			# possible 2 answer
			if sorted_arr[3] > 1500:
				myIndex.append(9)
			else:
				myIndexVal = np.where(arr==np.amax(arr))
				# print(myIndexVal[0])
				myIndex.append(myIndexVal[0][0])
		# print(len(myIndex))
		# grading = []
		# print('----')
		for x in range(0, self.questions-1):
			if self.answer[x]==myIndex[x]:
				self.grade.append(1)
			elif myIndex[x] == 9:
				self.grade.append(2)
			elif myIndex[x] == 8:
				self.grade.append(3)
			else:
				self.grade.append(0)
				
		total_sum = []
		disqualified_que = []
		no_answer_written = []
		for x in range(0, len(self.grade)):
			if self.grade[x] == 1:
				total_sum.append(self.grade[x])
			elif self.grade[x] == 2:
				disqualified_que.append(x+1)
			elif self.grade[x] == 3:
				no_answer_written.append(x+1)
				
		# print(self.answer)
		imgResult = self.img.copy()
		imgResult = utlis.showAnswers(imgResult, myIndex, self.grade, self.answer, self.questions, self.choices)
		# cv2.imshow('qw', imgResult)
		
		# will allow to print by the number of question
		# total_grade = self.grade[:self.questions]
		# cv2.imshow('ko', imgResult)
		return sum(total_sum), self.questions, imgResult, imgThresh, disqualified_que, no_answer_written

	def qrcode_reader(self):
		try:
			for barcode in decode(self.img):
				myData = barcode.data.decode('utf-8')
				return myData
		# 	when it cant grab the frame
		except -1072875772:
			print('cant grab')
			return 'cant grab'
		except Exception as ed:
			print('process_answer qr', ed)
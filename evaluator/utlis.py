import cv2
import numpy as np

# 17:00:00
def rectContour(contours):
  rectCon = []
  max_area = 0
  for i in contours:
    # gives the area of given countours
    area = cv2.contourArea(i)
    # print(area)
    if area > 50:
      # FIND THE PERIMETER(LENGTH)
      # SAY TRUE=FOR CLOSED POLYGON/ONLY WORK FOR CLOSED POLYGON
      peri = cv2.arcLength(i, True)
      approx = cv2.approxPolyDP(i, 0.05 * peri, True)
      # print('Corner Point numbers', len(approx))
      # if the corner point is 4 then put it in a list
      if len(approx)==4:
        rectCon.append(i)
  # print(rectCon)
  # SORT BY contourArea BY DESCENDING(LARGE TO SMALLER)
  rectCon = sorted(rectCon, key=cv2.contourArea, reverse=True)
  # print('len of cont', len(rectCon))
  return rectCon


# GET 4 CORNER POINTS FOR THE GIVEN(EG: [0] MEANS THE FIRST BIGGEST ONE FROM THE GIVEN FUNCTION SORTED
def getCornerPoints(cont):
  peri = cv2.arcLength(cont, True)  # LENGTH OF CONTOUR
  approx = cv2.approxPolyDP(cont, 0.02 * peri, True)  # APPROXIMATE THE POLY TO GET CORNER POINTS
  return approx


# 33:00:00
def reorder(myPoints):
  myPoints = myPoints.reshape((4, 2))  # REMOVE EXTRA BRACKET
  # print(myPoints)
  myPointsNew = np.zeros((4, 1, 2), np.int32)  # NEW MATRIX WITH ARRANGED POINTS
  add = myPoints.sum(1)
  # print(add)  # myPoints = [[217 103] [161 342] [558 376] [549 137]]
  # then add the points add = [320 503 934 686] ([217 103] = [320]
  # so the smaller the sum the origin is it
  
  # print(np.argmax(add))
  # The origin value [217 103] = [320]
  myPointsNew[0] = myPoints[np.argmin(add)]  # [0,0]
  # Then the largest point sum [558 376] = [934]
  myPointsNew[3] = myPoints[np.argmax(add)]  # [w,h]
  diff = np.diff(myPoints, axis=1)
  myPointsNew[1] = myPoints[np.argmin(diff)]  # [w,0]
  myPointsNew[2] = myPoints[np.argmax(diff)]  # [h,0]
  # print(diff)
  
  return myPointsNew

# def splitBoxes(img, questions, choices):
# 	img = np.array(img)
# 	rows = np.vsplit(img, questions)
# 	# cv2.imshow('s', rows[1])
# 	boxes = []
# 	for r in rows:
# 		cols = np.hsplit(r, choices)
# 		# cv2.imshow('fd', cols[1])
# 		for box in cols:
# 			boxes.append(box)
# 	return boxes
def splitBoxes(img, questions, choices):
    img = np.array(img)
    num_rows, num_cols = img.shape[0], img.shape[1]

    # Calculate the number of rows and columns to split based on the number of questions and choices
    row_segments = split_array(list(range(num_cols)), questions)
    col_segments = split_array(list(range(num_rows)), choices)

    boxes = []
    current_col = 0

    for row_segs in row_segments:
        current_row = 0
        for col_segs in col_segments:
            boxes.append(img[current_row: current_row + col_segs, current_col: current_col + row_segs])
            current_row += col_segs
        current_col += row_segs

    return boxes

def split_array(array, num_parts):
    total_elements = len(array)
    segment_length = total_elements // num_parts
    remaining_elements = total_elements % num_parts

    result = []

    current_index = 0
    for i in range(num_parts):
        current_segment_length = segment_length + 1 if i < remaining_elements else segment_length
        result.append(current_segment_length)
        current_index += current_segment_length

    return result

def splitExp(img, questions):
  img = np.array(img)
  row = np.vsplit(img, questions)
  return row

# def drawGrid(img, questions=30, choices=5):
# 	secW = int(img.shape[1] / choices)
# 	secH = int(img.shape[0] / questions)
# 	for i in range(0, 9):
# 		pt1 = (0, secH * i)
# 		pt2 = (img.shape[1], secH * i)
# 		pt3 = (secW * i, 0)
# 		# print('pt3', pt3)
# 		pt4 = (secW * i, img.shape[0])
# 		cv2.line(img, pt1, pt2, (255, 255, 0), 2)
# 		cv2.line(img, pt3, pt4, (255, 255, 0), 2)
# 	return img


# 01:18:00
# def showAnswers(img, myIndex, grading, answer, questions, choices):
# 	# 600/5=120 image.shape[1] = original width that have been assign in OMR_main.py
# 	secW = int(img.shape[1]/choices)
# 	# print(img.shape[0])
# 	# print(secW)
# 	secH = int(img.shape[0] / questions)
# 	# print('g', len(myIndex))
#
# 	for x in range(0, questions):
# 		myAns = myIndex[x]
# 		# print('a', myAns)
# 		cX = (myAns * secW) + secW // 2  # Find the center value
# 		cY = (x * secH) + secH // 2
# 		if grading[x]==1:
# 			# print('Grd in utls', grading[x])
# 			myColor = (0, 255, 0)
# 			# cv2.rectangle(img, (myAns*(secW), x*secH), ((myAns*(secW))+secW, (x*secH)+secH), myColor, cv2.FILLED)
# 			cv2.circle(img, (cX, cY), 12, myColor, cv2.FILLED)
# 		# cv2.rectangle(img, cX, cY, myColor, cv2.FILLED)
# 		else:
# 			myColor = (0, 0, 255)
# 			correctAns = answer[x]
# 			# cv2.rectangle(img, (myAns * (secW), x * secH), ((myAns * (secW)) + (secW), (x * secH) + secH), myColor, cv2.FILLED)
# 			cv2.circle(img, ((correctAns * secW) + secW // 2, (x * secH) + secH // 2), 10, (0, 255, 0), cv2.FILLED)
# 		cv2.circle(img, (cX, cY), 10, myColor, cv2.FILLED)
# 	return img

def showAnswers(img, myIndex, grading, answer, questions=None, choices=None):
  # print(img.shape[0], img.shape[1], '----------------')
  # cv2.imshow('wrt', col[0])
  # 600/5=120 image.shape[1] = original width that have been assign in OMR_main.py
  secW = int(img.shape[1] / choices)
  # print(img.shape[0])
  secH = int(img.shape[0] / questions)
  # print(grading)
  for x in range(0, questions-1):
    # print('questions', questions)
    myAns = myIndex[x]
    # print(len(myIndex))
    cX = secW + (myAns * secW) + secW // 2  # Find the center value
    cY = secH + (x * secH) + secH // 2
    dx = secW + ( -1* secW) + secW//2
    # print(grading, 'grading')
    if grading[x]!=-1:
    
      if grading[x]==1:
        # print('Grd in utls', grading[x])
        myColor = (0, 255, 0)
        # cv2.rectangle(img, (myAns*(secW), x*secH), ((myAns*(secW))+secW, (x*secH)+secH), myColor, cv2.FILLED)
        cv2.circle(img, (cX, cY), 14, myColor, cv2.FILLED)
      # cv2.rectangle(img, cX, cY, myColor, cv2.FILLED)
      elif grading[x]==2:
        myColor = (255, 255, 255)
        cv2.circle(img, (dx, cY), 18, myColor, cv2.FILLED)
      elif grading[x]==3:
        myColor = (255, 255, 0)
        cv2.circle(img, (dx, cY), 18, myColor, cv2.FILLED)
      elif grading[x]==0:
        myColor = (0, 255, 0)
        correctAns = answer[x]
        # cv2.rectangle(img, (myAns * (secW), x * secH), ((myAns * (secW)) + (secW), (x * secH) + secH), myColor, cv2.FILLED)
        cv2.circle(img, (secW + (correctAns * secW) + secW // 2, secH + (x * secH) + secH // 2), 10, (255, 0, 0), cv2.FILLED)
        # cv2.circle(img, (cX, cY), 18, (0, 255, 0), cv2.FILLED)
      cv2.circle(img, (cX, cY), 9, myColor, cv2.FILLED)
  return img


def showAnswers_tf(img, myIndex, grading, answer, questions=None, choices=None):
  # cv2.imshow('wrt', col[0])
  # 600/5=120 image.shape[1] = original width that have been assign in OMR_main.py
  secW = int(img.shape[1] / choices)
  # print(img.shape[0])
  secH = int(img.shape[0] / questions)

  for x in range(0, questions-1):
    # print(x+1, grading[x]')
    myAns = myIndex[x]

    cX = (myAns * secW) + secW // 2  # Find the center value
    cY = secH + (x * secH) + secH // 2
    dX = (1 * secW)
    if grading[x]!=-1:
      
      if grading[x]==1:
        myColor = (0, 255, 0)
        cv2.circle(img, (cX, cY), 30, myColor, cv2.FILLED)
      elif grading[x]==2:
        myColor = (255, 255, 255)
        cv2.circle(img, (dX, cY), 35, myColor, cv2.FILLED)
      elif grading[x]==3:
        myColor = (255, 255, 0)
        cv2.circle(img, (dX, cY), 18, myColor, cv2.FILLED)
      elif grading[x]==0:
        myColor = (0, 255, 0)
        correctAns = answer[x]

        # cv2.rectangle(img, (myAns * (secW), x * secH), ((myAns * (secW)) + (secW), (x * secH) + secH), myColor, cv2.FILLED)
        cv2.circle(img, (secW + (correctAns * secW) + secW // 2, secH + (x * secH) + secH // 2), 10, (255, 0, 0),
          cv2.FILLED)
      cv2.circle(img, (cX, cY), 20, myColor, cv2.FILLED)
  return img

def img_warp(img_box, img, widthImg, heightImg):
  img_box = reorder(img_box)
  pt1 = np.float32(img_box)
  pt2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
  matrix = cv2.getPerspectiveTransform(pt1, pt2)
  imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))
  return imgWarpColored

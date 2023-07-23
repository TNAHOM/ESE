import cv2
import numpy as np
from evaluator import utlis


class TryClass:
  def __init__(self, img, sz_num, width=None, height=None, img_num=None):
    self.img = img
    # Not for webcam
    # self.read = cv2.imread(self.img)
    self.sz_num = sz_num
    self.width = width
    self.height = height
    self.img_num = img_num
    
  
  def process_img(self):
    img = cv2.resize(self.img, (self.width, self.height))
    # img = cv2.rotate(not_img, cv2.ROTATE_90_CLOCKWISE)
    imgBiggestCountour = img.copy()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
    imgCanny = cv2.Canny(imgBlur, 10, 50)
    countours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    rectCon = utlis.rectContour(countours)
    # print('kl', len(rectCon))
    x = utlis.getCornerPoints(rectCon[self.sz_num])
    # y = utlis.getCornerPoints(rectCon[1])
    # z = utlis.getCornerPoints(rectCon[2])
    # u = utlis.getCornerPoints(rectCon[3])
    # v = utlis.getCornerPoints(rectCon[4])
    # w = utlis.getCornerPoints(rectCon[5])

    if x.size!=0:
      # cv2.drawContours(imgBiggestCountour, x, -1, (0, 255, 0), 15)
      # cv2.drawContours(imgBiggestCountour, y, -1, (0, 255, 0), 15)
      # cv2.drawContours(imgBiggestCountour, z, -1, (0, 255, 0), 15)
      # cv2.drawContours(imgBiggestCountour, u, -1, (0, 255, 0), 15)
      # cv2.drawContours(imgBiggestCountour, v, -1, (0, 255, 0), 15)
      # cv2.drawContours(imgBiggestCountour, w, -1, (0, 255, 0), 15)

      img_warped = utlis.reorder(x)
      pt1 = np.float32(img_warped)

      pt2 = np.float32([[0, 0], [self.width, 0], [0, self.height], [self.width, self.height]])
      matrix = cv2.getPerspectiveTransform(pt1, pt2)
      
      imgWarpColored = cv2.warpPerspective(img, matrix, (self.width, self.height))

      # img_warped_2 = utlis.reorder(y)
      # img_warped_3 = utlis.reorder(z)
      # img_warped_4 = utlis.reorder(u)
      # img_warped_5 = utlis.reorder(v)
      # img_warped_6 = utlis.reorder(w)

      
      # print(tuple(map(tuple, pt2)), 'tuple->pt2')
      # print(pt1, 'pt2')
      # write is the top and write2 is the bottom
      # CHOOSE1
      # write = tuple(map(tuple, img_warped[0]))  # --> top left
      # write2 = tuple(map(tuple, img_warped[2])) # --> bottom left
      # write3 = tuple(map(tuple, img_warped[1])) # --> bottom right
      # mid = write[0][0]
      # mid2 = (write[0][1] + write2[0][1]) // 2
			#
      # write_2 = tuple(map(tuple, img_warped_2[0]))
      # write2_2 = tuple(map(tuple, img_warped_2[2]))
      # write3_2 = tuple(map(tuple, img_warped_2[1]))
      # mid_2 = write_2[0][0]
      # mid2_2 = (write_2[0][1] + write2_2[0][1]) // 2

      # CHOOSE
      # write_3 = tuple(map(tuple, img_warped_3[0]))
      # write2_3 = tuple(map(tuple, img_warped_3[2]))
      # write3_3 = tuple(map(tuple, img_warped_3[1]))
      # mid_3 = (write_3[0][0])
      # mid2_3 = (write_3[0][1] + write2_3[0][1]) // 2 - (write_3[0][1] // 3)
			#
      # # Matching
      # write_4 = tuple(map(tuple, img_warped_4[0]))
      # write2_4 = tuple(map(tuple, img_warped_4[2]))
      # write3_4 = tuple(map(tuple, img_warped_4[1]))
      # mid_4 = write_4[0][0]
      # mid2_4 = (write_4[0][1] + write2_4[0][1]) // 2 + (write_4[0][1] // 3)
			#
      # # T/F
      # write_5 = tuple(map(tuple, img_warped_5[0]))
      # write2_5 = tuple(map(tuple, img_warped_5[2]))
      # write3_5 = tuple(map(tuple, img_warped_5[1]))
      # mid_5 = write_5[0][0]
      # mid2_5 = (write_5[0][1] + write2_5[0][1]) // 2
			#
      # # CODE
      # write_6 = tuple(map(tuple, img_warped_6[0]))
      # write2_6 = tuple(map(tuple, img_warped_6[2]))
      # write3_6 = tuple(map(tuple, img_warped_6[1]))
      # mid_6 = write_6[0][0]
      # mid2_6 = (write_6[0][1] + write2_6[0][1]) // 2
			#
      #
      # cv2.putText(imgBiggestCountour, 'CHOOSE2', (mid, mid2), cv2.FONT_HERSHEY_COMPLEX,
      #   1, (0, 255, 255), 2)
      # cv2.putText(imgBiggestCountour, 'CHOOSE1', (mid_2, mid2_2), cv2.FONT_HERSHEY_COMPLEX,
      #   1, (0, 255, 255), 2)
      # cv2.putText(imgBiggestCountour, 'NAME', (mid_3, mid2_3), cv2.FONT_HERSHEY_COMPLEX,
      #   1, (0, 255, 255), 2)
      # cv2.putText(imgBiggestCountour, 'MATCHING', (mid_4, mid2_4), cv2.FONT_HERSHEY_COMPLEX,
      #   1, (0, 255, 255), 2)
      # cv2.putText(imgBiggestCountour, 'CODE', (mid_5, mid2_5), cv2.FONT_HERSHEY_COMPLEX,
      #   1, (0, 255, 255), 2)
      # cv2.putText(imgBiggestCountour, 'T/F', (mid_6, mid2_6), cv2.FONT_HERSHEY_COMPLEX,
      #   1, (0, 255, 255), 2)
      #
      # cv2.imshow('imgWarpColored', imgBiggestCountour)
      # cv2.waitKey(0)
      return imgWarpColored, imgBiggestCountour

  def process_img_folder(self):
    # not_img = cv2.resize(self.img, (self.width, self.height))
    # img = cv2.rotate(not_img, cv2.ROTATE_90_CLOCKWISE)
    img = self.img
    
    imgBiggestCountour = img.copy()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
    imgCanny = cv2.Canny(imgBlur, 10, 50)
    countours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    rectCon = utlis.rectContour(countours)
    # print('kl', len(rectCon))
    x = utlis.getCornerPoints(rectCon[self.sz_num])
    if x.size!=0:
      cv2.drawContours(imgBiggestCountour, x, -1, (0, 255, 0), 15)
      
      img_warped = utlis.reorder(x)
      # print(img_warped, 'imgwarped')
      pt1 = np.float32(img_warped)
      # print(pt1[0],pt1, 'pt1')
      
      pt2 = np.float32([[0, 0], [self.width, 0], [0, self.height], [self.width, self.height]])
      matrix = cv2.getPerspectiveTransform(pt1, pt2)
      imgWarpColored = cv2.warpPerspective(img, matrix, (self.width, self.height))
      
      return imgWarpColored, imgBiggestCountour
  

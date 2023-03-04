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
      not_img = cv2.resize(self.img, (self.width, self.height))
      img = cv2.rotate(not_img, cv2.ROTATE_90_CLOCKWISE)
      imgBiggestCountour = img.copy()
      imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
      imgCanny = cv2.Canny(imgBlur, 10, 50)
      countours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
      rectCon = utlis.rectContour(countours)
      # print('kl', len(rectCon))
      x = utlis.getCornerPoints(rectCon[self.sz_num])
      y = utlis.getCornerPoints(rectCon[1])
      z = utlis.getCornerPoints(rectCon[2])
      if x.size!=0:
        cv2.drawContours(imgBiggestCountour, x, -1, (0, 255, 0), 15)
        cv2.drawContours(imgBiggestCountour, y, -1, (0, 255, 0), 15)
        cv2.drawContours(imgBiggestCountour, z, -1, (0, 255, 0), 15)


        # cv2.imshow('we', imgBiggestCountour)
        
        img_warped = utlis.reorder(x)
        # print(img_warped, 'imgwarped')
        pt1 = np.float32(img_warped)
        # print(pt1[0],pt1, 'pt1')
        pt2 = np.float32([[0, 0], [self.width, 0], [0, self.height], [self.width, self.height]])
        matrix = cv2.getPerspectiveTransform(pt1, pt2)
        
        img_warped_2 = utlis.reorder(y)
        img_warped_3 = utlis.reorder(z)

        
        # print(tuple(map(tuple, pt2)), 'tuple->pt2')
        # print(pt1, 'pt2')
        # write is the top and write2 is the bottom
        write = tuple(map(tuple, img_warped[0]))
        write2 = tuple(map(tuple, img_warped[2]))
        write3 = tuple(map(tuple, img_warped[1]))
        mid = ((write[0][0] + write3[0][0])//2 - (write[0][0]//8))
        mid2 = (write[0][1] + write2[0][1])//2

        write_2 = tuple(map(tuple, img_warped_2[0]))
        write2_2 = tuple(map(tuple, img_warped_2[2]))
        write3_2 = tuple(map(tuple, img_warped_2[1]))
        mid_2 = ((write_2[0][0] + write3_2[0][0]) // 2 - (write_2[0][0] // 8))
        mid2_2 = (write_2[0][1] + write2_2[0][1]) // 2

        write_3 = tuple(map(tuple, img_warped_3[0]))
        write2_3 = tuple(map(tuple, img_warped_3[2]))
        write3_3 = tuple(map(tuple, img_warped_3[1]))
        mid_3 = ((write_3[0][0] + write3_3[0][0]) // 2 - (write_3[0][0] // 16))
        mid2_3 = (write_3[0][1] + write2_3[0][1]) // 2
        
        imgWarpColored = cv2.warpPerspective(img, matrix, (self.width, self.height))
        
        cv2.putText(imgBiggestCountour, '2', (mid, mid2), cv2.FONT_HERSHEY_COMPLEX,
          3, (0, 255, 255), 3)
        cv2.putText(imgBiggestCountour, '1', (mid_2, mid2_2), cv2.FONT_HERSHEY_COMPLEX,
	        3, (0, 255, 255), 3)
        cv2.putText(imgBiggestCountour, '3', (mid_3, mid2_3), cv2.FONT_HERSHEY_COMPLEX,
	        2, (0, 255, 255), 3)
        return imgWarpColored, imgBiggestCountour
      

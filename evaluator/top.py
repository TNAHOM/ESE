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

    if x.size!=0:
      # cv2.drawContours(imgBiggestCountour, x, -1, (0, 255, 0), 15)
      # cv2.imshow('we', imgBiggestCountour)
      # cv2.waitKey(0)
      cv2.destroyAllWindows()
      img_warped = utlis.reorder(x)
      pt1 = np.float32(img_warped)

      pt2 = np.float32([[0, 0], [self.width, 0], [0, self.height], [self.width, self.height]])
      matrix = cv2.getPerspectiveTransform(pt1, pt2)
      
      imgWarpColored = cv2.warpPerspective(img, matrix, (self.width, self.height))
      # cv2.imshow('mk', imgWarpColored)
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
  

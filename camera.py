import cv2
import numpy as np

class digimono_camera:
    def __init__(self):
       pass 
    def __enter__(self):
        return self
    def __exit__(self, ex_type, ex_value, trace):
        pass
        #print("exit")
    #マスクを作成し、抽出した数とその中心点を返す
    #引数：画像、閾値（２行３列）
    #戻り地：マスク、輪郭（配列）・抽出したものの中心点（配列）
    def mask_detect(self, img, threshold):
        #hsv色空間に変換
        hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        #maskの作成(２値化)
        hsv_min = threshold[1,]
        hsv_max = threshold[0,]
        mask = cv2.inRange(hsv, hsv_min, hsv_max)

        #neiborhood = np.array([[0, 1, 0],
        #                       [1, 1, 1],
        #                       [0, 1, 0]],
        #                       np.uint8)

        #mask = cv2.dilate(mask, neiborhood, iterations = 2)
        #mask = cv.erode(mask, neiborhood, iterations = 2)

        #輪郭の抽出
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #imgとマスクの合算
        mask = cv2.bitwise_and(img, img, mask=mask)
        #必要な輪郭のみ抽出する
        ret_contours = []
        for i in range(len(contours)):
            area = cv2.contourArea(contours[i])
            if(area > 700):
                ret_contours.append(contours[i])
        #位置を格納する変数の定義
        point = []
        for i in range(len(ret_contours)):
            mu = cv2.moments(ret_contours[i])
            x,y = int(mu["m10"]/mu["m00"]), int(mu["m01"]/mu["m00"])
            point.append([x, y])
        return mask, ret_contours, point

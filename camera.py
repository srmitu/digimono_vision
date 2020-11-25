# -*- coding: utf-8 -*-
import cv2
import numpy as np
import threading 
from threading import Thread
from threading import RLock
import time
import camera_frame

class digimono_camera(camera_frame.digimono_camera_frame):

    def __init__(self):
        self.frame = cv2.imread('opencv.jpeg')
        self.lock = RLock()
        self.thread = Thread(target=self.mask_detect, args=())
        self.thread.daemon = True
        self.thread.start()
        #初期化
        self.cutout = 0
        self.mask = 0
        
        self.threshold=[]
        #赤色のときは閾値は２つ
        #それ以外のときは閾値は１つ
        self.contours = []
        self.point = []
        self.task = 0

    def __enter__(self):
        return self
    def __exit__(self, ex_type, ex_value, trace):
        pass
        #print("exit")0
    #マスクを作成し、抽出した数とその中心点を求める
    def mask_detect(self):
        while True:
            #hsv色空間に変換
            camera_frame = self.frame
            hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
            #maskの作成(２値化)
            if len(self.threshold) == 2:
                hsv_min = self.threshold[1,]
                hsv_max = self.threshold[0,]
                self.mask = cv2.inRange(hsv, hsv_min, hsv_max)
            elif len(self.threshold) == 4:
                hsv_min = self.threshold[1,]
                hsv_max = self.threshold[0,]
                mask1 = cv2.inRange(hsv, hsv_min, hsv_max)
                hsv_min = self.threshold[3,]
                hsv_max = self.threshold[2,]
                mask2 = cv2.inRange(hsv, hsv_min, hsv_max)
                
                self.mask = mask1 + mask2
                
            if len(self.threshold) > 0:
                #neiborhood = np.array([[0, 1, 0],
                #                       [1, 1, 1],
                #                       [0, 1, 0]],
                #                       np.uint8)

                #self.mask = cv2.dilate(self.mask, neiborhood, iterations = 2)
                #self.mask = cv.erode(self.mask, neiborhood, iterations = 2)

                #輪郭の抽出
                all_contours, hierarchy = cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                #imgとマスクの合算
                #self.mask = cv2.bitwise_and(hsv, hsv, mask=self.mask)
                self.cutout = cv2.bitwise_and(camera_frame, camera_frame, mask=self.mask)
                while True:
                    if(self.task == 0):
                        break
                with self.lock:
                    #必要な輪郭のみ抽出する
                    self.contours = []
                    for i in range(len(all_contours)):
                        area = cv2.contourArea(all_contours[i])
                        if(area > 700):
                            self.contours.append(all_contours[i])
                    #print(self.contours)
                    #位置を格納する変数の定義
                    self.point = []
                    for i in range(len(self.contours)):
                        mu = cv2.moments(self.contours[i])
                        if int(mu["m00"]) != 0:
                            x,y = int(mu["m10"]/mu["m00"]), int(mu["m01"]/mu["m00"])
                            self.point.append([x, y])
                    self.task =1

    def in_frame(self, inFrame):
        self.frame = inFrame

    def in_threshold(self, inThreshold):
        self.threshold = inThreshold
    def get_contours(self):
        return_contours = []
        with self.lock:
            return_contours = self.contours
        return return_contours

    def get_lock(self):
        return self.lock

    def get_point(self):
        return_point = []
        with self.lock:
            return_point = self.point
        return return_point

    def get_mask(self):
        return self.mask
    def get_task(self):
        with self.lock:
            return_task = self.task
        return return_task
    def in_task(self, inTask):
        self.task = inTask
    def get_cutout(self):
        return self.cutout

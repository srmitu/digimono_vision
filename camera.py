# -*- coding: utf-8 -*-
import cv2
import numpy as np
import threading 
from threading import Thread
from threading import RLock
import time
import camera_frame

class digimono_camera(camera_frame.digimono_camera_frame):

    def __init__(self, threshold, draw_color):
        self.frame = cv2.imread('opencv.jpeg')
        #初期化
        self.cutout = 0
        self.mask = 0
        self.threshold = threshold
        #赤色のときは閾値は２つ
        #それ以外のときは閾値は１つ
        self.contours = []
        self.point = []
        self.task = 0
        self.draw_color = tuple(draw_color)
        self.resize_vertical = 600
        self.resize_wide =720
        self.permit_area = 500
        
        self.thread = Thread(target=self.mask_detect, args=())
        self.thread.daemon = True
        self.thread.start()

    def __enter__(self):
        return self
    def __exit__(self, ex_type, ex_value, trace):
        pass
        #print("exit")
    #マスクを作成し、抽出した数とその中心点を求める
    def mask_detect(self):
        while True:
            while True:
                if(self.task == 0):
                    break
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
                
                neiborhood = np.array([[0, 1, 0],
                                       [1, 1, 1],
                                       [0, 1, 0]],
                                       np.uint8)
                
                self.mask = cv2.morphologyEx(self.mask, cv2.MORPH_OPEN, neiborhood)
                #輪郭の抽出
                all_contours, hierarchy = cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                #imgとマスクの合算
                self.cutout = cv2.bitwise_and(camera_frame, camera_frame, mask=self.mask)
                #必要な輪郭のみ抽出する
                self.contours = []
                for i in range(len(all_contours)):
                    area = cv2.contourArea(all_contours[i])
                    if(area > self.permit_area):
                        self.contours.append(all_contours[i])
                #位置を格納する変数の定義
                self.point = []
                for i in range(len(self.contours)):
                    mu = cv2.moments(self.contours[i])
                    if int(mu["m00"]) != 0:
                        x,y = int(mu["m10"]/mu["m00"]), int(mu["m01"]/mu["m00"])
                        self.point.append([x, y])
                self.task =1

    def put_frame(self, inFrame):
        self.frame = inFrame
        self.task = 0

    def put_threshold(self, inThreshold):
        self.threshold = inThreshold
    def get_contours(self):
        return_contours = []
        return_contours = self.contours
        return return_contours


    def get_point(self):
        return_point = []
        return_point = self.point
        return return_point

    def get_mask(self):
        return self.mask
    def get_task(self):
        return_task = self.task
        return return_task
    def put_task(self, inTask):
        self.task = inTask
    def get_cutout(self):
        return self.cutout

    def show_mask(self, num_screen):
        title_mask = "Mask" + str(num_screen)
        cv2.namedWindow(title_mask, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(title_mask, self.resize_wide, self.resize_vertical)
        cv2.imshow(title_mask, self.mask)

    def show_cutout(self, num_screen):
        title_cutout = "Cutout" + str(num_screen)
        cv2.namedWindow(title_cutout, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(title_cutout, self.resize_wide, self.resize_vertical)
        cv2.imshow(title_cutout, self.cutout)

    def draw_contours(self, edit_frame):
        return_edit_frame = edit_frame
        for num_contours in range(len(self.contours)):
            return_edit_frame = cv2.drawContours(edit_frame, self.contours, num_contours, self.draw_color, 3)
        return return_edit_frame

    def put_resize(self, vertical, wide):
        self.resize_wide = wide
        self.resize_vertical = vertical

# -*- coding: utf-8 -*-
import cv2
import numpy
from multiprocessing import Process, Manager, Value, Array
class digimono_camera_mask(object):

    def __init__(self, threshold, draw_color):
        
        #初期化
        #共有設定
        self.frame = Array('i', 0)
        self.mask = Array('i', 0)
        self.threshold = Array('i', 0)
        self.draw_color = Array('i', 0)

        self.threshold = threshold
        self.draw_color = tuple(draw_color)

        self.resize_vertical = 600
        self.resize_wide =720
        self.permit_area = 500

    def __enter__(self):
        return self
    def __exit__(self, ex_type, ex_value, trace):
        pass
    #マスクを作成し、抽出した数とその中心点を求める
    def mask_detect(self, frame, contours, point):
        #i.value += 1
        #hsv色空間に変換
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #maskの作成(２値化)
        if(len(self.threshold) == 2):
            mask = cv2.inRange(hsv, self.threshold[1,], self.threshold[0,])
        elif(len(self.threshold) == 4):
            mask1 = cv2.inRange(hsv, self.threshold[1,], self.threshold[0,])
            mask2 = cv2.inRange(hsv, self.threshold[3,], self.threshold[2,])
            mask = mask1 + mask2
        
        if(len(self.threshold) == 2 or len(self.threshold) == 4):
            self.mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, numpy.ones((5,5), numpy.uint8))
            #輪郭の抽出
            all_contours, hierarchy = cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            #必要な輪郭のみ抽出する
            for num_all_contours in range(len(all_contours)):
                if(cv2.contourArea(all_contours[num_all_contours]) > self.permit_area):
                    contours.append(all_contours[num_all_contours])
                    mu = cv2.moments(all_contours[num_all_contours])
                    x,y = int(mu["m10"]/mu["m00"]), int(mu["m01"]/mu["m00"])
                    point.append([x, y])

    def get_mask(self):
        return self.mask
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

    def draw_contours(self, edit_frame, contours):
        return_edit_frame = edit_frame.copy()
        for num_contours in range(len(contours)):
            return_edit_frame = cv2.drawContours(edit_frame, self.contours, num_contours, self.draw_color, 2)
        return return_edit_frame

    def put_resize(self, vertical, wide):
        self.resize_wide = wide
        self.resize_vertical = vertical

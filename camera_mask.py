# -*- coding: utf-8 -*-
import cv2
import numpy
from multiprocessing import Manager, Value, Array, Event
class digimono_camera_mask(object):

    def __init__(self, draw_color):
        #初期化
        self.draw_color = tuple(draw_color)

    def __enter__(self):
        return self
    def __exit__(self, ex_type, ex_value, trace):
        pass

    #マスクを作成し、抽出した数とその中心点を求める
    def mask_detect(self, hsv_frame, contours, point, threshold, permit_area, task):
        #毎度更新必要:frame
        #毎度更新される:contours, point, task
        #値変更必要なし(初期に入れるのみ):threshold, point_erea
        pattern = len(threshold)
        task.value = 1
        while True:
            while task.value == 1:
                pass
            hsv = hsv_frame[0]
            #maskの作成(２値化)
            if(pattern == 2):
                mask1 = cv2.inRange(hsv, threshold[1], threshold[0])
                mask = mask1 
            elif(pattern == 4):
                mask1 = cv2.inRange(hsv, threshold[1], threshold[0])
                mask2 = cv2.inRange(hsv, threshold[3], threshold[2])
                mask = mask1 + mask2
            if(pattern == 2 or pattern == 4):
                #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, numpy.ones((5,5), numpy.uint8))
                #輪郭の抽出
                all_contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                #必要な輪郭のみ抽出する
                for num_all_contours in range(len(all_contours)):
                    if(cv2.contourArea(all_contours[num_all_contours]) > permit_area):
                        contours.append(all_contours[num_all_contours])
                        mu = cv2.moments(all_contours[num_all_contours])
                        x,y = int(mu["m10"]/mu["m00"]), int(mu["m01"]/mu["m00"])
                        point.append([x, y])
            
            task.value = 1

    def draw_contours(self, edit_frame, contours, thickness):
        return_edit_frame = edit_frame.copy()
        for num_contours in range(len(contours)):
            return_edit_frame = cv2.drawContours(edit_frame, contours, num_contours, self.draw_color, thickness)
        return return_edit_frame
    
    def draw_point(self, frame, point):
        return_frame = frame
        for num_point in range(len(point)):
            return_frame = cv2.circle(frame, tuple(point[num_point]), 5, tuple(self.draw_color), -1)
        return return_frame

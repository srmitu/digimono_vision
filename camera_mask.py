# -*- coding: utf-8 -*-
import cv2
from multiprocessing import Manager, Value, Array, Event
import time
import numpy as np
class digimono_camera_mask(object):

    def __init__(self, draw_color):
        #初期化
        self.draw_color = tuple(draw_color)
        if(np.sum(self.draw_color) < 180):
            self.draw_sub_color = (255,255,255)
        else:
            self.draw_sub_color = (0,0,0)

    def __enter__(self):
        return self
    def __exit__(self, ex_type, ex_value, trace):
        pass

    #マスクを作成し、抽出した数とその中心点を求める
    def mask_detect(self, hsv_frame, contours, point, threshold, permit_area, task, end_flag):
        #毎度更新必要:frame
        #毎度更新される:contours, point, task
        #値変更必要なし(初期に入れるのみ):threshold, point_erea
        pattern = len(threshold)
        task.value = False 
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
        while(task.value == False and end_flag.value == False):
            time.sleep(0.02)
        while(end_flag.value == False):
            hsv = hsv_frame[0]
            #maskの作成(２値化)
            if(pattern == 2):
                mask1 = cv2.inRange(hsv, tuple(threshold[1]), tuple(threshold[0]))
                mask = mask1 
            elif(pattern == 4):
                mask1 = cv2.inRange(hsv, tuple(threshold[1]), tuple(threshold[0]))
                mask2 = cv2.inRange(hsv, tuple(threshold[3]), tuple(threshold[2]))
                mask = mask1 + mask2
            if(pattern == 2 or pattern == 4):
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                #輪郭の抽出
                all_contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                #必要な輪郭のみ抽出する
                for num_all_contours in range(len(all_contours)):
                    if(cv2.contourArea(all_contours[num_all_contours]) > permit_area):
                        contours.append(all_contours[num_all_contours])
                        mu = cv2.moments(all_contours[num_all_contours])
                        x,y = int(mu["m10"]/mu["m00"]), int(mu["m01"]/mu["m00"])
                        point.append([x, y])

                if(len(contours) != len(point)):
                    print("contours", contours, "point", point)
            
            task.value = False
            while(task.value == False and end_flag.value == False):
                time.sleep(0.02)
        print("end_mask_process")

    def draw_contours(self, edit_frame, contours, thickness):
        return_edit_frame = edit_frame.copy()
        for num_contours in range(len(contours)):
            return_edit_frame = cv2.drawContours(edit_frame, contours, num_contours, self.draw_sub_color, thickness)
            return_edit_frame = cv2.drawContours(edit_frame, contours, num_contours, self.draw_color, thickness-1)
        return return_edit_frame
    
    def draw_point(self, frame, point):
        return_frame = frame
        for num_point in range(len(point)):
            return_frame = cv2.circle(frame, tuple(point[num_point]), 5, (self.draw_sub_color), -1)
            return_frame = cv2.circle(frame, tuple(point[num_point]), 4, tuple(self.draw_color), -1)
        return return_frame

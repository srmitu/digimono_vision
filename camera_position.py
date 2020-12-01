import cv2
import numpy as np
from multiprocessing import Process, Value, Array

class digimono_camera_position(object):
    def __init__(self, no, mode, type_shape, shape, color, draw_color):
        #初期化
        #共有設定
        self.no = Value('i', 0)
        self.mode = Value('i', -1)
        self.type_shape = Value('i', -1)
        self.shape = Array('i', 0)
        self.color = Value('i', -1)
        self.draw_color = Array('i', 0)
        self.cal_time_n = Value('i', 0)#0 = False, 1 = True
        self.old_in_shape_n = Value('i', 0) #0 = False, 1 = True
        
        self.no.value = no
        self.mode.value = mode
        self.type_shape.value = type_shape
        self.shape = shape
        self.color.value = color
        self.draw_color = draw_color #tuple化必要

    def __enter__(self):
        pass
    def __exit__(self):
        pass
        #print("exit")

    def position_detect(self, rise_or_false, point, in_shape_position):
        enter_time = 0
        exit_time = 0
        in_shape = 0 #0 = False, 1 = True
        position = point[self.color.value]
        if(position != []):
            if(self.type_shape.value == 0):#四角
                for num_position in range(len(position)):
                    rectangle_x = abs(position[num_position][0]-self.shape[0][0])
                    rectangle_y = abs(position[num_position][1]-self.shape[0][1])
                    if(rectangle_x < self.shape[1][0] and rectangle_y  < self.shape[1][1]):
                        in_shape = 1
                        in_shape_position.append(position[num_position])

            elif(self.type_shape.value == 1):#楕円
                for num_position in range(len(position)):
                    ellipse_x = ((position[num_position][0]-self.shape[0][0]) / self.shape[1][0]) ** 2 
                    ellipse_y = ((position[num_position][1]-self.shape[0][1]) / self.shape[1][1]) ** 2
                    ellipse = ellipse_x + ellipse_y
                    if(ellipse < 1):
                        in_shape = 1
                        in_shape_position.append(position[num_position])

            if((self.old_in_shape_n.value == 0 and in_shape == 1) and ((self.mode.value <= 1 and self.cal_time_n.value == 0) or self.mode.value > 1)):
                rise_or_false[self.no.value] = str("rise")
            elif((self.old_in_shape_n.value == 1 and in_shape == 0) and ((self.mode <= 1 and self.cal_time.value == 0) or self.mode.value > 1)):
                rise_or_false[self.no.value] = str("fall")
            elif(in_shape == 1):
                rise_or_false[self.no.value] = str("in")
            elif(in_shape == 0):
                rise_or_false[self.no.value] = str("out")
            else:
                rise_or_false[self.no.value] = str("none")

    def get_cal_time(self):
        return_cal_time = False
        if(self.cal_time_n.value == 1):
            return_cal_time = True
        return return_cal_time
    def put_cal_time(self, bool_cal_time):
        if(bool_cal_time == False):
            self.cal_time_n.value = 0
        elif(bool_cal_time == True):
            self.cal_time_n.value = 1

    def draw_in_shape_position(self, frame, in_shape_position):
        return_frame = frame
        for num_position in range(len(in_shape_position)):
            return_frame = cv2.circle(frame, tuple(in_shape_position[num_point]), 20, tuple(self.draw_color), -1)
        return return_frame

    def draw_shape(self, frame):
        return_frame = frame
        print(3)
        if(self.type_shape == 0):
            left_up = ((self.shape[0][0]-self.shape[1][0]), (self.shape[0][1]+self.shape[1][1]))
            right_down = ((self.shape[0][0]+self.shape[1][0]), (self.shape[0][1]-self.shape[1][1]))
            return_frame = cv2.rectangle(frame, left_up, right_down, tuple(self.draw_color), 3)
            print(4)
        elif(self.type_shape == 1):
            return_frame = cv2.ellipse(frame, (tuple(self.shape[0]),tuple(self.shape[1] * 2),0), tuple(self.draw_color), 3)
        return return_frame
        


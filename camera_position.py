import cv2
import numpy as np
from multiprocessing import Process, Value, Array
import time

class digimono_camera_position(object):
    def __init__(self, draw_color, type_shape, shape):
        #初期化
        self.draw_color = tuple(draw_color) 
        self.type_shape = type_shape
        self.shape = shape

    def __enter__(self):
        pass
    def __exit__(self):
        pass

    def position_detect(self, point, cal_time,  in_shape_position, task, state, mode, type_shape, shape):
        #毎度更新必要:point, cal_time
        #毎度更新される:in_shape_position, state, task
        #値変更なし:mode, type_shape, shape 
        in_shape = False 
        old_in_shape = False
        task.value = False
        while True:
            while task.value == False:
                time.sleep(0.02)
                pass
            in_shape_point = []
            in_shape = False
            if point:#中身が入っているとTrue, 入っていないとFalse
                if(type_shape == 0):#四角
                    for num in range(len(point)):
                        rectangle_x = abs(point[num][0]-shape[0][0])
                        rectangle_y = abs(point[num][1]-shape[0][1])
                        if(rectangle_x < shape[1][0] and rectangle_y  < shape[1][1]):
                            in_shape = True
                            in_shape_point.append(point[num])

                elif(type_shape == 1):#楕円
                    for num in range(len(point)):
                        ellipse_x = ((point[num][0]-shape[0][0]) / shape[1][0]) ** 2 
                        ellipse_y = ((point[num][1]-shape[0][1]) / shape[1][1]) ** 2
                        ellipse = ellipse_x + ellipse_y
                        if(ellipse < 1):
                            in_shape = True
                            in_shape_point.append(point[num])

                if((old_in_shape == False and in_shape == True) and ((mode <= 1 and cal_time == 0) or mode > 1)):
                    state.value = ord('r')#rise
                elif((old_in_shape == True and in_shape == False) and ((mode <= 1 and cal_time == 0) or mode > 1)):
                    state.value = ord('f') #fall
                elif(in_shape == True):
                    state.value = ord('i') #in
                elif(in_shape == False):
                    state.value = ord('o') #out
                else:
                    state.value = ord('n') #none
            for num in range(len(in_shape_point)):
                in_shape_position.append(in_shape_point.pop(0))
            #print("in_shape_position", in_shape_position)
            task.value = False
    
    def draw_in_shape_position(self, frame, in_shape_position):
        return_frame = frame
        for num_position in range(len(in_shape_position)):
            return_frame = cv2.circle(frame, tuple(in_shape_position[num_position]), 20, tuple(self.draw_color), -1)
        return return_frame

    def draw_shape(self, frame):
        return_frame = frame
        if(self.type_shape == 0):
            left_up = ((self.shape[0][0]-self.shape[1][0]), (self.shape[0][1]+self.shape[1][1]))
            right_down = ((self.shape[0][0]+self.shape[1][0]), (self.shape[0][1]-self.shape[1][1]))
            return_frame = cv2.rectangle(frame, left_up, right_down, tuple(self.draw_color), 3)
        elif(self.type_shape == 1):
            return_frame = cv2.ellipse(frame, (tuple(self.shape[0]),tuple(self.shape[1] * 2),0), tuple(self.draw_color), 3)
        return return_frame
        


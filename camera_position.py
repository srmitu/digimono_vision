import cv2
import numpy as np
from multiprocessing import Process, Value, Array

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

    def position_detect(self, position, cal_time,  in_shape_position, task, state, mode, type_shape, shape):
        #毎度更新必要:point, cal_time
        #毎度更新される:in_shape_position, state, task
        #値変更なし:mode, type_shape, shape 
        in_shape = 0 #0 = False, 1 = True
        old_in_shape = 0
        task.value = 1
        while True:
            while task.value == 1:
                pass
            task.value = 0
            if(position != []):
                if(type_shape == 0):#四角
                    for num in range(len(position)):
                        rectangle_x = abs(position[num][0]-shape[0][0])
                        rectangle_y = abs(position[num][1]-shape[0][1])
                        if(rectangle_x < shape[1][0] and rectangle_y  < shape[1][1]):
                            in_shape = 1
                            in_shape_position.append(position[num])

                elif(type_shape == 1):#楕円
                    for num in range(len(position)):
                        ellipse_x = ((position[num][0]-shape[0][0]) / shape[1][0]) ** 2 
                        ellipse_y = ((position[num][1]-shape[0][1]) / shape[1][1]) ** 2
                        ellipse = ellipse_x + ellipse_y
                        if(ellipse < 1):
                            in_shape = 1
                            in_shape_position.append(position[num])

                if((old_in_shape == 0 and in_shape == 1) and ((mode <= 1 and cal_time == 0) or mode > 1)):
                    state.value = 10 #rise
                elif((old_in_shape == 1 and in_shape == 0) and ((mode <= 1 and cal_time == 0) or mode > 1)):
                    state.value = 11 #fall
                elif(in_shape == 1):
                    state.value = 1 #in
                elif(in_shape == 0):
                    state.value = 0 #out
                else:
                    state.value = 20 #none
            task.value = 1
    
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
        


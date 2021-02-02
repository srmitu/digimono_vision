import cv2
from multiprocessing import Process, Value, Array
import numpy as np
import time
import logging

class digimono_camera_position(object):
    def __init__(self, draw_color, type_shape, shape, mode):
        self.logger = logging.getLogger(__name__)
        #初期化
        self.draw_color = tuple(draw_color) 
        if(np.sum(self.draw_color) < 180):
            self.draw_sub_color = (255,255,255)
        else:
            self.draw_sub_color = (0,0,0)
        self.type_shape = type_shape
        self.shape = shape
        self.mode = mode

    def __enter__(self):
        pass
    def __exit__(self):
        pass

    def position_detect(self, point,  in_shape_position, task, state, type_shape, shape, end_flag):
        #毎度更新必要:point
        #毎度更新される:in_shape_position, state, task
        #値変更なし:type_shape, shape 
        in_shape = False 
        old_in_shape = False
        task.value = False
        while(task.value == False and end_flag.value == False):
            time.sleep(0.02)
        while(end_flag.value == False):
            in_shape_point = []
            in_shape = False
            if point:#中身が入っているとTrue, 入っていないとFalse
                if(type_shape == "rectangle"):#四角
                    for num in range(len(point)):
                        rectangle_x = abs(point[num][0]-shape[0][0])
                        rectangle_y = abs(point[num][1]-shape[0][1])
                        if(rectangle_x < shape[1][0] and rectangle_y  < shape[1][1]):
                            in_shape = True
                            in_shape_point.append(point[num])

                elif(type_shape == "ellipse"):#楕円
                    for num in range(len(point)):
                        ellipse_x = ((point[num][0]-shape[0][0]) / shape[1][0]) ** 2 
                        ellipse_y = ((point[num][1]-shape[0][1]) / shape[1][1]) ** 2
                        ellipse = ellipse_x + ellipse_y
                        if(ellipse < 1):
                            in_shape = True
                            in_shape_point.append(point[num])

                if(old_in_shape == False and in_shape == True):
                    state.value = ord('r')#rise
                elif(old_in_shape == True and in_shape == False):
                    state.value = ord('f') #fall
                elif(in_shape == True):
                    state.value = ord('i') #in
                elif(in_shape == False):
                    state.value = ord('o') #out
                else:
                    state.value = ord('n') #none
            old_in_shape = in_shape
            for num in range(len(in_shape_point)):
                in_shape_position.append(in_shape_point.pop(0))
            task.value = False
            while(task.value == False and end_flag.value == False):
                time.sleep(0.02)
        self.logger.info("end_position_process")
    
    def draw_in_shape_position(self, frame, in_shape_position):
        return_frame = frame
        for num_position in range(len(in_shape_position)):
            return_frame = cv2.circle(frame, tuple(in_shape_position[num_position]), 20, (self.draw_sub_color), -1)
            return_frame = cv2.circle(frame, tuple(in_shape_position[num_position]), 18, tuple(self.draw_color), -1)
        return return_frame

    def draw_shape(self, frame, num):
        return_frame = frame
        if(self.type_shape == "rectangle"):
            left_up = ((self.shape[0][0]-self.shape[1][0]), (self.shape[0][1]-self.shape[1][1]))
            right_down = ((self.shape[0][0]+self.shape[1][0]), (self.shape[0][1]+self.shape[1][1]))
            return_frame = cv2.rectangle(frame, left_up, right_down, (self.draw_sub_color), 3)
            return_frame = cv2.rectangle(frame, left_up, right_down, tuple(self.draw_color), 2)
        elif(self.type_shape == "ellipse"):
            return_frame = cv2.ellipse(frame, (tuple(self.shape[0]), (self.shape[1][0]*2, self.shape[1][1]*2),0), (self.draw_sub_color), 3)
            return_frame = cv2.ellipse(frame, (tuple(self.shape[0]), (self.shape[1][0]*2, self.shape[1][1]*2),0), tuple(self.draw_color), 2)
        name = self.mode + " - " + str(num)
        text_position = ((self.shape[0][0]-self.shape[1][0]), (self.shape[0][1]+self.shape[1][1]+15))
        cv2.putText(return_frame, name, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (self.draw_sub_color), 2)
        cv2.putText(return_frame, name, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, tuple(self.draw_color), 1)
        return return_frame

    def add_draw_shape(self, frame, num, draw_color, type_shape, shape):
        if(np.sum(draw_color) < 180):
            draw_sub_color = (255,255,255)
        else:
            draw_sub_color = (0,0,0)
        return_frame = frame
        if(type_shape == "rectangle"):
            left_up = ((shape[0][0]-shape[1][0]), (shape[0][1]-shape[1][1]))
            right_down = ((shape[0][0]+shape[1][0]), (shape[0][1]+shape[1][1]))
            return_frame = cv2.rectangle(frame, left_up, right_down, tuple(draw_sub_color), 3)
            return_frame = cv2.rectangle(frame, left_up, right_down, tuple(draw_color), 2)
        elif(type_shape == "ellipse"):
            return_frame = cv2.ellipse(frame, (tuple(shape[0]), (shape[1][0]*2, shape[1][1]*2),0), tuple(draw_sub_color), 3)
            return_frame = cv2.ellipse(frame, (tuple(shape[0]), (shape[1][0]*2, shape[1][1]*2),0), tuple(draw_color), 2)
        name = "add - " + str(num)
        text_position = ((shape[0][0]-shape[1][0]), (shape[0][1]+shape[1][1]+15))
        cv2.putText(return_frame, name, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, tuple(draw_sub_color), 2)
        cv2.putText(return_frame, name, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, tuple(draw_color), 1)
        return return_frame
        


import cv2
import numpy as np
import datetime
import time

class digimono_camera_position(object):
    def __init__(self, mode, type_shape, shape, color, draw_color):
        self.mode = mode
        self.type_shape = type_shape
        self.shape = shape
        self.color = color
        self.position = []
        self.draw_color = tuple(draw_color)
        self.in_shape = False
        self.in_shape_position = []
        self.cal_time = False
        self.old_in_shape = False

    def __enter__(self):
        pass
    def __exit__(self):
        pass
        #print("exit")

    def position_detect(self):
        self.in_shape_position = []
        self.in_shape = False
        if(self.position != []):
            if(self.type_shape == 0):#四角
                for num_position in range(len(self.position)):
                    rectangle_x = abs(self.position[num_position][0]-self.shape[0][0])
                    rectangle_y = abs(self.position[num_position][1]-self.shape[0][1])
                    if(rectangle_x < self.shape[1][0] and rectangle_y  < self.shape[1][1]):
                        self.in_shape = True
                        self.in_shape_position.append(self.position[num_position])

            elif(self.type_shape == 1):#楕円
                for num_position in range(len(self.position)):
                    ellipse_x = ((self.position[num_position][0]-self.shape[0][0]) / self.shape[1][0]) ** 2 
                    ellipse_y = ((self.position[num_position][1]-self.shape[0][1]) / self.shape[1][1]) ** 2
                    ellipse = ellipse_x + ellipse_y
                    if(ellipse < 1):
                        self.in_shape = True
                        self.in_shape_position.append(self.position[num_position])

            if((self.old_in_shape == False and self.in_shape == True) and ((self.mode <= 1 and self.cal_time == False) or self.mode > 1)):
                self.enter_time = datetime.datetime.now()
            elif((self.old_in_shape == True and self.in_shape == False) and ((self.mode <= 1 and self.cal_time == False) or self.mode > 1)):
                self.exit_time = datetime.datetime.now()
    def get_in_shape(self):
        return_in_shape = self.in_shape
        return return_in_shape
    def get_enter_time(self):
        return_enter_time = self.enter_time
        return return_enter_time
    def get_exit_time(self):
        return_exit_time = self.exit_time
        return return_exit_time

    def get_cal_time(self):
        return_cal_time = self.cal_time
        return return_cal_time
    def put_cal_time(self, bool_in_cal_time):
        self.cal_time = bool_in_cal_time

    def get_in_shape_position(self):
        return_in_shape_position = self.in_shape_position
        return return_in_shape_position
    def put_position(self, point):
        self.position = point[self.color]
        self.position_detect()

    def draw_position(self, frame):
        return_frame = frame
        for num_position in range(len(self.position)):
            return_frame = cv2.circle(frame, tuple(self.position[num_position]), 5, self.draw_color, -1)
        for num_in_shape_position in range(len(self.in_shape_position)):
            return_frame = cv2.circle(frame, tuple(self.in_shape_position[num_in_shape_position]), 20, self.draw_color, -1)
        return return_frame

    def draw_in_shape_position(self, frame):
        return_frame = frame
        for num_position in range(len(self.in_shape_position)):
            return_frame = cv2.circle(frame, tuple(self.in_shape_position[num_point]), 20, self.draw_color, -1)
        return return_frame

    def draw_shape(self, frame):
        return_frame = frame
        if(self.type_shape == 0):
            left_up = ((self.shape[0][0]-self.shape[1][0]), (self.shape[0][1]+self.shape[1][1]))
            right_down = ((self.shape[0][0]+self.shape[1][0]), (self.shape[0][1]-self.shape[1][1]))
            return_frame = cv2.rectangle(frame, left_up, right_down, self.draw_color, 3)
        elif(self.type_shape == 1):
            return_frame = cv2.ellipse(frame, (tuple(self.shape[0]),tuple(self.shape[1]),0),self.draw_color, 3)
        return return_frame
        


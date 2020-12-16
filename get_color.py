import cv2
import numpy as np
import multiprocessing
from multiprocessing import Manager, Process, Value
import matplotlib.pyplot as plt
import time

class digimono_get_color(object):
    def __init__(self, left, right, up, down):
        print("start_digimono_get_color")
        self.hsv = Manager().list()
        self.hsv.append(0)
        self.color_init()
        self.end_flag = Value('b')
        self.end_flag.value = False
        self.task = Value('b')
        self.task.value = False
        self.left = left
        self.right = right
        self.up = up
        self.down = down

        self.p_color =  Process(target=self.color_detect_p, args=(self.hsv, self.task, self.end_flag, self.h_array, self.s_array, self.v_array))
        self.p_color.daemon = True
        self.p_color.start()

    def color_detect_p(self, hsv, task, end_flag, h, s, v):
        while(task.value == False and end_flag.value == False):
            time.sleep(0.02)
        while(end_flag.value == False):
            array = hsv[0]
            for wide in range(self.right - self.left):
                for vertical in range(self.down - self.up):
                    h[array[wide][vertical][0]] += 1
                    s[array[wide][vertical][1]] += 1
                    v[array[wide][vertical][2]] += 1

            task.value = False
            while(task.value == False and end_flag.value == False):
                time.sleep(0.02)
        print("end_color_detect_process")

    def color_init(self):
        self.h_array = Manager().list()
        self.s_array = Manager().list()
        self.v_array = Manager().list()
        for i in range(180):
            self.h_array.append(0)
        for i in range(256):
            self.s_array.append(0)
            self.v_array.append(0)
        
    def put_hsv(self, hsv):
        self.hsv.append(hsv)
        self.hsv.pop(0)
        while(self.task.value == True):
            time.sleep(0.02)
        self.task.value = True

    def color_detect_end(self):
        self.draw()
        threshold = self.color_detect()
        return threshold


    def kill(self):
        self.end_flag.value = True

    def draw(self):
        line_h = np.array(range(180))
        line_s_v = np.array(range(256))
        fig = plt.figure()
        axH = fig.add_subplot(3,1,1)
        axH.bar(line_h, self.h_array, width=1.0, color='#FF0000', align="center")
        #axH.title("H")
        axS = fig.add_subplot(3,1,2)
        axS.bar(line_s_v, self.s_array, width=1.0, color='#FF0000', align="center")
        #axS.title("S")
        axV = fig.add_subplot(3,1,3)
        axV.bar(line_s_v, self.v_array, width=1.0, color='#FF0000', align="center")
        #axV.title("V")
        print("show")
        
        #fig.tight_layout()
        fig.show()

    def found_ave_num(self, ave, array):
        return_num = 0
        for num in range(len(array)):
            if((ave * (len(array) / 2)) < np.sum(array[0:num])):
                return_num = num
                break
        return return_num

    def found_std_num(self, ave, ave_num, array):
        return_num1 = int(ave_num - len(array)/2)
        return_num2 = int(ave_num + len(array)/2)
        
        if(return_num1 < 0):
            return_num1 = 0
        if(return_num2 > len(array)):
            return_num2 = len(array)
        change = False
        area = ave * len(array) * 0.75
        print("area", area)
        for num in range(ave_num):
            if((len(array) - ave_num) <= 0):
                break
            area_det = np.sum(array[(ave_num - num):(ave_num + num)])
            if(area_det > area):
                return_num1 = ave_num - num
                return_num2 = ave_num + num
                break
             
        return return_num1, return_num2

    def color_detect(self):
        h_a = np.array(self.h_array)
        h_a_f1 = h_a[0:90]
        h_a_f2 = h_a[90:180]
        s_a = np.array(self.s_array)
        v_a = np.array(self.v_array)
        h_a_f1_ave = h_a_f1.mean()
        h_a_f2_ave = h_a_f2.mean()
        h_a_f1_ave_num = self.found_ave_num(h_a_f1_ave, h_a_f1)
        h_a_f2_ave_num = self.found_ave_num(h_a_f2_ave, h_a_f2) + 90
        if((h_a_f1_ave_num > 40 and h_a_f2_ave_num < 140) or (np.sum(h_a_f1) * 0.1 > np.sum(h_a_f2)) or (np.sum(h_a_f2) * 0.1 > np.sum(h_a_f1))):
            h_a_f2_ave_num = 0
            h_a_ave = h_a.mean()
            h_a_ave_num = self.found_ave_num(h_a_ave, h_a)
        s_a_ave = s_a.mean()
        s_a_ave_num = self.found_ave_num(s_a_ave, s_a)
        v_a_ave = v_a.mean()
        v_a_ave_num = self.found_ave_num(v_a_ave, v_a)
        threshold = []
        print(h_a)
        print(s_a)
        print(v_a)
        print("s_a_ave", s_a_ave_num)
        print("v_a_ave", v_a_ave_num)
        s_a_std_num1, s_a_std_num2 = self.found_std_num(s_a_ave, s_a_ave_num, s_a) 
        v_a_std_num1, v_a_std_num2 = self.found_std_num(v_a_ave, v_a_ave_num, v_a) 
        if(h_a_f2_ave_num == 0):
            print("h_a_ave", h_a_ave_num)
            h_a_std_num1, h_a_std_num2 = self.found_std_num(h_a_ave, h_a_ave_num, h_a) 
            threshold = [[h_a_std_num2, s_a_std_num2, v_a_std_num2], [h_a_std_num1, s_a_std_num1, v_a_std_num1]]
        else:
            print("h_a_f1_ave, h_a_f2_ave", h_a_f1_ave_num, h_a_f2_ave_num)
            h_a_f1_std_num1, h_a_f1_std_num2 = self.found_std_num(h_a_f1_ave, h_a_f1_ave_num, h_a_f1) 
            h_a_f2_std_num1, h_a_f2_std_num2 = self.found_std_num(h_a_f2_ave, h_a_f2_ave_num, h_a_f2) 
            threshold = [[h_a_f1_std_num2, s_a_std_num2, v_a_std_num2], [h_a_f1_std_num1, s_a_std_num1, v_a_std_num1]]
            threshold.append([[h_a_f2_std_num2, s_a_std_num2, v_a_std_num2], [h_a_f2_std_num1, s_a_std_num1, v_a_std_num1]])
        
        print("threshold", threshold)
        return threshold
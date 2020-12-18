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
        self.color_init()
        self.end_flag = Value('b')
        self.end_flag.value = False
        self.task = Value('b')
        self.task.value = False
        self.left = left
        self.right = right
        self.up = up
        self.down = down
        self.already = Value('i', 0)
        self.total = Value('i', 0)

        self.p_color =  Process(target=self.color_detect_p, args=(self.hsv, self.task, self.end_flag, self.h_array, self.s_array, self.v_array, self.already, self.total))
        self.p_color.daemon = True
        self.p_color.start()

    def color_detect_p(self, hsv, task, end_flag, h, s, v, already, total):
        while(task.value == False and end_flag.value == False):
            time.sleep(0.02)
        while(end_flag.value == False):
            array = np.array(hsv[0])
            frame_h = array[:,:,0].copy()
            frame_s = array[:,:,1].copy()
            frame_v = array[:,:,2].copy()
            #print("hsv",frame_h, frame_s, frame_v)
  
            for num in range(256):
                s[num] += np.count_nonzero(frame_s == num)
                v[num] += np.count_nonzero(frame_v == num)
                if(num < 180):
                    h[num] += np.count_nonzero(frame_h == num)
            already.value += 1
            print("done " + str(already.value) + "/" + str(total.value), end="\r")
            hsv.pop(0)
            if(len(hsv) <= 0):
                task.value = False
            #elif(already.value == total.value):
                #task.value = False
            else:
                task.value = True
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
        self.total.value += 1
        if(self.task.value == False):
            self.task.value = True

    def wait_task(self):
        if(self.task.value == True):
            return True
        else:
            return False

    def color_detect_end(self):
        print("\n")
        self.total.value = 0
        self.already.value = 0
        self.draw()
        threshold = self.color_detect()
        for num in range(256):
            self.s_array[num] = 0
            self.v_array[num] = 0
            if(num < 180):
                self.h_array[num] = 0
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
        print("h_a_f2", h_a_f2)
        s_a = np.array(self.s_array)
        v_a = np.array(self.v_array)
        h_a_f1_ave = h_a_f1.mean()
        h_a_f2_ave = h_a_f2.mean()
        h_a_f1_ave_num = self.found_ave_num(h_a_f1_ave, h_a_f1)
        h_a_f2_ave_num = self.found_ave_num(h_a_f2_ave, h_a_f2) + 90
        print(h_a_f1_ave_num, h_a_f2_ave_num)
        if((h_a_f1_ave_num > 30 and h_a_f2_ave_num < 150) or (np.sum(h_a_f1) * 0.1 > np.sum(h_a_f2)) or (np.sum(h_a_f2) * 0.1 > np.sum(h_a_f1))):
            h_a_f2_ave_num = 0
            h_a_ave = h_a.mean()
            h_a_ave_num = self.found_ave_num(h_a_ave, h_a)
        s_a_ave = s_a.mean()
        s_a_ave_num = self.found_ave_num(s_a_ave, s_a)
        v_a_ave = v_a.mean()
        v_a_ave_num = self.found_ave_num(v_a_ave, v_a)
        threshold = []
        '''
        print("h", h_a)
        print("s", s_a)
        print("v", v_a)
        '''
        for num in range(256):
            if(num<180):
                print(num, "v",v_a[num], "s",s_a[num], "h", h_a[num])
            else:
                print(num, "v",v_a[num], "s",s_a[num])
        s_a_std_num1, s_a_std_num2 = self.found_std_num(s_a_ave, s_a_ave_num, s_a) 
        v_a_std_num1, v_a_std_num2 = self.found_std_num(v_a_ave, v_a_ave_num, v_a) 
        if(h_a_f2_ave_num == 0):
            h_a_std_num1, h_a_std_num2 = self.found_std_num(h_a_ave, h_a_ave_num, h_a) 
            threshold = [[h_a_std_num2, s_a_std_num2, v_a_std_num2], [h_a_std_num1, s_a_std_num1, v_a_std_num1]]
        else:
            h_a_f1_std_num1, h_a_f1_std_num2 = self.found_std_num(h_a_f1_ave, h_a_f1_ave_num, h_a_f1) 
            h_a_f2_std_num1, h_a_f2_std_num2 = self.found_std_num(h_a_f2_ave, h_a_f2_ave_num, h_a_f2) 
            threshold = [[h_a_f1_std_num2, s_a_std_num2, v_a_std_num2], [h_a_f1_std_num1, s_a_std_num1, v_a_std_num1]]
            threshold.append([[h_a_f2_std_num2, s_a_std_num2, v_a_std_num2], [h_a_f2_std_num1, s_a_std_num1, v_a_std_num1]])
        
        print("threshold", threshold)
        return threshold

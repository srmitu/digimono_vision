import cv2
import numpy as np
import multiprocessing
from multiprocessing import Manager, Process, Value
import matplotlib as mpl
mpl.use('TkAgg')
mpl.rc('font', family='Noto Sans CJK JP')
import matplotlib.pyplot as plt
from scipy.stats import norm
import time
from copy import deepcopy

class digimono_get_color(object):
    def __init__(self, left, right, up, down, num_attempt):
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
        self.area = (right - left) * (down - up) * num_attempt
        self.already = Value('i', 0)
        self.total = Value('i', 0)
        self.h_array = [0] * 180
        self.s_array = [0] * 256
        self.v_array = [0] * 256
        self.old_h_array = [0] * 180
        self.old_s_array = [0] * 256
        self.old_v_array = [0] * 256
        self.p_color =  Process(target=self.color_detect_p, args=(self.hsv, self.task, self.end_flag, self.shared_h_array, self.shared_s_array, self.shared_v_array, self.already, self.total))
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
        self.shared_h_array = Manager().list()
        self.shared_s_array = Manager().list()
        self.shared_v_array = Manager().list()
        for i in range(180):
            self.shared_h_array.append(0)
        for i in range(256):
            self.shared_s_array.append(0)
            self.shared_v_array.append(0)
        
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

    def color_detect_end(self, mode):
        if(mode < -1):
            mode = -1
        elif(mode > 1):
            mode = 1
        else:
            mode = int(mode)
        self.total.value = 0
        self.already.value = 0
        threshold = self.color_detect(mode, True)
        shared_h_array = deepcopy(self.shared_h_array)
        shared_s_array = deepcopy(self.shared_s_array)
        shared_v_array = deepcopy(self.shared_v_array)

        self.p_draw = Process(target=self.draw, args=(self.h_array, self.s_array, self.v_array, shared_h_array, shared_s_array, shared_v_array))
        self.p_draw.daemon = True
        self.p_draw.start()

        for num in range(256):
            self.shared_s_array[num] = 0
            self.shared_v_array[num] = 0
            if(num < 180):
                self.shared_h_array[num] = 0

        return threshold

    def color_undo(self):
        i = 0
        for num in range(256):
            if(num < 180):
                self.h_array[num] ,self.old_h_array[num] = self.old_h_array[num], self.h_array[num]
            self.s_array[num] ,self.old_s_array[num] = self.old_s_array[num], self.s_array[num]
            self.v_array[num] ,self.old_v_array[num] = self.old_v_array[num], self.v_array[num]
        threshold = self.color_detect(0, False)
        return threshold

    def color_change(self, threshold):
        print(threshold)
        self.old_h_array = deepcopy(self.h_array)
        self.old_s_array = deepcopy(self.s_array)
        self.old_v_array = deepcopy(self.v_array)
        line_h = np.array(range(180))
        line_s_v = np.array(range(256))
        if(len(threshold) == 2):
            h_range = (threshold[0][0]-1) - threshold[1][0]
            s_range = (threshold[0][1]-1) - threshold[1][1]
            v_range = (threshold[0][2]-1) - threshold[1][2]
            h_ave = (h_range)/2 + threshold[1][0]
            s_ave = (s_range)/2 + threshold[1][1]
            v_ave = (v_range)/2 + threshold[1][2]
            h_std = (h_ave - threshold[1][0])
            s_std = (s_ave - threshold[1][1])
            v_std = (v_ave - threshold[1][2])
            h_array = norm.pdf(line_h, h_ave, h_std)
            s_array = norm.pdf(line_s_v, s_ave, s_std)
            v_array = norm.pdf(line_s_v, v_ave, v_std)
            self.h_array = self.area * h_array * (0.75 + 0.0)
            self.s_array = self.area * s_array * (0.75 + 0.0)
            self.v_array = self.area * v_array * (0.75 + 0.0)
            for num in range(256):
                if(num < 180):
                    if(threshold[1][0] <= num and num < threshold[0][0]):
                        self.h_array[num] += self.area * 0.75 * (0.317 + 0.0) / h_range
                    else:
                        self.h_array[num] = 0
                if(threshold[1][1] <= num and num < threshold[0][1]):
                    self.s_array[num] += self.area * 0.75 * (0.317 + 0.0) / s_range
                else:
                    self.s_array[num] = 0
                if(threshold[1][2] <= num and num < threshold[0][2]):
                    self.v_array[num] += self.area * 0.75 * (0.317 + 0.0) / v_range
                else:
                    self.v_array[num] = 0
        if(len(threshold) == 4):
            h1_range = (threshold[0][0]-1) - threshold[1][0]
            h2_range = (threshold[2][0]-1) - threshold[3][0]
            s_range = (threshold[0][1]-1) - threshold[1][1]
            v_range = (threshold[0][2]-1) - threshold[1][2]
            h1_ave = (h1_range)/2 + threshold[1][0]
            h2_ave = (h2_range)/2 + (threshold[3][0] - 90)
            s_ave = (s_range)/2 + threshold[1][1]
            v_ave = (v_range)/2 + threshold[1][2]
            h1_std = (h1_ave - threshold[1][0])
            h2_std = (h2_ave - (threshold[3][0] - 90))
            s_std = (s_ave - threshold[1][1])
            v_std = (v_ave - threshold[1][2])
            line_h = np.array(range(90))
            h1_array = norm.pdf(line_h, h1_ave, h1_std)
            h2_array = norm.pdf(line_h, h2_ave, h2_std)
            s_array = norm.pdf(line_s_v, s_ave, s_std)
            v_array = norm.pdf(line_s_v, v_ave, v_std)
            h1_array_det = self.area * h1_array * (0.375 + 0.0)
            h2_array_det = self.area * h2_array * (0.375 + 0.0)
            self.s_array = self.area * s_array * (0.75 + 0.0)
            self.v_array = self.area * v_array * (0.75 + 0.0)
            for num in range(256):
                if(num < (180/2)):
                    if(threshold[1][0] <= num and num < threshold[0][0]):
                        h1_array_det[num] += self.area * 0.375 * (0.317 + 0.0) / h1_range
                    else:
                        h1_array_det[num] = 0
                    if(threshold[3][0] <= num + 90 and num + 90 < threshold[2][0]):
                        h2_array_det[num] += self.area * 0.375 * (0.317 + 0.0) / h2_range
                    else:
                        h2_array_det[num] = 0
                if(threshold[1][1] <= num and num < threshold[0][1]):
                    self.s_array[num] += self.area * 0.75 * (0.317 + 0.0) / s_range
                else:
                    self.s_array[num] = 0
                if(threshold[1][2] <= num and num < threshold[0][2]):
                    self.v_array[num] += self.area * 0.75 * (0.317 + 0.0) / v_range
                else:
                    self.v_array[num] = 0
            self.h_array = np.append(h1_array_det, h2_array_det)

    def kill(self):
        self.end_flag.value = True

    def draw(self, now_h, now_s, now_v, d_h, d_s, d_v):
        line_h = np.array(range(180))
        line_s_v = np.array(range(256))
        fig = plt.figure()
        fig.subplots_adjust(hspace=0.5)
        axH = fig.add_subplot(3,1,1)
        axH.bar(line_h, now_h, width=1.0, color='#FF0000', align="center", zorder=1)
        axH.scatter(line_h, d_h, s=8, zorder=3)
        axH.set_xlabel("H")
        axH.set_ylabel("取得回数")
        axH.grid(True)
        axS = fig.add_subplot(3,1,2)
        axS.bar(line_s_v, now_s, width=1.0, color='#FF0000', align="center", zorder=1)
        axS.scatter(line_s_v, d_s, s=8, zorder=3)
        axS.set_xlabel("S")
        axS.set_ylabel("取得回数")
        axS.grid(True)
        axV = fig.add_subplot(3,1,3)
        axV.bar(line_s_v, now_v, width=1.0, color='#FF0000', align="center", zorder=1)
        axV.scatter(line_s_v, d_v, s=8, zorder=3)
        axV.set_xlabel("V")
        axV.set_ylabel("取得回数")
        axV.grid(True)
        print("show")
        
        plt.show(block=True)

    def found_median_num(self, array):
        return_num = 0
        total = np.sum(array)
        for num in range(len(array)):
            if(total / 2 <= np.sum(array[0:(num+1)])):
                return_num = num
                break
        return return_num

    def found_std_num(self, median_num, array):
        if(np.sum(np.array(array)) == 0):
            return 0, 0
        return_num1 = 0
        return_num2 = len(array)
        if(len(array)  > 90):
            area = self.area * 0.75
        else:
            area = self.area * 0.375
        l = 0
        r = 0
        for num in range(len(array)):
            if(num % 2 == 0):
                l += 1
            else:
                r += 1
            if(median_num - l < 0):
                l -= 1
                r += 1
            elif(median_num + r > len(array)):
                r -= 1
                l += 1
            area_det = np.sum(array[(median_num - l):(median_num + r + 1)])
            if(area_det >= area):
                if not(num ==0):
                    break
        return_num1 = median_num - l
        return_num2 = median_num + r + 1
        return return_num1, return_num2

    def color_detect(self, mode, status):
        old_h_array = [0] * 180
        old_s_array = [0] * 256
        old_v_array = [0] * 256
        shared_h_array = [0] * 180
        shared_s_array = [0] * 256
        shared_v_array = [0] * 256
        if(status == True):
            self.old_h_array = deepcopy(self.h_array)
            self.old_s_array = deepcopy(self.s_array)
            self.old_v_array = deepcopy(self.v_array)
            old_h_array = deepcopy(self.old_h_array)
            old_s_array = deepcopy(self.old_s_array)
            old_v_array = deepcopy(self.old_v_array)
            shared_h_array = deepcopy(self.shared_h_array)
            shared_s_array = deepcopy(self.shared_s_array)
            shared_v_array = deepcopy(self.shared_v_array)
        if(mode == 1):
            print("+")
            for num in range(256):
                if(num < 180):
                    self.h_array[num] = old_h_array[num] + shared_h_array[num]
                self.s_array[num] = old_s_array[num] + shared_s_array[num]
                self.v_array[num] = old_v_array[num] + shared_v_array[num]
        elif(mode == -1):
            print("-")
            for num in range(256):
                if(num < 180):
                    self.h_array[num] = old_h_array[num] - shared_h_array[num]
                    if(self.h_array[num] <= 0):
                        self.h_array[num] = 0
                self.s_array[num] = old_s_array[num] - shared_s_array[num]
                self.v_array[num] = old_v_array[num] - shared_v_array[num]
                if(self.s_array[num] <= 0):
                    self.s_array[num] = 0
                if(self.v_array[num] <= 0):
                    self.v_array[num] = 0
        elif(mode == 0):
            if(status == True):
                self.h_array = deepcopy(self.shared_h_array)
                self.s_array = deepcopy(self.shared_s_array)
                self.v_array = deepcopy(self.shared_v_array)
        h_a = np.array(self.h_array)
        h_a_f1 = h_a[0:90]
        h_a_f2 = h_a[90:180]
        s_a = np.array(self.s_array)
        v_a = np.array(self.v_array)
        h_a_f1_med_num = self.found_median_num(h_a_f1)
        h_a_f2_med_num = self.found_median_num(h_a_f2) + 90
        if((h_a_f1_med_num > 30 and h_a_f2_med_num < 150) or (np.sum(h_a_f1) * 0.1 > np.sum(h_a_f2)) or (np.sum(h_a_f2) * 0.1 > np.sum(h_a_f1))):
            h_a_f2_med_num = 0
            h_a_med_num = self.found_median_num(h_a)
        s_a_med_num = self.found_median_num(s_a)
        v_a_med_num = self.found_median_num(v_a)
        threshold = []
        s_a_std_num1, s_a_std_num2 = self.found_std_num(s_a_med_num, s_a) 
        v_a_std_num1, v_a_std_num2 = self.found_std_num(v_a_med_num, v_a) 
        if(h_a_f2_med_num == 0):
            h_a_std_num1, h_a_std_num2 = self.found_std_num(h_a_med_num, h_a) 
            threshold = [[h_a_std_num2, s_a_std_num2, v_a_std_num2], [h_a_std_num1, s_a_std_num1, v_a_std_num1]]
        else:
            h_a_f1_std_num1, h_a_f1_std_num2 = self.found_std_num(h_a_f1_med_num, h_a_f1) 
            h_a_f2_std_num1, h_a_f2_std_num2 = self.found_std_num(h_a_f2_med_num - 90, h_a_f2)
            threshold = [[h_a_f1_std_num2, s_a_std_num2, v_a_std_num2], [h_a_f1_std_num1, s_a_std_num1, v_a_std_num1]]
            threshold.append([h_a_f2_std_num2 + 90, s_a_std_num2, v_a_std_num2])
            threshold.append([h_a_f2_std_num1 + 90, s_a_std_num1, v_a_std_num1])

        print("threshold", threshold)
        return threshold

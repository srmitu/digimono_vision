import camera_mask
import camera_position
import config_read
import cv2
import numpy
import datetime
import time
import colorsys
from multiprocessing import Process, Value, Array, Manager
class digimono_camera_main(object):
    def  __init__(self):
        #コンフィグファイルの読みi込み
        self.digi_config = config_read.digimono_config_read()
        self.camera_num, self.min_area, self.permit_show_video, self.permit_record, self.threshold, self.color, self.mode, self.type_shape, self.shape, self.num_color, self.num_shape = self.digi_config.config_detect()

    def initialize(self):
        #描画する色(閾値から決定)
        self.draw_color = []
        for i in range(self.num_color):
            threshold_item = self.threshold[i]
            h_ave = (threshold_item[0,0] + threshold_item[1,0]) / 2
            s_ave = threshold_item[0,1]
            v_ave = threshold_item[0,2]
            r,g,b = colorsys.hsv_to_rgb(h_ave/180 , s_ave/255, v_ave/255)
            self.draw_color.append([b*255, g*255, r*255])

        #maskとpositionのクラス
        self.digi_mask_l = []
        self.digi_position_l = []
        for num_list in range(self.num_color):
            self.digi_mask_l.append(camera_mask.digimono_camera_mask(self.draw_color[num_list]))
        for num_list in range(self.num_shape):
            self.digi_position_l.append(camera_position.digimono_camera_position(self.draw_color[self.color[num_list]], self.type_shape[num_list], self.shape[num_list], self.mode[num_list]))

        #初期化
        self.cal_time = False 
        self.display_time = False
        self.dt1=0
        self.dt2=0
        self.shared_contours = []
        self.shared_mask_point = []
        self.shared_position_point = []
        self.shared_mask_task = []
        self.shared_in_shape_position = []
        self.shared_position_task = []
        self.shared_state = []
        self.error_start_time = []
        self.contours = []
        self.point = []
        self.state = []
        self.in_shape_position = []
        for num in range(self.num_color):
            self.shared_contours.append(0)
            self.shared_mask_point.append(0)
            self.shared_mask_task.append(0)
            self.shared_position_point.append(0)
            self.contours.append(0)
            self.point.append(0)
            self.shared_contours[num] = Manager().list()
            self.shared_mask_point[num] = Manager().list()
            self.shared_mask_task[num] = Value('b')
            self.shared_mask_task[num].value = False
            self.shared_position_point[num] = Manager().list()
            self.contours[num] = []
            self.point[num] = []
        for num in range(self.num_shape):
            self.shared_in_shape_position.append(0)
            self.shared_position_task.append(0)
            self.shared_state.append(0)
            self.error_start_time.append(0)
            self.state.append(0)
            self.in_shape_position.append(0)
            self.shared_in_shape_position[num] = Manager().list()
            self.shared_position_task[num] = Value('b')
            self.shared_position_task[num].value = False
            self.shared_state[num] = Value('l', 0)
            self.error_start_time[num] = 0
            self.state[num] = 0 
            self.in_shape_position[num] = []
        #フレームの初期化
        self.raw_frame = 0

    def make_process(self):
        #フレームを取得(初回のみ)
        self.shared_hsv = Manager().list()
        self.shared_hsv.append(self.raw_frame)

        #maskiのプロセスを生成
        for num in range(self.num_color):
            self.p_mask = Process(target=self.digi_mask_l[num].mask_detect, args=(self.shared_hsv, self.shared_contours[num], self.shared_mask_point[num], self.threshold[num], self.min_area, self.shared_mask_task[num]))
            self.p_mask.daemon = True
            self.p_mask.start()
        #positionのプロセスを生成
        for num in range(self.num_shape):
            self.p_position = Process(target=self.digi_position_l[num].position_detect, args=(self.shared_position_point[self.color[num]], self.shared_in_shape_position[num], self.shared_position_task[num], self.shared_state[num], self.type_shape[num], self.shape[num]))
            self.p_position.daemon = True
            self.p_position.start()

    def start_mask_process(self):
        #フレームを取得
        self.shared_hsv.append(cv2.cvtColor(self.raw_frame, cv2.COLOR_BGR2HSV))
        self.shared_hsv.pop(0)
        self.frame = self.raw_frame.copy()
        for num in range(self.num_color):
            self.shared_mask_task[num].value = True

    def start_position_process(self):
        for num in range(self.num_shape):
            self.shared_position_task[num].value = True
    
    def wait_mask_process(self):
        for num in range(self.num_color):
            self.contours[num] = []
            self.point[num] = []
            while self.shared_mask_task[num].value == True:
                time.sleep(0.01)
                pass
            len_shared_contours = len(self.shared_contours[num])
            len_shared_position_point = len(self.shared_position_point[num])
            for num_pop in range(len_shared_position_point):
                self.shared_position_point[num].pop(0)
            for num_pop in range(len_shared_contours):
                self.contours[num].append(self.shared_contours[num].pop(0))
                self.point[num].append(self.shared_mask_point[num].pop(0))
                self.shared_position_point[num].append(self.point[num][num_pop])

    def draw_contours_and_point(self):
        #見つかった輪郭の重心を描く
        for num in range(self.num_color):
            self.digi_mask_l[num].draw_point(self.frame, self.point[num])
            self.digi_mask_l[num].draw_contours(self.frame, self.contours[num], 2)
    
    def wait_position_process(self):
        #positionのサブプロセスが終わるまで待機
        for num in range(self.num_shape):
            while self.shared_position_task[num].value == True:
                time.sleep(0.01)
                pass
            len_shared_in_shape_position = len(self.shared_in_shape_position[num])
            self.in_shape_position[num] = []
            self.state[num] = 0
            for num_pop in range(len_shared_in_shape_position):
                self.in_shape_position[num].append(self.shared_in_shape_position[num].pop(0))
                self.state[num] = self.shared_state[num].value
        for num in range(self.num_shape):
            self.digi_position_l[num].draw_in_shape_position(self.frame, self.in_shape_position[num])


    def check_position_and_shape(self):
        #重心が枠に貼っているか確認
        multiple_block = False
        for num in range(self.num_shape):
            if(self.mode[num] == "START" and self.state[num] == ord('r')):#rise
                if(self.cal_time == False and multiple_block == False):
                    self.cal_time = True
                    self.display_time = True
                    multiple_block = True
                    self.dt1 = datetime.datetime.now()

            elif(self.mode[num] == "END" and self.state[num] == ord('r')):#rise
                if(self.cal_time == True and multiple_block == False):
                    self.cal_time = False
                    multiple_block = True
                    self.dt2 = datetime.datetime.now()
            elif(self.mode[num] == "ERROR"):
                if(self.state[num] == ord('i')):
                    error_time = datetime.datetime.now() - self.error_start_time[num]
                    if(error_time.seconds >= 60):
                        print(num, "ERROR")
                else:
                    self.error_start_time[num] = datetime.datetime.now()
    
            self.frame = self.digi_position_l[num].draw_shape(self.frame)

    def calculate_cycle_time(self):
        #サイクルタイム計算の処理
        if(self.cal_time == False):
            if(cv2.waitKey(5) == 13):#Enter key
                self.display_time = False
        if(self.display_time == True):
            if(self.cal_time == True):
                self.dt2=datetime.datetime.now()
            #print(dt2 - dt1)
            dt=str(self.dt2 - self.dt1)
            cv2.putText(self.frame, dt, (10,480), cv2.FONT_HERSHEY_SIMPLEX, 3, (255,255,255), 3)
    

    


import camera_mask
import camera_position
import camera_capture
import get_color
import config_read
import logger
import user_code
import cv2
import datetime
import time
import colorsys
import glob
import shutil
import os
import csv
from multiprocessing import Process, Value, Array, Manager
class digimono_camera_process(object):
    def  __init__(self):
        self.start_time = datetime.datetime.now().strftime('%Y-%m-%d')
        pass

    def read_config(self):
        #コンフィグファイルの読みi込み
        self.digi_config = config_read.digimono_config_read('config.yml')
        config_list = self.digi_config.config_detect()

        self.camera_num = config_list.pop(0)
        self.min_area = config_list.pop(0)
        self.permit_record_raw = config_list.pop(0)
        self.permit_record_processed = config_list.pop(0)
        self.permit_color_detect = config_list.pop(0)
        self.color_detect_shape = config_list.pop(0)
        self.color_detect_num_attempt = config_list.pop(0)
        self.record_time = config_list.pop(0)
        self.recommend_video = config_list.pop(0)
        self.recommend_processed = config_list.pop(0)
        self.num_recommend_slow = config_list.pop(0)
        self.num_recommend_fast = config_list.pop(0)
        self.threshold = config_list.pop(0)
        self.color = config_list.pop(0)
        self.mode = config_list.pop(0)
        self.type_shape = config_list.pop(0)
        self.shape = config_list.pop(0)
        self.num_color = config_list.pop(0)
        self.num_shape = config_list.pop(0)
        self.permit_show_video = config_list.pop(0)
        self.permit_show_processed = config_list.pop(0)
        self.permit_show_contours = config_list.pop(0)

    def load_class(self):
        #ロガーファイルの作成
        self.log = logger.digimono_logger("cycle")
        self.user = user_code.digimono_user_code()
        

    def initialize(self):
        #描画する色(閾値から決定)
        self.draw_color = []
        for num in range(self.num_color):
            threshold_item = self.threshold[num]
            h_ave = (threshold_item[0][0] + threshold_item[1][0]) / 2
            s_ave = threshold_item[0][1]
            v_ave = threshold_item[0][2]
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
        
        self.end_flag_mask = []
        self.end_flag_position = []
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
            self.end_flag_mask.append(0)
            self.shared_contours.append(0)
            self.shared_mask_point.append(0)
            self.shared_mask_task.append(0)
            self.shared_position_point.append(0)
            self.contours.append(0)
            self.point.append(0)
            self.end_flag_mask[num] = Value('b')
            self.end_flag_mask[num].value = False
            self.shared_contours[num] = Manager().list()
            self.shared_mask_point[num] = Manager().list()
            self.shared_mask_task[num] = Value('b')
            self.shared_mask_task[num].value = False
            self.shared_position_point[num] = Manager().list()
            self.contours[num] = []
            self.point[num] = []

        for num in range(self.num_shape):
            self.end_flag_position.append(0)
            self.shared_in_shape_position.append(0)
            self.shared_position_task.append(0)
            self.shared_state.append(0)
            self.error_start_time.append(0)
            self.state.append(0)
            self.in_shape_position.append(0)
            self.end_flag_position[num] = Value('b')
            self.end_flag_position[num].value = False
            self.shared_in_shape_position[num] = Manager().list()
            self.shared_position_task[num] = Value('b')
            self.shared_position_task[num].value = False
            self.shared_state[num] = Value('l', 0)
            self.error_start_time[num] = 0
            self.state[num] = 0 
            self.in_shape_position[num] = []
        #フレームの初期化
        self.raw_frame = 0
        #GUIと通信用の変数の初期化
        self.cycle_reset = False
        self.end_check = False
        self.reboot_check = False
        self.color_capture = False

    def make_process(self):
        #フレームを取得(初回のみ)
        self.shared_hsv = Manager().list()
        self.shared_hsv.append(self.raw_frame)
        
        #maskのプロセスを生成
        for num in range(self.num_color):
            self.p_mask = Process(target=self.digi_mask_l[num].mask_detect, args=(self.shared_hsv, self.shared_contours[num], self.shared_mask_point[num], self.threshold[num], self.min_area, self.shared_mask_task[num], self.end_flag_mask[num]))
            self.p_mask.daemon = True
            self.p_mask.start()

        #positionのプロセスを生成
        for num in range(self.num_shape):
            self.p_position = Process(target=self.digi_position_l[num].position_detect, args=(self.shared_position_point[self.color[num]], self.shared_in_shape_position[num], self.shared_position_task[num], self.shared_state[num], self.type_shape[num], self.shape[num], self.end_flag_position[num]))
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
            self.contours[num].clear()
            self.point[num].clear()

            while self.shared_mask_task[num].value == True:
                time.sleep(0.01)

            len_shared_position_point = len(self.shared_position_point[num])

            for num_pop in range(len_shared_position_point):
                self.shared_position_point[num].pop(0)

            while(len(self.shared_contours[num]) > 0 and len(self.shared_mask_point[num]) > 0):
                self.contours[num].append(self.shared_contours[num].pop(0))
                self.point[num].append(self.shared_mask_point[num].pop(0))
            for num_pop in range(len(self.point[num])):
                self.shared_position_point[num].append(self.point[num][num_pop])

    def draw_contours_and_point(self):
        #見つかった輪郭の重心を描く
        for num in range(self.num_color):
            self.digi_mask_l[num].draw_point(self.frame, self.point[num])
            if(self.permit_show_contours == True):
                self.digi_mask_l[num].draw_contours(self.frame, self.contours[num], 2)

    def log_write(self):
        self.log.write_cycle()
        self.user.log_write()
    
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
                    self.log.l_start(num)
                    self.dt1 = datetime.datetime.now()
                    self.user.start_rise(num)

            elif(self.mode[num] == "END" and self.state[num] == ord('r')):#rise
                if(self.cal_time == True and multiple_block == False):
                    self.cal_time = False
                    multiple_block = True
                    self.log.l_end(num)
                    self.dt2 = datetime.datetime.now()
                    self.user.end_rise(num, self.dt2 - self.dt1)
            elif(self.mode[num] == "ERROR"):
                #条件に応じてユーザーコードを実行します
                if(self.state[num] == ord('r')):
                    self.user.error_rise(num)
                elif(self.state[num] == ord('i')):
                    self.user.error_in(num)
                elif(self.state[num] == ord('o')):
                    self.user.error_out(num)
                elif(self.state[num] == ord('f')):
                    self.user.error_fall(num)
            elif(self.mode[num] == "RECOGNITION"):
                #条件に応じてユーザーコードを実行します
                if(self.state[num] == ord('r')):
                    self.user.recognition_rise(num)
                elif(self.state[num] == ord('i')):
                    self.user.recognition_in(num)
                elif(self.state[num] == ord('o')):
                    self.user.recognition_out(num)
                elif(self.state[num] == ord('f')):
                    self.user.recognition_fall(num)
    
            self.frame = self.digi_position_l[num].draw_shape(self.frame)

    def calculate_cycle_time(self):
        #サイクルタイム計算の処理
        if(self.cal_time == False):
            if(self.permit_show_processed == True):
                if(self.cycle_reset == True):#Enter key
                    self.display_time = False
        if(self.display_time == True):
            if(self.cal_time == True):
                self.dt2=datetime.datetime.now()
            #print(dt2 - dt1)
            dt=str(self.dt2 - self.dt1)
            cv2.putText(self.frame, dt, (10,480), cv2.FONT_HERSHEY_SIMPLEX, 3, (255,255,255), 3)

    def user_frame(self):
        self.frame = self.user.edit_frame(self.frame)

    def log_end(self):
        self.log.l_finish()
        self.log.log_close()

    def user_end(self):
        self.user.finish_process()

    def clear_mask_process(self):
        for num in range(self.num_color):
            self.end_flag_mask[num].value = True 

    def clear_position_process(self):
        for num in range(self.num_shape):
            self.end_flag_position[num].value = True

    def clear_color_process(self):
        self.digi_color.kill()

    def put_end_check(self, boolean):
        self.end_check(boolean)

    def reboot_finish(self):
        for num in range(self.num_color):
            self.end_flag_mask[num].value = False   
        for num in range(self.num_shape):
            self.end_flag_position[num].value = False   

    def color_detect_start(self, left, right, up, down):
        self.digi_color = get_color.digimono_get_color(left, right, up, down, self.color_detect_num_attempt)

    def color_detect(self, left, right, up, down):
        frame_Box = self.raw_frame[up: down, left: right]
        self.digi_color.put_hsv(cv2.cvtColor(frame_Box, cv2.COLOR_BGR2HSV))

    def color_detect_end(self, mode):
        self.threshold[0] = self.digi_color.color_detect_end(mode)

    def color_undo(self):
        self.threshold[0] = self.digi_color.color_undo()

    def color_change(self, threshold):
        self.threshold[0] = threshold
        self.digi_color.color_change(threshold)

    def wait_task(self):
        return self.digi_color.wait_task()
    def recommend(self):
        self.video_result = []
        self.processed_result = []
        self.get_log_files()
        self.get_result_files()
        if self.recommend_video:
            self.pickup_cycle_video(self.pickup_log_cycle_slow(self.num_recommend_slow))
            self.pickup_cycle_video(self.pickup_log_cycle_slow(self.num_recommend_fast))
            self.pickup_error_recognition_video(self.error_data)
            self.pickup_error_recognition_video(self.recognition_data)
        if self.recommend_processed:
            self.pickup_cycle_processed(self.pickup_log_cycle_slow(self.num_recommend_slow))
            self.pickup_cycle_processed(self.pickup_log_cycle_slow(self.num_recommend_fast))
            self.pickup_error_recognition_processed(self.error_data)
            self.pickup_error_recognition_processed(self.recognition_data)
        self.copy_to_recommend()
   
    #logファイルを解析で使用するためにデータを取得するメソッドです。
    def get_log_files(self):
        path = 'log/' + self.start_time + '/'
        #今回作成したログのみを取り出します。
        list_of_cycle_files = glob.glob(path + 'cycle_*')
        lastest_cycle_file = max(list_of_cycle_files, key=os.path.getctime)
        list_of_error_files = glob.glob(path + 'error_*')
        lastest_error_file = max(list_of_error_files, key=os.path.getctime)
        list_of_recognition_files = glob.glob(path + 'recognition_*')
        lastest_recognition_file = max(list_of_recognition_files, key=os.path.getctime)
        #print(lastest_cycle_file, lastest_error_file, lastest_recognition_file)
        #サイクルタイムに関するログを取得します。
        cycle_file = open((lastest_cycle_file), 'r', encoding="utf-8")
        cycle_reader = csv.reader(cycle_file)
        cycle_data = [row for row in cycle_reader]
        cycle_file.close()
        #エラー枠に関するログを取得します。
        error_file = open((lastest_error_file), 'r', encoding="utf-8")
        error_reader = csv.reader(error_file)
        error_data = [row for row in error_reader]
        error_file.close()
        #認識エリアに関するログを取得します。
        recognition_file = open((lastest_recognition_file), 'r', encoding="utf-8")
        recognition_reader = csv.reader(recognition_file)
        recognition_data = [row for row in recognition_reader]
        recognition_file.close()
        #必要なデータだけ取り出します。
        self.cycle_data = []
        self.error_data = []
        self.recognition_data = []
        if not (len(cycle_data) <= 2):
            self.cycle_data = cycle_data[2:]
        if not (len(error_data) <= 2):
            self.error_data = error_data[2:]
        if not (len(recognition_data) <= 2):
            self.recognition_data = recognition_data[2:]
        #print(self.cycle_data, self.error_data, self.recognition_data)

    #ログをもとにサイクルタイムが遅い順に並び替えて上から必要な数だけ取り出します。
    def pickup_log_cycle_slow(self, how_many):
        sorted_cycle_data = sorted(self.cycle_data, key = lambda x: x[:][4], reverse=True)
        return sorted_cycle_data[0:how_many]

    #ログをもとにサイクルタイムが速い順に並び替えて上から必要な数だけ取り出します。
    def pickup_log_cycle_fast(self, how_many):
        sorted_cycle_data = sorted(self.cycle_data, key = lambda x: x[:][4])
        return sorted_cycle_data[0:how_many]

    #result内の動画ファイルをすべて取得し、作成日時で並べる
    def get_result_files(self):
        video_files = glob.glob("result/**/video_*.mp4")
        self.sorted_video_files = sorted(video_files, key = lambda x: os.path.getctime(x), reverse=True)
        processed_files = glob.glob("result/**/processed_*.mp4")
        self.sorted_processed_files = sorted(processed_files, key = lambda x: os.path.getctime(x), reverse=True)
        result_files = video_files
        result_files.extend(processed_files)
        self.sorted_result_files = sorted(result_files, key = lambda x: os.path.getctime(x), reverse=True)

    #サイクルタイムのdataをもとに必要なもとの動画を取り出す。
    def pickup_cycle_video(self, cycle_data):
        end_ok = False
        if not (len(cycle_data) == 0 and len(self.sorted_video_files) == 0):
            for num_data in range(len(cycle_data)):
                for num_result in range(len(self.sorted_video_files)):
                    if(os.path.getctime(self.sorted_video_files[num_result]) < float(cycle_data[num_data][3])):
                        if not num_result == 0:
                            if((self.sorted_video_files[num_result - 1] in self.video_result) == False):
                                self.video_result.append(self.sorted_video_files[num_result - 1])
                            end_ok = True
                    if(end_ok == True and os.path.getctime(self.sorted_video_files[num_result]) < float(cycle_data[num_data][1])):
                        break
                num_result = len(self.sorted_video_files) - 1
                if(end_ok == False and os.path.getctime(self.sorted_video_files[num_result]) > float(cycle_data[num_data][3])):
                    if((self.sorted_video_files[num_result] in self.video_result) == False):
                        self.video_result.append(self.sorted_video_files[num_result])
                if(os.path.getctime(self.sorted_video_files[num_result]) > float(cycle_data[num_data][1])):
                    if((self.sorted_video_files[num_result] in self.video_result) == False):
                        self.video_result.append(self.sorted_video_files[num_result])
                end_ok = False
        #print(self.video_result)
    #サイクルタイムのdataをもとに必要な加工の動画を取り出す。
    def pickup_cycle_processed(self, cycle_data):
        end_ok = False
        if not (len(cycle_data) == 0 and len(self.sorted_processed_files) == 0):
            for num_data in range(len(cycle_data)):
                for num_result in range(len(self.sorted_processed_files)):
                    if(os.path.getctime(self.sorted_video_files[num_result]) < float(cycle_data[num_data][3])):
                        if not num_result == 0:
                            if((self.sorted_processed_files[num_result - 1] in self.processed_result) == False):
                                self.processed_result.append(self.sorted_processed_files[num_result - 1])
                            end_ok = True
                    if(end_ok == True and os.path.getctime(self.sorted_processed_files[num_result]) < float(cycle_data[num_data][1])):
                        break
                num_result = len(self.sorted_processed_files) - 1
                if(end_ok == False and os.path.getctime(self.sorted_processed_files[num_result]) > float(cycle_data[num_data][3])):
                    if((self.sorted_processed_files[num_result] in self.processed_result) == False):
                        self.processed_result.append(self.sorted_processed_files[num_result])
                if(os.path.getctime(self.sorted_video_files[num_result]) > float(cycle_data[num_data][1])):
                    if((self.sorted_processed_files[num_result] in self.processed_result) == False):
                        self.processed_result.append(self.sorted_processed_files[num_result])
                end_ok = False
        #print(self.video_result)
    #errorや認識のdataをもとに必要なもとの動画を取り出す。
    def pickup_error_recognition_video(self, data):
        end_ok = False
        if not (len(data) == 0 and len(self.sorted_video_files) == 0):
            for num_data in range(len(data)):
                for num_result in range(len(self.sorted_video_files)):
                    if(os.path.getctime(self.sorted_video_files[num_result]) < float(data[num_data][1])):
                        if not num_result == 0:
                            if((self.sorted_video_files[num_result - 1] in self.video_result) == False):
                                self.video_result.append(self.sorted_video_files[num_result - 1])
                            end_ok = True
                            break
                num_result = len(self.sorted_video_files) - 1
                if(end_ok == False and os.path.getctime(self.sorted_video_files[num_result]) > float(data[num_data][1])):
                    if((self.sorted_video_files[num_result] in self.video_result) == False):
                        self.video_result.append(self.sorted_video_files[num_result])
                end_ok = False
        #print(self.video_result)
    #errorや認識のdataをもとに必要な加工の動画を取り出す。
    def pickup_error_recognition_processed(self, data):
        end_ok = False
        if not (len(data) == 0 and len(self.sorted_processed_files) == 0):
            for num_data in range(len(data)):
                for num_result in range(len(self.sorted_processed_files)):
                    if(os.path.getctime(self.sorted_video_files[num_result]) < float(data[num_data][1])):
                        if not num_result == 0:
                            if((self.sorted_processed_files[num_result - 1] in self.processed_result) == False):
                                self.processed_result.append(self.sorted_processed_files[num_result - 1])
                            end_ok = True
                            break
                num_result = len(self.sorted_processed_files) - 1
                if(end_ok == False and os.path.getctime(self.sorted_processed_files[num_result]) > float(data[num_data][1])):
                    if((self.sorted_processed_files[num_result] in self.processed_result) == False):
                        self.processed_result.append(self.sorted_processed_files[num_result])
                end_ok = False
        #print(self.video_result)



    #取り出したものを推薦フォルダ(recommend)にコピーする
    def copy_to_recommend(self):
        #もし日付ディレクトリごとになってほしくない場合はFalseにする。
        bool_div_dir = True
        if not os.path.isdir('recommend/'):
            os.makedirs('recommend/')
        #推薦フォルダの容量が4GB超えていたら古い順に削除します。
        while True:
            list_files = glob.glob("recommend/**/*.mp4")
            list_files.extend(glob.glob("recommend/*.mp4"))
            sorted_list_files = sorted(list_files, key = lambda x: os.path.getctime(x))
            total = 0
            for i in range(len(sorted_list_files)):
                total += int(os.path.getsize(sorted_list_files[i]))
            if(total <= 4*1000*1000*1000):
                break
            else:
                print("remove", sorted_list_files[0])
                os.remove(sorted_list_files[0])
        #推薦フォルダの中にあるフォルダの中身が空の場合自動削除
        files = os.listdir('recommend/')
        directory = [f for f in files if os.path.isdir(os.path.join('recommend', f))]
        for num_dir in range(len(directory)):
            dir_files = os.listdir('recommend/' + str(directory[num_dir]) + '/')
            if([f for f in dir_files if os.path.isfile(os.path.join('recommend/' + str(directory[num_dir]) + '/', f))] == []):
                os.rmdir('recommend/' + str(directory[num_dir]) + '/')
        if not len(self.video_result) == 0:
            copy_video_result = []
            for i in range(len(self.video_result)):
                if(bool_div_dir == False):
                    name = self.video_result[i].replace('result/', '')
                else:
                    name = self.video_result[i]
                    dir_name_sign = self.video_result[i].replace('result/', '')
                    dir_name = 'recommend/' + dir_name_sign[:(dir_name_sign.find('/')+1)]
                    if not os.path.isdir(dir_name):
                        os.makedirs(dir_name)
                copy_video_result.append(str('recommend/' + name[(name.find('/')+1):]))
                shutil.copy2(self.video_result[i], copy_video_result[i])
        if not len(self.processed_result) == 0:
            copy_processed_result = []
            for i in range(len(self.processed_result)):
                if(bool_div_dir == False):
                    name = self.processed_result[i].replace('result/', '')
                else:
                    name = self.processed_result[i]
                    dir_name_sign = self.processed_result[i].replace('result/', '')
                    dir_name = 'recommend/' + dir_name_sign[:(dir_name_sign.find('/')+1)]
                    if not os.path.isdir(dir_name):
                        os.makedirs(dir_name)
                copy_processed_result.append(str('recommend/' + name[name.find('/')+1:]))
                shutil.copy2(self.processed_result[i], copy_processed_result[i])


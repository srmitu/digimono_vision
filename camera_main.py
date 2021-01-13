import camera_frame
import camera_capture
import camera_process
import cv2
from datetime import datetime
import time
import colorsys
import psutil

class digimono_camera_main(object):
    def  __init__(self):
        self.digi_process = camera_process.digimono_camera_process()
        self.digi_process.read_config()
        self.digi_process.load_class()
        self.comm_init()
        if(self.digi_process.permit_color_detect == False):
            self.main_init()
        else:
            self.main_init_color()

    def main_init(self):
        self.key = -1
        #camera_frameの定義
        self.digi_frame = camera_frame.digimono_camera_frame(self.digi_process.camera_num, self.digi_process.permit_show_video, self.digi_process.permit_record_raw)
        #カメラ処理をするための初期化
        self.digi_process.initialize()
        #フレームを取得
        self.digi_process.raw_frame = self.digi_frame.get_frame()
        #カメラ処理をするためのプロセスの生成
        self.digi_process.make_process()
        #録画するためのcamera_captureの定義、プロセスの生成
        if(self.digi_process.permit_record_processed == True):
            if(self.digi_process.permit_record_raw == True):
                permit_delete = False
            else:
                permit_delete = True
            self.digi_record = camera_capture.digimono_camera_capture(self.digi_frame.frame_height, self.digi_frame.frame_width, self.digi_frame.frame_fps, True, permit_delete)
            permit_used_percent, total = self.digi_record.check_percent()
            while(psutil.disk_usage('/').used / total >= permit_used_percent or psutil.disk_usage('/').free / (1024 * 1024 * 1024) <= 2):
                time.sleep(0.2)
        #maskを処理するプロセスを開始する
        self.digi_process.start_mask_process()
        #startしたことを知らせる
        print("----------------start---------------------")

    def main_init_color(self):
        self.key = -1
        #camera_frameの定義
        self.digi_frame = camera_frame.digimono_camera_frame(self.digi_process.camera_num, self.digi_process.permit_show_video, False)
        #カメラ処理をするための初期化
        self.digi_process.initialize()
        self.color_capture = False
        self.color_capture_already = False
        self.old_color_capture = False
        self.old_color_capture_already = False
        self.old_state = False
        self.num_color_detect = 0
        self.digi_process.num_color = 1
        self.digi_process.num_shape = 0
        self.threshold = []
        self.color_undo = False
        self.comm_color_undo = False
        self.color_mode = 0
        self.comm_color_mode = 0
        self.color_threshold = []
        self.comm_color_threshold = []
        self.color_change = False
        shape = self.digi_process.color_detect_shape
        self.left = shape[0][0] - shape[1][0]
        self.up =shape[0][1] - shape[1][1]
        self.right = shape[0][0] + shape[1][0]
        self.down = shape[0][1] + shape[1][1]
        self.digi_process.color_detect_start(self.left, self.right, self.up, self.down)
        print("----------------start_calibration---------------------")
        
    def get_frame_normal(self):
        #maskを処理するプロセスからの終了処理を受け取り、値を更新する
        self.digi_process.wait_mask_process()
        #フレームを取得
        self.digi_process.raw_frame = self.digi_frame.get_frame()
        #positionを処理するプロセスを開始する
        self.digi_process.start_position_process()
        #maskを処理するプロセスを開始する
        self.digi_process.start_mask_process()
        #見つかった輪郭と重心を描く
        self.digi_process.draw_contours_and_point()
        #ログを書き出す
        self.digi_process.log_write()
        #positionを処理するプロセスからの終了処理を受け取り、値を更新する
        self.digi_process.wait_position_process()
        #重心が枠に入っているか確認
        self.digi_process.check_position_and_shape()
        #サイクルタイム計算の処理
        self.digi_process.cycle_reset = self.cycle_reset()
        self.digi_process.calculate_cycle_time()

        #録画
        if(self.digi_process.permit_record_processed == True):
            self.digi_record.ret.value = self.digi_frame.get_ret()
            self.digi_record.put_frame(self.digi_process.frame)
        #結果表示・終了判定
        if(self.digi_process.permit_show_processed == True):
            self.digi_frame.show_edit_frame(self.digi_process.frame)
        self.end_check()
        return self.digi_process.frame

    def get_frame_color(self):
        if(self.color_capture == True):
            #フレームを取得
            self.digi_process.raw_frame = self.digi_frame.get_frame()
            if(self.color_capture_already == True):
                #maskのみリブート
                self.clear_mask_process()
                time.sleep(1)
                self.color_capture_already = False
                self.old_color_capture_already = False
            if(self.old_color_capture == False):
                print("----------------calibration---------------------")
                self.num_color_detect = 0
                self.old_color_capture = True
            if(self.num_color_detect >= (self.digi_process.color_detect_num_attempt / (abs(self.color_mode)+1))):
                if(self.old_state == False):
                    self.old_state = True
                    print("color_record_end")
                if(self.digi_process.wait_task() == False):
                    mode = 0
                    self.color_detect_end(self.color_mode)
                    print("----------------calibration_end---------------------")
                    self.old_state = False
                    self.color_capture = False
                    self.old_color_capture = False
                    self.color_capture_already = True
                    self.color_mode = 0
                    self.comm_color_mode = 0
            else:
                self.color_detect()
                self.num_color_detect += 1
        elif(self.color_undo == True):
            print("----------------undo or redo---------------------")
            if(self.color_capture_already == True):
                #maskのみリブート
                self.clear_mask_process()
                time.sleep(1)
                self.old_color_capture_already = False
            self.digi_process.color_undo()
            self.color_undo = False
            self.color_capture_already = True
        elif(self.color_change == True):
            print("----------------color_change---------------------")
            if(self.color_capture_already == True):
                #maskのみリブート
                self.clear_mask_process()
                time.sleep(1)
                self.old_color_capture_already = False
            self.digi_process.color_change(self.color_threshold)
            self.color_change = False
            self.color_capture_already = True
            
        else:
            self.color_capture = self.color_capture_check()
            self.color_undo = self.color_undo_check()
            self.color_mode = self.color_mode_check()
            self.color_change, self.color_threshold = self.color_threshold_check()
        return_frame = []
        
        if(self.color_capture_already == True):
            if(self.old_color_capture_already == False):
                self.old_color_capture_already = True
                self.digi_process.initialize()
                self.digi_process.raw_frame = self.digi_frame.get_frame()
                self.digi_process.make_process()
                self.digi_process.start_mask_process()
            self.digi_process.wait_mask_process()
            self.digi_process.start_mask_process()
            self.digi_process.raw_frame = self.digi_frame.get_frame()
            self.digi_process.draw_contours_and_point()
            return_frame = self.digi_process.frame
            return_frame = cv2.putText(return_frame, str(len(self.digi_process.point[0])), (500,40), cv2.FONT_HERSHEY_PLAIN, 3, (255,255,255), 3)
            return_frame = cv2.putText(return_frame, str(len(self.digi_process.point[0])), (500,40), cv2.FONT_HERSHEY_PLAIN, 3, (0,0,0), 2)
        if(return_frame == []):
            return_frame = self.digi_frame.get_frame()
        shape = self.digi_process.color_detect_shape
        return_frame = cv2.rectangle(return_frame, tuple([self.left, self.up]), tuple([self.right, self.down]), (255,255,255), 5)
        return_frame = cv2.rectangle(return_frame, tuple([self.left, self.up]), tuple([self.right, self.down]), (0,0,0), 3)
        if(self.color_mode == 1):
            return_frame = cv2.putText(return_frame, "+", (600,40), cv2.FONT_HERSHEY_PLAIN, 3, (255,255,255), 3)
            return_frame = cv2.putText(return_frame, "+", (600,40), cv2.FONT_HERSHEY_PLAIN, 3, (0,0,0), 2)
        elif(self.color_mode == -1):
            return_frame = cv2.putText(return_frame, "-", (600,40), cv2.FONT_HERSHEY_PLAIN, 3, (255,255,255), 3)
            return_frame = cv2.putText(return_frame, "-", (600,40), cv2.FONT_HERSHEY_PLAIN, 3, (0,0,0), 2)
        #枠の中心のHSV値を表示する(目安)
        point_x = int((self.right - self.left)/2 + self.left)
        point_y = int((self.down - self.up)/2 + self.up)
        h,s,v = colorsys.rgb_to_hsv(return_frame[point_y][point_x][2]/255, return_frame[point_y][point_x][1]/255, return_frame[point_y][point_x][0]/255)
        return_frame = cv2.putText(return_frame, str(tuple([int(h*180), int(s*255), int(v*255)])), (400,70), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,0), 2)
        return_frame = cv2.putText(return_frame, str(tuple([int(h*180), int(s*255), int(v*255)])), (400,70), cv2.FONT_HERSHEY_PLAIN, 2, (255,2555,255), 1)
        #色取得中か表示
        if(self.color_capture == True and self.old_state ==False):
            return_frame = cv2.putText(return_frame, "*CAPTURE", (0,30), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,0), 3)
            return_frame = cv2.putText(return_frame, "*CAPTURE", (0,30), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255), 2)

        #結果表示・終了判定
        if(self.digi_process.permit_show_processed == True):
            self.digi_frame.show_edit_frame(return_frame)
            if(self.color_capture == False):
                self.end_check()
        
        return return_frame
            


    def color_detect(self):
        #生データから情報を得る
        self.digi_process.color_detect(self.left, self.right, self.up, self.down)
        
    def color_detect_end(self, mode):
        #結果をプロットする
        self.digi_process.color_detect_end(mode)

    def reboot(self):
        print("----------------reboot---------------------")
        #まずは終了させる
        if(self.digi_process.color_detect == False and self.digi_process.permit_record_processed == True):
            self.digi_record.ret.value = False
        self.clear_process()
        time.sleep(3)
        #再起動（再定義）する
        self.__init__()
        self.digi_process.reboot_finish()

    def get_ret(self):
        return self.digi_frame.get_ret()

    def clear_process(self):
        self.clear_mask_process()
        self.clear_position_process()
        if(self.digi_process.permit_color_detect == False and self.digi_process.permit_record_processed == True):
            self.clear_record_process()
        if(self.digi_process.permit_color_detect == True):
            self.digi_process.clear_color_process()
        self.clear_frame_process()

    def clear_mask_process(self):
        self.digi_process.clear_mask_process()
        
    def clear_position_process(self):
        self.digi_process.clear_position_process()

    def clear_record_process(self):
        self.digi_record.ret.value = False

    def clear_frame_process(self):
        self.digi_frame.kill()
   
    def comm_init(self):
        self.comm_cycle_reset = False
        self.comm_end_check = False
        self.comm_reboot_check = False
        self.comm_color_capture = False

    def cycle_reset(self):
        return_bool = False
        if(self.digi_process.permit_show_processed == True):
            if(self.key == 13): #Enter key
                return_bool = True
        if(self.comm_cycle_reset == True):
            self.comm_cycle_reset = False
            return_bool = True

        return return_bool

    def end_check(self):
        return_bool = False
        if(self.digi_process.permit_show_processed == True):
            return_bool = self.digi_frame.end_check(self.key)
        if(self.comm_end_check == True):
            self.digi_frame.ret.value = False
            self.digi_frame.end_flag.value = True
            self.comm_end_check = False
            return_bool = True
        return return_bool

    def reboot_check(self):
        return_bool = False
        if(self.digi_process.permit_show_processed == True):
            if(self.key == ord('r')):
                self.key = -1
                return_bool= True
                print("reboot request from key")
        
        if(self.comm_reboot_check == True):
            self.comm_reboot_check = False
            return_bool = True
            print("reboot request")
        
        return return_bool

    def color_capture_check(self):
        return_bool = False

        if(self.digi_process.permit_show_processed == True):
            if(self.key == ord('c')):
                return_bool = True
                print("color capture from key")
        if(self.comm_color_capture == True):
            self.comm_color_capture = False
            return_bool = True
            print("color capture")

        return return_bool

    def color_undo_check(self):
        return_bool = False
        if(self.digi_process.permit_show_processed == True):
            if(self.key == ord('u')):
                return_bool = True
                print("undo or redo from key")
        if(self.comm_color_undo == True):
            self.comm_color_undo = False
            return_bool = True
            print("undo or redo")
        return return_bool

    def color_mode_check(self):
        return_mode = self.color_mode
        if(self.digi_process.permit_show_processed == True):
            if(self.key == ord('p')):
                return_mode = 1
                print("mode is + from key")
            elif(self.key == ord('n')):
                return_mode = 0
                print("mode is none from key")
            elif(self.key == ord('m')):
                return_mode = -1
                print("mode is - from key")
        elif(self.comm_color_mode != self.color_mode):
            return_mode = self.comm_color_mode

        return return_mode
        
    def color_threshold_check(self):
        return_threshold = self.color_threshold
        bool_chage = False
        if(self.digi_process.permit_show_processed == True):
            if(self.key == ord('i')):
                print()
                y_or_n_one_threshold = input("しきい値のH(色相)は1種類だけですか?[y/n]: ")
                if(y_or_n_one_threshold == 'y'):
                    error_time = 0
                    try:
                        h_max, h_min = (int(x) for x in input("しきい値のH(色相)の最大、最小を順に入力してください(スペースで区切ってください): ").split())
                        if not ((h_max <= 180 and h_max >= 0) and (h_min <= 180 and h_min >= 0)):
                            print("数字は0〜180の間である必要があります。操作はキャンセルされます。")
                            error_time = 1
                        if(h_max < h_min and error_time == 0):
                            h_max, h_min = h_min, h_max
                    except ValueError:
                        error_time = 1
                        print("無効な数字です。操作はキャンセルされます。")
                    if(error_time == 0):
                        try:
                            s_max, s_min = (int(x) for x in input("しきい値のS(彩度)の最大、最小を順に入力してください(スペースで区切ってください): ").split())
                            if not ((s_max <= 256 and s_max >= 0) and (s_min <= 256 and s_min >= 0)):
                                print("数字は0〜256の間である必要があります。操作はキャンセルされます。")
                                error_time = 1
                            if(s_max < s_min and error_time == 0):
                                s_max, s_min = s_min, s_max
                        except ValueError:
                            error_time = 1
                            print("無効な数字です。操作はキャンセルされます。")
                    if(error_time == 0):
                        try:
                            v_max, v_min = (int(x) for x in input("しきい値のV(明度)の最大、最小を順に入力してください(スペースで区切ってください): ").split())
                            if not ((v_max <= 256 and v_max >= 0) and (v_min <= 256 and v_min >= 0)):
                                print("数字は0〜256の間である必要があります。操作はキャンセルされます。")
                                error_time = 1
                            if(v_max < v_min and error_time == 0):
                                v_max, v_min = v_min, v_max
                        except ValueError:
                            error_time = 1
                            print("無効な数字です。操作はキャンセルされます。")
                    if(error_time == 0):
                        return_threshold = [[h_max, s_max, v_max], [h_min, s_min, v_min]]
                        bool_chage = True
                elif(y_or_n_one_threshold == 'n'):
                    error_time = 0
                    try:
                        h1_max, h1_min = (int(x) for x in input("しきい値のH(色相)の1つめの最大、最小を順に入力してください(スペースで区切ってください、90未満の数字にしてください): ").split())
                        if not ((h1_max <= 90 and h1_max >= 0) and (h1_min <= 90 and h1_min >= 0)):
                            print("数字は0〜90の間である必要があります。操作はキャンセルされます。")
                            error_time = 1
                        if(h1_max < h1_min and error_time == 0):
                            h1_max, h1_min = h1_min, h1_max
                    except ValueError:
                        error_time = 1
                        print("無効な数字です。操作はキャンセルされます。")
                    if(error_time == 0):
                        try:
                            h2_max, h2_min = (int(x) for x in input("しきい値のH(色相)の2つ目の最大、最小を順に入力してください(スペースで区切ってください、90以上の数字にしてください): ").split())
                            if not ((h2_max <= 180 and h2_max >= 90) and (h2_min <= 180 and h2_min >= 90)):
                                print("数字は90~180の間である必要があります。操作はキャンセルされます。")
                                error_time = 1
                            if(h2_max < h2_min and error_time == 0):
                                h2_max, h2_min = h2_min, h2_max
                        except ValueError:
                            error_time = 1
                            print("無効な数字です。操作はキャンセルされます。")
                    if(error_time == 0):
                        try:
                            s_max, s_min = (int(x) for x in input("しきい値のS(彩度)の最大、最小を順に入力してください(スペースで区切ってください): ").split())
                            if not ((s_max <= 256 and s_max >= 0) and (s_min <= 256 and s_min >= 0)):
                                print("数字は0〜256の間である必要があります。操作はキャンセルされます。")
                                error_time = 1
                            if(s_max < s_min and error_time == 0):
                                s_max, s_min = s_min, s_max
                        except ValueError:
                            error_time = 1
                            print("無効な数字です。操作はキャンセルされます。")
                    if(error_time == 0):
                        try:
                            v_max, v_min = (int(x) for x in input("しきい値のV(明度)の最大、最小を順に入力してください(スペースで区切ってください): ").split())
                            if not ((v_max <= 256 and v_max >= 0) and (v_min <= 256 and v_min >= 0)):
                                print("数字は0〜256の間である必要があります。操作はキャンセルされます。")
                                error_time = 1
                            if(v_max < v_min and error_time == 0):
                                v_max, v_min = v_min, v_max
                        except ValueError:
                            error_time = 1
                            print("無効な数字です。操作はキャンセルされます。")
                    if(error_time == 0):
                        return_threshold = [[h1_max, s_max, v_max], [h1_min, s_min, v_min], [h2_max, s_max, v_max], [h2_min, s_min, v_min]]
                        bool_chage = True
                else:
                    print("操作がキャンセルされました。")
        elif(self.comm_color_threshold != self.color_threshold):
            return_threshold = self.comm_color_threshold
            bool_chage = True

        return bool_chage, return_threshold

    #ここからはmain関数にて呼び出されるメソッド

    def get_frame(self):
        #キー入力やGUIからの情報を更新する
        self.key = -1
        if(self.digi_process.permit_show_processed == True):
            self.key = cv2.waitKey(10)
        if(self.reboot_check() == True):
            self.reboot()
        if(self.digi_process.permit_color_detect == False):
            return self.get_frame_normal()
        else:
            return self.get_frame_color()

    #GUIと通信するために呼び出すメソッド
    #Trueにした場合、実行後自動的にFalseになります。
    def put_cycle_reset(self, boolean):
        self.comm_cycle_reset = boolean

    def put_end_check(self, boolean):
        self.comm_end_check = boolean

    def put_reboot_check(self, boolean):
        self.comm_reboot_check = boolean

    def put_comm_color_capture(self, boolean):
        self.comm_color_capture = boolean

    def put_color_undo(self):
        self.comm_color_undo = True

    def put_color_redo(self):
        self.put_color_undo()

    def put_color_mode(self, number):
        if(number > 1):
            color_mode = 1
        elif(number < -1):
            color_mode = -1
        else:
            color_mode = int(number)
        if(color_mode == 1):
            if(self.color_mode == 1):
                self.comm_color_mode = 0
            else:
                self.comm_color_mode = 1
        elif(color_mode == -1):
            if(self.color_mode == -1):
                self.comm_color_mode = 0
            else:
                self.comm_color_mode = -1
        self.comm_color_mode_bool = True

    def put_color_throeshold(self, threshold):
        if(len(threshold) == 2 or len(threshold) == 4):
            self.comm_threshold = threshold
    
    def main_end(self):
        if(self.digi_process.permit_record_processed == True):    
            self.digi_record.ret.value = self.digi_frame.get_ret()
        self.clear_process()
        self.digi_process.log_end()
        self.digi_process.user_end()
        print("----------------end---------------------")

 

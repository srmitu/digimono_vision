import camera_frame
import camera_capture
import camera_process
import cv2
from datetime import datetime
import time

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
    def __del__(self):
        self.main_end()

    def main_init(self):
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
            self.digi_record = camera_capture.digimono_camera_capture(self.digi_frame.frame_height, self.digi_frame.frame_width, self.digi_frame.frame_fps, True)
        #maskを処理するプロセスを開始する
        self.digi_process.start_mask_process()
        #startしたことを知らせる
        print("----------------start---------------------")

    def main_init_color(self):
        #camera_frameの定義
        self.digi_frame = camera_frame.digimono_camera_frame(self.digi_process.camera_num, self.digi_process.permit_show_video, False)
        #カメラ処理をするための初期化
        self.digi_process.initialize()
        self.color_capture = False
        self.color_capture_already = False
        self.old_color_capture = False
        self.old_color_capture_already = False
        self.old_state = False
        self.start_color_detect = 0
        self.digi_process.num_color = 1
        self.digi_process.num_shape = 0
        self.threshold = []
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
            self.digi_frame.end_check()
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
                self.start_color_detect = datetime.now()
                self.old_color_capture = True
            delta = datetime.now() - self.start_color_detect
            if(delta.seconds >= self.digi_process.color_detect_time):
                if(self.old_state == False):
                    self.old_state = True
                    print("color_record_end")
                if(self.digi_process.wait_task() == False):
                    self.color_detect_end()
                    print("----------------calibration_end---------------------")
                    self.old_state = False
                    self.color_capture = False
                    self.old_color_capture = False
                    self.color_capture_already = True
            else:
                self.color_detect()
        else:
            self.color_capture = self.color_capture_check()
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
        if(return_frame == []):
            return_frame = self.digi_frame.get_frame()
        shape = self.digi_process.color_detect_shape
        return_frame = cv2.rectangle(return_frame, tuple([self.left, self.up]), tuple([self.right, self.down]), (255,255,255), 5)
        return_frame = cv2.rectangle(return_frame, tuple([self.left, self.up]), tuple([self.right, self.down]), (0,0,0), 3)
        #結果表示・終了判定
        if(self.digi_process.permit_show_processed == True):
            self.digi_frame.show_edit_frame(return_frame)
            if(self.color_capture == False):
                self.digi_frame.end_check()
        
        return return_frame
            


    def color_detect(self):
        #生データから情報を得る
        self.digi_process.color_detect(self.left, self.right, self.up, self.down)
        
    def color_detect_end(self):
        #結果をプロットする
        self.digi_process.color_detect_end()

    def reboot(self):
        print("----------------reboot---------------------")
        #まずは終了させる
        if(self.digi_process.color_detect == False and self.digi_process.permit_record_processed == True):
            self.digi_record.ret.value = False
        self.clear_process()
        time.sleep(3)
        #再起動（再定義）する
        self.__init__()
        '''
        self.digi_process = camera_process.digimono_camera_process()
        self.digi_process.read_config()
        self.digi_process.load_class()
        self.main_init()
        '''
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
            if(cv2.waitKey(5) == 13): #Enter key
                return_bool = True
        if(self.comm_cycle_reset == True):
            self.comm_cycle_reset = False
            return_bool = True

        return return_bool

    def end_check(self):
        return_bool = False
        if(self.comm_end_check == True):
            self.comm_end_check = False
            return_bool = True
        return return_bool

    def reboot_check(self):
        return_bool = False
        if(self.digi_process.permit_show_processed == True):
            if(cv2.waitKey(5) == ord('r')):
                return_bool= True
                print("reboot request")
        
        if(self.comm_reboot_check == True):
            self.comm_reboot_check = False
            return_bool = True
            print("reboot request")
        
        return return_bool

    def color_capture_check(self):
        return_bool = False

        if(self.digi_process.permit_show_processed == True):
            if(cv2.waitKey(5) == ord('c')):
                return_bool = True
                print("color capture")
        if(self.comm_color_capture == True):
            self.comm_color_capture = False
            return_bool = True
            print("color capture")


        return return_bool

    #ここからはmain関数にて呼び出されるメソッド

    def get_frame(self):
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
    
    def main_end(self):
        self.digi_frame.end_flag = True
        if(self.digi_process.permit_record_processed == True):    
            self.digi_record.ret.value = self.digi_frame.get_ret()
        self.digi_process.log_end()
        print("----------------end---------------------")

 

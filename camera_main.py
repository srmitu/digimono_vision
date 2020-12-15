import camera_frame
import camera_capture
import camera_process
import time

class digimono_camera_main(object):
    def  __init__(self):
        self.digi_process = camera_process.digimono_camera_process()
        self.digi_process.read_config()
        self.digi_process.load_class()
        self.main_init()

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

    #ここからはmain関数にて呼び出されるメソッド

    def main_loop(self):
        if(self.digi_process.reboot_check() == True):
            self.reboot()
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

    def reboot(self):
        print("----------------reboot---------------------")
        #まずは終了させる
        if(self.digi_process.permit_record_processed == True):
            self.digi_record.ret.value = False
        self.clear_process()
        time.sleep(3)
        #再起動（再定義）する
        self.digi_process = camera_process.digimono_camera_process()
        self.digi_process.read_config()
        self.digi_process.load_class()
        self.main_init()
        self.digi_process.reboot_finish()


    def main_end(self):
        self.digi_frame.end_flag = True
        if(self.digi_process.permit_record_processed == True):    
            self.digi_record.ret.value = self.digi_frame.get_ret()
        self.digi_process.log_end()
        print("----------------end---------------------")

    def get_ret(self):
        return self.digi_frame.get_ret()

    def clear_process(self):
        self.clear_mask_process()
        self.clear_position_process()
        if(self.digi_process.permit_record_processed == True):
            self.clear_record_process()
        self.clear_frame_process()

    def clear_mask_process(self):
        self.digi_process.clear_mask_process()
        
    def clear_position_process(self):
        self.digi_process.clear_position_process()

    def clear_record_process(self):
        self.digi_record.ret.value = False

    def clear_frame_process(self):
        self.digi_frame.kill()
   

    


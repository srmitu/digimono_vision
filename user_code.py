import logger
import datetime
import time

class digimono_user_code(object):
    #-------------------ここから下は通常呼び出されます------------------
    def __init__(self):
        #初期化する
        self.log = logger.digimono_logger("add") #ロガーファイルを作成するクラスをインスタンス化
        #ここから下がユーザーコードになります

    #START枠にriseしたときのメソッド
    def start_rise(self, num):
        pass

    #END枠にriseしたときのメソッド
    def end_rise(self, num, cycle_time):
        pass

    #ERROR枠にriseしたときのメソッド
    def error_rise(self, num):
        #例です
        #使用しない場合はpassを入れてください
        print(num, "ERROR")
        self.log.l_error(num)

    #ERROR枠にinしたときのメソッド
    def error_in(self, num):
        pass
    #ERROR枠にoutしたときのメソッド
    def error_out(self, num):
        pass
    #ERROR枠にfallしたときのメソッド
    def error_fall(self, num):
        pass

    #認識枠にriseしたときのメソッド
    def recognition_rise(self, num):
        #例です
        print(num, "RECOGNITION") 
        self.log.l_recognition(num)
    #認識枠にinしたときのメソッド
    def recognition_in(self, num):
        pass
    #認識枠にoutしたときのメソッド
    def recognition_out(self, num):
        pass
    #認識枠にfallしたときのメソッド
    def recognitino_fall(self, num):
        pass
    #ログファイルに書く
    #このメソッドはloggerクラスのメソッドを呼び出すもので
    #もし書き込むデータがあったら書き込むというものです。
    #camera_mainにて毎ループ呼び出すようになっています。
    def log_write(self):
        self.log.write_add()

    #映像を加工できるメソッド
    def edit_frame(self, frame):
        edit_frame = frame
        #ここから

        #ここまで
        return edit_frame
    
    #すべての処理が終了した際に行うものを集めたメソッド
    def finish_process(self):
        self.log.log_close()
        #ここから下がユーザーコードになります

    #-------------------ここから上は通常の処理で呼び出されます------------------
    #--------------注意：ここから下は通常の処理では呼び出されません-------------

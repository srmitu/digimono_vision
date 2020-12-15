import logger

class digimono_user_code(object):
    def __init__(self):
        #初期化する
        self.log = logger.digimono_logger("add") #ロガーファイルを作成するクラスをインスタンス化
        #ここから下がユーザーコードになります
    
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

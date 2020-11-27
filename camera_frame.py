from threading import Thread
import cv2
import time

class digimono_camera_frame(object):
    def __init__(self, camera_num):
        self.frame = cv2.imread('opencv.jpeg')
        #ret: True時はカメラの使用許可    
        self.ret = False
        #resize_vertical, resize_wide: 初期の画面の大きさを定義する
        self.resize_vertical = 300
        self.resize_wide = 400
        
        self.capture = cv2.VideoCapture(camera_num)
        self.thread = Thread(target = self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        

    def update(self):
        while self.capture.isOpened():
            self.ret, self.frame = self.capture.read()
            time.sleep(.01)
        exit(1)

    #毎フレーム読み出さなくてはならないメソッド
    def end_check(self):
        if cv2.waitKey(1) == ord('q'):
            self.capture.release()
            cv2.destoryAllWindows()
            exit(1)

    def show_frame(self):
        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("frame", self.resize_wide, self.resize_vertical)
        cv2.imshow("frame", self.frame)

    def get_frame(self):
        return self.frame

    def get_ret(self):
        return self.ret

    def put_resize(self, vertical, wide):
        self.resize_wide = wide
        self.resize_vertical = vertical

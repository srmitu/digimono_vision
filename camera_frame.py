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
        self.edit_resize_vertical = 800
        self.edit_resize_wide = 1000
        
        self.capture = cv2.VideoCapture(camera_num)
        #遅延抑制
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
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
        if cv2.waitKey(1) == 27:#ESC key
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)

    def show_frame(self):
        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("frame", self.resize_wide, self.resize_vertical)
        cv2.imshow("frame", self.frame)
    def show_edit_frame(self, edit_frame):
        cv2.namedWindow("FrameEdit", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("FrameEdit", self.edit_resize_wide, self.edit_resize_vertical)
        cv2.imshow("FrameEdit",edit_frame)

    def get_frame(self):
        return self.frame

    def get_ret(self):
        return self.ret

    def put_resize(self, vertical, wide):
        self.resize_wide = wide
        self.resize_vertical = vertical
    def put_edit_resize(self, vertical, wide):
        self.edit_resize_wide = wide
        self.edit_resize_vertical = vertical

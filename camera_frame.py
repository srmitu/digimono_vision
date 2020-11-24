from threading import Thread
import cv2
import time

class digimono_camera_frame(object):
    #ret: True時はカメラの使用許可    
    ret = 0
    #frame: 映像を保存. 初期化のため,0が入っている. 実際に使用するときは少し待ってから使用する
    frame = 0
    #resize_vertical, resize_wide: 初期の画面の大きさを定義する
    resize_vertical = 800
    resize_wide = 1000
    def __init__(self, camera_num):
        self.capture = cv2.VideoCapture(camera_num)
        self.thread = Thread(target = self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while self.capture.isOpened():
            self.ret, self.frame = self.capture.read()
            digimono_camera_frame.ret = self.ret
            digimono_camera_frame.frame = self.frame
            time.sleep(.01)
        exit(1)

    #毎フレーム読み出さなくてはならないメソッド
    def end_cheack(self):
        if cv2.waitKey(1) == ord('q'):
            self.capture.release()
            cv2.destoryAllWindows()
            exit(1)

    def show_frame(self):
        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("frame", digimono_camera_frame.resize_wide, digimono_camera_frame.resize_vertical)
        cv2.imshow("frame", self.frame)

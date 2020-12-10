import multiprocessing 
from multiprocessing import Manager, Process, Value
import cv2
import time

class digimono_camera_frame(object):
    def __init__(self, camera_num, permit_show_video):
        self.frame = Manager().list()
        self.frame_height = Value('i', 0)
        self.frame_width = Value('i', 0)
        self.frame_fps = Value('i', 0)
        #resize_vertical, resize_wide: 初期の画面の大きさを定義する
        self.edit_resize_vertical = 800
        self.edit_resize_wide = 1000
        self.request = Value('b')
        self.request.value = False
        self.ret = Value('b')
        self.ret.value = True

        #遅延抑制
        #self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        p_frame = Process(target=self.frame_detect, args=(self.frame, camera_num, self.request, self.ret, permit_show_video))
        p_frame.daemon = True
        p_frame.start()
        
    def frame_detect(self, frame, camera_num, request, ret, show_video):
        capture= cv2.VideoCapture(camera_num)
        self.frame_height.value = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_width.value = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_fps.value = int(capture.get(cv2.CAP_PROP_FPS))
        ret.value = True
        while(ret.value == True):
            ret.value, video = capture.read()
            if(request.value == True):
                frame.append(video)
                request.value = False
            if(show_video == True):
                cv2.namedWindow("video", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("video", 400, 300)
                cv2.imshow("video", video)
		if(cv2.waitKey(10) == 27):#ESC key
                    capture.release()
                    cv2.destroyAllWindows()
                    break
        ret.value = False
        capture.release()
        cv2.destroyAllWindows()

    def show_edit_frame(self, edit_frame):
        cv2.namedWindow("FrameEdit", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("FrameEdit", self.edit_resize_wide, self.edit_resize_vertical)
        cv2.imshow("FrameEdit",edit_frame)

    def get_frame(self):
        if(self.ret.value == False):
            return -1 
        self.request.value = True
        while(self.request.value == True):
            time.sleep(0.01)
        return self.frame.pop(0)

    def get_ret(self):
        return self.ret.value

    def put_edit_resize(self, vertical, wide):
        self.edit_resize_wide = wide
        self.edit_resize_vertical = vertical

    def end_check(self):
        if(cv2.waitKey(1) == 27):#ESC key
            self.ret.value = False
        if(self.ret.value == False):
            cv2.destroyAllWindows()
            return -1

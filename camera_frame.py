import multiprocessing 
from multiprocessing import Manager, Process, Value
import camera_capture
import cv2
import time
from datetime import datetime

class digimono_camera_frame(object):
    def __init__(self, camera_num, permit_show_video, permit_record_raw):
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
        self.end_flag = Value('b') 
        self.end_flag.value = False
        self.record_kill_flag = Value('b')
        self.record_kill_flag.value = False
        self.permit_record_raw = permit_record_raw

        self.p_frame = Process(target=self.frame_detect, args=(self.frame, camera_num, self.request, permit_show_video, self.permit_record_raw))
        if(permit_record_raw == False):
            self.p_frame.daemon = True
        self.p_frame.start()
        
    def frame_detect(self, frame, camera_num, request, show_video, record_raw):
        capture= cv2.VideoCapture(camera_num)
        #遅延抑制
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.frame_height.value = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_width.value = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        #capture.set(cv2.CAP_PROP_FPS, 5)
        self.frame_fps.value = int(capture.get(cv2.CAP_PROP_FPS))
        if(record_raw == True):
            self.digi_record = camera_capture.digimono_camera_capture(self.frame_height, self.frame_width, self.frame_fps, False)
        #ret.value = True
        while(self.ret.value == True and self.end_flag.value == False):
            self.ret.value, video = capture.read()
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
            if(record_raw == True):
                self.digi_record.ret.value = self.ret.value
                self.digi_record.put_frame(video)
                if(self.record_kill_flag.value == True):
                    self.digi_record.ret.value = False

        self.ret.value = False
        if(record_raw == True):
            self.digi_record.ret.value = False
        
        capture.release()
        time.sleep(0.5)
        print("end_frame_process")

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
            self.end_flag.value = True

        if(self.ret == False):
            cv2.destroyAllWindows()
            #return -1

    def kill(self):
        if(self.permit_record_raw == True):
            self.record_kill_flag.value = True
        self.end_flag.value = True
        #time.sleep(1)
        #self.p_frame.terminate()



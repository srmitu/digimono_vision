from multiprocessing import Manager, Process, Value
import cv2
import datetime
import time
import os

class digimono_camera_capture(object):
    def __init__(self, height, wide, fps):
        self.wide = wide.value
        self.height = height.value
        self.fps = fps.value
        self.frame = Manager().list()
        self.ret = Value('b')
        self.task = Value('b')
        p_record = Process(target=self.record, args=(self.frame, self.wide, self.height, self.fps, self.ret, self.task))
        p_record.daemon = True
        p_record.start()

    def record(self, frame, wide, height, fps, ret, task):
        video_format = cv2.VideoWriter_fourcc('m', 'p' ,'4', 'v')
        dt_start = datetime.datetime.now()
        video_path = 'result/' + str(datetime.datetime.today().date()) 
        video_name = video_path + '/' + str(dt_start.strftime('%H:%M:%S')) + '.mp4'
        print(video_path)
        if not os.path.isdir(video_path):
            os.makedirs(video_path)
        #video_pass = 'result/test.mp4' 
        writer = cv2.VideoWriter(video_name, video_format, fps/10, (wide, height))
        print("record start")
        ret.value = True
        while(ret.value == True):
            print('\r' + "record", end="")
            while(task.value == False):
                time.sleep(0.03)
            dt_now = datetime.datetime.now()
            dt = dt_now - dt_start
            if(dt.seconds >= 30):
                writer.release()
                dt_start = dt_now
                video_path = 'result/' + str(datetime.datetime.today().date()) 
                video_name = video_path + '/' + str(dt_start.strftime('%H:%M:%S')) + '.mp4'
                if not os.path.isdir(video_path):
                    os.makedirs(video_path)
                writer = cv2.VideoWriter(video_name, video_format, fps/10, (wide, height))
                print("change")
            writer.write(frame[0])
            if(ret.value == False):
                break
            task.value = False
        writer.release()
        print("record_end")

    def put_frame(self, in_frame):
        self.frame.append(in_frame)
        if(len(self.frame) ==2):
            self.frame.pop(0)

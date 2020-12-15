from multiprocessing import Manager, Process, Value
import cv2
import datetime
import time
import os
class digimono_camera_capture(object):
    def __init__(self, height, wide, fps, bool_processed):
        self.wide = wide.value
        self.height = height.value
        if(bool_processed == True):
            self.fps = fps.value / 10
        else:
            self.fps = fps.value / 6 
        self.bool_processed = bool_processed
        self.frame = Manager().list()
        self.ret = Value('b')
        self.ret.value = True
        self.task = Value('b')
        self.p_record = Process(target=self.record, args=(self.frame, self.task))
        self.p_record.daemon = True
        self.p_record.start()

    def record(self, frame, task):
        video_format = cv2.VideoWriter_fourcc('m', 'p' ,'4', 'v')
        dt_start = datetime.datetime.now()
        video_path = 'result/' + str(datetime.datetime.today().date())
        if(self.bool_processed == True):
            video_type = 'processed_'
        else:
            video_type = 'video_'
        video_name = video_path + '/' + str(video_type) + str(dt_start.strftime('%H:%M:%S')) + '.mp4'

        if not os.path.isdir(video_path):
            os.makedirs(video_path)
        writer = cv2.VideoWriter(video_name, video_format, self.fps, (self.wide, self.height))
        print("record start")
        self.ret.value = True
        print("recording in " + str(video_name))
        while(self.ret.value == True):
            while(task.value == False):
                time.sleep(0.1)
                if(self.ret.value == False):
                    break
            if(self.ret.value == False):
                break
            dt_now = datetime.datetime.now()
            dt = dt_now - dt_start
            if(dt.seconds >= 30):
                print(str(video_name) + "...finish")
                writer.release()
                dt_start = dt_now
                video_path = 'result/' + str(datetime.datetime.today().date()) 
                video_name = video_path + '/' + str(video_type) + str(dt_start.strftime('%H:%M:%S')) + '.mp4'
                if not os.path.isdir(video_path):
                    os.makedirs(video_path)
                writer = cv2.VideoWriter(video_name, video_format, self.fps, (self.wide, self.height))
                print("recording in " + str(video_name))
            put_frame = cv2.putText(frame[0], str(datetime.datetime.now()), (0,10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)
            writer.write(put_frame)
            if(self.ret.value == False):
                break
            task.value = False
        writer.release()
        print("record_end")
        print("end_record_process")

    def put_frame(self, in_frame):
        self.frame.append(in_frame)
        if(len(self.frame) ==2):
            self.frame.pop(0)
        self.task.value = True


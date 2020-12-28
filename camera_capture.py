from multiprocessing import Manager, Process, Value
import cv2
import datetime
import time
import os
import psutil
import shutil

class digimono_camera_capture(object):
    def __init__(self, height, wide, fps, bool_processed, bool_master):
        self.wide = wide.value
        self.height = height.value
        if(bool_processed == True):
            self.fps = fps.value / 10
        else:
            self.fps = fps.value / 6 
        self.bool_processed = bool_processed
        self.bool_master = bool_master
        self.frame = Manager().list()
        self.ret = Value('b')
        self.ret.value = True
        self.task = Value('b')
        self.total = psutil.disk_usage('/').total
        # 設定
        self.used_percent = 0.9
        # マルチスレッド
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

        #容量を確認し、足らなければ、削除する
        if(psutil.disk_usage('/').used / self.total >= self.used_percent or (psutil.disk_usage('/').free / (1024 * 1024 * 1024)) <= 1):
            if(self.bool_master == True):
                if not os.path.isdir('result/'):
                    print("容量不足ですが、resultフォルダがなく、削除するフォルダがありません。手動でその他のファイルを削除する必要があります。")
                    while True:
                        pass
                all_number_dir = False
                while(all_number_dir == False):
                    files = os.listdir('result/')
                    files_dir = [f for f in files if os.path.isdir(os.path.join('result/', f))]
                    try:
                        files_dir_sort = sorted(files_dir, key=lambda x: datetime.date(datetime.datetime.strptime(x, '%Y-%m-%d').year, datetime.datetime.strptime(x, '%Y-%m-%d').month, datetime.datetime.strptime(x, '%Y-%m-%d').day))
                        all_number_dir = True
                    except ValueError:
                        print("resultフォルダに日付フォルダ以外がある場合、エラーとなります。プログラムを終了してから日付フォルダ以外を削除してください")
                        while True:
                            pass
                for num in range(len(files_dir_sort)):
                    if(os.path.isdir('result/' + files_dir_sort[num])):
                        shutil.rmtree('result/' + files_dir_sort[num])
                        print('result/' + files_dir_sort[num] + 'は容量不足のため削除されます。')
                    if(psutil.disk_usage('/').used / self.total < self.used_percent and (psutil.disk_usage('/').free / (1024 * 1024 * 1024)) > 2):
                        break
                if(psutil.disk_usage('/').used / self.total >= self.used_percent or (psutil.disk_usage('/').free / (1024 * 1024 * 1024)) <= 2):
                    print("容量不足ですが、result内に削除するフォルダがないので、resultフォルダが削除されます。")
                    time.sleep(30)
                    shutil.rmtree('result/')
                    print("容量不足ですが、result内に削除するフォルダがないので、resultフォルダが削除されます。")
                    if(psutil.disk_usage('/').used / self.total >= self.used_percent or (psutil.disk_usage('/').free / (1024 * 1024 * 1024)) <= 2):
                        print("容量不足ですが、resultフォルダがなく、削除するフォルダがありません。手動でその他のファイルを削除する必要があります。")
                        while True:
                            pass
            else:
                while(psutil.disk_usage('/').used/ self.total >= self.used_percent or (psutil.disk_usage('/').free/(1024 * 1024 * 1024)) <= 2):
                    time.sleep(0.5)
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
            if(dt.seconds >= 60*60):
                print(str(video_name) + "...finish")
                writer.release()
                dt_start = dt_now
                video_path = 'result/' + str(datetime.datetime.today().date()) 
                video_name = video_path + '/' + str(video_type) + str(dt_start.strftime('%H:%M:%S')) + '.mp4'
                #容量を確認し、足らなければ、削除する
                if(psutil.disk_usage('/').used / self.total >=self.used_percent or (psutil.disk_usage('/').free / (1024 * 1024 * 1024)) <= 1):
                    if(self.bool_master == True):
                        if not os.path.isdir('result/'):
                            print("容量不足ですが、resultフォルダがなく、削除するフォルダがありません。手動でその他のファイルを削除する必要があります。")
                            while True:
                                pass
                        all_number_dir = False
                        while(all_number_dir == False):
                            files = os.listdir('result/')
                            files_dir = [f for f in files if os.path.isdir(os.path.join('result/', f))]
                            try:
                                files_dir_sort = sorted(files_dir, key=lambda x: datetime.date(datetime.datetime.strptime(x, '%Y-%m-%d').year, datetime.datetime.strptime(x, '%Y-%m-%d').month, datetime.datetime.strptime(x, '%Y-%m-%d').day))
                                all_number_dir = True
                            except ValueError:
                                print("resultフォルダに日付フォルダ以外がある場合、エラーとなります。プログラムを終了してから日付フォルダ以外を削除してください")
                                while True:
                                    pass
                        for num in range(len(files_dir_sort)):
                            if(os.path.isdir('result/' + files_dir_sort[num])):
                                shutil.rmtree('result/' + files_dir_sort[num])
                                print('result/' + files_dir_sort[num] + 'は容量不足のため削除されます。')
                            if(psutil.disk_usage('/').used / self.total < self.used_percent and (psutil.disk_usage('/').free / (1024 * 1024 * 1024)) > 2):
                                break
                        if(psutil.disk_usage('/').used / self.total >= self.used_percent or (psutil.disk_usage('/').free / (1024 * 1024 * 1024)) <= 2):
                            shutil.rmtree('result/')
                            print("容量不足ですが、result内に削除するフォルダがないので、resultフォルダが削除されます。")
                            if(psutil.disk_usage('/').used / self.total >= self.used_percent or (psutil.disk_usage('/').free / (1024 * 1024 * 1024)) <= 2):
                                print("容量不足ですが、resultフォルダがなく、削除するフォルダがありません。手動でその他のファイルを削除する必要があります。")
                                while True:
                                    pass
                    else:
                        while(psutil.disk_usage('/').used / self.total >= self.used_percent or (psutil.disk_usage('/').free/(1024 * 1024 * 1024)) <= 2):
                            time.sleep(0.5)
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

    def check_percent(self):
        return self.used_percent, self.total


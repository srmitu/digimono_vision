import csv
import time
import os
import datetime
import logging

class digimono_logger(object):
    def __init__(self, create_type):
        self.logger = logging.getLogger(__name__)
        self.task_start = False
        self.task_end = False
        self.task_error = False
        self.task_recognition = False
        self.time_class_start = datetime.datetime.now()
        self.time_start = 0
        self.time_end = 0
        self.time_error = 0
        self.time_recognition = 0
        self.num_start = 0
        self.num_end = 0
        self.num_error = 0
        self.time_recognition = 0
        self.mode_cycle = False
        self.mode_add = False
        if(create_type == "all" or create_type == "cycle"):
            self.mode_cycle = True
        if(create_type == "all" or create_type == "add"):
            self.mode_add = True
        #csvファイルを開く
        self.logger_path = 'log/' + str(datetime.datetime.today().date())
        self.logger_cycle_name = self.logger_path + '/cycle_' + str(self.time_class_start.strftime('%H:%M:%S')) + '.csv'
        self.logger_error_name = self.logger_path + '/error_' + str(self.time_class_start.strftime('%H:%M:%S')) + '.csv'
        self.logger_recognition_name = self.logger_path + '/recognition_' + str(self.time_class_start.strftime('%H:%M:%S')) + '.csv'
        if not os.path.isdir(self.logger_path):
            os.makedirs(self.logger_path)
        if(self.mode_cycle == True):
            self.logger_cycle_file = open(self.logger_cycle_name, 'w')
            self.logger_cycle = csv.writer(self.logger_cycle_file)
            #列タイトルを記入
            self.write_list = ["開始時間", self.time_class_start.strftime('%H:%M:%S')]
            self.logger_cycle.writerow(self.write_list)
            self.write_list = ["反応したSTART枠の番号", "START枠に入った時間(UNIX)", "反応したEND枠の番号", "END枠に入った時間(UNIX)", "サイクルタイム"]
            self.logger_cycle.writerow(self.write_list)
        if(self.mode_add == True):
            self.logger_error_file = open(self.logger_error_name, 'w')
            self.logger_recognition_file = open(self.logger_recognition_name, 'w')
            self.logger_error = csv.writer(self.logger_error_file)
            self.logger_recognition = csv.writer(self.logger_recognition_file)
            #列タイトルを記入
            self.write_list = ["開始時間", self.time_class_start.strftime('%H:%M:%S')]
            self.logger_error.writerow(self.write_list)
            self.logger_recognition.writerow(self.write_list)
            self.write_list = ["反応したERROR枠の番号", "ERROR枠に入った時間(UNIX)"]
            self.logger_error.writerow(self.write_list)
            self.write_list = ["反応した認識枠の番号", "認識枠に入った時間(UNIX)"]
            self.logger_recognition.writerow(self.write_list)

    def l_start(self, num):
        self.time_start = time.time() #UNIX時間の取得
        self.num_start = num
        self.task_start = True

    def l_end(self, num):
        self.time_end = time.time() #UNIX時間の取得
        self.num_end = num
        self.task_end = True

    def l_error(self, num):
        self.time_error = time.time() #UNIX時間の取得
        self.num_error = num
        self.task_error = True

    def l_recognition(self, num):
        self.time_recognition = time.time()
        self.num_recognition = num
        self.task_recognition = True

    def l_finish(self):
        self.time_end = time.time() #UNIX時間の取得
        self.num_end = -1
        self.task_end = True
        self.write_cycle()

    def write_cycle(self):
        if(self.task_start == True and self.task_end == True and self.mode_cycle == True):
            self.write_list = [self.num_start, self.time_start, self.num_end, self.time_end, self.time_end - self.time_start]
            self.logger_cycle.writerow(self.write_list)
            self.task_start = False
            self.task_end = False

    def write_add(self):
        if(self.task_error == True and self.mode_add == True):
            self.write_list = [self.num_error, self.time_error]
            self.logger_error.writerow(self.write_list)
            self.task_error = False
        if(self.task_recognition == True and self.mode_add == True):
            self.write_list = [self.num_recognition, self.time_recognition]
            self.logger_recognition.writerow(self.write_list)
            self.task_recognition = False

    def log_close(self):
        if(self.mode_cycle == True):
            self.logger_cycle_file.close()
        if(self.mode_add == True):
            self.logger_error_file.close()
            self.logger_recognition_file.close()
        self.logger.info("log_file is closed")

            

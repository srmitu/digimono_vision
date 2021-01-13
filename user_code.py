import logger
import csv
import datetime
import os
import glob
import time
import shutil

class digimono_user_code(object):
    #-------------------ここから下は通常呼び出されます------------------
    def __init__(self):
        #初期化する
        self.log = logger.digimono_logger("add") #ロガーファイルを作成するクラスをインスタンス化
        self.start_time = datetime.datetime.now().strftime('%Y-%m-%d')
        #ここから下がユーザーコードになります

    #START枠にriseしたときのメソッド
    def start_rise(self, num):
        pass

    #END枠にriseしたときのメソッド
    def end_rise(self, num, cycle_time):
        pass

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

    #映像を加工できるメソッド
    def edit_frame(self, frame):
        edit_frame = frame
        #ここから

        #ここまで
        return edit_frame
    
    #すべての処理が終了した際に行うものを集めたメソッド
    def finish_process(self):
        self.log.log_close()
        self.video_result = []
        self.processed_result = []
        #ここから下がユーザーコードになります

    #-------------------ここから上は通常の処理で呼び出されます------------------
    #--------------注意：ここから下は通常の処理では呼び出されません-------------

    #logファイルを解析で使用するためにデータを取得するメソッドです。
    def get_log_files(self):
        path = 'log/' + self.start_time + '/'
        #今回作成したログのみを取り出します。
        list_of_cycle_files = glob.glob(path + 'cycle_*')
        lastest_cycle_file = max(list_of_cycle_files, key=os.path.getctime)
        list_of_error_files = glob.glob(path + 'error_*')
        lastest_error_file = max(list_of_error_files, key=os.path.getctime)
        list_of_recognition_files = glob.glob(path + 'recognition_*')
        lastest_recognition_file = max(list_of_recognition_files, key=os.path.getctime)
        #print(lastest_cycle_file, lastest_error_file, lastest_recognition_file)
        #サイクルタイムに関するログを取得します。
        cycle_file = open((lastest_cycle_file), 'r', encoding="utf-8")
        cycle_reader = csv.reader(cycle_file)
        cycle_data = [row for row in cycle_reader]
        cycle_file.close()
        #エラー枠に関するログを取得します。
        error_file = open((lastest_error_file), 'r', encoding="utf-8")
        error_reader = csv.reader(error_file)
        error_data = [row for row in error_reader]
        error_file.close()
        #認識エリアに関するログを取得します。
        recognition_file = open((lastest_recognition_file), 'r', encoding="utf-8")
        recognition_reader = csv.reader(recognition_file)
        recognition_data = [row for row in recognition_reader]
        recognition_file.close()
        #必要なデータだけ取り出します。
        self.cycle_data = []
        self.error_data = []
        self.recognition_data = []
        if not (len(cycle_data) <= 2):
            self.cycle_data = cycle_data[2:]
        if not (len(error_data) <= 2):
            self.error_data = error_data[2:]
        if not (len(recognition_data) <= 2):
            self.recognition_data = recognition_data[2:]
        #print(self.cycle_data, self.error_data, self.recognition_data)

    #ログをもとにサイクルタイムが遅い順に並び替えて上から必要な数だけ取り出します。
    def pickup_log_cycle_slow(self, how_many):
        sorted_cycle_data = sorted(self.cycle_data, key = lambda x: x[:][4], reverse=True)
        return sorted_cycle_data[0:how_many]

    #ログをもとにサイクルタイムが速い順に並び替えて上から必要な数だけ取り出します。
    def pickup_log_cycle_fast(self, how_many):
        sorted_cycle_data = sorted(self.cycle_data, key = lambda x: x[:][4])
        return sorted_cycle_data[0:how_many]

    #result内の動画ファイルをすべて取得し、作成日時で並べる
    def get_result_files(self):
        video_files = glob.glob("result/**/video_*.mp4")
        self.sorted_video_files = sorted(video_files, key = lambda x: os.path.getctime(x), reverse=True)
        processed_files = glob.glob("result/**/processed_*.mp4")
        self.sorted_processed_files = sorted(processed_files, key = lambda x: os.path.getctime(x), reverse=True)
        result_files = video_files
        result_files.extend(processed_files)
        self.sorted_result_files = sorted(result_files, key = lambda x: os.path.getctime(x), reverse=True)

    #サイクルタイムのdataをもとに必要なもとの動画を取り出す。
    def pickup_cycle_video(self, cycle_data):
        end_ok = False
        if not (len(cycle_data) == 0 and len(self.sorted_video_files) == 0):
            for num_data in range(len(cycle_data)):
                for num_result in range(len(self.sorted_video_files)):
                    if(os.path.getctime(self.sorted_video_files[num_result]) < float(cycle_data[num_data][3])):
                        if not num_result == 0:
                            if((self.sorted_video_files[num_result - 1] in self.video_result) == False):
                                self.video_result.append(self.sorted_video_files[num_result - 1])
                            end_ok = True
                    if(end_ok == True and os.path.getctime(self.sorted_video_files[num_result]) < float(cycle_data[num_data][1])):
                        break
                num_result = len(self.sorted_video_files) - 1
                if(end_ok == False and os.path.getctime(self.sorted_video_files[num_result]) > float(cycle_data[num_data][3])):
                    if((self.sorted_video_files[num_result] in self.video_result) == False):
                        self.video_result.append(self.sorted_video_files[num_result])
                if(os.path.getctime(self.sorted_video_files[num_result]) > float(cycle_data[num_data][1])):
                    if((self.sorted_video_files[num_result] in self.video_result) == False):
                        self.video_result.append(self.sorted_video_files[num_result])
                end_ok = False
        #print(self.video_result)
    #サイクルタイムのdataをもとに必要な加工の動画を取り出す。
    def pickup_cycle_processed(self, cycle_data):
        end_ok = False
        if not (len(cycle_data) == 0 and len(self.sorted_processed_files) == 0):
            for num_data in range(len(cycle_data)):
                for num_result in range(len(self.sorted_processed_files)):
                    if(os.path.getctime(self.sorted_video_files[num_result]) < float(cycle_data[num_data][3])):
                        if not num_result == 0:
                            if((self.sorted_processed_files[num_result - 1] in self.processed_result) == False):
                                self.processed_result.append(self.sorted_processed_files[num_result - 1])
                            end_ok = True
                    if(end_ok == True and os.path.getctime(self.sorted_processed_files[num_result]) < float(cycle_data[num_data][1])):
                        break
                num_result = len(self.sorted_processed_files) - 1
                if(end_ok == False and os.path.getctime(self.sorted_processed_files[num_result]) > float(cycle_data[num_data][3])):
                    if((self.sorted_processed_files[num_result] in self.processed_result) == False):
                        self.processed_result.append(self.sorted_processed_files[num_result])
                if(os.path.getctime(self.sorted_video_files[num_result]) > float(cycle_data[num_data][1])):
                    if((self.sorted_processed_files[num_result] in self.processed_result) == False):
                        self.processed_result.append(self.sorted_processed_files[num_result])
                end_ok = False
        #print(self.video_result)
    #errorや認識のdataをもとに必要なもとの動画を取り出す。
    def pickup_error_recognition_video(self, data):
        end_ok = False
        if not (len(data) == 0 and len(self.sorted_video_files) == 0):
            for num_data in range(len(data)):
                for num_result in range(len(self.sorted_video_files)):
                    if(os.path.getctime(self.sorted_video_files[num_result]) < float(data[num_data][1])):
                        if not num_result == 0:
                            if((self.sorted_video_files[num_result - 1] in self.video_result) == False):
                                self.video_result.append(self.sorted_video_files[num_result - 1])
                            end_ok = True
                            break
                num_result = len(self.sorted_video_files) - 1
                if(end_ok == False and os.path.getctime(self.sorted_video_files[num_result]) > float(data[num_data][1])):
                    if((self.sorted_video_files[num_result] in self.video_result) == False):
                        self.video_result.append(self.sorted_video_files[num_result])
                end_ok = False
        #print(self.video_result)
    #errorや認識のdataをもとに必要な加工の動画を取り出す。
    def pickup_error_recognition_processed(self, data):
        end_ok = False
        if not (len(data) == 0 and len(self.sorted_processed_files) == 0):
            for num_data in range(len(data)):
                for num_result in range(len(self.sorted_processed_files)):
                    if(os.path.getctime(self.sorted_video_files[num_result]) < float(data[num_data][1])):
                        if not num_result == 0:
                            if((self.sorted_processed_files[num_result - 1] in self.processed_result) == False):
                                self.processed_result.append(self.sorted_processed_files[num_result - 1])
                            end_ok = True
                            break
                num_result = len(self.sorted_processed_files) - 1
                if(end_ok == False and os.path.getctime(self.sorted_processed_files[num_result]) > float(data[num_data][1])):
                    if((self.sorted_processed_files[num_result] in self.processed_result) == False):
                        self.processed_result.append(self.sorted_processed_files[num_result])
                end_ok = False
        #print(self.video_result)



    #取り出したものを推薦フォルダ(recommend)にコピーする
    def copy_to_recommend(self):
        #もし日付ディレクトリごとになってほしくない場合はFalseにする。
        bool_div_dir = True
        #推薦フォルダの容量が4GB超えていたら古い順に削除します。
        while True:
            list_files = glob.glob("recommend/**/*.mp4")
            list_files.extend(glob.glob("recommend/*.mp4"))
            sorted_list_files = sorted(list_files, key = lambda x: os.path.getctime(x))
            total = 0
            for i in range(len(sorted_list_files)):
                total += int(os.path.getsize(sorted_list_files[i]))
            if(total <= 4*1000*1000*1000):
                break
            else:
                print("remove", sorted_list_files[0])
                os.remove(sorted_list_files[0])
        #推薦フォルダの中にあるフォルダの中身が空の場合自動削除
        files = os.listdir('recommend/')
        directory = [f for f in files if os.path.isdir(os.path.join('recommend', f))]
        for num_dir in range(len(directory)):
            dir_files = os.listdir('recommend/' + str(directory[num_dir]) + '/')
            if([f for f in dir_files if os.path.isfile(os.path.join('recommend/' + str(directory[num_dir]) + '/', f))] == []):
                os.rmdir('recommend/' + str(directory[num_dir]) + '/')
        if not os.path.isdir('recommend/'):
            os.makedirs('recommend/')
        if not len(self.video_result) == 0:
            copy_video_result = []
            for i in range(len(self.video_result)):
                if(bool_div_dir == False):
                    name = self.video_result[i].replace('result/', '')
                else:
                    name = self.video_result[i]
                    dir_name_sign = self.video_result[i].replace('result/', '')
                    dir_name = 'recommend/' + dir_name_sign[:(dir_name_sign.find('/')+1)]
                    if not os.path.isdir(dir_name):
                        os.makedirs(dir_name)
                copy_video_result.append(str('recommend/' + name[(name.find('/')+1):]))
                shutil.copy2(self.video_result[i], copy_video_result[i])
        if not len(self.processed_result) == 0:
            copy_processed_result = []
            for i in range(len(self.processed_result)):
                if(bool_div_dir == False):
                    name = self.processed_result[i].replace('result/', '')
                else:
                    name = self.processed_result[i]
                    dir_name_sign = self.processed_result[i].replace('result/', '')
                    dir_name = 'recommend/' + dir_name_sign[:(dir_name_sign.find('/')+1)]
                    if not os.path.isdir(dir_name):
                        os.makedirs(dir_name)
                copy_processed_result.append(str('recommend/' + name[name.find('/')+1:]))
                shutil.copy2(self.processed_result[i], copy_processed_result[i])

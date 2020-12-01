import camera_mask
import camera_frame
import camera_position
import cv2
import numpy
import datetime
import time
import colorsys
from multiprocessing import Process, Manager, Value, Array, Pool

#実際の環境によって変更する変数
camera_num = 0
max_mask_process = 2
#設定ファイルを作成するまで必要な変数群
num_color = 3
num_shape = 3

#閾値
threshold = []
threshold.append(numpy.array([[85, 255, 230],[50, 45,35]]))
threshold.append(numpy.array([[140, 255, 255],[100, 100, 100]]))
threshold.append(numpy.array([[15, 255, 255],[0, 100, 100],[180, 255, 255],[160, 100, 100]]))
#枠座標
shape = []
shape.append(numpy.array([[100,100],[50,50]]))
shape.append(numpy.array([[550,100],[50,50]]))
shape.append(numpy.array([[550,300],[100,50]]))
#モード
#0:start area
#1:end area
mode = []
mode.append(0)
mode.append(1)
mode.append(3)
#描画する色(閾値から決定)
draw_color = []
for i in range(num_color):
    threshold_item = threshold[i]
    h_ave = (threshold_item[0,0] + threshold_item[1,0]) / 2
    s_ave = threshold_item[0,1]
    v_ave = threshold_item[0,2]
    r,g,b = colorsys.hsv_to_rgb(h_ave/180 , s_ave/255, v_ave/255)
    draw_color.append([b*255, g*255, r*255])
#使用するクラス
digimono_camera_frame = camera_frame.digimono_camera_frame(camera_num)
digimono_camera_mask_list = []
digimono_camera_position_list = []
for num_list in range(num_color):
    digimono_camera_mask_list.append(camera_mask.digimono_camera_mask(threshold[num_list], draw_color[num_list]))
for num_list in range(num_shape-1):
    digimono_camera_position_list.append(camera_position.digimono_camera_position(num_list, mode[num_list], 0, shape[num_list], num_list, draw_color[num_list]))
num_list = 2
digimono_camera_position_list.append(camera_position.digimono_camera_position(num_list, mode[num_list], 1, shape[num_list], num_list, draw_color[num_list]))
#初期化
cal_time = False
display_time = False
dt1=0
dt2=0
#初期化(共有変数)
shared_contours = []
shared_point = []
shared_in_shape_position_rise_or_fall = []
shared_in_shape_position = []

for num in range(num_color):
    shared_contours.append(0)
    shared_point.append(0)
for num in range(num_shape):
    shared_in_shape_position.append(0)
for num in range(num_color):#共有設定
    shared_contours[num] = Manager().list()
    shared_point[num] = Manager().list()
#フレームを取得(初回のみ)
raw_frame = digimono_camera_frame.get_frame()
#初回のみmaskのプロセスを無限ループ外で実行
mask_process_list = []
#mask_process = Pool(max_mask_process)
for num_process in range(num_color):
    #mask_process.apply_async(digimono_camera_mask_list[num_process].mask_detect, args=(shared_array))
    mask_process = Process(target=digimono_camera_mask_list[num_process].mask_detect, args=(raw_frame, shared_contours[num_process], shared_point[num_process]))
    mask_process.start()
    mask_process_list.append(mask_process)
while True:
    frame = digimono_camera_frame.get_frame().copy()

    #maskのサブプロセスが終わるまで待機(初回は無限ループ外で実行されているのを待つ)
    for mask_process in mask_process_list:
        #mask_process.close()
        dt5 = datetime.datetime.now()
        mask_process.join()
        #print(datetime.datetime.now() - dt5)
    contours = shared_contours.copy()
    point = shared_point.copy()

    #フレームを取得
    raw_frame = digimono_camera_frame.get_frame()
    dt4 = datetime.datetime.now()

    #maskに関する共有する変数を再定義(初期化)
    for num in range(num_color):#共有設定
        shared_contours[num] = Manager().list()
        shared_point[num] = Manager().list()

    #maskのサブプロセスを実行
    mask_process_list = []
    #mask_process = Pool(max_mask_process)
    for num_process in range(num_color):
        #mask_process.apply_async(digimono_camera_mask_list[num_process].mask_detect, args=(shared_array))
        mask_process = Process(target=digimono_camera_mask_list[num_process].mask_detect, args=(raw_frame, shared_contours[num_process], shared_point[num_process]))
        mask_process.start()
        mask_process_list.append(mask_process)
    print("make_mask_process", datetime.datetime.now() - dt4)
    dt4 = datetime.datetime.now()
    #positionに関する共有する変数を再定義(初期化)
    shared_in_shape_position_rise_or_fall = []
    shared_in_shape_position_rise_or_fall = Manager().dict()
    #shared_in_shape_position = []
    shared_point = point.copy()
    for num in range(num_shape):
       shared_in_shape_position[num] = Manager().list()

    #positionのサブプロセスを実行
    position_process_list = []
    for num_process in range(num_shape):
        shape_process = Process(target=digimono_camera_position_list[num_process].position_detect, args=(shared_in_shape_position_rise_or_fall, shared_point, shared_in_shape_position[num_process]))
        shape_process.start()
        position_process_list.append(shape_process)
     
    print("position_mask_process", datetime.datetime.now() - dt4)
    #shapeのサブプロセスが終わるまで待機
    for shape_process in position_process_list:
        #shape_process.close()
        dt5 = datetime.datetime.now()
        shape_process.join()
        print("shape",datetime.datetime.now() - dt5)
    in_shape_point = shared_in_shape_position[num_process]
    in_shape_position_rise_or_fall = shared_in_shape_position_rise_or_fall
    dt4 = datetime.datetime.now()
    #重心が枠に貼っているか確認
    num_mode = 0
    for num_list in digimono_camera_position_list:
        if(num_mode == 0 and in_shape_position_rise_or_fall[num_mode] == str("rise")):
            if(cal_time == False):
                cal_time = True
                display_time = True
                num_list.put_cal_time(True)
                dt1 = datetime.datetime.now()

        elif(num_mode == 1 and in_shape_position_rise_or_fall[num_mode] == str("rise")):
            if(cal_time == True):
                cal_time = False
                num_list.put_cal_time(True)
                dt2 = datetime.datetime.now()
        num_mode += 1
        frame = num_list.draw_shape(frame)
    
    if(cal_time==False):
        if(cv2.waitKey(5) == 13):
            display_time=False
        for num_list in digimono_camera_position_list:
            num_list.put_cal_time(False)
    if(display_time==True):
        if(cal_time==True):
            dt2=datetime.datetime.now()
        #print(dt2 - dt1)
        dt=str(dt2-dt1)
        cv2.putText(frame, dt, (10,480), cv2.FONT_HERSHEY_SIMPLEX, 3, (255,255,255), 3)
    print("juusin", datetime.datetime.now() - dt4)
    # 結果表示
    digimono_camera_frame.show_frame()
    digimono_camera_frame.show_edit_frame(frame)
    '''
    num_screen = 0
    for num_list in digimono_camera_mask_list:
        num_list.show_cutout(num_screen)
        num_screen += 1
    '''
    digimono_camera_frame.end_check()

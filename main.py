import camera_mask
import camera_frame
import camera_position
import cv2
import numpy
import datetime
import time
import colorsys
from multiprocessing import Process, Value, Array, Manager

#実際の環境によって変更する変数
camera_num = 0
max_mask_process = 3
permit_show_video = True
#設定ファイルを作成するまで必要な変数群
num_color = 3
num_shape = 3

#閾値
threshold = []
threshold.append(numpy.array([[85, 255, 230],[50, 45,35]]))
threshold.append(numpy.array([[140, 255, 255],[100, 100, 100]]))
threshold.append(numpy.array([[15, 255, 255],[0, 100, 100],[180, 255, 255],[160, 100, 100]]))
#枠の形 0なら四角、1なら楕円
type_shape = []
type_shape.append(0)
type_shape.append(0)
type_shape.append(1)
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
mode.append(2)
#positionのプロセスで判定する色の番号
color = []
color.append(0)
color.append(1)
color.append(2)
#判定する最小の面積
min_area = 500
#描画する色(閾値から決定)
draw_color = []
for i in range(num_color):
    threshold_item = threshold[i]
    h_ave = (threshold_item[0,0] + threshold_item[1,0]) / 2
    s_ave = threshold_item[0,1]
    v_ave = threshold_item[0,2]
    r,g,b = colorsys.hsv_to_rgb(h_ave/180 , s_ave/255, v_ave/255)
    draw_color.append([b*255, g*255, r*255])
#プロセスから取り出した値を格納する変数を定義
contours = []
point = []
for i in range(num_color):
    contours.append(0)
    point.append(0)
    contours[i] = []
    point[i] = []
state = []
in_shape_position = []
for i in range(num_shape):
    state.append(0)
    in_shape_position.append(0)
    state[i] = 0 
    in_shape_position[i] = []
#使用するクラス
digi_frame = camera_frame.digimono_camera_frame(camera_num, permit_show_video)
digi_mask_l = []
digi_position_l = []
for num_list in range(num_color):
    digi_mask_l.append(camera_mask.digimono_camera_mask(draw_color[num_list]))
for num_list in range(num_shape):
    digi_position_l.append(camera_position.digimono_camera_position(draw_color[num_list], type_shape[num_list], shape[num_list]))
#初期化
cal_time = False 
display_time = False
dt1=0
dt2=0
shared_contours = []
shared_mask_point = []
shared_position_point = []
shared_mask_task = []
shared_in_shape_position = []
shared_position_task = []
shared_state = []
error_start_time = []
for num in range(num_color):
    shared_contours.append(0)
    shared_mask_point.append(0)
    shared_mask_task.append(0)
    shared_position_point.append(0)
    shared_contours[num] = Manager().list()
    shared_mask_point[num] = Manager().list()
    shared_mask_task[num] = Value('b')
    shared_position_point[num] = Manager().list()
for num in range(num_shape):
    shared_in_shape_position.append(0)
    shared_position_task.append(0)
    shared_state.append(0)
    error_start_time.append(0)
    shared_in_shape_position[num] = Manager().list()
    shared_position_task[num] = Value('b')
    shared_state[num] = Value('l', 0)
    error_start_time[num] = 0

#フレームを取得(初回のみ)
raw_frame = digi_frame.get_frame()
shared_hsv = Manager().list()
shared_hsv.append(raw_frame)

#maskのプロセスを生成
p_mask_l = []
for num in range(num_color):
    p_mask = Process(target=digi_mask_l[num].mask_detect, args=(shared_hsv, shared_contours[num], shared_mask_point[num], threshold[num], min_area, shared_mask_task[num]))
    p_mask.daemon = True
    p_mask.start()
    p_mask_l.append(p_mask)
#positionのプロセスを生成
p_position_l = []
for num in range(num_shape):
    p_position = Process(target=digi_position_l[num].position_detect, args=(shared_position_point[color[num]], shared_in_shape_position[num], shared_position_task[num], shared_state[num], type_shape[num], shape[num]))
    p_position.daemon = True
    p_position.start()
    p_position_l.append(p_position)

#子プロセスの無限ループ内の処理を開始させる
for num in range(num_color):
    shared_mask_task[num].value = False
for num in range(num_shape):
    shared_position_task[num].value = False
print("start")
#無限ループ
while(digi_frame.get_ret() == True):
    #frame = raw_frame.copy()
    #maskのサブプロセスが終わるまで待機(初回は無限ループ外で実行されているのを待つ)
    for num in range(num_color):
        contours[num] = []
        point[num] = []
        while shared_mask_task[num].value == True:
            time.sleep(0.01)
            pass
        len_shared_contours = len(shared_contours[num])
        len_shared_position_point = len(shared_position_point[num])
        for num_pop in range(len_shared_position_point):
            shared_position_point[num].pop(0)
        for num_pop in range(len_shared_contours):
            contours[num].append(shared_contours[num].pop(0))
            point[num].append(shared_mask_point[num].pop(0))
            shared_position_point[num].append(point[num][num_pop])
    #フレームを取得
    raw_frame = digi_frame.get_frame()
    shared_hsv.append(cv2.cvtColor(raw_frame, cv2.COLOR_BGR2HSV))
    shared_hsv.pop(0)
    frame = raw_frame.copy()
    #positionのプロセスに処理を開始させる
    for num in range(num_shape):
        shared_position_task[num].value = True
    #maskのプロセスに処理を開始させる
    for num in range(num_color):
        shared_mask_task[num].value = True
    #見つかった輪郭の重心を描く
    for num in range(num_color):
        digi_mask_l[num].draw_point(frame, point[num])
        digi_mask_l[num].draw_contours(frame, contours[num], 2)

    #shapeのサブプロセスが終わるまで待機
    for num in range(num_shape):
        while shared_position_task[num].value == True:
            time.sleep(0.01)
            pass
        len_shared_in_shape_position = len(shared_in_shape_position[num])
        in_shape_position[num] = []
        state[num] = 0
        for num_pop in range(len_shared_in_shape_position):
            in_shape_position[num].append(shared_in_shape_position[num].pop(0))
            state[num] = shared_state[num].value
    for num in range(num_shape):
        digi_position_l[num].draw_in_shape_position(frame, in_shape_position[num])
    #重心が枠に貼っているか確認
    for num in range(num_shape):
        if(mode[num] == 0 and state[num] == ord('r')):#rise
            if(cal_time == False):
                cal_time = True
                display_time = True
                dt1 = datetime.datetime.now()

        elif(mode[num] == 1 and state[num] == ord('r')):#rise
            if(cal_time == True):
                cal_time = False
                dt2 = datetime.datetime.now()
        elif(mode[num] == 2):
            if(state[num] == ord('i')):
                error_time = datetime.datetime.now()-error_start_time[num]
                if(error_time.seconds >= 60):
                    print(num, "ERROR")
            else:
                error_start_time[num] = datetime.datetime.now()

        frame = digi_position_l[num].draw_shape(frame)
    #サイクルタイム計算の処理
    if(cal_time == False):
        if(cv2.waitKey(5) == 13):#Enter key
            display_time = False
    if(display_time == True):
        if(cal_time == True):
            dt2=datetime.datetime.now()
        #print(dt2 - dt1)
        dt=str(dt2-dt1)
        cv2.putText(frame, dt, (10,480), cv2.FONT_HERSHEY_SIMPLEX, 3, (255,255,255), 3)
    # 結果表示
    digi_frame.show_edit_frame(frame)

    digi_frame.end_check()


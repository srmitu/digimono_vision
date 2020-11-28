import camera
import camera_frame
import camera_position
import cv2
import numpy
import datetime
import time
import colorsys

#実際の環境によって変更する変数
camera_num = 0

#閾値
threshold = []
threshold.append(numpy.array([[85, 255, 230],[50, 45,35]]))
threshold.append(numpy.array([[145, 180, 170],[95, 45,35]]))

#枠座標
shape = []
shape.append(numpy.array([[100,100],[50,50]]))
shape.append(numpy.array([[550,100],[50,50]]))

#モード
mode = []
mode.append(0)
mode.append(1)

draw_color = []
for i in range(2):
    threshold_item = threshold[i]
    h_ave = (threshold_item[0,0] + threshold_item[1,0]) / 2
    s_ave = (threshold_item[0,1] + threshold_item[1,1]) / 2
    v_ave = (threshold_item[0,2] + threshold_item[1,2]) / 2
    r,g,b = colorsys.hsv_to_rgb(h_ave/180 , s_ave/255, v_ave/255)
    draw_color.append([b*255, g*255, r*255])
        
#使用するクラス
digimono_camera_frame = camera_frame.digimono_camera_frame(camera_num)
digimono_camera_list = []
digimono_camera_position_list = []
for num_list in range(2):
    digimono_camera_list.append(camera.digimono_camera(threshold[num_list], draw_color[num_list]))
for num_list in range(2):
    digimono_camera_position_list.append(camera_position.digimono_camera_position(mode[num_list], 0, shape[num_list], 0, draw_color[0]))
cal_time = False
display_time = False
dt1=0
dt2=0
print("start")
#フレームを取得
raw_frame = digimono_camera_frame.get_frame()
while True:
    frame = raw_frame.copy()
    for num_list in digimono_camera_list:
        while True:
            if(num_list.get_task() == 1):
                break
    cutout = []
    point = []
    for num_list in digimono_camera_list:
        cutout.append(num_list.get_cutout())
        frame = num_list.draw_contours(frame)
        point.append(num_list.get_point())
    #フレームを取得
    raw_frame = digimono_camera_frame.get_frame()
    for num_list in digimono_camera_list:
        num_list.put_frame(raw_frame)
    num_mode = 0
    for num_list in digimono_camera_position_list:
        num_list.put_position(point)
        frame = num_list.draw_position(frame)
        if(num_mode == 0 and num_list.get_in_shape() == True):
            if(cal_time == False):
                cal_time = True
                display_time = True
                num_list.put_cal_time(True)
                dt1 = num_list.get_enter_time()

        elif(num_mode == 1 and num_list.get_in_shape() == True):
            if(cal_time == True):
                cal_time = False
                num_list.put_cal_time(True)
                dt2 = num_list.get_enter_time()
        num_mode += 1
        frame = num_list.draw_shape(frame)
    
    for num_point in range(len(point[1])):
        cv2.circle(frame, tuple(point[1][num_point]), 2, tuple(draw_color[1]), 4)
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
    # 結果表示
    digimono_camera_frame.show_frame()
    cv2.namedWindow("FrameEdit", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("FrameEdit", 1000,800)
    cv2.imshow("FrameEdit",frame)
    num_screen = 0
    for num_list in digimono_camera_list:
        num_list.show_cutout(num_screen)
        num_screen += 1
    digimono_camera_frame.end_check()

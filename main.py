import camera
import camera_frame
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
for num_list in range(2):
    digimono_camera_list.append(camera.digimono_camera(threshold[num_list]))

cal_time = 0
display_time = 0
dt1=0
dt2=0
print("start")
#安定状態になるための待ち時間
#time.sleep(2)
while True:
    #フレームを取得
    raw_frame = digimono_camera_frame.get_frame()
    frame = raw_frame.copy()
    for num_list in digimono_camera_list:
        num_list.put_frame(raw_frame)
    #digimono_camera_list[1].put_frame(raw_frame)
    for num_list in digimono_camera_list:
        while True:
            if(num_list.get_task() == 1):
                break
    cutout = []
    contours = []
    point = []
    for num_list in digimono_camera_list:
        cutout.append(num_list.get_cutout())
        contours.append(num_list.get_contours())
        point.append(num_list.get_point())
        num_list.put_task(0)
    cv2.rectangle(frame, (50,50), (150,150), (250,0,0), 3)
    cv2.rectangle(frame, (500,50), (600,150), (250,0,0), 3)
    for num_color in range(2):
        for num_contours in range(len(contours[num_color])):
            frame = cv2.drawContours(frame,contours[num_color],num_contours,(draw_color[num_color][0],draw_color[num_color][1],draw_color[num_color][2]),3)
        
            #start
            if(point[num_color][num_contours][0]<150 and point[num_color][num_contours][0]>50  and point[num_color][num_contours][1]<150 and point[num_color][num_contours][1]>50):
                cv2.circle(frame, (point[num_color][num_contours][0],point[num_color][num_contours][1]), 2, (0,0,250),20)
                if(cal_time==0):
                    cal_time=1
                    display_time=1
                    dt1=datetime.datetime.now()
            #end
            elif(point[num_color][num_contours][0]<600 and point[num_color][num_contours][0]>500  and point[num_color][num_contours][1]<150 and point[num_color][num_contours][1]>50):
                cv2.circle(frame, (point[num_color][num_contours][0],point[num_color][num_contours][1]), 2, (0,0,250),20)
                if(cal_time==1):
                    cal_time=0
            else:
        
                cv2.circle(frame, (point[num_color][num_contours][0],point[num_color][num_contours][1]), 2, (draw_color[num_color][0], draw_color[num_color][1], draw_color[num_color][2]),4)
        
        
    if(cal_time==0 and cv2.waitKey(1) == 13):
        display_time=0
    if(display_time==1):
        if(cal_time==1):
            dt2=datetime.datetime.now()
        #print(dt2 - dt1)
        dt=str(dt2-dt1)
        cv2.putText(frame, dt, (10,480), cv2.FONT_HERSHEY_SIMPLEX, 3, (255,255,255), 3)
    # 結果表示
    digimono_camera_frame.show_frame()
    cv2.namedWindow("FrameEdit", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("FrameEdit", 1000,800)
    cv2.imshow("FrameEdit",frame)
    cv2.namedWindow("Cutout", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Cutout", 1000,800)
    cv2.imshow("Cutout",cutout[0])
    cv2.namedWindow("Cutout2", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Cutout2", 1000,800)
    cv2.imshow("Cutout2",cutout[1])

    digimono_camera_frame.end_check()

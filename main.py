import camera
import camera_frame
import cv2
import numpy
import datetime
import time

#実際の環境によって変更する変数
camera_num = 0

#使用するクラス
digimono_camera = camera.digimono_camera()
digimono_camera_frame = camera_frame.digimono_camera_frame(camera_num)

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
    #生のカメラデータは早めに出力する
    digimono_camera_frame.show_frame()
    digimono_camera.in_frame(raw_frame)
    #緑検出
    threshold = numpy.array([[85, 255, 230],[50, 45,35]])
    digimono_camera.in_threshold(threshold)
    while True:
        if(digimono_camera.get_task() == 1):
            break
    cutout = digimono_camera.get_cutout()
    contours = digimono_camera.get_contours()
    point = digimono_camera.get_point()
    digimono_camera.in_task(0)
    cv2.rectangle(frame, (50,50), (150,150), (250,0,0), 3)
    cv2.rectangle(frame, (500,50), (600,150), (250,0,0), 3)
    for i in range(len(contours)):
        frame = cv2.drawContours(frame,contours,i,(0,150,0),3)
        
        #start
        if(point[i][0]<150 and point[i][0]>50  and point[i][1]<150 and point[i][1]>50):
            cv2.circle(frame, (point[i][0],point[i][1]), 2, (0,0,250),20)
            if(cal_time==0):
                cal_time=1
                display_time=1
                dt1=datetime.datetime.now()
        #end
        elif(point[i][0]<600 and point[i][0]>500  and point[i][1]<150 and point[i][1]>50):
            cv2.circle(frame, (point[i][0],point[i][1]), 2, (0,0,250),20)
            if(cal_time==1):
                cal_time=0
        else:
        
            cv2.circle(frame, (point[i][0],point[i][1]), 2, (0,250,0),4)
        
        
    if(cal_time==0 and cv2.waitKey(1) == 13):
        display_time=0
    if(display_time==1):
        if(cal_time==1):
            dt2=datetime.datetime.now()
        #print(dt2 - dt1)
        dt=str(dt2-dt1)
        cv2.putText(frame, dt, (10,480), cv2.FONT_HERSHEY_SIMPLEX, 3, (255,255,255), 3)
    # 結果表示
    cv2.namedWindow("FrameEdit", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("FrameEdit", 1000,800)
    cv2.imshow("FrameEdit",frame)
    cv2.namedWindow("Cutout", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Cutout", 1000,800)
    cv2.imshow("Cutout",cutout)

    digimono_camera_frame.end_check()

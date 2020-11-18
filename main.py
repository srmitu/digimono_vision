import camera
import cv2
import numpy
import datetime

with camera.digimono_camera() as digimono_camera:
    cal_time = 0
    display_time = 0
    dt1=0
    dt2=0
    cap = cv2.VideoCapture(0)
    while(cap.isOpened()):
        #フレームを取得
        ret, frame = cap.read()
        #緑検出
        threshold = numpy.array([[85, 255, 230],[50, 45,35]])
        mask,contours,point = digimono_camera.mask_detect(frame, threshold)
        #print(point)
        cv2.rectangle(frame, (50,50), (150,150), (250,0,0), 3)
        cv2.rectangle(frame, (500,50), (600,150), (250,0,0), 3)
        for i in range(len(contours)):
            mask = cv2.drawContours(mask,contours,i,(0,150,0),3)
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
        cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Frame", 1000,800)
        cv2.imshow("Frame", frame)
        cv2.namedWindow("Mask", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Mask", 1000,800)
        cv2.imshow("Mask",mask)


        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

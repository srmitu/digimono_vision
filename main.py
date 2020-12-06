import camera_frame
import camera_main

#camera_mainの定義、コンフィグファイルの読み込み
digi_main = camera_main.digimono_camera_main()
#camera_frameの定義
digi_frame = camera_frame.digimono_camera_frame(digi_main.camera_num, digi_main.permit_show_video)
#カメラ処理をするための初期化
digi_main.initialize()
#フレームを取得
digi_main.raw_frame = digi_frame.get_frame()
#カメラ処理をするためのプロセスの生成
digi_main.make_process()
#maskを処理するプロセスを開始する
digi_main.start_mask_process()

print("start")
#無限ループ
while(digi_frame.get_ret() == True):
    #maskを処理するプロセスからの終了処理を受け取り、値を更新する
    digi_main.wait_mask_process()
    #フレームを取得
    digi_main.raw_frame = digi_frame.get_frame()
    #positionを処理するプロセスを開始する
    digi_main.start_position_process()
    #maskを処理するプロセスを開始する
    digi_main.start_mask_process()
    #見つかった輪郭と重心を描く
    digi_main.draw_contours_and_point()
    #positionを処理するプロセスからの終了処理を受け取り、値を更新する
    digi_main.wait_position_process()
    #重心が枠に貼っているか確認
    digi_main.check_position_and_shape()
    #サイクルタイム計算の処理
    digi_main.calculate_cycle_time()
    #結果表示
    digi_frame.show_edit_frame(digi_main.frame)
    #終了判定
    digi_frame.end_check()

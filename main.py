# -*- coding: utf-8 -*-
import camera_main
#camera_mainの定義,コンフィグファイルの読み込み,無限ループに入る前に済ませておく処理をすべて行う
digi_main = camera_main.digimono_camera_main()

#無限ループ
while(digi_main.get_ret() == True):
    digi_main.get_frame()
digi_main.main_end()

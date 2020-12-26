# digimono_vision
"デジもの"でカメラを使用したプロジェクト実習のコードを管理しています。

## 開発デバイス
raspberry pi 4 model B <br>
raspberry pi 3 model B

USBカメラ([logicoolのカメラ](https://www.logicool.co.jp/ja-jp/product/hd-webcam-c270n), Amazonへのリンクは[こちら](https://www.amazon.co.jp/%E3%83%AD%E3%82%B8%E3%82%AF%E3%83%BC%E3%83%AB-%E3%82%A6%E3%82%A7%E3%83%96%E3%82%AB%E3%83%A1%E3%83%A9-C270n-%E3%82%B9%E3%83%88%E3%83%AA%E3%83%BC%E3%83%9F%E3%83%B3%E3%82%B0-2%E5%B9%B4%E9%96%93%E3%83%A1%E3%83%BC%E3%82%AB%E3%83%BC%E4%BF%9D%E8%A8%BC/dp/B07QMKND9M))

raspberry piを使用する際はケース、ファンまたはヒートシンクを使用することをお勧めします。また、microSDカードは32GB以上、Class10、UHS-Ⅰ以上を推奨します。
## 開発環境
python 3.7.3 <br>
opencv 4.1.0 <br>
matplotlib 3.3.3 <br>
scipy 1.5.4 <br>

## インストールが必要なライブラリ
python3<br>
opencv(バージョン4.1.0.25)<br>
pyyaml<br>
scipy(バージョン1.5.4)

## ライブラリのインストール手順
[ここ](https://qiita.com/wk_/items/8db529a6b24a955888db)のサイトを参考にしています。
まずはターミナルを立ち上げます。**Ctrl+Alt+T**で立ち上がります。<br>
次に必要なライブラリを入れます。<br>(コピー&ペーストで構いません。ただし、Raspberry PiのTerminal上でコピー＆ペーストをするためには**Ctrl+Shift+C**または**Ctrl+Shift+V**になりますので注意していください。また、すでに入っていたり不必要なライブラリも入っていることもあります。ご了承ください。)
```
sudo apt update
sudo apt upgrade
sudo apt install python3 python3-pip git vim nano
sudo pip install --upgrade pip
sudo apt install libavutil56 libcairo-gobject2 libgtk-3-0 libqtgui4 libpango-1.0-0 libqtcore4 libavcodec58 libcairo2 libswscale5 libtiff5 libqt4-test libatk1.0-0 libavformat58 libgdk-pixbuf2.0-0 libilmbase23 libjasper1 libopenexr23 libpangocairo-1.0-0 libwebp6 libatlas-base-dev gfortran
```
そして、opencvとpyyaml,scipyを入れます。
```
sudo pip3 install opencv-python==4.1.0.25
sudo pip3 install pyyaml
sudo pip3 install scipy
```
## Raspberry Piにプログラムを入れる
このリポジトリをクローンします。
```
git clone https://github.com/srmitu/digimono_vision.git
```
その後、digimono_visionのディレクトリに移動します。
```
cd digimono_vision
```
## 実行
カメラはraspberry piの電源を入れる前にあらかじめ接続しておいてください。<br>
main.pyを実行してください。
```
python3 main.py
```
## モード
設定ファイルを変更することにより、このプログラムは大きく分けて2種類の挙動をします。
### 通常モード
設定ファイルにある、閾値と枠の情報を基に計算をし、物体が枠に入ったかを調べ、その結果によって動作をします
### 色取得モード
キー入力により、色を取得することができます。

色取得モードにするためには`debug:`内の`color_detection`のコメントアウトを削除し、インデントを整えた後、有効な`shape`と`num_attempt`を入力します。

## キー入力
`permit_show_processed`を`Ture`にしている時に限ります。
### 2モード共通
`ESC`: 終了(このコマンドのみ`permit_show_video`を`True`にしていても作用します。)<br>
`r`: 再起動(正しくは初期化)
### 通常モード
`ENTER`: 時間を計測した後に限り、計測結果をクリアできます。
### 色取得モード
`c`: 設定ファイルで設定した分、色を取得します。取得結果は反映され、グラフとしても表示されます。<br>
`p`: 前回取得した色に加えて色を取得できるように設定できます。画面の右端に`+`と表示されます。実行するにはその状態で`c`を押します。キャンセルする場合は`n`を押します。<br>
`m`: 前回取得した色からこれから取得する色を削除することができるように設定できます。画面の右端に`-`と表示されます。実行するにはその状態で`c`を押します。キャンセルする場合は`n`を押します。<br>
`n`: `p`や`m`をキャンセルします。<br>
`u`: 前回取得した時の設定に戻ります。
`i`: 自分で閾値を設定できます。この際には映像は止まり、端末にキーボードから数字を画面の指示に従い入力する必要があります。

## プログラムの概要
このプログラムはマルチプロセス化しています。
### camera_frame.py
camera_frame.pyはカメラから映像を入手するクラスが入っているプログラムです。このクラスは呼び出すとプロセスを作成し、デーモンの状態で稼働します。
### camera_main.py
camera_main.pyはcamera_process.py内のクラスを使用してカメラ周りのコントロールをするクラスが入っているプログラムです。
### camara_process.py
camera_process.pyはcamera_maskとcamera_position内のクラスをマルチプロセス化して管理するための便利なメソッドをもつクラスが入っているプログラムです。
### camera_mask.py
camera_mask.pyは入手したカメラの映像から指定した色を抽出し、それの輪郭と中心（重心）を抽出するクラスが入っているプログラムです。このクラスが処理できるのは1つの色だけで、複数色で処理したい場合は別途呼び出す必要があります。使用するためにはtaskを操作する必要があります。また、このプログラムはマルチプロセス化することを強くすすめます。
### camera_position.py
camera_position.pyは入手した中心（重心）が指定した枠に入っているか判定するクラスが入っているプログラムです。判定には中心（重心）の他に判定する色、枠の情報が必要となります。このクラスも1つの条件のみしか判断しないため、別のパターンを処理したい場合は別途呼び出す必要があります。使用するためにはtaskを操作する必要があります。また、このプログラムはマルチプロセス化することを強くすすめます。
### camera_capture.py
camera_capture.pyは加工した映像データを録画するクラスが入っているプログラムです。このクラスは呼び出すとプロセスを作成し、デーモンの状態で稼働します。
### logger.py
ログ(csvファイル)を出力するためのクラスが入っているプログラムです。ここでいうログとは重心が枠の中に入った時間(UNIX)とその枠の番号が、枠の種類によって違うファイルに出力されます。
### get_color.py
色を取得するクラスが入っているプログラムです。通常運用ですと使用しません。しかし、設定ファイルを書き換えることにより、色を取得する専用のモードになり、camera_main.pyでもそのための処理が始まります。キー入力が必要です。取得した閾値で設定ファイルを書き換えることにより、その環境にあった動作が期待できます。
### user_code.py
ユーザーコードを管理するクラスが入っているプログラムです。汎用性はそこまで高くはありませんが、基本的にここのコードを触ることによって、その環境にあった動作が期待できます。
### config_read.py
設定ファイル(config.yml)を呼び出し、読み込むクラスが入っているプログラムです。設定ファイルはyamlを使用しています。

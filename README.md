# digimono_vision
"デジもの"でカメラを使用したプロジェクト実習のコードを管理しています。

## 開発デバイス
raspberry pi 4 model B <br>
raspberry pi 3 model B

USBカメラ([logicoolのカメラ](https://www.logicool.co.jp/ja-jp/product/hd-webcam-c270n), Amazonへのリンクは[こちら](https://www.amazon.co.jp/%E3%83%AD%E3%82%B8%E3%82%AF%E3%83%BC%E3%83%AB-%E3%82%A6%E3%82%A7%E3%83%96%E3%82%AB%E3%83%A1%E3%83%A9-C270n-%E3%82%B9%E3%83%88%E3%83%AA%E3%83%BC%E3%83%9F%E3%83%B3%E3%82%B0-2%E5%B9%B4%E9%96%93%E3%83%A1%E3%83%BC%E3%82%AB%E3%83%BC%E4%BF%9D%E8%A8%BC/dp/B07QMKND9M))

raspberry piを使用する際はケース、ファンまたはヒートシンクを使用することをお勧めします。
## 開発環境
python 3.7.3 <br>
opencv 4.1.0

## インストールが必要なライブラリ
python3<br>
opencv(バージョン4.1.0)<br>
pyyaml

## プログラムの概要
このプログラムはマルチプロセス化しています。
### camera_frame.py
camera_frame.pyはカメラから映像を入手するクラスが入っているプログラムです。このクラスは呼び出すとプロセスを作成し、デーモンの状態で稼働します。
### camara_main.py
camera_main.pyはcamera_maskとcamera_position内のクラスをマルチプロセス化して管理するクラスが入っているプログラムです。
### camera_mask.py
camera_mask.pyは入手したカメラの映像から指定した色を抽出し、それの輪郭と中心（重心）を抽出するクラスが入っているプログラムです。このクラスが処理できるのは1つの色だけで、複数色で処理したい場合は別途呼び出す必要があります。使用するためにはtaskを操作する必要があります。また、このプログラムはマルチプロセス化することを強くすすめます。
### camera_position.py
camera_position.pyは入手した中心（重心）が指定した枠に入っているか判定するクラスが入っているプログラムです。判定には中心（重心）の他に判定する色、枠の情報が必要となります。このクラスも1つの条件のみしか判断しないため、別のパターンを処理したい場合は別途呼び出す必要があります。使用するためにはtaskを操作する必要があります。また、このプログラムはマルチプロセス化することを強くすすめます。
### camera_capture.py
camera_capture.pyは加工した映像データを録画するクラスが入っているプログラムです。
### config_read.py
設定ファイル(config.yml)を呼び出し、読み込むクラスが入っているプログラムです。設定ファイルはyamlを使用しています。

## 実行
カメラを接続し、raspberry piの電源を入れます。
その後、main.pyを実行します。
```
python3 main.py
```
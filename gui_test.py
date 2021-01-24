import sys
import os
import cv2
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import yaml
import camera_main
import time


#camera_mainの定義、コンフィグファイルの読み込み
digi_main = camera_main.digimono_camera_main()

class Thread(QThread):
    frameGrabbed = pyqtSignal(QImage)

    def run(self):
        while digi_main.get_ret():
            # Qt はチャンネル順が RGB なので変換する。
            rgbImage = cv2.cvtColor(digi_main.get_frame(), cv2.COLOR_BGR2RGB)
            # numpy 配列を QImage に変換する。
            qImage = QImage(
                rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
            # シグナルを送出する。
            self.frameGrabbed.emit(qImage)
            # スリープを入れる。1000 / fps 分入れる
            QThread.msleep(1000 / 30)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        pixmap = QPixmap.fromImage(image)
        # ラベルの大きさに合わせて QPixmap をスケールする。
        #pixmap = pixmap.scaled(
        #    self.label.width(), self.label.height(), Qt.KeepAspectRatio)
        self.label.setPixmap(pixmap)

    @pyqtSlot()
    def initUI(self):
        font=QFont()
        font.setPointSize(15)
        # shape parameta
        self.oxedit=QLineEdit("0",self)
        self.oxedit.setFont(font)
        self.oyedit=QLineEdit("0",self)
        self.oyedit.setFont(font)
        self.xedit=QLineEdit("0",self)
        self.xedit.setFont(font)
        self.yedit=QLineEdit("0",self)
        self.yedit.setFont(font)
        center=QLabel('中心座標')
        ox=QLabel('x')
        oy=QLabel('y')
        parameta=QLabel('パラメータ')
        x=QLabel('X')
        y=QLabel('Y')
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(center, 1, 0)
        grid.addWidget(ox, 2, 0)
        grid.addWidget(self.oxedit, 2, 1)
        grid.addWidget(oy, 2, 2)
        grid.addWidget(self.oyedit, 2, 3)
        grid.addWidget(parameta, 3, 0)
        grid.addWidget(x, 4, 0)
        grid.addWidget(self.xedit, 4, 1)
        grid.addWidget(y, 4, 2)
        grid.addWidget(self.yedit, 4, 3)
        # ボタンの設定
        button = QPushButton("exit", self)
        button.setStyleSheet('QPushButton {background-color: red; color: red;}')
        #button.setGeometry(1600, 800, 200, 50)
        button.clicked.connect(self.on_click)
        apbutton = QPushButton("apply", self)
        apbutton.clicked.connect(self.on_apply)
        dlbutton = QPushButton("remove", self)
        dlbutton.clicked.connect(self.on_remove)
        self.dledit=QLineEdit("0",self)
        self.dledit.setFont(font)
        removehbox = QHBoxLayout()
        removehbox.addWidget(dlbutton)
        removehbox.addWidget(self.dledit)
        # ラベル作成、初期の名前を設定する
        self.lbl = QLabel("長方形", self)
        self.activeShape = "rectangle"

        # QComboBoxオブジェクトの作成
        combo = QComboBox(self)
        # アイテムの名前設定
        combo.addItem("長方形")
        combo.addItem("楕円")

        # アイテムが選択されたらonActivated関数の呼び出し
        combo.activated[str].connect(self.onActivated)        

        # 画像表示用のラベル
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(combo)
        vbox.addWidget(self.lbl)
        vbox.addWidget(apbutton)
        vbox.addLayout(removehbox)
        vbox.addLayout(grid)
        vbox.addWidget(button)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.label)
        hbox.addLayout(vbox)
        self.setLayout(hbox)

        # 画像キャプチャー用のスレッドを作成する。
        th = Thread(self)
        th.frameGrabbed.connect(self.setImage)
        th.start()

    def onActivated(self, text):
        # ラベルに選択されたアイテムの名前を設定
        self.lbl.setText(text)
        # ラベルの長さを調整
        self.lbl.adjustSize()  
        self.activeShape = text

    def on_apply(self):
        print("clicked apply")
        color = 0
        mode = "START"
        shape_type = self.activeShape
        if shape_type == "長方形" :
            shape_type = "rectangle"
        elif shape_type == "楕円" :
            shape_type = "ellipse"
        string = self.oxedit.text()
        ox = int(string, 10)
        string = self.oyedit.text()
        oy = int(string, 10)
        string = self.xedit.text()
        x = int(string, 10)
        string = self.yedit.text()
        y = int(string, 10)
        with open('config.yml', 'r') as f:
            data = yaml.safe_load(f)
            num_keys = data['shape'].keys()
            data['shape'][len(num_keys)] = {'num_color':color, 'mode':mode, 'type_shape':shape_type, 'shape':[[ox, oy], [x, y]]}
        with open('config.yml', 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        digi_main.reboot()
        time.sleep(20)

    def on_remove(self):
        print("clicked remove")
        string = self.dledit.text()
        num = int(string, 10)
        with open('config.yml', 'r') as f:
            rawdata = yaml.safe_load(f)
            del rawdata['shape'][num]
            num_keys = rawdata['shape'].keys()
            data = rawdata.copy()
            i = 0
            for key in list(rawdata['shape']) :
                data['shape'][i] = rawdata['shape'][key]
                i += 1
        with open('config.yml', 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        digi_main.reboot()
        time.sleep(20)


    def on_click(self):
        print("clicked exit")
        digi_main.put_end_check(True)
        digi_main.main_end()
        os._exit(0)
        sys.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Window()
    #w.show()
    w.showFullScreen()
    sys.exit(app.exec_())

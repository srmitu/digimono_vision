import sys
import os
import cv2
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import yaml
import camera_main
import time
import logging
import datetime


#camera_mainの定義、コンフィグファイルの読み込み
#digi_main = camera_main.digimono_camera_main()

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

class Thread(QThread):
    frameGrabbed = pyqtSignal(QImage)
    def contact(self, digi_main):
        self.digi_main = digi_main

    def run(self):
        try:
            while True:
                # Qt はチャンネル順が RGB なので変換する。
                rgbImage = cv2.cvtColor(self.digi_main.get_frame(), cv2.COLOR_BGR2RGB)
                # numpy 配列を QImage に変換する。
                qImage = QImage(
                    rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
                # シグナルを送出する。
                self.frameGrabbed.emit(qImage)
                # スリープを入れる。1000 / fps 分入れる
                QThread.msleep(1000 // 30)
        except:
            pass


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        pixmap = QPixmap.fromImage(image)
        # ラベルの大きさに合わせて QPixmap をスケールする。
        #pixmap = pixmap.scaled(
        #   1000, 1000, Qt.KeepAspectRatio, Qt.FastTransformation)
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
        self.oxedit.textChanged.connect(self.add_shape)
        self.oyedit.textChanged.connect(self.add_shape)
        self.xedit.textChanged.connect(self.add_shape)
        self.yedit.textChanged.connect(self.add_shape)

        center=QLabel('中心座標')
        ox=QLabel('x')
        oy=QLabel('y')
        parameta=QLabel('パラメータ')
        x=QLabel('X')
        y=QLabel('Y')
        grid = QGridLayout()
        grid.setSpacing(15)
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
        # ラベル作成、初期の名前を設定する
        self.lbl2 = QLabel("START", self)
        self.activeMode = "START"

        # QComboBoxオブジェクトの作成
        combo2 = QComboBox(self)
        # アイテムの名前設定
        combo2.addItem("START")
        combo2.addItem("END")
        combo2.addItem("ERROR")
        combo2.addItem("RECOGNITION")

        # アイテムが選択されたらonActivated関数の呼び出し
        combo2.activated[str].connect(self.onActivatedmode)        

        # 画像表示用のラベル
        self.label = QLabel(self)
        #self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        
        #logging
        logTextBox = QTextEditLogger(self)
        # You can format what is printed to text box
        logTextBox.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.DEBUG)
        log_display = QVBoxLayout()
        # Add the new logging box widget to the layout
        log_display.addWidget(logTextBox.widget)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(combo2)
        vbox.addWidget(self.lbl2)
        vbox.addWidget(combo)
        vbox.addWidget(self.lbl)
        vbox.addWidget(apbutton)
        vbox.addLayout(removehbox)
        vbox.addLayout(grid)
        vbox.addWidget(button)
        ibox = QVBoxLayout()
        ibox.addStretch(1)
        ibox.addWidget(self.label)
        ibox.addLayout(log_display)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        #hbox.addWidget(self.label)
        hbox.addLayout(ibox)
        hbox.addLayout(vbox)
        self.setLayout(hbox)

        # 画像キャプチャー用のスレッドを作成する。
        #th = Thread(self, main)
        th = Thread(self)
        self.digi_main = camera_main.digimono_camera_main()
        th.contact(self.digi_main)
        th.frameGrabbed.connect(self.setImage)
        th.start()

    def onActivated(self, text):
        # ラベルに選択されたアイテムの名前を設定
        self.lbl.setText(text)
        # ラベルの長さを調整
        self.lbl.adjustSize()  
        self.activeShape = text
        self.add_shape()
    def onActivatedmode(self, text):
        # ラベルに選択されたアイテムの名前を設定
        self.lbl2.setText(text)
        # ラベルの長さを調整
        self.lbl2.adjustSize()  
        self.activeMode = text

    def add_shape(self):
        x = 0
        y = 0
        error = 0
        color = 0
        shape_type = self.activeShape
        if shape_type == "長方形" :
            shape_type = "rectangle"
        elif shape_type == "楕円" :
            shape_type = "ellipse"
        string = self.oxedit.text()
        try:
            ox = int(string, 10)
        except:
            error += 1
        string = self.oyedit.text()
        try:
            oy = int(string, 10)
        except:
            error += 1
        string = self.xedit.text()
        try:
            x = int(string, 10)
        except:
            error += 1
        string = self.yedit.text()
        try:
            y = int(string, 10)
        except:
            error = 1
        if(error == 0):
            if(x > 0 and y > 0):
                with open('config.yml', 'r') as f:
                    data = yaml.safe_load(f)
                    num_keys = data['shape'].keys()
                self.digi_main.put_add_shape(len(num_keys), color, shape_type, [[ox, oy], [x, y]])
            else:
                self.digi_main.reset_add()
        else:
            self.digi_main.reset_add()


    def on_apply(self):
        print("clicked apply")
        color = 0
        mode = self.activeMode
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
        self.digi_main.put_reboot_check(True)

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
        self.digi_main.put_reboot_check(True)


    def on_click(self):
        print("clicked exit")
        self.digi_main.put_end_check(True)
        self.digi_main.main_end()
        sys.exit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    w = Window()
    #w.show()
    w.showFullScreen()
    sys.exit(app.exec_())

import yaml
import sys
import numpy

class digimono_config_read(object):
    def __init__(self):
        pass
    def config_detect(self):
        f = open("config.yml", "r+")
        config_data = yaml.safe_load(f)

        #定義の読み込み
        camera_num = config_data['define']['camera_num']
        min_area = config_data['define']['min_area']
        permit_show_video = config_data['define']['permit_show_video']
        print("define data can be read")

        #maskプロセス用の設定の読み込み
        threshold = []
        num_color = len(config_data['color'])
        for num in range(num_color):
            if((num in config_data['color']) == False):
                print('Error: There is no color number(' + str(num) + ') data in the config data', file=sys.stderr)
                sys.exit(1)
            threshold.append(numpy.array(config_data['color'][num]))
        print(str(num_color) + 'data about color can be read')

        #positionプロセス用の設定の読み込み
        color = []
        mode = []
        type_shape = []
        shape = []
        num_shape = len(config_data['shape'])
        for num in range(num_shape):
            if((num in config_data['shape']) == False):
                print('Error: There is no shape number(' + str(num) + ') data in the config data', file=sys.stderr)
                sys.exit(1)
            color.append(config_data['shape'][num]['num_color'])
            mode.append(config_data['shape'][num]['mode'])
            type_shape.append(config_data['shape'][num]['type_shape'])
            shape.append((config_data['shape'][num]['shape']))
        print(str(num_color) + 'data about shape can be read')

        print("All data can be read")
        return camera_num, min_area, permit_show_video, threshold, color, mode, type_shape, shape, num_color, num_shape

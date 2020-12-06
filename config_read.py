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
        permit_record = config_data['define']['permit_record']
        print("define data can be read")

        #maskプロセス用の設定の読み込み
        threshold = []
        num_color = len(config_data['color'])
        for num in range(num_color):
            if((num in config_data['color']) == False):
                print('Error: There is no color number(' + str(num) + ') data in the config data', file=sys.stderr)
                sys.exit(1)
            threshold.append(numpy.array(config_data['color'][num]))
        print(str(num_color) + ' data about color can be read')

        #positionプロセス用の設定の読み込み
        color = []
        mode = []
        type_shape = []
        shape = []
        num_shape = len(config_data['shape'])
        for num in range(num_shape):
            if((num in config_data['shape']) == False):
                print('Error: There is no shape number(' + str(num) + ') in the config data', file=sys.stderr)
                sys.exit(1)
            #不適切な設定ファイルになっていないかチェック
            if(config_data['shape'][num]['type_shape'] != "rectangle" and config_data['shape'][num]['type_shape'] != "ellipse"):
                print('Error: type_shape data of number(' + str(num) + ') in the config data is not correct', file=sys.stderr)
                sys.exit(1)
            if(config_data['shape'][num]['mode'] != "START" and config_data['shape'][num]['mode'] != "END" and config_data['shape'][num]['mode'] != "ERROR" and config_data['shape'][num]['mode'] != "RECOGNITION"):
                print('Error: mode data of number(' + str(num) + ') in the config data is not correct', file=sys.stderr)
                sys.exit(1)
            if(len(config_data['shape'][num]['shape']) != 2):
                print('Error: shape data of number(' + str(num) + ') in the config data is not correct. length is not 2', file=sys.stderr)
                print(len(config_data['shape'][num]['shape']))
                sys.exit(1)
            if(config_data['shape'][num]['num_color'] >= num_color or config_data['shape'][num]['num_color'] < 0):
                print('Error: num_color data of number(' + str(num) + ') in the config data is not correct', file=sys.stderr)
                sys.exit(1)

            color.append(config_data['shape'][num]['num_color'])
            mode.append(config_data['shape'][num]['mode'])
            type_shape.append(config_data['shape'][num]['type_shape'])
            shape.append((config_data['shape'][num]['shape']))
        print(str(num_color) + ' data about shape can be read')

        print("All data can be read")
        return camera_num, min_area, permit_show_video, permit_record,  threshold, color, mode, type_shape, shape, num_color, num_shape

import yaml
import sys

class digimono_config_read(object):
    def __init__(self, config_name):
        self.config_name = config_name
        pass
    def config_detect(self):
        f = open(self.config_name, "r+")
        config_data = yaml.safe_load(f)
        #返却するリストを定義
        return_config = []

        #定義の読み込み
        camera_num = config_data['define']['camera_num']
        min_area = config_data['define']['min_area']
        if(('what_record' in config_data['define']) == True):
            if(config_data['define']['what_record'] != "none" and config_data['define']['what_record'] != "video" and config_data['define']['what_record'] != "processed" and config_data['define']['what_record'] != "both" and config_data['define']['what_record'] != "all"):
                print('Error: I do not know what to record. none? video? processed? all? or both?', file=sys.stderr)
                sys.exit(1)
            permit_record = config_data['define']['what_record']
        else:
            permit_record = "none"
        permit_record_raw = False
        permit_record_processed = False
        if(permit_record == "video" or permit_record == "both" or permit_record == "all"):
            permit_record_raw = True
        if(permit_record == "processed" or permit_record == "both" or permit_record == "all"):
            permit_record_processed = True
        
        return_config.append(camera_num)
        return_config.append(min_area)
        return_config.append(permit_record_raw)
        return_config.append(permit_record_processed)
        print("define data can be read")

        #maskプロセス用の設定の読み込み
        threshold = []
        num_color = len(config_data['color'])
        for num in range(num_color):
            if((num in config_data['color']) == False):
                print('Error: There is no color number(' + str(num) + ') data in the config data', file=sys.stderr)
                sys.exit(1)
            threshold.append(config_data['color'][num])
        return_config.append(threshold)
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
        return_config.append(color)
        return_config.append(mode)
        return_config.append(type_shape)
        return_config.append(shape)
        print(str(num_shape) + ' data about shape can be read')
        return_config.append(num_color)
        return_config.append(num_shape)
        #デバック用の設定を読み込み(値がなかった場合はエラーを起こさない)
        permit_show_video = False
        permit_show_processed = False
        permit_show_contours = False
        permit_color_detect = False
        color_detect_shape = 0
        color_detect_num_attempt = 0
        if(('debug' in config_data) == True and config_data['debug'] != None):
            print("found debug data", end="\r")
            if(('permit_show_video' in config_data['debug']) == True):
                permit_show_video = config_data['debug']['permit_show_video']
            if(('permit_show_processed' in config_data['debug']) == True):
                permit_show_processed = config_data['debug']['permit_show_processed']
            if(('permit_show_contours' in config_data['debug']) == True):
                permit_show_contours = config_data['debug']['permit_show_contours']
            if(('color_detection' in config_data['debug']) == True):
                if((('shape' in config_data['debug']['color_detection']) == True) and (('num_attempt' in config_data['debug']['color_detection']) == True)):
                        print('color_detect')
                        permit_color_detect = True
                        color_detect_shape = config_data['debug']['color_detection']['shape']
                        color_detect_num_attempt = config_data['debug']['color_detection']['num_attempt']
            print('All data about debug can be read')
        return_config.append(permit_show_video)
        return_config.append(permit_show_processed)
        return_config.append(permit_show_contours)
        return_config.append(permit_color_detect)
        return_config.append(color_detect_shape)
        return_config.append(color_detect_num_attempt)
            

        print("All data can be read")
        return return_config
        #順にcamera_num, min_area, permit_record_raw, permit_record_processed, threshold, color, mode, type_shape, shape, num_color, num_shape, permit_show_video, permit_show_processed, permit_show_contours, permit_color_detect, color_detect_shape, color_detect_num_attempt

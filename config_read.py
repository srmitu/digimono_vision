import yaml
import sys
import logging

class digimono_config_read(object):
    def __init__(self, config_name):
        self.config_name = config_name
        self.logger = logging.getLogger(__name__)
    def config_detect(self):
        f = open(self.config_name, "r+")
        config_data = yaml.safe_load(f)
        #返却するリストを定義
        return_config = []

        #定義の読み込み
        permit_color_detect = False
        color_detect_shape = 0
        color_detect_num_attempt = 0
        record_time = 3600
        permit_record_raw = False
        permit_record_processed = False
        recommend_video = False
        recommend_processed = False
        num_recommend_slow = 0
        num_recommend_fast = 0
        camera_num = config_data['define']['camera_num']
        min_area = config_data['define']['min_area']
        if(('what_record' in config_data['define']) == True):
            if(config_data['define']['what_record'] != "none" and config_data['define']['what_record'] != "video" and config_data['define']['what_record'] != "processed" and config_data['define']['what_record'] != "both" and config_data['define']['what_record'] != "all"):
                self.logger.error('Error: I do not know what to record. none? video? processed? all? or both?', file=sys.stderr)
                sys.exit(1)
            permit_record = config_data['define']['what_record']
        else:
            permit_record = "none"
        if(permit_record == "video" or permit_record == "both" or permit_record == "all"):
            permit_record_raw = True
        if(permit_record == "processed" or permit_record == "both" or permit_record == "all"):
            permit_record_processed = True
        if(('color_detection' in config_data['define']) == True):
            if((('shape' in config_data['define']['color_detection']) == True) and (('num_attempt' in config_data['define']['color_detection']) == True)):
                if not (config_data['define']['color_detection']['num_attempt'] == 0):
                    self.logger.info('color_detect')
                    permit_color_detect = True
                    color_detect_shape = config_data['define']['color_detection']['shape']
                    color_detect_num_attempt = config_data['define']['color_detection']['num_attempt']
        if(('record_time' in config_data['define']) == True):
            record_time = config_data['define']['record_time']
        if(('recommend_video' in config_data['define']) == True):
            recommend_video = config_data['define']['recommend_video']
        if(('recommend_processed' in config_data['define']) == True):
            recommend_processed = config_data['define']['recommend_processed']
        if(('num_recommend_slow' in config_data['define']) == True):
            num_recommend_slow = config_data['define']['num_recommend_slow']
        if(('num_recommend_fast' in config_data['define']) == True):
            num_recommend_fast = config_data['define']['num_recommend_fast']
        
        return_config.append(camera_num)
        return_config.append(min_area)
        return_config.append(permit_record_raw)
        return_config.append(permit_record_processed)
        return_config.append(permit_color_detect)
        return_config.append(color_detect_shape)
        return_config.append(color_detect_num_attempt)
        return_config.append(record_time)
        return_config.append(recommend_video)
        return_config.append(recommend_processed)
        return_config.append(num_recommend_slow)
        return_config.append(num_recommend_fast)
        self.logger.info("define data can be read")

        #maskプロセス用の設定の読み込み
        threshold = []
        num_color = len(config_data['color'])
        for num in range(num_color):
            if((num in config_data['color']) == False):
                self.logger.error('Error: There is no color number(' + str(num) + ') data in the config data', file=sys.stderr)
                sys.exit(1)
            threshold.append(config_data['color'][num])
        return_config.append(threshold)
        self.logger.info(str(num_color) + ' data about color can be read')

        #positionプロセス用の設定の読み込み
        color = []
        mode = []
        type_shape = []
        shape = []
        num_shape = len(config_data['shape'])
        for num in range(num_shape):
            if((num in config_data['shape']) == False):
                self.logger.error('Error: There is no shape number(' + str(num) + ') in the config data', file=sys.stderr)
                sys.exit(1)
            #不適切な設定ファイルになっていないかチェック
            if(config_data['shape'][num]['type_shape'] != "rectangle" and config_data['shape'][num]['type_shape'] != "ellipse"):
                self.logger.error('Error: type_shape data of number(' + str(num) + ') in the config data is not correct', file=sys.stderr)
                sys.exit(1)
            if(config_data['shape'][num]['mode'] != "START" and config_data['shape'][num]['mode'] != "END" and config_data['shape'][num]['mode'] != "ERROR" and config_data['shape'][num]['mode'] != "RECOGNITION"):
                self.logger.error('Error: mode data of number(' + str(num) + ') in the config data is not correct', file=sys.stderr)
                sys.exit(1)
            if(len(config_data['shape'][num]['shape']) != 2):
                self.logger.error('Error: shape data of number(' + str(num) + ') in the config data is not correct. length is not 2', file=sys.stderr)
                self.logger.error(len(config_data['shape'][num]['shape']))
                sys.exit(1)
            if(config_data['shape'][num]['num_color'] >= num_color or config_data['shape'][num]['num_color'] < 0):
                self.logger.error('Error: num_color data of number(' + str(num) + ') in the config data is not correct', file=sys.stderr)
                sys.exit(1)

            color.append(config_data['shape'][num]['num_color'])
            mode.append(config_data['shape'][num]['mode'])
            type_shape.append(config_data['shape'][num]['type_shape'])
            shape.append((config_data['shape'][num]['shape']))
        return_config.append(color)
        return_config.append(mode)
        return_config.append(type_shape)
        return_config.append(shape)
        self.logger.info(str(num_shape) + ' data about shape can be read')
        return_config.append(num_color)
        return_config.append(num_shape)

        #デバック用の設定を読み込み(値がなかった場合はエラーを起こさない)
        permit_show_video = False
        permit_show_processed = False
        permit_show_contours = False
        if(('debug' in config_data) == True and config_data['debug'] != None):
            self.logger.info("found debug data")
            if(('permit_show_video' in config_data['debug']) == True):
                permit_show_video = config_data['debug']['permit_show_video']
            if(('permit_show_processed' in config_data['debug']) == True):
                permit_show_processed = config_data['debug']['permit_show_processed']
            if(('permit_show_contours' in config_data['debug']) == True):
                permit_show_contours = config_data['debug']['permit_show_contours']
            self.logger.info('All data about debug can be read')
        return_config.append(permit_show_video)
        return_config.append(permit_show_processed)
        return_config.append(permit_show_contours)
            

        self.logger.info("All data can be read")
        return return_config
        #順にcamera_num, min_area, permit_record_raw, permit_record_processed, permit_color_detect, color_detect_shape, color_detect_num_attempt, record_time, recommend_video, recommend_processed, num_recommend_slow, num_recommend_fast, threshold, color, mode, type_shape, shape, num_color, num_shape, permit_show_video, permit_show_processed, permit_show_contours

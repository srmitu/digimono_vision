import subprocess
import glob
import os

class digimono_rclone_copy(object):
    def __init__(self):
        self.path = "/home/pi/git_opencv/digimono_vision/"
        self.copy_dir = ""
        self.drive_name = ""
        self.drive_dir = ""
        self.bool_combine_file = False

    def share(self):
        if not (self.copy_dir == "" and self.drive_name == ""):
            print(self.path+str(self.copy_dir))
            if os.path.isdir(self.path+str(self.copy_dir)):
                if(self.bool_combine_file == True):
                    if(str(self.copy_dir) in str('/')):
                        files = glob.glob(self.path+str(self.copy_dir) + '*')
                    else:
                        files = glob.glob(self.path+str(self.copy_dir) + '/*')
                else:
                    files = glob.glob(self.path+str(self.copy_dir))
                drive_name = str(self.drive_name) + str(":")
                for video_file in files:
                    str_video_file = str(video_file)
                    print('rclone', 'copy', str(video_file), drive_name + str(self.drive_dir))
                    subprocess.run(['rclone', 'copy', str(video_file), drive_name + str(self.drive_dir)])
            else:
                print('no such dir name:' + path + str(self.copy_dir))
        else:
            print('dir name is blank')
            print('self.copy_dir:', self.copy_dir)
            print('self.drive_name:', self.drive_name)
    def copy(self):
        self.share()

    def put_copy_dir(self, name):
        self.copy_dir = str(name)

    def put_drive_name(self, name):
        self.drive_name = str(name)

    def put_drive_dir(self, name):
        self.drive_dir = str(name)

    def put_bool_combine_file(self, boolean):
        if(boolean == True):
            self.bool_combine_file = True
        elif(boolean == False):
            self.bool_combine_file = False

    def get_copy_dir():
        return self.copy_dir

    def get_drive_name():
        return self.copy_di

    def get_drive_dir():
        return  self.copy_dir

    def get_bool_combine_file(self):
        return self.bool_combine_file

if __name__ == '__main__':
    rclone_copy = digimono_rclone_copy()
    rclone_copy.put_copy_dir('')
    rclone_copy.put_drive_name('')
    rclone_copy.put_drive_dir('')
    rclone_copy.share()


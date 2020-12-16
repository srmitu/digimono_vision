import cv2

class digimono_comm(object):
    def __init__(self):
        self.reboot = False

    def cycle_reset(self, permit_show_processed):
        return_bool = False
        if(permit_show_processed == True):
            if(cv2.waitKey(5) == 13): #Enter key
                return_bool = True
        '''
        #GUIからの信号
        elif(#GUIからの処理#):
            return_bool = True
        '''

        return return_bool

    def end_check(self):
        return_bool = False
        '''
        #GUIからの信号
        if(#GUIからの処理#):
            return_bool True
        '''
        return return_bool
    def reboot_check(self, permit_show_processed):
        #本来はGUIからの信号によりrebootを判断
        #debug用に他の手段もある。
        if(permit_show_processed == True):
            if(cv2.waitKey(5) == ord('r')):
                self.reboot = True
                print("reboot request")
        '''
        #GUIからの信号
        elif(#GUIからの処理#):
            self.reboot = True
        '''
        return self.reboot

    def color_capture(self, permit_show_processed):
        return_bool = False

        if(permit_show_processed == True):
            if(cv2.waitKey(5) == ord('c')):
                return_bool = True
                print("color capture")

        return return_bool

      



        

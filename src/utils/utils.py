import os
import sys

class utils:
    
    def open_path(path: str):
        os.startfile(path)
        
    def resource_path(file):
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        return os.path.join(base_path, file)
    
 
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

    def get_unique_filepath(directory: str, base_name: str) -> str:
        filename = os.path.join(directory, base_name)
        counter = 1
        while os.path.exists(filename):
            name_only, ext = os.path.splitext(base_name)
            filename = os.path.join(directory, f"{name_only}_{counter}{ext}")
            counter += 1
        return filename

import json
import os
from pathlib import Path
import shutil
import sys
from src.utils.utils import utils

class settings:
    
    def __init__(self):
         self.config_path = self.ensure_config_available()
        
    def get_config_file_path(self):
        return self.config_path
        
    def get_db_config(self):
        with open(self.config_path,'r') as config_file:
            config = json.load(config_file)
            
        return config.get("db_config")
    
    def get_db_name(self):
        db_config = self.get_db_config()
        return db_config["database"]

    def get_server_name(self):
        db_config = self.get_db_config()
            
        return db_config["server"]

    def is_configured(self):
        db_config = self.get_db_config()
        is_configured = all(v not in [None, ""] for v in db_config.values())
            
        return is_configured
    
    #Download Path
    def get_download_path(self):
        config_path = Path(self.get_config_file_path()) 
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("download_path", "")
        
    def set_download_path(self, new_path):
        config_path = Path(self.get_config_file_path()) 
        
        with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        
        config["download_path"] = new_path
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            
            
    #Installed App
    
    def get_user_config_path(self):
        # Ruta segura para guardar el archivo (editable por el usuario)
        appdata_dir = os.path.join(os.getenv("APPDATA"), "SQLObjectGenerator")
        os.makedirs(appdata_dir, exist_ok=True)
        return os.path.join(appdata_dir, "config.json")
    
    def get_installed_config_path(self):
        # Ruta del archivo junto al ejecutable (solo lectura)
        if getattr(sys, 'frozen', False):
            # Cuando está empaquetado con PyInstaller
            base_path = sys._MEIPASS
        else:
            # En modo desarrollo
            base_path = os.path.dirname(__file__)
        return os.path.join(base_path, "config.json")
    
    def ensure_config_available(self):
        user_config = self.get_user_config_path()
        if not os.path.exists(user_config):
            original_config = self.get_installed_config_path()
            shutil.copy2(original_config, user_config)
        return user_config
        
import json
from pathlib import Path
from src.utils.utils import utils

class settings:
    
    def __init__(self):
         self.config_path = utils.resource_path('config.json')
        
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
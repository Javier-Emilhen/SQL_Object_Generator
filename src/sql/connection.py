import json
from sqlalchemy import create_engine, text
from src.config.config import settings

class sql_class:
    
    def __init__(self):
        _settings = settings()
        self.engine = None
        self.config_path = _settings.get_config_file_path()
        self.server = None
        self.database = None
        self.username = None
        self.password = None
        
        self.load_sql_data()
    
    def load_sql_data(self):
        
        config = settings()
        db_config = config.get_db_config()
            
        self.server = db_config["server"]
        self.username = db_config["username"]
        self.password = db_config["password"]
        self.database = db_config["database"]
        self.engine = None
        
    def connect(self):
        
        config = settings()
        is_configured = config.is_configured()
        
        if(not is_configured):
           raise Exception("The SQL configuration is required, go to the settings button below (Settings).")
        
        connection_string = f'mssql+pyodbc://{self.username}:{self.password}@{self.server}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server'
        self.engine = create_engine(connection_string,pool_pre_ping=True)


    def execute(self, query):
    
        try:
            if self.engine is None:
                print ('No database connection')
                return None
          
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                return result.fetchall()
          
        except Exception as e:
            print(f"Execute error: {e}")
            return None    
        
    def close(self):
       try:
            if self.engine:
                self.engine.dispose()
       except Exception as e:
         print(f"Error al ejecutar la consulta: {e}")

    def test_connection(self, server,username,password,database):
        try:
           
           connection_string = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
           engine = create_engine(connection_string,pool_pre_ping=True)
           
           with engine.connect() as conn:
            engine.dispose()
            return True, "Successful connection"
          
        except Exception as ex :
            return False, f"Connection error: \n{repr(ex)}"
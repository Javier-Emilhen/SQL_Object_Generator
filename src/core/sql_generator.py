import json
import os
from pathlib import Path
from datetime import datetime
from src.models.sql_objects import sql_objects
from src.utils.enumerators import objects_types
from src.utils.enumerators import table_get_options
from src.sql.connection import sql_class
from src.config.config import settings
from src.utils.utils import utils
from src.utils.enumerators import sql_definitions

class sql_generator:
        
    def __init__(self,download_path, clipboard, table_options):
        self.download_path = download_path
        self.clipboard = clipboard
        self.table_options = table_options
        self.db = sql_class()
        self.db.connect()
        
    def download(self,list_sql_objects ): 
        try:
            
            if(not self.clipboard and not Path(self.download_path).exists()):
                raise Exception("The route provided does not exist")
            
            #definiciones
            _sp_definitions=[]
            _table_definitions=[]
            _function_definitions=[]
            _table_records = ""
            scripts = ""
             
            stored_procedures = [item for item in list_sql_objects if item.Object_Key == objects_types.SP.value]
            tables = [item for item in list_sql_objects if item.Object_Key == objects_types.TBL.value]
            functions = [item for item in list_sql_objects if item.Object_Key == objects_types.FN.value]
                
            if(self.table_options in [table_get_options.Schema_Data.name,table_get_options.Schema_Only.name]):
                _sp_definitions = self.get_sp_definition(stored_procedures)
                _table_definitions = self.get_tbl_definition(tables)
                _function_definitions = self.get_fn_definitions(functions)
                scripts = self.generate_definitions(_sp_definitions,_function_definitions, _table_definitions)
                
            if(self.table_options in [table_get_options.Schema_Data.name,table_get_options.Data_Only.name]):
                _table_records = self.get_tbl_records(tables)
                scripts += _table_records
            
            message = None
            
            #Escribir archivos  
            if(not self.clipboard):
                
                base_name = f"Scripts_SQL_{datetime.now().strftime('%d_%m_%Y')}.sql"
                download_path = self.download_path.strip().strip('"')
                filename = os.path.join(download_path, base_name)
                # Si el archivo ya existe, agrega sufijos (1), (2), etc.
                counter = 1
                while os.path.exists(filename):
                    name_only, ext = os.path.splitext(base_name)
                    filename = os.path.join(download_path, f"{name_only}_{counter}{ext}")
                    counter += 1

                # Guardar el archivo
                with open(filename, 'w', encoding="utf-8") as file:
                    file.write(scripts)

                # sql_name = "Scripts_SQL" + datetime.now() + ".sql"
                # filename = os.path.join(self.download_path.strip().strip('"'), sql_name)
                # with open(filename,'w',encoding="utf-8") as file:
                #     file.write(scripts)
                message = "File successfully generated"
                return True, message, None
            #Portapapeles
            else:
                message = "Records successfully generated in the clipboard"
                return True, message, scripts
                
        except Exception as ex :
            return False, f"Error: {ex}",None
      
    def get_sp_definition(self, stored_procedures: list[sql_objects]):
        
        if(len(stored_procedures) == 0): return []
        
        procedures_definition = []

        stored_procedures.sort(key=lambda x: x.Name.lower())

        for sp in stored_procedures:
            result = self.db.execute(f"{sql_definitions.SP_FILE.value} '{sp.Schema}.{sp.Name}'")
            script = ""
            for row in result:
                script += row[0]

            script = script.replace("\r","")
            procedures_definition.append([sp.Schema, sp.Name, script, sp.Sql_Object])
            
        return procedures_definition
        
    def get_fn_definitions(self, functions:list[sql_objects]):
        
        if(len(functions) == 0):
            return []
        
        functions_definitions = []
        
        functions.sort(key=lambda x: x.Name.lower())
        
        for func in functions:
            query = f"DECLARE @ID_Function INTEGER = {func.ID} "
        
            function_path = utils.resource_path(sql_definitions.FUNCTIONS_FILE.value)
            
            with open(function_path, 'r',  encoding='utf-8') as sql_file:
                query += sql_file.read()
                
            result = self.db.execute(query)
            script = ""
            for row in result:
                script += row[0]
            
            script = script.replace("\r","")
            functions_definitions.append([func.Schema, func.Name, script, func.Sql_Object])
        
        return functions_definitions
      
    def get_tbl_definition(self, tables: list[sql_objects]):
        
        if(len(tables) == 0):
            return []
        
        tables_definitions = []
        
        tables.sort(key=lambda x: x.Name.lower())
        
        for tbl in tables:
            query = f"DECLARE @ID_Table INTEGER = {tbl.ID} "
            
            tables_path = utils.resource_path(sql_definitions.TABLES_FILE.value)
            
            with open(tables_path, 'r',  encoding='utf-8') as sql_file:
                query += sql_file.read()
            
            try:
            
                script = self.db.execute(query)
            
                tbl_script = ""

                for row in script:
                    tbl_script += row[0]
            
            except Exception as ex:
                tbl_script = "-- Error generating script:\n" + '-- '+ str(ex)
            
            tbl_script += "\n"
            
            tables_definitions.append([tbl.Schema, tbl.Name, tbl_script, tbl.Sql_Object, ])
        
        return tables_definitions
    
    def get_tbl_records(self, tables: list[sql_objects]):
        table_records = ""
        
        tables.sort(key=lambda x: x.Name.lower())
        
        for tbl in tables:
            query = f"DECLARE @ID_Table INTEGER = {tbl.ID} "
            
            tables_records_path = utils.resource_path(sql_definitions.TABLE_RECORDS.value)
            
            with open(tables_records_path, 'r',  encoding='utf-8') as sql_file:
                query += sql_file.read()
            
            script = self.db.execute(query)
            
            tbl_script = f"-- [{tbl.Schema}].[{tbl.Name}]\n"

            if(len(script) == 0):
                tbl_script += "-- No records found"
            else:
                for row in script:
                    tbl_script += f"{row[0]}\n"
            
            table_records += tbl_script + "\n"
        
        result = f"\n-- TABLE RECORDS:\n" 
        result += "-- --------------------------------------------------------------------------- \n"
        result +=  table_records
        
        return result
    
    def generate_definitions(self, _sp_definitions,_function_definitions,_table_definitions):
        
        _settings = settings()
        path = _settings.get_config_file_path()
        with open(path,'r') as config_file:
            config = json.load(config_file)
        database = config.get("db_config")["database"]

        sp_count = len(_sp_definitions)
        fn_count =  len(_function_definitions)
        tbl_count =  len(_table_definitions)
        items_count = sp_count + fn_count + tbl_count
        result = ""

        definitions = _table_definitions + _sp_definitions + _function_definitions
        
        definitions.sort(key=lambda x: (x[0], x[1]))

        object_sql_list_names = "\n".join(f"-- {sql_type} - {schema}.{name}" for schema, name, _, sql_type in definitions) + "\n"

        result += F"--------------------------------------------------------------------------------------------------------\r"
        result += F"----------------------------------    OPERATION RESULTS   ----------------------------------------------\n"
        result += F"--------------------------------------------------------------------------------------------------------\r"
        result += F"-- Total: {items_count} \r"
        result += F"--   * TABLES: {tbl_count} \r"
        result += F"--   * STORED PROCEDURES: {sp_count} \r"
        result += F"--   * FUNCTIONS: {fn_count} \r"
        result += f"{object_sql_list_names}"
        result += F"--------------------------------------------------------------------------------------------------------\r\n"
        result +=f"USE [{database}]\nGO\n"
        
        for schema,name,script, sql_object_type in definitions:
           result += f"-- /****** Object: {sql_object_type} [{schema}].[{name}] Script Date: {datetime.now()} ******/\n"
           result += "SET ANSI_NULLS ON\nGO\nSET QUOTED_IDENTIFIER ON\nGO\n"
           result += script
        
        return result

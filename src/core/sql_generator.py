from datetime import datetime
import json
import os
from src.models.sql_objects import sql_objects
from src.utils.enumerators import objects_types
from src.sql.connection import sql_class
from pathlib import Path

class sql_generator:
        
    def __init__(self,download_path, clipboard):
        self.download_path = download_path
        self.clipboard = clipboard
        self.db = sql_class()
        self.db.connect()
        
    def download(self,list_sql_objects ): 
        try:
            
            if(not Path(self.download_path).exists()):
                raise Exception("The route provided does not exist")
            
            #definiciones
            _sp_definitions=[]
            _table_definitions=[]
            _function_definitions=[]

            stored_procedures = [item for item in list_sql_objects if item.ClaveObjeto == objects_types.SP.value]
            tables = [item for item in list_sql_objects if item.ClaveObjeto == objects_types.TBL.value]
            functions = [item for item in list_sql_objects if item.ClaveObjeto == objects_types.FN.value]

            if (len(stored_procedures)> 0): 
                _sp_definitions = self.get_sp_definition(stored_procedures)

            if (len(tables)> 0): 
                _table_definitions = self.get_tbl_definition(tables)

            if (len(functions)> 0): 
                _function_definitions = self.get_fn_definitions(functions)

            scripts = self.generate_scripts(_sp_definitions,_function_definitions, _table_definitions)
            
            message = None
            
            #Escribir archivos  
            if(not self.clipboard):
                filename = os.path.join(self.download_path.strip().strip('"'), "Scripts_SQL.sql")
                with open(filename,'w',encoding="utf-8") as file:
                    file.write(scripts)
                message = "File successfully generated"
                return True, message, None
            #Portapapeles
            else:
                message = "Records successfully generated in the clipboard"
                return True, message, scripts
                
        except Exception as ex :
            return False, f"Error: {ex}",None
      
    def get_sp_definition(self, stored_procedures: list[sql_objects]):
        procedures_definition = []

        stored_procedures.sort(key=lambda x: x.Nombre.lower())

        for sp in stored_procedures:
            result = self.db.execute(f"EXEC sp_helptext '{sp.Esquema}.{sp.Nombre}'")
            script = ""
            for row in result:
                script += row[0]

            script = script.replace("\r","")
            procedures_definition.append([sp.Esquema, sp.Nombre, script, sp.TipoObjetoSQL])
            
        return procedures_definition
        
    def get_fn_definitions(self, functions:list[sql_objects]):
        functions_definitions = []
        
        functions.sort(key=lambda x: x.Nombre.lower())
        
        for func in functions:
            query = f"DECLARE @ID_Function INTEGER = {func.ID} "
            with open("src\sql\Consulta_Funciones_SQL.sql", 'r',  encoding='utf-8') as sql_file:
                query += sql_file.read()
                
            result = self.db.execute(query)
            script = ""
            for row in result:
                script += row[0]
            
            script = script.replace("\r","")
            functions_definitions.append([func.Esquema, func.Nombre, script, func.TipoObjetoSQL])
        
        return functions_definitions
      
    def get_tbl_definition(self, tables: list[sql_objects]):
        tables_definitions = []
        
        tables.sort(key=lambda x: x.Nombre.lower())
        
        for tbl in tables:
            query = f"DECLARE @ID_Table INTEGER = {tbl.ID} "
            with open("src\sql\Consulta_Tabla_SQL.sql", 'r',  encoding='utf-8') as sql_file:
                query += sql_file.read()
            
            script = self.db.execute(query)
            
            tbl_script = ""

            for row in script:
                tbl_script += row[0]
            
            tbl_script += "\n"
            
            tables_definitions.append([tbl.Esquema, tbl.Nombre, tbl_script, tbl.TipoObjetoSQL, ])
        
        return tables_definitions
            
    def generate_scripts(self, _sp_definitions,_function_definitions,_table_definitions):
        
        with open('src/config/config.json','r') as config_file:
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

        result += F"----------------------------------    OPERATION RESULTS   ----------------------------------------------\n"
        result += F"--------------------------------------------------------------------------------------------------------\r"
        result += F"-- COUNT: {items_count} \r"
        result += F"--   * TABLES: {tbl_count} \r"
        result += F"--   * STORED PROCEDURES: {sp_count} \r"
        result += F"--   * FUNCTIONS: {fn_count} \r"
        result += f"{object_sql_list_names}"
        result += F"--------------------------------------------------------------------------------------------------------\r\n"
        result +=f"USE [{database}]\nGO\n"
        
        for schema,name,script, sql_object_type in definitions:
        #    result += f"--------------------------------------------------------------------------------------\n"
           result += f"-- /****** Object: {sql_object_type} [{schema}].[{name}] Script Date: {datetime.now()} ******/\n "
        #    result += f"--------------------------------------------------------------------------------------\n"
           result += "SET ANSI_NULLS ON\nGO\nSET QUOTED_IDENTIFIER ON\nGO\n"
           result += script
        
        return result

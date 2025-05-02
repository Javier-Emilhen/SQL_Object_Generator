import os
import uuid
from datetime import datetime
from src.sql.connection import sql_class
from src.models.sql_objects import sql_objects
from src.utils.utils import utils
from src.utils.enumerators import sql_definitions

class sql_search_engine:

    def __init__(self, filter_text, init_date, end_date, object_type, schema ):
        self.filter_text = filter_text
        self.init_date = init_date
        self.end_date = end_date
        self.object_type = object_type
        self.schema = schema
        
        self.db = sql_class()
        self.db.connect()

    def find_sql_objects(self):

        input_params = [
            f"DECLARE @Name AS VARCHAR(MAX) = '{self.filter_text}';\n",
            f"DECLARE @Init_Date AS DATETIME;\n ",
            f"DECLARE @End_Date AS DATETIME;\n",
            f"DECLARE @Object_Key AS varchar(10);\n"
            f"DECLARE @Schema AS varchar(max);\n"
        ]

        if (len(self.filter_text) > 0):
            input_params.append(F"SET @Name = '{self.filter_text}'; \n")
        
        if (len(self.schema) > 0):
            input_params.append(F"SET @Schema = '{self.schema}'; \n")
            
        if (len(self.init_date) > 0):
            date = datetime.strptime(self.init_date, "%d/%m/%Y")
            format_init_date = date.strftime("%Y%m%d")
            input_params.append(F"SET @Init_Date = '{format_init_date}'; \n")

        if (len(self.end_date) > 0):
            date = datetime.strptime(self.end_date, "%d/%m/%Y")
            format_end_date = date.strftime("%Y%m%d")
            input_params.append(F"SET @End_Date = '{format_end_date}'; \n")

        if (not self.object_type == None):
             input_params.append(F"SET @Object_Key = '{self.object_type}'; \n")


        query = "".join(input_params)

        #Leer el archivo donde se aloja la query de consulta
        # path = utils.resource_path('SQL_Objects_Query.sql')
        path = utils.resource_path(sql_definitions.SEARCH_FILE.value)
        with open(path, 'r',  encoding='utf-8') as sql_file:
            query += sql_file.read()
        
        #Guardar la consulta que se generó  
        # _path_generated_querys = f"src\generated_querys\{str(uuid.uuid4()) }.sql"
        # os.makedirs(os.path.dirname(_path_generated_querys), exist_ok=True)
        # with open(_path_generated_querys,'a',encoding="utf-8") as file:
        #     file.write(query)

        results = self.db.execute(query)
        
        # Mapear resultados a instancias de MiClase
        objects = [sql_objects(
                        ID=row._mapping['ID'],
                        Schema=row._mapping['Schema'],
                        Name=row._mapping['Name'],
                        Object_Key=row._mapping["Object_Key"],
                        Sql_Object = row._mapping["Sql_Object"],
                        Creation_Date = row._mapping["Creation_Date"],
                        Modification_Date = row._mapping["Modification_Date"]
                    ) for row in results]
        
        return objects

from datetime import datetime
from src.sql.connection import sql_class
from src.models.sql_objects import sql_objects
from src.utils.utils import utils
from src.utils.enumerators import sql_definitions

class sql_search_engine:

    def __init__(self, filter_text, init_date, end_date, object_type, schema, filter_type ):
        self.filter_text = filter_text
        self.init_date = init_date
        self.end_date = end_date
        self.object_type = object_type
        self.schema = schema
        self.filter_type = filter_type

        self.db = sql_class()
        self.db.connect()

    def find_sql_objects(self):

        # Variables T-SQL declaradas con NULL — ningún input del usuario toca el string de query
        declare_block = (
            "DECLARE @Name AS VARCHAR(MAX) = NULL;\n"
            "DECLARE @Init_Date AS DATETIME = NULL;\n"
            "DECLARE @End_Date AS DATETIME = NULL;\n"
            "DECLARE @Object_Key AS varchar(10) = NULL;\n"
            "DECLARE @Schema AS varchar(max) = NULL;\n"
            "DECLARE @FilterType AS varchar(max) = NULL;\n"
        )

        # Los valores del usuario se pasan como parámetros bind — nunca concatenados al query
        set_statements = []
        params = {}

        if self.filter_text:
            set_statements.append("SET @Name = :filter_text;")
            params["filter_text"] = self.filter_text

        if self.schema:
            set_statements.append("SET @Schema = :schema;")
            params["schema"] = self.schema

        if self.filter_type:
            set_statements.append("SET @FilterType = :filter_type;")
            params["filter_type"] = self.filter_type

        if self.init_date:
            date = datetime.strptime(self.init_date, "%d/%m/%Y")
            params["init_date"] = date.strftime("%Y%m%d")
            set_statements.append("SET @Init_Date = :init_date;")

        if self.end_date:
            date = datetime.strptime(self.end_date, "%d/%m/%Y")
            params["end_date"] = date.strftime("%Y%m%d")
            set_statements.append("SET @End_Date = :end_date;")

        if self.object_type is not None:
            set_statements.append("SET @Object_Key = :object_key;")
            params["object_key"] = self.object_type

        path = utils.resource_path(sql_definitions.SEARCH_FILE.value)
        with open(path, 'r', encoding='utf-8') as sql_file:
            sql_content = sql_file.read()

        query = declare_block + "\n".join(set_statements) + "\n" + sql_content

        results = self.db.execute(query, params)

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

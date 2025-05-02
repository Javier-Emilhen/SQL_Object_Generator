from enum import Enum

class object_types(Enum):
    SP = "Stored Procedures"
    TBL = "Tables"
    FN = "Functions"

class objects_types(Enum):
    SP = "SP"
    TBL = "TBL"
    FN = "F"
    
class sql_definitions(Enum):
    SEARCH_FILE = 'sql_obj_query.sql'
    FUNCTIONS_FILE = 'sql_fn_query.sql'
    TABLES_FILE = 'sql_tables_query.sql'
    SP_FILE = 'EXEC sp_helptext'
    TABLE_RECORDS = 'sql_table_records.sql'
    
class table_get_options(Enum):
    Data_Only = "Data Only"
    Schema_Data = "Schema and Data"
    Schema_Only = "Schema Only"
    # test = "Scddddddddddddddddddddhema Only"
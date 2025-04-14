import pyodbc
from datetime import datetime
from src.utils.Connection import sql_class
from src.utils.Objects import SQL_Objects

_server= ".\MSSQL2016"
_database = "PhiniaMantenimientoAutonomo"
_username="sa"
_password ="Nadabueno#1"
_sql_select_path = "SQL_Scripts\ConsultaUltimosCambios.sql"
_result_path = "Results\CambiosMbComisiones_23092024.sql"

_init_date = datetime(2024,9,2)
_object_type = "SP"


# def get_sql_server_connection():
#         connection = pyodbc.connect(
#         f'DRIVER={{ODBC Driver 17 for SQL Server}};'
#         f'SERVER={_server};'
#         f'DATABASE={_database};'
#         f'UID={_username};'
#         f'PWD={_password}')
                
#         connection.autocommit = False
        
#         return connection
           
def generate_scripts():
    
    input_params = [
        f"DECLARE @Fecha AS DATETIME = '{_init_date}' ; " ,
        f"DECLARE @ClaveObjeto AS VARCHAR(10) = '{_object_type}' ; "   
    ]
    
    query = "".join(input_params)
    
    #Leer el archivo donde se aloja la query de consulta
    with open(_sql_select_path, 'r',  encoding='utf-8') as sql_file:
        query += sql_file.read()
        
    #Guardar la consulta que se generó  
    with open("Generated_Querys\Select_Query.sql",'w') as file:
        file.write(query)
         
    #cursor.execute(script_sql)
    
    sql_conn = sql_class(_server,_database,_username,_password)
    sql_conn.connect()
    
    with sql_conn.engine.connect() as connection:
        
        #Obtener los procedimientos
        results = connection.execute(query)
    
        # Mapear resultados a instancias de MiClase
        instancias = [SQL_Objects(
                        schema=row['Esquema'],
                        name=row['Nombre'],
                        object_key=row["ClaveObjeto"],
                        object_type = row["TipoObjeto"],
                        creation_date = row["FechaCreacion"],
                        modification_date = row["FechaModificacion"]
                    ) for row in results]
    
    for instancia in instancias:
        print(instancia)
    
    #sql_conn.close()
    
    #Inicializar el arreglo de procedimientos
    
    print("Generando Scripts: \n")
    
    functions = {item for item in results if item[2] == "T"}
    
    stored_procedures = {item for item in results if item[2] == "SP"}
    
    tables = [item for item in results if item[2] == "T"]
    
    
    
    
    
def write_stored_procedures(stored_procedures):

    procedures_definition = []
    
    for proc in stored_procedures:
        sp_name = proc[1]
        sp_schema = proc[0]
        
        cursor.execute(f"EXEC sp_helptext {sp_name}")
        sp_text = cursor.fetchall()
    
        print(f"-{sp_schema}.{sp_name}")
        
        sp_script = ""

        for row in sp_text:
            sp_script += row[0]
            
        sp_script = sp_script.replace("\r","")
        procedures_definition.append([sp_schema,sp_name,sp_script])
    
    save_to_file(_result_path, procedures_definition)
    
    
    
def save_to_file(filename, procedures):
    
    print(f"\n Generando archivo SQL")
    print(f"Ruta del archivo: - {filename} \n")
    
    with open(filename,'w') as file:
        file.write("-- Lista de procedimientos SQL Generados\r")
        file.write(F"-- Fecha de generacion: {_init_date} \r")
        file.write(F"-- Cantidad: {len(procedures) } \r\n")

        sp_name_list = ""
        
        for schema,name,script in procedures:
            sp_name_list +=  f"-- {schema}.{name} \n"

        file.write(sp_name_list + "\r\n")
        
        file.write(f"USE [{_database}]\nGO\n")
        
        for schema, name, script in procedures:
            file.write(f"--------------------------------------------------------------------------------------\n")
            file.write(f"-- Stored Procedure Generated: [{schema}].[{name}] \n")
            file.write(f"--------------------------------------------------------------------------------------\n")
            file.write("SET ANSI_NULLS ON\nGO\nSET QUOTED_IDENTIFIER ON\nGO\n")
            file.write(script)
            file.write("\r\n")
            
    print("Archivo generado con exito")

def start_sql_generator():
    try:
        #Generar scripts
        generate_scripts()
    
    except Exception as ex:
      print(f"Error: {ex}")


#Inicio de la aplicación
start_sql_generator()
    
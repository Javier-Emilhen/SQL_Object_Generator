import pyodbc
from datetime import datetime

_server= "CIS00236\MSSQL2019"
_database = "db_9de684_macrobodega"
_username="sa"
_password ="Nadabueno#1"
_function_name = "ObtenerCambios_BaseDatos"
_sql_function_path = "FuncionSQL.txt"

_init_date = datetime(2024,8,28)
_object_type = "SP"

def get_sql_server_connection():
    
    try:
        connection = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={_server};'
        f'DATABASE={_database};'
        f'UID={_username};'
        f'PWD={_password}')
    
       # cursor = connection.cursor()
        
        return connection
        
    except:
      print('An exception occurred')  
    
def verify_table_valued_function(cursor):
    
    try:
        
        function_exists = False
        
        #connection = get_sql_server_connection()
    
        #cursor = connection.cursor()
    
        cursor.execute(f"""
        SELECT
	        SPECIFIC_NAME 
        FROM Information_schema.Routines 
        WHERE Specific_schema = 'dbo' 
	        AND specific_name = '{_function_name}' 
	        AND Routine_Type = 'function'
	        AND ROUTINE_CATALOG = '{_database}'  
        """)
    
        function = cursor.fetchall()

        print(function)
        
        if len(function) > 0:
            function_exists = True
                    
        return function_exists
        
    except Exception as ex:
      print(F'Error: {ex}')
    #finally:
        # cursor.close()
        # connection.close()

def create_table_valued_function(connection):
     
    try:
        
        print("Creando funcion para consultar los ultimos cambios")        
        
        #Obtener el archivo con la funcion SQL para los ultimos cambios
        with open(_sql_function_path, 'r',  encoding='utf-16') as sql_file:
            script_sql = sql_file.read()
        
        #print (script_sql)
        cursor = connection.cursor()
    
        cursor.execute(script_sql)
        connection.commit()
        
        print("Funcion creada correctamente")
    
    except Exception as ex:
        print(f"Error al ejecutar el script: {ex}")
        connection.rollback()  # Revertir los cambios si hay un error
       
def generate_scripts(cursor):
         
    cursor.execute(f"""
        select Nombre
        from [dbo].[{_function_name}]('{_init_date}', '{_object_type}') 
        ORDER BY Nombre DESC
    """)
    
    stored_procedures = cursor.fetchall()
    
    procedures_definition = []
    
    print("Generando procedimientos almacenados: \n")
    
    for proc in stored_procedures:
        sp_name = proc[0]
        cursor.execute(f"EXEC sp_helptext {sp_name}")
        sp_text = cursor.fetchall()
    
        print(f"- {sp_name}")
        
        sp_script = ""

        for row in sp_text:
            sp_script += row[0]
            
        procedures_definition.append([sp_name,sp_script])

    # cursor.close()
    
    save_to_file("Procedimientos.sql", procedures_definition)
    
def save_to_file(filename, procedures):
    
    print(f"Generando archivo SQL")
    print(f"Ruta del archivo: - {filename} \n")
    
    with open(filename,'w') as file:
        
        file.write(f"USE [{_database}] \n GO \n")
        
        for name, script in procedures:
            file.write(f"-- Stored Procedure: {name} \n")
            file.write("SET ANSI_NULLS ON \n GO \n SET QUOTED_IDENTIFIER ON \n GO \n")
            file.write(script)

def start_sql_generator():

    #Creando la conexión a SQL Server
    connection = get_sql_server_connection()
    
    cursor = connection.cursor()

    function_exist = verify_table_valued_function(cursor)
    
    #Si no existe la funcion, crearla
    if not function_exist:
        create_table_valued_function(connection)
    
    #Generar scripts
    generate_scripts(cursor)

    cursor.close()
    connection.close()



#Inicio de la aplicación
start_sql_generator()
    
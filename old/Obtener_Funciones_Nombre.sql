-- --DECLARE @FunctionName NVARCHAR(255) = 'Funcion_AreasAVisualizar' 
-- DECLARE @SchemaName NVARCHAR(255)
-- DECLARE @SQL NVARCHAR(MAX)

-- -- Obtener el esquema de la función
-- SELECT @SchemaName = s.name
-- FROM sys.objects o
-- INNER JOIN sys.schemas s ON o.schema_id = s.schema_id
-- WHERE o.name = @FunctionName AND o.type IN ('FN', 'IF', 'TF')

-- -- Validar si la función existe
-- IF @SchemaName IS NULL
-- BEGIN
--     PRINT 'ERROR: La función ' + @FunctionName + ' no existe.'
--     RETURN
-- END

-- -- Obtener el cuerpo de la función (definición SQL)
-- SELECT @SQL = sm.definition
-- FROM sys.sql_modules sm
-- INNER JOIN sys.objects o ON sm.object_id = o.object_id
-- WHERE o.name = @FunctionName AND o.type IN ('FN', 'IF', 'TF')  -- FN: Escalar, IF: Tabular, TF: Tabular

-- -- Mostrar el script generado
-- select  @SQL as Definicion

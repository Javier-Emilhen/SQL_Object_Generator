--DECLARE @ID_Function integer = 1419152101
DECLARE @SchemaName NVARCHAR(255)
DECLARE @SQL NVARCHAR(MAX)

SELECT @SQL = sm.definition
FROM sys.sql_modules sm
INNER JOIN sys.objects o ON sm.object_id = o.object_id
WHERE o.object_id = @ID_Function 
AND o.type IN ('FN', 'IF', 'TF')

select  @SQL as Definicion
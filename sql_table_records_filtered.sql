-- Declared from Python before this block:
-- DECLARE @Schema_Name AS NVARCHAR(128) = N'...'
-- DECLARE @Table_Name  AS NVARCHAR(128) = N'...'
-- DECLARE @Where_Clause AS NVARCHAR(MAX) = N'...'  -- or NULL

DECLARE @ID_Table AS INT

SELECT @ID_Table = so.object_id
FROM sys.objects so
JOIN sys.schemas sc ON sc.schema_id = so.schema_id
WHERE so.type = 'U'
  AND so.name = @Table_Name
  AND sc.name = @Schema_Name

IF @ID_Table IS NULL
BEGIN
    RAISERROR('Table [%s].[%s] not found in the database.', 16, 1, @Schema_Name, @Table_Name)
    RETURN
END

declare @sql as varchar(max) = ''
select @sql = 'SELECT ''INSERT INTO ' + '['+schema_name(ta.schema_id)+']' + '.' + '['+so.name+']' + '(' + substring(o.list, 1, len(o.list)-1) + ')VALUES('
+ substring(val.list, 1, len(val.list)-1) + ');''  FROM ' + schema_name(ta.schema_id) + '.' + so.name
+ CASE
    WHEN @Where_Clause IS NOT NULL AND LTRIM(RTRIM(@Where_Clause)) <> ''
    THEN ' WHERE ' + @Where_Clause
    ELSE ''
  END
+ ';'
from    sys.objects so
join sys.tables ta on ta.object_id=so.object_id
cross apply
(SELECT '[' +column_name + '],'
 from information_schema.columns c
 join syscolumns co on co.name=c.COLUMN_NAME and object_name(co.id)=so.name and OBJECT_NAME(co.id)=c.TABLE_NAME and co.id=so.object_id and c.TABLE_SCHEMA=SCHEMA_NAME(so.schema_id)
 where table_name = so.name
 order by ordinal_position
FOR XML PATH('')) o (list)
cross apply
(SELECT '''+' +case
         when data_type = 'uniqueidentifier' THEN 'CASE WHEN [' + column_name+'] IS NULL THEN ''NULL'' ELSE ''''''''+CONVERT(NVARCHAR(MAX),[' + COLUMN_NAME + '])+'''''''' END '
         WHEN data_type = 'timestamp' then '''''''''+CONVERT(NVARCHAR(MAX),CONVERT(BINARY(8),[' + COLUMN_NAME + ']),1)+'''''''''
         WHEN data_type = 'nvarchar' then 'CASE WHEN [' + column_name+'] IS NULL THEN ''NULL'' ELSE ''''''''+REPLACE([' + COLUMN_NAME + '],'''''''','''''''''''')+'''''''' END'
         WHEN data_type = 'varchar' then 'CASE WHEN [' + column_name+'] IS NULL THEN ''NULL'' ELSE ''''''''+REPLACE([' + COLUMN_NAME + '],'''''''','''''''''''')+'''''''' END'
         WHEN data_type = 'char' then 'CASE WHEN [' + column_name+'] IS NULL THEN ''NULL'' ELSE ''''''''+REPLACE([' + COLUMN_NAME + '],'''''''','''''''''''')+'''''''' END'
         WHEN data_type = 'nchar' then 'CASE WHEN [' + column_name+'] IS NULL THEN ''NULL'' ELSE ''''''''+REPLACE([' + COLUMN_NAME + '],'''''''','''''''''''')+'''''''' END'
         when DATA_TYPE='datetime' then 'CASE WHEN [' + column_name+'] IS NULL THEN ''NULL'' ELSE ''''''''+CONVERT(NVARCHAR(MAX),[' + COLUMN_NAME + '],121)+'''''''' END '
         when DATA_TYPE='datetime2' then 'CASE WHEN [' + column_name+'] IS NULL THEN ''NULL'' ELSE ''''''''+CONVERT(NVARCHAR(MAX),[' + COLUMN_NAME + '],121)+'''''''' END '
         when DATA_TYPE='date' then 'CASE WHEN [' + column_name+'] IS NULL THEN ''NULL'' ELSE ''''''''+CONVERT(NVARCHAR(MAX),[' + COLUMN_NAME + '],121)+'''''''' END '
         when DATA_TYPE='datetimeoffset' then 'CASE WHEN [' + column_name+'] IS NULL THEN ''NULL'' ELSE ''''''''+CONVERT(NVARCHAR(MAX),[' + COLUMN_NAME + '],121)+'''''''' END '
         when DATA_TYPE='geography' and column_name<>'Shape' then 'ST_GeomFromText(''POINT('+column_name+'.Lat '+column_name+'.Long)'') '
         when DATA_TYPE='geography' and column_name='Shape' then '''''''''+CONVERT(NVARCHAR(MAX),[' + COLUMN_NAME + '])+'''''''''
         when DATA_TYPE='xml' then 'CASE WHEN [' + column_name+'] IS NULL THEN ''NULL'' ELSE ''''''''+REPLACE(CONVERT(NVARCHAR(MAX),[' + COLUMN_NAME + ']),'''''''','''''''''''')+'''''''' END '
         when DATA_TYPE='text' then 'CASE WHEN [' + column_name+'] IS NULL THEN ''NULL'' ELSE ''''''''+REPLACE(CONVERT(NVARCHAR(MAX),[' + COLUMN_NAME + ']),'''''''','''''''''''')+'''''''' END '
         WHEN DATA_TYPE='image' then 'CASE WHEN [' + column_name+'] IS NULL THEN ''NULL'' ELSE ''''''''+CONVERT(NVARCHAR(MAX),CONVERT(VARBINARY(MAX),[' + COLUMN_NAME + ']),1)+'''''''' END '
         WHEN DATA_TYPE = 'varbinary' THEN 'CASE WHEN [' + column_name + '] IS NULL THEN ''NULL'' ELSE ''0x'' + LOWER(CONVERT(VARCHAR(MAX), [' + column_name + '], 2)) END'
         WHEN DATA_TYPE='binary' then 'CASE WHEN [' + column_name+'] IS NULL THEN ''NULL'' ELSE ''''''''+CONVERT(NVARCHAR(MAX),[' + COLUMN_NAME + '],1)+'''''''' END '
         when DATA_TYPE='time' then 'CASE WHEN [' + column_name+'] IS NULL THEN ''NULL'' ELSE ''''''''+CONVERT(NVARCHAR(MAX),[' + COLUMN_NAME + '])+'''''''' END '
         ELSE 'CASE WHEN [' + column_name+'] IS NULL THEN ''NULL'' ELSE CONVERT(NVARCHAR(MAX),['+column_name+']) END' end
   + '+'','
 from information_schema.columns c
 join syscolumns co on co.name=c.COLUMN_NAME and object_name(co.id)=so.name and OBJECT_NAME(co.id)=c.TABLE_NAME and co.id=so.object_id and c.TABLE_SCHEMA=SCHEMA_NAME(so.schema_id)
 where table_name = so.name
 order by ordinal_position
FOR XML PATH('')) val (list)
where   so.type = 'U'
and so.object_id = @ID_Table

exec( @sql)

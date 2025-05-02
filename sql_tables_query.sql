--DECLARE @ID_Table INTEGER =1974298093

DECLARE @object_name SYSNAME, @object_id INT
DECLARE @SQL NVARCHAR(MAX) = ''

SELECT 
      @object_name = '[' + s.name + '].[' + o.name + ']',
      @object_id = o.[object_id]
FROM sys.objects o WITH (NOWAIT)
JOIN sys.schemas s WITH (NOWAIT) ON o.[schema_id] = s.[schema_id]
--WHERE s.name + '.' + o.name = @table_name
WHERE O.object_id = @ID_Table
    AND o.[type] = 'U'
    AND o.is_ms_shipped = 0

;WITH index_column AS 
(
    SELECT 
          ic.[object_id]
        , ic.index_id
        , ic.is_descending_key
        , ic.is_included_column
        , c.name
    FROM sys.index_columns ic WITH (NOWAIT)
    JOIN sys.columns c WITH (NOWAIT) ON ic.[object_id] = c.[object_id] AND ic.column_id = c.column_id
    WHERE ic.[object_id] = @object_id
),
fk_columns AS 
(
     SELECT 
          k.constraint_object_id
        , cname = c.name
        , rcname = rc.name
    FROM sys.foreign_key_columns k WITH (NOWAIT)
    JOIN sys.columns rc WITH (NOWAIT) ON rc.[object_id] = k.referenced_object_id AND rc.column_id = k.referenced_column_id 
    JOIN sys.columns c WITH (NOWAIT) ON c.[object_id] = k.parent_object_id AND c.column_id = k.parent_column_id
    WHERE k.parent_object_id = @object_id
)
SELECT @SQL = 'CREATE TABLE ' + @object_name +'(' + CHAR(10) + STUFF((
    SELECT ' ,[' + c.name + '] ' + 
        CASE WHEN c.is_computed = 1
            THEN 'AS ' + cc.[definition] 
            ELSE UPPER(tp.name) + 
                CASE WHEN tp.name IN ('varchar', 'char', 'varbinary', 'binary', 'text')
                       THEN '(' + CASE WHEN c.max_length = -1 THEN 'MAX' ELSE CAST(c.max_length AS VARCHAR(5)) END + ')'
                     WHEN tp.name IN ('nvarchar', 'nchar', 'ntext')
                       THEN '(' + CASE WHEN c.max_length = -1 THEN 'MAX' ELSE CAST(c.max_length / 2 AS VARCHAR(5)) END + ')'
                     WHEN tp.name IN ('datetime2', 'time2', 'datetimeoffset') 
                       THEN '(' + CAST(c.scale AS VARCHAR(5)) + ')'
                    WHEN tp.name IN ('decimal', 'numeric')
                       THEN '(' + CAST(c.[precision] AS VARCHAR(5)) + ',' + CAST(c.scale AS VARCHAR(5)) + ')'
                    ELSE ''
                END +
                --CASE WHEN c.collation_name IS NOT NULL THEN ' COLLATE ' + c.collation_name ELSE '' END +
                CASE WHEN c.is_nullable = 1 THEN ' NULL' ELSE ' NOT NULL' END +
                CASE WHEN dc.[definition] IS NOT NULL THEN ' DEFAULT' + dc.[definition] ELSE '' END + 
                CASE WHEN ic.is_identity = 1 THEN ' IDENTITY(' + CAST(ISNULL(ic.seed_value, '0') AS CHAR(1)) + ',' + CAST(ISNULL(ic.increment_value, '1') AS CHAR(1)) + ')' ELSE '' END 
        END + CHAR(13)
    FROM sys.columns c WITH (NOWAIT)
		JOIN sys.types tp WITH (NOWAIT) ON c.user_type_id = tp.user_type_id
		LEFT JOIN sys.computed_columns cc WITH (NOWAIT) ON c.[object_id] = cc.[object_id] AND c.column_id = cc.column_id
		LEFT JOIN sys.default_constraints dc WITH (NOWAIT) ON c.default_object_id != 0 AND c.[object_id] = dc.parent_object_id AND c.column_id = dc.parent_column_id
		LEFT JOIN sys.identity_columns ic WITH (NOWAIT) ON c.is_identity = 1 AND c.[object_id] = ic.[object_id] AND c.column_id = ic.column_id
    WHERE c.[object_id] = @object_id
    ORDER BY c.column_id
    FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)'), 1, 2, CHAR(9) + ' ')
    + ISNULL((SELECT ',CONSTRAINT [' + k.name + '] PRIMARY KEY ' +
            CASE WHEN i.[type_desc] IS NOT NULL THEN ' ' + i.[type_desc] ELSE '' END + ' (' +
                (SELECT STUFF((
                     SELECT ', [' + c.name + '] ' + CASE WHEN ic.is_descending_key = 1 THEN 'DESC' ELSE 'ASC' END
                     FROM sys.index_columns ic WITH (NOWAIT)
                     JOIN sys.columns c WITH (NOWAIT) ON c.[object_id] = ic.[object_id] AND c.column_id = ic.column_id
                     WHERE ic.is_included_column = 0
                         AND ic.[object_id] = k.parent_object_id 
                         AND ic.index_id = k.unique_index_id     
                     FOR XML PATH(N''), TYPE).value('.', 'NVARCHAR(MAX)'), 1, 2, ''))
        + ')' + CHAR(13) +
        '        WITH (' +
            'PAD_INDEX = ' + UPPER(CASE WHEN i.is_padded = 1 THEN 'ON' ELSE 'OFF' END) + ', ' +
            'STATISTICS_NORECOMPUTE = ' + UPPER(CASE WHEN st.no_recompute = 1 THEN 'ON' ELSE 'OFF' END)+', ' +
            'IGNORE_DUP_KEY = ' + UPPER(CASE WHEN i.ignore_dup_key = 1 THEN 'ON' ELSE 'OFF' END) + ', ' +
            'ALLOW_ROW_LOCKS = ' + UPPER(CASE WHEN i.allow_row_locks = 1 THEN 'ON' ELSE 'OFF' END) + ', ' +
            'ALLOW_PAGE_LOCKS = ' + UPPER(CASE WHEN i.allow_page_locks = 1 THEN 'ON' ELSE 'OFF' END) + ', ' +
            'FILLFACTOR = ' + CAST(i.fill_factor AS VARCHAR) + ', ' +
            'OPTIMIZE_FOR_SEQUENTIAL_KEY = ' + UPPER(CASE WHEN i.optimize_for_sequential_key = 1 THEN 'ON' ELSE 'OFF' END) +
        ') ON [' + ds.name + ']' + CHAR(13) + ')' + 'ON [' + ds.name + ']'
 FROM sys.key_constraints k
	JOIN sys.indexes i ON i.object_id = k.parent_object_id AND i.index_id = k.unique_index_id
	JOIN sys.data_spaces ds ON ds.data_space_id = i.data_space_id
	JOIN sys.stats st ON st.object_id = i.object_id AND st.stats_id = i.index_id
 WHERE k.parent_object_id = @object_id 
     AND k.[type] = 'PK'), '')
    + ISNULL((SELECT (
        SELECT CHAR(10) + 'GO' + CHAR(10)+
             'ALTER TABLE ' + @object_name + ' WITH' 
            + CASE WHEN fk.is_not_trusted = 1 
                THEN ' NOCHECK' 
                ELSE ' CHECK' 
              END + 
              ' ADD CONSTRAINT [' + fk.name  + '] FOREIGN KEY(' 
              + STUFF((
                SELECT ', [' + k.cname + ']'
                FROM fk_columns k
                WHERE k.constraint_object_id = fk.[object_id]
                FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)'), 1, 2, '')
               + ')' +
              ' REFERENCES [' + SCHEMA_NAME(ro.[schema_id]) + '].[' + ro.name + '] ('
              + STUFF((
                SELECT ', [' + k.rcname + ']'
                FROM fk_columns k
                WHERE k.constraint_object_id = fk.[object_id]
                FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)'), 1, 2, '')
               + ')'
            + CASE 
                WHEN fk.delete_referential_action = 1 THEN ' ON DELETE CASCADE' 
                WHEN fk.delete_referential_action = 2 THEN ' ON DELETE SET NULL'
                WHEN fk.delete_referential_action = 3 THEN ' ON DELETE SET DEFAULT' 
                ELSE '' 
              END
            + CASE 
                WHEN fk.update_referential_action = 1 THEN ' ON UPDATE CASCADE'
                WHEN fk.update_referential_action = 2 THEN ' ON UPDATE SET NULL'
                WHEN fk.update_referential_action = 3 THEN ' ON UPDATE SET DEFAULT'  
                ELSE '' 
              END 
            + CHAR(13) + 'ALTER TABLE ' + @object_name + ' CHECK CONSTRAINT [' + fk.name  + ']' + CHAR(13)
        FROM sys.foreign_keys fk WITH (NOWAIT)
			JOIN sys.objects ro WITH (NOWAIT) ON ro.[object_id] = fk.referenced_object_id
        WHERE fk.parent_object_id = @object_id
		ORDER by ro.object_id DESC
        FOR XML PATH(N''), TYPE).value('.', 'NVARCHAR(MAX)')), '')
    + ISNULL(((SELECT
         CHAR(13) + 'CREATE' + CASE WHEN i.is_unique = 1 THEN ' UNIQUE' ELSE '' END 
                + ' NONCLUSTERED INDEX [' + i.name + '] ON ' + @object_name + ' (' +
                STUFF((
                SELECT ', [' + c.name + ']' + CASE WHEN c.is_descending_key = 1 THEN ' DESC' ELSE ' ASC' END
                FROM index_column c
                WHERE c.is_included_column = 0
                    AND c.index_id = i.index_id
                FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)'), 1, 2, '') + ')'  
                + ISNULL(CHAR(13) + 'INCLUDE (' + 
                    STUFF((
                    SELECT ', [' + c.name + ']'
                    FROM index_column c
                    WHERE c.is_included_column = 1
                        AND c.index_id = i.index_id
                    FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)'), 1, 2, '') + ')', '') + CASE WHEN ISNULL(i.filter_definition,'') = '' THEN '' ELSE ' WHERE ' + i.filter_definition END + CHAR(13)
        FROM sys.indexes i WITH (NOWAIT)
        WHERE i.[object_id] = @object_id
            AND i.is_primary_key = 0
            AND i.[type] = 2
        FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)')
    ), '')

SELECT CAST(@SQL AS NTEXT)
--PRINT CAST(@SQL AS NTEXT)


-- Original code obtained from 
-- https://stackoverflow.com/questions/706664/generate-sql-create-scripts-for-existing-tables-with-query
-- Script written by Devart
-- https://stackoverflow.com/users/135566/devart
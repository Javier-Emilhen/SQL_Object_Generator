SET NOCOUNT ON;
DECLARE @Result AS TABLE(
	Esquema varchar(100),
	Nombre varchar(100),
	TipoObjetoSQL varchar(50),
	ClaveObjeto varchar(50),
	FechaCreacion datetime,
	FechaModificacion datetime NULL
);

--Obtener Tablas 
INSERT INTO @Result(
	Esquema,
	Nombre,
	TipoObjetoSQL,
	ClaveObjeto,
	FechaCreacion,
	FechaModificacion
)
SELECT
	SCHEMA_NAME(schema_id),
	name,
	type_desc,
	'T',
	create_date,
	modify_date
FROM sys.tables
WHERE (@Fecha IS NULL)
	OR (modify_date >= @Fecha)
	AND (@ClaveObjeto IS NULL OR @ClaveObjeto = 'T')
ORDER BY name

-- Obtener Procedimientos Almacendos
INSERT INTO @Result(
	Esquema,
	Nombre,
	TipoObjetoSQL,
	ClaveObjeto,
	FechaCreacion,
	FechaModificacion
)
SELECT 
	SCHEMA_NAME(schema_id),
	name, 
	type_desc,
	'SP',
	create_date,
	modify_date
FROM sys.procedures P
	JOIN sys.sql_modules AS M ON P.object_id = M.object_id  
WHERE (@Fecha IS NULL)
	OR (modify_date >= @Fecha)
	AND (@ClaveObjeto IS NULL OR @ClaveObjeto = 'SP')
ORDER BY name

-- Obtener Funciones
INSERT INTO @Result(
	Esquema,
	Nombre,
	TipoObjetoSQL,
	ClaveObjeto,
	FechaCreacion,
	FechaModificacion
)
SELECT 
	SCHEMA_NAME(schema_id),
	name, 
	type_desc,
	'F',
	create_date,
	modify_date
FROM sys.objects F
	JOIN sys.sql_modules AS M ON F.object_id = M.object_id  
WHERE (@Fecha IS NULL)
	OR (modify_date >= @Fecha)
	AND (F.type IN ('FN', 'IF', 'TF'))
	AND (@ClaveObjeto IS NULL OR (@ClaveObjeto = 'F') )
ORDER BY name

SELECT
	Esquema,
	Nombre,
	ClaveObjeto,
	TipoObjetoSQL,
	FechaCreacion,
	FechaModificacion
FROM @Result
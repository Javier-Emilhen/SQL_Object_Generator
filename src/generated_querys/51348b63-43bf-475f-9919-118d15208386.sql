DECLARE @Filtro AS VARCHAR(MAX) = '';
DECLARE @Fecha_Inicio AS DATETIME;
 DECLARE @Fecha_Fin AS DATETIME;
DECLARE @ClaveObjeto AS varchar(10);
DECLARE @Esquema AS varchar(max);
SET @Fecha_Inicio = '20250408'; 
SET @ClaveObjeto = 'SP;TBL;FN'; 

--   DECLARE @Fecha_Inicio AS DATETIME
--   DECLARE @Fecha_Fin AS DATETIME 
--   DECLARE @ClaveObjeto AS VARCHAR(10) = 'SP;TBL;FN'
--   DECLARE @Filtro as varchar(max) 
--   DECLARE @Esquema as varchar(max) 

-- Validaciones de campos
IF (LEN(@ClaveObjeto) = 0 ) SET @ClaveObjeto = NULL 
IF (LEN(@Filtro) = 0 ) SET @Filtro = NULL 
IF (@Fecha_Fin is not null) SET @Fecha_Fin = DATEADD(MINUTE, -1, DATEADD(DAY, 1, @Fecha_Fin)) 

SET NOCOUNT ON;

DECLARE @Result AS TABLE(
	ID integer,
	Esquema varchar(100),
	Nombre varchar(100),
	TipoObjetoSQL varchar(50),
	ClaveObjeto varchar(50),
	FechaCreacion datetime,
	FechaModificacion datetime NULL
);

--Obtener Tablas 
INSERT INTO @Result(
	ID,
	Esquema,
	Nombre,
	TipoObjetoSQL,
	ClaveObjeto,
	FechaCreacion,
	FechaModificacion
)
SELECT
	OBJECT_ID,
	SCHEMA_NAME(schema_id),
	name,
	type_desc,
	'TBL',
	create_date,
	modify_date
FROM sys.tables
WHERE ( -- Filtro de fechas
		(@Fecha_Inicio is null and @Fecha_Fin is null) -- Todos
		 OR (modify_date >= @Fecha_Inicio and modify_date <= @Fecha_Fin) -- Ambas fechas
		 OR (@Fecha_Fin IS NULL AND modify_date >= @Fecha_Inicio) -- Solo fecha fin
		 OR (@Fecha_Inicio IS NULL AND modify_date <= @Fecha_Fin) -- Solo fecha inicio
	)
	AND (@ClaveObjeto IS NULL OR @ClaveObjeto LIKE '%TBL%')
	AND (@Filtro is null OR name like '%' + @Filtro + '%')
	AND (@Esquema IS NULL OR SCHEMA_NAME(schema_id) like '%' + @Esquema + '%')
ORDER BY name

-- Obtener Procedimientos Almacendos
INSERT INTO @Result(
	ID,
	Esquema,
	Nombre,
	TipoObjetoSQL,
	ClaveObjeto,
	FechaCreacion,
	FechaModificacion
)
SELECT 
	P.OBJECT_ID,
	SCHEMA_NAME(schema_id),
	name, 
	type_desc,
	'SP',
	create_date,
	modify_date
FROM sys.procedures P
	JOIN sys.sql_modules AS M ON P.object_id = M.object_id  
WHERE ( -- Filtro de fechas
		(@Fecha_Inicio is null and @Fecha_Fin is null) -- Todos
		 OR (modify_date >= @Fecha_Inicio and modify_date <= @Fecha_Fin) -- Ambas fechas
		 OR (@Fecha_Fin IS NULL AND modify_date >= @Fecha_Inicio) -- Solo fecha fin
		 OR (@Fecha_Inicio IS NULL AND modify_date <= @Fecha_Fin) -- Solo fecha inicio
	)
	AND (@ClaveObjeto IS NULL OR @ClaveObjeto LIKE '%SP%')
	AND (@Filtro is null OR name like '%' + @Filtro + '%')
	AND (@Esquema IS NULL OR SCHEMA_NAME(schema_id) like '%' + @Esquema + '%')
ORDER BY name

-- Obtener Funciones
INSERT INTO @Result(
	ID,
	Esquema,
	Nombre,
	TipoObjetoSQL,
	ClaveObjeto,
	FechaCreacion,
	FechaModificacion
)
SELECT 
	F.OBJECT_ID,
	SCHEMA_NAME(schema_id),
	name, 
	type_desc,
	'F',
	create_date,
	modify_date
FROM sys.objects F
	JOIN sys.sql_modules AS M ON F.object_id = M.object_id  
WHERE ( -- Filtro de fechas
		(@Fecha_Inicio is null and @Fecha_Fin is null) -- Todos
		 OR (modify_date >= @Fecha_Inicio and modify_date <= @Fecha_Fin) -- Ambas fechas
		 OR (@Fecha_Fin IS NULL AND modify_date >= @Fecha_Inicio) -- Solo fecha fin
		 OR (@Fecha_Inicio IS NULL AND modify_date <= @Fecha_Fin) -- Solo fecha inicio
	)
	AND (F.type IN ('FN', 'IF', 'TF'))
	AND (@ClaveObjeto IS NULL OR @ClaveObjeto LIKE '%FN%')
	AND (@Filtro is null OR name like '%' + @Filtro + '%')
	AND (@Esquema IS NULL OR SCHEMA_NAME(schema_id) like '%' + @Esquema + '%')
ORDER BY name

SELECT
	ID,
	Esquema,
	Nombre,
	ClaveObjeto,
	TipoObjetoSQL,
	FechaCreacion,
	FechaModificacion
FROM @Result
ORDER BY Esquema, Nombre ASC
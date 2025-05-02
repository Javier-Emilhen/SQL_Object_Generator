
   --DECLARE @Init_Date AS DATETIME
   --DECLARE @End_Date AS DATETIME 
   --DECLARE @Object_Key AS VARCHAR(10) = 'SP;TBL;FN'
   --DECLARE @Name as varchar(max) 
   --DECLARE @Schema as varchar(max) 

-- Validaciones de campos
IF (LEN(@Object_Key) = 0 ) SET @Object_Key = NULL 
IF (LEN(@Name) = 0 ) SET @Name = NULL 
IF (@End_Date is not null) SET @End_Date = DATEADD(MINUTE, -1, DATEADD(DAY, 1, @End_Date)) 

SET NOCOUNT ON;

DECLARE @Result AS TABLE(
	ID					integer,
	Schema_				varchar(100),
	Name_				varchar(100),
	Sql_Object			varchar(50),
	Object_Key			varchar(50),
	Creation_Date		datetime,
	Modification_Date	datetime NULL
);

--Obtener Tablas 
INSERT INTO @Result
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
		(@Init_Date is null and @End_Date is null) -- Todos
		 OR (modify_date >= @Init_Date and modify_date <= @End_Date) -- Ambas fechas
		 OR (@End_Date IS NULL AND modify_date >= @Init_Date) -- Solo fecha fin
		 OR (@Init_Date IS NULL AND modify_date <= @End_Date) -- Solo fecha inicio
	)
	AND (@Object_Key IS NULL OR @Object_Key LIKE '%TBL%')
	AND (@Name is null OR name like '%' + @Name + '%')
	AND (@Schema IS NULL OR SCHEMA_NAME(schema_id) like '%' + @Schema + '%')
ORDER BY name

-- Obtener Procedimientos Almacendos
INSERT INTO @Result
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
		(@Init_Date is null and @End_Date is null) -- Todos
		 OR (modify_date >= @Init_Date and modify_date <= @End_Date) -- Ambas fechas
		 OR (@End_Date IS NULL AND modify_date >= @Init_Date) -- Solo fecha fin
		 OR (@Init_Date IS NULL AND modify_date <= @End_Date) -- Solo fecha inicio
	)
	AND (@Object_Key IS NULL OR @Object_Key LIKE '%SP%')
	AND (@Name is null OR name like '%' + @Name + '%')
	AND (@Schema IS NULL OR SCHEMA_NAME(schema_id) like '%' + @Schema + '%')
ORDER BY name

-- Obtener Funciones
INSERT INTO @Result
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
		(@Init_Date is null and @End_Date is null) -- Todos
		 OR (modify_date >= @Init_Date and modify_date <= @End_Date) -- Ambas fechas
		 OR (@End_Date IS NULL AND modify_date >= @Init_Date) -- Solo fecha fin
		 OR (@Init_Date IS NULL AND modify_date <= @End_Date) -- Solo fecha inicio
	)
	AND (F.type IN ('FN', 'IF', 'TF'))
	AND (@Object_Key IS NULL OR @Object_Key LIKE '%FN%')
	AND (@Name is null OR name like '%' + @Name + '%')
	AND (@Schema IS NULL OR SCHEMA_NAME(schema_id) like '%' + @Schema + '%')
ORDER BY name

SELECT
	ID,
	Schema_ as 'Schema',
	Name_ as 'Name',
	Sql_Object,
	Object_Key,
	Creation_Date,
	Modification_Date
FROM @Result
ORDER BY Schema_, Name_ ASC
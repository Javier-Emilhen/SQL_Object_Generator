--USE [db_9de684_macrobodega]
--GO
/****** Object:  UserDefinedFunction [dbo].[ObtenerCambios_BaseDatos]    Script Date: 12/09/2024 03:31:58 p. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE FUNCTION [dbo].[ObtenerCambios_BaseDatos]
(	
	@Fecha AS DATETIME = NULL,
	@TipoObjeto AS VARCHAR(10) = NULL
)
RETURNS @Result TABLE(
		Nombre varchar(100),
		TipoObjeto varchar(50),
		FechaCreacion datetime,
		FechaModificacion datetime NULL
)
AS
BEGIN
		-- Test
		--select * from [dbo].[ObtenerCambios_BaseDatos]('2024-08-28 00:00:00:000', NULL) ORDER BY Nombre DESC

		--Obtener Tablas 
		INSERT INTO @Result(
			Nombre,
			TipoObjeto,
			FechaCreacion,
			FechaModificacion
		)
		SELECT
			name,
			type_desc,
			create_date,
			modify_date
		FROM sys.tables
		WHERE (@Fecha IS NULL)
			OR (modify_date >= @Fecha)
			AND (@TipoObjeto IS NULL OR @TipoObjeto = 'T')
		ORDER BY name

		-- Obtener Procedimientos Almacendos
		INSERT INTO @Result(
			Nombre,
			TipoObjeto,
			FechaCreacion,
			FechaModificacion
		)
		SELECT 
			name, 
			type_desc,
			create_date,
			modify_date
		FROM sys.procedures P
			JOIN sys.sql_modules AS M ON P.object_id = M.object_id  
		WHERE (@Fecha IS NULL)
			OR (modify_date >= @Fecha)
			AND (@TipoObjeto IS NULL OR @TipoObjeto = 'SP')
		ORDER BY name

	RETURN

END
-- =====================================================
-- SCRIPT DE DIAGNÓSTICO PARA VISTAS
-- =====================================================

USE GAMLO_Empleados;
GO

-- Verificar si las vistas existen
SELECT 
    name as view_name,
    create_date,
    modify_date
FROM sys.views 
WHERE name IN ('vw_required_apps', 'vw_current_access', 'vw_to_grant', 'vw_to_revoke', 'vw_system_stats')
ORDER BY name;
GO

-- Verificar las columnas de las tablas base
SELECT 
    'headcount' as table_name,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'headcount'
ORDER BY ORDINAL_POSITION;
GO

SELECT 
    'applications' as table_name,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'applications'
ORDER BY ORDINAL_POSITION;
GO

SELECT 
    'historico' as table_name,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'historico'
ORDER BY ORDINAL_POSITION;
GO

-- Intentar crear las vistas una por una para identificar el problema
PRINT 'Intentando crear vw_required_apps...';
GO

-- Verificar si vw_required_apps se puede crear
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_required_apps')
    DROP VIEW [dbo].[vw_required_apps];
GO

CREATE VIEW [dbo].[vw_required_apps] AS
SELECT 
    h.scotia_id,
    h.unit,
    h.unidad_subunidad,
    h.position,
    a.logical_access_name,
    a.subunit,
    a.position_role,
    a.role_name,
    a.system_owner,
    a.access_type,
    a.category,
    a.description
FROM [dbo].[headcount] h
INNER JOIN (
    SELECT DISTINCT
        logical_access_name,
        unit,
        unidad_subunidad,
        position_role,
        subunit,
        role_name,
        system_owner,
        access_type,
        category,
        description
    FROM [dbo].[applications]
    WHERE access_status = 'Activo'
) a ON 
    UPPER(LTRIM(RTRIM(h.unidad_subunidad))) = UPPER(LTRIM(RTRIM(a.unidad_subunidad))) AND
    UPPER(LTRIM(RTRIM(h.position))) = UPPER(LTRIM(RTRIM(a.position_role)))
WHERE h.activo = 1
GROUP BY h.scotia_id, a.logical_access_name, h.unit, h.unidad_subunidad, h.position, a.subunit, a.position_role, 
         a.role_name, a.system_owner, a.access_type, a.category, a.description;
GO

PRINT 'vw_required_apps creada exitosamente';
GO

-- Verificar si vw_current_access se puede crear
PRINT 'Intentando crear vw_current_access...';
GO

IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_current_access')
    DROP VIEW [dbo].[vw_current_access];
GO

CREATE VIEW [dbo].[vw_current_access] AS
SELECT 
    h.scotia_id,
    head.unit,
    head.position,
    h.app_access_name as logical_access_name,
    h.subunit,
    head.position as position_role,
    h.record_date,
    h.status
FROM [dbo].[historico] h
INNER JOIN [dbo].[headcount] head ON h.scotia_id = head.scotia_id
WHERE h.status = 'Completado'
AND h.process_access IN ('onboarding', 'lateral_movement')
AND head.activo = 1
AND h.app_access_name IS NOT NULL
GROUP BY h.scotia_id, h.app_access_name, head.unit, head.position, h.subunit, h.record_date, h.status;
GO

PRINT 'vw_current_access creada exitosamente';
GO

-- Verificar si vw_to_grant se puede crear
PRINT 'Intentando crear vw_to_grant...';
GO

IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_to_grant')
    DROP VIEW [dbo].[vw_to_grant];
GO

CREATE VIEW [dbo].[vw_to_grant] AS
SELECT 
    req.scotia_id,
    req.unit,
    req.position,
    req.logical_access_name,
    req.subunit,
    req.position_role,
    'onboarding' as process_type
FROM [dbo].[vw_required_apps] req
LEFT JOIN [dbo].[vw_current_access] curr ON 
    req.scotia_id = curr.scotia_id AND
    UPPER(LTRIM(RTRIM(req.logical_access_name))) = UPPER(LTRIM(RTRIM(curr.logical_access_name))) AND
    UPPER(LTRIM(RTRIM(req.unit))) = UPPER(LTRIM(RTRIM(curr.unit))) AND
    UPPER(LTRIM(RTRIM(req.position))) = UPPER(LTRIM(RTRIM(curr.position)))
WHERE curr.scotia_id IS NULL;
GO

PRINT 'vw_to_grant creada exitosamente';
GO

-- Verificar si vw_to_revoke se puede crear
PRINT 'Intentando crear vw_to_revoke...';
GO

IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_to_revoke')
    DROP VIEW [dbo].[vw_to_revoke];
GO

CREATE VIEW [dbo].[vw_to_revoke] AS
SELECT 
    curr.scotia_id,
    curr.unit,
    curr.position,
    curr.logical_access_name,
    curr.subunit,
    curr.position_role,
    curr.record_date,
    'offboarding' as process_type
FROM [dbo].[vw_current_access] curr
LEFT JOIN [dbo].[vw_required_apps] req ON 
    curr.scotia_id = req.scotia_id AND
    UPPER(LTRIM(RTRIM(curr.logical_access_name))) = UPPER(LTRIM(RTRIM(req.logical_access_name))) AND
    UPPER(LTRIM(RTRIM(curr.unit))) = UPPER(LTRIM(RTRIM(req.unit))) AND
    UPPER(LTRIM(RTRIM(curr.position))) = UPPER(LTRIM(RTRIM(req.position)))
WHERE req.scotia_id IS NULL;
GO

PRINT 'vw_to_revoke creada exitosamente';
GO

-- Verificar si vw_system_stats se puede crear
PRINT 'Intentando crear vw_system_stats...';
GO

IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_system_stats')
    DROP VIEW [dbo].[vw_system_stats];
GO

CREATE VIEW [dbo].[vw_system_stats] AS
SELECT 
    (SELECT COUNT(*) FROM [dbo].[headcount] WHERE activo = 1) as empleados_activos,
    (SELECT COUNT(*) FROM [dbo].[applications] WHERE access_status = 'Activo') as aplicaciones_activas,
    (SELECT COUNT(*) FROM [dbo].[historico]) as total_historico,
    (SELECT COUNT(*) FROM [dbo].[procesos]) as total_procesos,
    (SELECT COUNT(*) FROM [dbo].[headcount]) as total_empleados,
    (SELECT COUNT(*) FROM [dbo].[applications]) as total_aplicaciones;
GO

PRINT 'vw_system_stats creada exitosamente';
GO

-- Probar las vistas
PRINT 'Probando las vistas...';
GO

SELECT 'vw_required_apps' as vista, COUNT(*) as registros FROM [dbo].[vw_required_apps]
UNION ALL
SELECT 'vw_current_access' as vista, COUNT(*) as registros FROM [dbo].[vw_current_access]
UNION ALL
SELECT 'vw_to_grant' as vista, COUNT(*) as registros FROM [dbo].[vw_to_grant]
UNION ALL
SELECT 'vw_to_revoke' as vista, COUNT(*) as registros FROM [dbo].[vw_to_revoke]
UNION ALL
SELECT 'vw_system_stats' as vista, COUNT(*) as registros FROM [dbo].[vw_system_stats];
GO

PRINT 'Diagnóstico completado exitosamente';
GO

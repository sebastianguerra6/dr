-- =====================================================
-- SCRIPT DE CONFIGURACIÓN CORREGIDO PARA SQL SERVER
-- Sistema de Gestión de Empleados y Conciliación de Accesos
-- =====================================================

-- Crear base de datos si no existe
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'GAMLO_Empleados_DR')
BEGIN
    CREATE DATABASE GAMLO_Empleados_DR;
    PRINT 'Base de datos GAMLO_Empleados_DR creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Base de datos GAMLO_Empleados_DR ya existe';
END
GO

USE GAMLO_Empleados_DR;
GO

-- Crear esquema dedicado para objetos DR si no existe
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'dr')
BEGIN
    EXEC('CREATE SCHEMA dr AUTHORIZATION dbo;');
    PRINT 'Esquema dr creado exitosamente.';
END
ELSE
BEGIN
    PRINT 'Esquema dr ya existe.';
END
GO

-- Eliminar llaves foráneas existentes para poder recrear las tablas
DECLARE @fk_table SYSNAME, @sql NVARCHAR(400);

SET @fk_table = NULL;
SELECT @fk_table = QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) + '.' + QUOTENAME(OBJECT_NAME(parent_object_id))
FROM sys.foreign_keys WHERE name = 'FK_historico_headcount';
IF @fk_table IS NOT NULL
BEGIN
    SET @sql = N'ALTER TABLE ' + @fk_table + N' DROP CONSTRAINT FK_historico_headcount;';
    EXEC sp_executesql @sql;
    PRINT 'FK_historico_headcount eliminada.';
END

SET @fk_table = NULL;
SELECT @fk_table = QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) + '.' + QUOTENAME(OBJECT_NAME(parent_object_id))
FROM sys.foreign_keys WHERE name = 'FK_procesos_headcount';
IF @fk_table IS NOT NULL
BEGIN
    SET @sql = N'ALTER TABLE ' + @fk_table + N' DROP CONSTRAINT FK_procesos_headcount;';
    EXEC sp_executesql @sql;
    PRINT 'FK_procesos_headcount eliminada.';
END

SET @fk_table = NULL;
SELECT @fk_table = QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) + '.' + QUOTENAME(OBJECT_NAME(parent_object_id))
FROM sys.foreign_keys WHERE name = 'FK_historico_applications';
IF @fk_table IS NOT NULL
BEGIN
    SET @sql = N'ALTER TABLE ' + @fk_table + N' DROP CONSTRAINT FK_historico_applications;';
    EXEC sp_executesql @sql;
    PRINT 'FK_historico_applications eliminada.';
END
GO

-- =====================================================
-- TABLA 1: HEADCOUNT (Empleados) - Fuente externa existente
-- =====================================================
IF OBJECT_ID(N'[dbo].[Master_Staff_List]', N'U') IS NULL
BEGIN
    RAISERROR('La tabla [dbo].[Master_Staff_List] no existe. Cree la tabla o actualice el nombre antes de ejecutar este script.', 16, 1);
    RETURN;
END
PRINT 'Usando tabla existente [dbo].[Master_Staff_List] como fuente de headcount.';
GO

-- Sin tocar la tabla original, solo crear sinónimos dentro del esquema dr
IF EXISTS (SELECT 1 FROM sys.synonyms WHERE name = 'headcount' AND schema_id = SCHEMA_ID('dr'))
    DROP SYNONYM [dr].[headcount];
GO
CREATE SYNONYM [dr].[headcount] FOR [dbo].[Master_Staff_List];
GO

-- =====================================================
-- TABLA 2: APPLICATIONS (Aplicaciones y Accesos)
-- =====================================================
IF OBJECT_ID(N'[dbo].[applications_dr]', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[applications_dr] (
        [id] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [status] VARCHAR(50) NULL,
        [unit] VARCHAR(150) NULL,
        [service] VARCHAR(150) NULL,
        [role] VARCHAR(150) NULL,
        [system_jurisdiction] VARCHAR(150) NULL,
        [name_element] VARCHAR(200) NOT NULL,
        [type_of_element] VARCHAR(150) NULL,
        [system_description] NVARCHAR(MAX) NULL,
        [information_needed] NVARCHAR(MAX) NULL,
        [approval_needed] NVARCHAR(MAX) NULL,
        [request_object] NVARCHAR(MAX) NULL,
        [form_need_to_request_access] NVARCHAR(MAX) NULL,
        [roles_and_profiles] NVARCHAR(MAX) NULL,
        [how_to_request_system_access] NVARCHAR(MAX) NULL,
        [how_to_remove_system_access] NVARCHAR(MAX) NULL,
        [for_issues] NVARCHAR(MAX) NULL,
        [critical_non_critical] VARCHAR(50) NULL,
        [application_owner] VARCHAR(150) NULL,
        [direct_contact] VARCHAR(150) NULL,
        [sla_onboarding] VARCHAR(50) NULL,
        [sla_offboarding] VARCHAR(50) NULL,
        [system_application_link] VARCHAR(255) NULL,
        [log_in_information] NVARCHAR(MAX) NULL,
        [access_blocked_password] NVARCHAR(MAX) NULL,
        [bulk_request] NVARCHAR(MAX) NULL,
        [certification_process] NVARCHAR(MAX) NULL,
        [license] NVARCHAR(MAX) NULL
    );
    PRINT 'Tabla applications_dr creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla applications_dr ya existía. Se conserva tal cual.';
END
GO

IF EXISTS (SELECT 1 FROM sys.synonyms WHERE name = 'applications' AND schema_id = SCHEMA_ID('dr'))
    DROP SYNONYM [dr].[applications];
GO
CREATE SYNONYM [dr].[applications] FOR [dbo].[applications_dr];
GO

-- =====================================================
-- VISTAS DE COMPATIBILIDAD (mantienen nombres legacy)
-- =====================================================
IF OBJECT_ID(N'[dbo].[vw_headcount_legacy]', N'V') IS NOT NULL
    DROP VIEW [dbo].[vw_headcount_legacy];
GO
CREATE VIEW [dbo].[vw_headcount_legacy] AS
SELECT
    h.scotia_id,
    h.eikon_id,
    h.employee_number,
    h.employee_number AS employee,
    CONCAT(h.employee_name, ' ', h.employee_last_name) AS full_name,
    h.employee_name,
    h.employee_last_name,
    h.business_email AS email,
    h.department AS unit,
    h.department AS unidad_subunidad,
    h.current_position_title AS position,
    h.current_position_title AS position_role,
    h.current_position_level,
    h.status,
    CASE WHEN h.status IN ('Active', 'Activo') THEN 1 ELSE 0 END AS activo,
    h.exit_date AS inactivation_date,
    h.modality_as_today,
    h.action_item,
    h.exit_reason,
    h.modality_reason,
    h.gender,
    h.dob,
    h.office,
    h.brigade,
    h.begdate,
    h.position_code
FROM dbo.Master_Staff_List h;
GO

IF OBJECT_ID(N'[dbo].[vw_applications_legacy]', N'V') IS NOT NULL
    DROP VIEW [dbo].[vw_applications_legacy];
GO
CREATE VIEW [dbo].[vw_applications_legacy] AS
SELECT
    a.id,
    a.status AS access_status,
    a.unit,
    a.service AS subunit,
    CONCAT(
        ISNULL(a.unit, ''),
        CASE WHEN a.unit IS NOT NULL AND a.service IS NOT NULL THEN '/' ELSE '' END,
        ISNULL(a.service, '')
    ) AS unidad_subunidad,
    a.role AS position_role,
    a.roles_and_profiles AS role_name,
    a.name_element AS logical_access_name,
    a.type_of_element AS access_type,
    a.critical_non_critical AS category,
    a.application_owner AS system_owner,
    a.system_description AS description,
    a.system_application_link,
    a.log_in_information,
    a.direct_contact,
    a.sla_onboarding,
    a.sla_offboarding,
    a.bulk_request,
    a.certification_process,
    a.license
FROM dbo.applications_dr a;
GO

-- =====================================================
-- TABLA 3: HISTORICO (Historial de Procesos)
-- =====================================================
IF OBJECT_ID(N'[dbo].[historico_dr]', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[historico_dr] (
        [id] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [scotia_id] VARCHAR(20) NOT NULL,
        [employee_email] VARCHAR(150) NULL,
        [case_id] VARCHAR(100) NULL,
        [responsible] VARCHAR(100) NULL,
        [record_date] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [request_date] DATE NULL,
        [process_access] VARCHAR(50) NULL,
        [subunit] VARCHAR(100) NULL,
        [event_description] NVARCHAR(MAX) NULL,
        [ticket_email] VARCHAR(150) NULL,
        [app_access_name] VARCHAR(150) NULL,
        [computer_system_type] VARCHAR(100) NULL,
        [duration_of_access] VARCHAR(50) NULL,
        [status] VARCHAR(50) NULL,
        [closing_date_app] DATE NULL,
        [closing_date_ticket] DATE NULL,
        [app_quality] VARCHAR(50) NULL,
        [confirmation_by_user] DATE NULL,
        [comment] NVARCHAR(MAX) NULL,
        [comment_tq] NVARCHAR(MAX) NULL,
        [ticket_quality] VARCHAR(50) NULL,
        [general_status_ticket] VARCHAR(50) NULL,
        [general_status_case] VARCHAR(50) NULL,
        [average_time_open_ticket] VARCHAR(20) NULL,
        [sla_app] VARCHAR(50) NULL,
        [sla_ticket] VARCHAR(50) NULL,
        [sla_case] VARCHAR(50) NULL
    );
    PRINT 'Tabla historico_dr creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla historico_dr ya existía. Se conserva tal cual.';
END
GO

IF EXISTS (SELECT 1 FROM sys.synonyms WHERE name = 'historico' AND schema_id = SCHEMA_ID('dr'))
    DROP SYNONYM [dr].[historico];
GO
CREATE SYNONYM [dr].[historico] FOR [dbo].[historico_dr];
GO

-- =====================================================
-- TABLA 4: PROCESOS (Gestión de Procesos)
-- =====================================================
IF OBJECT_ID(N'[dbo].[procesos_dr]', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[procesos_dr] (
        [id] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [sid] VARCHAR(20) NOT NULL,
        [nueva_sub_unidad] VARCHAR(100) NULL,
        [nuevo_cargo] VARCHAR(100) NULL,
        [status] VARCHAR(50) NOT NULL DEFAULT 'Pendiente',
        [request_date] DATE NULL,
        [ingreso_por] VARCHAR(100) NULL,
        [fecha_creacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [fecha_actualizacion] DATETIME2 NULL,
        [tipo_proceso] VARCHAR(50) NULL,
        [app_name] VARCHAR(150) NULL,
        [mail] VARCHAR(150) NULL,
        [closing_date_app] DATE NULL,
        [app_quality] VARCHAR(50) NULL,
    [confirmation_by_user] DATE NULL,
        [comment] NVARCHAR(MAX) NULL
    );
    PRINT 'Tabla procesos_dr creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla procesos_dr ya existía. Se conserva tal cual.';
END
GO

IF EXISTS (SELECT 1 FROM sys.synonyms WHERE name = 'procesos' AND schema_id = SCHEMA_ID('dr'))
    DROP SYNONYM [dr].[procesos];
GO
CREATE SYNONYM [dr].[procesos] FOR [dbo].[procesos_dr];
GO

-- =====================================================
-- CREAR FOREIGN KEYS DESPUÉS DE CREAR TODAS LAS TABLAS
-- =====================================================

-- Foreign Key para historico -> headcount
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_historico_headcount')
BEGIN
ALTER TABLE [dbo].[historico_dr]
    ADD CONSTRAINT [FK_historico_headcount] 
FOREIGN KEY ([scotia_id]) REFERENCES [dbo].[Master_Staff_List]([scotia_id]) ON DELETE CASCADE;
    PRINT 'Foreign Key FK_historico_headcount creada exitosamente';
END
GO

-- Foreign Key para historico -> applications
-- COMENTADO: No se puede crear porque logical_access_name no es UNIQUE
-- IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_historico_applications')
-- BEGIN
--     ALTER TABLE [dr].[historico]
--     ADD CONSTRAINT [FK_historico_applications] 
--     FOREIGN KEY ([app_access_name]) REFERENCES [dr].[applications]([logical_access_name]) ON DELETE SET NULL;
--     PRINT 'Foreign Key FK_historico_applications creada exitosamente';
-- END
PRINT 'Foreign Key FK_historico_applications omitida: logical_access_name no es UNIQUE en applications';
GO

-- Foreign Key para procesos -> headcount
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_procesos_headcount')
BEGIN
ALTER TABLE [dbo].[procesos_dr]
    ADD CONSTRAINT [FK_procesos_headcount] 
FOREIGN KEY ([sid]) REFERENCES [dbo].[Master_Staff_List]([scotia_id]) ON DELETE CASCADE;
    PRINT 'Foreign Key FK_procesos_headcount creada exitosamente';
END
GO

-- =====================================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- =====================================================

-- Índices para headcount
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_headcount_department_title' AND object_id = OBJECT_ID(N'[dbo].[Master_Staff_List]'))
BEGIN
    CREATE INDEX IX_headcount_department_title ON [dbo].[Master_Staff_List] ([department], [current_position_title]);
    PRINT 'Índice IX_headcount_department_title creado exitosamente';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_headcount_level_code' AND object_id = OBJECT_ID(N'[dbo].[Master_Staff_List]'))
BEGIN
    CREATE INDEX IX_headcount_level_code ON [dbo].[Master_Staff_List] ([current_position_level], [position_code]);
    PRINT 'Índice IX_headcount_level_code creado exitosamente';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_headcount_status' AND object_id = OBJECT_ID(N'[dbo].[Master_Staff_List]'))
BEGIN
    CREATE INDEX IX_headcount_status ON [dbo].[Master_Staff_List] ([status]);
    PRINT 'Índice IX_headcount_status creado exitosamente';
END
GO

-- Índices para applications
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_applications_unit_role' AND object_id = OBJECT_ID(N'[dbo].[applications_dr]'))
BEGIN
    CREATE INDEX IX_applications_unit_role ON [dbo].[applications_dr] ([unit], [role]);
    PRINT 'Índice IX_applications_unit_role creado exitosamente';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_applications_service_role' AND object_id = OBJECT_ID(N'[dbo].[applications_dr]'))
BEGIN
    CREATE INDEX IX_applications_service_role ON [dbo].[applications_dr] ([service], [role]);
    PRINT 'Índice IX_applications_service_role creado exitosamente';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_applications_status' AND object_id = OBJECT_ID(N'[dbo].[applications_dr]'))
BEGIN
    CREATE INDEX IX_applications_status ON [dbo].[applications_dr] ([status]);
    PRINT 'Índice IX_applications_status creado exitosamente';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_applications_name_element' AND object_id = OBJECT_ID(N'[dbo].[applications_dr]'))
BEGIN
    CREATE INDEX IX_applications_name_element ON [dbo].[applications_dr] ([name_element]);
    PRINT 'Índice IX_applications_name_element creado exitosamente';
END
GO

-- Índices para historico
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_historico_scotia_status' AND object_id = OBJECT_ID(N'[dbo].[historico_dr]'))
BEGIN
    CREATE INDEX IX_historico_scotia_status ON [dbo].[historico_dr] ([scotia_id], [status]);
    PRINT 'Índice IX_historico_scotia_status creado exitosamente';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_historico_process_status' AND object_id = OBJECT_ID(N'[dbo].[historico_dr]'))
BEGIN
    CREATE INDEX IX_historico_process_status ON [dbo].[historico_dr] ([process_access], [status]);
    PRINT 'Índice IX_historico_process_status creado exitosamente';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_historico_record_date' AND object_id = OBJECT_ID(N'[dbo].[historico_dr]'))
BEGIN
    CREATE INDEX IX_historico_record_date ON [dbo].[historico_dr] ([record_date]);
    PRINT 'Índice IX_historico_record_date creado exitosamente';
END
GO

-- =====================================================
-- VISTAS DEL SISTEMA
-- =====================================================

-- Vista para aplicaciones requeridas
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'vw_required_apps')
BEGIN
    EXEC('CREATE VIEW [dbo].[vw_required_apps] AS
    SELECT 
        h.scotia_id,
        h.department,
        h.current_position_title,
        h.current_position_level,
        h.position_code,
        a.name_element,
        a.unit,
        a.service,
        a.role,
        a.type_of_element,
        a.application_owner,
        a.system_description
    FROM [dr].[headcount] h
    INNER JOIN (
        SELECT DISTINCT
            name_element,
            unit,
            service,
            role,
            type_of_element,
            application_owner,
            system_description,
            status
        FROM [dr].[applications]
        WHERE status IN (''Active'', ''Activo'')
    ) a ON 
        UPPER(LTRIM(RTRIM(ISNULL(h.department, '''')))) = UPPER(LTRIM(RTRIM(ISNULL(a.unit, ''''))))
        AND UPPER(LTRIM(RTRIM(ISNULL(h.current_position_title, '''')))) = UPPER(LTRIM(RTRIM(ISNULL(a.role, ''''))))
        AND UPPER(LTRIM(RTRIM(ISNULL(h.current_position_level, '''')))) = UPPER(LTRIM(RTRIM(ISNULL(a.service, ''''))))
        AND UPPER(LTRIM(RTRIM(ISNULL(h.position_code, '''')))) = UPPER(LTRIM(RTRIM(ISNULL(a.type_of_element, ''''))))
    WHERE h.status IN (''Active'', ''Activo'')
    GROUP BY h.scotia_id, h.department, h.current_position_title, h.current_position_level, h.position_code,
             a.name_element, a.unit, a.service, a.role, a.type_of_element, a.application_owner, a.system_description');
    PRINT 'Vista vw_required_apps creada exitosamente';
END
ELSE
BEGIN
    EXEC('ALTER VIEW [dbo].[vw_required_apps] AS
    SELECT 
        h.scotia_id,
        h.department,
        h.current_position_title,
        h.current_position_level,
        h.position_code,
        a.name_element,
        a.unit,
        a.service,
        a.role,
        a.type_of_element,
        a.application_owner,
        a.system_description
    FROM [dr].[headcount] h
    INNER JOIN (
        SELECT DISTINCT
            name_element,
            unit,
            service,
            role,
            type_of_element,
            application_owner,
            system_description,
            status
        FROM [dr].[applications]
        WHERE status IN (''Active'', ''Activo'')
    ) a ON 
        UPPER(LTRIM(RTRIM(ISNULL(h.department, '''')))) = UPPER(LTRIM(RTRIM(ISNULL(a.unit, ''''))))
        AND UPPER(LTRIM(RTRIM(ISNULL(h.current_position_title, '''')))) = UPPER(LTRIM(RTRIM(ISNULL(a.role, ''''))))
        AND UPPER(LTRIM(RTRIM(ISNULL(h.current_position_level, '''')))) = UPPER(LTRIM(RTRIM(ISNULL(a.service, ''''))))
        AND UPPER(LTRIM(RTRIM(ISNULL(h.position_code, '''')))) = UPPER(LTRIM(RTRIM(ISNULL(a.type_of_element, ''''))))
    WHERE h.status IN (''Active'', ''Activo'')
    GROUP BY h.scotia_id, h.department, h.current_position_title, h.current_position_level, h.position_code,
             a.name_element, a.unit, a.service, a.role, a.type_of_element, a.application_owner, a.system_description');
    PRINT 'Vista vw_required_apps actualizada exitosamente';
END
GO

-- Vista para accesos actuales
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'vw_current_access')
BEGIN
    EXEC('CREATE VIEW [dbo].[vw_current_access] AS
    SELECT 
        h.scotia_id,
        hc.department,
        hc.current_position_title,
        hc.current_position_level,
        hc.position_code,
        h.app_access_name AS name_element,
        h.subunit,
        h.record_date,
        h.status
    FROM [dr].[historico] h
    INNER JOIN [dr].[headcount] hc ON h.scotia_id = hc.scotia_id
    WHERE h.status IN (''closed completed'', ''Completado'')
    AND h.process_access IN (''onboarding'', ''lateral_movement'')
    AND hc.status IN (''Active'', ''Activo'')
    AND h.app_access_name IS NOT NULL
    GROUP BY h.scotia_id, h.app_access_name, hc.department, hc.current_position_title, hc.current_position_level, hc.position_code, h.subunit, h.record_date, h.status');
    PRINT 'Vista vw_current_access creada exitosamente';
END
ELSE
BEGIN
    -- Actualizar vista existente
    EXEC('ALTER VIEW [dbo].[vw_current_access] AS
    SELECT 
        h.scotia_id,
        hc.department,
        hc.current_position_title,
        hc.current_position_level,
        hc.position_code,
        h.app_access_name AS name_element,
        h.subunit,
        h.record_date,
        h.status
    FROM [dr].[historico] h
    INNER JOIN [dr].[headcount] hc ON h.scotia_id = hc.scotia_id
    WHERE h.status IN (''closed completed'', ''Completado'')
    AND h.process_access IN (''onboarding'', ''lateral_movement'')
    AND hc.status IN (''Active'', ''Activo'')
    AND h.app_access_name IS NOT NULL
    GROUP BY h.scotia_id, h.app_access_name, hc.department, hc.current_position_title, hc.current_position_level, hc.position_code, h.subunit, h.record_date, h.status');
    PRINT 'Vista vw_current_access actualizada exitosamente';
END
GO

-- Vista para accesos por otorgar
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'vw_to_grant')
BEGIN
    EXEC('CREATE VIEW [dbo].[vw_to_grant] AS
    SELECT 
        req.scotia_id,
        req.department,
        req.current_position_title,
        req.current_position_level,
        req.position_code,
        req.name_element,
        req.unit,
        req.service,
        req.role,
        req.type_of_element,
        ''onboarding'' AS process_type
    FROM [dbo].[vw_required_apps] req
    LEFT JOIN [dbo].[vw_current_access] curr ON 
        req.scotia_id = curr.scotia_id AND
        UPPER(LTRIM(RTRIM(req.name_element))) = UPPER(LTRIM(RTRIM(curr.name_element)))
    WHERE curr.scotia_id IS NULL');
    PRINT 'Vista vw_to_grant creada exitosamente';
END
ELSE
BEGIN
    -- Actualizar vista existente
    EXEC('ALTER VIEW [dbo].[vw_to_grant] AS
    SELECT 
        req.scotia_id,
        req.department,
        req.current_position_title,
        req.current_position_level,
        req.position_code,
        req.name_element,
        req.unit,
        req.service,
        req.role,
        req.type_of_element,
        ''onboarding'' AS process_type
    FROM [dbo].[vw_required_apps] req
    LEFT JOIN [dbo].[vw_current_access] curr ON 
        req.scotia_id = curr.scotia_id AND
        UPPER(LTRIM(RTRIM(req.name_element))) = UPPER(LTRIM(RTRIM(curr.name_element)))
    WHERE curr.scotia_id IS NULL');
    PRINT 'Vista vw_to_grant actualizada exitosamente';
END
GO

-- Vista para accesos por revocar
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'vw_to_revoke')
BEGIN
    EXEC('CREATE VIEW [dbo].[vw_to_revoke] AS
    SELECT 
        curr.scotia_id,
        curr.department,
        curr.current_position_title,
        curr.current_position_level,
        curr.position_code,
        curr.name_element,
        curr.subunit,
        curr.record_date,
        ''offboarding'' AS process_type
    FROM [dbo].[vw_current_access] curr
    LEFT JOIN [dbo].[vw_required_apps] req ON 
        curr.scotia_id = req.scotia_id AND
        UPPER(LTRIM(RTRIM(curr.name_element))) = UPPER(LTRIM(RTRIM(req.name_element)))
    WHERE req.scotia_id IS NULL');
    PRINT 'Vista vw_to_revoke creada exitosamente';
END
ELSE
BEGIN
    -- Actualizar vista existente
    EXEC('ALTER VIEW [dbo].[vw_to_revoke] AS
    SELECT 
        curr.scotia_id,
        curr.department,
        curr.current_position_title,
        curr.current_position_level,
        curr.position_code,
        curr.name_element,
        curr.subunit,
        curr.record_date,
        ''offboarding'' AS process_type
    FROM [dbo].[vw_current_access] curr
    LEFT JOIN [dbo].[vw_required_apps] req ON 
        curr.scotia_id = req.scotia_id AND
        UPPER(LTRIM(RTRIM(curr.name_element))) = UPPER(LTRIM(RTRIM(req.name_element)))
    WHERE req.scotia_id IS NULL');
    PRINT 'Vista vw_to_revoke actualizada exitosamente';
END
GO

-- Vista para estadísticas del sistema
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'vw_system_stats')
BEGIN
    EXEC('CREATE VIEW [dbo].[vw_system_stats] AS
    SELECT 
        (SELECT COUNT(*) FROM [dr].[headcount] WHERE status IN (''Active'', ''Activo'')) as empleados_activos,
        (SELECT COUNT(*) FROM [dr].[applications] WHERE status IN (''Active'', ''Activo'')) as aplicaciones_activas,
        (SELECT COUNT(*) FROM [dr].[historico]) as total_historico,
        (SELECT COUNT(*) FROM [dr].[procesos]) as total_procesos,
        (SELECT COUNT(*) FROM [dr].[headcount]) as total_empleados,
        (SELECT COUNT(*) FROM [dr].[applications]) as total_aplicaciones');
    PRINT 'Vista vw_system_stats creada exitosamente';
END
GO

-- =====================================================
-- PROCEDIMIENTOS ALMACENADOS
-- =====================================================

-- Procedimiento para obtener estadísticas de la base de datos
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_GetDatabaseStats')
BEGIN
    EXEC('CREATE PROCEDURE [dbo].[sp_GetDatabaseStats]
    AS
    BEGIN
        SELECT 
            ''headcount'' as tabla, COUNT(*) as registros FROM [dr].[headcount]
        UNION ALL
        SELECT ''applications'' as tabla, COUNT(*) as registros FROM [dr].[applications]
        UNION ALL
        SELECT ''historico'' as tabla, COUNT(*) as registros FROM [dr].[historico]
        UNION ALL
        SELECT ''procesos'' as tabla, COUNT(*) as registros FROM [dr].[procesos];
    END');
    PRINT 'Procedimiento sp_GetDatabaseStats creado exitosamente';
END
GO

-- Procedimiento para obtener historial de empleado
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_GetEmployeeHistory')
BEGIN
    EXEC('CREATE PROCEDURE [dbo].[sp_GetEmployeeHistory]
        @scotia_id VARCHAR(20)
    AS
    BEGIN
        SELECT 
            h.*, 
            a.logical_access_name AS app_logical_access_name,
            a.description AS app_description,
            a.unit AS app_unit,
            a.subunit AS app_subunit,
            a.position_role AS app_position_role,
            a.category AS app_category
        FROM [dr].[historico] h
        LEFT JOIN (
            SELECT 
                logical_access_name,
                description,
                unit,
                subunit,
                position_role,
                category,
                ROW_NUMBER() OVER (PARTITION BY logical_access_name ORDER BY id) as rn
            FROM [dbo].[vw_applications_legacy]
        ) a ON h.app_access_name = a.logical_access_name AND a.rn = 1
        WHERE h.scotia_id = @scotia_id
        ORDER BY h.record_date DESC;
    END');
    PRINT 'Procedimiento sp_GetEmployeeHistory creado exitosamente';
END
GO

-- Procedimiento para obtener aplicaciones por posición
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_GetApplicationsByPosition')
BEGIN
    EXEC('CREATE PROCEDURE [dbo].[sp_GetApplicationsByPosition]
        @position VARCHAR(100) = NULL,
        @unit VARCHAR(100) = NULL,
        @subunit VARCHAR(100) = NULL
    AS
    BEGIN
        SELECT *
        FROM [dbo].[vw_applications_legacy]
        WHERE access_status IN (''Activo'', ''Active'')
        AND (@position IS NULL OR position_role = @position)
        AND (@unit IS NULL OR unit = @unit)
        AND (@subunit IS NULL OR subunit = @subunit)
        ORDER BY unit, position_role, logical_access_name;
    END');
    PRINT 'Procedimiento sp_GetApplicationsByPosition creado exitosamente';
END
GO

-- =====================================================
-- FUNCIÓN ESCALAR
-- =====================================================

-- Función para normalizar texto
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[fn_NormalizeText]') AND type in (N'FN'))
    DROP FUNCTION [dbo].[fn_NormalizeText];
GO

CREATE FUNCTION [dbo].[fn_NormalizeText](@text VARCHAR(MAX))
RETURNS VARCHAR(MAX)
AS
BEGIN
    DECLARE @result VARCHAR(MAX);
    SET @result = UPPER(LTRIM(RTRIM(ISNULL(@text, ''))));
    RETURN @result;
END
GO

PRINT 'Función fn_NormalizeText creada exitosamente';

-- =====================================================
-- DATOS DE EJEMPLO
-- =====================================================

-- Insertar datos de ejemplo en applications
IF NOT EXISTS (SELECT * FROM applications_dr WHERE name_element = 'Sistema de Gestión')
BEGIN
    INSERT INTO [dbo].[applications_dr] (
        status, unit, service, role, system_jurisdiction,
        name_element, type_of_element, system_description,
        application_owner, critical_non_critical, system_application_link
    )
    VALUES 
        ('Active', 'Tecnología', 'Desarrollo', 'Analista', 'Global', 'Sistema de Gestión', 'Aplicación', 'ERP corporativo', 'Admin Sistema', 'Crítico', 'https://sistema.empresa.com'),
        ('Active', 'Tecnología', 'DevOps', 'Analista Senior', 'Global', 'GitLab', 'Aplicación', 'Repositorio de código', 'Admin DevOps', 'Crítico', 'https://gitlab.empresa.com');
    PRINT 'Datos de ejemplo insertados en applications';
END
GO

-- Insertar datos de ejemplo en historico (solo si existen los SID en Master_Staff_List)
DECLARE @historico_rows_inserted INT = 0;

IF EXISTS (SELECT 1 FROM Master_Staff_List WHERE scotia_id = 'EMP001')
BEGIN
    IF NOT EXISTS (SELECT 1 FROM historico_dr WHERE scotia_id = 'EMP001')
    BEGIN
        INSERT INTO [dbo].[historico_dr] (scotia_id, case_id, responsible, record_date, request_date, process_access, subunit, event_description, ticket_email, app_access_name, computer_system_type, duration_of_access, status, closing_date_app, closing_date_ticket, app_quality, confirmation_by_user, comment, comment_tq, ticket_quality, general_status_ticket, general_status_case, average_time_open_ticket, sla_app, sla_ticket, sla_case)
        VALUES ('EMP001', 'CASE-20240115-001', 'Admin Sistema', GETDATE(), '2024-01-14', 'onboarding', 'Tecnología/Desarrollo', 'Usuario creado en sistema', 'admin@empresa.com', 'Sistema de Gestión', 'Sistemas', 'Permanente', 'Completado', '2024-01-15', '2024-01-15', 'Excelente', '2024-01-16', 'Usuario creado exitosamente', 'Ticket completado satisfactoriamente', 'Excelente', 'Completado', 'Completado', '00:30:00', 'Cumplido', 'Cumplido', 'Cumplido');
        SET @historico_rows_inserted += 1;
    END
END
ELSE
    PRINT 'Dato demo EMP001 omitido: no existe en Master_Staff_List.';

IF EXISTS (SELECT 1 FROM Master_Staff_List WHERE scotia_id = 'EMP002')
BEGIN
    IF NOT EXISTS (SELECT 1 FROM historico_dr WHERE scotia_id = 'EMP002')
    BEGIN
        INSERT INTO [dbo].[historico_dr] (scotia_id, case_id, responsible, record_date, request_date, process_access, subunit, event_description, ticket_email, app_access_name, computer_system_type, duration_of_access, status, closing_date_app, closing_date_ticket, app_quality, confirmation_by_user, comment, comment_tq, ticket_quality, general_status_ticket, general_status_case, average_time_open_ticket, sla_app, sla_ticket, sla_case)
        VALUES ('EMP002', 'CASE-20240115-002', 'Admin Portal', GETDATE(), '2024-01-14', 'onboarding', 'Tecnología/Desarrollo', 'Usuario creado en portal', 'admin@empresa.com', 'GitLab', 'Desarrollo', 'Permanente', 'Completado', '2024-01-15', '2024-01-15', 'Excelente', '2024-01-16', 'Usuario creado exitosamente', 'Ticket completado satisfactoriamente', 'Excelente', 'Completado', 'Completado', '00:45:00', 'Cumplido', 'Cumplido', 'Cumplido');
        SET @historico_rows_inserted += 1;
    END
END
ELSE
    PRINT 'Dato demo EMP002 omitido: no existe en Master_Staff_List.';

IF EXISTS (SELECT 1 FROM Master_Staff_List WHERE scotia_id = 'EMP003')
BEGIN
    IF NOT EXISTS (SELECT 1 FROM historico_dr WHERE scotia_id = 'EMP003')
    BEGIN
        INSERT INTO [dbo].[historico_dr] (scotia_id, case_id, responsible, record_date, request_date, process_access, subunit, event_description, ticket_email, app_access_name, computer_system_type, duration_of_access, status, closing_date_app, closing_date_ticket, app_quality, confirmation_by_user, comment, comment_tq, ticket_quality, general_status_ticket, general_status_case, average_time_open_ticket, sla_app, sla_ticket, sla_case)
        VALUES ('EMP003', 'CASE-20240115-003', 'Admin Sistema', GETDATE(), '2024-01-14', 'onboarding', 'Tecnología/Desarrollo', 'Usuario creado en sistema', 'admin@empresa.com', 'Jira', 'Gestión', 'Permanente', 'Completado', '2024-01-15', '2024-01-15', 'Excelente', '2024-01-16', 'Usuario creado exitosamente', 'Ticket completado satisfactoriamente', 'Excelente', 'Completado', 'Completado', '00:20:00', 'Cumplido', 'Cumplido', 'Cumplido');
        SET @historico_rows_inserted += 1;
    END
END
ELSE
    PRINT 'Dato demo EMP003 omitido: no existe en Master_Staff_List.';

IF @historico_rows_inserted > 0
    PRINT CONCAT('Datos de ejemplo insertados en historico: ', @historico_rows_inserted);
ELSE
    PRINT 'No se insertaron datos demo en historico (faltan SID en Master_Staff_List).';
GO

-- =====================================================
-- MIGRACIÓN SIMPLE PARA CONFIRMATION_BY_USER
-- =====================================================

-- Migrar confirmation_by_user de VARCHAR a DATE en tabla historico
IF EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[historico_dr]') AND name = 'confirmation_by_user' AND system_type_id = 167)
BEGIN
    PRINT 'Migrando confirmation_by_user de VARCHAR a DATE en tabla historico...';
    ALTER TABLE [dbo].[historico_dr] ALTER COLUMN [confirmation_by_user] DATE NULL;
    PRINT 'Migración de historico completada';
END
ELSE
BEGIN
    PRINT 'confirmation_by_user en historico ya es DATE o no existe';
END
GO

-- Migrar confirmation_by_user de VARCHAR a DATE en tabla procesos
IF EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[procesos_dr]') AND name = 'confirmation_by_user' AND system_type_id = 167)
BEGIN
    PRINT 'Migrando confirmation_by_user de VARCHAR a DATE en tabla procesos...';
    ALTER TABLE [dbo].[procesos_dr] ALTER COLUMN [confirmation_by_user] DATE NULL;
    PRINT 'Migración de procesos completada';
END
ELSE
BEGIN
    PRINT 'confirmation_by_user en procesos ya es DATE o no existe';
END
GO

-- Procedimiento para obtener reporte de conciliación completo
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_GetAccessReconciliationReport')
    DROP PROCEDURE [dbo].[sp_GetAccessReconciliationReport];
GO

CREATE PROCEDURE [dbo].[sp_GetAccessReconciliationReport]
    @scotia_id VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Variables para almacenar resultados
    DECLARE @emp_unit VARCHAR(100), @emp_position VARCHAR(100), @emp_unidad_subunidad VARCHAR(150);
    
    -- Obtener datos del empleado
    SELECT @emp_unit = unit, @emp_position = position, @emp_unidad_subunidad = unidad_subunidad
    FROM [dbo].[vw_headcount_legacy]
    WHERE scotia_id = @scotia_id AND activo = 1;
    
    IF @emp_unit IS NULL OR @emp_position IS NULL
    BEGIN
        SELECT 'error' as status, 'Empleado no encontrado o inactivo' as message;
        RETURN;
    END
    
    -- Crear tabla temporal para resultados
    CREATE TABLE #ReconciliationResults (
        access_type VARCHAR(20),
        app_name VARCHAR(150),
        unit VARCHAR(100),
        subunit VARCHAR(100),
        position_role VARCHAR(100),
        role_name VARCHAR(100),
        description NVARCHAR(MAX),
        record_date DATETIME2,
        status VARCHAR(50)
    );
    
    -- 1. Accesos actuales (del historial) - SOLO COMPLETADOS
    INSERT INTO #ReconciliationResults
    SELECT 
        'current' as access_type,
        h.app_access_name as app_name,
        a.unit,
        h.subunit,
        @emp_position as position_role,
        a.role_name,
        a.description,
        h.record_date,
        h.status
    FROM [dr].[historico] h
    LEFT JOIN [dbo].[vw_applications_legacy] a ON h.app_access_name = a.logical_access_name
    WHERE h.scotia_id = @scotia_id
    AND h.process_access IN ('onboarding', 'lateral_movement')
    AND h.app_access_name IS NOT NULL
    AND h.status = 'Completado';
    
    -- 2. Accesos requeridos (de la malla de aplicaciones)
    INSERT INTO #ReconciliationResults
    SELECT 
        'required' as access_type,
        a.logical_access_name as app_name,
        a.unit,
        a.subunit,
        a.position_role,
        a.role_name,
        a.description,
        NULL as record_date,
        'Required' as status
    FROM [dbo].[vw_applications_legacy] a
    WHERE a.access_status IN ('Activo','Active')
    AND a.unidad_subunidad = @emp_unidad_subunidad
    AND a.position_role = @emp_position;
    
    -- 3. Calcular accesos a otorgar (requeridos - actuales)
    INSERT INTO #ReconciliationResults
    SELECT 
        'to_grant' as access_type,
        req.app_name,
        req.unit,
        req.subunit,
        req.position_role,
        req.role_name,
        req.description,
        NULL as record_date,
        'To Grant' as status
    FROM (
        SELECT DISTINCT app_name, unit, subunit, position_role, role_name, description
        FROM #ReconciliationResults 
        WHERE access_type = 'required'
    ) req
    LEFT JOIN (
        SELECT DISTINCT app_name
        FROM #ReconciliationResults 
        WHERE access_type = 'current'
    ) curr ON req.app_name = curr.app_name
    WHERE curr.app_name IS NULL;
    
    -- 4. Calcular accesos a revocar (actuales - requeridos)
    INSERT INTO #ReconciliationResults
    SELECT 
        'to_revoke' as access_type,
        curr.app_name,
        curr.unit,
        curr.subunit,
        curr.position_role,
        curr.role_name,
        curr.description,
        curr.record_date,
        'To Revoke' as status
    FROM (
        SELECT DISTINCT app_name, unit, subunit, position_role, role_name, description, record_date
        FROM #ReconciliationResults 
        WHERE access_type = 'current'
    ) curr
    LEFT JOIN (
        SELECT DISTINCT app_name
        FROM #ReconciliationResults 
        WHERE access_type = 'required'
    ) req ON curr.app_name = req.app_name
    WHERE req.app_name IS NULL;
    
    -- Retornar resultados
    SELECT * FROM #ReconciliationResults
    WHERE access_type IN ('current', 'to_grant', 'to_revoke')
    ORDER BY access_type, app_name;
    
    -- Limpiar tabla temporal
    DROP TABLE #ReconciliationResults;
END
GO

PRINT 'Procedimiento sp_GetAccessReconciliationReport creado exitosamente';

-- Procedimiento para procesar onboarding
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_ProcessEmployeeOnboarding')
    DROP PROCEDURE [dbo].[sp_ProcessEmployeeOnboarding];
GO

CREATE PROCEDURE [dbo].[sp_ProcessEmployeeOnboarding]
    @scotia_id VARCHAR(20),
    @position VARCHAR(100),
    @unit VARCHAR(100),
    @unidad_subunidad VARCHAR(150),
    @responsible VARCHAR(100) = 'Sistema',
    @subunit VARCHAR(100) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @case_id VARCHAR(100);
    DECLARE @records_created INT = 0;
    
    -- Generar case_id único
    SET @case_id = 'CASE-' + FORMAT(GETDATE(), 'yyyyMMddHHmmssfff') + '-' + @scotia_id;
    
    -- Actualizar estado del empleado a activo
    UPDATE [dr].[headcount] 
    SET status = 'Active', exit_date = NULL
    WHERE scotia_id = @scotia_id;
    
    -- Actualizar posición y unidad si están vacías
    UPDATE [dr].[headcount] 
    SET current_position_title = @position,
        department = @unit
    WHERE scotia_id = @scotia_id 
    AND (current_position_title IS NULL OR current_position_title = '' OR department IS NULL OR department = '');
    
    -- Obtener aplicaciones requeridas y crear registros históricos
    INSERT INTO [dr].[historico] (
        scotia_id, case_id, responsible, record_date, process_access, 
        subunit, event_description, ticket_email, 
        app_access_name, computer_system_type, status, general_status_case
    )
    SELECT 
        @scotia_id,
        @case_id,
        @responsible,
        GETDATE(),
        'onboarding',
        ISNULL(@subunit, a.subunit),
        'Otorgamiento de acceso para ' + a.logical_access_name,
        @responsible + '@empresa.com',
        a.logical_access_name,
        a.category,
        'Pendiente',
        'En Proceso'
    FROM [dbo].[vw_applications_legacy] a
    WHERE a.access_status IN ('Activo','Active')
    AND a.unidad_subunidad = @unidad_subunidad
    AND a.position_role = @position
    AND NOT EXISTS (
        SELECT 1 FROM [dr].[historico] h 
        WHERE h.scotia_id = @scotia_id 
        AND h.app_access_name = a.logical_access_name 
        AND h.status = 'Pendiente'
    );
    
    SET @records_created = @@ROWCOUNT;
    
    -- Retornar resultado
    SELECT 'success' as status, 
           'Onboarding procesado para ' + @scotia_id + '. ' + 
           CAST(@records_created AS VARCHAR(10)) + ' accesos requeridos.' as message,
           @records_created as records_created;
END
GO

PRINT 'Procedimiento sp_ProcessEmployeeOnboarding creado exitosamente';

-- Procedimiento para procesar offboarding
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_ProcessEmployeeOffboarding')
    DROP PROCEDURE [dbo].[sp_ProcessEmployeeOffboarding];
GO

CREATE PROCEDURE [dbo].[sp_ProcessEmployeeOffboarding]
    @scotia_id VARCHAR(20),
    @responsible VARCHAR(100) = 'Sistema'
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @case_id VARCHAR(100);
    DECLARE @records_created INT = 0;
    
    -- Generar case_id único
    SET @case_id = 'CASE-' + FORMAT(GETDATE(), 'yyyyMMddHHmmssfff') + '-' + @scotia_id;
    
    -- Actualizar estado del empleado a inactivo
    UPDATE [dr].[headcount] 
    SET status = 'Inactive', exit_date = GETDATE()
    WHERE scotia_id = @scotia_id;
    
    -- Crear registros de offboarding para accesos activos
    INSERT INTO [dr].[historico] (
        scotia_id, case_id, responsible, record_date, process_access, 
        subunit, event_description, ticket_email, 
        app_access_name, computer_system_type, status, general_status_case
    )
    SELECT DISTINCT
        @scotia_id,
        @case_id,
        @responsible,
        GETDATE(),
        'offboarding',
        h.subunit,
        'Revocación de acceso para ' + h.app_access_name,
        @responsible + '@empresa.com',
        h.app_access_name,
        a.category,
        'Pendiente',
        'En Proceso'
    FROM [dr].[historico] h
    LEFT JOIN [dbo].[vw_applications_legacy] a ON h.app_access_name = a.logical_access_name
    WHERE h.scotia_id = @scotia_id
    AND h.process_access IN ('onboarding', 'lateral_movement')
    AND h.status = 'Completado'
    AND h.app_access_name IS NOT NULL;
    
    SET @records_created = @@ROWCOUNT;
    
    -- Retornar resultado
    SELECT 'success' as status, 
           'Offboarding procesado para ' + @scotia_id + '. ' + 
           CAST(@records_created AS VARCHAR(10)) + ' accesos a revocar.' as message,
           @records_created as records_created;
END
GO

PRINT 'Procedimiento sp_ProcessEmployeeOffboarding creado exitosamente';

-- Procedimiento para obtener estadísticas de conciliación
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_GetReconciliationStats')
    DROP PROCEDURE [dbo].[sp_GetReconciliationStats];
GO

CREATE PROCEDURE [dbo].[sp_GetReconciliationStats]
    @scotia_id VARCHAR(20) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    IF @scotia_id IS NULL
    BEGIN
        -- Estadísticas globales
        SELECT 
            'Global' as scope,
            (SELECT COUNT(*) FROM [dr].[headcount] WHERE status IN ('Active','Activo')) as empleados_activos,
            (SELECT COUNT(*) FROM [dr].[applications] WHERE status IN ('Active','Activo')) as aplicaciones_activas,
            (SELECT COUNT(*) FROM [dr].[historico] WHERE status = 'Pendiente') as tickets_pendientes,
            (SELECT COUNT(*) FROM [dr].[historico] WHERE status = 'Completado') as tickets_completados,
            (SELECT COUNT(*) FROM [dr].[historico]) as total_historico;
    END
    ELSE
    BEGIN
        -- Estadísticas del empleado específico
        DECLARE @current_access INT, @to_grant INT, @to_revoke INT;
        
        SELECT @current_access = COUNT(DISTINCT app_access_name)
        FROM [dr].[historico] 
        WHERE scotia_id = @scotia_id 
        AND process_access IN ('onboarding', 'lateral_movement')
        AND status = 'Completado';
        
        -- Usar el procedimiento de conciliación para obtener to_grant y to_revoke
        CREATE TABLE #TempReconciliation (
            access_type VARCHAR(20),
            app_name VARCHAR(150)
        );
        
        INSERT INTO #TempReconciliation
        EXEC [dbo].[sp_GetAccessReconciliationReport] @scotia_id;
        
        SELECT @to_grant = COUNT(*) FROM #TempReconciliation WHERE access_type = 'to_grant';
        SELECT @to_revoke = COUNT(*) FROM #TempReconciliation WHERE access_type = 'to_revoke';
        
        SELECT 
            @scotia_id as scope,
            @current_access as accesos_actuales,
            @to_grant as accesos_a_otorgar,
            @to_revoke as accesos_a_revocar,
            (@current_access + @to_grant - @to_revoke) as accesos_finales;
        
        DROP TABLE #TempReconciliation;
    END
END
GO

PRINT 'Procedimiento sp_GetReconciliationStats creado exitosamente';

-- =====================================================
-- VERIFICACIÓN FINAL
-- =====================================================

-- Mostrar estadísticas de las tablas creadas
SELECT 'headcount' as tabla, COUNT(*) as registros FROM [dr].[headcount]
UNION ALL
SELECT 'applications' as tabla, COUNT(*) as registros FROM [dr].[applications]
UNION ALL
SELECT 'historico' as tabla, COUNT(*) as registros FROM [dr].[historico]
UNION ALL
SELECT 'procesos' as tabla, COUNT(*) as registros FROM [dr].[procesos];

-- Mostrar las vistas creadas
SELECT 'vw_required_apps' as vista, COUNT(*) as registros FROM [dbo].[vw_required_apps]
UNION ALL
SELECT 'vw_current_access' as vista, COUNT(*) as registros FROM [dbo].[vw_current_access]
UNION ALL
SELECT 'vw_to_grant' as vista, COUNT(*) as registros FROM [dbo].[vw_to_grant]
UNION ALL
SELECT 'vw_to_revoke' as vista, COUNT(*) as registros FROM [dbo].[vw_to_revoke]
UNION ALL
SELECT 'vw_system_stats' as vista, COUNT(*) as registros FROM [dbo].[vw_system_stats];

-- =====================================================
-- ARQUITECTURA HÍBRIDA: SOLO PROCEDIMIENTOS COMPLEJOS EN SQL SERVER
-- Las consultas simples se manejan directamente en Python
-- =====================================================

-- NOTA: Los procedimientos simples como sp_GetEmployeeById, sp_GetAllEmployees, etc.
-- se han movido de vuelta al código Python para mantener una arquitectura híbrida
-- que balancea la complejidad entre SQL Server y Python.

PRINT '=====================================================';
PRINT 'CONFIGURACIÓN COMPLETADA EXITOSAMENTE';
PRINT 'Base de datos: GAMLO_Empleados_DR';
PRINT 'Tablas creadas: headcount, applications, historico, procesos';
PRINT 'Vistas creadas: vw_required_apps, vw_current_access, vw_to_grant, vw_to_revoke, vw_system_stats';
PRINT 'Procedimientos básicos: sp_GetDatabaseStats, sp_GetEmployeeHistory, sp_GetApplicationsByPosition';
PRINT 'Procedimientos de conciliación: sp_GetAccessReconciliationReport, sp_ProcessEmployeeOnboarding, sp_ProcessEmployeeOffboarding, sp_GetReconciliationStats';
PRINT 'Migración automática: confirmation_by_user de VARCHAR a DATE';
PRINT 'Función creada: fn_NormalizeText';
PRINT 'Datos de ejemplo insertados correctamente';
PRINT '=====================================================';
PRINT 'CAMBIOS EN TABLA HISTORICO:';
PRINT '  - Campos agregados: duration_of_access, comment_tq, general_status_ticket, general_status_case, sla_app, sla_ticket, sla_case';
PRINT '  - Campos eliminados: sid, area';
PRINT '  - Campo subunit ahora se llena con unidad/subunidad';
PRINT '  - Campo computer_system_type ahora se llena con category de application';
PRINT '  - Campo scotia_id ahora representa el mail de la persona';
PRINT '  - Campo confirmation_by_user migrado de VARCHAR a DATE';
PRINT '=====================================================';
PRINT 'CAMBIOS EN TABLA PROCESOS:';
PRINT '  - Campo confirmation_by_user migrado de VARCHAR(50) a DATE';
PRINT '=====================================================';
PRINT 'MIGRACIÓN DE CONFIRMATION_BY_USER:';
PRINT '  - Los valores VARCHAR se convierten automáticamente a DATE';
PRINT '  - Migración simple y segura usando ALTER COLUMN';
PRINT '=====================================================';
PRINT 'ARQUITECTURA HÍBRIDA IMPLEMENTADA:';
PRINT '  - Consultas simples: Manejadas directamente en Python';
PRINT '  - Lógica compleja: Procedimientos almacenados en SQL Server';
PRINT '  - Balance óptimo entre flexibilidad y rendimiento';
PRINT '=====================================================';

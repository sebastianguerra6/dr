-- =====================================================
-- SCRIPT DE CONFIGURACIÓN CORREGIDO PARA SQL SERVER
-- Sistema de Gestión de Empleados y Conciliación de Accesos
-- =====================================================

-- Crear base de datos si no existe
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'GAMLO_Empleados')
BEGIN
    CREATE DATABASE GAMLO_Empleados;
    PRINT 'Base de datos GAMLO_Empleados creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Base de datos GAMLO_Empleados ya existe';
END
GO

USE GAMLO_Empleados;
GO

-- =====================================================
-- TABLA 1: HEADCOUNT (Empleados)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[headcount]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[headcount] (
        [scotia_id] VARCHAR(20) NOT NULL PRIMARY KEY,
        [employee] VARCHAR(100) NOT NULL,
        [full_name] VARCHAR(150) NOT NULL,
        [email] VARCHAR(150) NOT NULL,
        [position] VARCHAR(100) NULL,
        [manager] VARCHAR(100) NULL,
        [senior_manager] VARCHAR(100) NULL,
        [unit] VARCHAR(100) NULL,
        [unidad_subunidad] VARCHAR(150) NULL,
        [start_date] DATE NULL,
        [ceco] VARCHAR(100) NULL,
        [skip_level] VARCHAR(100) NULL,
        [cafe_alcides] VARCHAR(100) NULL,
        [parents] VARCHAR(100) NULL,
        [personal_email] VARCHAR(150) NULL,
        [size] VARCHAR(50) NULL,
        [birthday] DATE NULL,
        [validacion] VARCHAR(100) NULL,
        [activo] BIT NOT NULL DEFAULT 1,
        [inactivation_date] DATE NULL
    );
    PRINT 'Tabla headcount creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla headcount ya existe';
    -- Agregar columna unidad_subunidad si no existe
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[headcount]') AND name = 'unidad_subunidad')
    BEGIN
        ALTER TABLE [dbo].[headcount]
        ADD [unidad_subunidad] VARCHAR(150) NULL;
        PRINT 'Columna unidad_subunidad agregada a la tabla headcount';
    END
END
GO

-- =====================================================
-- TABLA 2: APPLICATIONS (Aplicaciones y Accesos)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[applications]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[applications] (
        [id] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [jurisdiction] VARCHAR(100) NULL,
        [unit] VARCHAR(100) NULL,
        [subunit] VARCHAR(100) NULL,
        [unidad_subunidad] VARCHAR(150) NULL,
        [logical_access_name] VARCHAR(150) NOT NULL,
        [alias] VARCHAR(150) NULL,
        [path_email_url] VARCHAR(255) NULL,
        [position_role] VARCHAR(100) NULL,
        [exception_tracking] VARCHAR(255) NULL,
        [fulfillment_action] VARCHAR(255) NULL,
        [system_owner] VARCHAR(100) NULL,
        [role_name] VARCHAR(100) NULL,
        [access_type] VARCHAR(50) NULL,
        [category] VARCHAR(100) NULL,
        [additional_data] VARCHAR(255) NULL,
        [ad_code] VARCHAR(100) NULL,
        [access_status] VARCHAR(50) NULL,
        [last_update_date] DATETIME2 NULL,
        [require_licensing] VARCHAR(255) NULL,
        [description] NVARCHAR(MAX) NULL,
        [authentication_method] VARCHAR(100) NULL
    );
    PRINT 'Tabla applications creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla applications ya existe';
    -- Agregar columna unidad_subunidad si no existe
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[applications]') AND name = 'unidad_subunidad')
    BEGIN
        ALTER TABLE [dbo].[applications]
        ADD [unidad_subunidad] VARCHAR(150) NULL;
        PRINT 'Columna unidad_subunidad agregada a la tabla applications';
    END
END
GO

-- =====================================================
-- TABLA 3: HISTORICO (Historial de Procesos)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[historico]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[historico] (
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
    PRINT 'Tabla historico creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla historico ya existe';
    -- Agregar campos faltantes si no existen
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[historico]') AND name = 'duration_of_access')
    BEGIN
        ALTER TABLE [dbo].[historico] ADD [duration_of_access] VARCHAR(50) NULL;
        PRINT 'Columna duration_of_access agregada a la tabla historico';
    END
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[historico]') AND name = 'comment_tq')
    BEGIN
        ALTER TABLE [dbo].[historico] ADD [comment_tq] NVARCHAR(MAX) NULL;
        PRINT 'Columna comment_tq agregada a la tabla historico';
    END
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[historico]') AND name = 'general_status_ticket')
    BEGIN
        ALTER TABLE [dbo].[historico] ADD [general_status_ticket] VARCHAR(50) NULL;
        PRINT 'Columna general_status_ticket agregada a la tabla historico';
    END
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[historico]') AND name = 'general_status_case')
    BEGIN
        ALTER TABLE [dbo].[historico] ADD [general_status_case] VARCHAR(50) NULL;
        PRINT 'Columna general_status_case agregada a la tabla historico';
    END
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[historico]') AND name = 'sla_app')
    BEGIN
        ALTER TABLE [dbo].[historico] ADD [sla_app] VARCHAR(50) NULL;
        PRINT 'Columna sla_app agregada a la tabla historico';
    END
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[historico]') AND name = 'sla_ticket')
    BEGIN
        ALTER TABLE [dbo].[historico] ADD [sla_ticket] VARCHAR(50) NULL;
        PRINT 'Columna sla_ticket agregada a la tabla historico';
    END
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[historico]') AND name = 'sla_case')
    BEGIN
        ALTER TABLE [dbo].[historico] ADD [sla_case] VARCHAR(50) NULL;
        PRINT 'Columna sla_case agregada a la tabla historico';
    END
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[historico]') AND name = 'employee_email')
    BEGIN
        ALTER TABLE [dbo].[historico] ADD [employee_email] VARCHAR(150) NULL;
        PRINT 'Columna employee_email agregada a la tabla historico';
    END
    -- Eliminar campos que sobran si existen
    IF EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[historico]') AND name = 'sid')
    BEGIN
        ALTER TABLE [dbo].[historico] DROP COLUMN [sid];
        PRINT 'Columna sid eliminada de la tabla historico';
    END
    IF EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[historico]') AND name = 'area')
    BEGIN
        ALTER TABLE [dbo].[historico] DROP COLUMN [area];
        PRINT 'Columna area eliminada de la tabla historico';
    END
END
GO

-- =====================================================
-- TABLA 4: PROCESOS (Gestión de Procesos)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[procesos]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[procesos] (
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
        [confirmation_by_user] VARCHAR(50) NULL,
        [comment] NVARCHAR(MAX) NULL
    );
    PRINT 'Tabla procesos creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla procesos ya existe';
END
GO

-- =====================================================
-- CREAR FOREIGN KEYS DESPUÉS DE CREAR TODAS LAS TABLAS
-- =====================================================

-- Foreign Key para historico -> headcount
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_historico_headcount')
BEGIN
    ALTER TABLE [dbo].[historico]
    ADD CONSTRAINT [FK_historico_headcount] 
    FOREIGN KEY ([scotia_id]) REFERENCES [dbo].[headcount]([scotia_id]) ON DELETE CASCADE;
    PRINT 'Foreign Key FK_historico_headcount creada exitosamente';
END
GO

-- Foreign Key para historico -> applications
-- COMENTADO: No se puede crear porque logical_access_name no es UNIQUE
-- IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_historico_applications')
-- BEGIN
--     ALTER TABLE [dbo].[historico]
--     ADD CONSTRAINT [FK_historico_applications] 
--     FOREIGN KEY ([app_access_name]) REFERENCES [dbo].[applications]([logical_access_name]) ON DELETE SET NULL;
--     PRINT 'Foreign Key FK_historico_applications creada exitosamente';
-- END
PRINT 'Foreign Key FK_historico_applications omitida: logical_access_name no es UNIQUE en applications';
GO

-- Foreign Key para procesos -> headcount
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_procesos_headcount')
BEGIN
    ALTER TABLE [dbo].[procesos]
    ADD CONSTRAINT [FK_procesos_headcount] 
    FOREIGN KEY ([sid]) REFERENCES [dbo].[headcount]([scotia_id]) ON DELETE CASCADE;
    PRINT 'Foreign Key FK_procesos_headcount creada exitosamente';
END
GO

-- =====================================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- =====================================================

-- Índices para headcount
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_headcount_unit_position' AND object_id = OBJECT_ID(N'[dbo].[headcount]'))
BEGIN
    CREATE INDEX IX_headcount_unit_position ON [dbo].[headcount] ([unit], [position]);
    PRINT 'Índice IX_headcount_unit_position creado exitosamente';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_headcount_unidad_subunidad_position' AND object_id = OBJECT_ID(N'[dbo].[headcount]'))
BEGIN
    CREATE INDEX IX_headcount_unidad_subunidad_position ON [dbo].[headcount] ([unidad_subunidad], [position]);
    PRINT 'Índice IX_headcount_unidad_subunidad_position creado exitosamente';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_headcount_activo' AND object_id = OBJECT_ID(N'[dbo].[headcount]'))
BEGIN
    CREATE INDEX IX_headcount_activo ON [dbo].[headcount] ([activo]);
    PRINT 'Índice IX_headcount_activo creado exitosamente';
END
GO

-- Índices para applications
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_applications_unit_position' AND object_id = OBJECT_ID(N'[dbo].[applications]'))
BEGIN
    CREATE INDEX IX_applications_unit_position ON [dbo].[applications] ([unit], [position_role]);
    PRINT 'Índice IX_applications_unit_position creado exitosamente';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_applications_unidad_subunidad_position' AND object_id = OBJECT_ID(N'[dbo].[applications]'))
BEGIN
    CREATE INDEX IX_applications_unidad_subunidad_position ON [dbo].[applications] ([unidad_subunidad], [position_role]);
    PRINT 'Índice IX_applications_unidad_subunidad_position creado exitosamente';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_applications_access_status' AND object_id = OBJECT_ID(N'[dbo].[applications]'))
BEGIN
    CREATE INDEX IX_applications_access_status ON [dbo].[applications] ([access_status]);
    PRINT 'Índice IX_applications_access_status creado exitosamente';
END
GO

-- Índices para historico
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_historico_scotia_status' AND object_id = OBJECT_ID(N'[dbo].[historico]'))
BEGIN
    CREATE INDEX IX_historico_scotia_status ON [dbo].[historico] ([scotia_id], [status]);
    PRINT 'Índice IX_historico_scotia_status creado exitosamente';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_historico_process_status' AND object_id = OBJECT_ID(N'[dbo].[historico]'))
BEGIN
    CREATE INDEX IX_historico_process_status ON [dbo].[historico] ([process_access], [status]);
    PRINT 'Índice IX_historico_process_status creado exitosamente';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_historico_record_date' AND object_id = OBJECT_ID(N'[dbo].[historico]'))
BEGIN
    CREATE INDEX IX_historico_record_date ON [dbo].[historico] ([record_date]);
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
        WHERE access_status = ''Activo''
    ) a ON 
        UPPER(LTRIM(RTRIM(h.unidad_subunidad))) = UPPER(LTRIM(RTRIM(a.unidad_subunidad))) AND
        UPPER(LTRIM(RTRIM(h.position))) = UPPER(LTRIM(RTRIM(a.position_role)))
    WHERE h.activo = 1
    GROUP BY h.scotia_id, a.logical_access_name, h.unit, h.unidad_subunidad, h.position, a.subunit, a.position_role, 
             a.role_name, a.system_owner, a.access_type, a.category, a.description');
    PRINT 'Vista vw_required_apps creada exitosamente';
END
ELSE
BEGIN
    -- Actualizar vista existente
    EXEC('ALTER VIEW [dbo].[vw_required_apps] AS
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
        WHERE access_status = ''Activo''
    ) a ON 
        UPPER(LTRIM(RTRIM(h.unidad_subunidad))) = UPPER(LTRIM(RTRIM(a.unidad_subunidad))) AND
        UPPER(LTRIM(RTRIM(h.position))) = UPPER(LTRIM(RTRIM(a.position_role)))
    WHERE h.activo = 1
    GROUP BY h.scotia_id, a.logical_access_name, h.unit, h.unidad_subunidad, h.position, a.subunit, a.position_role, 
             a.role_name, a.system_owner, a.access_type, a.category, a.description');
    PRINT 'Vista vw_required_apps actualizada exitosamente';
END
GO

-- Vista para accesos actuales
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'vw_current_access')
BEGIN
    EXEC('CREATE VIEW [dbo].[vw_current_access] AS
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
    WHERE h.status = ''Completado''
    AND h.process_access IN (''onboarding'', ''lateral_movement'')
    AND head.activo = 1
    AND h.app_access_name IS NOT NULL
    GROUP BY h.scotia_id, h.app_access_name, head.unit, head.position, h.subunit, h.record_date, h.status');
    PRINT 'Vista vw_current_access creada exitosamente';
END
ELSE
BEGIN
    -- Actualizar vista existente
    EXEC('ALTER VIEW [dbo].[vw_current_access] AS
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
    WHERE h.status = ''Completado''
    AND h.process_access IN (''onboarding'', ''lateral_movement'')
    AND head.activo = 1
    AND h.app_access_name IS NOT NULL
    GROUP BY h.scotia_id, h.app_access_name, head.unit, head.position, h.subunit, h.record_date, h.status');
    PRINT 'Vista vw_current_access actualizada exitosamente';
END
GO

-- Vista para accesos por otorgar
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'vw_to_grant')
BEGIN
    EXEC('CREATE VIEW [dbo].[vw_to_grant] AS
    SELECT 
        req.scotia_id,
        req.unit,
        req.position,
        req.logical_access_name,
        req.subunit,
        req.position_role,
        ''onboarding'' as process_type
    FROM [dbo].[vw_required_apps] req
    LEFT JOIN [dbo].[vw_current_access] curr ON 
        req.scotia_id = curr.scotia_id AND
        UPPER(LTRIM(RTRIM(req.logical_access_name))) = UPPER(LTRIM(RTRIM(curr.logical_access_name))) AND
        UPPER(LTRIM(RTRIM(req.unit))) = UPPER(LTRIM(RTRIM(curr.unit))) AND
        UPPER(LTRIM(RTRIM(req.position))) = UPPER(LTRIM(RTRIM(curr.position)))
    WHERE curr.scotia_id IS NULL');
    PRINT 'Vista vw_to_grant creada exitosamente';
END
ELSE
BEGIN
    -- Actualizar vista existente
    EXEC('ALTER VIEW [dbo].[vw_to_grant] AS
    SELECT 
        req.scotia_id,
        req.unit,
        req.position,
        req.logical_access_name,
        req.subunit,
        req.position_role,
        ''onboarding'' as process_type
    FROM [dbo].[vw_required_apps] req
    LEFT JOIN [dbo].[vw_current_access] curr ON 
        req.scotia_id = curr.scotia_id AND
        UPPER(LTRIM(RTRIM(req.logical_access_name))) = UPPER(LTRIM(RTRIM(curr.logical_access_name))) AND
        UPPER(LTRIM(RTRIM(req.unit))) = UPPER(LTRIM(RTRIM(curr.unit))) AND
        UPPER(LTRIM(RTRIM(req.position))) = UPPER(LTRIM(RTRIM(curr.position)))
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
        curr.unit,
        curr.position,
        curr.logical_access_name,
        curr.subunit,
        curr.position_role,
        curr.record_date,
        ''offboarding'' as process_type
    FROM [dbo].[vw_current_access] curr
    LEFT JOIN [dbo].[vw_required_apps] req ON 
        curr.scotia_id = req.scotia_id AND
        UPPER(LTRIM(RTRIM(curr.logical_access_name))) = UPPER(LTRIM(RTRIM(req.logical_access_name))) AND
        UPPER(LTRIM(RTRIM(curr.unit))) = UPPER(LTRIM(RTRIM(req.unit))) AND
        UPPER(LTRIM(RTRIM(curr.position))) = UPPER(LTRIM(RTRIM(req.position)))
    WHERE req.scotia_id IS NULL');
    PRINT 'Vista vw_to_revoke creada exitosamente';
END
ELSE
BEGIN
    -- Actualizar vista existente
    EXEC('ALTER VIEW [dbo].[vw_to_revoke] AS
    SELECT 
        curr.scotia_id,
        curr.unit,
        curr.position,
        curr.logical_access_name,
        curr.subunit,
        curr.position_role,
        curr.record_date,
        ''offboarding'' as process_type
    FROM [dbo].[vw_current_access] curr
    LEFT JOIN [dbo].[vw_required_apps] req ON 
        curr.scotia_id = req.scotia_id AND
        UPPER(LTRIM(RTRIM(curr.logical_access_name))) = UPPER(LTRIM(RTRIM(req.logical_access_name))) AND
        UPPER(LTRIM(RTRIM(curr.unit))) = UPPER(LTRIM(RTRIM(req.unit))) AND
        UPPER(LTRIM(RTRIM(curr.position))) = UPPER(LTRIM(RTRIM(req.position)))
    WHERE req.scotia_id IS NULL');
    PRINT 'Vista vw_to_revoke actualizada exitosamente';
END
GO

-- Vista para estadísticas del sistema
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'vw_system_stats')
BEGIN
    EXEC('CREATE VIEW [dbo].[vw_system_stats] AS
    SELECT 
        (SELECT COUNT(*) FROM [dbo].[headcount] WHERE activo = 1) as empleados_activos,
        (SELECT COUNT(*) FROM [dbo].[applications] WHERE access_status = ''Activo'') as aplicaciones_activas,
        (SELECT COUNT(*) FROM [dbo].[historico]) as total_historico,
        (SELECT COUNT(*) FROM [dbo].[procesos]) as total_procesos,
        (SELECT COUNT(*) FROM [dbo].[headcount]) as total_empleados,
        (SELECT COUNT(*) FROM [dbo].[applications]) as total_aplicaciones');
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
            ''headcount'' as tabla, COUNT(*) as registros FROM [dbo].[headcount]
        UNION ALL
        SELECT ''applications'' as tabla, COUNT(*) as registros FROM [dbo].[applications]
        UNION ALL
        SELECT ''historico'' as tabla, COUNT(*) as registros FROM [dbo].[historico]
        UNION ALL
        SELECT ''procesos'' as tabla, COUNT(*) as registros FROM [dbo].[procesos];
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
        FROM [dbo].[historico] h
        LEFT JOIN (
            SELECT 
                logical_access_name,
                description,
                unit,
                subunit,
                position_role,
                category,
                ROW_NUMBER() OVER (PARTITION BY logical_access_name ORDER BY id) as rn
            FROM [dbo].[applications]
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
        FROM [dbo].[applications]
        WHERE access_status = ''Activo''
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

-- Insertar datos de ejemplo en headcount
IF NOT EXISTS (SELECT * FROM headcount WHERE scotia_id = 'EMP001')
BEGIN
    INSERT INTO [dbo].[headcount] (scotia_id, employee, full_name, email, position, manager, senior_manager, unit, unidad_subunidad, start_date, ceco, skip_level, cafe_alcides, parents, personal_email, size, birthday, validacion, activo, inactivation_date)
    VALUES 
        ('EMP001', 'Juan Pérez', 'Juan Carlos Pérez García', 'juan.perez@empresa.com', 'Analista', 'María González', 'Carlos López', 'Tecnología', 'Tecnología/Desarrollo', '2023-01-15', 'CECO001', 'Nivel 1', 'Café 1', 'Padres', 'juan.personal@gmail.com', 'M', '1985-05-20', 'Validado', 1, NULL),
        ('EMP002', 'María González', 'María Elena González López', 'maria.gonzalez@empresa.com', 'Analista Senior', 'Carlos López', 'Ana Martínez', 'Tecnología', 'Tecnología/Desarrollo', '2022-03-10', 'CECO002', 'Nivel 2', 'Café 2', 'Padres', 'maria.personal@gmail.com', 'L', '1980-08-15', 'Validado', 1, NULL),
        ('EMP003', 'Carlos López', 'Carlos Alberto López Martínez', 'carlos.lopez@empresa.com', 'Gerente', 'Ana Martínez', 'Director', 'Tecnología', 'Tecnología/Desarrollo', '2021-06-01', 'CECO003', 'Nivel 3', 'Café 3', 'Padres', 'carlos.personal@gmail.com', 'XL', '1975-12-03', 'Validado', 1, NULL);
    PRINT 'Datos de ejemplo insertados en headcount';
END
GO

-- Insertar datos de ejemplo en applications
IF NOT EXISTS (SELECT * FROM applications WHERE logical_access_name = 'Sistema de Gestión')
BEGIN
    INSERT INTO [dbo].[applications] (jurisdiction, unit, subunit, unidad_subunidad, logical_access_name, alias, path_email_url, position_role, exception_tracking, fulfillment_action, system_owner, role_name, access_type, category, additional_data, ad_code, access_status, last_update_date, require_licensing, description, authentication_method)
    VALUES 
        -- TECNOLOGÍA - ANALISTA
        ('Global', 'Tecnología', 'Desarrollo', 'Tecnología/Desarrollo', 'Sistema de Gestión', 'SIS-GEST', 'https://sistema.empresa.com', 'Analista', 'TRK001', 'Crear usuario', 'Admin Sistema', 'Usuario', 'Aplicación', 'Sistemas', 'Datos adicionales', 'AD001', 'Activo', GETDATE(), 'Licencia estándar', 'Sistema principal de gestión empresarial', 'LDAP'),
        ('Global', 'Tecnología', 'Desarrollo', 'Tecnología/Desarrollo', 'GitLab', 'GIT-REPO', 'https://gitlab.empresa.com', 'Analista', 'TRK002', 'Crear usuario', 'Admin GitLab', 'Developer', 'Aplicación', 'Desarrollo', 'Datos adicionales', 'AD002', 'Activo', GETDATE(), 'Licencia estándar', 'Repositorio de código fuente', 'LDAP'),
        ('Global', 'Tecnología', 'Desarrollo', 'Tecnología/Desarrollo', 'Jira', 'JIRA-PROJ', 'https://jira.empresa.com', 'Analista', 'TRK003', 'Asignar acceso', 'Admin Jira', 'Developer', 'Aplicación', 'Gestión', 'Datos adicionales', 'AD003', 'Activo', GETDATE(), 'Licencia estándar', 'Gestión de proyectos y tickets', 'LDAP'),
        
        -- TECNOLOGÍA - ANALISTA SENIOR
        ('Global', 'Tecnología', 'Desarrollo', 'Tecnología/Desarrollo', 'Sistema de Gestión', 'SIS-GEST-ADM', 'https://sistema.empresa.com', 'Analista Senior', 'TRK004', 'Crear usuario', 'Admin Sistema', 'Administrador', 'Aplicación', 'Sistemas', 'Datos adicionales', 'AD004', 'Activo', GETDATE(), 'Licencia premium', 'Sistema principal de gestión empresarial', 'LDAP'),
        ('Global', 'Tecnología', 'Desarrollo', 'Tecnología/Desarrollo', 'GitLab', 'GIT-REPO-ADM', 'https://gitlab.empresa.com', 'Analista Senior', 'TRK005', 'Crear usuario', 'Admin GitLab', 'Maintainer', 'Aplicación', 'Desarrollo', 'Datos adicionales', 'AD005', 'Activo', GETDATE(), 'Licencia premium', 'Repositorio de código fuente', 'LDAP'),
        ('Global', 'Tecnología', 'Desarrollo', 'Tecnología/Desarrollo', 'Jira', 'JIRA-PROJ-ADM', 'https://jira.empresa.com', 'Analista Senior', 'TRK006', 'Asignar acceso', 'Admin Jira', 'Project Lead', 'Aplicación', 'Gestión', 'Datos adicionales', 'AD006', 'Activo', GETDATE(), 'Licencia premium', 'Gestión de proyectos y tickets', 'LDAP'),
        ('Global', 'Tecnología', 'Desarrollo', 'Tecnología/Desarrollo', 'Docker Registry', 'DOCK-REG', 'https://registry.empresa.com', 'Analista Senior', 'TRK007', 'Crear usuario', 'Admin Docker', 'Maintainer', 'Aplicación', 'DevOps', 'Datos adicionales', 'AD007', 'Activo', GETDATE(), 'Licencia premium', 'Registro de contenedores Docker', 'LDAP'),
        
        -- TECNOLOGÍA - GERENTE
        ('Global', 'Tecnología', 'Desarrollo', 'Tecnología/Desarrollo', 'Sistema de Gestión', 'SIS-GEST-MGR', 'https://sistema.empresa.com', 'Gerente', 'TRK008', 'Crear usuario', 'Admin Sistema', 'Manager', 'Aplicación', 'Sistemas', 'Datos adicionales', 'AD008', 'Activo', GETDATE(), 'Licencia premium', 'Sistema principal de gestión empresarial', 'LDAP'),
        ('Global', 'Tecnología', 'Desarrollo', 'Tecnología/Desarrollo', 'GitLab', 'GIT-REPO-MGR', 'https://gitlab.empresa.com', 'Gerente', 'TRK009', 'Crear usuario', 'Admin GitLab', 'Owner', 'Aplicación', 'Desarrollo', 'Datos adicionales', 'AD009', 'Activo', GETDATE(), 'Licencia premium', 'Repositorio de código fuente', 'LDAP'),
        ('Global', 'Tecnología', 'Desarrollo', 'Tecnología/Desarrollo', 'Jira', 'JIRA-PROJ-MGR', 'https://jira.empresa.com', 'Gerente', 'TRK010', 'Asignar acceso', 'Admin Jira', 'Administrator', 'Aplicación', 'Gestión', 'Datos adicionales', 'AD010', 'Activo', GETDATE(), 'Licencia premium', 'Gestión de proyectos y tickets', 'LDAP'),
        ('Global', 'Tecnología', 'Desarrollo', 'Tecnología/Desarrollo', 'Power BI', 'POWER-BI', 'https://powerbi.empresa.com', 'Gerente', 'TRK011', 'Crear usuario', 'Admin PowerBI', 'Admin', 'Aplicación', 'Analytics', 'Datos adicionales', 'AD011', 'Activo', GETDATE(), 'Licencia premium', 'Herramienta de análisis de datos', 'LDAP'),
        
        -- RECURSOS HUMANOS - ANALISTA
        ('Global', 'Recursos Humanos', 'RRHH', 'Recursos Humanos/RRHH', 'Sistema de Gestión', 'SIS-GEST-RRHH', 'https://sistema.empresa.com', 'Analista', 'TRK015', 'Crear usuario', 'Admin Sistema', 'Usuario', 'Aplicación', 'Sistemas', 'Datos adicionales', 'AD015', 'Activo', GETDATE(), 'Licencia estándar', 'Sistema principal de gestión empresarial', 'LDAP'),
        ('Global', 'Recursos Humanos', 'RRHH', 'Recursos Humanos/RRHH', 'Workday', 'WD-RRHH', 'https://workday.empresa.com', 'Analista', 'TRK016', 'Crear usuario', 'Admin Workday', 'Analyst', 'Aplicación', 'RRHH', 'Datos adicionales', 'AD016', 'Activo', GETDATE(), 'Licencia estándar', 'Sistema de gestión de RRHH', 'LDAP'),
        ('Global', 'Recursos Humanos', 'RRHH', 'Recursos Humanos/RRHH', 'SuccessFactors', 'SF-RRHH', 'https://successfactors.empresa.com', 'Analista', 'TRK017', 'Crear usuario', 'Admin SuccessFactors', 'Analyst', 'Aplicación', 'RRHH', 'Datos adicionales', 'AD017', 'Activo', GETDATE(), 'Licencia estándar', 'Gestión de talento y rendimiento', 'LDAP'),
        
        -- RECURSOS HUMANOS - GERENTE
        ('Global', 'Recursos Humanos', 'RRHH', 'Recursos Humanos/RRHH', 'Sistema de Gestión', 'SIS-GEST-RRHH-MGR', 'https://sistema.empresa.com', 'Gerente', 'TRK018', 'Crear usuario', 'Admin Sistema', 'Manager', 'Aplicación', 'Sistemas', 'Datos adicionales', 'AD018', 'Activo', GETDATE(), 'Licencia premium', 'Sistema principal de gestión empresarial', 'LDAP'),
        ('Global', 'Recursos Humanos', 'RRHH', 'Recursos Humanos/RRHH', 'Workday', 'WD-RRHH-MGR', 'https://workday.empresa.com', 'Gerente', 'TRK019', 'Crear usuario', 'Admin Workday', 'Manager', 'Aplicación', 'RRHH', 'Datos adicionales', 'AD019', 'Activo', GETDATE(), 'Licencia premium', 'Sistema de gestión de RRHH', 'LDAP'),
        ('Global', 'Recursos Humanos', 'RRHH', 'Recursos Humanos/RRHH', 'SuccessFactors', 'SF-RRHH-MGR', 'https://successfactors.empresa.com', 'Gerente', 'TRK020', 'Crear usuario', 'Admin SuccessFactors', 'Manager', 'Aplicación', 'RRHH', 'Datos adicionales', 'AD020', 'Activo', GETDATE(), 'Licencia premium', 'Gestión de talento y rendimiento', 'LDAP');
    PRINT 'Datos de ejemplo insertados en applications';
END
GO

-- Insertar datos de ejemplo en historico
IF NOT EXISTS (SELECT * FROM historico WHERE scotia_id = 'EMP001')
BEGIN
    INSERT INTO [dbo].[historico] (scotia_id, case_id, responsible, record_date, request_date, process_access, subunit, event_description, ticket_email, app_access_name, computer_system_type, duration_of_access, status, closing_date_app, closing_date_ticket, app_quality, confirmation_by_user, comment, comment_tq, ticket_quality, general_status_ticket, general_status_case, average_time_open_ticket, sla_app, sla_ticket, sla_case)
    VALUES 
        ('EMP001', 'CASE-20240115-001', 'Admin Sistema', GETDATE(), '2024-01-14', 'onboarding', 'Tecnología/Desarrollo', 'Usuario creado en sistema', 'admin@empresa.com', 'Sistema de Gestión', 'Sistemas', 'Permanente', 'Completado', '2024-01-15', '2024-01-15', 'Excelente', '2024-01-16', 'Usuario creado exitosamente', 'Ticket completado satisfactoriamente', 'Excelente', 'Completado', 'Completado', '00:30:00', 'Cumplido', 'Cumplido', 'Cumplido'),
        ('EMP002', 'CASE-20240115-002', 'Admin Portal', GETDATE(), '2024-01-14', 'onboarding', 'Tecnología/Desarrollo', 'Usuario creado en portal', 'admin@empresa.com', 'GitLab', 'Desarrollo', 'Permanente', 'Completado', '2024-01-15', '2024-01-15', 'Excelente', '2024-01-16', 'Usuario creado exitosamente', 'Ticket completado satisfactoriamente', 'Excelente', 'Completado', 'Completado', '00:45:00', 'Cumplido', 'Cumplido', 'Cumplido'),
        ('EMP003', 'CASE-20240115-003', 'Admin Sistema', GETDATE(), '2024-01-14', 'onboarding', 'Tecnología/Desarrollo', 'Usuario creado en sistema', 'admin@empresa.com', 'Jira', 'Gestión', 'Permanente', 'Completado', '2024-01-15', '2024-01-15', 'Excelente', '2024-01-16', 'Usuario creado exitosamente', 'Ticket completado satisfactoriamente', 'Excelente', 'Completado', 'Completado', '00:20:00', 'Cumplido', 'Cumplido', 'Cumplido');
    PRINT 'Datos de ejemplo insertados en historico';
END
GO

-- =====================================================
-- MIGRACIÓN SIMPLE PARA CONFIRMATION_BY_USER
-- =====================================================

-- Migrar confirmation_by_user de VARCHAR a DATE en tabla historico
IF EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[historico]') AND name = 'confirmation_by_user' AND system_type_id = 167)
BEGIN
    PRINT 'Migrando confirmation_by_user de VARCHAR a DATE en tabla historico...';
    ALTER TABLE [dbo].[historico] ALTER COLUMN [confirmation_by_user] DATE NULL;
    PRINT 'Migración de historico completada';
END
ELSE
BEGIN
    PRINT 'confirmation_by_user en historico ya es DATE o no existe';
END
GO

-- Migrar confirmation_by_user de VARCHAR a DATE en tabla procesos
IF EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[procesos]') AND name = 'confirmation_by_user' AND system_type_id = 167)
BEGIN
    PRINT 'Migrando confirmation_by_user de VARCHAR a DATE en tabla procesos...';
    ALTER TABLE [dbo].[procesos] ALTER COLUMN [confirmation_by_user] DATE NULL;
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
    FROM [dbo].[headcount] 
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
    FROM [dbo].[historico] h
    LEFT JOIN [dbo].[applications] a ON h.app_access_name = a.logical_access_name
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
    FROM [dbo].[applications] a
    WHERE a.access_status = 'Activo'
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
    UPDATE [dbo].[headcount] 
    SET activo = 1, inactivation_date = NULL
    WHERE scotia_id = @scotia_id;
    
    -- Actualizar posición, unidad y unidad_subunidad si están vacías
    UPDATE [dbo].[headcount] 
    SET position = @position, unit = @unit, unidad_subunidad = @unidad_subunidad
    WHERE scotia_id = @scotia_id 
    AND (position IS NULL OR position = '' OR unit IS NULL OR unit = '' OR unidad_subunidad IS NULL OR unidad_subunidad = '');
    
    -- Obtener aplicaciones requeridas y crear registros históricos
    INSERT INTO [dbo].[historico] (
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
    FROM [dbo].[applications] a
    WHERE a.access_status = 'Activo'
    AND a.unidad_subunidad = @unidad_subunidad
    AND a.position_role = @position
    AND NOT EXISTS (
        SELECT 1 FROM [dbo].[historico] h 
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
    UPDATE [dbo].[headcount] 
    SET activo = 0, inactivation_date = GETDATE()
    WHERE scotia_id = @scotia_id;
    
    -- Crear registros de offboarding para accesos activos
    INSERT INTO [dbo].[historico] (
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
    FROM [dbo].[historico] h
    LEFT JOIN [dbo].[applications] a ON h.app_access_name = a.logical_access_name
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
            (SELECT COUNT(*) FROM [dbo].[headcount] WHERE activo = 1) as empleados_activos,
            (SELECT COUNT(*) FROM [dbo].[applications] WHERE access_status = 'Activo') as aplicaciones_activas,
            (SELECT COUNT(*) FROM [dbo].[historico] WHERE status = 'Pendiente') as tickets_pendientes,
            (SELECT COUNT(*) FROM [dbo].[historico] WHERE status = 'Completado') as tickets_completados,
            (SELECT COUNT(*) FROM [dbo].[historico]) as total_historico;
    END
    ELSE
    BEGIN
        -- Estadísticas del empleado específico
        DECLARE @current_access INT, @to_grant INT, @to_revoke INT;
        
        SELECT @current_access = COUNT(DISTINCT app_access_name)
        FROM [dbo].[historico] 
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
SELECT 'headcount' as tabla, COUNT(*) as registros FROM [dbo].[headcount]
UNION ALL
SELECT 'applications' as tabla, COUNT(*) as registros FROM [dbo].[applications]
UNION ALL
SELECT 'historico' as tabla, COUNT(*) as registros FROM [dbo].[historico]
UNION ALL
SELECT 'procesos' as tabla, COUNT(*) as registros FROM [dbo].[procesos];

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
PRINT 'Base de datos: GAMLO_Empleados';
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

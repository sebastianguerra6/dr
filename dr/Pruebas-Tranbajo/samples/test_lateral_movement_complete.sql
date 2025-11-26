-- =====================================================
-- SCRIPT COMPLETO PARA PROBAR LATERAL MOVEMENT
-- =====================================================
-- Este script crea:
-- 1. Empleados en headcount (posición original y destino)
-- 2. Aplicaciones para diferentes posiciones/unidades
-- 3. Registros históricos iniciales (onboarding)
-- 4. Un registro de lateral movement para probar
-- =====================================================

SET NOCOUNT ON;

PRINT '=====================================================';
PRINT 'INICIANDO SCRIPT DE PRUEBA PARA LATERAL MOVEMENT';
PRINT '=====================================================';

-- =====================================================
-- PASO 1: CREAR EMPLEADOS EN HEADCOUNT
-- =====================================================
PRINT '';
PRINT 'PASO 1: Creando empleados en headcount...';

-- Empleado que va a hacer lateral movement (posición original)
IF NOT EXISTS (SELECT * FROM headcount WHERE scotia_id = 'LM001')
BEGIN
    INSERT INTO [dbo].[headcount] (
        scotia_id, full_name, email, position, manager, senior_manager,
        unit, unidad_subunidad, start_date, ceco, skip_level,
        cafe_alcides, parents, personal_email, size, birthday, validacion, activo
    ) VALUES (
        'LM001', 
        'Juan Pérez García',
        'juan.perez@empresa.com',
        'Analista',  -- Posición original
        'María López',
        'Carlos Rodríguez',
        'Tecnología/Desarrollo',
        'Tecnología/Desarrollo/Backend',
        '2024-01-15',
        'CC001',
        'Ana Martínez',
        'Café A1',
        'Padre: Pedro Pérez, Madre: Carmen García',
        'juan.perez.personal@gmail.com',
        'M',
        '1990-05-20',
        'Validado',
        1  -- Active
    );
    PRINT '  ✓ Empleado LM001 creado (Analista - Tecnología/Desarrollo/Backend)';
END
ELSE
BEGIN
    PRINT '  ⚠ Empleado LM001 ya existe';
END

-- Empleado de referencia para la posición destino (opcional)
IF NOT EXISTS (SELECT * FROM headcount WHERE scotia_id = 'LM002')
BEGIN
    INSERT INTO [dbo].[headcount] (
        scotia_id, full_name, email, position, manager, senior_manager,
        unit, unidad_subunidad, start_date, ceco, skip_level,
        cafe_alcides, parents, personal_email, size, birthday, validacion, activo
    ) VALUES (
        'LM002',
        'Ana Martínez Silva',
        'ana.martinez@empresa.com',
        'Analista Senior',  -- Posición destino para lateral movement
        'Carlos Rodríguez',
        'Laura Fernández',
        'Business Intelligence/Analytics',
        'Business Intelligence/Analytics/Data Science',
        '2023-06-10',
        'CC002',
        'Pedro Gómez',
        'Café B2',
        'Padre: Luis Martínez, Madre: Sofía Silva',
        'ana.martinez.personal@gmail.com',
        'M',
        '1988-09-15',
        'Validado',
        1  -- Active
    );
    PRINT '  ✓ Empleado LM002 creado (Analista Senior - Business Intelligence/Analytics/Data Science)';
END
ELSE
BEGIN
    PRINT '  ⚠ Empleado LM002 ya existe';
END

-- =====================================================
-- PASO 2: CREAR APLICACIONES PARA POSICIÓN ORIGINAL
-- =====================================================
PRINT '';
PRINT 'PASO 2: Creando aplicaciones para posición original (Analista - Tecnología/Desarrollo)...';

-- Aplicación 1: Para posición original
IF NOT EXISTS (SELECT * FROM applications WHERE logical_access_name = 'GitLab' AND position_role = 'Analista' AND unidad_subunidad = 'Tecnología/Desarrollo/Backend')
BEGIN
    INSERT INTO [dbo].[applications] (
        logical_access_name, unit, unidad_subunidad, position_role, subunit,
        role_name, system_owner, access_type, category, description,
        path_email_url, access_status
    ) VALUES (
        'GitLab',
        'Tecnología',
        'Tecnología/Desarrollo/Backend',
        'Analista',
        'Desarrollo',
        'Developer',
        'IT Operations',
        'Aplicación',
        'Herramientas de Desarrollo',
        'Plataforma de control de versiones Git',
        'gitlab@empresa.com',
        'Active'
    );
    PRINT '  ✓ Aplicación GitLab creada para Analista - Tecnología/Desarrollo/Backend';
END

-- Aplicación 2: Para posición original
IF NOT EXISTS (SELECT * FROM applications WHERE logical_access_name = 'Jira' AND position_role = 'Analista' AND unidad_subunidad = 'Tecnología/Desarrollo/Backend')
BEGIN
    INSERT INTO [dbo].[applications] (
        logical_access_name, unit, unidad_subunidad, position_role, subunit,
        role_name, system_owner, access_type, category, description,
        path_email_url, access_status
    ) VALUES (
        'Jira',
        'Tecnología',
        'Tecnología/Desarrollo/Backend',
        'Analista',
        'Desarrollo',
        'User',
        'Project Management',
        'Aplicación',
        'Gestión de Proyectos',
        'Herramienta de gestión de proyectos y seguimiento de issues',
        'jira@empresa.com',
        'Active'
    );
    PRINT '  ✓ Aplicación Jira creada para Analista - Tecnología/Desarrollo/Backend';
END

-- Aplicación 3: Para posición original
IF NOT EXISTS (SELECT * FROM applications WHERE logical_access_name = 'Docker Registry' AND position_role = 'Analista' AND unidad_subunidad = 'Tecnología/Desarrollo/Backend')
BEGIN
    INSERT INTO [dbo].[applications] (
        logical_access_name, unit, unidad_subunidad, position_role, subunit,
        role_name, system_owner, access_type, category, description,
        path_email_url, access_status
    ) VALUES (
        'Docker Registry',
        'Tecnología',
        'Tecnología/Desarrollo/Backend',
        'Analista',
        'Desarrollo',
        'Developer',
        'DevOps',
        'Aplicación',
        'Infraestructura',
        'Registro de contenedores Docker',
        'docker@empresa.com',
        'Active'
    );
    PRINT '  ✓ Aplicación Docker Registry creada para Analista - Tecnología/Desarrollo/Backend';
END

-- =====================================================
-- PASO 3: CREAR APLICACIONES PARA POSICIÓN DESTINO
-- =====================================================
PRINT '';
PRINT 'PASO 3: Creando aplicaciones para posición destino (Analista Senior - Business Intelligence/Analytics)...';

-- Aplicación 1: Para posición destino
IF NOT EXISTS (SELECT * FROM applications WHERE logical_access_name = 'Power BI' AND position_role = 'Analista Senior' AND unidad_subunidad = 'Business Intelligence/Analytics/Data Science')
BEGIN
    INSERT INTO [dbo].[applications] (
        logical_access_name, unit, unidad_subunidad, position_role, subunit,
        role_name, system_owner, access_type, category, description,
        path_email_url, access_status
    ) VALUES (
        'Power BI',
        'Business Intelligence',
        'Business Intelligence/Analytics/Data Science',
        'Analista Senior',
        'Analytics',
        'Data Analyst',
        'BI Team',
        'Aplicación',
        'Business Intelligence',
        'Plataforma de visualización y análisis de datos',
        'powerbi@empresa.com',
        'Active'
    );
    PRINT '  ✓ Aplicación Power BI creada para Analista Senior - Business Intelligence/Analytics/Data Science';
END

-- Aplicación 2: Para posición destino
IF NOT EXISTS (SELECT * FROM applications WHERE logical_access_name = 'Tableau' AND position_role = 'Analista Senior' AND unidad_subunidad = 'Business Intelligence/Analytics/Data Science')
BEGIN
    INSERT INTO [dbo].[applications] (
        logical_access_name, unit, unidad_subunidad, position_role, subunit,
        role_name, system_owner, access_type, category, description,
        path_email_url, access_status
    ) VALUES (
        'Tableau',
        'Business Intelligence',
        'Business Intelligence/Analytics/Data Science',
        'Analista Senior',
        'Analytics',
        'Analyst',
        'BI Team',
        'Aplicación',
        'Business Intelligence',
        'Herramienta de visualización de datos y dashboards',
        'tableau@empresa.com',
        'Active'
    );
    PRINT '  ✓ Aplicación Tableau creada para Analista Senior - Business Intelligence/Analytics/Data Science';
END

-- Aplicación 3: Para posición destino
IF NOT EXISTS (SELECT * FROM applications WHERE logical_access_name = 'Python Jupyter' AND position_role = 'Analista Senior' AND unidad_subunidad = 'Business Intelligence/Analytics/Data Science')
BEGIN
    INSERT INTO [dbo].[applications] (
        logical_access_name, unit, unidad_subunidad, position_role, subunit,
        role_name, system_owner, access_type, category, description,
        path_email_url, access_status
    ) VALUES (
        'Python Jupyter',
        'Business Intelligence',
        'Business Intelligence/Analytics/Data Science',
        'Analista Senior',
        'Analytics',
        'Data Scientist',
        'Data Engineering',
        'Aplicación',
        'Herramientas de Análisis',
        'Plataforma Jupyter para análisis de datos con Python',
        'jupyter@empresa.com',
        'Active'
    );
    PRINT '  ✓ Aplicación Python Jupyter creada para Analista Senior - Business Intelligence/Analytics/Data Science';
END

-- Aplicación 4: Compartida entre ambas posiciones (para probar mantenimiento)
IF NOT EXISTS (SELECT * FROM applications WHERE logical_access_name = 'Office 365' AND position_role = 'Analista Senior' AND unidad_subunidad = 'Business Intelligence/Analytics/Data Science')
BEGIN
    INSERT INTO [dbo].[applications] (
        logical_access_name, unit, unidad_subunidad, position_role, subunit,
        role_name, system_owner, access_type, category, description,
        path_email_url, access_status
    ) VALUES (
        'Office 365',
        'Business Intelligence',
        'Business Intelligence/Analytics/Data Science',
        'Analista Senior',
        'Analytics',
        'User',
        'IT Operations',
        'Aplicación',
        'Productividad',
        'Suite de productividad Microsoft Office 365',
        'office365@empresa.com',
        'Active'
    );
    PRINT '  ✓ Aplicación Office 365 creada para Analista Senior - Business Intelligence/Analytics/Data Science';
END

-- También crear Office 365 para la posición original (aplicación compartida)
IF NOT EXISTS (SELECT * FROM applications WHERE logical_access_name = 'Office 365' AND position_role = 'Analista' AND unidad_subunidad = 'Tecnología/Desarrollo/Backend')
BEGIN
    INSERT INTO [dbo].[applications] (
        logical_access_name, unit, unidad_subunidad, position_role, subunit,
        role_name, system_owner, access_type, category, description,
        path_email_url, access_status
    ) VALUES (
        'Office 365',
        'Tecnología',
        'Tecnología/Desarrollo/Backend',
        'Analista',
        'Desarrollo',
        'User',
        'IT Operations',
        'Aplicación',
        'Productividad',
        'Suite de productividad Microsoft Office 365',
        'office365@empresa.com',
        'Active'
    );
    PRINT '  ✓ Aplicación Office 365 creada para Analista - Tecnología/Desarrollo/Backend (compartida)';
END

-- =====================================================
-- PASO 4: CREAR REGISTROS HISTÓRICOS INICIALES (ONBOARDING)
-- =====================================================
PRINT '';
PRINT 'PASO 4: Creando registros históricos iniciales (onboarding para LM001)...';

-- Onboarding 1: GitLab
IF NOT EXISTS (SELECT * FROM historico WHERE scotia_id = 'LM001' AND app_access_name = 'GitLab' AND process_access = 'onboarding')
BEGIN
    INSERT INTO [dbo].[historico] (
        scotia_id, employee_email, case_id, responsible, record_date, request_date,
        process_access, subunit, event_description, ticket_email,
        app_access_name, computer_system_type, status,
        closing_date_app, closing_date_ticket, app_quality,
        confirmation_by_user, comment, ticket_quality,
        general_status_ticket, average_time_open_ticket
    ) VALUES (
        'LM001', 'juan.perez@empresa.com', 'ONB-LM001-001', 'Sistema', GETDATE(), GETDATE(),
        'onboarding', 'Desarrollo', 'Otorgamiento de acceso para GitLab', 'admin@empresa.com',
        'GitLab', 'Desktop', 'closed completed',
        GETDATE(), GETDATE(), 'Excelente',
        '2024-01-16', 'Acceso otorgado durante onboarding', 'Excelente',
        'Completado', '00:30:00'
    );
    PRINT '  ✓ Registro histórico creado: GitLab (onboarding)';
END

-- Onboarding 2: Jira
IF NOT EXISTS (SELECT * FROM historico WHERE scotia_id = 'LM001' AND app_access_name = 'Jira' AND process_access = 'onboarding')
BEGIN
    INSERT INTO [dbo].[historico] (
        scotia_id, employee_email, case_id, responsible, record_date, request_date,
        process_access, subunit, event_description, ticket_email,
        app_access_name, computer_system_type, status,
        closing_date_app, closing_date_ticket, app_quality,
        confirmation_by_user, comment, ticket_quality,
        general_status_ticket, average_time_open_ticket
    ) VALUES (
        'LM001', 'juan.perez@empresa.com', 'ONB-LM001-002', 'Sistema', GETDATE(), GETDATE(),
        'onboarding', 'Desarrollo', 'Otorgamiento de acceso para Jira', 'admin@empresa.com',
        'Jira', 'Desktop', 'closed completed',
        GETDATE(), GETDATE(), 'Excelente',
        '2024-01-16', 'Acceso otorgado durante onboarding', 'Excelente',
        'Completado', '00:25:00'
    );
    PRINT '  ✓ Registro histórico creado: Jira (onboarding)';
END

-- Onboarding 3: Docker Registry
IF NOT EXISTS (SELECT * FROM historico WHERE scotia_id = 'LM001' AND app_access_name = 'Docker Registry' AND process_access = 'onboarding')
BEGIN
    INSERT INTO [dbo].[historico] (
        scotia_id, employee_email, case_id, responsible, record_date, request_date,
        process_access, subunit, event_description, ticket_email,
        app_access_name, computer_system_type, status,
        closing_date_app, closing_date_ticket, app_quality,
        confirmation_by_user, comment, ticket_quality,
        general_status_ticket, average_time_open_ticket
    ) VALUES (
        'LM001', 'juan.perez@empresa.com', 'ONB-LM001-003', 'Sistema', GETDATE(), GETDATE(),
        'onboarding', 'Desarrollo', 'Otorgamiento de acceso para Docker Registry', 'admin@empresa.com',
        'Docker Registry', 'Desktop', 'closed completed',
        GETDATE(), GETDATE(), 'Buena',
        '2024-01-16', 'Acceso otorgado durante onboarding', 'Buena',
        'Completado', '00:35:00'
    );
    PRINT '  ✓ Registro histórico creado: Docker Registry (onboarding)';
END

-- Onboarding 4: Office 365 (compartida)
IF NOT EXISTS (SELECT * FROM historico WHERE scotia_id = 'LM001' AND app_access_name = 'Office 365' AND process_access = 'onboarding')
BEGIN
    INSERT INTO [dbo].[historico] (
        scotia_id, employee_email, case_id, responsible, record_date, request_date,
        process_access, subunit, event_description, ticket_email,
        app_access_name, computer_system_type, status,
        closing_date_app, closing_date_ticket, app_quality,
        confirmation_by_user, comment, ticket_quality,
        general_status_ticket, average_time_open_ticket
    ) VALUES (
        'LM001', 'juan.perez@empresa.com', 'ONB-LM001-004', 'Sistema', GETDATE(), GETDATE(),
        'onboarding', 'Desarrollo', 'Otorgamiento de acceso para Office 365', 'admin@empresa.com',
        'Office 365', 'Desktop', 'closed completed',
        GETDATE(), GETDATE(), 'Excelente',
        '2024-01-16', 'Acceso otorgado durante onboarding', 'Excelente',
        'Completado', '00:15:00'
    );
    PRINT '  ✓ Registro histórico creado: Office 365 (onboarding) - Aplicación compartida';
END

-- =====================================================
-- PASO 5: CREAR REGISTRO DE LATERAL MOVEMENT
-- =====================================================
PRINT '';
PRINT 'PASO 5: Creando registro de lateral movement...';

-- Registro de lateral movement (este es el que vas a procesar)
IF NOT EXISTS (SELECT * FROM historico WHERE scotia_id = 'LM001' AND process_access = 'lateral_movement' AND case_id LIKE 'LM-%')
BEGIN
    -- Actualizar posición del empleado en headcount (simulando el movimiento)
    UPDATE [dbo].[headcount]
    SET position = 'Analista Senior',
        unit = 'Business Intelligence/Analytics',
        unidad_subunidad = 'Business Intelligence/Analytics/Data Science'
    WHERE scotia_id = 'LM001';
    
    PRINT '  ✓ Posición del empleado LM001 actualizada en headcount: Analista → Analista Senior';
    PRINT '  ✓ Unidad actualizada: Tecnología/Desarrollo → Business Intelligence/Analytics';
    
    -- Crear registro de lateral movement (este registro indica el cambio)
    INSERT INTO [dbo].[historico] (
        scotia_id, employee_email, case_id, responsible, record_date, request_date,
        process_access, subunit, event_description, ticket_email,
        app_access_name, computer_system_type, status,
        closing_date_app, closing_date_ticket, app_quality,
        confirmation_by_user, comment, ticket_quality,
        general_status_ticket, average_time_open_ticket
    ) VALUES (
        'LM001', 'juan.perez@empresa.com', 'LM-20251027-LM001', 'Sistema', GETDATE(), GETDATE(),
        'lateral_movement', 'Analytics', 'Movimiento lateral: Analista (Tecnología/Desarrollo) → Analista Senior (Business Intelligence/Analytics)', 'admin@empresa.com',
        'Lateral Movement', 'Desktop', 'to validate',
        NULL, NULL, NULL,
        NULL, 'Movimiento lateral pendiente de procesamiento. Se deben otorgar accesos de nueva posición y revocar accesos obsoletos.', NULL,
        'En Proceso', NULL
    );
    PRINT '  ✓ Registro de lateral movement creado (status: to validate)';
END
ELSE
BEGIN
    PRINT '  ⚠ Registro de lateral movement ya existe';
END

-- =====================================================
-- RESUMEN
-- =====================================================
PRINT '';
PRINT '=====================================================';
PRINT 'SCRIPT COMPLETADO EXITOSAMENTE';
PRINT '=====================================================';
PRINT '';
PRINT 'Datos creados:';
PRINT '  - Empleados: 2 (LM001, LM002)';
PRINT '  - Aplicaciones posición original: 3 (GitLab, Jira, Docker Registry)';
PRINT '  - Aplicaciones posición destino: 4 (Power BI, Tableau, Python Jupyter, Office 365)';
PRINT '  - Aplicación compartida: 1 (Office 365)';
PRINT '  - Registros históricos: 4 (onboarding inicial)';
PRINT '  - Registro lateral movement: 1 (pendiente de procesar)';
PRINT '';
PRINT 'Estado del empleado LM001:';
PRINT '  - Posición actual: Analista Senior';
PRINT '  - Unidad: Business Intelligence/Analytics/Data Science';
PRINT '  - Accesos actuales: GitLab, Jira, Docker Registry, Office 365';
PRINT '  - Accesos esperados después del lateral movement:';
PRINT '    • Mantener: Office 365 (compartida)';
PRINT '    • Revocar: GitLab, Jira, Docker Registry (solo para posición original)';
PRINT '    • Otorgar: Power BI, Tableau, Python Jupyter (nueva posición)';
PRINT '';
PRINT 'Para probar el lateral movement:';
PRINT '  1. Busca el empleado LM001 en la aplicación';
PRINT '  2. Procesa el lateral movement desde la interfaz';
PRINT '  3. Verifica que se creen los registros correctos:';
PRINT '     - Revocaciones para GitLab, Jira, Docker Registry';
PRINT '     - Otorgamientos para Power BI, Tableau, Python Jupyter';
PRINT '     - Mantenimiento de Office 365';
PRINT '';
PRINT '=====================================================';


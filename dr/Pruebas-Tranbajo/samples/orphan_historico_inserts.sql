-- Orphan historico inserts: SIDs intentionally not present in headcount
-- Úsalo para probar que el sistema admite historiales sin registro en headcount
-- Ajusta las fechas si lo necesitas

SET NOCOUNT ON;

PRINT 'Insertando historiales huérfanos (sin headcount)...';

-- ORPH001 - acceso manual
INSERT INTO [dbo].[historico] (
    scotia_id, employee_email, case_id, responsible, record_date, request_date,
    process_access, subunit, event_description, ticket_email,
    app_access_name, computer_system_type, status,
    closing_date_app, closing_date_ticket, app_quality,
    confirmation_by_user, comment, ticket_quality,
    general_status_ticket, average_time_open_ticket
) VALUES (
    'ORPH001', NULL, 'MAN-20251027-0001', 'Tester', GETDATE(), NULL,
    'manual_access', 'N/A', 'Acceso manual otorgado por pruebas', 'tester@empresa.com',
    'Power BI', 'Desktop', 'closed completed',
    NULL, NULL, NULL,
    '2025-10-27', 'Carga de histórico manual para pruebas', NULL,
    'En Proceso', '00:10:00'
);

-- ORPH002 - onboarding histórico (app asignada)
INSERT INTO [dbo].[historico] (
    scotia_id, employee_email, case_id, responsible, record_date, request_date,
    process_access, subunit, event_description, ticket_email,
    app_access_name, computer_system_type, status,
    closing_date_app, closing_date_ticket, app_quality,
    confirmation_by_user, comment, ticket_quality,
    general_status_ticket, average_time_open_ticket
) VALUES (
    'ORPH002', NULL, 'ONB-20251027-0002', 'Tester', GETDATE(), NULL,
    'onboarding', 'Desarrollo', 'Otorgamiento de acceso para JIRA', 'tester@empresa.com',
    'Jira', 'Desktop', 'closed completed',
    NULL, NULL, NULL,
    NULL, 'Carga histórica (onboarding) para pruebas', NULL,
    'En Proceso', '00:05:00'
);

-- ORPH003 - flex staff (incluye la posición temporal en la descripción)
INSERT INTO [dbo].[historico] (
    scotia_id, employee_email, case_id, responsible, record_date, request_date,
    process_access, subunit, event_description, ticket_email,
    app_access_name, computer_system_type, status,
    closing_date_app, closing_date_ticket, app_quality,
    confirmation_by_user, comment, ticket_quality,
    general_status_ticket, average_time_open_ticket
) VALUES (
    'ORPH003', NULL, 'FLEX-20251027-0003', 'Tester', GETDATE(), NULL,
    'flex_staff', 'Tecnología/Desarrollo', 'Otorgamiento temporal de acceso para Sistema de Gestión (flex staff - Gerente de Tecnología)', 'tester@empresa.com',
    'Sistema de Gestión', 'Desktop', 'closed completed',
    NULL, NULL, NULL,
    NULL, 'Carga histórica (flex staff) para pruebas', NULL,
    'En Proceso', '00:12:00'
);

PRINT 'Listo: historiales huérfanos insertados.';


-- 1) Deshabilitar FK
ALTER TABLE [dbo].[historico] NOCHECK CONSTRAINT [FK_historico_headcount];

-- 2) Ejecuta samples/orphan_historico_inserts.sql

-- 3) Re‑habilitar la FK (sin revalidar historial existente)
ALTER TABLE [dbo].[historico] WITH NOCHECK CHECK CONSTRAINT [FK_historico_headcount];


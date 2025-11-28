-- =====================================================
-- Script standalone: tabla Master_Staff_List + datos demo
-- Úsalo solo en entornos de prueba. En productivo ya existe.
-- =====================================================

IF DB_ID('GAMLO_Empleados_DR') IS NULL
BEGIN
    PRINT 'Creando base de datos GAMLO_Empleados_DR...';
    CREATE DATABASE GAMLO_Empleados_DR;
END
GO

USE GAMLO_Empleados_DR;
GO

IF OBJECT_ID(N'[dbo].[Master_Staff_List]', N'U') IS NOT NULL
BEGIN
    DROP TABLE [dbo].[Master_Staff_List];
    PRINT 'Tabla Master_Staff_List previa eliminada (modo demo).';
END
GO

CREATE TABLE [dbo].[Master_Staff_List] (
    [scotia_id]             VARCHAR(20)    NOT NULL PRIMARY KEY,
    [eikon_id]              VARCHAR(30)    NULL,
    [employee_number]       VARCHAR(30)    NOT NULL,
    [employee_name]         VARCHAR(150)   NOT NULL,
    [employee_last_name]    VARCHAR(150)   NOT NULL,
    [business_email]        VARCHAR(180)   NOT NULL,
    [office]                VARCHAR(150)   NULL,
    [department]            VARCHAR(150)   NOT NULL,
    [current_position_title]    VARCHAR(150) NOT NULL,
    [current_position_level]    VARCHAR(100) NULL,
    [hiring_date_bns]       DATE           NULL,
    [hiring_date_gbs]       DATE           NULL,
    [hiring_date_aml]       DATE           NULL,
    [supervisor_name]       VARCHAR(150)   NULL,
    [supervisor_last_name]  VARCHAR(150)   NULL,
    [address]               VARCHAR(255)   NULL,
    [brigade]               VARCHAR(150)   NULL,
    [begdate]               DATE           NULL,
    [status]                VARCHAR(50)    NOT NULL,
    [exit_date]             DATE           NULL,
    [modality_as_today]     VARCHAR(120)   NULL,
    [action_item]           VARCHAR(255)   NULL,
    [exit_reason]           VARCHAR(255)   NULL,
    [modality_reason]       VARCHAR(255)   NULL,
    [gender]                VARCHAR(50)    NULL,
    [dob]                   DATE           NULL,
    [position_code]         VARCHAR(60)    NULL
);
PRINT 'Tabla Master_Staff_List creada (demo).';
GO

INSERT INTO [dbo].[Master_Staff_List] (
    scotia_id, eikon_id, employee_number, employee_name, employee_last_name,
    business_email, office, department, current_position_title, current_position_level,
    hiring_date_bns, hiring_date_gbs, hiring_date_aml, supervisor_name, supervisor_last_name,
    address, brigade, begdate, status, exit_date, modality_as_today, action_item,
    exit_reason, modality_reason, gender, dob, position_code
) VALUES
('SID001', 'EIK001', '1001', 'Lucía', 'Torres', 'lucia.torres@demo.com', 'CDMX Reforma', 'Riesgos',
 'Analista AML', 'Senior', '2021-02-15', '2021-02-15', '2021-02-15', 'Mario', 'Soto',
 'Av. Reforma 123', 'GBS', '2021-02-15', 'Active', NULL, 'Presencial', NULL,
 NULL, NULL, 'Female', '1992-06-18', 'AML-SR-01'),
('SID002', 'EIK002', '1002', 'Jorge', 'Ramírez', 'jorge.ramirez@demo.com', 'Bogotá Chico', 'Operaciones',
 'Coordinador Backoffice', 'Lead', '2019-10-01', NULL, NULL, 'Patricia', 'Mora',
 'Cll 90 # 9-45', 'GBS', '2019-10-01', 'Active', NULL, 'Híbrido', NULL,
 NULL, NULL, 'Male', '1987-11-05', 'OPS-LD-02'),
('SID003', 'EIK003', '1003', 'Ana', 'Silva', 'ana.silva@demo.com', 'SCL Centro', 'Tecnología',
 'Arquitecta Datos', 'Manager', '2018-05-20', NULL, NULL, 'Carlos', 'Durán',
 'Av. Libertador 890', 'GBS', '2018-05-20', 'Inactive', '2024-01-15', 'Remoto', NULL,
 'Renuncia voluntaria', 'Cambio de país', 'Female', '1985-02-12', 'IT-MGR-05');
PRINT 'Datos de prueba insertados en Master_Staff_List.';
GO



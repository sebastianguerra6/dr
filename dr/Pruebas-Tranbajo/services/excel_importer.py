"""
Servicio para importar datos desde Excel a bases de datos
Soporta SQLite y SQL Server con las mismas tablas
"""
import pandas as pd
import sqlite3
import pyodbc
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import sys
import os

# Agregar el directorio database al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
from config import get_database_connection


class ExcelToSQLiteImporter:
    """Importador de Excel a SQLite"""
    
    def __init__(self):
        self.db_manager = get_database_connection()
        self.connection = self.db_manager.get_connection()
    
    def import_from_excel(self, excel_path: str, sheet_name: str, table_name: str, 
                         skip_rows: int = 0) -> Tuple[bool, str, int]:
        """
        Importa datos desde Excel a SQLite
        
        Args:
            excel_path: Ruta del archivo Excel
            sheet_name: Nombre de la hoja
            table_name: Nombre de la tabla destino
            skip_rows: Filas a saltar desde el inicio
            
        Returns:
            Tuple[success, message, records_imported]
        """
        try:
            # Leer Excel
            df = pd.read_excel(excel_path, sheet_name=sheet_name, skiprows=skip_rows)
            
            # Limpiar datos
            df = df.dropna(how='all')  # Eliminar filas completamente vacías
            df = df.fillna('')  # Llenar valores nulos con string vacío
            
            # Convertir columnas a string para evitar problemas de tipos
            for col in df.columns:
                df[col] = df[col].astype(str)
            
            # Insertar datos
            cursor = self.connection.cursor()
            records_imported = 0
            
            for _, row in df.iterrows():
                try:
                    # Preparar datos para inserción
                    data_dict = row.to_dict()
                    
                    if table_name == 'headcount':
                        self._insert_headcount(cursor, data_dict)
                    elif table_name == 'applications':
                        self._insert_application(cursor, data_dict)
                    elif table_name == 'historico':
                        self._insert_historico(cursor, data_dict)
                    else:
                        return False, f"Tabla {table_name} no soportada", 0
                    
                    records_imported += 1
                    
                except Exception as e:
                    print(f"Error insertando fila: {e}")
                    continue
            
            self.connection.commit()
            return True, f"Importación exitosa: {records_imported} registros importados", records_imported
            
        except Exception as e:
            return False, f"Error importando desde Excel: {str(e)}", 0
    
    def _insert_headcount(self, cursor, data: Dict[str, Any]) -> None:
        """Inserta datos en la tabla headcount"""
        cursor.execute('''
            INSERT OR REPLACE INTO headcount 
            (scotia_id, employee, full_name, email, position, manager, senior_manager, 
             unit, start_date, ceco, skip_level, cafe_alcides, parents, personal_email, 
             size, birthday, validacion, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('scotia_id', ''),
            data.get('employee', ''),
            data.get('full_name', ''),
            data.get('email', ''),
            data.get('position', ''),
            data.get('manager', ''),
            data.get('senior_manager', ''),
            data.get('unit', ''),
            data.get('start_date', ''),
            data.get('ceco', ''),
            data.get('skip_level', ''),
            data.get('cafe_alcides', ''),
            data.get('parents', ''),
            data.get('personal_email', ''),
            data.get('size', ''),
            data.get('birthday', ''),
            data.get('validacion', ''),
            data.get('activo', 'True').lower() == 'true'
        ))
    
    def _insert_application(self, cursor, data: Dict[str, Any]) -> None:
        """Inserta datos en la tabla applications"""
        cursor.execute('''
            INSERT OR REPLACE INTO applications 
            (jurisdiction, unit, subunit, logical_access_name, alias, path_email_url, 
             position_role, exception_tracking, fulfillment_action, system_owner, 
             role_name, access_type, category, additional_data, ad_code, access_status, 
             last_update_date, require_licensing, description, authentication_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('jurisdiction', ''),
            data.get('unit', ''),
            data.get('subunit', ''),
            data.get('logical_access_name', ''),
            data.get('alias', ''),
            data.get('path_email_url', ''),
            data.get('position_role', ''),
            data.get('exception_tracking', ''),
            data.get('fulfillment_action', ''),
            data.get('system_owner', ''),
            data.get('role_name', ''),
            data.get('access_type', ''),
            data.get('category', ''),
            data.get('additional_data', ''),
            data.get('ad_code', ''),
            data.get('access_status', ''),
            data.get('last_update_date', ''),
            data.get('require_licensing', ''),
            data.get('description', ''),
            data.get('authentication_method', '')
        ))
    
    def _insert_historico(self, cursor, data: Dict[str, Any]) -> None:
        """Inserta datos en la tabla historico"""
        cursor.execute('''
            INSERT OR REPLACE INTO historico 
            (scotia_id, case_id, responsible, record_date, request_date, process_access, 
             sid, area, subunit, event_description, ticket_email, app_access_name, 
             computer_system_type, status, closing_date_app, closing_date_ticket, 
             app_quality, confirmation_by_user, comment, ticket_quality, 
             average_time_open_ticket)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('scotia_id', ''),
            data.get('case_id', ''),
            data.get('responsible', ''),
            data.get('record_date', ''),
            data.get('request_date', ''),
            data.get('process_access', ''),
            data.get('sid', ''),
            data.get('area', ''),
            data.get('subunit', ''),
            data.get('event_description', ''),
            data.get('ticket_email', ''),
            data.get('app_access_name', ''),
            data.get('computer_system_type', ''),
            data.get('status', ''),
            data.get('closing_date_app', ''),
            data.get('closing_date_ticket', ''),
            data.get('app_quality', ''),
            data.get('confirmation_by_user', ''),
            data.get('comment', ''),
            data.get('ticket_quality', ''),
            data.get('average_time_open_ticket', '')
        ))
    
    def close(self):
        """Cierra la conexión"""
        if self.connection:
            self.connection.close()


class ExcelToSQLServerImporter:
    """Importador de Excel a SQL Server"""
    
    def __init__(self, server: str, database: str, username: str = None, password: str = None, 
                 trusted_connection: bool = True):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.trusted_connection = trusted_connection
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Establece conexión con SQL Server"""
        try:
            if self.trusted_connection:
                connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes;"
            else:
                connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password};"
            
            self.connection = pyodbc.connect(connection_string)
            print("✅ Conexión a SQL Server establecida")
            
        except Exception as e:
            print(f"❌ Error conectando a SQL Server: {e}")
            raise
    
    def create_tables(self) -> Tuple[bool, str]:
        """Crea las tablas en SQL Server si no existen"""
        try:
            cursor = self.connection.cursor()
            
            # Crear tabla headcount
            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='headcount' AND xtype='U')
                CREATE TABLE headcount (
                    scotia_id VARCHAR(20) PRIMARY KEY,
                    employee VARCHAR(100) NOT NULL,
                    full_name VARCHAR(150) NOT NULL,
                    email VARCHAR(150) NOT NULL,
                    position VARCHAR(100),
                    manager VARCHAR(100),
                    senior_manager VARCHAR(100),
                    unit VARCHAR(100),
                    start_date DATE,
                    ceco VARCHAR(100),
                    skip_level VARCHAR(100),
                    cafe_alcides VARCHAR(100),
                    parents VARCHAR(100),
                    personal_email VARCHAR(150),
                    size VARCHAR(50),
                    birthday DATE,
                    validacion VARCHAR(100),
                    activo BIT DEFAULT 1
                )
            ''')
            
            # Crear tabla applications
            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='applications' AND xtype='U')
                CREATE TABLE applications (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    jurisdiction VARCHAR(100),
                    unit VARCHAR(100),
                    subunit VARCHAR(100),
                    logical_access_name VARCHAR(150) NOT NULL,
                    alias VARCHAR(150),
                    path_email_url VARCHAR(255),
                    position_role VARCHAR(100),
                    exception_tracking VARCHAR(255),
                    fulfillment_action VARCHAR(255),
                    system_owner VARCHAR(100),
                    role_name VARCHAR(100),
                    access_type VARCHAR(50),
                    category VARCHAR(100),
                    additional_data VARCHAR(255),
                    ad_code VARCHAR(100),
                    access_status VARCHAR(50),
                    last_update_date DATETIME,
                    require_licensing VARCHAR(255),
                    description TEXT,
                    authentication_method VARCHAR(100)
                )
            ''')
            
            # Crear tabla historico
            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='historico' AND xtype='U')
                CREATE TABLE historico (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    scotia_id VARCHAR(20),
                    case_id VARCHAR(100),
                    responsible VARCHAR(100),
                    record_date DATETIME DEFAULT GETDATE(),
                    request_date DATE,
                    process_access VARCHAR(50),
                    sid VARCHAR(100),
                    area VARCHAR(100),
                    subunit VARCHAR(100),
                    event_description TEXT,
                    ticket_email VARCHAR(150),
                    app_access_name VARCHAR(150),
                    computer_system_type VARCHAR(100),
                    status VARCHAR(50),
                    closing_date_app DATE,
                    closing_date_ticket DATE,
                    app_quality VARCHAR(50),
                    confirmation_by_user BIT,
                    comment TEXT,
                    ticket_quality VARCHAR(50),
                    average_time_open_ticket VARCHAR(50)
                )
            ''')
            
            self.connection.commit()
            return True, "Tablas creadas exitosamente"
            
        except Exception as e:
            return False, f"Error creando tablas: {str(e)}"
    
    def import_from_excel(self, excel_path: str, sheet_name: str, table_name: str, 
                         skip_rows: int = 0) -> Tuple[bool, str, int]:
        """
        Importa datos desde Excel a SQL Server
        
        Args:
            excel_path: Ruta del archivo Excel
            sheet_name: Nombre de la hoja
            table_name: Nombre de la tabla destino
            skip_rows: Filas a saltar desde el inicio
            
        Returns:
            Tuple[success, message, records_imported]
        """
        try:
            # Leer Excel
            df = pd.read_excel(excel_path, sheet_name=sheet_name, skiprows=skip_rows)
            
            # Limpiar datos
            df = df.dropna(how='all')
            df = df.fillna('')
            
            # Convertir columnas a string
            for col in df.columns:
                df[col] = df[col].astype(str)
            
            # Insertar datos
            cursor = self.connection.cursor()
            records_imported = 0
            
            for _, row in df.iterrows():
                try:
                    data_dict = row.to_dict()
                    
                    if table_name == 'headcount':
                        self._insert_headcount_sqlserver(cursor, data_dict)
                    elif table_name == 'applications':
                        self._insert_application_sqlserver(cursor, data_dict)
                    elif table_name == 'historico':
                        self._insert_historico_sqlserver(cursor, data_dict)
                    else:
                        return False, f"Tabla {table_name} no soportada", 0
                    
                    records_imported += 1
                    
                except Exception as e:
                    print(f"Error insertando fila: {e}")
                    continue
            
            self.connection.commit()
            return True, f"Importación exitosa: {records_imported} registros importados", records_imported
            
        except Exception as e:
            return False, f"Error importando desde Excel: {str(e)}", 0
    
    def _insert_headcount_sqlserver(self, cursor, data: Dict[str, Any]) -> None:
        """Inserta datos en la tabla headcount de SQL Server"""
        cursor.execute('''
            MERGE headcount AS target
            USING (SELECT ? AS scotia_id, ? AS employee, ? AS full_name, ? AS email, 
                          ? AS position, ? AS manager, ? AS senior_manager, ? AS unit,
                          ? AS start_date, ? AS ceco, ? AS skip_level, ? AS cafe_alcides,
                          ? AS parents, ? AS personal_email, ? AS size, ? AS birthday,
                          ? AS validacion, ? AS activo) AS source
            ON target.scotia_id = source.scotia_id
            WHEN MATCHED THEN
                UPDATE SET employee = source.employee, full_name = source.full_name,
                          email = source.email, position = source.position,
                          manager = source.manager, senior_manager = source.senior_manager,
                          unit = source.unit, start_date = source.start_date,
                          ceco = source.ceco, skip_level = source.skip_level,
                          cafe_alcides = source.cafe_alcides, parents = source.parents,
                          personal_email = source.personal_email, size = source.size,
                          birthday = source.birthday, validacion = source.validacion,
                          activo = source.activo
            WHEN NOT MATCHED THEN
                INSERT (scotia_id, employee, full_name, email, position, manager, 
                       senior_manager, unit, start_date, ceco, skip_level, cafe_alcides,
                       parents, personal_email, size, birthday, validacion, activo)
                VALUES (source.scotia_id, source.employee, source.full_name, source.email,
                       source.position, source.manager, source.senior_manager, source.unit,
                       source.start_date, source.ceco, source.skip_level, source.cafe_alcides,
                       source.parents, source.personal_email, source.size, source.birthday,
                       source.validacion, source.activo);
        ''', (
            data.get('scotia_id', ''),
            data.get('employee', ''),
            data.get('full_name', ''),
            data.get('email', ''),
            data.get('position', ''),
            data.get('manager', ''),
            data.get('senior_manager', ''),
            data.get('unit', ''),
            data.get('start_date', ''),
            data.get('ceco', ''),
            data.get('skip_level', ''),
            data.get('cafe_alcides', ''),
            data.get('parents', ''),
            data.get('personal_email', ''),
            data.get('size', ''),
            data.get('birthday', ''),
            data.get('validacion', ''),
            1 if data.get('activo', 'True').lower() == 'true' else 0
        ))
    
    def _insert_application_sqlserver(self, cursor, data: Dict[str, Any]) -> None:
        """Inserta datos en la tabla applications de SQL Server"""
        cursor.execute('''
            INSERT INTO applications 
            (jurisdiction, unit, subunit, logical_access_name, alias, path_email_url, 
             position_role, exception_tracking, fulfillment_action, system_owner, 
             role_name, access_type, category, additional_data, ad_code, access_status, 
             last_update_date, require_licensing, description, authentication_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('jurisdiction', ''),
            data.get('unit', ''),
            data.get('subunit', ''),
            data.get('logical_access_name', ''),
            data.get('alias', ''),
            data.get('path_email_url', ''),
            data.get('position_role', ''),
            data.get('exception_tracking', ''),
            data.get('fulfillment_action', ''),
            data.get('system_owner', ''),
            data.get('role_name', ''),
            data.get('access_type', ''),
            data.get('category', ''),
            data.get('additional_data', ''),
            data.get('ad_code', ''),
            data.get('access_status', ''),
            data.get('last_update_date', ''),
            data.get('require_licensing', ''),
            data.get('description', ''),
            data.get('authentication_method', '')
        ))
    
    def _insert_historico_sqlserver(self, cursor, data: Dict[str, Any]) -> None:
        """Inserta datos en la tabla historico de SQL Server"""
        cursor.execute('''
            INSERT INTO historico 
            (scotia_id, employee_email, case_id, responsible, record_date, request_date, process_access, 
             subunit, event_description, ticket_email, app_access_name, 
             computer_system_type, status, closing_date_app, closing_date_ticket, 
             app_quality, confirmation_by_user, comment, ticket_quality, general_status_ticket, 
             average_time_open_ticket)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('scotia_id', ''),
            data.get('employee_email', ''),
            data.get('case_id', ''),
            data.get('responsible', ''),
            data.get('record_date', ''),
            data.get('request_date', ''),
            data.get('process_access', ''),
            data.get('subunit', ''),
            data.get('event_description', ''),
            data.get('ticket_email', ''),
            data.get('app_access_name', ''),
            data.get('computer_system_type', ''),
            data.get('status', ''),
            data.get('closing_date_app', ''),
            data.get('closing_date_ticket', ''),
            data.get('app_quality', ''),
            data.get('confirmation_by_user', ''),
            data.get('comment', ''),
            data.get('ticket_quality', ''),
            data.get('average_time_open_ticket', '')
        ))
    
    def close(self):
        """Cierra la conexión"""
        if self.connection:
            self.connection.close()


# Funciones de conveniencia
def import_excel_to_sqlite(excel_path: str, sheet_name: str, table_name: str, 
                          db_path: str = None, skip_rows: int = 0) -> Tuple[bool, str, int]:
    """Función de conveniencia para importar Excel a SQLite"""
    importer = ExcelToSQLiteImporter(db_path)
    try:
        return importer.import_from_excel(excel_path, sheet_name, table_name, skip_rows)
    finally:
        importer.close()


def import_excel_to_sqlserver(excel_path: str, sheet_name: str, table_name: str,
                             server: str, database: str, username: str = None, 
                             password: str = None, trusted_connection: bool = True,
                             skip_rows: int = 0) -> Tuple[bool, str, int]:
    """Función de conveniencia para importar Excel a SQL Server"""
    importer = ExcelToSQLServerImporter(server, database, username, password, trusted_connection)
    try:
        # Crear tablas si no existen
        success, message = importer.create_tables()
        if not success:
            return False, f"Error creando tablas: {message}", 0
        
        return importer.import_from_excel(excel_path, sheet_name, table_name, skip_rows)
    finally:
        importer.close()

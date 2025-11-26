"""
Servicio para gestionar la lógica de negocio entre las tablas:
- headcount (personas)
- applications (aplicaciones y accesos)
- historico (historial de procesos)

Sistema optimizado para SQL Server únicamente.
"""
import pyodbc
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import sys
import os

# Importar configuración
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import get_database_connection


class AccessManagementService:
    """Servicio principal para gestionar accesos y procesos"""

    # ==============================
    # UTILIDADES INTERNAS
    # ==============================
    @staticmethod
    def _safe_strip(value: Optional[str], default: str = '') -> str:
        """Maneja de forma segura el strip de valores que pueden ser None"""
        if value is None:
            return default
        if isinstance(value, str):
            return value.strip()
        return str(value).strip() if value else default
    
    @staticmethod
    def _access_key(unit: Optional[str], subunit: Optional[str], position_role: Optional[str], logical_access_name: Optional[str]) -> Tuple[str, str, str, str]:
        """Crea una clave normalizada para comparar accesos por 4 campos.
        Orden: (unit, subunit, position_role, logical_access_name)
        """
        return (
            (unit or '').strip(),
            (subunit or '').strip(),
            (position_role or '').strip(),
            (logical_access_name or '').strip(),
        )

    @staticmethod
    def _triplet_key(unidad_subunidad: Optional[str], position_role: Optional[str], logical_access_name: Optional[str]) -> Tuple[str, str, str]:
        """Crea una clave normalizada para comparar accesos por 3 campos usando unidad_subunidad.
        Orden: (unidad_subunidad, position_role, logical_access_name)
        """
        return (
            (unidad_subunidad or '').strip().upper(),
            (position_role or '').strip().upper(),
            (logical_access_name or '').strip().upper(),
        )

    def __init__(self):
        """Inicializa el servicio con conexión a SQL Server"""
        self.db_manager = get_database_connection()
        self._ensure_views_and_indexes()

    def get_connection(self) -> pyodbc.Connection:
        """Obtiene una conexión a la base de datos"""
        return self.db_manager.get_connection()

    def _ensure_views_and_indexes(self):
        """Asegura que existan los índices necesarios para SQL Server"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Crear índices para optimizar las consultas (sintaxis SQL Server)
            indexes = [
                "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_applications_unit_position' AND object_id = OBJECT_ID('applications')) CREATE INDEX idx_applications_unit_position ON applications (unit, position_role)",
                "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_historico_scotia_status' AND object_id = OBJECT_ID('historico')) CREATE INDEX idx_historico_scotia_status ON historico (scotia_id, status)",
                "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_historico_process_status' AND object_id = OBJECT_ID('historico')) CREATE INDEX idx_historico_process_status ON historico (process_access, status)",
                "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_headcount_unit_position' AND object_id = OBJECT_ID('headcount')) CREATE INDEX idx_headcount_unit_position ON headcount (unit, position)"
            ]
            
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                except Exception as e:
                    print(f"Advertencia: No se pudo crear índice: {e}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error creando vistas e índices: {e}")
            # No lanzar excepción para no interrumpir la inicialización

    # ==============================
    # MÉTODOS PARA HEADCOUNT
    # ==============================

    def create_employee(self, employee_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Crea un nuevo empleado en headcount"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Validar datos requeridos
            required_fields = ['scotia_id', 'employee', 'full_name', 'email']
            for field in required_fields:
                if not employee_data.get(field):
                    return False, f"Campo requerido faltante: {field}"

            # Usar unidad_subunidad directamente si se proporciona, o construirla
            unidad_subunidad = employee_data.get('unidad_subunidad', '')
            if not unidad_subunidad:
                unit = employee_data.get('unit', '')
                subunit = employee_data.get('subunit', '')
                unidad_subunidad = f"{unit}/{subunit}" if unit and subunit else unit if unit else None
            
            # Insertar empleado
            cursor.execute('''
                INSERT INTO headcount 
                (scotia_id, employee, full_name, email, position, manager, senior_manager, 
                 unit, unidad_subunidad, start_date, ceco, skip_level, cafe_alcides, parents, personal_email, 
                 size, birthday, validacion, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                employee_data.get('scotia_id'),
                employee_data.get('employee'),
                employee_data.get('full_name'),
                employee_data.get('email'),
                employee_data.get('position'),
                employee_data.get('manager'),
                employee_data.get('senior_manager'),
                employee_data.get('unit'),
                unidad_subunidad,
                employee_data.get('start_date'),
                employee_data.get('ceco'),
                employee_data.get('skip_level'),
                employee_data.get('cafe_alcides'),
                employee_data.get('parents'),
                employee_data.get('personal_email'),
                employee_data.get('size'),
                employee_data.get('birthday'),
                employee_data.get('validacion'),
                employee_data.get('activo', True)
            ))

            conn.commit()
            conn.close()

            return True, f"Empleado {employee_data.get('scotia_id')} creado exitosamente"

        except pyodbc.IntegrityError:
            return False, f"Error de integridad: El empleado {employee_data.get('scotia_id')} ya existe"
        except Exception as e:
            return False, f"Error creando empleado: {str(e)}"

    def get_employee_by_id(self, scotia_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un empleado por su scotia_id usando consulta directa"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM headcount WHERE scotia_id = ?', (scotia_id,))
            row = cursor.fetchone()

            if row:
                columns = [description[0] for description in cursor.description]
                employee = dict(zip(columns, row))
                conn.close()
                return employee

            conn.close()
            return None

        except Exception as e:
            print(f"Error obteniendo empleado: {e}")
            return None

    def get_all_employees(self) -> List[Dict[str, Any]]:
        """Obtiene todos los empleados activos usando consulta directa"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM headcount WHERE activo = 1 ORDER BY full_name')
            rows = cursor.fetchall()

            columns = [description[0] for description in cursor.description]
            employees = [dict(zip(columns, row)) for row in rows]

            conn.close()
            return employees

        except Exception as e:
            print(f"Error obteniendo empleados: {e}")
            return []

    def update_employee_position(self, scotia_id: str, new_position: str, new_unit: str, new_unidad_subunidad: str = None) -> Tuple[bool, str]:
        """Actualiza la posición, unidad y unidad_subunidad de un empleado"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Si no se proporciona unidad_subunidad, generar una basada en la unidad
            if new_unidad_subunidad is None:
                new_unidad_subunidad = f"{new_unit}/General" if new_unit else "Sin Unidad/Subunidad"

            cursor.execute('''
                UPDATE headcount 
                SET position = ?, unit = ?, unidad_subunidad = ?
                WHERE scotia_id = ?
            ''', (new_position, new_unit, new_unidad_subunidad, scotia_id))

            if cursor.rowcount == 0:
                conn.close()
                return False, f"Empleado {scotia_id} no encontrado"

            conn.commit()
            conn.close()

            return True, f"Posición y unidad actualizadas para {scotia_id}"

        except Exception as e:
            return False, f"Error actualizando posición: {str(e)}"

    def update_employee(self, scotia_id: str, employee_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Actualiza todos los datos de un empleado"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Manejar unidad_subunidad
            update_data = employee_data.copy()
            if 'unidad_subunidad' not in update_data or not update_data['unidad_subunidad']:
                # Si no se proporciona unidad_subunidad, construirla
                if 'subunit' in update_data and 'unit' in update_data:
                    unit = update_data['unit']
                    subunit = update_data['subunit']
                    update_data['unidad_subunidad'] = f"{unit}/{subunit}" if unit and subunit else unit if unit else None
                    # No actualizar subunit directamente ya que no existe en la tabla
                    del update_data['subunit']

            # Construir query de actualización dinámicamente
            set_clauses = []
            params = []

            for campo, valor in update_data.items():
                if campo != 'scotia_id':  # No actualizar el SID
                    set_clauses.append(f"{campo} = ?")
                    params.append(valor)

            if not set_clauses:
                return False, "No hay datos para actualizar"

            query = f"""
                UPDATE headcount 
                SET {', '.join(set_clauses)}
                WHERE scotia_id = ?
            """
            params.append(scotia_id)

            cursor.execute(query, params)

            if cursor.rowcount == 0:
                conn.close()
                return False, f"Empleado {scotia_id} no encontrado"

            conn.commit()
            conn.close()

            return True, f"Empleado {scotia_id} actualizado exitosamente"

        except Exception as e:
            return False, f"Error actualizando empleado: {str(e)}"

    def delete_employee(self, scotia_id: str) -> Tuple[bool, str]:
        """Elimina un empleado del headcount"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Verificar si el empleado existe
            cursor.execute('SELECT full_name FROM headcount WHERE scotia_id = ?', (scotia_id,))
            empleado = cursor.fetchone()

            if not empleado:
                conn.close()
                return False, f"Empleado {scotia_id} no encontrado"

            # Eliminar el empleado
            cursor.execute('DELETE FROM headcount WHERE scotia_id = ?', (scotia_id,))

            if cursor.rowcount == 0:
                conn.close()
                return False, f"No se pudo eliminar el empleado {scotia_id}"

            conn.commit()
            conn.close()

            return True, f"Empleado {scotia_id} eliminado exitosamente"

        except Exception as e:
            return False, f"Error eliminando empleado: {str(e)}"

    # ==============================
    # MÉTODOS PARA APPLICATIONS
    # ==============================

    def get_applications_by_position(self, position: str, unidad_subunidad: str, subunit: Optional[str] = None, title: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtiene las aplicaciones que debe tener un empleado según posición/unidad_subunidad/subunidad/título.
        **Sin duplicados**: devuelve una fila por tripleta (unidad_subunidad, position_role, logical_access_name).
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Construir consulta dinámicamente
            query = 'SELECT logical_access_name, jurisdiction, unit, subunit, unidad_subunidad, alias, path_email_url, position_role, exception_tracking, fulfillment_action, system_owner, role_name, access_type, category, additional_data, ad_code, access_status, last_update_date, require_licensing, description, authentication_method FROM applications WHERE 1=1'
            params = []
            
            if unidad_subunidad:
                query += ' AND UPPER(LTRIM(RTRIM(unidad_subunidad))) = UPPER(LTRIM(RTRIM(?)))'
                params.append(unidad_subunidad)
            
            if subunit:
                query += ' AND UPPER(LTRIM(RTRIM(subunit))) = UPPER(LTRIM(RTRIM(?)))'
                params.append(subunit)
            
            if position:
                # Buscar en ambas columnas: position (nueva) y position_role (antigua)
                query += ' AND (UPPER(LTRIM(RTRIM(position))) = UPPER(LTRIM(RTRIM(?))) OR UPPER(LTRIM(RTRIM(position_role))) = UPPER(LTRIM(RTRIM(?))))'
                params.append(position)
                params.append(position)
            
            if title:
                query += ' AND UPPER(LTRIM(RTRIM(role_name))) = UPPER(LTRIM(RTRIM(?)))'
                params.append(title)
            
            query += ' ORDER BY logical_access_name'
            
            # Debug: imprimir la consulta y parámetros
            print(f"DEBUG get_applications_by_position:")
            print(f"  - Posición: '{position}'")
            print(f"  - Unidad/Subunidad: '{unidad_subunidad}'")
            print(f"  - Subunidad: '{subunit}'")
            print(f"  - Título: '{title}'")
            print(f"  - Consulta: {query}")
            print(f"  - Parámetros: {params}")
            
            cursor.execute(query, params)

            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            applications = [dict(zip(columns, row)) for row in rows]
            
            # Debug: mostrar resultados
            print(f"  - Resultados encontrados: {len(applications)}")
            
            # Si no hay resultados, hacer debug para ver qué datos existen
            if len(applications) == 0:
                print("DEBUG: No se encontraron aplicaciones. Verificando qué datos existen...")
                
                # Verificar posiciones disponibles
                cursor.execute("SELECT DISTINCT position, position_role FROM applications WHERE access_status = 'Active'")
                positions = cursor.fetchall()
                print(f"DEBUG: Posiciones disponibles: {positions}")
                
                # Verificar unidades/subunidades disponibles
                cursor.execute("SELECT DISTINCT unidad_subunidad FROM applications WHERE access_status = 'Active'")
                unidades = cursor.fetchall()
                print(f"DEBUG: Unidades/Subunidades disponibles: {unidades}")
                
                # Verificar subunidades disponibles
                cursor.execute("SELECT DISTINCT subunit FROM applications WHERE access_status = 'Active'")
                subunidades = cursor.fetchall()
                print(f"DEBUG: Subunidades disponibles: {subunidades}")
                
                # Buscar aplicaciones que contengan "Summer" en cualquier campo
                cursor.execute("SELECT logical_access_name, position, position_role, unidad_subunidad, subunit FROM applications WHERE access_status = 'Active' AND (position LIKE '%Summer%' OR position_role LIKE '%Summer%')")
                summer_apps = cursor.fetchall()
                print(f"DEBUG: Aplicaciones que contienen 'Summer': {summer_apps}")
                
                # Buscar aplicaciones que contengan "Business Intelligence" o "Analytics"
                cursor.execute("SELECT logical_access_name, position, position_role, unidad_subunidad, subunit FROM applications WHERE access_status = 'Active' AND (unidad_subunidad LIKE '%Business Intelligence%' OR unidad_subunidad LIKE '%Analytics%' OR subunit LIKE '%Analytics%')")
                bi_apps = cursor.fetchall()
                print(f"DEBUG: Aplicaciones relacionadas con Business Intelligence/Analytics: {bi_apps}")
            
            for app in applications:
                print(f"    * {app.get('logical_access_name', '')} | {app.get('unidad_subunidad', '')} | {app.get('position_role', '')}")

            conn.close()
            return applications

        except Exception as e:
            print(f"Error obteniendo aplicaciones por posición: {e}")
            return []

    def get_applications_by_position_flexible(self, position: str, unit: str, subunit: Optional[str] = None, title: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtiene las aplicaciones usando la misma lógica flexible que se usa para accesos normales.
        Esta función es más permisiva y encuentra aplicaciones incluso si las unidades/subunidades no coinciden exactamente.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Construir consulta más flexible - similar a la lógica de accesos normales
            query = 'SELECT logical_access_name, jurisdiction, unit, subunit, alias, path_email_url, position_role, exception_tracking, fulfillment_action, system_owner, role_name, access_type, category, additional_data, ad_code, access_status, last_update_date, require_licensing, description, authentication_method FROM applications WHERE 1=1'
            params = []
            
            # Filtrar por posición (obligatorio)
            if position:
                query += ' AND UPPER(LTRIM(RTRIM(position_role))) = UPPER(LTRIM(RTRIM(?)))'
                params.append(position)
            
            # Filtrar por unidad_subunidad (obligatorio) - buscar solo coincidencia exacta
            # Esto evita encontrar "eddu/qa" cuando se busca "eddu" (solo encuentra "eddu" exacto)
            if unit:
                # Normalizar el valor de búsqueda para comparación exacta
                unit_normalized = unit.strip().upper()
                # Buscar solo coincidencia exacta de unidad_subunidad
                query += ' AND UPPER(LTRIM(RTRIM(unidad_subunidad))) = ?'
                params.append(unit_normalized)
            
            # Subunidad es opcional - no filtrar si no se proporciona
            if subunit:
                query += ' AND UPPER(LTRIM(RTRIM(subunit))) = UPPER(LTRIM(RTRIM(?)))'
                params.append(subunit)
            
            # Título es opcional
            if title:
                query += ' AND UPPER(LTRIM(RTRIM(role_name))) = UPPER(LTRIM(RTRIM(?)))'
                params.append(title)
            
            query += ' ORDER BY logical_access_name'
            
            # Debug: imprimir la consulta y parámetros
            print(f"DEBUG get_applications_by_position_flexible:")
            print(f"  - Posición: '{position}'")
            print(f"  - Unidad: '{unit}'")
            print(f"  - Subunidad: '{subunit}' (opcional)")
            print(f"  - Título: '{title}' (opcional)")
            print(f"  - Consulta: {query}")
            print(f"  - Parámetros: {params}")
            
            cursor.execute(query, params)

            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            applications = [dict(zip(columns, row)) for row in rows]
            
            # Debug: mostrar resultados
            print(f"  - Resultados encontrados: {len(applications)}")
            
            # Si no hay resultados, hacer debug para ver qué datos existen
            if len(applications) == 0:
                print("DEBUG: No se encontraron aplicaciones para flex staff. Verificando qué datos existen...")
                
                # Verificar posiciones disponibles
                cursor.execute("SELECT DISTINCT position, position_role FROM applications WHERE access_status = 'Active'")
                positions = cursor.fetchall()
                print(f"DEBUG: Posiciones disponibles: {positions}")
                
                # Verificar unidades disponibles
                cursor.execute("SELECT DISTINCT unit FROM applications WHERE access_status = 'Active'")
                units = cursor.fetchall()
                print(f"DEBUG: Unidades disponibles: {units}")
                
                # Buscar aplicaciones que contengan "Analista"
                cursor.execute("SELECT logical_access_name, position, position_role, unit, subunit FROM applications WHERE access_status = 'Active' AND (position LIKE '%Analista%' OR position_role LIKE '%Analista%')")
                analista_apps = cursor.fetchall()
                print(f"DEBUG: Aplicaciones que contienen 'Analista': {analista_apps}")
                
                # Buscar aplicaciones que contengan "Recursos Humanos"
                cursor.execute("SELECT logical_access_name, position, position_role, unit, subunit FROM applications WHERE access_status = 'Active' AND (unit LIKE '%Recursos Humanos%' OR subunit LIKE '%Recursos Humanos%')")
                rh_apps = cursor.fetchall()
                print(f"DEBUG: Aplicaciones relacionadas con Recursos Humanos: {rh_apps}")
            
            for app in applications:
                print(f"    * {app.get('logical_access_name', '')} | {app.get('unit', '')} | {app.get('subunit', '')} | {app.get('position_role', '')}")

            conn.close()
            return applications

        except Exception as e:
            print(f"Error obteniendo aplicaciones por posición flexible: {e}")
            return []

    def get_all_applications(self) -> List[Dict[str, Any]]:
        """Obtiene todas las aplicaciones"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM applications ORDER BY logical_access_name')
            rows = cursor.fetchall()

            columns = [description[0] for description in cursor.description]
            applications = [dict(zip(columns, row)) for row in rows]

            conn.close()
            return applications

        except Exception as e:
            print(f"Error obteniendo aplicaciones: {e}")
            return []

    def _get_application_by_name(self, logical_access_name: str) -> Optional[Dict[str, Any]]:
        """Obtiene una aplicación por su logical_access_name"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT TOP 1 logical_access_name, jurisdiction, unit, subunit, 
                       alias, path_email_url, position_role, exception_tracking, 
                       fulfillment_action, system_owner, role_name, access_type, 
                       category, additional_data, ad_code, access_status, 
                       last_update_date, require_licensing, description, 
                       authentication_method
                FROM applications 
                WHERE logical_access_name = ?
            ''', (logical_access_name,))

            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                app = dict(zip(columns, row))
                conn.close()
                return app

            conn.close()
            return None

        except Exception as e:
            print(f"Error obteniendo aplicación por nombre: {e}")
            return None

    def create_application(self, app_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Crea una nueva aplicación"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Validar datos requeridos
            if not app_data.get('logical_access_name'):
                return False, "Campo requerido faltante: logical_access_name"

            # Usar unidad_subunidad directamente si se proporciona, o construirla
            unidad_subunidad = app_data.get('unidad_subunidad', '')
            if not unidad_subunidad:
                unit = app_data.get('unit', '')
                subunit = app_data.get('subunit', '')
                unidad_subunidad = f"{unit}/{subunit}" if unit and subunit else unit if unit else None

            # Usar OUTPUT INSERTED.id para SQL Server
            cursor.execute('''
                INSERT INTO applications 
                (jurisdiction, unit, subunit, unidad_subunidad, logical_access_name, alias, path_email_url, position_role, 
                 exception_tracking, fulfillment_action, system_owner, role_name, access_type, 
                 category, additional_data, ad_code, access_status, last_update_date, 
                 require_licensing, description, authentication_method)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                app_data.get('jurisdiction'),
                app_data.get('unit'),
                app_data.get('subunit'),
                unidad_subunidad,
                app_data.get('logical_access_name'),
                app_data.get('alias'),
                app_data.get('path_email_url'),
                app_data.get('position_role'),
                app_data.get('exception_tracking'),
                app_data.get('fulfillment_action'),
                app_data.get('system_owner'),
                app_data.get('role_name'),
                app_data.get('access_type'),
                app_data.get('category'),
                app_data.get('additional_data'),
                app_data.get('ad_code'),
                app_data.get('access_status', 'Active'),
                datetime.now().isoformat(),
                app_data.get('require_licensing'),
                app_data.get('description'),
                app_data.get('authentication_method')
            ))
            app_id = cursor.fetchone()[0]

            conn.commit()
            conn.close()

            return True, f"Aplicación {app_data.get('logical_access_name')} creada exitosamente con ID {app_id}"

        except pyodbc.IntegrityError:
            return False, "Error de integridad: La aplicación ya existe"
        except Exception as e:
            return False, f"Error creando aplicación: {str(e)}"

    def update_application(self, app_id: int, app_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Actualiza una aplicación existente"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM applications WHERE id = ?', (app_id,))
            result = cursor.fetchone()
            if not result or result[0] == 0:
                return False, f"Aplicación con ID {app_id} no encontrada"

            # Manejar unidad_subunidad
            update_data = app_data.copy()
            if 'unidad_subunidad' not in update_data or not update_data['unidad_subunidad']:
                # Si no se proporciona unidad_subunidad, construirla
                if 'subunit' in update_data and 'unit' in update_data:
                    unit = update_data['unit']
                    subunit = update_data['subunit']
                    update_data['unidad_subunidad'] = f"{unit}/{subunit}" if unit and subunit else unit if unit else None

            set_clauses = []
            params = []

            for field, value in update_data.items():
                if field in ['jurisdiction', 'unit', 'subunit', 'unidad_subunidad', 'logical_access_name', 'alias', 'path_email_url', 
                           'position_role', 'exception_tracking', 'fulfillment_action', 'system_owner', 
                           'role_name', 'access_type', 'category', 'additional_data', 'ad_code', 
                           'access_status', 'require_licensing', 'description', 'authentication_method']:
                    set_clauses.append(f"{field} = ?")
                    params.append(value)

            if not set_clauses:
                return False, "No hay campos válidos para actualizar"

            set_clauses.append("last_update_date = ?")
            params.append(datetime.now().isoformat())

            params.append(app_id)

            query = f"UPDATE applications SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, params)

            conn.commit()
            conn.close()

            return True, f"Aplicación {app_id} actualizada exitosamente"

        except Exception as e:
            return False, f"Error actualizando aplicación: {str(e)}"

    def delete_application(self, app_id: int) -> Tuple[bool, str]:
        """Elimina una aplicación"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT logical_access_name FROM applications WHERE id = ?', (app_id,))
            result = cursor.fetchone()
            if not result:
                return False, f"Aplicación con ID {app_id} no encontrada"

            app_name = result[0]

            cursor.execute('SELECT COUNT(*) FROM historico WHERE app_access_name = ?', (app_name,))
            historico_count = cursor.fetchone()[0]

            if historico_count > 0:
                return False, f"No se puede eliminar la aplicación porque tiene {historico_count} registros en el historial"

            cursor.execute('DELETE FROM applications WHERE id = ?', (app_id,))

            conn.commit()
            conn.close()

            return True, f"Aplicación {app_name} eliminada exitosamente"

        except Exception as e:
            return False, f"Error eliminando aplicación: {str(e)}"

    # ==============================
    # MÉTODOS PARA HISTORICO
    # ==============================

    def create_manual_access_record(self, scotia_id: str, app_name: str, 
                                   responsible: str = "Manual", 
                                   description: str = None,
                                   position: str = None) -> Tuple[bool, str]:
        """Crea un registro manual individual de acceso para una persona específica"""
        try:
            # Verificar que el empleado existe
            employee = self.get_employee_by_id(scotia_id)
            if not employee:
                return False, f"Empleado {scotia_id} no encontrado"
            
            # Generar case_id único
            case_id = f"MANUAL-{datetime.now().strftime('%Y%m%d%H%M%S%f')}-{scotia_id}"
            
            # Crear descripción si no se proporciona
            if not description:
                description = f"Acceso manual a {app_name} para {employee.get('full_name', scotia_id)}"
            
            # Obtener información de la aplicación si se proporciona posición
            app_info = None
            if position:
                try:
                    conn = self.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT TOP 1 unit, subunit, role_name, description
                        FROM applications 
                        WHERE logical_access_name = ? AND position_role = ?
                    ''', (app_name, position))
                    
                    app_row = cursor.fetchone()
                    if app_row:
                        app_info = {
                            'unit': app_row[0],
                            'subunit': app_row[1],
                            'role_name': app_row[2],
                            'description': app_row[3]
                        }
                    conn.close()
                except Exception as e:
                    print(f"Error obteniendo información de aplicación: {e}")
            
            # Datos del registro manual
            record_data = {
                'scotia_id': scotia_id,
                'case_id': case_id,
                'responsible': responsible,
                'record_date': datetime.now().isoformat(),
                'request_date': datetime.now().strftime('%Y-%m-%d'),
                'process_access': 'manual_access',
                'sid': scotia_id,
                'area': app_info.get('unit', employee.get('unit', 'Sin Unidad')) if app_info else employee.get('unit', 'Sin Unidad'),
                'subunit': app_info.get('subunit', employee.get('unit', 'Sin Unidad')) if app_info else employee.get('unit', 'Sin Unidad'),
                'event_description': description,
                'ticket_email': f"{responsible}@empresa.com",
                'app_access_name': app_name,
                'computer_system_type': 'Desktop',
                'status': 'Pendiente',
                'closing_date_app': None,
                'closing_date_ticket': None,
                'app_quality': None,
                'confirmation_by_user': None,
                'comment': f"Registro manual creado por {responsible}" + (f" para posición {position}" if position else ""),
                'ticket_quality': None,
                'average_time_open_ticket': None
            }
            
            # Crear el registro
            success, message = self.create_historical_record(record_data)
            
            if success:
                return True, f"Registro manual creado exitosamente para {scotia_id} - {app_name}"
            else:
                return False, f"Error creando registro manual: {message}"
                
        except Exception as e:
            return False, f"Error creando registro manual: {str(e)}"

    def create_historical_record(self, record_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Crea un registro en el historial con verificación anti-duplicados"""
        try:
            print(f"DEBUG: Iniciando creación de registro histórico")
            print(f"DEBUG: Datos recibidos: {record_data}")
            
            conn = self.get_connection()
            cursor = conn.cursor()

            required_fields = ['scotia_id', 'process_access']
            for field in required_fields:
                if not record_data.get(field):
                    print(f"DEBUG: Error - Campo requerido faltante: {field}")
                    return False, f"Campo requerido faltante: {field}"

            # Verificación anti-duplicados: evita más de un "Pendiente" por la misma app/empleado
            # PERO permite registros de offboarding incluso si ya existe un registro pendiente
            process_access = record_data.get('process_access', '')
            if process_access != 'offboarding':
                cursor.execute('''
                    SELECT COUNT(*) FROM historico
                    WHERE scotia_id = ?
                      AND status = 'Pendiente'
                      AND UPPER(TRIM(app_access_name)) = UPPER(TRIM(?))
                ''', (record_data['scotia_id'], record_data.get('app_access_name', '')))
                
                existing_count = cursor.fetchone()[0]
                if existing_count > 0:
                    conn.close()
                    return True, f"Registro ya pendiente; no se duplicó (existentes: {existing_count})"

            # Obtener el email del empleado si no se proporciona
            employee_email = record_data.get('employee_email')
            if not employee_email:
                print(f"DEBUG: Obteniendo email del empleado {record_data.get('scotia_id')}")
                cursor.execute('SELECT email FROM headcount WHERE scotia_id = ?', (record_data.get('scotia_id'),))
                email_result = cursor.fetchone()
                employee_email = email_result[0] if email_result else None
                print(f"DEBUG: Email obtenido: {employee_email}")

            print(f"DEBUG: Preparando inserción con email: {employee_email}")
            
            # Preparar parámetros para debug
            params = (
                record_data.get('scotia_id'),
                employee_email,
                record_data.get('case_id'),
                record_data.get('responsible'),
                record_data.get('record_date', datetime.now().isoformat()),
                record_data.get('request_date'),
                record_data.get('process_access'),
                record_data.get('subunit'),
                record_data.get('event_description'),
                record_data.get('ticket_email'),
                record_data.get('app_access_name'),
                record_data.get('computer_system_type'),
                record_data.get('status', 'Pendiente'),
                record_data.get('closing_date_app'),
                record_data.get('closing_date_ticket'),
                record_data.get('app_quality'),
                record_data.get('confirmation_by_user'),
                record_data.get('comment'),
                record_data.get('ticket_quality'),
                record_data.get('general_status_ticket'),
                record_data.get('average_time_open_ticket')
            )
            
            print(f"DEBUG: Parámetros para inserción: {params}")
            
            cursor.execute('''
                INSERT INTO historico 
                (scotia_id, employee_email, case_id, responsible, record_date, request_date, process_access, subunit, 
                 event_description, ticket_email, app_access_name, computer_system_type, status, 
                 closing_date_app, closing_date_ticket, app_quality, confirmation_by_user, comment, 
                 ticket_quality, general_status_ticket, average_time_open_ticket)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', params)

            conn.commit()
            print(f"DEBUG: Registro insertado exitosamente en la base de datos")
            conn.close()

            return True, "Registro histórico creado exitosamente"

        except Exception as e:
            return False, f"Error creando registro histórico: {str(e)}"

    def get_employee_history(self, scotia_id: str) -> List[Dict[str, Any]]:
        """Obtiene el historial de un empleado incluyendo metadatos de la app para comparación estricta.
        Evita duplicados usando subconsulta para obtener solo una app por logical_access_name.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT 
                    h.*, 
                    a.logical_access_name AS app_logical_access_name,
                    a.description AS app_description,
                    a.unit AS app_unit,
                    a.subunit AS app_subunit,
                    a.position_role AS app_position_role
                FROM historico h
                LEFT JOIN (
                    SELECT 
                        logical_access_name,
                        description,
                        unit,
                        subunit,
                        position_role,
                        ROW_NUMBER() OVER (PARTITION BY logical_access_name ORDER BY id) as rn
                    FROM applications
                ) a ON h.app_access_name = a.logical_access_name AND a.rn = 1
                WHERE h.scotia_id = ?
                ORDER BY h.record_date DESC
            ''', (scotia_id,))

            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            history = [dict(zip(columns, row)) for row in rows]

            conn.close()
            return history

        except Exception as e:
            print(f"Error obteniendo historial: {e}")
            return []

    def get_employee_current_access(self, scotia_id: str) -> List[Dict[str, Any]]:
        """Obtiene los accesos actuales del empleado (completados y pendientes)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT DISTINCT
                    h.scotia_id,
                    h.subunit as unit,
                    h.subunit,
                    h.app_access_name as logical_access_name,
                    h.record_date,
                    h.status,
                    h.process_access,
                    a.position_role
                FROM historico h
                LEFT JOIN applications a ON h.app_access_name = a.logical_access_name
                WHERE h.scotia_id = ?
                AND h.status = 'closed completed'
                AND h.process_access IN ('onboarding', 'lateral_movement')
                AND h.app_access_name IS NOT NULL
                ORDER BY h.record_date DESC
            ''', (scotia_id,))

            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            current_access = [dict(zip(columns, row)) for row in rows]

            conn.close()
            return current_access

        except Exception as e:
            print(f"Error obteniendo accesos actuales del empleado: {e}")
            return []

    def get_employee_current_position_access(self, scotia_id: str) -> List[Dict[str, Any]]:
        """Obtiene todos los accesos actuales del empleado: asignados por aplicación, manuales y flex staff"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Primero obtener la posición actual del empleado
            cursor.execute('''
                SELECT unit, position FROM headcount 
                WHERE scotia_id = ? AND activo = 1
            ''', (scotia_id,))
            
            emp_data = cursor.fetchone()
            has_headcount = bool(emp_data)
            current_unit, current_position = (emp_data if has_headcount else (None, None))
            if has_headcount:
                print(f"DEBUG: Accesos actuales - Posición actual: {current_position} en unidad: {current_unit}")
                print(f"DEBUG: Onboarding: mostrar todos cuyo último proceso fue onboarding (sin filtrar por unidad/posición)")
                print(f"DEBUG: Lateral Movement: solo los que coinciden con posición actual")
            else:
                print("DEBUG: SID sin registro activo en headcount - usando modo fallback solo con historico")
                print(f"DEBUG: Onboarding: mostrar todos cuyo último proceso fue onboarding")
                print(f"DEBUG: Lateral Movement: mostrar todos cuyo último proceso fue lateral_movement")

            # Obtener la posición temporal específica de Flex Staff más reciente
            cursor.execute('''
                SELECT TOP 1 event_description
                FROM historico 
                WHERE scotia_id = ? 
                AND process_access = 'flex_staff' 
                AND status = 'closed completed'
                ORDER BY record_date DESC
            ''', (scotia_id,))
            
            flex_staff_desc = cursor.fetchone()
            flex_staff_position = None
            if flex_staff_desc:
                # Extraer la posición temporal de la descripción: "(flex staff - POSICIÓN)"
                import re
                match = re.search(r'\(flex staff - ([^)]+)\)', flex_staff_desc[0])
                if match:
                    flex_staff_position = match.group(1).strip()
                    print(f"DEBUG: Posición temporal de Flex Staff encontrada: {flex_staff_position}")
            
            # Construir el filtro para Flex Staff
            flex_staff_filter = f'%flex staff - {flex_staff_position}%' if flex_staff_position else '%flex staff%'

            # Primero verificar qué registros hay en el historial para este empleado
            cursor.execute('''
                SELECT COUNT(*), process_access, status
                FROM historico
                WHERE scotia_id = ?
                GROUP BY process_access, status
            ''', (scotia_id,))
            debug_counts = cursor.fetchall()
            print(f"DEBUG: Registros en historial por tipo y status:")
            total_registros = 0
            for count, proc, stat in debug_counts:
                print(f"  {proc} - {stat}: {count}")
                total_registros += count
            print(f"DEBUG: Total de registros en historial: {total_registros}")
            
            # Verificar específicamente registros 'closed completed'
            cursor.execute('''
                SELECT COUNT(*), process_access
                FROM historico
                WHERE scotia_id = ?
                AND status = 'closed completed'
                AND process_access IN ('onboarding', 'lateral_movement', 'flex_staff', 'manual_access', 'offboarding')
                GROUP BY process_access
            ''', (scotia_id,))
            completed_counts = cursor.fetchall()
            print(f"DEBUG: Registros 'closed completed' disponibles:")
            for count, proc in completed_counts:
                print(f"  {proc}: {count}")
            
            # Verificar cuántos accesos tienen offboarding como último proceso
            cursor.execute('''
                WITH AllProcessesByApp AS (
                    SELECT 
                        app_access_name,
                        process_access as last_process,
                        MAX(record_date) as last_record_date
                    FROM historico
                    WHERE scotia_id = ?
                    AND status = 'closed completed'
                    AND process_access IN ('onboarding', 'lateral_movement', 'flex_staff', 'manual_access', 'offboarding')
                    AND app_access_name IS NOT NULL
                    GROUP BY app_access_name, process_access
                ),
                LastProcessByApp AS (
                    SELECT 
                        app_access_name,
                        last_process,
                        ROW_NUMBER() OVER (PARTITION BY app_access_name ORDER BY last_record_date DESC) as rn
                    FROM AllProcessesByApp
                )
                SELECT COUNT(*) 
                FROM LastProcessByApp 
                WHERE rn = 1 AND last_process = 'offboarding'
            ''', (scotia_id,))
            offboarding_count = cursor.fetchone()[0]
            print(f"DEBUG: Accesos excluidos por tener offboarding como último proceso: {offboarding_count}")

            # Obtener unidad_subunidad del headcount si existe
            unidad_subunidad = None
            if has_headcount:
                cursor.execute('''
                    SELECT unidad_subunidad FROM headcount 
                    WHERE scotia_id = ? AND activo = 1
                ''', (scotia_id,))
                unidad_result = cursor.fetchone()
                unidad_subunidad = unidad_result[0] if unidad_result else None
                print(f"DEBUG: unidad_subunidad del headcount: {unidad_subunidad}")

            # Obtener todos los tipos de accesos actuales
            # IMPORTANTE: Excluir accesos cuyo último proceso sea 'offboarding' (ya fueron removidos)
            query = '''
                WITH AllProcessesByApp AS (
                    -- Para cada aplicación, obtener todos los procesos con sus fechas máximas
                    SELECT 
                        app_access_name,
                        process_access as last_process,
                        MAX(record_date) as last_record_date
                    FROM historico
                    WHERE scotia_id = ?
                    AND status = 'closed completed'
                    AND process_access IN ('onboarding', 'lateral_movement', 'flex_staff', 'manual_access', 'offboarding')
                    AND app_access_name IS NOT NULL
                    GROUP BY app_access_name, process_access
                ),
                LastProcessByApp AS (
                    -- Para cada aplicación, obtener solo el proceso más reciente (último en el tiempo)
                    SELECT 
                        app_access_name,
                        last_process,
                        last_record_date,
                        ROW_NUMBER() OVER (PARTITION BY app_access_name ORDER BY last_record_date DESC) as rn
                    FROM AllProcessesByApp
                )
                SELECT 
                    h.scotia_id,
                    h.subunit as unit,
                    h.subunit,
                    h.app_access_name as logical_access_name,
                    MAX(h.record_date) as record_date,
                    h.status,
                    h.process_access,
                    MAX(h.event_description) as event_description,
                    CASE 
                        WHEN h.process_access = 'flex_staff' THEN 
                            SUBSTRING(MAX(h.event_description), CHARINDEX('flex staff - ', MAX(h.event_description)) + 13, 
                                     CHARINDEX(')', MAX(h.event_description), CHARINDEX('flex staff - ', MAX(h.event_description))) - CHARINDEX('flex staff - ', MAX(h.event_description)) - 13)
                        WHEN h.process_access = 'manual_access' THEN 
                            COALESCE(MAX(a.position_role), 'Manual')
                        ELSE MAX(a.position_role)
                    END as position_role,
                    MAX(a.role_name) as role_name,
                    MAX(a.description) as description,
                    CASE 
                        WHEN h.process_access = 'manual_access' THEN 'Manual'
                        WHEN h.process_access = 'flex_staff' THEN 'Flex Staff'
                        WHEN h.process_access IN ('onboarding', 'lateral_movement') THEN 'Aplicación'
                        ELSE 'Otro'
                    END as access_type
                FROM historico h
                LEFT JOIN applications a ON h.app_access_name = a.logical_access_name
                INNER JOIN LastProcessByApp lp ON h.app_access_name = lp.app_access_name AND lp.rn = 1
                WHERE h.scotia_id = ?
                AND h.status = 'closed completed'
                AND h.process_access IN ('onboarding', 'lateral_movement', 'flex_staff', 'manual_access')
                AND h.app_access_name IS NOT NULL
                -- EXCLUIR accesos cuyo último proceso sea 'offboarding' (ya fueron removidos)
                AND lp.last_process != 'offboarding'
                AND (
                    -- Mostrar onboarding si fue el último proceso (sin filtrar por unidad/posición)
                    (lp.last_process = 'onboarding' AND h.process_access = 'onboarding')
                    OR
                    -- Mostrar lateral_movement si fue el último proceso
                    -- Y si hay headcount, verificar que coincida con posición actual
                    (lp.last_process = 'lateral_movement' AND h.process_access = 'lateral_movement'
                     {lateral_condition})
                    OR
                    -- Mostrar manual_access siempre (si fue el último proceso)
                    (lp.last_process = 'manual_access' AND h.process_access = 'manual_access')
                    OR
                    -- Mostrar flex_staff con el filtro de posición temporal (si fue el último proceso)
                    (lp.last_process = 'flex_staff' AND h.process_access = 'flex_staff' 
                     AND h.event_description LIKE ?)
                )
                GROUP BY h.scotia_id, h.subunit, h.app_access_name, h.status, h.process_access
                ORDER BY h.process_access, MAX(h.record_date) DESC
            '''

            # Construir la condición para lateral_movement
            # Para lateral_movement, si hay headcount, solo mostrar si coincide con unidad_subunidad y posición
            # Para onboarding, mostrar todos sin restricciones
            if has_headcount and unidad_subunidad:
                # Si hay headcount, filtrar lateral_movement por unidad_subunidad y posición
                # Pero solo si la aplicación tiene estos campos definidos
                lateral_condition = "AND (a.unidad_subunidad = ? AND a.position_role = ?)"
                params = (scotia_id, scotia_id, unidad_subunidad, current_position, flex_staff_filter)
                print(f"DEBUG: Usando filtro lateral_movement con unidad_subunidad={unidad_subunidad}, position={current_position}")
            else:
                # Sin headcount o sin unidad_subunidad: mostrar todos los lateral_movement también
                lateral_condition = ""
                params = (scotia_id, scotia_id, flex_staff_filter)
                print(f"DEBUG: Sin filtro lateral_movement (no hay headcount o unidad_subunidad)")
            
            query = query.format(lateral_condition=lateral_condition)
            print(f"DEBUG: Ejecutando consulta con {len(params)} parámetros")
            print(f"DEBUG: Parámetros: scotia_id (2 veces)={scotia_id}, unidad_subunidad={unidad_subunidad if has_headcount else 'N/A'}, position={current_position if has_headcount else 'N/A'}, flex_staff_filter={flex_staff_filter}")
            try:
                cursor.execute(query, params)
            except Exception as query_error:
                print(f"ERROR en consulta SQL: {query_error}")
                print(f"Query: {query}")
                print(f"Params: {params}")
                raise

            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            current_access = [dict(zip(columns, row)) for row in rows]
            
            print(f"DEBUG: Accesos encontrados: {len(current_access)}")
            for acceso in current_access:
                print(f"DEBUG: - {acceso.get('logical_access_name', '')} | {acceso.get('process_access', '')} | {acceso.get('position_role', '')} | {acceso.get('access_type', '')}")
                
            # Debug específico para accesos manuales
            manual_accesses = [a for a in current_access if a.get('process_access') == 'manual_access']
            print(f"DEBUG: Accesos manuales encontrados: {len(manual_accesses)}")
            for manual in manual_accesses:
                print(f"DEBUG: Manual - {manual.get('logical_access_name', '')} | Status: {manual.get('status', '')}")

            conn.close()
            return current_access

        except Exception as e:
            print(f"Error obteniendo accesos actuales del empleado: {e}")
            return []

    # ==============================
    # MÉTODOS DE LÓGICA DE NEGOCIO
    # ==============================

    def update_employee_status(self, scotia_id: str, active: bool) -> Tuple[bool, str]:
        """Actualiza el estado activo/inactivo de un empleado"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar que el empleado existe
            cursor.execute('SELECT COUNT(*) FROM headcount WHERE scotia_id = ?', (scotia_id,))
            result = cursor.fetchone()
            if not result or result[0] == 0:
                conn.close()
                return False, f"Empleado {scotia_id} no encontrado"
            
            # Actualizar estado
            if active:
                cursor.execute('''
                    UPDATE headcount 
                    SET activo = 1, inactivation_date = NULL
                    WHERE scotia_id = ?
                ''', (scotia_id,))
                status_text = "activo"
            else:
                cursor.execute('''
                    UPDATE headcount 
                    SET activo = 0, inactivation_date = ?
                    WHERE scotia_id = ?
                ''', (datetime.now().isoformat(), scotia_id))
                status_text = "inactivo"
            
            conn.commit()
            conn.close()
            
            return True, f"Estado del empleado {scotia_id} cambiado a {status_text}"
            
        except Exception as e:
            return False, f"Error actualizando estado del empleado: {str(e)}"

    def process_employee_onboarding(self, scotia_id: str, position: str, unit: str, 
                                   responsible: str = "Sistema",
                                   subunit: Optional[str] = None) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Procesa el onboarding de un empleado y determina qué accesos necesita.
        Crea registros por cada app que coincida con (unit, subunit?, position_role) **sin duplicados**.
        Actualiza la posición y unidad del empleado si están vacías.
        Cambia el estado del empleado de inactivo a activo automáticamente.
        """
        try:
            # 1. Verificar que el empleado existe
            employee = self.get_employee_by_id(scotia_id)
            if not employee:
                return False, f"Empleado {scotia_id} no encontrado", []

            # 2. Actualizar estado del empleado a activo
            success, message = self.update_employee_status(scotia_id, True)
            if success:
                print(f"✅ {message}")
            else:
                print(f"⚠️ {message}")

            # 3. Usar el valor de unidad_subunidad del formulario para filtrar
            # Este valor viene del campo "Nueva Unidad/Subunidad" del formulario
            unidad_subunidad = unit  # Usar directamente el valor del formulario
            
            # 4. Actualizar posición, unidad y unidad_subunidad del empleado si están vacías
            current_position = self._safe_strip(employee.get('position'), '')
            current_unit = self._safe_strip(employee.get('unit'), '')
            current_unidad_subunidad = self._safe_strip(employee.get('unidad_subunidad'), '')
            
            if not current_position or not current_unit or not current_unidad_subunidad:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE headcount 
                    SET position = ?, unit = ?, unidad_subunidad = ?
                    WHERE scotia_id = ?
                ''', (position, unit, unidad_subunidad, scotia_id))
                conn.commit()
                conn.close()
                print(f"✅ Posición, unidad y unidad_subunidad actualizadas para {scotia_id}")
                print(f"  - unidad_subunidad: '{unidad_subunidad}' (del formulario)")
            else:
                print(f"✅ Empleado ya tiene todos los campos poblados")
                print(f"  - unidad_subunidad actual: '{current_unidad_subunidad}'")
            
            # 5. Obtener aplicaciones requeridas para la posición y unidad/subunidad
            required_apps = self.get_applications_by_position(position, unidad_subunidad, subunit=subunit)
            if not required_apps:
                return False, f"No se encontraron aplicaciones para la posición '{position}'", []

            # 6. Crear registros históricos para cada aplicación (dedupe por tripleta normalizada)
            case_id = f"CASE-{datetime.now().strftime('%Y%m%d%H%M%S%f')}-{scotia_id}"
            created_records = []
            seen_triplets = set()

            for app in required_apps:
                unit_n = self._safe_strip(app.get('unit'), '').upper()
                pos_n = self._safe_strip(app.get('position_role'), '').upper()
                lan_n = self._safe_strip(app.get('logical_access_name'), '').upper()

                tkey = (unit_n, pos_n, lan_n)
                if tkey in seen_triplets:
                    continue
                seen_triplets.add(tkey)

                record_data = {
                    'scotia_id': scotia_id,
                    'case_id': case_id,
                    'responsible': responsible,
                    'process_access': 'onboarding',
                    'subunit': app.get('subunit') or '',  # ya no afecta dedupe
                    'event_description': f"Otorgamiento de acceso para {app.get('logical_access_name')}",
                    'ticket_email': app.get('path_email_url', ''),
                    'app_access_name': app.get('logical_access_name'),
                    'computer_system_type': 'Desktop',
                    'status': 'Pendiente',
                    'general_status_ticket': 'En Proceso'
                }

                success, message = self.create_historical_record(record_data)
                if success:
                    created_records.append(record_data)
                else:
                    print(f"Error creando registro para {app.get('logical_access_name')}: {message}")

            return True, f"Onboarding procesado para {scotia_id}. {len(created_records)} accesos requeridos.", created_records

        except Exception as e:
            return False, f"Error procesando onboarding: {str(e)}", []

    def process_employee_offboarding(self, scotia_id: str, responsible: str = "Sistema") -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Procesa el offboarding de un empleado (revoca todo lo que figure completado).
        
        Busca directamente en la base de datos todos los accesos con 'closed completed' del empleado,
        sin filtrar por subunidad u otros campos. Solo busca por scotia_id.
        
        Solo revoca accesos que:
        - Tienen estado 'closed completed'
        - Son de tipos: onboarding, lateral_movement, flex_staff, manual_access
        - NO han sido ya revocados en un offboarding anterior
        """
        try:
            employee = self.get_employee_by_id(scotia_id)
            if not employee:
                return False, f"Empleado {scotia_id} no encontrado", []

            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Buscar directamente en la base de datos todos los accesos completados del empleado
            # que NO hayan sido ya revocados en un offboarding anterior
            cursor.execute('''
                SELECT DISTINCT
                    h.id,
                    h.app_access_name,
                    h.process_access,
                    h.record_date,
                    h.subunit,
                    h.event_description
                FROM historico h
                WHERE h.scotia_id = ?
                AND UPPER(LTRIM(RTRIM(h.status))) = 'CLOSED COMPLETED'
                AND h.process_access IN ('onboarding', 'lateral_movement', 'flex_staff', 'manual_access')
                AND h.app_access_name IS NOT NULL
                AND NOT EXISTS (
                    -- Verificar que no haya un offboarding completado posterior para este mismo acceso
                    SELECT 1 
                    FROM historico h2 
                    WHERE h2.scotia_id = h.scotia_id
                    AND h2.app_access_name = h.app_access_name
                    AND h2.process_access = 'offboarding'
                    AND UPPER(LTRIM(RTRIM(h2.status))) = 'CLOSED COMPLETED'
                    AND h2.record_date >= h.record_date
                )
                ORDER BY h.record_date DESC
            ''', (scotia_id,))
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            active_access = [dict(zip(columns, row)) for row in rows]
            
            conn.close()
            
            print(f"DEBUG: Accesos encontrados para revocar (solo 'closed completed' y no revocados previamente): {len(active_access)}")
            for acc in active_access:
                app_name = acc.get('app_access_name') or ''
                print(f"DEBUG: Acceso a revocar: {app_name} - Tipo: {acc.get('process_access', 'N/A')}")

            case_id = f"CASE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{scotia_id}"
            created_records = []
            processed_access = []
            skipped_inactive_access = []

            for access in active_access:
                app_name = self._safe_strip(access.get('app_access_name'), '')
                if not app_name:
                    continue  # Saltar si no hay nombre de aplicación
                
                access_type = self._safe_strip(access.get('process_access'), '')
                
                # Verificar si el acceso de la aplicación está activo
                app_info = self._get_application_by_name(app_name)
                access_status = self._safe_strip(app_info.get('access_status'), '') if app_info else ''
                normalized_status = access_status.lower()
                is_active_status = normalized_status in ('activo', 'active')
                if access_status and not is_active_status:
                    print(f"DEBUG: Omitiendo offboarding para {app_name} porque el acceso está '{access_status}'")
                    skipped_inactive_access.append(app_name)
                    continue
                
                # Crear descripción específica según el tipo de acceso
                if access_type == 'flex_staff':
                    event_description = f"Revocación de acceso temporal (flex staff) para {app_name}"
                elif access_type == 'manual_access':
                    event_description = f"Revocación de acceso manual para {app_name}"
                elif access_type in ('onboarding', 'lateral_movement'):
                    event_description = f"Revocación de acceso de posición para {app_name}"
                else:
                    event_description = f"Revocación de acceso para {app_name}"
                
                record_data = {
                    'scotia_id': scotia_id,
                    'case_id': case_id,
                    'responsible': responsible,
                    'process_access': 'offboarding',
                    'subunit': 'out of the company',  # Subárea fija para offboarding
                    'event_description': event_description,
                    'ticket_email': f"{responsible}@empresa.com",
                    'app_access_name': app_name,
                    'computer_system_type': 'Desktop',
                    'status': 'Pendiente',
                    'general_status_ticket': 'En Proceso'
                }

                success, message = self.create_historical_record(record_data)
                if success:
                    created_records.append(record_data)
                    processed_access.append(access)
                else:
                    print(f"Error creando registro de offboarding para {app_name}: {message}")

            # Marcar empleado como inactivo y registrar fecha de inactivación
            conn = self.get_connection()
            cursor = conn.cursor()
            inactivation_date = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                UPDATE headcount 
                SET activo = 0, 
                    inactivation_date = ?, 
                    unit = 'out of the unit',
                    unidad_subunidad = 'out of the unit'
                WHERE scotia_id = ?
            ''', (inactivation_date, scotia_id))
            conn.commit()
            conn.close()

            # Crear mensaje detallado con conteo por tipo de acceso
            access_counts = {}
            for access in processed_access:
                access_type = access.get('process_access', '')
                access_counts[access_type] = access_counts.get(access_type, 0) + 1
            
            message = f"Offboarding procesado para {scotia_id}. {len(created_records)} accesos a revocar (solo 'closed completed'):\n"
            for access_type, count in access_counts.items():
                if access_type == 'onboarding':
                    message += f"- Accesos de onboarding: {count}\n"
                elif access_type == 'lateral_movement':
                    message += f"- Accesos de movimiento lateral: {count}\n"
                elif access_type == 'flex_staff':
                    message += f"- Accesos temporales (flex staff): {count}\n"
                elif access_type == 'manual_access':
                    message += f"- Accesos manuales: {count}\n"
                else:
                    message += f"- Accesos {access_type}: {count}\n"
            
            if skipped_inactive_access:
                message += f"- Accesos omitidos por estar inactivos: {', '.join(skipped_inactive_access)}\n"
            
            return True, message.strip(), created_records

        except Exception as e:
            return False, f"Error procesando offboarding: {str(e)}", []

    def process_lateral_movement(self, scotia_id: str, new_position: str, new_unit: str, 
                                responsible: str = "Sistema", new_subunit: Optional[str] = None) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Procesa un movimiento lateral: revoca accesos de posición anterior y otorga nuevos.
        
        Lógica mejorada:
        - REVOCA solo accesos específicos de la posición anterior que no son necesarios en la nueva
        - OTORGA nuevos accesos de la nueva posición
        - Evita duplicados comparando por logical_access_name y unidad
        """
        try:
            print(f"DEBUG: Iniciando lateral movement para {scotia_id}")
            print(f"DEBUG: Nueva posición: {new_position}")
            print(f"DEBUG: Nueva unidad: {new_unit}")
            print(f"DEBUG: Nueva subunidad: {new_subunit}")
            
            employee = self.get_employee_by_id(scotia_id)
            if not employee:
                print(f"DEBUG: Error - Empleado {scotia_id} no encontrado")
                return False, f"Empleado {scotia_id} no encontrado", []

            old_position = self._safe_strip(employee.get('position'), '')
            old_unit = self._safe_strip(employee.get('unit'), '')
            old_unidad_subunidad = self._safe_strip(employee.get('unidad_subunidad'), '')
            
            print(f"DEBUG: Posición anterior: {old_position}")
            print(f"DEBUG: Unidad anterior: {old_unit}")
            print(f"DEBUG: Unidad/Subunidad anterior: {old_unidad_subunidad}")

            # Obtener accesos requeridos para la nueva posición (usando unidad_subunidad como el onboarding)
            new_unidad_subunidad = f"{new_unit}/{new_subunit}" if new_subunit else new_unit
            print(f"DEBUG: Nueva unidad_subunidad: {new_unidad_subunidad}")
            new_mesh_apps = self.get_applications_by_position(new_position, new_unidad_subunidad, subunit=new_subunit)
            print(f"DEBUG: Aplicaciones encontradas para nueva posición: {len(new_mesh_apps)}")
            for app in new_mesh_apps:
                print(f"DEBUG: App requerida para nueva posición: {app.get('logical_access_name', '')} - Unidad/Subunidad: {app.get('unidad_subunidad', '')}")
            
            # Obtener accesos ACTUALES del empleado (no los de la malla anterior, sino los que realmente tiene)
            current_access = self.get_employee_current_position_access(scotia_id)
            print(f"DEBUG: Accesos actuales del empleado: {len(current_access)}")
            
            # Crear índice de accesos actuales usando logical_access_name + unidad_subunidad
            # Obtener unidad_subunidad de todas las aplicaciones de una vez
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener unidad_subunidad del headcount para usar como fallback
            cursor.execute('SELECT unidad_subunidad FROM headcount WHERE scotia_id = ?', (scotia_id,))
            hc_result = cursor.fetchone()
            default_unidad_subunidad = self._safe_strip(hc_result[0] if hc_result else None, '').upper()
            
            # Obtener unidad_subunidad de todas las aplicaciones actuales de una vez
            app_names = [self._safe_strip(acc.get('logical_access_name'), '').upper() for acc in current_access if acc.get('logical_access_name')]
            app_unidad_subunidad_map = {}
            
            if app_names:
                placeholders = ','.join(['?'] * len(app_names))
                cursor.execute(f'''
                    SELECT DISTINCT a.logical_access_name, a.unidad_subunidad
                    FROM applications a
                    WHERE a.logical_access_name IN ({placeholders})
                ''', tuple(app_names))
                for row in cursor.fetchall():
                    app_unidad_subunidad_map[self._safe_strip(row[0], '').upper()] = self._safe_strip(row[1], '').upper()
            
            conn.close()
            
            current_access_by_key = {}
            for acc in current_access:
                app_name = self._safe_strip(acc.get('logical_access_name'), '').upper()
                if app_name:
                    # Usar unidad_subunidad de la aplicación si está disponible, sino usar la del headcount
                    app_unidad_subunidad = app_unidad_subunidad_map.get(app_name, default_unidad_subunidad)
                    
                    key = f"{app_name}|||{app_unidad_subunidad}"
                    current_access_by_key[key] = {
                        'logical_access_name': app_name,
                        'unidad_subunidad': app_unidad_subunidad,
                        'process_access': acc.get('process_access', ''),
                        'status': acc.get('status', '')
                    }
            
            print(f"DEBUG: Accesos actuales indexados: {len(current_access_by_key)}")
            for key, acc in current_access_by_key.items():
                print(f"DEBUG: Acceso actual: {acc.get('logical_access_name', '')} - {acc.get('unidad_subunidad', '')}")
            
            # Crear índice de accesos requeridos para la nueva posición
            new_apps_by_key = {}
            for app in new_mesh_apps:
                app_name = self._safe_strip(app.get('logical_access_name'), '').upper()
                app_unidad_subunidad = self._safe_strip(app.get('unidad_subunidad'), '').upper()
                key = f"{app_name}|||{app_unidad_subunidad}"
                if app_name:  # Solo agregar si tiene nombre
                    new_apps_by_key[key] = app
            
            print(f"DEBUG: Accesos requeridos para nueva posición: {len(new_apps_by_key)}")
            for key, app in new_apps_by_key.items():
                print(f"DEBUG: Acceso requerido: {app.get('logical_access_name', '')} - {app.get('unidad_subunidad', '')}")
            
            # Calcular qué revocar y qué otorgar
            to_revoke = []
            to_grant = []
            maintained = []
            
            # REVOCAR: accesos actuales que NO están en los requeridos de la nueva posición
            # Solo si están en estado 'closed completed'
            for key, current_acc in current_access_by_key.items():
                if key not in new_apps_by_key:
                    # Este acceso actual no es necesario en la nueva posición, revocarlo
                    # Pero solo si está en 'closed completed'
                    if self._safe_strip(current_acc.get('status'), '').lower() == 'closed completed':
                        # Buscar la app completa en applications para obtener todos los datos
                        conn = self.get_connection()
                        cursor = conn.cursor()
                        cursor.execute('''
                            SELECT logical_access_name, unidad_subunidad, subunit, path_email_url
                            FROM applications
                            WHERE logical_access_name = ?
                        ''', (current_acc.get('logical_access_name', ''),))
                        app_data = cursor.fetchone()
                        conn.close()
                        
                        if app_data:
                            app_dict = {
                                'logical_access_name': app_data[0],
                                'unidad_subunidad': app_data[1] or current_acc.get('unidad_subunidad', ''),
                                'subunit': app_data[2] or '',
                                'path_email_url': app_data[3] or ''
                            }
                            to_revoke.append(app_dict)
                            print(f"DEBUG: Marcado para revocar (no necesario en nueva posición): {app_dict.get('logical_access_name', '')} - {app_dict.get('unidad_subunidad', '')}")
                        else:
                            # Si no está en applications, crear un dict básico
                            app_dict = {
                                'logical_access_name': current_acc.get('logical_access_name', ''),
                                'unidad_subunidad': current_acc.get('unidad_subunidad', ''),
                                'subunit': '',
                                'path_email_url': ''
                            }
                            to_revoke.append(app_dict)
                            print(f"DEBUG: Marcado para revocar (no está en applications): {app_dict.get('logical_access_name', '')}")
                else:
                    # Este acceso ya lo tiene y también lo necesita en la nueva posición, mantenerlo
                    maintained.append(current_acc)
                    print(f"DEBUG: Acceso mantenido (ya lo tiene y lo necesita): {current_acc.get('logical_access_name', '')} - {current_acc.get('unidad_subunidad', '')}")
            
            # OTORGAR: accesos requeridos de la nueva posición que NO tiene actualmente
            for key, app in new_apps_by_key.items():
                if key not in current_access_by_key:
                    to_grant.append(app)
                    print(f"DEBUG: Marcado para otorgar (no lo tiene actualmente): {app.get('logical_access_name', '')} - {app.get('unidad_subunidad', '')}")
                else:
                    print(f"DEBUG: Acceso ya existe (no se otorga): {app.get('logical_access_name', '')} - {app.get('unidad_subunidad', '')}")
            
            print(f"DEBUG: Resumen - Mantener: {len(maintained)}, Revocar: {len(to_revoke)}, Otorgar: {len(to_grant)}")

            case_id = f"CASE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{scotia_id}"
            created_records = []

            # 1. REVOCAR accesos de la posición anterior que ya no son necesarios
            print(f"DEBUG: Procesando {len(to_revoke)} aplicaciones para revocar")
            for acc in to_revoke:
                print(f"DEBUG: Procesando revocación: {acc.get('logical_access_name', '')}")
                record_data = {
                    'scotia_id': scotia_id,
                    'case_id': case_id,
                    'responsible': responsible,
                    'process_access': 'offboarding',
                    'subunit': acc.get('subunit', ''),
                    'event_description': f"Revocación de acceso para {acc.get('logical_access_name', '')} (lateral movement - cambio de posición)",
                    'ticket_email': acc.get('path_email_url', ''),
                    'app_access_name': acc.get('logical_access_name', ''),
                    'computer_system_type': 'Desktop',
                    'status': 'Pendiente',
                    'general_status_ticket': 'En Proceso'
                }
                print(f"DEBUG: Creando registro de revocación para {acc.get('logical_access_name', '')}")
                ok, message = self.create_historical_record(record_data)
                print(f"DEBUG: Resultado de revocación: {ok}, Mensaje: {message}")
                if ok:
                    created_records.append(record_data)
                    print(f"DEBUG: Registro de revocación agregado a created_records")
                else:
                    print(f"DEBUG: Error creando registro de revocación: {message}")

            # 2. OTORGAR nuevos accesos de la nueva posición que no tiene actualmente
            print(f"DEBUG: Procesando {len(to_grant)} aplicaciones para otorgar")
            for app in to_grant:
                print(f"DEBUG: Procesando otorgamiento: {app.get('logical_access_name', '')}")
                record_data = {
                    'scotia_id': scotia_id,
                    'case_id': case_id,
                    'responsible': responsible,
                    'process_access': 'lateral_movement',
                    'subunit': app.get('subunit', ''),
                    'event_description': f"Otorgamiento de acceso para {app.get('logical_access_name', '')} (lateral movement - nueva posición)",
                    'ticket_email': app.get('path_email_url', ''),
                    'app_access_name': app.get('logical_access_name', ''),
                    'computer_system_type': 'Desktop',
                    'status': 'Pendiente',
                    'general_status_ticket': 'En Proceso'
                }
                print(f"DEBUG: Creando registro de otorgamiento para {app.get('logical_access_name', '')}")
                ok, message = self.create_historical_record(record_data)
                print(f"DEBUG: Resultado de otorgamiento: {ok}, Mensaje: {message}")
                if ok:
                    created_records.append(record_data)
                    print(f"DEBUG: Registro de otorgamiento agregado a created_records")
                else:
                    print(f"DEBUG: Error creando registro de otorgamiento: {message}")

            # Actualizar posición/unidad del empleado
            success, message = self.update_employee_position(scotia_id, new_position, new_unit, new_unidad_subunidad)
            if not success:
                return False, f"Error actualizando posición: {message}", []

            # Crear mensaje detallado
            revoke_details = []
            if to_revoke:
                revoke_details = [app.get('logical_access_name', '') for app in to_revoke]
            
            grant_details = []
            if to_grant:
                grant_details = [app.get('logical_access_name', '') for app in to_grant]
            
            maintained_details = []
            if maintained:
                maintained_details = [app.get('logical_access_name', '') for app in maintained]
            
            message = f"Movimiento lateral procesado para {scotia_id}.\n"
            message += f"- Accesos mantenidos ({len(maintained)}): {', '.join(maintained_details) if maintained_details else 'Ninguno'}\n"
            message += f"- Accesos revocados ({len(to_revoke)}): {', '.join(revoke_details) if revoke_details else 'Ninguno'}\n"
            message += f"- Accesos otorgados ({len(to_grant)}): {', '.join(grant_details) if grant_details else 'Ninguno'}"

            return True, message, created_records

        except Exception as e:
            return False, f"Error procesando movimiento lateral: {str(e)}", []

    def process_flex_staff_assignment(self, scotia_id: str, temporary_position: str, temporary_unit: str, 
                                    temporary_subunit: Optional[str] = None, duration_days: Optional[int] = None,
                                    responsible: str = "Sistema") -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Procesa una asignación de flex staff: otorga accesos temporales sin revocar los originales.
        
        Lógica de flex staff:
        - MANTIENE todos los accesos de la posición original
        - OTORGA accesos adicionales de la posición temporal
        - Marca los accesos temporales con fecha de expiración
        - NO revoca ningún acceso existente
        """
        try:
            print(f"DEBUG: Iniciando flex staff para {scotia_id}")
            print(f"DEBUG: Posición temporal: {temporary_position}")
            print(f"DEBUG: Unidad temporal: {temporary_unit}")
            print(f"DEBUG: Subunidad temporal: {temporary_subunit}")
            print(f"DEBUG: Duración: {duration_days} días")
            
            employee = self.get_employee_by_id(scotia_id)
            if not employee:
                print(f"DEBUG: Error - Empleado {scotia_id} no encontrado")
                return False, f"Empleado {scotia_id} no encontrado", []

            original_position = self._safe_strip(employee.get('position'), '')
            original_unit = self._safe_strip(employee.get('unit'), '')

            # Obtener accesos actuales del empleado (posición original)
            current_access = self.get_employee_current_access(scotia_id)
            
            # También obtener accesos flex_staff existentes (pendientes y completados) para evitar duplicados
            flex_staff_access = self._get_all_flex_staff_access(scotia_id)
            print(f"DEBUG: Accesos flex_staff existentes (pendientes y completados): {len(flex_staff_access)}")
            
            # Obtener accesos requeridos para la posición temporal usando lógica flexible
            # No usar subunidad para flex staff - buscar solo por posición y unidad
            print(f"DEBUG: Buscando aplicaciones para posición temporal: {temporary_position} en unidad: {temporary_unit}")
            temp_mesh_apps = self.get_applications_by_position_flexible(temporary_position, temporary_unit, subunit=None)
            print(f"DEBUG: Aplicaciones encontradas para posición temporal: {len(temp_mesh_apps)}")
            for app in temp_mesh_apps:
                print(f"DEBUG: - {app.get('logical_access_name', '')} | {app.get('unit', '')} | {app.get('subunit', '')}")
            
            # Crear índices para comparación (incluyendo accesos flex_staff existentes)
            current_apps_by_name = {}
            for acc in current_access:
                app_name = self._safe_strip(acc.get('logical_access_name'), '').upper()
                if app_name:
                    current_apps_by_name[app_name] = acc
            
            # Agregar accesos flex_staff existentes a la comparación para evitar duplicados
            for acc in flex_staff_access:
                app_name = self._safe_strip(acc.get('logical_access_name'), '').upper()
                if app_name and app_name not in current_apps_by_name:
                    current_apps_by_name[app_name] = acc
                    print(f"DEBUG: Acceso flex_staff existente incluido en comparación: {app_name}")
            
            temp_apps_by_name = {}
            for app in temp_mesh_apps:
                app_name = self._safe_strip(app.get('logical_access_name'), '').upper()
                if app_name:
                    temp_apps_by_name[app_name] = app

            # Calcular qué accesos temporales otorgar (solo los que no tiene)
            to_grant_temp = []
            
            for app_name, app in temp_apps_by_name.items():
                if app_name not in current_apps_by_name:
                    to_grant_temp.append(app)

            case_id = f"FLEX-{datetime.now().strftime('%Y%m%d%H%M%S')}-{scotia_id}"
            created_records = []

            # OTORGAR accesos temporales de la nueva posición
            print(f"DEBUG: Procesando {len(to_grant_temp)} aplicaciones para flex staff")
            for app in to_grant_temp:
                print(f"DEBUG: Procesando flex staff: {app.get('logical_access_name', '')}")
                # Calcular fecha de expiración si se especifica duración
                expiration_date = None
                if duration_days:
                    expiration_date = datetime.now().replace(hour=23, minute=59, second=59) + timedelta(days=duration_days)
                
                record_data = {
                    'scotia_id': scotia_id,
                    'case_id': case_id,
                    'responsible': responsible,
                    'process_access': 'flex_staff',
                    'subunit': app.get('subunit', ''),
                    'event_description': f"Otorgamiento temporal de acceso para {app.get('logical_access_name', '')} (flex staff - {temporary_position})",
                    'ticket_email': app.get('path_email_url', ''),
                    'app_access_name': app.get('logical_access_name', ''),
                    'computer_system_type': 'Desktop',
                    'status': 'Pendiente',
                    'general_status_ticket': 'En Proceso',
                    'expiration_date': expiration_date.isoformat() if expiration_date else None
                }
                print(f"DEBUG: Creando registro flex staff para {app.get('logical_access_name', '')}")
                ok, message = self.create_historical_record(record_data)
                print(f"DEBUG: Resultado de flex staff: {ok}, Mensaje: {message}")
                if ok:
                    created_records.append(record_data)
                    print(f"DEBUG: Registro flex staff agregado a created_records")
                else:
                    print(f"DEBUG: Error creando registro flex staff: {message}")

            # Crear mensaje detallado
            grant_details = [app.get('logical_access_name', '') for app in to_grant_temp]
            maintained_count = len(current_apps_by_name)
            
            message = f"Asignación flex staff procesada para {scotia_id}.\n"
            message += f"- Posición original: {original_position} ({original_unit})\n"
            message += f"- Posición temporal: {temporary_position} ({temporary_unit})\n"
            message += f"- Accesos originales mantenidos: {maintained_count}\n"
            message += f"- Accesos temporales otorgados ({len(to_grant_temp)}): {', '.join(grant_details) if grant_details else 'Ninguno'}\n"
            if duration_days:
                message += f"- Duración: {duration_days} días\n"
                message += f"- Fecha de expiración: {expiration_date.strftime('%Y-%m-%d') if expiration_date else 'No especificada'}"

            return True, message, created_records

        except Exception as e:
            return False, f"Error procesando asignación flex staff: {str(e)}", []

    def process_flex_staff_return(self, scotia_id: str, responsible: str = "Sistema") -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Procesa el retorno de flex staff: revoca solo los accesos temporales.
        
        Lógica de retorno:
        - REVOCA solo accesos marcados como 'flex_staff'
        - MANTIENE todos los accesos de la posición original
        - Restaura la posición original del empleado
        """
        try:
            employee = self.get_employee_by_id(scotia_id)
            if not employee:
                return False, f"Empleado {scotia_id} no encontrado", []

            # Obtener accesos temporales (flex_staff) del empleado
            temp_access = self.get_employee_flex_staff_access(scotia_id)
            
            case_id = f"RETURN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{scotia_id}"
            created_records = []

            # REVOCAR accesos temporales
            for acc in temp_access:
                record_data = {
                    'scotia_id': scotia_id,
                    'case_id': case_id,
                    'responsible': responsible,
                    'process_access': 'flex_staff_return',
                    'subunit': acc.get('subunit', ''),
                    'event_description': f"Revocación de acceso temporal para {acc.get('logical_access_name', '')} (retorno flex staff)",
                    'ticket_email': f"{responsible}@empresa.com",  # No hay app data disponible aquí
                    'app_access_name': acc.get('logical_access_name', ''),
                    'computer_system_type': 'Desktop',
                    'status': 'Pendiente',
                    'general_status_ticket': 'En Proceso'
                }
                ok, _ = self.create_historical_record(record_data)
                if ok:
                    created_records.append(record_data)

            # Crear mensaje detallado
            revoke_details = [acc.get('logical_access_name', '') for acc in temp_access]
            
            message = f"Retorno flex staff procesado para {scotia_id}.\n"
            message += f"- Accesos temporales revocados ({len(temp_access)}): {', '.join(revoke_details) if revoke_details else 'Ninguno'}\n"
            message += f"- Accesos originales mantenidos: Todos los de la posición original"

            return True, message, created_records

        except Exception as e:
            return False, f"Error procesando retorno flex staff: {str(e)}", []

    def _get_all_flex_staff_access(self, scotia_id: str) -> List[Dict[str, Any]]:
        """Obtiene TODOS los accesos flex_staff de un empleado (pendientes y completados) para evitar duplicados"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT
                    h.app_access_name as logical_access_name,
                    h.subunit as unit,
                    h.subunit,
                    h.event_description,
                    h.record_date,
                    h.status,
                    h.expiration_date
                FROM historico h
                WHERE h.scotia_id = ?
                AND h.process_access = 'flex_staff'
                AND h.app_access_name IS NOT NULL
                ORDER BY h.app_access_name
            ''', (scotia_id,))
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            access_list = [dict(zip(columns, row)) for row in rows]
            
            conn.close()
            return access_list
            
        except Exception as e:
            print(f"Error obteniendo todos los accesos flex staff: {e}")
            return []

    def get_employee_flex_staff_access(self, scotia_id: str) -> List[Dict[str, Any]]:
        """Obtiene los accesos temporales (flex_staff) de un empleado"""
        try:
            print(f"DEBUG: Buscando accesos flex_staff para {scotia_id}")
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT
                    h.app_access_name as logical_access_name,
                    h.subunit as unit,
                    h.subunit,
                    h.event_description,
                    h.record_date,
                    h.status,
                    h.expiration_date
                FROM historico h
                WHERE h.scotia_id = ?
                AND h.process_access = 'flex_staff'
                AND h.app_access_name IS NOT NULL
                AND h.status = 'closed completed'
                ORDER BY h.app_access_name
            ''', (scotia_id,))
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            access_list = [dict(zip(columns, row)) for row in rows]
            
            print(f"DEBUG: Accesos flex_staff encontrados: {len(access_list)}")
            for acc in access_list:
                print(f"DEBUG: - {acc.get('logical_access_name', '')} | {acc.get('status', '')} | {acc.get('event_description', '')}")
            
            # Si no hay resultados, verificar qué registros existen para este empleado
            if len(access_list) == 0:
                print(f"DEBUG: No se encontraron accesos flex_staff. Verificando registros del empleado...")
                cursor.execute('''
                    SELECT process_access, app_access_name, status, event_description
                    FROM historico 
                    WHERE scotia_id = ? 
                    ORDER BY record_date DESC
                ''', (scotia_id,))
                all_records = cursor.fetchall()
                print(f"DEBUG: Todos los registros del empleado: {len(all_records)}")
                for record in all_records[:10]:  # Mostrar solo los primeros 10
                    print(f"DEBUG: - {record[0]} | {record[1]} | {record[2]} | {record[3]}")
            
            conn.close()
            return access_list
            
        except Exception as e:
            print(f"Error obteniendo accesos flex staff: {e}")
            return []

    def get_access_reconciliation_report(self, scotia_id: str) -> Dict[str, Any]:
        """Genera un reporte de conciliación mejorado que maneja mejor los cambios de posición."""
        try:
            # 1) Empleado
            employee = self.get_employee_by_id(scotia_id)
            if not employee:
                return {"error": f"Empleado {scotia_id} no encontrado"}

            emp_unit = self._safe_strip(employee.get('unit'), '')
            emp_position = self._safe_strip(employee.get('position'), '')
            emp_unidad_subunidad = self._safe_strip(employee.get('unidad_subunidad'), '')
            
            # Debug: mostrar valores del empleado
            print(f"DEBUG empleado {scotia_id}:")
            print(f"  - unit: '{emp_unit}'")
            print(f"  - position: '{emp_position}'")
            print(f"  - unidad_subunidad: '{emp_unidad_subunidad}'")
            print(f"  - Datos completos del empleado:")
            for key, value in employee.items():
                print(f"    - {key}: '{value}'")
            
            # Si no hay unidad_subunidad, construirla a partir de unit y subunit
            if not emp_unidad_subunidad:
                history = self.get_employee_history(scotia_id)
                emp_subunit = ''
                if history:
                    # Buscar el subunit más reciente del historial
                    for h in history:
                        if h.get('area') == emp_unit and h.get('subunit'):
                            emp_subunit = self._safe_strip(h.get('subunit'), '')
                            break
                
                # Si no encontramos subunit, usar un valor por defecto basado en la unidad
                if not emp_subunit:
                    emp_subunit = 'General'  # Valor por defecto
                
                emp_unidad_subunidad = f"{emp_unit}/{emp_subunit}"

            # 3) Requeridos por malla de apps para la posición/unidad_subunidad del empleado
            # Solo buscar por unidad_subunidad y position_role (comparación estricta)
            required_apps = self.get_applications_by_position(
                position=emp_position,
                unidad_subunidad=emp_unidad_subunidad,
                subunit=None,  # No filtrar por subunit para ser más inclusivo
                title=None,    # No tenemos title del empleado
            )

            # Filtrar aplicaciones que coincidan exactamente con unidad_subunidad y position_role
            filtered_required_apps = []
            for app in required_apps:
                app_unidad_subunidad = self._safe_strip(app.get('unidad_subunidad'), '')
                app_position = self._safe_strip(app.get('position_role'), '')
                
                # Solo incluir si coincide exactamente con unidad_subunidad y position
                if app_unidad_subunidad == emp_unidad_subunidad and app_position == emp_position:
                    filtered_required_apps.append(app)

            # Claves requeridas - usar tripleta normalizada: unidad_subunidad, position_role, logical_access_name
            required_keys = {
                self._triplet_key(app.get('unidad_subunidad'), app.get('position_role'), app.get('logical_access_name'))
                for app in filtered_required_apps
            }

            # Índice para detalles usando la misma clave normalizada
            req_index = {
                self._triplet_key(app.get('unidad_subunidad'), app.get('position_role'), app.get('logical_access_name')): app
                for app in filtered_required_apps
            }

            # 4) Historial/actuales: considerar solo registros COMPLETADOS
            # MEJORA: Solo considerar accesos completados como actuales
            # Los accesos pendientes o en proceso aparecerán como "a otorgar"
            current_records = []
            for h in history:
                if (h.get('process_access') in ('onboarding', 'lateral_movement') and 
                    h.get('status') == 'Completado'):
                    hist_unit = h.get('app_unit') or h.get('area', '')
                    hist_position = h.get('app_position_role') or h.get('position', '')
                    hist_name = h.get('app_logical_access_name') or h.get('app_access_name', '')
                    
                    # Considerar todos los registros de onboarding completados, independientemente de la unidad
                    if hist_name:
                        # Si no hay posición en el historial, usar la posición actual
                        if not hist_position:
                            hist_position = emp_position
                        
                        # Agregar el registro con la posición actualizada si es necesario
                        h_updated = h.copy()
                        h_updated['app_position_role'] = hist_position
                        h_updated['app_unit'] = hist_unit
                        h_updated['app_logical_access_name'] = hist_name
                        current_records.append(h_updated)

            # Claves actuales - usar tripleta normalizada: unit, position_role, logical_access_name (ignora subunit)
            # MEJORA: Considerar accesos de todas las unidades, pero normalizar posiciones
            current_keys = set()
            for h in current_records:
                app_unit = h.get('app_unit') or h.get('area', '')
                app_position = h.get('app_position_role') or h.get('position', '')
                app_name = h.get('app_logical_access_name') or h.get('app_access_name', '')
                
                # Si no hay position en el historial, usar la posición actual del empleado
                if not app_position:
                    app_position = emp_position
                
                # MEJORA: Si la posición del historial es diferente a la actual, 
                # usar la posición actual para la comparación (esto evita falsos positivos)
                if app_position != emp_position:
                    app_position = emp_position
                
                # Construir unidad_subunidad para el acceso actual
                app_subunit = h.get('subunit', '')
                if not app_subunit:
                    app_subunit = 'General'
                app_unidad_subunidad = f"{app_unit}/{app_subunit}"
                
                # Considerar todos los accesos usando unidad_subunidad
                if app_position and app_name:
                    current_keys.add(self._triplet_key(app_unidad_subunidad, app_position, app_name))

            # 4) Deltas estrictos por clave completa
            to_grant_keys = required_keys - current_keys
            to_revoke_keys = current_keys - required_keys

            # 5) Construcción de listas detalladas
            to_grant: List[Dict[str, Any]] = []
            for key in to_grant_keys:
                app = req_index.get(key, {})
                to_grant.append({
                    'unidad_subunidad': key[0],
                    'unit': app.get('unit', ''),  # unit del app original
                    'subunit': app.get('subunit', ''),  # subunit del app original
                    'position_role': key[1],
                    'app_name': key[2],
                    'role_name': app.get('role_name', ''),
                    'description': app.get('description', ''),
                })

            to_revoke: List[Dict[str, Any]] = []
            # Para revocar, buscamos el primer record que matchee esa clave para dar contexto (fecha, etc.)
            rec_index = {}
            for h in current_records:
                app_unit = h.get('app_unit') or h.get('area', '')
                app_position = h.get('app_position_role') or h.get('position', '')
                app_name = h.get('app_logical_access_name') or h.get('app_access_name', '')
                
                # Si no hay position en el historial, usar la posición actual del empleado
                if not app_position:
                    app_position = emp_position
                
                # Construir unidad_subunidad para el acceso actual
                app_subunit = h.get('subunit', '')
                if not app_subunit:
                    app_subunit = 'General'
                app_unidad_subunidad = f"{app_unit}/{app_subunit}"
                
                if app_unidad_subunidad and app_position and app_name:
                    key = self._triplet_key(app_unidad_subunidad, app_position, app_name)
                    rec_index[key] = h
            for key in to_revoke_keys:
                h = rec_index.get(key, {})
                to_revoke.append({
                    'unidad_subunidad': key[0],
                    'unit': h.get('app_unit', '') or h.get('area', ''),  # unit del historial
                    'subunit': h.get('app_subunit', '') or h.get('subunit', ''),  # subunit del historial
                    'position_role': key[1],
                    'app_name': key[2],
                    'granted_date': h.get('record_date', ''),
                    'status': h.get('status', ''),
                })

            # 6) Construir lista de actuales deduplicada usando tripleta normalizada
            current_access: List[Dict[str, Any]] = []
            seen_keys = set()
            for h in current_records:
                # Solo agregar si coincide con la unidad_subunidad actual del empleado
                app_unit = h.get('app_unit') or h.get('area', '')
                app_subunit = h.get('subunit', '')
                if not app_subunit:
                    app_subunit = 'General'
                app_unidad_subunidad = f"{app_unit}/{app_subunit}"
                
                if app_unidad_subunidad == emp_unidad_subunidad:
                    app_position = h.get('app_position_role') or h.get('position', '')
                    app_name = h.get('app_logical_access_name') or h.get('app_access_name', '')
                    
                    # Si no hay position en el historial, usar la posición actual del empleado
                    if not app_position:
                        app_position = emp_position
                    
                    if app_unidad_subunidad and app_position and app_name:
                        key = self._triplet_key(app_unidad_subunidad, app_position, app_name)
                        if key not in seen_keys:
                            seen_keys.add(key)
                            current_access.append({
                                'unidad_subunidad': key[0],
                                'unit': h.get('app_unit', '') or h.get('area', ''),  # unit del historial
                                'subunit': h.get('app_subunit', '') or h.get('subunit', ''),  # subunit del historial
                                'position_role': key[1],
                                'app_name': key[2],
                                'granted_date': h.get('record_date'),
                                'status': h.get('status'),
                            })

            return {
                "employee": employee,
                "current_access": current_access,
                "to_grant": to_grant,
                "to_revoke": to_revoke,
                "summary": {
                    "total_current": len(current_access),
                    "total_required": len(required_apps),
                    "to_grant_count": len(to_grant),
                    "to_revoke_count": len(to_revoke)
                }
            }

        except Exception as e:
            return {"error": f"Error generando reporte: {str(e)}"}

    def delete_historical_record(self, scotia_id: str, case_id: str, app_access_name: str = None, delete_all: bool = False) -> bool:
        """Elimina un registro específico o todos los registros de un case_id."""
        try:
            print(f"[DEBUG] delete_historical_record called -> scotia_id={scotia_id}, case_id={case_id}, app_access_name={app_access_name}, delete_all={delete_all}")
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                if delete_all:
                    cursor.execute(
                        "DELETE FROM historico WHERE CAST(scotia_id AS NVARCHAR(50)) = ? AND case_id = ?",
                        (scotia_id, case_id)
                    )
                    print(f"[DEBUG] delete_all affected rows: {cursor.rowcount}")
                elif app_access_name:
                    cursor.execute('SELECT id FROM historico WHERE CAST(scotia_id AS NVARCHAR(50)) = ? AND case_id = ? AND app_access_name = ?', (scotia_id, case_id, app_access_name))
                    
                    if not cursor.fetchone():
                        print("[DEBUG] No matching record found for provided app_access_name")
                        return False
                    
                    # Eliminar solo el registro específico
                    cursor.execute(
                        "DELETE FROM historico WHERE CAST(scotia_id AS NVARCHAR(50)) = ? AND case_id = ? AND app_access_name = ?",
                        (scotia_id, case_id, app_access_name)
                    )
                    print(f"[DEBUG] delete specific rowcount: {cursor.rowcount}")
                else:
                    # Si no se proporciona app_access_name, eliminar solo el primer registro encontrado
                    cursor.execute('SELECT TOP 1 id FROM historico WHERE CAST(scotia_id AS NVARCHAR(50)) = ? AND case_id = ?', (scotia_id, case_id))
                    
                    if not cursor.fetchone():
                        print("[DEBUG] No records found for given scotia_id and case_id")
                        return False
                    
                    # Eliminar solo el primer registro
                    cursor.execute(
                        "DELETE TOP (1) FROM historico WHERE CAST(scotia_id AS NVARCHAR(50)) = ? AND case_id = ?",
                        (scotia_id, case_id)
                    )
                    print(f"[DEBUG] delete first row rowcount: {cursor.rowcount}")
                
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error eliminando registro: {str(e)}")
            return False

    def get_headcount_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del headcount agrupadas por diferentes criterios"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            # 1. Estadísticas por unidad
            cursor.execute('''
                SELECT unit as unidad, COUNT(*) as total_empleados,
                       COUNT(CASE WHEN activo = 1 THEN 1 END) as activos,
                       COUNT(CASE WHEN activo = 0 THEN 1 END) as inactivos,
                       COUNT(CASE WHEN position IS NOT NULL AND position != '' THEN 1 END) as con_posicion,
                       COUNT(CASE WHEN start_date IS NOT NULL AND start_date != '' THEN 1 END) as con_fecha_inicio
                FROM headcount
                WHERE unit IS NOT NULL AND unit != ''
                GROUP BY unit
                ORDER BY total_empleados DESC
            ''')
            stats['por_unidad'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # 2. Estadísticas por puesto
            cursor.execute('''
                SELECT position as puesto, unit as unidad, COUNT(*) as total_empleados,
                       COUNT(CASE WHEN activo = 1 THEN 1 END) as activos,
                       COUNT(CASE WHEN activo = 0 THEN 1 END) as inactivos,
                       COUNT(CASE WHEN start_date IS NOT NULL AND start_date != '' THEN 1 END) as con_fecha_inicio
                FROM headcount
                WHERE position IS NOT NULL AND position != ''
                GROUP BY position, unit
                ORDER BY total_empleados DESC
            ''')
            stats['por_puesto'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # 3. Estadísticas por manager
            cursor.execute('''
                SELECT manager, unit as unidad, COUNT(*) as total_empleados,
                       COUNT(CASE WHEN activo = 1 THEN 1 END) as activos,
                       COUNT(CASE WHEN activo = 0 THEN 1 END) as inactivos
                FROM headcount
                WHERE manager IS NOT NULL AND manager != ''
                GROUP BY manager, unit
                ORDER BY total_empleados DESC
            ''')
            stats['por_manager'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # 4. Estadísticas por senior manager
            cursor.execute('''
                SELECT senior_manager, unit as unidad, COUNT(*) as total_empleados,
                       COUNT(CASE WHEN activo = 1 THEN 1 END) as activos,
                       COUNT(CASE WHEN activo = 0 THEN 1 END) as inactivos
                FROM headcount
                WHERE senior_manager IS NOT NULL AND senior_manager != ''
                GROUP BY senior_manager, unit
                ORDER BY total_empleados DESC
            ''')
            stats['por_senior_manager'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # 5. Estadísticas por estado de activación
            cursor.execute('''
                SELECT 
                    CASE WHEN activo = 1 THEN 'Active' ELSE 'Inactive' END as estado,
                    COUNT(*) as total_empleados,
                    COUNT(CASE WHEN inactivation_date IS NOT NULL THEN 1 END) as con_fecha_inactivacion
                FROM headcount
                GROUP BY activo
                ORDER BY activo DESC
            ''')
            stats['por_estado'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # 6. Estadísticas por año de inicio (si hay fecha de inicio)
            cursor.execute('''
                SELECT 
                    YEAR(start_date) as año_inicio,
                    COUNT(*) as total_empleados,
                    COUNT(CASE WHEN activo = 1 THEN 1 END) as activos,
                    COUNT(CASE WHEN activo = 0 THEN 1 END) as inactivos
                FROM headcount
                WHERE start_date IS NOT NULL
                GROUP BY YEAR(start_date)
                ORDER BY año_inicio DESC
            ''')
            stats['por_año_inicio'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # 7. Resumen detallado por unidad (con lista de empleados)
            cursor.execute('''
                SELECT 
                    unit as unidad,
                    scotia_id,
                    full_name,
                    position as puesto,
                    manager,
                    senior_manager,
                    CASE WHEN activo = 1 THEN 'Active' ELSE 'Inactive' END as estado,
                    start_date,
                    inactivation_date
                FROM headcount
                WHERE unit IS NOT NULL AND unit != ''
                ORDER BY unit, full_name
            ''')
            stats['detalle_por_unidad'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # 8. Estadísticas generales
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_empleados,
                    COUNT(CASE WHEN activo = 1 THEN 1 END) as activos,
                    COUNT(CASE WHEN activo = 0 THEN 1 END) as inactivos,
                    COUNT(CASE WHEN position IS NOT NULL AND position != '' THEN 1 END) as con_posicion,
                    COUNT(CASE WHEN start_date IS NOT NULL AND start_date != '' THEN 1 END) as con_fecha_inicio,
                    COUNT(CASE WHEN manager IS NOT NULL AND manager != '' THEN 1 END) as con_manager,
                    COUNT(CASE WHEN senior_manager IS NOT NULL AND senior_manager != '' THEN 1 END) as con_senior_manager,
                    COUNT(CASE WHEN inactivation_date IS NOT NULL THEN 1 END) as con_fecha_inactivacion
                FROM headcount
            ''')
            stats['generales'] = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
            
            conn.close()
            return stats
            
        except Exception as e:
            return {"error": f"Error obteniendo estadísticas del headcount: {str(e)}"}

    def get_available_applications(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de aplicaciones disponibles para registros manuales"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener aplicaciones únicas del historial y de la tabla applications
            cursor.execute('''
                SELECT DISTINCT app_access_name as application_name
                FROM historico 
                WHERE app_access_name IS NOT NULL AND app_access_name != ''
                UNION
                SELECT DISTINCT logical_access_name as application_name
                FROM applications 
                WHERE logical_access_name IS NOT NULL AND logical_access_name != ''
                ORDER BY application_name
            ''')
            
            applications = [{'name': row[0]} for row in cursor.fetchall()]
            conn.close()
            
            return applications
            
        except Exception as e:
            return []
    
    def get_available_positions(self) -> List[str]:
        """Obtiene todas las posiciones disponibles"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT position_role
                FROM applications 
                WHERE access_status = 'Active' AND position_role IS NOT NULL
                ORDER BY position_role
            ''')
            
            positions = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return positions
            
        except Exception as e:
            print(f"Error obteniendo posiciones disponibles: {e}")
            return []
    
    def get_applications_by_position_simple(self, position: str) -> List[Dict[str, Any]]:
        """Obtiene aplicaciones filtradas por posición (versión simple)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT logical_access_name, description, role_name, unit, subunit
                FROM applications 
                WHERE access_status = 'Active' 
                AND position_role = ?
                ORDER BY logical_access_name
            ''', (position,))
            
            applications = []
            for row in cursor.fetchall():
                applications.append({
                    'logical_access_name': row[0],
                    'description': row[1] or '',
                    'role_name': row[2] or '',
                    'unit': row[3] or '',
                    'subunit': row[4] or ''
                })
            
            conn.close()
            return applications
            
        except Exception as e:
            print(f"Error obteniendo aplicaciones por posición: {e}")
            return []

    def get_historial_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del historial agrupadas por diferentes criterios"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            # 1. Estadísticas por unidad
            cursor.execute('''
                SELECT h.area as unidad, COUNT(*) as total_registros,
                       COUNT(CASE WHEN h.status = 'Completado' THEN 1 END) as completados,
                       COUNT(CASE WHEN h.status = 'Pendiente' THEN 1 END) as pendientes,
                       COUNT(CASE WHEN h.status = 'En Proceso' THEN 1 END) as en_proceso,
                       COUNT(CASE WHEN h.status = 'Cancelado' THEN 1 END) as cancelados,
                       COUNT(CASE WHEN h.status = 'Rechazado' THEN 1 END) as rechazados
                FROM historico h
                WHERE h.area IS NOT NULL AND h.area != ''
                GROUP BY h.area
                ORDER BY total_registros DESC
            ''')
            stats['por_unidad'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # 2. Estadísticas por subunidad
            cursor.execute('''
                SELECT h.subunit as subunidad, h.area as unidad, COUNT(*) as total_registros,
                       COUNT(CASE WHEN h.status = 'Completado' THEN 1 END) as completados,
                       COUNT(CASE WHEN h.status = 'Pendiente' THEN 1 END) as pendientes,
                       COUNT(CASE WHEN h.status = 'En Proceso' THEN 1 END) as en_proceso,
                       COUNT(CASE WHEN h.status = 'Cancelado' THEN 1 END) as cancelados,
                       COUNT(CASE WHEN h.status = 'Rechazado' THEN 1 END) as rechazados
                FROM historico h
                WHERE h.subunit IS NOT NULL AND h.subunit != ''
                GROUP BY h.subunit, h.area
                ORDER BY total_registros DESC
            ''')
            stats['por_subunidad'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # 3. Estadísticas por puesto
            cursor.execute('''
                SELECT head.position as puesto, head.unit as unidad, COUNT(*) as total_registros,
                       COUNT(CASE WHEN h.status = 'Completado' THEN 1 END) as completados,
                       COUNT(CASE WHEN h.status = 'Pendiente' THEN 1 END) as pendientes,
                       COUNT(CASE WHEN h.status = 'En Proceso' THEN 1 END) as en_proceso,
                       COUNT(CASE WHEN h.status = 'Cancelado' THEN 1 END) as cancelados,
                       COUNT(CASE WHEN h.status = 'Rechazado' THEN 1 END) as rechazados
                FROM historico h
                INNER JOIN headcount head ON h.scotia_id = head.scotia_id
                WHERE head.position IS NOT NULL AND head.position != ''
                GROUP BY head.position, head.unit
                ORDER BY total_registros DESC
            ''')
            stats['por_puesto'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # 4. Estadísticas por aplicación
            cursor.execute('''
                SELECT h.app_access_name as aplicacion, COUNT(*) as total_registros,
                       COUNT(CASE WHEN h.status = 'Completado' THEN 1 END) as completados,
                       COUNT(CASE WHEN h.status = 'Pendiente' THEN 1 END) as pendientes,
                       COUNT(CASE WHEN h.status = 'En Proceso' THEN 1 END) as en_proceso,
                       COUNT(CASE WHEN h.status = 'Cancelado' THEN 1 END) as cancelados,
                       COUNT(CASE WHEN h.status = 'Rechazado' THEN 1 END) as rechazados
                FROM historico h
                WHERE h.app_access_name IS NOT NULL AND h.app_access_name != ''
                GROUP BY h.app_access_name
                ORDER BY total_registros DESC
            ''')
            stats['por_aplicacion'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # 5. Estadísticas por proceso
            cursor.execute('''
                SELECT h.process_access as proceso, COUNT(*) as total_registros,
                       COUNT(CASE WHEN h.status = 'Completado' THEN 1 END) as completados,
                       COUNT(CASE WHEN h.status = 'Pendiente' THEN 1 END) as pendientes,
                       COUNT(CASE WHEN h.status = 'En Proceso' THEN 1 END) as en_proceso,
                       COUNT(CASE WHEN h.status = 'Cancelado' THEN 1 END) as cancelados,
                       COUNT(CASE WHEN h.status = 'Rechazado' THEN 1 END) as rechazados
                FROM historico h
                WHERE h.process_access IS NOT NULL AND h.process_access != ''
                GROUP BY h.process_access
                ORDER BY total_registros DESC
            ''')
            stats['por_proceso'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # 6. Estadísticas generales
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_registros,
                    COUNT(CASE WHEN h.status = 'Completado' THEN 1 END) as completados,
                    COUNT(CASE WHEN h.status = 'Pendiente' THEN 1 END) as pendientes,
                    COUNT(CASE WHEN h.status = 'En Proceso' THEN 1 END) as en_proceso,
                    COUNT(CASE WHEN h.status = 'Cancelado' THEN 1 END) as cancelados,
                    COUNT(CASE WHEN h.status = 'Rechazado' THEN 1 END) as rechazados
                FROM historico h
            ''')
            stats['generales'] = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
            
            conn.close()
            return stats
            
        except Exception as e:
            return {"error": f"Error obteniendo estadísticas: {str(e)}"}

    def buscar_procesos(self, filtros: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Busca procesos en el historial con filtros opcionales.
        
        Args:
            filtros: Diccionario con filtros de búsqueda
            
        Returns:
            Lista de registros del historial que coinciden con los filtros
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Query base
            query = '''
                SELECT h.*, a.logical_access_name, a.description as app_description
                FROM historico h
                LEFT JOIN (
                    SELECT 
                        logical_access_name,
                        description,
                        ROW_NUMBER() OVER (PARTITION BY logical_access_name ORDER BY id) as rn
                    FROM applications
                ) a ON h.app_access_name = a.logical_access_name AND a.rn = 1
            '''
            
            # Construir WHERE clause basado en filtros
            where_conditions = []
            params = []
            
            if filtros:
                for campo, valor in filtros.items():
                    if valor and valor.strip():
                        if campo == 'numero_caso':
                            where_conditions.append("h.case_id LIKE ?")
                            params.append(f"%{valor}%")
                        elif campo == 'sid':
                            where_conditions.append("h.scotia_id LIKE ?")
                            params.append(f"%{valor}%")
                        elif campo == 'proceso':
                            where_conditions.append("h.process_access LIKE ?")
                            params.append(f"%{valor}%")
                        elif campo == 'aplicacion':
                            where_conditions.append("h.app_access_name LIKE ?")
                            params.append(f"%{valor}%")
                        elif campo == 'estado':
                            where_conditions.append("h.status LIKE ?")
                            params.append(f"%{valor}%")
                        elif campo == 'fecha':
                            where_conditions.append("h.record_date LIKE ?")
                            params.append(f"%{valor}%")
                        elif campo == 'responsable':
                            where_conditions.append("h.responsible LIKE ?")
                            params.append(f"%{valor}%")
                        elif campo == 'descripcion':
                            where_conditions.append("h.event_description LIKE ?")
                            params.append(f"%{valor}%")
            
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)
            
            query += " ORDER BY h.record_date DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            # Convertir a diccionarios
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            print(f"Error en buscar_procesos: {e}")
            return []

    def assign_accesses(self, scotia_id: str, responsable: str = "Sistema") -> Tuple[bool, str, Dict[str, int]]:
        """
        Asigna accesos automáticamente según la unit y position del empleado.
        
        Args:
            scotia_id: ID del empleado
            responsable: Responsable del proceso (default: "Sistema")
            
        Returns:
            Tuple[bool, str, Dict[str, int]]: (success, message, counts)
            counts contiene: {'granted': int, 'revoked': int}
        """
        try:
            # Verificar que el empleado existe
            employee = self.get_employee_by_id(scotia_id)
            if not employee:
                return False, f"Empleado {scotia_id} no encontrado", {'granted': 0, 'revoked': 0}
            
            # Verificar si ya hay registros pendientes para este empleado
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM historico WHERE scotia_id = ? AND status = \'Pendiente\'', (scotia_id,))
            existing_pending = cursor.fetchone()[0]
            
            if existing_pending > 0:
                conn.close()
                return False, f"Ya existen {existing_pending} registros pendientes para {scotia_id}. Complete los procesos pendientes antes de crear nuevos.", {'granted': 0, 'revoked': 0}
            
            # Obtener reporte de conciliación usando el procedimiento almacenado
            reconciliation_report = self.get_access_reconciliation_report(scotia_id)
            
            if not reconciliation_report.get('success', False):
                return False, reconciliation_report.get('message', 'Error obteniendo reporte de conciliación'), {'granted': 0, 'revoked': 0}
            
            data = reconciliation_report.get('data', {})
            to_grant = data.get('to_grant', [])
            to_revoke = data.get('to_revoke', [])
            
            # Contadores
            granted_count = 0
            revoked_count = 0
            
            # Generar un solo case_id para todo el proceso
            case_id = f"CASE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{scotia_id}"
            
            # Procesar accesos por otorgar
            for access_data in to_grant:
                app_name = access_data.get('app_name', '')
                if app_name:
                    # Crear registro histórico para otorgamiento
                    record_data = {
                        'scotia_id': scotia_id,
                        'case_id': case_id,
                        'responsible': responsable,
                        'process_access': 'onboarding',
                        'sid': scotia_id,
                        'area': access_data.get('unit', ''),
                        'subunit': access_data.get('subunit', ''),
                        'event_description': f"Otorgamiento automático de acceso para {app_name}",
                        'ticket_email': f"{responsable}@empresa.com",  # No hay app data disponible aquí
                        'app_access_name': app_name,
                        'computer_system_type': 'Desktop',
                        'status': 'Pendiente',
                        'general_status_ticket': 'En Proceso'
                    }
                    
                    success, message = self.create_historical_record(record_data)
                    if success:
                        granted_count += 1
                    else:
                        print(f"Error creando registro de otorgamiento: {message}")
            
            # Procesar accesos por revocar
            for access_data in to_revoke:
                app_name = access_data.get('app_name', '')
                if app_name:
                    # Crear registro histórico para revocación
                    record_data = {
                        'scotia_id': scotia_id,
                        'case_id': case_id,
                        'responsible': responsable,
                        'process_access': 'offboarding',
                        'sid': scotia_id,
                        'area': access_data.get('unit', ''),
                        'subunit': access_data.get('subunit', ''),
                        'event_description': f"Revocación automática de acceso para {app_name}",
                        'ticket_email': f"{responsable}@empresa.com",  # No hay app data disponible aquí
                        'app_access_name': app_name,
                        'computer_system_type': 'Desktop',
                        'status': 'Pendiente',
                        'general_status_ticket': 'En Proceso'
                    }
                    
                    success, message = self.create_historical_record(record_data)
                    if success:
                        revoked_count += 1
                    else:
                        print(f"Error creando registro de revocación: {message}")
            
            conn.close()
            
            counts = {'granted': granted_count, 'revoked': revoked_count}
            message = f"Proceso completado. Otorgados: {granted_count}, Revocados: {revoked_count}"
            
            return True, message, counts
            
        except Exception as e:
            return False, f"Error en assign_accesses: {str(e)}", {'granted': 0, 'revoked': 0}

    def get_access_reconciliation_report(self, scotia_id: str) -> Dict[str, Any]:
        """Obtiene el reporte de conciliación de accesos para un empleado usando procedimiento almacenado"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Ejecutar procedimiento almacenado
            cursor.execute("EXEC sp_GetAccessReconciliationReport ?", (scotia_id,))
            results = cursor.fetchall()
            
            if not results:
                return {
                    'success': False,
                    'message': f'No se encontraron datos para el empleado {scotia_id}',
                    'data': {}
                }
            
            # Verificar si hay error
            first_row = results[0]
            if len(first_row) >= 2 and first_row[0] == 'error':
                return {
                    'success': False,
                    'message': first_row[1],
                    'data': {}
                }
            
            # Procesar resultados
            current_access = []
            to_grant = []
            to_revoke = []
            
            for row in results:
                access_type = row[0]
                app_name = row[1]
                unit = row[2]
                subunit = row[3]
                position_role = row[4]
                role_name = row[5]
                description = row[6]
                record_date = row[7]
                status = row[8]
                
                access_data = {
                    'app_name': app_name,
                    'unit': unit,
                    'subunit': subunit,
                    'position_role': position_role,
                    'role_name': role_name,
                    'description': description,
                    'status': status
                }
                
                if access_type == 'current':
                    access_data['date'] = record_date
                    current_access.append(access_data)
                elif access_type == 'to_grant':
                    to_grant.append(access_data)
                elif access_type == 'to_revoke':
                    access_data['date'] = record_date
                    to_revoke.append(access_data)
            
            # Obtener información del empleado
            employee = self.get_employee_by_id(scotia_id)
            
            conn.close()
            
            return {
                'success': True,
                'message': f'Reporte de conciliación generado para {scotia_id}',
                'data': {
                    'employee': employee,
                    'current_access': current_access,
                    'to_grant': to_grant,
                    'to_revoke': to_revoke,
                    'summary': {
                        'current_count': len(current_access),
                        'to_grant_count': len(to_grant),
                        'to_revoke_count': len(to_revoke),
                        'final_count': len(current_access) + len(to_grant) - len(to_revoke)
                    }
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error generando reporte de conciliación: {str(e)}',
                'data': {}
            }

    def revoke_specific_access(self, scotia_id: str, app_name: str, access_type: str, responsible: str = "Sistema") -> Dict[str, Any]:
        """
        Revoca un acceso específico (flex staff o manual) de un empleado
        
        Args:
            scotia_id: ID del empleado
            app_name: Nombre de la aplicación
            access_type: Tipo de acceso ('flex_staff' o 'manual_access')
            responsible: Persona responsable de la revocación
            
        Returns:
            Dict con el resultado de la operación
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar que el acceso existe y es del tipo correcto
            print(f"DEBUG: Buscando acceso {access_type} para {app_name} del empleado {scotia_id}")
            cursor.execute('''
                SELECT h.id, h.app_access_name, h.process_access, h.event_description, h.status
                FROM historico h
                WHERE h.scotia_id = ? 
                AND h.app_access_name = ?
                AND h.process_access = ?
                AND h.status IN ('to validate', 'closed completed', 'in progress', 'in validation')
                ORDER BY h.record_date DESC
            ''', (scotia_id, app_name, access_type))
            
            access_record = cursor.fetchone()
            
            if not access_record:
                print(f"DEBUG: No se encontró acceso {access_type} con status 'Pendiente'. Verificando otros estados...")
                # Buscar con otros estados
                cursor.execute('''
                    SELECT h.id, h.app_access_name, h.process_access, h.event_description, h.status
                    FROM historico h
                    WHERE h.scotia_id = ? 
                    AND h.app_access_name = ?
                    AND h.process_access = ?
                    ORDER BY h.record_date DESC
                ''', (scotia_id, app_name, access_type))
                
                all_records = cursor.fetchall()
                print(f"DEBUG: Registros encontrados para {app_name} con {access_type}: {len(all_records)}")
                for record in all_records:
                    print(f"DEBUG: - ID: {record[0]}, App: {record[1]}, Process: {record[2]}, Status: {record[4]}")
                
                return {
                    'success': False,
                    'message': f'No se encontró acceso {access_type} activo para {app_name}'
                }
            
            # Crear registro de revocación en el historial
            case_id = f"REVOKE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{scotia_id}"
            event_description = f"Revocación de acceso {access_type} para {app_name}"
            
            cursor.execute('''
                INSERT INTO historico (
                    scotia_id, employee_email, case_id, responsible, record_date, request_date,
                    process_access, subunit, event_description,
                    ticket_email, app_access_name, computer_system_type, duration_of_access, status,
                    closing_date_app, closing_date_ticket, app_quality,
                    confirmation_by_user, comment, comment_tq, ticket_quality, general_status_ticket,
                    general_status_case, average_time_open_ticket, sla_app, sla_ticket, sla_case
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                scotia_id, scotia_id, case_id, responsible, datetime.now(), None,
                'offboarding', 'N/A', event_description,
                f'{responsible}@empresa.com', app_name, 'Desktop', None, 'Pendiente',
                None, None, None, None, f'Revocación de acceso {access_type} por {responsible}', 
                None, 'En Proceso', None, None, None, None, None, None
            ))
            
            # Marcar el acceso original como revocado
            cursor.execute('''
                UPDATE historico 
                SET status = 'Revocado', 
                    closing_date_app = ?,
                    comment = COALESCE(comment, '') + ' | Revocado por ' + ?
                WHERE id = ?
            ''', (datetime.now(), responsible, access_record[0]))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': f'Acceso {access_type} para {app_name} revocado exitosamente',
                'case_id': case_id
            }
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return {
                'success': False,
                'message': f'Error revocando acceso: {str(e)}'
            }

    def get_revocable_accesses(self, scotia_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene los accesos que pueden ser revocados (flex staff y manuales)
        
        Args:
            scotia_id: ID del empleado
            
        Returns:
            Lista de accesos revocables
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT 
                    h.app_access_name,
                    h.process_access,
                    h.event_description,
                    h.record_date,
                    h.responsible,
                    h.case_id
                FROM historico h
                WHERE h.scotia_id = ? 
                AND h.process_access IN ('flex_staff', 'manual_access')
                AND h.status = 'Pendiente'
                ORDER BY h.record_date DESC
            ''', (scotia_id,))
            
            accesses = []
            for row in cursor.fetchall():
                accesses.append({
                    'app_name': row[0],
                    'access_type': row[1],
                    'description': row[2],
                    'record_date': row[3],
                    'responsible': row[4],
                    'case_id': row[5]
                })
            
            conn.close()
            return accesses
            
        except Exception as e:
            print(f"Error obteniendo accesos revocables: {e}")
            return []


# Instancia global del servicio
access_service = AccessManagementService()

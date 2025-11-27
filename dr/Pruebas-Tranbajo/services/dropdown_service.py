"""
Servicio para obtener valores únicos de la base de datos para dropdowns
"""
from services.access_management_service import access_service
import pyodbc
from typing import List, Dict, Any

class DropdownService:
    """Servicio para obtener valores únicos de la base de datos"""
    
    def __init__(self):
        self.access_service = access_service
    
    def get_connection(self) -> pyodbc.Connection:
        """Obtiene una conexión a la base de datos"""
        return self.access_service.get_connection()
    
    def get_unique_units(self) -> List[str]:
        """Obtiene las unidades únicas de la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT unit 
                FROM applications 
                WHERE unit IS NOT NULL AND unit != ''
                ORDER BY unit
            """)
            
            units = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return units
            
        except Exception as e:
            print(f"Error obteniendo unidades: {e}")
            return []
    
    def get_unique_subunits(self) -> List[str]:
        """Obtiene las subunidades únicas de la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT service 
                FROM applications 
                WHERE service IS NOT NULL AND service != ''
                ORDER BY service
            """)
            
            subunits = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return subunits
            
        except Exception as e:
            print(f"Error obteniendo subunidades: {e}")
            return []
    
    def get_unique_positions(self) -> List[str]:
        """Obtiene las posiciones únicas de la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT role 
                FROM applications 
                WHERE role IS NOT NULL AND role != ''
                ORDER BY role
            """)
            
            positions = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return positions
            
        except Exception as e:
            print(f"Error obteniendo posiciones: {e}")
            return []
    
    def get_unique_roles(self) -> List[str]:
        """Obtiene los roles únicos de la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT roles_and_profiles 
                FROM applications 
                WHERE roles_and_profiles IS NOT NULL AND roles_and_profiles != ''
                ORDER BY roles_and_profiles
            """)
            
            roles = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return roles
            
        except Exception as e:
            print(f"Error obteniendo roles: {e}")
            return []
    
    def get_unique_jurisdictions(self) -> List[str]:
        """Obtiene las jurisdicciones únicas de la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT system_jurisdiction 
                FROM applications 
                WHERE system_jurisdiction IS NOT NULL AND system_jurisdiction != ''
                ORDER BY system_jurisdiction
            """)
            
            jurisdictions = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return jurisdictions
            
        except Exception as e:
            print(f"Error obteniendo jurisdicciones: {e}")
            return []
    
    def get_unique_system_owners(self) -> List[str]:
        """Obtiene los propietarios de sistema únicos de la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT application_owner 
                FROM applications 
                WHERE application_owner IS NOT NULL AND application_owner != ''
                ORDER BY application_owner
            """)
            
            owners = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return owners
            
        except Exception as e:
            print(f"Error obteniendo propietarios: {e}")
            return []
    
    def get_unique_categories(self) -> List[str]:
        """Obtiene las categorías únicas de la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT critical_non_critical 
                FROM applications 
                WHERE critical_non_critical IS NOT NULL AND critical_non_critical != ''
                ORDER BY critical_non_critical
            """)
            
            categories = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return categories
            
        except Exception as e:
            print(f"Error obteniendo categorías: {e}")
            return []
    
    def get_unique_access_types(self) -> List[str]:
        """Obtiene los tipos de acceso únicos de la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT type_of_element 
                FROM applications 
                WHERE type_of_element IS NOT NULL AND type_of_element != ''
                ORDER BY type_of_element
            """)
            
            access_types = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return access_types
            
        except Exception as e:
            print(f"Error obteniendo tipos de acceso: {e}")
            return []
    
    def get_unique_access_statuses(self) -> List[str]:
        """Obtiene los estados de acceso únicos de la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT status 
                FROM applications 
                WHERE status IS NOT NULL AND status != ''
                ORDER BY status
            """)
            
            statuses = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return statuses
            
        except Exception as e:
            print(f"Error obteniendo estados: {e}")
            return []
    
    def get_unique_authentication_methods(self) -> List[str]:
        """Obtiene los métodos de autenticación únicos de la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT log_in_information 
                FROM applications 
                WHERE log_in_information IS NOT NULL AND log_in_information != ''
                ORDER BY log_in_information
            """)
            
            methods = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return methods
            
        except Exception as e:
            print(f"Error obteniendo métodos de autenticación: {e}")
            return []
    
    def get_unique_unidad_subunidad(self) -> List[str]:
        """Obtiene las unidades/subunidades únicas de la base de datos (solo de applications)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Solo obtener de la tabla applications (que tiene las aplicaciones reales)
            cursor.execute("""
                SELECT DISTINCT 
                    CONCAT(
                        ISNULL(unit, ''),
                        CASE 
                            WHEN unit IS NOT NULL AND service IS NOT NULL THEN ' / ' 
                            ELSE '' 
                        END,
                        ISNULL(service, '')
                    ) AS unidad_subunidad
                FROM applications 
                WHERE (unit IS NOT NULL AND unit != '') OR (service IS NOT NULL AND service != '')
                ORDER BY unidad_subunidad
            """)
            
            apps_unidad_subunidad = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            # Si no hay datos en la base de datos, usar valores por defecto
            if not apps_unidad_subunidad:
                apps_unidad_subunidad = ["Tecnología/Desarrollo", "Tecnología/QA", "Tecnología/Infraestructura", 
                                       "Recursos Humanos/RRHH", "Finanzas/Contabilidad", "Marketing/Ventas", 
                                       "Operaciones/Logística", "Legal/Compliance"]
            
            return apps_unidad_subunidad
            
        except Exception as e:
            print(f"Error obteniendo unidades/subunidades: {e}")
            # En caso de error, devolver valores por defecto
            return ["Tecnología/Desarrollo", "Tecnología/QA", "Tecnología/Infraestructura", 
                   "Recursos Humanos/RRHH", "Finanzas/Contabilidad", "Marketing/Ventas", 
                   "Operaciones/Logística", "Legal/Compliance"]
    
    def get_all_dropdown_values(self) -> Dict[str, List[str]]:
        """Obtiene todos los valores únicos para los dropdowns"""
        return {
            'units': self.get_unique_units(),
            'subunits': self.get_unique_subunits(),
            'unidad_subunidad': self.get_unique_unidad_subunidad(),
            'positions': self.get_unique_positions(),
            'roles': self.get_unique_roles(),
            'jurisdictions': self.get_unique_jurisdictions(),
            'system_owners': self.get_unique_system_owners(),
            'categories': self.get_unique_categories(),
            'access_types': self.get_unique_access_types(),
            'access_statuses': self.get_unique_access_statuses(),
            'authentication_methods': self.get_unique_authentication_methods()
        }

# Instancia global del servicio
dropdown_service = DropdownService()

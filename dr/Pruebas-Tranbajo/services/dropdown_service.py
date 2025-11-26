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
                SELECT DISTINCT subunit 
                FROM applications 
                WHERE subunit IS NOT NULL AND subunit != ''
                ORDER BY subunit
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
                SELECT DISTINCT position_role 
                FROM applications 
                WHERE position_role IS NOT NULL AND position_role != ''
                ORDER BY position_role
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
                SELECT DISTINCT role_name 
                FROM applications 
                WHERE role_name IS NOT NULL AND role_name != ''
                ORDER BY role_name
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
                SELECT DISTINCT jurisdiction 
                FROM applications 
                WHERE jurisdiction IS NOT NULL AND jurisdiction != ''
                ORDER BY jurisdiction
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
                SELECT DISTINCT system_owner 
                FROM applications 
                WHERE system_owner IS NOT NULL AND system_owner != ''
                ORDER BY system_owner
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
                SELECT DISTINCT category 
                FROM applications 
                WHERE category IS NOT NULL AND category != ''
                ORDER BY category
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
                SELECT DISTINCT access_type 
                FROM applications 
                WHERE access_type IS NOT NULL AND access_type != ''
                ORDER BY access_type
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
                SELECT DISTINCT access_status 
                FROM applications 
                WHERE access_status IS NOT NULL AND access_status != ''
                ORDER BY access_status
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
                SELECT DISTINCT authentication_method 
                FROM applications 
                WHERE authentication_method IS NOT NULL AND authentication_method != ''
                ORDER BY authentication_method
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
                SELECT DISTINCT unidad_subunidad 
                FROM applications 
                WHERE unidad_subunidad IS NOT NULL AND unidad_subunidad != ''
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

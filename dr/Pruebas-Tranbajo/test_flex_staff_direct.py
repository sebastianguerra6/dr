"""
Script de prueba directo para verificar la lógica de Flex Staff
Accede directamente a la base de datos sin importar servicios complejos
"""

import sys
import os
import sqlite3
from pathlib import Path

# Buscar la base de datos
db_paths = [
    "gamlo_access_management.db",
    "database/gamlo_access_management.db",
    "../gamlo_access_management.db"
]

db_path = None
for path in db_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print("❌ No se encontró la base de datos")
    print("Buscando en:", db_paths)
    sys.exit(1)

print(f"✅ Base de datos encontrada: {db_path}\n")

def get_employee_by_id(conn, scotia_id):
    """Obtiene un empleado por su SID"""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT scotia_id, full_name, position, unit, unidad_subunidad, activo
        FROM headcount
        WHERE scotia_id = ?
    ''', (scotia_id,))
    row = cursor.fetchone()
    if row:
        return {
            'scotia_id': row[0],
            'full_name': row[1],
            'position': row[2],
            'unit': row[3],
            'unidad_subunidad': row[4],
            'activo': row[5]
        }
    return None

def get_current_access(conn, scotia_id):
    """Obtiene accesos actuales del empleado"""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT
            h.app_access_name as logical_access_name,
            h.process_access,
            h.status
        FROM historico h
        WHERE h.scotia_id = ?
        AND h.status = 'closed completed'
        AND h.process_access IN ('onboarding', 'lateral_movement')
        AND h.app_access_name IS NOT NULL
        ORDER BY h.app_access_name
    ''', (scotia_id,))
    
    rows = cursor.fetchall()
    return [{'logical_access_name': r[0], 'process_access': r[1], 'status': r[2]} for r in rows]

def get_flex_staff_access(conn, scotia_id):
    """Obtiene todos los accesos flex_staff del empleado"""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT
            h.app_access_name as logical_access_name,
            h.status
        FROM historico h
        WHERE h.scotia_id = ?
        AND h.process_access = 'flex_staff'
        AND h.app_access_name IS NOT NULL
        ORDER BY h.app_access_name
    ''', (scotia_id,))
    
    rows = cursor.fetchall()
    return [{'logical_access_name': r[0], 'status': r[1]} for r in rows]

def get_applications_by_position(conn, position, unit):
    """Obtiene aplicaciones por posición y unidad"""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT logical_access_name, unit, subunit, position_role, unidad_subunidad
        FROM applications
        WHERE UPPER(LTRIM(RTRIM(position_role))) = UPPER(LTRIM(RTRIM(?)))
        AND UPPER(LTRIM(RTRIM(unidad_subunidad))) LIKE UPPER(LTRIM(RTRIM(?)))
        AND access_status = 'Active'
        ORDER BY logical_access_name
    ''', (position, f'%{unit}%'))
    
    rows = cursor.fetchall()
    return [{
        'logical_access_name': r[0],
        'unit': r[1],
        'subunit': r[2],
        'position_role': r[3],
        'unidad_subunidad': r[4]
    } for r in rows]

def test_flex_staff_logic(scotia_id: str, temporary_position: str, temporary_unit: str):
    """Prueba la lógica de flex staff"""
    print("=" * 80)
    print("PRUEBA DE LÓGICA DE FLEX STAFF")
    print("=" * 80)
    print(f"\nEmpleado: {scotia_id}")
    print(f"Posición temporal: {temporary_position}")
    print(f"Unidad temporal: {temporary_unit}\n")
    
    conn = sqlite3.connect(db_path)
    
    try:
        # 1. Verificar que el empleado existe
        employee = get_employee_by_id(conn, scotia_id)
        if not employee:
            print(f"❌ ERROR: Empleado {scotia_id} no encontrado")
            return False
        
        print(f"✅ Empleado encontrado: {employee.get('full_name', 'N/A')}")
        print(f"   Posición original: {employee.get('position', 'N/A')}")
        print(f"   Unidad original: {employee.get('unit', 'N/A')}")
        print(f"   Active: {'Sí' if employee.get('activo') else 'No'}\n")
        
        # 2. Obtener accesos actuales
        print("📋 PASO 1: Obteniendo accesos actuales del empleado...")
        current_access = get_current_access(conn, scotia_id)
        print(f"   Accesos actuales encontrados: {len(current_access)}")
        
        current_apps_by_name = {}
        for acc in current_access:
            app_name = (acc.get('logical_access_name') or '').strip().upper()
            if app_name:
                current_apps_by_name[app_name] = acc
                print(f"   - {app_name} (tipo: {acc.get('process_access', 'N/A')})")
        
        print(f"\n   Total de accesos únicos: {len(current_apps_by_name)}\n")
        
        # 3. Obtener accesos flex_staff existentes
        print("📋 PASO 2: Obteniendo accesos flex_staff existentes...")
        flex_staff_access = get_flex_staff_access(conn, scotia_id)
        print(f"   Accesos flex_staff existentes: {len(flex_staff_access)}")
        
        for acc in flex_staff_access:
            app_name = (acc.get('logical_access_name') or '').strip().upper()
            if app_name:
                print(f"   - {app_name} (estado: {acc.get('status', 'N/A')})")
        print()
        
        # 4. Agregar accesos flex_staff a la comparación
        print("📋 PASO 3: Agregando accesos flex_staff a la comparación...")
        for acc in flex_staff_access:
            app_name = (acc.get('logical_access_name') or '').strip().upper()
            if app_name and app_name not in current_apps_by_name:
                current_apps_by_name[app_name] = acc
                print(f"   ✅ Agregado a comparación: {app_name}")
        print(f"   Total de accesos para comparar (incluyendo flex_staff): {len(current_apps_by_name)}\n")
        
        # 5. Obtener aplicaciones de la posición temporal
        print("📋 PASO 4: Obteniendo aplicaciones de la posición temporal...")
        temp_apps = get_applications_by_position(conn, temporary_position, temporary_unit)
        print(f"   Aplicaciones encontradas para posición temporal: {len(temp_apps)}")
        
        temp_apps_by_name = {}
        for app in temp_apps:
            app_name = (app.get('logical_access_name') or '').strip().upper()
            if app_name:
                temp_apps_by_name[app_name] = app
                print(f"   - {app_name}")
        
        print(f"\n   Total de aplicaciones únicas: {len(temp_apps_by_name)}\n")
        
        # 6. Calcular qué accesos se otorgarían
        print("📋 PASO 5: Calculando accesos a otorgar (solo los que NO tiene)...")
        to_grant_temp = []
        already_has = []
        
        for app_name, app in temp_apps_by_name.items():
            if app_name not in current_apps_by_name:
                to_grant_temp.append(app)
                print(f"   ✅ OTORGAR: {app_name}")
            else:
                already_has.append(app_name)
                print(f"   ⏭️  YA TIENE: {app_name} (no se creará registro histórico)")
        
        print(f"\n   Resumen:")
        print(f"   - Accesos a otorgar: {len(to_grant_temp)}")
        print(f"   - Accesos que ya tiene: {len(already_has)}")
        print(f"   - Accesos originales mantenidos: {len(current_access)}\n")
        
        # 7. Resumen final
        print("=" * 80)
        print("RESUMEN DE LA PRUEBA")
        print("=" * 80)
        print(f"✅ Empleado existe: {employee.get('full_name', 'N/A')}")
        print(f"✅ Accesos actuales (onboarding/lateral): {len(current_access)}")
        print(f"✅ Accesos flex_staff existentes: {len(flex_staff_access)}")
        print(f"✅ Aplicaciones de posición temporal: {len(temp_apps_by_name)}")
        print(f"✅ Accesos a otorgar: {len(to_grant_temp)}")
        print(f"✅ Accesos que ya tiene (no duplicados): {len(already_has)}")
        print("=" * 80)
        
        return True
        
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python test_flex_staff_direct.py <SID> <posicion_temporal> <unidad_temporal>")
        print("\nEjemplo:")
        print("  python test_flex_staff_direct.py 12345 ANALISTA SENIOR TECNOLOGÍA")
        print("\nBuscando empleados disponibles...\n")
        
        # Intentar obtener un empleado de prueba
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT scotia_id, full_name, position, unit FROM headcount WHERE activo = 1 LIMIT 3')
            rows = cursor.fetchall()
            conn.close()
            
            if rows:
                print("Empleados disponibles para prueba:")
                for row in rows:
                    print(f"  SID: {row[0]}, Nombre: {row[1]}, Posición: {row[2]}, Unidad: {row[3]}")
                
                if rows:
                    sid, name, pos, unit = rows[0]
                    print(f"\n🔍 Ejecutando prueba con el primer empleado: {name} (SID: {sid})")
                    print(f"   Posición temporal: {pos or 'ANALISTA SENIOR'}, Unidad: {unit or 'TECNOLOGÍA'}\n")
                    test_flex_staff_logic(sid, pos or "ANALISTA SENIOR", unit or "TECNOLOGÍA")
            else:
                print("❌ No se encontraron empleados activos en la base de datos")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    sid = sys.argv[1]
    temp_position = sys.argv[2]
    temp_unit = sys.argv[3]
    
    test_flex_staff_logic(sid, temp_position, temp_unit)


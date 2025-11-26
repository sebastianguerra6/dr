"""
Script de prueba simplificado para verificar el proceso de Flex Staff
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from services.access_management_service import access_service
    
    def test_flex_staff_logic(scotia_id: str, temporary_position: str, temporary_unit: str, duration_days: int = 30):
        """
        Prueba la lógica de flex staff sin ejecutar el proceso completo
        """
        print("=" * 80)
        print("PRUEBA DE LÓGICA DE FLEX STAFF")
        print("=" * 80)
        print(f"\nEmpleado: {scotia_id}")
        print(f"Posición temporal: {temporary_position}")
        print(f"Unidad temporal: {temporary_unit}")
        print(f"Duración: {duration_days} días\n")
        
        # 1. Verificar que el empleado existe
        employee = access_service.get_employee_by_id(scotia_id)
        if not employee:
            print(f"❌ ERROR: Empleado {scotia_id} no encontrado")
            return False
        
        print(f"✅ Empleado encontrado: {employee.get('full_name', 'N/A')}")
        print(f"   Posición original: {employee.get('position', 'N/A')}")
        print(f"   Unidad original: {employee.get('unit', 'N/A')}\n")
        
        # 2. Obtener accesos actuales del empleado
        print("📋 PASO 1: Obteniendo accesos actuales del empleado...")
        current_access = access_service.get_employee_current_access(scotia_id)
        print(f"   Accesos actuales encontrados: {len(current_access)}")
        
        current_apps_by_name = {}
        for acc in current_access:
            app_name = acc.get('logical_access_name', '').strip().upper()
            if app_name:
                current_apps_by_name[app_name] = acc
                print(f"   - {app_name} (tipo: {acc.get('process_access', 'N/A')})")
        
        print(f"\n   Total de accesos únicos: {len(current_apps_by_name)}\n")
        
        # 3. Obtener accesos flex_staff existentes
        print("📋 PASO 1.5: Obteniendo accesos flex_staff existentes...")
        flex_staff_access = access_service._get_all_flex_staff_access(scotia_id)
        print(f"   Accesos flex_staff existentes: {len(flex_staff_access)}")
        for acc in flex_staff_access:
            app_name = acc.get('logical_access_name', '').strip().upper()
            if app_name:
                print(f"   - {app_name} (estado: {acc.get('status', 'N/A')})")
        print()
        
        # 4. Obtener aplicaciones de la posición temporal
        print("📋 PASO 2: Obteniendo aplicaciones de la posición temporal...")
        temp_mesh_apps = access_service.get_applications_by_position_flexible(
            temporary_position, temporary_unit, subunit=None
        )
        print(f"   Aplicaciones encontradas para posición temporal: {len(temp_mesh_apps)}")
        
        temp_apps_by_name = {}
        for app in temp_mesh_apps:
            app_name = app.get('logical_access_name', '').strip().upper()
            if app_name:
                temp_apps_by_name[app_name] = app
                print(f"   - {app_name}")
        
        print(f"\n   Total de aplicaciones únicas: {len(temp_apps_by_name)}\n")
        
        # 5. Agregar accesos flex_staff a la comparación
        print("📋 PASO 3: Agregando accesos flex_staff a la comparación...")
        for acc in flex_staff_access:
            app_name = acc.get('logical_access_name', '').strip().upper()
            if app_name and app_name not in current_apps_by_name:
                current_apps_by_name[app_name] = acc
                print(f"   ✅ Agregado a comparación: {app_name}")
        print(f"   Total de accesos para comparar (incluyendo flex_staff): {len(current_apps_by_name)}\n")
        
        # 6. Calcular qué accesos se otorgarían
        print("📋 PASO 4: Calculando accesos a otorgar (solo los que NO tiene)...")
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
        print(f"   - Accesos originales mantenidos: {len(current_apps_by_name) - len(flex_staff_access)}\n")
        
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
    
    if __name__ == "__main__":
        if len(sys.argv) < 4:
            print("Uso: python test_flex_staff_simple.py <SID> <posicion_temporal> <unidad_temporal> [duracion_dias]")
            print("\nEjemplo:")
            print("  python test_flex_staff_simple.py 12345 ANALISTA SENIOR TECNOLOGÍA 30")
            print("\nO ejecutar sin parámetros para usar valores de prueba...")
            
            # Intentar obtener un empleado de prueba
            try:
                conn = access_service.get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT scotia_id, full_name, position, unit FROM headcount WHERE activo = 1 LIMIT 1')
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    sid, name, pos, unit = row
                    print(f"\n🔍 Empleado de prueba encontrado: {name} (SID: {sid})")
                    print(f"   Posición: {pos}, Unidad: {unit}")
                    print(f"\nEjecutando prueba con este empleado...\n")
                    test_flex_staff_logic(sid, pos or "ANALISTA SENIOR", unit or "TECNOLOGÍA", 30)
                else:
                    print("\n❌ No se encontraron empleados activos en la base de datos")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("\nPor favor, ejecute el script con parámetros:")
                print("  python test_flex_staff_simple.py <SID> <posicion> <unidad>")
            sys.exit(1)
        
        sid = sys.argv[1]
        temp_position = sys.argv[2]
        temp_unit = sys.argv[3]
        duration = int(sys.argv[4]) if len(sys.argv) > 4 else 30
        
        # Ejecutar prueba de lógica
        test_flex_staff_logic(sid, temp_position, temp_unit, duration)

except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrese de tener todas las dependencias instaladas.")
    sys.exit(1)


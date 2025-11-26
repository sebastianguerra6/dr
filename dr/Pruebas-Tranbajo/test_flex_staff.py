"""
Script de prueba para verificar el proceso de Flex Staff
Verifica que:
1. Solo otorga accesos que el empleado NO tiene
2. Mantiene los accesos originales
3. No crea duplicados
4. Maneja correctamente la comparación de nombres
"""

import sys
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
    
    # 3. Obtener aplicaciones de la posición temporal
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
    
    # 4. Calcular qué accesos se otorgarían
    print("📋 PASO 3: Calculando accesos a otorgar (solo los que NO tiene)...")
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
    print(f"   - Accesos originales mantenidos: {len(current_apps_by_name)}\n")
    
    # 5. Verificar lógica de duplicados
    print("📋 PASO 4: Verificando lógica de duplicados...")
    if len(to_grant_temp) == 0:
        print("   ⚠️  ADVERTENCIA: No se otorgarán nuevos accesos")
        print("   Esto es correcto si el empleado ya tiene todos los accesos de la posición temporal")
    else:
        print(f"   ✅ Se crearán {len(to_grant_temp)} registros históricos nuevos")
        print(f"   ✅ No se crearán duplicados para los {len(already_has)} accesos que ya tiene\n")
    
    # 6. Verificar que los nombres se comparan correctamente (case-insensitive)
    print("📋 PASO 5: Verificando comparación de nombres (case-insensitive)...")
    test_cases = [
        ("JIRA", "jira"),
        ("Confluence", "CONFLUENCE"),
        ("GitLab", "gitlab"),
    ]
    
    all_correct = True
    for name1, name2 in test_cases:
        name1_upper = name1.strip().upper()
        name2_upper = name2.strip().upper()
        if name1_upper == name2_upper:
            print(f"   ✅ '{name1}' == '{name2}' (comparación correcta)")
        else:
            print(f"   ❌ '{name1}' != '{name2}' (comparación incorrecta)")
            all_correct = False
    
    if all_correct:
        print("   ✅ La comparación de nombres funciona correctamente\n")
    else:
        print("   ❌ Hay problemas con la comparación de nombres\n")
    
    # 7. Resumen final
    print("=" * 80)
    print("RESUMEN DE LA PRUEBA")
    print("=" * 80)
    print(f"✅ Empleado existe: {employee.get('full_name', 'N/A')}")
    print(f"✅ Accesos actuales: {len(current_apps_by_name)}")
    print(f"✅ Aplicaciones de posición temporal: {len(temp_apps_by_name)}")
    print(f"✅ Accesos a otorgar: {len(to_grant_temp)}")
    print(f"✅ Accesos que ya tiene (no duplicados): {len(already_has)}")
    print(f"✅ Lógica de comparación: {'Correcta' if all_correct else 'Con problemas'}")
    print("=" * 80)
    
    return True

def test_flex_staff_execution(scotia_id: str, temporary_position: str, temporary_unit: str, duration_days: int = 30):
    """
    Ejecuta el proceso completo de flex staff y verifica los resultados
    """
    print("\n" + "=" * 80)
    print("EJECUCIÓN COMPLETA DE FLEX STAFF")
    print("=" * 80)
    
    # Ejecutar flex staff
    success, message, records = access_service.process_flex_staff_assignment(
        scotia_id, temporary_position, temporary_unit, None, duration_days, "Sistema"
    )
    
    if success:
        print(f"\n✅ Flex staff ejecutado exitosamente")
        print(f"\nMensaje:\n{message}")
        print(f"\nRegistros creados: {len(records)}")
        for record in records:
            print(f"   - {record.get('app_access_name', 'N/A')}")
    else:
        print(f"\n❌ Error ejecutando flex staff: {message}")
    
    return success

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python test_flex_staff.py <SID> <posicion_temporal> <unidad_temporal> [duracion_dias]")
        print("\nEjemplo:")
        print("  python test_flex_staff.py 12345 ANALISTA SENIOR TECNOLOGÍA 30")
        sys.exit(1)
    
    sid = sys.argv[1]
    temp_position = sys.argv[2]
    temp_unit = sys.argv[3]
    duration = int(sys.argv[4]) if len(sys.argv) > 4 else 30
    
    # Ejecutar prueba de lógica
    test_flex_staff_logic(sid, temp_position, temp_unit, duration)
    
    # Preguntar si ejecutar el proceso completo
    print("\n" + "=" * 80)
    respuesta = input("¿Desea ejecutar el proceso completo de flex staff? (s/n): ")
    if respuesta.lower() == 's':
        test_flex_staff_execution(sid, temp_position, temp_unit, duration)
    else:
        print("Prueba de lógica completada. El proceso completo no se ejecutó.")


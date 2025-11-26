# GAMLO - Sistema Integrado de Gestión de Empleados y Conciliación de Accesos

## 📋 Descripción General

Sistema de escritorio desarrollado en Python con Tkinter para la gestión integral de empleados, incluyendo procesos de onboarding, offboarding, movimientos laterales, flex staff y conciliación de accesos. **Soporta tanto SQLite como SQL Server** con configuración flexible y arquitectura híbrida optimizada.

## 🚀 Características Principales

### 🎨 **Interfaz Moderna y Responsive**
- **Navegación lateral**: Botones grandes con iconos descriptivos
- **Estilos personalizados**: Sistema de estilos consistente y moderno
- **Ventana responsive**: Se adapta automáticamente al tamaño de pantalla
- **Logo GAMLO**: Posicionado estratégicamente en la interfaz
- **Tema profesional**: Colores corporativos y tipografía optimizada

### 🔧 **Funcionalidades Core**
- **Gestión de Procesos**: Onboarding, offboarding, movimientos laterales y flex staff
- **Edición y Búsqueda**: Herramientas avanzadas para modificar y consultar registros
- **Creación de Personas**: Formulario completo para agregar nuevos empleados
- **Filtrado Avanzado**: Sistema de filtrado en tiempo real con selección de columna
- **Conciliación de Accesos**: Sistema completo para gestionar permisos de usuarios
- **Acceso Manual**: Registro manual de accesos con filtrado por posición

### 🗄️ **Soporte Dual de Base de Datos**
- **SQLite**: Por defecto, ideal para desarrollo y pruebas
- **SQL Server**: Para entornos empresariales y producción
- **Configuración flexible**: Cambio fácil entre bases de datos
- **Migración automática**: Herramientas para migrar datos entre sistemas
- **Arquitectura híbrida**: Balance óptimo entre SQL Server y Python

## 🆕 Sistema de Conciliación de Accesos Avanzado

### **Características del Sistema**
- **Conciliación por SID**: Analiza accesos actuales vs. autorizados para un usuario específico
- **Conciliación Masiva**: Procesa todos los usuarios del sistema
- **Exportación a Excel**: Genera reportes con hojas de resumen y tickets
- **Registro de Tickets**: Crea tickets automáticos para accesos a otorgar/revocar
- **Historial Completo**: Seguimiento de todos los cambios de accesos
- **Flex Staff**: Gestión de accesos temporales para proyectos específicos

### **Funcionalidades Implementadas**
- ✅ **Conciliar Accesos**: Por SID específico con análisis detallado
- ✅ **Exportar Excel**: Con formato profesional y múltiples hojas
- ✅ **Registrar Tickets**: Inserta en histórico lo calculado
- ✅ **Conciliar Todos**: Procesamiento masivo del sistema
- ✅ **Base de Datos Dual**: SQLite y SQL Server
- ✅ **Flex Staff**: Accesos temporales con revocación automática
- ✅ **Acceso Manual**: Registro manual con filtrado por posición
- ✅ **Ver Accesos Actuales**: Visualización completa de accesos del empleado

## 🗂️ Estructura del Proyecto

```
Pruebas-Tranbajo/
├── app_empleados_refactorizada.py    # Aplicación principal
├── config.py                         # Configuración del sistema
├── requirements.txt                  # Dependencias
├── README.md                         # Este archivo
├── sql_server_setup.sql              # Script de configuración SQL Server
├── services/
│   ├── __init__.py
│   ├── access_management_service.py  # Servicio de gestión de accesos
│   ├── dropdown_service.py          # Servicio de dropdowns
│   ├── excel_importer.py            # Importador de Excel
│   ├── export_service.py            # Servicio de exportación
│   ├── history_service.py           # Servicio de historial
│   └── search_service.py            # Servicio de búsqueda
├── ui/
│   ├── __init__.py
│   ├── components.py                 # Componentes de interfaz
│   ├── manual_access_component.py   # Componente de registro manual
│   └── styles.py                    # Estilos personalizados
├── tests/
│   └── __init__.py
├── database/                         # Directorio para bases de datos
├── images/                          # Directorio para imágenes
└── output/                          # Archivos Excel generados
```

## 🚀 Instalación y Configuración

### **1. Instalación de Dependencias**
```bash
pip install -r requirements.txt
```

### **2. Configuración de Base de Datos**

#### **Opción A: SQLite (Por Defecto)**
```bash
# No requiere configuración adicional
python app_empleados_refactorizada.py
```

#### **Opción B: SQL Server**
```bash
# 1. Configurar SQL Server
# Abrir SQL Server Management Studio
# Ejecutar: sql_server_setup.sql

# 2. Configurar conexión en config.py
# Editar las credenciales de conexión

# 3. Ejecutar aplicación
python app_empleados_refactorizada.py
```

### **3. Verificación de Configuración**
```bash
# Probar configuración actual
python app_empleados_refactorizada.py
```

## 🔧 Configuración Avanzada

### **Configuración de SQL Server**

Editar `config.py`:
```python
# Cambiar a True para usar SQL Server
USE_SQL_SERVER = True

# Configuración de SQL Server
SQL_SERVER_CONFIG = {
    'server': 'localhost',  # Tu servidor SQL Server
    'database': 'GAMLO_Empleados',
    'username': 'sa',  # Tu usuario
    'password': 'TuPassword123!',  # Tu contraseña
    'driver': '{ODBC Driver 17 for SQL Server}',
    'trusted_connection': 'no',
    'timeout': 30
}
```

### **Requisitos para SQL Server**
- **SQL Server 2016+** (Express, Standard, o Enterprise)
- **ODBC Driver 17 for SQL Server**
- **SQL Server Management Studio** (recomendado)
- **Puerto 1433** abierto

## 📊 Estructura de Base de Datos

### **Tablas Principales**

#### **1. headcount** - Empleados
```sql
- scotia_id (PK) - ID único del empleado
- employee - Nombre de usuario
- full_name - Nombre completo
- email - Correo electrónico
- position - Cargo/Posición
- unit - Unidad/Departamento
- unidad_subunidad - Unidad/Subunidad completa
- activo - Estado activo/inactivo
```

#### **2. applications** - Aplicaciones
```sql
- id (PK) - ID autoincremental
- logical_access_name - Nombre lógico del acceso
- unit - Unidad que usa la aplicación
- subunit - Subunidad específica
- unidad_subunidad - Unidad/Subunidad completa
- position_role - Rol de posición requerido
- role_name - Nombre del rol
- category - Categoría de la aplicación
- access_status - Estado del acceso
```

#### **3. historico** - Historial de Procesos (Actualizado)
```sql
- id (PK) - ID autoincremental
- scotia_id (FK) - Referencia a headcount
- case_id - ID del caso
- responsible - Responsable del proceso
- record_date - Fecha de registro
- request_date - Fecha de solicitud
- process_access - Tipo de proceso
- subunit - Subunidad (unidad/subunidad)
- event_description - Descripción del evento
- ticket_email - Email del ticket
- app_access_name - Nombre de la aplicación
- computer_system_type - Tipo de sistema (category)
- duration_of_access - Duración del acceso
- status - Estado del proceso
- closing_date_app - Fecha de cierre de aplicación
- closing_date_ticket - Fecha de cierre de ticket
- app_quality - Calidad de la aplicación
- confirmation_by_user - Confirmación del usuario
- comment - Comentario
- comment_tq - Comentario TQ
- ticket_quality - Calidad del ticket
- general_status_ticket - Estado general del ticket
- general_status_case - Estado general del caso
- average_time_open_ticket - Tiempo promedio de ticket abierto
- sla_app - SLA de la aplicación
- sla_ticket - SLA del ticket
- sla_case - SLA del caso
```

#### **4. procesos** - Gestión de Procesos
```sql
- id (PK) - ID autoincremental
- sid (FK) - Referencia a headcount
- tipo_proceso - Tipo de proceso
- status - Estado del proceso
```

### **Vistas del Sistema**
- **vw_required_apps**: Aplicaciones requeridas por empleado
- **vw_current_access**: Accesos actuales de cada empleado
- **vw_to_grant**: Accesos que faltan y deben ser otorgados
- **vw_to_revoke**: Accesos excesivos que deben ser revocados
- **vw_system_stats**: Estadísticas generales del sistema

### **Procedimientos Almacenados**
- **sp_GetAccessReconciliationReport**: Reporte completo de conciliación
- **sp_ProcessEmployeeOnboarding**: Procesamiento de onboarding
- **sp_ProcessEmployeeOffboarding**: Procesamiento de offboarding
- **sp_GetReconciliationStats**: Estadísticas de conciliación
- **sp_GetEmployeeHistory**: Historial de empleado
- **sp_GetApplicationsByPosition**: Aplicaciones por posición

## 🎯 Uso del Sistema

### **1. Gestión de Empleados**
- **Crear empleado**: Formulario de creación con validaciones completas
- **Editar empleado**: Modificar datos existentes con verificación
- **Buscar empleado**: Filtrado avanzado por múltiples criterios
- **Ver accesos actuales**: Visualización completa de accesos del empleado

### **2. Procesos de Acceso**
- **Onboarding**: Otorgar accesos para nueva posición
- **Offboarding**: Revocar accesos al salir de posición
- **Lateral Movement**: Movimiento aditivo (mantiene accesos actuales + agrega nuevos)
- **Flex Staff**: Accesos temporales para proyectos específicos
- **Acceso Manual**: Registro manual con filtrado por posición y nivel de permiso

### **3. Conciliación de Accesos**
- **Conciliar por SID**: Analizar accesos de un empleado específico
- **Conciliar todos**: Procesamiento masivo del sistema
- **Exportar Excel**: Generar reportes detallados con múltiples hojas
- **Registrar tickets**: Crear tickets automáticos
- **Ver accesos actuales**: Visualización completa de accesos

### **4. Búsqueda y Filtrado**
- **Filtrado en tiempo real**: Resultados se actualizan automáticamente
- **Selección de columna**: Filtrar por cualquier campo
- **Búsqueda inteligente**: Coincidencias parciales insensibles a mayúsculas
- **Filtrado por posición**: En acceso manual para seleccionar nivel correcto

## 🔧 Solución de Problemas

### **Error de Conexión SQL Server**
```bash
# Verificar que SQL Server esté ejecutándose
# Verificar credenciales en config.py
# Verificar que el puerto 1433 esté abierto
# Verificar que ODBC Driver 17 esté instalado
```

### **Error de Driver ODBC**
```bash
# Instalar "ODBC Driver 17 for SQL Server"
# Verificar que esté en la lista de drivers ODBC
```

### **Error de Permisos**
```bash
# Verificar que el usuario tenga permisos en la base de datos
# Ejecutar como administrador
```

### **Error de Accesos Actuales**
```bash
# Verificar que la consulta use unidad_subunidad y position_role
# Revisar que los accesos estén completados
```

## 🧪 Datos de Ejemplo

El sistema incluye datos de ejemplo para pruebas:
- **Empleados**: 3 empleados activos con diferentes posiciones
- **Aplicaciones**: 20+ aplicaciones en diferentes unidades y posiciones
- **Historial**: Registros de procesos completados
- **Procesos**: Gestión de procesos activos

## 🔧 Tecnologías Utilizadas

- **Python 3.10+**
- **Tkinter/ttk**: Interfaz gráfica moderna
- **SQLite3**: Base de datos por defecto
- **SQL Server**: Base de datos empresarial
- **pyodbc**: Conexión a SQL Server
- **Pandas**: Manipulación de datos
- **OpenPyXL**: Generación de archivos Excel
- **Threading**: Operaciones no bloqueantes
- **PIL**: Manejo de imágenes

## 📋 Criterios de Aceptación Cumplidos

- ✅ **Conciliar Accesos**: Muestra qué apps otorgar/quitar por SID
- ✅ **Exportar Excel**: Crea archivo con múltiples hojas y formato profesional
- ✅ **Registrar Tickets**: Agrega filas en historial consistentes
- ✅ **Re-ejecutar**: La conciliación refleja el nuevo estado
- ✅ **Integración UI**: Usa StringVar existentes sin remaquetar
- ✅ **Base de Datos Dual**: SQLite y SQL Server funcionando
- ✅ **Lateral Movement**: Lógica aditiva implementada
- ✅ **Flex Staff**: Accesos temporales con revocación
- ✅ **Acceso Manual**: Con filtrado por posición y nivel
- ✅ **Ver Accesos Actuales**: Visualización completa de accesos
- ✅ **Arquitectura Híbrida**: Balance óptimo entre SQL Server y Python

## 🚀 Características Avanzadas

### **1. Lateral Movement Aditivo**
- **Mantiene accesos actuales**: No revoca accesos existentes
- **Agrega nuevos accesos**: Solo otorga accesos que no tiene
- **Coexistencia**: Permite aplicaciones con mismo nombre pero diferente subunit

### **2. Flex Staff**
- **Accesos temporales**: Para proyectos específicos
- **Revocación automática**: Al finalizar el período
- **Gestión independiente**: No interfiere con accesos permanentes

### **3. Acceso Manual Mejorado**
- **Filtrado por posición**: Selecciona aplicaciones relevantes
- **Nivel de permiso**: Escoge el nivel correcto para la posición
- **Validación completa**: Verifica empleado y aplicación

### **4. Ver Accesos Actuales**
- **Visualización completa**: Todos los accesos del empleado
- **Filtrado inteligente**: Por tipo de acceso y estado
- **Información detallada**: Fechas, responsables, descripciones

### **5. Configuración Flexible**
- **Cambio fácil**: Entre SQLite y SQL Server
- **Herramientas de diagnóstico**: Verificación automática de configuración
- **Migración automática**: Datos se migran automáticamente

### **6. Robustez del Sistema**
- **Manejo de errores**: En cada operación
- **Verificaciones de integridad**: Antes de cada operación
- **Mensajes informativos**: Para debugging y monitoreo
- **Logs detallados**: Para seguimiento de operaciones

## 📞 Soporte y Mantenimiento

### **Para problemas específicos:**
1. **Verificar logs** de la aplicación
2. **Revisar configuración** de base de datos
3. **Consultar documentación** técnica incluida
4. **Verificar permisos** de usuario y base de datos
5. **Revisar estructura** de tablas y vistas

### **Para actualizaciones:**
1. **Hacer backup** de la base de datos
2. **Probar cambios** en entorno de desarrollo
3. **Documentar cambios** realizados
4. **Capacitar usuarios** sobre nuevas funcionalidades
5. **Actualizar documentación** técnica

## ✅ Estado Final

**🎉 SISTEMA COMPLETAMENTE FUNCIONAL Y OPTIMIZADO**

- ✅ Todas las funcionalidades implementadas y probadas
- ✅ Soporte dual de base de datos (SQLite + SQL Server)
- ✅ Lateral movement aditivo funcionando perfectamente
- ✅ Flex staff con revocación automática
- ✅ Acceso manual con filtrado inteligente
- ✅ Ver accesos actuales con información completa
- ✅ Conciliación de accesos precisa y detallada
- ✅ Interfaz moderna, responsive y profesional
- ✅ Arquitectura híbrida optimizada
- ✅ Herramientas de configuración incluidas
- ✅ Documentación completa y actualizada
- ✅ Scripts de migración y configuración listos
- ✅ Estructura de base de datos optimizada
- ✅ Procedimientos almacenados implementados

**El sistema está listo para usar en producción con cualquiera de las dos bases de datos y todas las funcionalidades avanzadas implementadas.**

---

## 📄 Licencia

Este proyecto es de uso interno para pruebas de trabajo.

## 🤝 Contribuciones

Para contribuir al proyecto:
1. Mantener la estructura de código limpia y documentada
2. Seguir las convenciones de nomenclatura existentes
3. Probar cambios antes de enviar
4. Documentar nuevas funcionalidades
5. Actualizar este README cuando sea necesario
6. Mantener compatibilidad con ambas bases de datos
7. Seguir la arquitectura híbrida establecida
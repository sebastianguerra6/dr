#!/usr/bin/env python3
"""
Configuración del sistema para SQL Server
Sistema optimizado para usar únicamente SQL Server
"""
import os
import pyodbc
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# =====================================================
# CONFIGURACIÓN SQL SERVER
# =====================================================

# Configuración de SQL Server
SQL_SERVER_CONFIG = {
    'server': 'localhost\\SQLEXPRESS01',  # Instancia SQLEXPRESS
    'database': 'GAMLO_Empleados',
    'username': '',  # No necesario con Windows Authentication
    'password': '',  # No necesario con Windows Authentication
    'driver': '{ODBC Driver 17 for SQL Server}',  # Ajustar según tu versión
    'trusted_connection': 'yes',  # Usar Windows Authentication
    'timeout': 30
}

# =====================================================
# GESTOR DE BASE DE DATOS
# =====================================================

class SQLServerConnection:
    """Clase para conexiones a SQL Server"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or SQL_SERVER_CONFIG
        self.connection_string = self._build_connection_string()
    
    def _build_connection_string(self) -> str:
        """Construye la cadena de conexión para SQL Server"""
        if self.config.get('trusted_connection', 'no').lower() == 'yes':
            # Autenticación de Windows (Trusted Connection)
            return (
                f"DRIVER={self.config['driver']};"
                f"SERVER={self.config['server']};"
                f"DATABASE={self.config['database']};"
                f"Trusted_Connection=yes;"
                f"Timeout={self.config['timeout']};"
            )
        else:
            # Autenticación SQL Server con usuario y contraseña
            if not self.config.get('username') or not self.config.get('password'):
                raise ValueError("Username y password son requeridos para autenticación SQL Server")
            
            return (
                f"DRIVER={self.config['driver']};"
                f"SERVER={self.config['server']};"
                f"DATABASE={self.config['database']};"
                f"UID={self.config['username']};"
                f"PWD={self.config['password']};"
                f"Timeout={self.config['timeout']};"
            )
    
    def get_connection(self) -> pyodbc.Connection:
        """Obtiene una conexión a la base de datos SQL Server"""
        try:
            return pyodbc.connect(self.connection_string)
        except pyodbc.Error as e:
            print(f"Error conectando a SQL Server: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Prueba la conexión a la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            return result[0] == 1
        except Exception as e:
            print(f"Error probando conexión: {e}")
            return False

# =====================================================
# FUNCIONES DE CONFIGURACIÓN
# =====================================================

def get_database_connection():
    """Retorna la clase de conexión a SQL Server"""
    return SQLServerConnection()

def test_database_connection():
    """Prueba la conexión a SQL Server"""
    connection = get_database_connection()
    return connection.test_connection()

def get_connection_info():
    """Retorna información sobre la configuración de conexión"""
    config = SQL_SERVER_CONFIG
    return {
        'type': 'SQL Server',
        'server': config['server'],
        'database': config['database'],
        'authentication': 'Windows Authentication' if config['trusted_connection'] == 'yes' else 'SQL Server Authentication',
        'driver': config['driver']
    }

# =====================================================
# FUNCIÓN PRINCIPAL
# =====================================================

if __name__ == "__main__":
    print("=== CONFIGURACIÓN DE CONEXIÓN SQL SERVER ===")
    
    config = SQL_SERVER_CONFIG
    print(f"🔐 Autenticación: {'Windows Authentication' if config['trusted_connection'] == 'yes' else 'SQL Server Authentication'}")
    print(f"🖥️  Servidor: {config['server']}")
    print(f"🗄️  Base de datos: {config['database']}")
    print(f"⏱️  Timeout: {config['timeout']} segundos")
    
    print("\n" + "="*50)
    
    # Probar conexión
    print("🔍 Probando conexión...")
    if test_database_connection():
        print("✅ Conexión a SQL Server exitosa")
        print("🎯 Sistema listo para usar")
    else:
        print("❌ Error conectando a SQL Server")
        print("\n🔧 Soluciones posibles:")
        print("   - Verificar que SQL Server esté ejecutándose")
        print("   - Verificar que el usuario tenga permisos en la base de datos")
        print("   - Verificar la configuración del servidor y base de datos")
        print("   - Verificar que la base de datos 'GAMLO_Empleados' exista")
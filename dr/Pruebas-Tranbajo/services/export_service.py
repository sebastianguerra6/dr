"""
Servicio de exportación a Excel para tickets de conciliación
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import os


class ExportService:
    """Servicio para exportar datos de conciliación a Excel"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_reconciliation_tickets(self, 
                                   reconciliation_data: List[Dict[str, Any]],
                                   ingresado_por: str = "Sistema",
                                   status: str = "Pendiente",
                                   comment: str = "") -> str:
        """
        Exporta los tickets de conciliación a Excel
        
        Args:
            reconciliation_data: Lista de resultados de conciliación
            ingresado_por: Usuario que genera los tickets
            status: Estado inicial de los tickets
            comment: Comentario general para todos los tickets
            
        Returns:
            Ruta del archivo Excel generado
        """
        try:
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"tickets_{timestamp}.xlsx"
            filepath = self.output_dir / filename
            
            # Preparar datos para la hoja de resumen
            summary_data = []
            all_tickets = []
            
            for person_data in reconciliation_data:
                if "error" in person_data:
                    continue
                
                sid = person_data.get("person_info", {}).get("sid", "N/A")
                area = person_data.get("person_info", {}).get("area", "N/A")
                subunit = person_data.get("person_info", {}).get("subunit", "N/A")
                cargo = person_data.get("person_info", {}).get("cargo", "N/A")
                
                current_count = len(person_data.get("current", []))
                target_count = len(person_data.get("target", []))
                to_grant_count = len(person_data.get("to_grant", []))
                to_revoke_count = len(person_data.get("to_revoke", []))
                
                # Agregar a resumen
                summary_data.append({
                    "SID": sid,
                    "Área": area,
                    "Sub Unidad": subunit,
                    "Cargo": cargo,
                    "Accesos Actuales": current_count,
                    "Accesos Objetivo": target_count,
                    "A Otorgar": to_grant_count,
                    "A Revocar": to_revoke_count
                })
                
                # Agregar tickets de GRANT
                for grant_item in person_data.get("to_grant", []):
                    all_tickets.append({
                        "SID": grant_item["sid"],
                        "App": grant_item["app_name"],
                        "Rol": grant_item.get("role_name", ""),
                        "Acción": grant_item["accion"],
                        "Motivo": grant_item["motivo"],
                        "Ingresado Por": ingresado_por,
                        "Fecha Solicitud": datetime.now().strftime("%Y-%m-%d"),
                        "Status": status,
                        "Comentarios": comment or f"Acceso requerido para {grant_item['app_name']}"
                    })
                
                # Agregar tickets de REVOKE
                for revoke_item in person_data.get("to_revoke", []):
                    all_tickets.append({
                        "SID": revoke_item["sid"],
                        "App": revoke_item["app_name"],
                        "Rol": revoke_item.get("role_name", ""),
                        "Acción": revoke_item["accion"],
                        "Motivo": revoke_item["motivo"],
                        "Ingresado Por": ingresado_por,
                        "Fecha Solicitud": datetime.now().strftime("%Y-%m-%d"),
                        "Status": status,
                        "Comentarios": comment or f"Acceso no autorizado para {revoke_item['app_name']}"
                    })
            
            # Crear DataFrames
            summary_df = pd.DataFrame(summary_data)
            tickets_df = pd.DataFrame(all_tickets)
            
            # Crear archivo Excel con múltiples hojas
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja de resumen
                summary_df.to_excel(writer, sheet_name='Resumen', index=False)
                
                # Hoja de tickets
                if not tickets_df.empty:
                    tickets_df.to_excel(writer, sheet_name='Tickets', index=False)
                else:
                    # Crear hoja vacía con columnas
                    empty_tickets = pd.DataFrame(columns=[
                        "SID", "App", "Rol", "Acción", "Motivo", 
                        "Ingresado Por", "Fecha Solicitud", "Status", "Comentarios"
                    ])
                    empty_tickets.to_excel(writer, sheet_name='Tickets', index=False)
                
                # Ajustar ancho de columnas
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return str(filepath)
            
        except Exception as e:
            raise Exception(f"Error exportando a Excel: {str(e)}")
    
    def export_single_person_tickets(self, 
                                   reconciliation_data: Dict[str, Any],
                                   ingresado_por: str = "Sistema",
                                   status: str = "Pendiente",
                                   comment: str = "") -> str:
        """
        Exporta tickets de conciliación para una sola persona
        
        Args:
            reconciliation_data: Resultado de conciliación de una persona
            ingresado_por: Usuario que genera los tickets
            status: Estado inicial de los tickets
            comment: Comentario general para todos los tickets
            
        Returns:
            Ruta del archivo Excel generado
        """
        return self.export_reconciliation_tickets([reconciliation_data], ingresado_por, status, comment)
    
    def export_access_history(self, 
                            access_history: List[Dict[str, Any]],
                            filename_prefix: str = "historial_accesos") -> str:
        """
        Exporta el historial de accesos a Excel
        
        Args:
            access_history: Lista de registros de historial
            filename_prefix: Prefijo para el nombre del archivo
            
        Returns:
            Ruta del archivo Excel generado
        """
        try:
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"{filename_prefix}_{timestamp}.xlsx"
            filepath = self.output_dir / filename
            
            # Crear DataFrame
            df = pd.DataFrame(access_history)
            
            # Crear archivo Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Historial', index=False)
                
                # Ajustar ancho de columnas
                worksheet = writer.sheets['Historial']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return str(filepath)
            
        except Exception as e:
            raise Exception(f"Error exportando historial: {str(e)}")
    
    def export_authorized_matrix(self, 
                               matrix_data: List[Dict[str, Any]],
                               filename_prefix: str = "matriz_autorizaciones") -> str:
        """
        Exporta la matriz de autorizaciones a Excel
        
        Args:
            matrix_data: Lista de registros de matriz de autorizaciones
            filename_prefix: Prefijo para el nombre del archivo
            
        Returns:
            Ruta del archivo Excel generado
        """
        try:
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"{filename_prefix}_{timestamp}.xlsx"
            filepath = self.output_dir / filename
            
            # Crear DataFrame
            df = pd.DataFrame(matrix_data)
            
            # Crear archivo Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Matriz', index=False)
                
                # Ajustar ancho de columnas
                worksheet = writer.sheets['Matriz']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return str(filepath)
            
        except Exception as e:
            raise Exception(f"Error exportando matriz: {str(e)}")
    
    def get_output_files(self) -> List[str]:
        """
        Obtiene la lista de archivos de salida existentes
        
        Returns:
            Lista de nombres de archivos
        """
        try:
            if not self.output_dir.exists():
                return []
            
            files = [f.name for f in self.output_dir.iterdir() if f.is_file() and f.suffix == '.xlsx']
            return sorted(files, reverse=True)  # Más recientes primero
            
        except Exception as e:
            print(f"Error obteniendo archivos de salida: {e}")
            return []
    
    def cleanup_old_files(self, keep_days: int = 30) -> int:
        """
        Limpia archivos antiguos del directorio de salida
        
        Args:
            keep_days: Número de días a mantener
            
        Returns:
            Número de archivos eliminados
        """
        try:
            if not self.output_dir.exists():
                return 0
            
            cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
            deleted_count = 0
            
            for file_path in self.output_dir.iterdir():
                if file_path.is_file() and file_path.suffix == '.xlsx':
                    if file_path.stat().st_mtime < cutoff_date:
                        file_path.unlink()
                        deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            print(f"Error limpiando archivos antiguos: {e}")
            return 0

    def export_headcount_statistics(self, statistics_data: Dict[str, Any], 
                                   source_system: str = "Sistema Integrado") -> str:
        """Exporta estadísticas del headcount a Excel"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"estadisticas_headcount_{timestamp}.xlsx"
            filepath = os.path.join(self.output_dir, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja 1: Estadísticas Generales
                if 'generales' in statistics_data:
                    generales_df = pd.DataFrame([statistics_data['generales']])
                    generales_df.to_excel(writer, sheet_name='Generales', index=False)
                
                # Hoja 2: Por Unidad
                if 'por_unidad' in statistics_data and statistics_data['por_unidad']:
                    unidad_df = pd.DataFrame(statistics_data['por_unidad'])
                    unidad_df.to_excel(writer, sheet_name='Por Unidad', index=False)
                
                # Hoja 3: Por Puesto
                if 'por_puesto' in statistics_data and statistics_data['por_puesto']:
                    puesto_df = pd.DataFrame(statistics_data['por_puesto'])
                    puesto_df.to_excel(writer, sheet_name='Por Puesto', index=False)
                
                # Hoja 4: Por Manager
                if 'por_manager' in statistics_data and statistics_data['por_manager']:
                    manager_df = pd.DataFrame(statistics_data['por_manager'])
                    manager_df.to_excel(writer, sheet_name='Por Manager', index=False)
                
                # Hoja 5: Por Senior Manager
                if 'por_senior_manager' in statistics_data and statistics_data['por_senior_manager']:
                    senior_manager_df = pd.DataFrame(statistics_data['por_senior_manager'])
                    senior_manager_df.to_excel(writer, sheet_name='Por Senior Manager', index=False)
                
                # Hoja 6: Por Estado
                if 'por_estado' in statistics_data and statistics_data['por_estado']:
                    estado_df = pd.DataFrame(statistics_data['por_estado'])
                    estado_df.to_excel(writer, sheet_name='Por Estado', index=False)
                
                # Hoja 7: Por Año de Inicio
                if 'por_año_inicio' in statistics_data and statistics_data['por_año_inicio']:
                    año_df = pd.DataFrame(statistics_data['por_año_inicio'])
                    año_df.to_excel(writer, sheet_name='Por Año de Inicio', index=False)
                
                # Hoja 8: Detalle por Unidad
                if 'detalle_por_unidad' in statistics_data and statistics_data['detalle_por_unidad']:
                    detalle_df = pd.DataFrame(statistics_data['detalle_por_unidad'])
                    detalle_df.to_excel(writer, sheet_name='Detalle por Unidad', index=False)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error exportando estadísticas del headcount: {str(e)}")

    def export_historial_statistics(self, statistics_data: Dict[str, Any], 
                                  source_system: str = "Sistema Integrado") -> str:
        """Exporta estadísticas del historial a Excel"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"estadisticas_historial_{timestamp}.xlsx"
            filepath = os.path.join(self.output_dir, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja 1: Estadísticas Generales
                if 'generales' in statistics_data:
                    generales_df = pd.DataFrame([statistics_data['generales']])
                    generales_df.to_excel(writer, sheet_name='Generales', index=False)
                
                # Hoja 2: Por Unidad
                if 'por_unidad' in statistics_data and statistics_data['por_unidad']:
                    unidad_df = pd.DataFrame(statistics_data['por_unidad'])
                    unidad_df.to_excel(writer, sheet_name='Por Unidad', index=False)
                
                # Hoja 3: Por Subunidad
                if 'por_subunidad' in statistics_data and statistics_data['por_subunidad']:
                    subunidad_df = pd.DataFrame(statistics_data['por_subunidad'])
                    subunidad_df.to_excel(writer, sheet_name='Por Subunidad', index=False)
                
                # Hoja 4: Por Puesto
                if 'por_puesto' in statistics_data and statistics_data['por_puesto']:
                    puesto_df = pd.DataFrame(statistics_data['por_puesto'])
                    puesto_df.to_excel(writer, sheet_name='Por Puesto', index=False)
                
                # Hoja 5: Por Aplicación
                if 'por_aplicacion' in statistics_data and statistics_data['por_aplicacion']:
                    aplicacion_df = pd.DataFrame(statistics_data['por_aplicacion'])
                    aplicacion_df.to_excel(writer, sheet_name='Por Aplicación', index=False)
                
                # Hoja 6: Por Proceso
                if 'por_proceso' in statistics_data and statistics_data['por_proceso']:
                    proceso_df = pd.DataFrame(statistics_data['por_proceso'])
                    proceso_df.to_excel(writer, sheet_name='Por Proceso', index=False)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error exportando estadísticas: {str(e)}")


# Instancia global para usar en toda la aplicación
export_service = ExportService()


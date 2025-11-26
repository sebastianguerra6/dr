"""
Servicio de historial para registrar tickets de conciliación
Sistema optimizado para SQL Server únicamente
"""
from typing import List, Dict, Any, Tuple
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import get_database_connection


class HistoryService:
    """Servicio para manejar el historial de accesos"""
    
    def __init__(self):
        self.db_manager = get_database_connection()
    
    def register_reconciliation_tickets(self, 
                                     reconciliation_data: Dict[str, Any],
                                     ingresado_por: str,
                                     status: str = "Pendiente",
                                     comment: str = "",
                                     check_duplicates: bool = True) -> Dict[str, Any]:
        """
        Registra los tickets de conciliación en el historial
        
        Args:
            reconciliation_data: Resultado de conciliación de una persona
            ingresado_por: Usuario que genera los tickets
            status: Estado inicial de los tickets
            comment: Comentario general para todos los tickets
            check_duplicates: Si verificar duplicados recientes
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            if "error" in reconciliation_data:
                return {
                    "success": False,
                    "error": reconciliation_data["error"],
                    "tickets_created": 0,
                    "tickets_skipped": 0
                }
            
            sid = reconciliation_data.get("person_info", {}).get("sid")
            if not sid:
                # Intentar obtener SID de los datos de conciliación
                to_grant = reconciliation_data.get("to_grant", [])
                to_revoke = reconciliation_data.get("to_revoke", [])
                if to_grant:
                    sid = to_grant[0].get("sid")
                elif to_revoke:
                    sid = to_revoke[0].get("sid")
                
                if not sid:
                    return {
                        "success": False,
                        "error": "No se pudo determinar el SID",
                        "tickets_created": 0,
                        "tickets_skipped": 0
                    }
            
            tickets_created = 0
            tickets_skipped = 0
            errors = []
            
            # Registrar tickets de GRANT (onboarding)
            for grant_item in reconciliation_data.get("to_grant", []):
                app_name = grant_item["app_name"]
                role_name = grant_item.get("role_name")
                
                # Verificar duplicados si está habilitado
                if check_duplicates and self.queries.check_duplicate_ticket(sid, app_name, "onboarding"):
                    tickets_skipped += 1
                    continue
                
                try:
                    self._insert_access_history(
                        sid=sid,
                        app_name=app_name,
                        role_name=role_name,
                        tipo="onboarding",
                        ingresado_por=ingresado_por,
                        status=status,
                        comment=comment or grant_item.get("motivo", "")
                    )
                    tickets_created += 1
                except Exception as e:
                    errors.append(f"Error creando ticket GRANT para {app_name}: {str(e)}")
            
            # Registrar tickets de REVOKE (offboarding)
            for revoke_item in reconciliation_data.get("to_revoke", []):
                app_name = revoke_item["app_name"]
                role_name = revoke_item.get("role_name")
                
                # Verificar duplicados si está habilitado
                if check_duplicates and self.queries.check_duplicate_ticket(sid, app_name, "offboarding"):
                    tickets_skipped += 1
                    continue
                
                try:
                    self._insert_access_history(
                        sid=sid,
                        app_name=app_name,
                        role_name=role_name,
                        tipo="offboarding",
                        ingresado_por=ingresado_por,
                        status=status,
                        comment=comment or revoke_item.get("motivo", "")
                    )
                    tickets_created += 1
                except Exception as e:
                    errors.append(f"Error creando ticket REVOKE para {app_name}: {str(e)}")
            
            return {
                "success": True,
                "tickets_created": tickets_created,
                "tickets_skipped": tickets_skipped,
                "errors": errors,
                "sid": sid
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error general registrando tickets: {str(e)}",
                "tickets_created": 0,
                "tickets_skipped": 0
            }
    
    def register_bulk_tickets(self, 
                            reconciliation_data_list: List[Dict[str, Any]],
                            ingresado_por: str,
                            status: str = "Pendiente",
                            comment: str = "",
                            check_duplicates: bool = True) -> Dict[str, Any]:
        """
        Registra tickets de conciliación para múltiples personas
        
        Args:
            reconciliation_data_list: Lista de resultados de conciliación
            ingresado_por: Usuario que genera los tickets
            status: Estado inicial de los tickets
            comment: Comentario general para todos los tickets
            check_duplicates: Si verificar duplicados recientes
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            total_tickets_created = 0
            total_tickets_skipped = 0
            total_errors = []
            results_by_sid = {}
            
            for person_data in reconciliation_data_list:
                result = self.register_reconciliation_tickets(
                    person_data, ingresado_por, status, comment, check_duplicates
                )
                
                if result["success"]:
                    total_tickets_created += result["tickets_created"]
                    total_tickets_skipped += result["tickets_skipped"]
                    total_errors.extend(result.get("errors", []))
                    
                    if result.get("sid"):
                        results_by_sid[result["sid"]] = {
                            "tickets_created": result["tickets_created"],
                            "tickets_skipped": result["tickets_skipped"]
                        }
                else:
                    total_errors.append(result["error"])
            
            return {
                "success": True,
                "total_tickets_created": total_tickets_created,
                "total_tickets_skipped": total_tickets_skipped,
                "total_errors": total_errors,
                "results_by_sid": results_by_sid,
                "total_persons_processed": len(reconciliation_data_list)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error en registro masivo: {str(e)}",
                "total_tickets_created": 0,
                "total_tickets_skipped": 0
            }
    
    def _insert_access_history(self, 
                             sid: str,
                             app_name: str,
                             role_name: str,
                             tipo: str,
                             ingresado_por: str,
                             status: str,
                             comment: str) -> int:
        """
        Inserta un registro en la tabla access_history
        
        Args:
            sid: SID de la persona
            app_name: Nombre de la aplicación
            role_name: Nombre del rol
            tipo: Tipo de acceso (onboarding/offboarding)
            ingresado_por: Usuario que genera el ticket
            status: Estado del ticket
            comment: Comentario del ticket
            
        Returns:
            Número de filas insertadas
        """
        query = """
            INSERT INTO access_history 
            (sid, app_name, role_name, tipo, record_date, ingresado_por, status, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        record_date = datetime.now().isoformat()
        
        return execute_update(query, (
            sid, app_name, role_name, tipo, record_date, ingresado_por, status, comment
        ))
    
    def get_recent_tickets(self, 
                          sid: str = None, 
                          limit: int = 50,
                          hours_back: int = 24) -> List[Dict[str, Any]]:
        """
        Obtiene tickets recientes del historial
        
        Args:
            sid: SID específico o None para todos
            limit: Límite de registros a retornar
            hours_back: Horas hacia atrás para buscar
            
        Returns:
            Lista de tickets recientes
        """
        try:
            if sid:
                query = """
                    SELECT 
                        sid, app_name, role_name, tipo, record_date,
                        ingresado_por, status, comment
                    FROM access_history
                    WHERE sid = ? 
                      AND datetime(record_date) > datetime('now', '-{} hours')
                    ORDER BY record_date DESC
                    LIMIT ?
                """.format(hours_back)
                params = (sid, limit)
            else:
                query = """
                    SELECT 
                        sid, app_name, role_name, tipo, record_date,
                        ingresado_por, status, comment
                    FROM access_history
                    WHERE datetime(record_date) > datetime('now', '-{} hours')
                    ORDER BY record_date DESC
                    LIMIT ?
                """.format(hours_back)
                params = (limit,)
            
            results = execute_query(query, params)
            
            tickets = []
            for row in results:
                tickets.append({
                    "sid": row[0],
                    "app_name": row[1],
                    "role_name": row[2],
                    "tipo": row[3],
                    "record_date": row[4],
                    "ingresado_por": row[5],
                    "status": row[6],
                    "comment": row[7]
                })
            
            return tickets
            
        except Exception as e:
            print(f"Error obteniendo tickets recientes: {e}")
            return []
    
    def update_ticket_status(self, 
                           ticket_id: int, 
                           new_status: str, 
                           comment: str = None) -> bool:
        """
        Actualiza el estado de un ticket
        
        Args:
            ticket_id: ID del ticket a actualizar
            new_status: Nuevo estado
            comment: Comentario opcional
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            if comment:
                query = """
                    UPDATE access_history 
                    SET status = ?, comment = ?
                    WHERE id = ?
                """
                params = (new_status, comment, ticket_id)
            else:
                query = """
                    UPDATE access_history 
                    SET status = ?
                    WHERE id = ?
                """
                params = (new_status, ticket_id)
            
            rows_affected = execute_update(query, params)
            return rows_affected > 0
            
        except Exception as e:
            print(f"Error actualizando estado del ticket: {e}")
            return False
    
    def get_ticket_statistics(self, 
                            sid: str = None, 
                            days_back: int = 30) -> Dict[str, Any]:
        """
        Obtiene estadísticas de tickets
        
        Args:
            sid: SID específico o None para todos
            days_back: Días hacia atrás para buscar
            
        Returns:
            Dict con estadísticas de tickets
        """
        try:
            if sid:
                query = """
                    SELECT 
                        tipo,
                        status,
                        COUNT(*) as count
                    FROM access_history
                    WHERE sid = ? 
                      AND datetime(record_date) > datetime('now', '-{} days')
                    GROUP BY tipo, status
                """.format(days_back)
                params = (sid,)
            else:
                query = """
                    SELECT 
                        tipo,
                        status,
                        COUNT(*) as count
                    FROM access_history
                    WHERE datetime(record_date) > datetime('now', '-{} days')
                    GROUP BY tipo, status
                """.format(days_back)
                params = ()
            
            results = execute_query(query, params)
            
            stats = {
                "onboarding": {"total": 0, "by_status": {}},
                "offboarding": {"total": 0, "by_status": {}}
            }
            
            for row in results:
                tipo = row[0]
                status = row[1]
                count = row[2]
                
                if tipo in stats:
                    stats[tipo]["total"] += count
                    if status not in stats[tipo]["by_status"]:
                        stats[tipo]["by_status"][status] = 0
                    stats[tipo]["by_status"][status] += count
            
            return stats
            
        except Exception as e:
            print(f"Error obteniendo estadísticas de tickets: {e}")
            return {}


# Instancia global para usar en toda la aplicación
history_service = HistoryService()


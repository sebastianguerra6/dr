import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import List, Optional
from tkinter import messagebox
from services.dropdown_service import dropdown_service

class CamposGeneralesFrame:
    """Componente para los campos generales del empleado"""
    
    def __init__(self, parent):
        self.parent = parent
        self.variables = {}
        self.comboboxes = {}  # Para guardar referencias a los comboboxes
        self._crear_variables()
        self._crear_widgets()
    
    def _crear_variables(self):
        """Crea las variables de control"""
        self.variables = {
            'sid': tk.StringVar(),
            'nueva_unidad_subunidad': tk.StringVar(),
            'nuevo_cargo': tk.StringVar(),
            'request_date': tk.StringVar(value=datetime.now().strftime("%Y-%m-%d")),
            'ingreso_por': tk.StringVar(),
            'fecha': tk.StringVar(value=datetime.now().strftime("%Y-%m-%d")),
            'status': tk.StringVar(value="Pendiente")
        }
    
    def _crear_widgets(self):
        """Crea los widgets de la interfaz"""
        self.frame = ttk.LabelFrame(self.parent, text="Información de Gestión de Proyectos", padding="20")
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.columnconfigure(1, weight=1)  # Cambiar a weight=1 para que se expanda
        
        # Centrar el contenido
        main_container = ttk.Frame(self.frame)
        main_container.grid(row=0, column=1, sticky="ew", padx=20)  # Aumentar padx de 15 a 20
        main_container.columnconfigure(1, weight=1)
        
        # Obtener valores únicos de la base de datos
        dropdown_values = dropdown_service.get_all_dropdown_values()
        
        # Campos
        campos = [
            ("SID:", "sid", "entry"),
            ("Nueva Unidad/Subunidad:", "nueva_unidad_subunidad", "combobox", dropdown_values['unidad_subunidad']),
            ("Nuevo Cargo:", "nuevo_cargo", "combobox", dropdown_values['positions']),
            ("Request Date:", "request_date", "entry"),
            ("Quien hace el ingreso:", "ingreso_por", "combobox", ["Juan Pérez", "María García"]),
            ("Fecha:", "fecha", "entry"),
            ("Status:", "status", "combobox", ["cancelled", "closed completed", "closed incompleted", "in progress", "in validation", "to validate"])
        ]
        
        for i, campo in enumerate(campos):
            label_text, var_name, tipo = campo[:3]
            ttk.Label(main_container, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=5, padx=(0, 15))
            
            if tipo == "entry":
                ttk.Entry(main_container, textvariable=self.variables[var_name], width=50).grid(
                    row=i, column=1, sticky=(tk.W, tk.E), pady=5
                )
            elif tipo == "combobox":
                valores = campo[3] if len(campo) > 3 else []
                combobox = ttk.Combobox(main_container, textvariable=self.variables[var_name], 
                            values=valores, width=47)
                combobox.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5)
                # Guardar referencia al combobox
                self.comboboxes[var_name] = combobox
        
        # Información del número de caso (solo informativo)
        info_frame = ttk.Frame(main_container)
        info_frame.grid(row=len(campos), column=0, columnspan=2, pady=(15, 0), sticky="ew")
        
        ttk.Label(info_frame, text="Nota: El número de caso se generará automáticamente al guardar", 
                  style="Normal.TLabel", foreground="gray").pack(anchor=tk.CENTER)
    
    def obtener_datos(self):
        """Obtiene los datos de los campos"""
        return {name: var.get() for name, var in self.variables.items()}
    
    def limpiar(self):
        """Limpia todos los campos"""
        for var in self.variables.values():
            var.set("")
        self.variables['request_date'].set(datetime.now().strftime("%Y-%m-%d"))
        self.variables['fecha'].set(datetime.now().strftime("%Y-%m-%d"))
        self.variables['status'].set("Pendiente")
    
    def validar_campos_obligatorios(self):
        """Valida que los campos obligatorios estén completos"""
        campos_obligatorios = ['sid', 'nueva_unidad_subunidad', 'nuevo_cargo', 'status']
        campos_vacios = []
        
        for campo in campos_obligatorios:
            if not self.variables[campo].get().strip():
                campos_vacios.append(campo)
        
        return campos_vacios
    
    def actualizar_desplegables(self):
        """Actualiza los valores de los desplegables desde la base de datos"""
        try:
            # Obtener valores actualizados de la base de datos
            from services.dropdown_service import dropdown_service
            dropdown_values = dropdown_service.get_all_dropdown_values()
            
            # Actualizar los comboboxes específicos
            if 'nueva_unidad_subunidad' in self.comboboxes:
                self.comboboxes['nueva_unidad_subunidad']['values'] = dropdown_values.get('unidad_subunidad', [])
            
            if 'nuevo_cargo' in self.comboboxes:
                self.comboboxes['nuevo_cargo']['values'] = dropdown_values.get('positions', [])
            
            print("Desplegables actualizados en CamposGeneralesFrame")
            
        except Exception as e:
            print(f"Error actualizando desplegables en CamposGeneralesFrame: {e}")

class OnboardingFrame:
    """Componente para la pestaña de onboarding"""
    
    def __init__(self, parent):
        self.parent = parent
        self.variables = {}
        self._crear_variables()
        self._crear_widgets()
    
    def _crear_variables(self):
        """Crea las variables de control"""
        self.variables = {
            'submenu_onboarding': tk.StringVar(),
            'other_onboarding': tk.StringVar()
        }
    
    def _crear_widgets(self):
        """Crea los widgets de la interfaz"""
        self.frame = ttk.Frame(self.parent)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        # Centrar el contenido
        main_container = ttk.Frame(self.frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)  # Aumentar padx de 15 a 20
        main_container.columnconfigure(0, weight=1)
        
        # Título
        ttk.Label(main_container, text="Tipo de Onboarding", 
                  style="Section.TLabel").pack(pady=(0, 20))
        
        # Frame para radio buttons
        radio_frame = ttk.Frame(main_container)
        radio_frame.pack(fill=tk.BOTH, expand=True)
        
        # Submenú con radio buttons
        opciones_submenu = ["Nuevo Empleado", "Recontratación", "Transferencia Interna", "Promoción"]
        for i, opcion in enumerate(opciones_submenu):
            ttk.Radiobutton(radio_frame, text=opcion, 
                           variable=self.variables['submenu_onboarding'], 
                           value=opcion).pack(anchor=tk.CENTER, pady=8)
        
        # Opción Other con campo de texto
        other_frame = ttk.Frame(radio_frame)
        other_frame.pack(anchor=tk.CENTER, pady=8)
        
        ttk.Radiobutton(other_frame, text="Other:", 
                       variable=self.variables['submenu_onboarding'], 
                       value="other").pack(side=tk.LEFT)
        
        ttk.Entry(other_frame, textvariable=self.variables['other_onboarding'], 
                 width=35).pack(side=tk.LEFT, padx=(5, 0))  # Aumentar width de 30 a 35
    
    def obtener_datos(self):
        """Obtiene los datos de los campos"""
        datos = {name: var.get() for name, var in self.variables.items()}
        
        # Si se seleccionó "other", usar el valor del campo de texto
        if datos['submenu_onboarding'] == 'other':
            datos['submenu_onboarding'] = datos['other_onboarding']
        
        return datos
    
    def limpiar(self):
        """Limpia todos los campos"""
        for var in self.variables.values():
            var.set("")

class OffboardingFrame:
    """Componente para la pestaña de offboarding"""
    
    def __init__(self, parent):
        self.parent = parent
        self.variables = {}
        self._crear_variables()
        self._crear_widgets()
    
    def _crear_variables(self):
        """Crea las variables de control"""
        self.variables = {
            'submenu_offboarding': tk.StringVar(),
            'other_offboarding': tk.StringVar()
        }
    
    def _crear_widgets(self):
        """Crea los widgets de la interfaz"""
        self.frame = ttk.Frame(self.parent)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        # Centrar el contenido
        main_container = ttk.Frame(self.frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)  # Aumentar padx de 15 a 20
        main_container.columnconfigure(0, weight=1)
        
        # Título
        ttk.Label(main_container, text="Tipo de Offboarding", 
                  style="Section.TLabel").pack(pady=(0, 20))
        
        # Frame para radio buttons
        radio_frame = ttk.Frame(main_container)
        radio_frame.pack(fill=tk.BOTH, expand=True)
        
        # Submenú con radio buttons
        opciones_submenu = ["Salida Definitiva", "Reducción de Personal", "Fin de Proyecto", "Cambio de Empresa"]
        for i, opcion in enumerate(opciones_submenu):
            ttk.Radiobutton(radio_frame, text=opcion, 
                           variable=self.variables['submenu_offboarding'], 
                           value=opcion).pack(anchor=tk.CENTER, pady=8)
        
        # Opción Other con campo de texto
        other_frame = ttk.Frame(radio_frame)
        other_frame.pack(anchor=tk.CENTER, pady=8)
        
        ttk.Radiobutton(other_frame, text="Other:", 
                       variable=self.variables['submenu_offboarding'], 
                       value="other").pack(side=tk.LEFT)
        
        ttk.Entry(other_frame, textvariable=self.variables['other_offboarding'], 
                 width=35).pack(side=tk.LEFT, padx=(5, 0))  # Aumentar width de 30 a 35
    
    def obtener_datos(self):
        """Obtiene los datos de los campos"""
        datos = {name: var.get() for name, var in self.variables.items()}
        
        # Si se seleccionó "other", usar el valor del campo de texto
        if datos['submenu_offboarding'] == 'other':
            datos['submenu_offboarding'] = datos['other_offboarding']
        
        return datos
    
    def limpiar(self):
        """Limpia todos los campos"""
        for var in self.variables.values():
            var.set("")

class LateralMovementFrame:
    """Componente para la pestaña de lateral movement"""
    
    def __init__(self, parent):
        self.parent = parent
        self.variables = {}
        self._crear_variables()
        self._crear_widgets()
    
    def _crear_variables(self):
        """Crea las variables de control"""
        self.variables = {
            'submenu_lateral': tk.StringVar(),
            'other_lateral': tk.StringVar()
        }
    
    def _crear_widgets(self):
        """Crea los widgets de la interfaz"""
        self.frame = ttk.Frame(self.parent)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        # Centrar el contenido
        main_container = ttk.Frame(self.frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)  # Aumentar padx de 15 a 20
        main_container.columnconfigure(1, weight=1)
        
        # Título
        ttk.Label(main_container, text="Información de Lateral Movement", 
                  style="Section.TLabel").pack(pady=(0, 20))
        
        # Frame para campos
        campos_frame = ttk.Frame(main_container)
        campos_frame.pack(fill=tk.BOTH, expand=True)
        campos_frame.columnconfigure(1, weight=1)
        
        # Título para radio buttons
        ttk.Label(campos_frame, text="Tipo de Movimiento:", style="Subsection.TLabel").grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Submenú con radio buttons
        opciones_submenu = ["Movimiento Horizontal", "Reasignación de Proyecto", "Cambio de Equipo", "Rotación de Funciones"]
        for i, opcion in enumerate(opciones_submenu):
            ttk.Radiobutton(campos_frame, text=opcion, 
                           variable=self.variables['submenu_lateral'], 
                           value=opcion).grid(row=1+i, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Opción Other con campo de texto
        other_row = 1 + len(opciones_submenu)
        other_frame = ttk.Frame(campos_frame)
        other_frame.grid(row=other_row, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Radiobutton(other_frame, text="Other:", 
                       variable=self.variables['submenu_lateral'], 
                       value="other").pack(side=tk.LEFT)
        
        ttk.Entry(other_frame, textvariable=self.variables['other_lateral'], 
                 width=35).pack(side=tk.LEFT, padx=(5, 0))  # Aumentar width de 30 a 35
    
    def obtener_datos(self):
        """Obtiene los datos de los campos"""
        datos = {name: var.get() for name, var in self.variables.items()}
        
        # Si se seleccionó "other", usar el valor del campo de texto
        if datos['submenu_lateral'] == 'other':
            datos['submenu_lateral'] = datos['other_lateral']
        
        return datos
    
    def limpiar(self):
        """Limpia todos los campos"""
        for var in self.variables.values():
            var.set("")

class FlexStaffFrame:
    """Componente para la pestaña de flex staff"""
    
    def __init__(self, parent):
        self.parent = parent
        self.variables = {}
        self._crear_variables()
        self._crear_widgets()
    
    def _crear_variables(self):
        """Crea las variables de control"""
        self.variables = {
            'tipo_flex_staff': tk.StringVar(),
            'duracion_dias': tk.StringVar(),
            'otro_tipo': tk.StringVar()
        }
    
    def _crear_widgets(self):
        """Crea los widgets de la interfaz"""
        self.frame = ttk.Frame(self.parent)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        # Centrar el contenido
        main_container = ttk.Frame(self.frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_container.columnconfigure(1, weight=1)
        
        # Título
        ttk.Label(main_container, text="Información de Flex Staff", 
                  style="Section.TLabel").pack(pady=(0, 20))
        
        # Frame para campos
        campos_frame = ttk.Frame(main_container)
        campos_frame.pack(fill=tk.BOTH, expand=True)
        campos_frame.columnconfigure(1, weight=1)
        
        # Tipo de flex staff
        ttk.Label(campos_frame, text="Tipo de Asignación:", style="Subsection.TLabel").grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        opciones_flex = ["Apoyo Temporal", "Proyecto Específico", "Cobertura de Vacaciones", "Capacitación Cruzada"]
        for i, opcion in enumerate(opciones_flex):
            ttk.Radiobutton(campos_frame, text=opcion, 
                           variable=self.variables['tipo_flex_staff'], 
                           value=opcion).grid(row=1+i, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Opción Other
        other_row = 1 + len(opciones_flex)
        other_frame = ttk.Frame(campos_frame)
        other_frame.grid(row=other_row, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Radiobutton(other_frame, text="Other:", 
                       variable=self.variables['tipo_flex_staff'], 
                       value="other").pack(side=tk.LEFT)
        
        ttk.Entry(other_frame, textvariable=self.variables['otro_tipo'], 
                 width=30).pack(side=tk.LEFT, padx=(5, 0))
        
        # Duración
        duracion_row = other_row + 1
        ttk.Label(campos_frame, text="Duración (días):", style="Subsection.TLabel").grid(
            row=duracion_row, column=0, sticky=tk.W, pady=(20, 5))
        
        duracion_entry = ttk.Entry(campos_frame, textvariable=self.variables['duracion_dias'], 
                                  width=10)
        duracion_entry.grid(row=duracion_row, column=1, sticky=tk.W, pady=(20, 5))
        
        # Información adicional
        info_row = duracion_row + 1
        info_text = ("Nota: Flex Staff mantiene accesos de su posición original\n"
                    "y recibe accesos adicionales de la posición temporal.")
        ttk.Label(campos_frame, text=info_text, style="Info.TLabel").grid(
            row=info_row, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def obtener_datos(self):
        """Obtiene los datos de los campos"""
        datos = {name: var.get() for name, var in self.variables.items()}
        
        # Si se seleccionó "other", usar el valor del campo de texto
        if datos['tipo_flex_staff'] == 'other':
            datos['tipo_flex_staff'] = datos['otro_tipo']
        
        # Convertir duración a entero si es posible
        try:
            datos['duracion_dias'] = int(datos['duracion_dias']) if datos['duracion_dias'] else None
        except ValueError:
            datos['duracion_dias'] = None
        
        return datos
    
    def limpiar(self):
        """Limpia todos los campos"""
        for var in self.variables.values():
            var.set("")

class EdicionBusquedaFrame:
    """Componente para la pestaña de edición y búsqueda de registros"""
    
    def __init__(self, parent, service=None):
        self.parent = parent
        self.service = service
        self.variables = {}
        self.registros_encontrados = []
        self._crear_variables()
        self._crear_widgets()
    
    def _crear_variables(self):
        """Crea las variables de control"""
        self.variables = {
            # Variables de búsqueda
            'numero_caso_busqueda': tk.StringVar(),
            'filtro_texto': tk.StringVar(),
            'columna_filtro': tk.StringVar(value="SID"),
            
            # Variables de edición - Todos los campos de la tabla historico
            'id_edicion': tk.StringVar(),
            'scotia_id_edicion': tk.StringVar(),
            'case_id_edicion': tk.StringVar(),
            'responsible_edicion': tk.StringVar(),
            'record_date_edicion': tk.StringVar(),
            'request_date_edicion': tk.StringVar(),
            'process_access_edicion': tk.StringVar(),
            'subunit_edicion': tk.StringVar(),
            'event_description_edicion': tk.StringVar(),
            'ticket_email_edicion': tk.StringVar(),
            'app_access_name_edicion': tk.StringVar(),
            'computer_system_type_edicion': tk.StringVar(),
            'duration_of_access_edicion': tk.StringVar(),
            'status_edicion': tk.StringVar(),
            'closing_date_app_edicion': tk.StringVar(),
            'closing_date_ticket_edicion': tk.StringVar(),
            'app_quality_edicion': tk.StringVar(),
            'confirmation_by_user_edicion': tk.StringVar(),
            'comment_edicion': tk.StringVar(),
            'comment_tq_edicion': tk.StringVar(),
            'ticket_quality_edicion': tk.StringVar(),
            'general_status_ticket_edicion': tk.StringVar(),
            'general_status_case_edicion': tk.StringVar(),
            'average_time_open_ticket_edicion': tk.StringVar(),
            'sla_app_edicion': tk.StringVar(),
            'sla_ticket_edicion': tk.StringVar(),
            'sla_case_edicion': tk.StringVar()
        }
        
        # Variables para filtros múltiples
        self.filtros_activos = {}
        self.campos_filtro = {
            "SID": "scotia_id",
            "Número de Caso": "case_id", 
            "Proceso": "process_access",
            "Aplicación": "app_access_name",
            "Estado": "status",
            "Request Date": "request_date",
            "Responsable": "responsible",
            "Subunidad": "subunit",
            "Email Ticket": "ticket_email",
            "Email Empleado": "employee_email",
            "Descripción": "event_description",
            "Calidad App": "app_quality",
            "Confirmación": "confirmation_by_user",
            "Comentario": "comment"
        }
    
    def _crear_widgets(self):
        """Crea los widgets de la interfaz simplificada"""
        self.frame = ttk.Frame(self.parent)
        
        # Configurar grid del frame principal
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
        # Título
        ttk.Label(self.frame, text="🔍 Edición y Búsqueda - Historial de Procesos", 
                  style="Title.TLabel").grid(row=0, column=0, pady=20, sticky="ew")
        
        # Frame principal simplificado
        main_frame = ttk.Frame(self.frame)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # Fila 2 para la tabla
        
        # Barra de herramientas (fuera del LabelFrame, igual que en Aplicaciones)
        toolbar = ttk.Frame(main_frame)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Botones principales
        ttk.Button(toolbar, text="✏️ Editar Registro", command=self.editar_registro_historial, 
                  style="Info.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="🗑️ Eliminar", command=self.eliminar_registro, 
                  style="Danger.TButton").pack(side=tk.LEFT, padx=(0, 10))
        
        # Separador
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Botones de estadísticas
        ttk.Button(toolbar, text="📊 Ver Estadísticas", command=self.mostrar_estadisticas, 
                  style="Success.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="📤 Exportar Excel", command=self.exportar_estadisticas, 
                  style="Warning.TButton").pack(side=tk.LEFT, padx=(0, 10))
        
        # Separador
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Botón para crear registro manual
        ttk.Button(toolbar, text="➕ Registro Manual", command=self.crear_registro_manual, 
                  style="Info.TButton").pack(side=tk.LEFT, padx=(0, 10))
        
        # Separador
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Botones de actualizar y mostrar todos
        ttk.Button(toolbar, text="🔄 Actualizar", command=self.actualizar_tabla).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="📋 Mostrar Todo el Historial", 
                  command=self.mostrar_todo_el_historial).pack(side=tk.LEFT, padx=(0, 10))
        
        # Panel de filtros múltiples
        self._crear_panel_filtros(main_frame)
        
        # Tabla de resultados - Actualizada para mostrar historial
        resultados_frame = ttk.Frame(main_frame)
        resultados_frame.grid(row=2, column=0, sticky="nsew", pady=(15, 0))
        
        # Crear Treeview para mostrar resultados del historial con más campos
        self.tree = ttk.Treeview(resultados_frame, columns=("ID", "SID", "Email", "Caso", "Proceso", "Aplicación", "Estado", "Fecha", "Fecha Solicitud", "Responsable", "Subunidad", "Tipo Sistema", "Duración", "Cierre App", "Cierre Ticket", "Calidad App", "Confirmación", "Comentario"), 
                                show="headings", height=12)
        
        # Configurar columnas
        self.tree.heading("ID", text="ID")
        self.tree.heading("SID", text="SID")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Caso", text="Caso")
        self.tree.heading("Proceso", text="Proceso")
        self.tree.heading("Aplicación", text="Aplicación")
        self.tree.heading("Estado", text="Estado")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Fecha Solicitud", text="Fecha Solicitud")
        self.tree.heading("Responsable", text="Responsable")
        self.tree.heading("Subunidad", text="Subunidad")
        self.tree.heading("Tipo Sistema", text="Tipo Sistema")
        self.tree.heading("Duración", text="Duración")
        self.tree.heading("Cierre App", text="Cierre App")
        self.tree.heading("Cierre Ticket", text="Cierre Ticket")
        self.tree.heading("Calidad App", text="Calidad App")
        self.tree.heading("Confirmación", text="Confirmación")
        self.tree.heading("Comentario", text="Comentario")
        
        # Configurar anchos de columna con minwidth
        self.tree.column("ID", width=50, minwidth=40)
        self.tree.column("SID", width=100, minwidth=80)
        self.tree.column("Email", width=200, minwidth=150)
        self.tree.column("Caso", width=120, minwidth=100)
        self.tree.column("Proceso", width=120, minwidth=100)
        self.tree.column("Aplicación", width=150, minwidth=120)
        self.tree.column("Estado", width=100, minwidth=80)
        self.tree.column("Fecha", width=120, minwidth=100)
        self.tree.column("Fecha Solicitud", width=120, minwidth=100)
        self.tree.column("Responsable", width=120, minwidth=100)
        self.tree.column("Subunidad", width=120, minwidth=100)
        self.tree.column("Tipo Sistema", width=120, minwidth=100)
        self.tree.column("Duración", width=100, minwidth=80)
        self.tree.column("Cierre App", width=100, minwidth=80)
        self.tree.column("Cierre Ticket", width=100, minwidth=80)
        self.tree.column("Calidad App", width=100, minwidth=80)
        self.tree.column("Confirmación", width=100, minwidth=80)
        self.tree.column("Comentario", width=200, minwidth=150)
        
        # Scrollbars (vertical y horizontal)
        vsb = ttk.Scrollbar(resultados_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(resultados_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Empaquetar tabla y scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Configurar grid para que la tabla se expanda
        resultados_frame.columnconfigure(0, weight=1)
        resultados_frame.rowconfigure(0, weight=1)
        
        # Eventos de la tabla
        self.tree.bind('<Double-1>', self._on_doble_clic)
        self.tree.bind('<Delete>', lambda e: self.eliminar_registro())
        
        # Inicializar filtro delay
        self.filtro_delay_id = None
    
    def _on_doble_clic(self, event):
        """Maneja el doble clic en la tabla"""
        self.editar_registro_historial()
    
    def actualizar_tabla(self):
        """Actualiza la tabla con todos los registros del historial"""
        try:
            # Limpiar tabla primero
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Obtener todos los registros del historial
            self.mostrar_todo_el_historial()
            
            # Mostrar mensaje de confirmación
            messagebox.showinfo("Actualización", "Tabla actualizada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando tabla: {str(e)}")
    
    
    def editar_registro_historial(self):
        """Edita el registro del historial seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un registro para editar")
            return
        
        try:
            # Obtener el registro seleccionado
            item = selection[0]
            values = self.tree.item(item, 'values')
            
            # Ahora los valores son: ID, SID, Caso, Proceso, Aplicación, Estado, Fecha, Fecha Solicitud, Responsable, Subunidad, Tipo Sistema, Duración, Cierre App, Cierre Ticket, Calidad App, Confirmación, Comentario
            record_id = values[0]  # ID
            scotia_id = values[1]  # SID
            case_id = values[2]    # Caso
            process_access = values[3]  # Proceso
            app_access_name = values[4]  # Aplicación
            
            # Buscar los datos completos del registro del historial
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
            from access_management_service import access_service
            
            # Obtener el registro completo del historial usando una combinación de campos
            conn = access_service.get_connection()
            cursor = conn.cursor()
            
            # Debug: imprimir los valores que estamos buscando
            print(f"DEBUG: Buscando registro con ID: {record_id}")
            
            cursor.execute('''
                SELECT * FROM historico 
                WHERE id = ?
            ''', (record_id,))
            row = cursor.fetchone()
            
            # Debug: imprimir si se encontró algo
            print(f"DEBUG: Registro encontrado: {row is not None}")
            
            if not row:
                conn.close()
                messagebox.showerror("Error", f"No se encontró el registro del historial con ID: {record_id}")
                return
            
            # Convertir a diccionario
            columns = [description[0] for description in cursor.description]
            historial_data = dict(zip(columns, row))
            conn.close()
            
            print(f"DEBUG: Datos del historial: {historial_data}")
            
            # Crear diálogo de edición del historial
            dialog = HistorialDialog(self.parent, f"Editar Registro de Historial - SID: {scotia_id}", historial_data)
            self.parent.wait_window(dialog.dialog)
            
            if dialog.result:
                success, message = self.actualizar_registro_historial_por_id(record_id, dialog.result)
                
                if success:
                    messagebox.showinfo("Éxito", message)
                    # Actualizar la tabla después de editar
                    self.actualizar_tabla()
                else:
                    messagebox.showerror("Error", message)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error editando registro: {str(e)}")
            print(f"Error en editar_registro_historial: {e}")
    
    def actualizar_registro_historial_por_id(self, record_id, data):
        """Actualiza un registro del historial usando el ID como identificador"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
            from access_management_service import access_service
            
            conn = access_service.get_connection()
            cursor = conn.cursor()
            
            # Obtener el scotia_id del registro para obtener el email del headcount
            cursor.execute('SELECT scotia_id FROM historico WHERE id = ?', (record_id,))
            scotia_id_result = cursor.fetchone()
            if scotia_id_result:
                scotia_id = scotia_id_result[0]
                # Obtener el email del empleado desde headcount
                cursor.execute('SELECT email FROM headcount WHERE scotia_id = ?', (scotia_id,))
                email_result = cursor.fetchone()
                if email_result:
                    data['employee_email'] = email_result[0]
            
            # Construir query de actualización
            set_clauses = []
            params = []
            
            for campo, valor in data.items():
                if campo != 'id':  # No actualizar el ID
                    set_clauses.append(f"{campo} = ?")
                    params.append(valor)
            
            if not set_clauses:
                return False, "No hay datos para actualizar"
            
            # Agregar el ID al WHERE
            params.append(record_id)
            
            query = f"UPDATE historico SET {', '.join(set_clauses)} WHERE id = ?"
            
            print(f"DEBUG: Query de actualización: {query}")
            print(f"DEBUG: Parámetros: {params}")
            
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            
            return True, "Registro actualizado exitosamente"
            
        except Exception as e:
            print(f"Error en actualizar_registro_historial_por_id: {e}")
            return False, f"Error actualizando registro: {str(e)}"
    
    def actualizar_registro_historial_por_campos(self, scotia_id, case_id, process_access, app_access_name, data):
        """Actualiza un registro del historial usando una combinación de campos para identificarlo"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
            from access_management_service import access_service
            
            conn = access_service.get_connection()
            cursor = conn.cursor()
            
            # Obtener el email del empleado desde headcount
            cursor.execute('SELECT email FROM headcount WHERE scotia_id = ?', (scotia_id,))
            email_result = cursor.fetchone()
            if email_result:
                data['employee_email'] = email_result[0]
            
            # Construir query de actualización
            set_clauses = []
            params = []
            
            for campo, valor in data.items():
                if campo not in ['scotia_id', 'case_id', 'process_access', 'app_access_name']:  # No actualizar los campos de identificación
                    set_clauses.append(f"{campo} = ?")
                    params.append(valor)
            
            if not set_clauses:
                return False, "No hay datos para actualizar"
            
            # Agregar los campos de identificación al WHERE
            where_clause = "scotia_id = ? AND case_id = ? AND process_access = ? AND app_access_name = ?"
            params.extend([scotia_id, case_id, process_access, app_access_name])
            
            query = f"UPDATE historico SET {', '.join(set_clauses)} WHERE {where_clause}"
            
            print(f"DEBUG: Query de actualización: {query}")
            print(f"DEBUG: Parámetros: {params}")
            
            cursor.execute(query, params)
            
            if cursor.rowcount == 0:
                conn.close()
                return False, f"Registro con SID {scotia_id}, Caso {case_id} no encontrado"
            
            conn.commit()
            conn.close()
            
            return True, f"Registro actualizado exitosamente"
            
        except Exception as e:
            return False, f"Error actualizando registro: {str(e)}"
    
    def eliminar_registro(self):
        """Elimina el registro seleccionado del historial"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un registro para eliminar")
            return
        
        if not self.service:
            messagebox.showerror("Error", "Servicio no disponible")
            return
        
        # Obtener datos del registro seleccionado
        items = selection
        if not items:
            messagebox.showwarning("Advertencia", "Seleccione al menos un registro para eliminar")
            return
        
        # Si hay más de uno seleccionado, preguntar si eliminar múltiples
        if len(items) > 1:
            confirm = messagebox.askyesno(
                "Eliminar múltiples registros",
                f"Se eliminarán {len(items)} registros individuales.\n\n¿Desea continuar?"
            )
            if not confirm:
                return
            
            errores = []
            eliminados = 0
            for item_id in items:
                values = self.tree.item(item_id)['values']
                if len(values) < 6:
                    continue
                record_id = values[0]
                scotia_id = values[1]
                case_id = values[3]
                app_name = values[5]
                
                success, message = self._eliminar_registro_historico(scotia_id, case_id, app_name)
                if success:
                    eliminados += 1
                else:
                    errores.append(f"SID {scotia_id}, Caso {case_id}: {message}")
            
            if eliminados:
                messagebox.showinfo("Éxito", f"Se eliminaron {eliminados} registros.")
                self.mostrar_todo_el_historial()
            if errores:
                messagebox.showerror("Errores", "\n".join(errores))
            return
        
        # Solo un registro seleccionado
        item = self.tree.item(selection[0])
        values = item['values']
        if len(values) < 6:
            messagebox.showerror("Error", "Datos de registro no válidos")
            return
        
        record_id = values[0]
        scotia_id = values[1]
        case_id = values[3]
        app_name = values[5]
        
        # Preguntar si eliminar todos los registros del caso
        if messagebox.askyesno(
            "Eliminar registros del caso",
            f"¿Desea eliminar TODOS los registros del caso {case_id}?\n\n"
            "Seleccione 'No' para eliminar solo este registro."
        ):
            self._eliminar_registros_caso(scotia_id, case_id)
            return
        
        # Confirmar eliminación individual
        result = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Eliminar registro?\n\n"
            f"SID: {scotia_id}\n"
            f"Caso: {case_id}\n"
            f"Aplicación: {app_name}"
        )
        
        if not result:
            return
        
        success, message = self._eliminar_registro_historico(scotia_id, case_id, app_name, delete_all=False)
        if success:
            messagebox.showinfo("Éxito", "Registro eliminado.")
            self.mostrar_todo_el_historial()
        else:
            messagebox.showerror("Error", message)
    
    def _eliminar_registro_historico(self, scotia_id, case_id, app_name=None, delete_all=False):
        """Elimina un registro específico del historial"""
        try:
            if not self.service:
                return False, "Servicio no disponible"
            
            # Usar el servicio para eliminar el registro específico
            success = self.service.delete_historical_record(scotia_id, case_id, app_name, delete_all=delete_all)
            
            if success:
                return True, "Registro eliminado exitosamente"
            else:
                detalle = f"SID={scotia_id}, Caso={case_id}"
                if app_name:
                    detalle += f", App={app_name}"
                return False, f"No se pudo eliminar el registro ({detalle}). Revisa los mensajes DEBUG en consola."
            
        except Exception as e:
            return False, f"Error eliminando registro: {str(e)}"

    def _eliminar_registros_caso(self, scotia_id: str, case_id: str):
        """Elimina todos los registros de un caso."""
        confirm = messagebox.askyesno(
            "Eliminar caso completo",
            f"Se eliminarán todos los registros del caso {case_id} (SID {scotia_id}). ¿Continuar?"
        )
        if not confirm:
            return

        success, message = self._eliminar_registro_historico(scotia_id, case_id, app_name=None, delete_all=True)
        if success:
            messagebox.showinfo("Éxito", f"Se eliminaron todos los registros del caso {case_id}.")
            self.mostrar_todo_el_historial()
        else:
            messagebox.showerror("Error", message)
    
    def mostrar_resultados_busqueda(self, resultados, busqueda=""):
        """Muestra los resultados de búsqueda en la tabla"""
        # Limpiar tabla anterior
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if resultados:
            for i, resultado in enumerate(resultados):
                if i < 2:  # Debug para los primeros 2 registros
                    print(f"DEBUG: Insertando registro {i}:")
                    print(f"  scotia_id: {resultado.get('scotia_id', '')}")
                    print(f"  employee: {resultado.get('employee', '')}")
                    print(f"  unit: {resultado.get('unit', '')}")
                    print(f"  position: {resultado.get('position', '')}")
                    print(f"  activo: {resultado.get('activo', True)}")
                    print(f"  start_date: {resultado.get('start_date', '')}")
                    print(f"  email: {resultado.get('email', '')}")
                
                # Mapear los campos correctos de la base de datos headcount
                # Separar nombre y apellido del full_name
                full_name = resultado.get('full_name', '')
                nombre_parts = full_name.split(' ', 1)
                nombre = nombre_parts[0] if nombre_parts else ''
                apellido = nombre_parts[1] if len(nombre_parts) > 1 else ''
                
                values = (
                    resultado.get('scotia_id', ''),  # SID
                    nombre,                          # Nombre
                    apellido,                        # Apellido
                    resultado.get('email', ''),      # Email
                    resultado.get('unit', ''),       # Departamento
                    resultado.get('unidad_subunidad', ''),  # Unidad/Subunidad
                    resultado.get('position', ''),   # Cargo
                    'Active' if resultado.get('activo', True) else 'Inactive'  # Estado
                )
                
                if i < 2:  # Debug para los primeros 2 registros
                    print(f"  Valores a insertar: {values}")
                
                self.tree.insert("", "end", values=values)
        else:
            messagebox.showinfo("Búsqueda", "No se encontraron registros")
    
    def buscar_por_numero_caso(self):
        """Busca registros por número de caso usando la base de datos"""
        numero_caso = self.variables['numero_caso_busqueda'].get().strip()
        if not numero_caso:
            messagebox.showwarning("Advertencia", "Por favor ingrese un número de caso para buscar")
            return
        
        try:
            if self.service and hasattr(self.service, 'buscar_procesos'):
                # Buscar en la base de datos
                filtros = {'numero_caso': numero_caso}
                resultados = self.service.buscar_procesos(filtros)
                self.mostrar_resultados_busqueda(resultados, f"número de caso: {numero_caso}")
            else:
                messagebox.showerror("Error", "Servicio no disponible para búsqueda")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")
            print(f"Error en buscar_por_numero_caso: {e}")
    
    def _crear_panel_filtros(self, parent):
        """Crea el panel de filtros múltiples"""
        # Frame para filtros
        filtros_frame = ttk.LabelFrame(parent, text="Filtros Múltiples", padding="10")
        filtros_frame.grid(row=1, column=0, sticky="ew", pady=(15, 0))
        filtros_frame.columnconfigure(1, weight=1)
        
        # Lista de filtros activos
        ttk.Label(filtros_frame, text="Filtros Activos:").grid(row=0, column=0, sticky="w", pady=5)
        self.filtros_listbox = tk.Listbox(filtros_frame, height=3)
        self.filtros_listbox.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        # Scrollbar para la lista
        scrollbar_filtros = ttk.Scrollbar(filtros_frame, orient="vertical", command=self.filtros_listbox.yview)
        scrollbar_filtros.grid(row=0, column=2, sticky="ns")
        self.filtros_listbox.configure(yscrollcommand=scrollbar_filtros.set)
        
        # Botones para gestionar filtros
        botones_filtros = ttk.Frame(filtros_frame)
        botones_filtros.grid(row=0, column=3, padx=(5, 0), pady=5)
        
        ttk.Button(botones_filtros, text="Eliminar", command=self._eliminar_filtro_seleccionado).pack(side=tk.TOP, pady=2)
        ttk.Button(botones_filtros, text="Limpiar", command=self._limpiar_todos_filtros).pack(side=tk.TOP, pady=2)
        
        # Frame para agregar nuevo filtro
        nuevo_filtro_frame = ttk.Frame(filtros_frame)
        nuevo_filtro_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        nuevo_filtro_frame.columnconfigure(1, weight=1)
        
        # Campo de texto para el valor del filtro
        ttk.Label(nuevo_filtro_frame, text="Valor:").grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
        self.entry_filtro = ttk.Entry(nuevo_filtro_frame, width=30)
        self.entry_filtro.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)
        
        # Combo para seleccionar campo
        ttk.Label(nuevo_filtro_frame, text="Campo:").grid(row=0, column=2, padx=(0, 5), pady=5, sticky="w")
        self.combo_campo = ttk.Combobox(nuevo_filtro_frame, values=list(self.campos_filtro.keys()), width=15)
        self.combo_campo.grid(row=0, column=3, padx=(0, 10), pady=5)
        
        # Botón para agregar filtro
        ttk.Button(nuevo_filtro_frame, text="Agregar Filtro", command=self._agregar_filtro).grid(row=0, column=4, padx=(0, 5), pady=5)
        
        # Botones de acción
        botones_accion = ttk.Frame(filtros_frame)
        botones_accion.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        
        ttk.Button(botones_accion, text="Aplicar Filtros", command=self._aplicar_filtros_multiples).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(botones_accion, text="Mostrar Todos", command=self.mostrar_todo_el_historial).pack(side=tk.LEFT)
        
        # Bind para Enter en el campo de texto
        self.entry_filtro.bind('<Return>', lambda e: self._agregar_filtro())
    
    def _agregar_filtro(self):
        """Agrega un nuevo filtro a la lista"""
        valor = self.entry_filtro.get().strip()
        campo = self.combo_campo.get()
        
        if not valor:
            messagebox.showwarning("Advertencia", "Por favor ingrese un valor para el filtro")
            return
        
        if not campo:
            messagebox.showwarning("Advertencia", "Por favor seleccione un campo para filtrar")
            return
        
        # Agregar filtro al diccionario
        campo_bd = self.campos_filtro.get(campo)
        if campo_bd:
            self.filtros_activos[campo] = valor
            self._actualizar_lista_filtros()
            
            # Limpiar campos
            self.entry_filtro.delete(0, tk.END)
            self.combo_campo.set("")
    
    def _eliminar_filtro_seleccionado(self):
        """Elimina el filtro seleccionado de la lista"""
        seleccion = self.filtros_listbox.curselection()
        if seleccion:
            indice = seleccion[0]
            campo = list(self.filtros_activos.keys())[indice]
            del self.filtros_activos[campo]
            self._actualizar_lista_filtros()
    
    def _limpiar_todos_filtros(self):
        """Limpia todos los filtros activos"""
        self.filtros_activos.clear()
        self._actualizar_lista_filtros()
    
    def _actualizar_lista_filtros(self):
        """Actualiza la lista visual de filtros activos"""
        self.filtros_listbox.delete(0, tk.END)
        for campo, valor in self.filtros_activos.items():
            self.filtros_listbox.insert(tk.END, f"{campo}: {valor}")
    
    def _aplicar_filtros_multiples(self):
        """Aplica todos los filtros activos"""
        if not self.filtros_activos:
            messagebox.showwarning("Advertencia", "No hay filtros activos para aplicar")
            return
        
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
            from access_management_service import access_service
            
            # Obtener todos los registros del historial
            todos_resultados = access_service.buscar_procesos({})
            
            # Aplicar filtros múltiples
            resultados_filtrados = self._aplicar_filtros_en_memoria(todos_resultados)
            
            # Mostrar resultados
            if resultados_filtrados:
                mensaje = f"Se encontraron {len(resultados_filtrados)} registros con los filtros aplicados"
                self.mostrar_resultados_historial(resultados_filtrados, mensaje)
            else:
                messagebox.showinfo("Filtros", "No se encontraron registros que coincidan con los filtros aplicados")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error aplicando filtros: {str(e)}")
    
    def _aplicar_filtros_en_memoria(self, resultados):
        """Aplica los filtros activos a los resultados en memoria"""
        if not resultados:
            return resultados
        
        resultados_filtrados = []
        for resultado in resultados:
            cumple_filtros = True
            
            for campo_ui, valor_filtro in self.filtros_activos.items():
                campo_bd = self.campos_filtro.get(campo_ui)
                if campo_bd:
                    valor_campo = str(resultado.get(campo_bd, '')).lower()
                    if valor_filtro.lower() not in valor_campo:
                        cumple_filtros = False
                        break
            
            if cumple_filtros:
                resultados_filtrados.append(resultado)
        
        return resultados_filtrados
    
    def mostrar_todo_el_historial(self):
        """Muestra todo el historial de procesos"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
            from access_management_service import access_service
            
            # Obtener todo el historial usando el método del servicio
            conn = access_service.get_connection()
            cursor = conn.cursor()
            
            # Primero verificar cuántos registros hay en total
            cursor.execute('SELECT COUNT(*) FROM historico')
            total_count = cursor.fetchone()[0]
            print(f"DEBUG: Total de registros en historico: {total_count}")
            
            # Verificar registros recientes
            cursor.execute('SELECT TOP 5 scotia_id, process_access, event_description, record_date FROM historico ORDER BY record_date DESC')
            recent_records = cursor.fetchall()
            print("DEBUG: Últimos 5 registros en la base de datos:")
            for record in recent_records:
                print(f"  SID={record[0]}, Process={record[1]}, Event={record[2][:30]}..., Date={record[3]}")
            
            cursor.execute('''
                SELECT h.id, h.scotia_id, h.case_id, h.responsible, h.record_date, h.request_date, 
                       h.process_access, h.subunit, h.event_description, h.ticket_email, h.app_access_name, 
                       h.computer_system_type, h.status, h.closing_date_app, h.closing_date_ticket, 
                       h.app_quality, h.confirmation_by_user, h.comment, h.ticket_quality, 
                       h.average_time_open_ticket, h.duration_of_access, h.comment_tq, h.general_status_ticket, 
                       h.general_status_case, h.sla_app, h.sla_ticket, h.sla_case, h.employee_email,
                       a.logical_access_name, a.description as app_description,
                       hc.email as headcount_email
                FROM historico h
                LEFT JOIN (
                    SELECT 
                        logical_access_name,
                        description,
                        ROW_NUMBER() OVER (PARTITION BY logical_access_name ORDER BY id) as rn
                    FROM applications
                ) a ON h.app_access_name = a.logical_access_name AND a.rn = 1
                LEFT JOIN headcount hc ON h.scotia_id = hc.scotia_id
                ORDER BY h.record_date DESC
            ''')
            rows = cursor.fetchall()
            conn.close()
            
            # Convertir a diccionarios
            columns = [description[0] for description in cursor.description]
            historial = [dict(zip(columns, row)) for row in rows]
            
            print(f"DEBUG: Historial obtenido: {len(historial)} registros")
            
            # Debug: mostrar los primeros 5 registros
            for i, registro in enumerate(historial[:5]):
                print(f"DEBUG: Registro {i}: SID={registro.get('scotia_id')}, Process={registro.get('process_access')}, Event={registro.get('event_description', '')[:50]}...")
            
            # Analizar registros de lateral movement para debug
            lateral_records = [r for r in historial if r.get('event_description') and 'lateral movement' in r.get('event_description', '')]
            onboarding_count = len([r for r in lateral_records if r.get('process_access') == 'onboarding'])
            offboarding_count = len([r for r in lateral_records if r.get('process_access') == 'offboarding'])
            
            print(f"DEBUG: Registros de lateral movement: {len(lateral_records)} (Onboarding: {onboarding_count}, Offboarding: {offboarding_count})")
            
            # Debug: mostrar todos los registros recientes (últimos 10)
            print("DEBUG: Últimos 10 registros:")
            for i, registro in enumerate(historial[:10]):
                print(f"  {i+1}. SID={registro.get('scotia_id')}, Process={registro.get('process_access')}, Status={registro.get('status')}, Event={registro.get('event_description', '')[:30]}...")
            
            self.mostrar_resultados_historial(historial, "")
            
            # Mostrar información de debug al usuario
            if lateral_records:
                messagebox.showinfo("Información de Debug", 
                    f"Se encontraron {len(lateral_records)} registros de lateral movement:\n"
                    f"• Onboarding: {onboarding_count}\n"
                    f"• Offboarding: {offboarding_count}\n\n"
                    f"Si no ves todos los registros, verifica:\n"
                    f"1. Filtros activos en la interfaz\n"
                    f"2. Búsqueda por SID específico\n"
                    f"3. Scroll en la tabla")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error obteniendo historial: {str(e)}")
            print(f"Error completo: {e}")
    
    def crear_datos_ejemplo_historial(self, conn, cursor):
        """Crea datos de ejemplo en la tabla historico si está vacía"""
        try:
            # Insertar algunos registros de ejemplo
            datos_ejemplo = [
                {
                    'scotia_id': 'S001',
                    'case_id': 'CASE-20241201-001',
                    'responsible': 'Admin',
                    'record_date': '2024-12-01 10:00:00',
                    'process_access': 'onboarding',
                    'sid': 'S001',
                    'area': 'Tecnología',
                    'subunit': 'Desarrollo',
                    'event_description': 'Acceso requerido para sistema de desarrollo',
                    'ticket_email': 'admin@empresa.com',
                    'app_access_name': 'Sistema Desarrollo',
                    'computer_system_type': 'Desktop',
                    'status': 'Pendiente',
                    'general_status_ticket': 'En Proceso'
                },
                {
                    'scotia_id': 'S002',
                    'case_id': 'CASE-20241201-002',
                    'responsible': 'Admin',
                    'record_date': '2024-12-01 11:00:00',
                    'process_access': 'offboarding',
                    'sid': 'S002',
                    'area': 'Tecnología',
                    'subunit': 'QA',
                    'event_description': 'Revocación de acceso para sistema de testing',
                    'ticket_email': 'admin@empresa.com',
                    'app_access_name': 'Sistema Testing',
                    'computer_system_type': 'Desktop',
                    'status': 'Completado',
                    'general_status_ticket': 'Completado'
                }
            ]
            
            for dato in datos_ejemplo:
                cursor.execute('''
                    INSERT INTO historico 
                    (scotia_id, case_id, responsible, record_date, process_access, sid, area, subunit,
                     event_description, ticket_email, app_access_name, computer_system_type, status, general_status_ticket)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    dato['scotia_id'], dato['case_id'], dato['responsible'], dato['record_date'],
                    dato['process_access'], dato['sid'], dato['area'], dato['subunit'],
                    dato['event_description'], dato['ticket_email'], dato['app_access_name'],
                    dato['computer_system_type'], dato['status'], dato['general_status_ticket']
                ))
            
            print("DEBUG: Datos de ejemplo creados en historico")
            
        except Exception as e:
            print(f"Error creando datos de ejemplo: {e}")
    
    def mostrar_resultados_historial(self, resultados, busqueda=""):
        """Muestra los resultados del historial en la tabla"""
        # Limpiar tabla anterior
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        print(f"DEBUG: Mostrando {len(resultados) if resultados else 0} resultados del historial")
        
        if resultados:
            for i, resultado in enumerate(resultados):
                # Debug: imprimir los primeros 3 registros
                if i < 3:
                    print(f"DEBUG: Registro {i}: {resultado}")
                
                # Formatear fecha
                fecha = resultado.get('record_date', '')
                try:
                    from datetime import datetime
                    fecha_formatted = datetime.fromisoformat(fecha).strftime('%d/%m/%Y %H:%M') if fecha else 'N/A'
                except:
                    fecha_formatted = fecha or 'N/A'
                
                # Formatear fecha de solicitud
                request_fecha = resultado.get('request_date', '')
                try:
                    from datetime import datetime
                    request_fecha_formatted = datetime.fromisoformat(request_fecha).strftime('%d/%m/%Y') if request_fecha else 'N/A'
                except:
                    request_fecha_formatted = request_fecha or 'N/A'
                
                # Formatear fechas adicionales
                closing_app = resultado.get('closing_date_app', '')
                closing_ticket = resultado.get('closing_date_ticket', '')
                try:
                    closing_app_formatted = datetime.fromisoformat(closing_app).strftime('%d/%m/%Y') if closing_app else 'N/A'
                    closing_ticket_formatted = datetime.fromisoformat(closing_ticket).strftime('%d/%m/%Y') if closing_ticket else 'N/A'
                except:
                    closing_app_formatted = closing_app or 'N/A'
                    closing_ticket_formatted = closing_ticket or 'N/A'
                
                # Formatear confirmación
                confirmation = resultado.get('confirmation_by_user', '')
                confirmation_text = 'Sí' if confirmation else 'No' if confirmation is not None else 'N/A'
                
                # Mapear todos los campos del historial
                # Usar el email del headcount si está disponible, sino usar el employee_email de la tabla historico
                email_to_show = resultado.get('headcount_email', '') or resultado.get('employee_email', '')
                
                # Debug para ver qué email se está usando
                if i < 3:  # Debug para los primeros 3 registros
                    print(f"DEBUG: Email del headcount: {resultado.get('headcount_email', '')}")
                    print(f"DEBUG: Email del historico: {resultado.get('employee_email', '')}")
                    print(f"DEBUG: Email final a mostrar: {email_to_show}")
                
                values = (
                    resultado.get('id', ''),                     # ID
                    resultado.get('scotia_id', ''),             # SID
                    email_to_show,                               # Email (del headcount o historico)
                    resultado.get('case_id', ''),               # Caso
                    resultado.get('process_access', ''),        # Proceso
                    resultado.get('app_access_name', ''),       # Aplicación
                    resultado.get('status', ''),                # Estado
                    fecha_formatted,                            # Fecha
                    request_fecha_formatted,                    # Fecha Solicitud
                    resultado.get('responsible', ''),           # Responsable
                    resultado.get('subunit', ''),               # Subunidad
                    resultado.get('computer_system_type', ''),   # Tipo Sistema
                    resultado.get('duration_of_access', ''),     # Duración
                    closing_app_formatted,                       # Cierre App
                    closing_ticket_formatted,                    # Cierre Ticket
                    resultado.get('app_quality', ''),           # Calidad App
                    confirmation_text,                          # Confirmación
                    resultado.get('comment', '')                # Comentario
                )
                
                if i < 3:  # Debug para los primeros 3 registros
                    print(f"DEBUG: Valores a insertar: {values}")
                
                self.tree.insert("", "end", values=values)
            
            if busqueda and busqueda.strip():
                messagebox.showinfo("Búsqueda", f"Se encontraron {len(resultados)} registros para: {busqueda}")
        else:
            if busqueda and busqueda.strip():
                messagebox.showinfo("Búsqueda", f"No se encontraron registros para: {busqueda}")
            elif busqueda == "":
                # Solo mostrar mensaje si no hay resultados y no es una búsqueda específica
                pass
            else:
                messagebox.showinfo("Búsqueda", "No se encontraron registros")
    
    def mostrar_resultados_busqueda(self, resultados, busqueda=""):
        """Muestra los resultados de búsqueda en el treeview"""
        # Limpiar resultados anteriores
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if resultados:
            for resultado in resultados:
                # Extraer valores del resultado de la base de datos real
                # Formatear fechas si están presentes
                record_date = resultado.get('record_date', '')
                if record_date:
                    try:
                        if isinstance(record_date, str):
                            # Intentar formatear si es string
                            record_date = str(record_date)[:19]  # Truncar a datetime si es muy largo
                        else:
                            record_date = str(record_date)
                    except:
                        record_date = str(record_date) if record_date else ''
                
                request_date = resultado.get('request_date', '')
                confirmation_date = resultado.get('confirmation_by_user', '')
                if confirmation_date:
                    try:
                        if isinstance(confirmation_date, str):
                            confirmation_date = str(confirmation_date)[:10]  # Solo fecha
                        else:
                            confirmation_date = str(confirmation_date)
                    except:
                        confirmation_date = str(confirmation_date) if confirmation_date else ''
                
                valores = (
                    resultado.get('id', ''),  # ID de la tabla
                    resultado.get('scotia_id', ''),  # SID
                    resultado.get('employee_email', ''),  # Email
                    resultado.get('case_id', ''),  # Caso
                    resultado.get('process_access', ''),  # Proceso
                    resultado.get('app_access_name', ''),  # Aplicación
                    resultado.get('status', ''),  # Estado
                    record_date,  # Fecha
                    request_date,  # Fecha Solicitud
                    resultado.get('responsible', ''),  # Responsable
                    resultado.get('subunit', ''),  # Subunidad
                    resultado.get('computer_system_type', ''),  # Tipo Sistema
                    resultado.get('duration_of_access', ''),  # Duración
                    resultado.get('closing_date_app', ''),  # Cierre App
                    resultado.get('closing_date_ticket', ''),  # Cierre Ticket
                    resultado.get('app_quality', ''),  # Calidad App
                    confirmation_date,  # Confirmación
                    resultado.get('comment', '')  # Comentario
                )
                self.tree.insert("", "end", values=valores)
            
            messagebox.showinfo("Búsqueda", f"Se encontraron {len(resultados)} registros para: {busqueda}")
        else:
            messagebox.showinfo("Búsqueda", f"No se encontraron registros para: {busqueda}")
    
    def buscar_todos_los_registros(self):
        """Busca todos los registros en la base de datos"""
        try:
            # Buscar todos los registros del historial
            self.mostrar_todo_el_historial()
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")
    
    def aplicar_filtro(self):
        """Aplica un filtro por texto en la columna seleccionada"""
        texto_filtro = self.variables['filtro_texto'].get().strip()
        columna = self.variables['columna_filtro'].get()
        
        if not texto_filtro:
            messagebox.showwarning("Advertencia", "Por favor ingrese texto para filtrar")
            return
        
        try:
            if self.service and hasattr(self.service, 'buscar_procesos'):
                # Mapear nombres de columnas a campos de la base de datos
                mapeo_columnas = {
                    "SID": "scotia_id",
                    "Status": "status",
                    "Request Date": "request_date",
                    "Tipo": "process_access",
                    "APP Name": "app_access_name",
                    "Mail": "ticket_email",
                    "App Quality": "app_quality",
                    "Confirmation by User": "confirmation_by_user",
                    "Comment": "comment",
                    "Case ID": "case_id",
                    "Responsible": "responsible",
                    "Subunit": "subunit",
                    "Event Description": "event_description"
                }
                
                campo_bd = mapeo_columnas.get(columna, "scotia_id")
                
                # Crear filtro para la búsqueda
                filtros = {campo_bd: texto_filtro}
                resultados = self.service.buscar_procesos(filtros)
                
                # Aplicar filtro adicional en memoria si es necesario
                if resultados:
                    resultados_filtrados = []
                    for resultado in resultados:
                        valor_campo = str(resultado.get(campo_bd, '')).lower()
                        if texto_filtro.lower() in valor_campo:
                            resultados_filtrados.append(resultado)
                    resultados = resultados_filtrados
                
                # Mostrar resultados con mensaje de confirmación
                self.mostrar_resultados_busqueda(resultados, f"filtro '{texto_filtro}' en columna '{columna}'")
            else:
                messagebox.showerror("Error", "Servicio no disponible para búsqueda")
        except Exception as e:
            messagebox.showerror("Error", f"Error aplicando filtro: {str(e)}")
            print(f"Error en aplicar_filtro: {e}")
    
    def limpiar_filtro(self):
        """Limpia el filtro y muestra todos los registros"""
        self.variables['filtro_texto'].set("")
        self.variables['columna_filtro'].set("SID")
        self.buscar_todos_los_registros()
    
    def _on_filtro_change(self, event):
        """Maneja el cambio en el campo de filtro para filtrado en tiempo real"""
        # Cancelar el delay anterior si existe
        if self.filtro_delay_id:
            self.parent.after_cancel(self.filtro_delay_id)
        
        # Programar nuevo filtrado con delay de 500ms
        self.filtro_delay_id = self.parent.after(500, self._aplicar_filtro_tiempo_real)
    
    def _aplicar_filtro_tiempo_real(self):
        """Aplica el filtro en tiempo real sin mostrar mensajes"""
        texto_filtro = self.variables['filtro_texto'].get().strip()
        columna = self.variables['columna_filtro'].get()
        
        if not texto_filtro:
            # Si no hay texto, mostrar todos los registros
            self.buscar_todos_los_registros()
            return
        
        try:
            if self.service and hasattr(self.service, 'buscar_procesos'):
                # Mapear nombres de columnas a campos de la base de datos
                mapeo_columnas = {
                    "SID": "scotia_id",
                    "Status": "status",
                    "Request Date": "request_date",
                    "Tipo": "process_access",
                    "APP Name": "app_access_name",
                    "Mail": "ticket_email",
                    "App Quality": "app_quality",
                    "Confirmation by User": "confirmation_by_user",
                    "Comment": "comment",
                    "Case ID": "case_id",
                    "Responsible": "responsible",
                    "Subunit": "subunit",
                    "Event Description": "event_description"
                }
                
                campo_bd = mapeo_columnas.get(columna, "scotia_id")
                
                # Crear filtro para la búsqueda
                filtros = {campo_bd: texto_filtro}
                resultados = self.service.buscar_procesos(filtros)
                
                # Aplicar filtro adicional en memoria si es necesario
                if resultados:
                    resultados_filtrados = []
                    for resultado in resultados:
                        valor_campo = str(resultado.get(campo_bd, '')).lower()
                        if texto_filtro.lower() in valor_campo:
                            resultados_filtrados.append(resultado)
                    resultados = resultados_filtrados
                
                # Mostrar resultados sin mensaje de confirmación
                self._mostrar_resultados_sin_mensaje(resultados)
            else:
                print("Servicio no disponible para filtrado en tiempo real")
        except Exception as e:
            print(f"Error en filtrado en tiempo real: {e}")
    
    def _mostrar_resultados_sin_mensaje(self, resultados):
        """Muestra los resultados sin mostrar mensajes de confirmación"""
        # Limpiar resultados anteriores
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if resultados:
            for resultado in resultados:
                # Extraer valores del resultado de la base de datos
                valores = (
                    resultado.get('numero_caso', ''),
                    resultado.get('sid', ''),
                    resultado.get('nueva_unidad_subunidad', ''),
                    resultado.get('nuevo_cargo', ''),
                    resultado.get('status', ''),
                    resultado.get('request_date', ''),
                    resultado.get('ingreso_por', ''),
                    resultado.get('tipo_proceso', ''),
                    resultado.get('app_name', ''),
                    resultado.get('mail', ''),
                    resultado.get('closing_date_app', ''),
                    resultado.get('app_quality', ''),
                    resultado.get('confirmation_by_user', ''),
                    resultado.get('comment', '')
                )
                self.tree.insert("", "end", values=valores)
    
    
    def seleccionar_registro(self, event):
        """Maneja la selección de un registro en el treeview"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            valores = item['values']
            
            # Cargar valores en los campos de edición
            if len(valores) >= 14:  # Ahora tenemos 14 columnas
                # Campos básicos
                self.variables['numero_caso_edicion'].set(valores[0])
                self.variables['nueva_unidad_subunidad_edicion'].set(valores[2])
                self.variables['nuevo_cargo_edicion'].set(valores[3])
                self.variables['status_edicion'].set(valores[4])
                self.variables['request_date_edicion'].set(valores[5])
                self.variables['ingreso_por_edicion'].set(valores[6])
                
                # Campos adicionales
                self.variables['mail_edicion'].set(valores[9] if valores[9] else '')
                self.variables['closing_date_app_edicion'].set(valores[10] if valores[10] else '')
                self.variables['app_quality_edicion'].set(valores[11] if valores[11] else '')
                
                # Formatear fecha de confirmación por usuario
                confirmation_date = valores[12] if valores[12] else ''
                if confirmation_date:
                    try:
                        from datetime import datetime
                        if isinstance(confirmation_date, str):
                            # Si es string, intentar parsear y formatear
                            parsed_date = datetime.strptime(confirmation_date, '%Y-%m-%d')
                            self.variables['confirmation_by_user_edicion'].set(confirmation_date)
                        else:
                            # Si es objeto datetime, formatear
                            self.variables['confirmation_by_user_edicion'].set(confirmation_date.strftime('%Y-%m-%d'))
                    except (ValueError, AttributeError):
                        self.variables['confirmation_by_user_edicion'].set('')
                else:
                    self.variables['confirmation_by_user_edicion'].set('')
                
                self.variables['comment_edicion'].set(valores[13] if valores[13] else '')
    
    def guardar_cambios(self):
        """Guarda los cambios realizados en los campos"""
        try:
            numero_caso = self.variables['numero_caso_edicion'].get().strip()
            if not numero_caso:
                messagebox.showwarning("Advertencia", "Por favor seleccione un registro para editar")
                return
            
            # Preparar datos para actualizar
            datos_actualizados = {
                'status': self.variables['status_edicion'].get(),
                'mail': self.variables['mail_edicion'].get(),
                'closing_date_app': self.variables['closing_date_app_edicion'].get(),
                'app_quality': self.variables['app_quality_edicion'].get(),
                'confirmation_by_user': self.variables['confirmation_by_user_edicion'].get(),
                'comment': self.variables['comment_edicion'].get()
            }
            
            # Validar fecha de confirmación por usuario
            confirmation_date = datos_actualizados.get('confirmation_by_user', '').strip()
            if confirmation_date and confirmation_date != 'YYYY-MM-DD':
                try:
                    # Validar formato de fecha
                    from datetime import datetime
                    datetime.strptime(confirmation_date, '%Y-%m-%d')
                except ValueError:
                    messagebox.showerror("Error", "La fecha de confirmación debe estar en formato YYYY-MM-DD")
                    return
            elif confirmation_date == 'YYYY-MM-DD':
                datos_actualizados['confirmation_by_user'] = None
            
            # Filtrar campos vacíos
            datos_actualizados = {k: v for k, v in datos_actualizados.items() if v and v.strip()}
            
            if not datos_actualizados:
                messagebox.showwarning("Advertencia", "No hay cambios para guardar")
                return
            
            # Guardar cambios usando el servicio
            if self.service and hasattr(self.service, 'actualizar_proceso'):
                exito, mensaje = self.service.actualizar_proceso(numero_caso, datos_actualizados)
                if exito:
                    messagebox.showinfo("Éxito", mensaje)
                    # Limpiar campos de edición
                    self.limpiar_campos_edicion()
                    # Refrescar la búsqueda actual
                    self.refrescar_busqueda_actual()
                else:
                    messagebox.showerror("Error", mensaje)
            else:
                messagebox.showerror("Error", "Servicio no disponible para actualizar")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando cambios: {str(e)}")
            print(f"Error en guardar_cambios: {e}")
    
    def limpiar_campos_edicion(self):
        """Limpia solo los campos de edición"""
        campos_edicion = [
            'mail_edicion', 'closing_date_app_edicion', 'app_quality_edicion',
            'confirmation_by_user_edicion', 'comment_edicion'
        ]
        for campo in campos_edicion:
            if campo in self.variables:
                self.variables[campo].set("")
    
    def refrescar_busqueda_actual(self):
        """Refresca la búsqueda actual para mostrar los cambios"""
        # Si hay un SID en búsqueda, refrescar esa búsqueda
        sid = self.variables['sid_busqueda'].get().strip()
        if sid:
            self.buscar_por_sid()
        else:
            # Si no hay búsqueda específica, mostrar todos los registros
            self.buscar_todos_los_registros()
    
    def obtener_datos(self):
        """Obtiene los datos de los campos de edición"""
        return {name: var.get() for name, var in self.variables.items()}
    
    def limpiar(self):
        """Limpia todos los campos"""
        for var in self.variables.values():
            var.set("")
        
        # Limpiar resultados de búsqueda
        for item in self.tree.get_children():
            self.tree.delete(item)

    def mostrar_estadisticas(self):
        """Muestra las estadísticas del historial en una ventana"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
            from access_management_service import access_service
            
            # Obtener estadísticas
            stats = access_service.get_historial_statistics()
            
            if "error" in stats:
                messagebox.showerror("Error", stats["error"])
                return
            
            # Crear ventana de estadísticas
            stats_window = tk.Toplevel(self.frame)
            stats_window.title("📊 Estadísticas del Historial")
            stats_window.geometry("800x600")
            stats_window.transient(self.frame)
            stats_window.grab_set()
            
            # Frame principal con scroll
            main_frame = ttk.Frame(stats_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Canvas para scroll
            canvas = tk.Canvas(main_frame)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Título
            ttk.Label(scrollable_frame, text="📊 Estadísticas del Historial", 
                     font=("Arial", 16, "bold")).pack(pady=(0, 20))
            
            # Estadísticas generales
            if 'generales' in stats:
                generales = stats['generales']
                ttk.Label(scrollable_frame, text="📈 Resumen General", 
                         font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
                
                generales_text = f"""
Total de Registros: {generales.get('total_registros', 0)}
Completados: {generales.get('completados', 0)}
Pendientes: {generales.get('pendientes', 0)}
En Proceso: {generales.get('en_proceso', 0)}
Cancelados: {generales.get('cancelados', 0)}
Rechazados: {generales.get('rechazados', 0)}
Empleados Únicos: {generales.get('empleados_unicos', 0)}
Aplicaciones Únicas: {generales.get('aplicaciones_unicas', 0)}
                """
                ttk.Label(scrollable_frame, text=generales_text, 
                         font=("Arial", 10)).pack(anchor="w", pady=(0, 20))
            
            # Estadísticas por unidad
            if 'por_unidad' in stats and stats['por_unidad']:
                ttk.Label(scrollable_frame, text="🏢 Por Unidad", 
                         font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
                
                # Crear tabla para unidades
                unidad_frame = ttk.Frame(scrollable_frame)
                unidad_frame.pack(fill=tk.X, pady=(0, 20))
                
                # Headers
                headers = ["Unidad", "Total", "Completados", "Pendientes", "En Proceso", "Cancelados", "Rechazados"]
                for i, header in enumerate(headers):
                    ttk.Label(unidad_frame, text=header, font=("Arial", 10, "bold")).grid(
                        row=0, column=i, padx=5, pady=2, sticky="w")
                
                # Datos
                for row_idx, unidad in enumerate(stats['por_unidad'][:10]):  # Mostrar solo top 10
                    ttk.Label(unidad_frame, text=unidad.get('unidad', '')[:20]).grid(
                        row=row_idx+1, column=0, padx=5, pady=1, sticky="w")
                    ttk.Label(unidad_frame, text=str(unidad.get('total_registros', 0))).grid(
                        row=row_idx+1, column=1, padx=5, pady=1, sticky="w")
                    ttk.Label(unidad_frame, text=str(unidad.get('completados', 0))).grid(
                        row=row_idx+1, column=2, padx=5, pady=1, sticky="w")
                    ttk.Label(unidad_frame, text=str(unidad.get('pendientes', 0))).grid(
                        row=row_idx+1, column=3, padx=5, pady=1, sticky="w")
                    ttk.Label(unidad_frame, text=str(unidad.get('en_proceso', 0))).grid(
                        row=row_idx+1, column=4, padx=5, pady=1, sticky="w")
                    ttk.Label(unidad_frame, text=str(unidad.get('cancelados', 0))).grid(
                        row=row_idx+1, column=5, padx=5, pady=1, sticky="w")
                    ttk.Label(unidad_frame, text=str(unidad.get('rechazados', 0))).grid(
                        row=row_idx+1, column=6, padx=5, pady=1, sticky="w")
            
            # Botón de cerrar
            ttk.Button(scrollable_frame, text="Cerrar", command=stats_window.destroy).pack(pady=20)
            
            # Configurar scroll
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrando estadísticas: {str(e)}")

    def exportar_estadisticas(self):
        """Exporta las estadísticas del historial a Excel"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
            from access_management_service import access_service
            from export_service import export_service
            
            # Obtener estadísticas
            stats = access_service.get_historial_statistics()
            
            if "error" in stats:
                messagebox.showerror("Error", stats["error"])
                return
            
            # Exportar a Excel
            filepath = export_service.export_historial_statistics(stats)
            
            messagebox.showinfo("Éxito", f"Estadísticas exportadas exitosamente a:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando estadísticas: {str(e)}")

    def crear_registro_manual(self):
        """Abre el diálogo para crear un registro manual de acceso"""
        try:
            from ui.manual_access_component import ManualAccessDialog
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
            from access_management_service import access_service
            
            # Abrir diálogo de registro manual
            dialog = ManualAccessDialog(self.frame, access_service)
            self.frame.wait_window(dialog.dialog)
            
            # Si se creó un registro, actualizar la tabla
            if dialog.result:
                self.actualizar_tabla()
                messagebox.showinfo("Éxito", "Registro manual creado exitosamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo diálogo de registro manual: {str(e)}")

class CreacionPersonaFrame:
    """Componente para la gestión completa de headcount y applications"""
    
    def __init__(self, parent, service=None):
        self.parent = parent
        self.service = service
        self.variables = {}
        self._crear_variables()
        self._crear_widgets()
    
    def _crear_variables(self):
        """Crea las variables de control"""
        self.variables = {
            # Campos básicos (nuevo esquema)
            'scotia_id': tk.StringVar(),
            'eikon_id': tk.StringVar(),
            'employee_number': tk.StringVar(),
            'employee_name': tk.StringVar(),
            'employee_last_name': tk.StringVar(),
            'business_email': tk.StringVar(),
            'department': tk.StringVar(),
            'office': tk.StringVar(),
            'current_position_title': tk.StringVar(),
            'current_position_level': tk.StringVar(),
            'hiring_date_bns': tk.StringVar(),
            'hiring_date_gbs': tk.StringVar(),
            'hiring_date_aml': tk.StringVar(),
            'supervisor_name': tk.StringVar(),
            'supervisor_last_name': tk.StringVar(),
            'address': tk.StringVar(),
            'brigade': tk.StringVar(),
            'begdate': tk.StringVar(),
            'status': tk.StringVar(value="Active"),
            'exit_date': tk.StringVar(),
            'modality_as_today': tk.StringVar(),
            'action_item': tk.StringVar(),
            'exit_reason': tk.StringVar(),
            'modality_reason': tk.StringVar(),
            'gender': tk.StringVar(),
            'dob': tk.StringVar(),
            'position_code': tk.StringVar(),
            # Campos para filtros
            'filtro_texto': tk.StringVar(),
            'columna_filtro': tk.StringVar(value="SID")
        }
        
        # Variables para filtros múltiples
        self.filtros_activos = {}
        self.campos_filtro = {
            "SID": "scotia_id",
            "Eikon ID": "eikon_id",
            "Employee #": "employee_number",
            "Nombre": "employee_name",
            "Apellido": "employee_last_name",
            "Business Email": "business_email",
            "Departamento": "department",
            "Oficina": "office",
            "Cargo": "current_position_title",
            "Nivel": "current_position_level",
            "Estado": "status",
            "Supervisor": "supervisor_name",
            "Supervisor Apellido": "supervisor_last_name",
            "Fecha Inicio (BNS)": "hiring_date_bns",
            "Fecha Inicio (GBS)": "hiring_date_gbs",
            "Fecha Inicio (AML)": "hiring_date_aml",
            "Begdate": "begdate",
            "Brigade": "brigade",
            "Acción": "action_item",
            "Motivo Salida": "exit_reason",
            "Modality": "modality_as_today",
            "Género": "gender"
        }
    
    def _crear_widgets(self):
        """Crea los widgets de la interfaz simplificada"""
        self.frame = ttk.Frame(self.parent)
        
        # Configurar grid del frame principal
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
        # Título con espaciado estándar
        ttk.Label(self.frame, text="👤 Gestión de Personas en Headcount", 
                  style="Title.TLabel").grid(row=0, column=0, pady=(10, 15), sticky="ew")
        
        # Frame principal simplificado
        main_frame = ttk.Frame(self.frame)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # Fila 2 para la tabla
        
        # Barra de herramientas (fuera del LabelFrame, igual que en Aplicaciones)
        toolbar = ttk.Frame(main_frame)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Botones principales
        ttk.Button(toolbar, text="➕ Nueva Persona", command=self.crear_persona, 
                  style="Success.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="✏️ Editar", command=self.editar_persona, 
                  style="Info.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="🗑️ Eliminar", command=self.eliminar_persona, 
                  style="Danger.TButton").pack(side=tk.LEFT, padx=(0, 10))
        
        # Separador
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Búsqueda
        ttk.Label(toolbar, text="🔍 Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_busqueda_change)
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de actualizar
        ttk.Button(toolbar, text="🔄 Actualizar", command=self.actualizar_tabla).pack(side=tk.LEFT)
        
        # Botón de exportar
        ttk.Button(toolbar, text="📊 Exportar", command=self.exportar_estadisticas_headcount).pack(side=tk.LEFT, padx=(10, 0))
        
        # Panel de filtros múltiples
        self._crear_panel_filtros_personas(main_frame)
        
        # Tabla de resultados
        resultados_frame = ttk.Frame(main_frame)
        resultados_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 15))
        
        # Configurar tabla de resultados
        resultados_frame.columnconfigure(0, weight=1)
        resultados_frame.rowconfigure(0, weight=1)
        
        # Crear Treeview para mostrar resultados
        self.tree = ttk.Treeview(resultados_frame, columns=("SID", "Eikon", "Employee #", "Nombre", "Apellido", "Business Email", "Departamento", "Cargo", "Estado"), 
                                show="headings", height=12)
        
        # Configurar columnas
        self.tree.heading("SID", text="SID")
        self.tree.heading("Eikon", text="Eikon ID")
        self.tree.heading("Employee #", text="Employee #")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Apellido", text="Apellido")
        self.tree.heading("Business Email", text="Business Email")
        self.tree.heading("Departamento", text="Departamento")
        self.tree.heading("Cargo", text="Cargo")
        self.tree.heading("Estado", text="Estado")
        
        # Configurar anchos de columna
        self.tree.column("SID", width=120, minwidth=100)
        self.tree.column("Eikon", width=130, minwidth=100)
        self.tree.column("Employee #", width=150, minwidth=120)
        self.tree.column("Nombre", width=140, minwidth=120)
        self.tree.column("Apellido", width=140, minwidth=120)
        self.tree.column("Business Email", width=250, minwidth=200)
        self.tree.column("Departamento", width=170, minwidth=140)
        self.tree.column("Cargo", width=200, minwidth=160)
        self.tree.column("Estado", width=120, minwidth=100)
        
        # Scrollbars (vertical y horizontal)
        vsb = ttk.Scrollbar(resultados_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(resultados_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Empaquetar tabla y scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Configurar grid para que la tabla se expanda
        resultados_frame.columnconfigure(0, weight=1)
        resultados_frame.rowconfigure(0, weight=1)
        
        # Eventos de la tabla
        self.tree.bind('<Double-1>', self._on_doble_clic)
        self.tree.bind('<Delete>', lambda e: self.eliminar_persona())
        
        # Inicializar filtro delay
        self.filtro_delay_id = None
    
    def _crear_panel_filtros_personas(self, parent):
        """Crea el panel de filtros múltiples para personas"""
        # Frame para filtros
        filtros_frame = ttk.LabelFrame(parent, text="Filtros Múltiples", padding="10")
        filtros_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        filtros_frame.columnconfigure(1, weight=1)
        
        # Lista de filtros activos
        ttk.Label(filtros_frame, text="Filtros Activos:").grid(row=0, column=0, sticky="w", pady=5)
        self.filtros_listbox = tk.Listbox(filtros_frame, height=3)
        self.filtros_listbox.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        # Scrollbar para la lista
        scrollbar_filtros = ttk.Scrollbar(filtros_frame, orient="vertical", command=self.filtros_listbox.yview)
        scrollbar_filtros.grid(row=0, column=2, sticky="ns")
        self.filtros_listbox.configure(yscrollcommand=scrollbar_filtros.set)
        
        # Botones para gestionar filtros
        botones_filtros = ttk.Frame(filtros_frame)
        botones_filtros.grid(row=0, column=3, padx=(5, 0), pady=5)
        
        ttk.Button(botones_filtros, text="Eliminar", command=self._eliminar_filtro_seleccionado_personas).pack(side=tk.TOP, pady=2)
        ttk.Button(botones_filtros, text="Limpiar", command=self._limpiar_todos_filtros_personas).pack(side=tk.TOP, pady=2)
        
        # Frame para agregar nuevo filtro
        nuevo_filtro_frame = ttk.Frame(filtros_frame)
        nuevo_filtro_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        nuevo_filtro_frame.columnconfigure(1, weight=1)
        
        # Campo de texto para el valor del filtro
        ttk.Label(nuevo_filtro_frame, text="Valor:").grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
        self.entry_filtro = ttk.Entry(nuevo_filtro_frame, width=30)
        self.entry_filtro.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)
        
        # Combo para seleccionar campo
        ttk.Label(nuevo_filtro_frame, text="Campo:").grid(row=0, column=2, padx=(0, 5), pady=5, sticky="w")
        self.combo_campo = ttk.Combobox(nuevo_filtro_frame, values=list(self.campos_filtro.keys()), width=15)
        self.combo_campo.grid(row=0, column=3, padx=(0, 10), pady=5)
        
        # Botón para agregar filtro
        ttk.Button(nuevo_filtro_frame, text="Agregar Filtro", command=self._agregar_filtro_personas).grid(row=0, column=4, padx=(0, 5), pady=5)
        
        # Botones de acción
        botones_accion = ttk.Frame(filtros_frame)
        botones_accion.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        
        ttk.Button(botones_accion, text="Aplicar Filtros", command=self._aplicar_filtros_multiples_personas).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(botones_accion, text="Mostrar Todos", command=self.mostrar_todos).pack(side=tk.LEFT)
        
        # Bind para Enter en el campo de texto
        self.entry_filtro.bind('<Return>', lambda e: self._agregar_filtro_personas())
    
    def _agregar_filtro_personas(self):
        """Agrega un nuevo filtro a la lista de personas"""
        valor = self.entry_filtro.get().strip()
        campo = self.combo_campo.get()
        
        if not valor:
            messagebox.showwarning("Advertencia", "Por favor ingrese un valor para el filtro")
            return
        
        if not campo:
            messagebox.showwarning("Advertencia", "Por favor seleccione un campo para filtrar")
            return
        
        # Agregar filtro al diccionario
        campo_bd = self.campos_filtro.get(campo)
        if campo_bd:
            self.filtros_activos[campo] = valor
            self._actualizar_lista_filtros_personas()
            
            # Limpiar campos
            self.entry_filtro.delete(0, tk.END)
            self.combo_campo.set("")
    
    def _eliminar_filtro_seleccionado_personas(self):
        """Elimina el filtro seleccionado de la lista de personas"""
        seleccion = self.filtros_listbox.curselection()
        if seleccion:
            indice = seleccion[0]
            campo = list(self.filtros_activos.keys())[indice]
            del self.filtros_activos[campo]
            self._actualizar_lista_filtros_personas()
    
    def _limpiar_todos_filtros_personas(self):
        """Limpia todos los filtros activos de personas"""
        self.filtros_activos.clear()
        self._actualizar_lista_filtros_personas()
    
    def _actualizar_lista_filtros_personas(self):
        """Actualiza la lista visual de filtros activos de personas"""
        self.filtros_listbox.delete(0, tk.END)
        for campo, valor in self.filtros_activos.items():
            self.filtros_listbox.insert(tk.END, f"{campo}: {valor}")
    
    def _aplicar_filtros_multiples_personas(self):
        """Aplica todos los filtros activos para personas"""
        if not self.filtros_activos:
            messagebox.showwarning("Advertencia", "No hay filtros activos para aplicar")
            return
        
        try:
            # Obtener todos los registros del headcount
            todos_resultados = self.service.obtener_todo_headcount()
            
            # Aplicar filtros múltiples
            resultados_filtrados = self._aplicar_filtros_en_memoria_personas(todos_resultados)
            
            # Mostrar resultados
            if resultados_filtrados:
                mensaje = f"Se encontraron {len(resultados_filtrados)} personas con los filtros aplicados"
                self.mostrar_resultados_busqueda(resultados_filtrados, mensaje)
            else:
                messagebox.showinfo("Filtros", "No se encontraron personas que coincidan con los filtros aplicados")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error aplicando filtros: {str(e)}")
    
    def _aplicar_filtros_en_memoria_personas(self, resultados):
        """Aplica los filtros activos a los resultados de personas en memoria"""
        if not resultados:
            return resultados
        
        resultados_filtrados = []
        for resultado in resultados:
            cumple_filtros = True
            
            for campo_ui, valor_filtro in self.filtros_activos.items():
                campo_bd = self.campos_filtro.get(campo_ui)
                if campo_bd:
                    valor_campo = self._obtener_valor_persona(resultado, campo_bd)
                    if valor_filtro.lower() not in valor_campo:
                        cumple_filtros = False
                        break
            
            if cumple_filtros:
                resultados_filtrados.append(resultado)
        
        return resultados_filtrados
    
    def mostrar_todos(self):
        """Muestra todos los registros del headcount"""
        try:
            # Obtener todos los registros de la base de datos real
            resultados = self.service.obtener_todo_headcount()
            self.mostrar_resultados_busqueda(resultados)
        except Exception as e:
            messagebox.showerror("Error", f"Error obteniendo registros: {str(e)}")
    
    def aplicar_filtro(self):
        """Aplica un filtro por texto en la columna seleccionada"""
        texto_filtro = self.variables['filtro_texto'].get().strip()
        columna = self.variables['columna_filtro'].get()
        
        if not texto_filtro:
            messagebox.showwarning("Advertencia", "Por favor ingrese texto para filtrar")
            return
        
        try:
            # Obtener todos los registros de la base de datos real
            todos_resultados = self.service.obtener_todo_headcount()
            
            # Mapear nombres de columnas a campos de la base de datos real
            mapeo_columnas = {
                "SID": "scotia_id",
                "Eikon ID": "eikon_id",
                "Employee #": "employee_number",
                "Nombre": "employee_name",
                "Apellido": "employee_last_name",
                "Business Email": "business_email",
                "Departamento": "department",
                "Cargo": "current_position_title",
                "Estado": "status"
            }
            
            campo_bd = mapeo_columnas.get(columna, "scotia_id")
            
            # Aplicar filtro en memoria
            if todos_resultados:
                resultados_filtrados = []
                for resultado in todos_resultados:
                    valor_campo = self._obtener_valor_persona(resultado, campo_bd)
                    if texto_filtro.lower() in valor_campo:
                        resultados_filtrados.append(resultado)
                todos_resultados = resultados_filtrados
            
            self.mostrar_resultados_busqueda(todos_resultados)
            messagebox.showinfo("Filtro", f"Se encontraron {len(todos_resultados)} registros para: filtro '{texto_filtro}' en columna '{columna}'")
        except Exception as e:
            messagebox.showerror("Error", f"Error aplicando filtro: {str(e)}")
            print(f"Error en aplicar_filtro: {e}")

    def _obtener_valor_persona(self, resultado, campo_bd: str) -> str:
        """Normaliza el valor del campo para filtros de personas."""
        valor = resultado.get(campo_bd, '')
        if campo_bd in ('activo', 'status'):
            if isinstance(valor, bool):
                return 'active' if valor else 'inactive'
            valor_str = str(valor or '').strip().lower()
            if valor_str in ('1', 'true', 'active', 'activo', 'yes', 'sí', 'si'):
                return 'active'
            if valor_str in ('0', 'false', 'inactive', 'inactivo', 'no'):
                return 'inactive'
            return valor_str or 'active'
        return str(valor).lower()
    
    def limpiar_filtro(self):
        """Limpia el filtro y muestra todos los registros"""
        self.variables['filtro_texto'].set("")
        self.variables['columna_filtro'].set("SID")
        self.mostrar_todos()
    
    def _on_filtro_change(self, event):
        """Maneja el cambio en el campo de filtro para filtrado en tiempo real"""
        # Cancelar el delay anterior si existe
        if self.filtro_delay_id:
            self.parent.after_cancel(self.filtro_delay_id)
        
        # Programar nuevo filtrado con delay de 500ms
        self.filtro_delay_id = self.parent.after(500, self._aplicar_filtro_tiempo_real)
    
    def _aplicar_filtro_tiempo_real(self):
        """Aplica el filtro en tiempo real sin mostrar mensajes"""
        texto_filtro = self.variables['filtro_texto'].get().strip()
        columna = self.variables['columna_filtro'].get()
        
        if not texto_filtro:
            # Si no hay texto, mostrar todos los registros
            self.mostrar_todos()
            return
        
        try:
            # Obtener todos los registros de la base de datos real
            todos_resultados = self.service.obtener_todo_headcount()
            
            # Mapear nombres de columnas a campos de la base de datos real
            mapeo_columnas = {
                "SID": "scotia_id",
                "Eikon ID": "eikon_id",
                "Employee #": "employee_number",
                "Nombre": "employee_name",
                "Apellido": "employee_last_name",
                "Business Email": "business_email",
                "Departamento": "department",
                "Cargo": "current_position_title",
                "Estado": "status"
            }
            
            campo_bd = mapeo_columnas.get(columna, "scotia_id")
            
            # Aplicar filtro en memoria
            if todos_resultados:
                resultados_filtrados = []
                for resultado in todos_resultados:
                    valor_campo = str(resultado.get(campo_bd, '')).lower()
                    if texto_filtro.lower() in valor_campo:
                        resultados_filtrados.append(resultado)
                todos_resultados = resultados_filtrados
            
            # Mostrar resultados sin mensaje de confirmación
            self._mostrar_resultados_sin_mensaje(todos_resultados)
        except Exception as e:
            print(f"Error en filtrado en tiempo real: {e}")
    
    
    def _mostrar_resultados_sin_mensaje(self, resultados):
        """Muestra los resultados sin mostrar mensajes de confirmación"""
        # Limpiar tabla anterior
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if resultados:
            for resultado in resultados:
                nombre = resultado.get('employee_name') or ''
                apellido = resultado.get('employee_last_name') or ''
                business_email = resultado.get('business_email') or resultado.get('email', '')
                department = resultado.get('department') or resultado.get('unit', '')
                cargo = resultado.get('current_position_title') or resultado.get('position', '')
                status = resultado.get('status') or ('Active' if resultado.get('activo', True) else 'Inactive')
                
                self.tree.insert("", "end", values=(
                    resultado.get('scotia_id', ''),  # SID
                    resultado.get('eikon_id', ''),
                    resultado.get('employee_number', ''),
                    nombre,                          # Nombre
                    apellido,                        # Apellido
                    business_email,
                    department,
                    cargo,
                    status
                ))
    
    
    
    def _get_unique_units(self) -> List[str]:
        """Obtiene departamentos únicos existentes en headcount para los combos."""
        try:
            registros = self.service.obtener_todo_headcount()
            unidades = sorted({(reg.get('department') or '').strip() for reg in registros if reg.get('department')}, key=str.lower)
            return unidades
        except Exception:
            return []

    def _get_unique_unidad_sub(self) -> List[str]:
        """Obtiene títulos de posición únicos existentes en headcount."""
        try:
            registros = self.service.obtener_todo_headcount()
            unidades = sorted({(reg.get('current_position_title') or '').strip() for reg in registros if reg.get('current_position_title')}, key=str.lower)
            return unidades
        except Exception:
            return []

    def crear_persona(self):
        """Crea una nueva persona usando el diálogo de edición"""
        try:
            # Crear diálogo de edición sin datos (para nueva persona)
            dialog = PersonaDialog(
                self.parent,
                "Nueva Persona",
                None,
                unidades=self._get_unique_units(),
                unidades_sub=self._get_unique_unidad_sub()
            )
            self.parent.wait_window(dialog.dialog)
            
            if dialog.result:
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
                from access_management_service import access_service
                
                success, message = access_service.create_employee(dialog.result)
                
                if success:
                    messagebox.showinfo("Éxito", message)
                    # Actualizar la tabla después de crear
                    self.actualizar_tabla()
                else:
                    messagebox.showerror("Error", message)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error creando empleado: {str(e)}")
    
    def validar_campos_obligatorios(self):
        """Valida que los campos obligatorios estén completos"""
        campos_obligatorios = ['scotia_id', 'employee_number', 'employee_name', 'business_email', 'department', 'current_position_title']
        campos_vacios = []
        
        for campo in campos_obligatorios:
            if not self.variables[campo].get().strip():
                campos_vacios.append(campo)
        
        return campos_vacios
    
    def obtener_datos(self):
        """Obtiene los datos de los campos"""
        return {name: var.get() for name, var in self.variables.items()}
    
    def limpiar(self):
        """Limpia todos los campos"""
        for var in self.variables.values():
            var.set("")
        self.variables['status'].set("Active")
    
    def actualizar_tabla(self):
        """Actualiza la tabla con todos los registros"""
        try:
            resultados = self.service.obtener_todo_headcount()
            self.mostrar_resultados_busqueda(resultados)
            messagebox.showinfo("Actualización", f"Tabla actualizada. Se encontraron {len(resultados)} registros.")
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando tabla: {str(e)}")
    
    def _on_doble_clic(self, event):
        """Maneja doble clic en la tabla"""
        self.editar_persona()
    
    def editar_persona(self):
        """Edita la persona seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione una persona para editar")
            return
        
        item = self.tree.item(selection[0])
        scotia_id = item['values'][0]
        
        # Buscar la persona en la base de datos
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
            from access_management_service import access_service
            
            persona_data = access_service.get_employee_by_id(scotia_id)
            if not persona_data:
                messagebox.showerror("Error", "No se pudo encontrar la persona seleccionada")
                return
            
            # Crear diálogo de edición
            dialog = PersonaDialog(
                self.parent,
                "Editar Persona",
                persona_data,
                unidades=self._get_unique_units(),
                unidades_sub=self._get_unique_unidad_sub()
            )
            self.parent.wait_window(dialog.dialog)
            
            if dialog.result:
                success, message = access_service.update_employee(scotia_id, dialog.result)
                if success:
                    messagebox.showinfo("Éxito", message)
                    self.actualizar_tabla()
                else:
                    messagebox.showerror("Error", message)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error editando persona: {str(e)}")
    
    def eliminar_persona(self):
        """Elimina la persona seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione una persona para eliminar")
            return
        
        item = self.tree.item(selection[0])
        scotia_id = item['values'][0]
        first_name = item['values'][3] if len(item['values']) > 3 else ''
        last_name = item['values'][4] if len(item['values']) > 4 else ''
        nombre = f"{first_name} {last_name}".strip()
        
        # Confirmar eliminación
        result = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar a {nombre} (SID: {scotia_id})?\n\n"
            "Esta acción no se puede deshacer."
        )
        
        if result:
            try:
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
                from access_management_service import access_service
                
                success, message = access_service.delete_employee(scotia_id)
                if success:
                    messagebox.showinfo("Éxito", message)
                    self.actualizar_tabla()
                else:
                    messagebox.showerror("Error", message)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error eliminando persona: {str(e)}")
    
    def mostrar_resultados_busqueda(self, resultados, busqueda=""):
        """Muestra los resultados de búsqueda en la tabla"""
        # Limpiar tabla anterior
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if resultados:
            for resultado in resultados:
                nombre = resultado.get('employee_name') or ''
                apellido = resultado.get('employee_last_name') or ''
                business_email = resultado.get('business_email') or resultado.get('email', '')
                department = resultado.get('department') or resultado.get('unit', '')
                cargo = resultado.get('current_position_title') or resultado.get('position', '')
                status = resultado.get('status') or ('Active' if resultado.get('activo', True) else 'Inactive')
                
                self.tree.insert("", "end", values=(
                    resultado.get('scotia_id', ''),  # SID
                    resultado.get('eikon_id', ''),
                    resultado.get('employee_number', ''),
                    nombre,                          # Nombre
                    apellido,                        # Apellido
                    business_email,
                    department,
                    cargo,
                    status
                ))
            
            # Mostrar mensaje de confirmación si se especifica
            if busqueda:
                messagebox.showinfo("Búsqueda", f"Se encontraron {len(resultados)} registros para: {busqueda}")
        else:
            # Mostrar mensaje si no hay resultados
            if busqueda:
                messagebox.showinfo("Búsqueda", f"No se encontraron registros para: {busqueda}")
            else:
                messagebox.showinfo("Búsqueda", "No se encontraron registros")

    def mostrar_estadisticas_headcount(self):
        """Muestra las estadísticas del headcount en una ventana"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
            from access_management_service import access_service
            
            # Obtener estadísticas
            stats = access_service.get_headcount_statistics()
            
            if "error" in stats:
                messagebox.showerror("Error", stats["error"])
                return
            
            # Crear ventana de estadísticas
            stats_window = tk.Toplevel(self.frame)
            stats_window.title("📊 Estadísticas del Headcount")
            stats_window.geometry("900x700")
            stats_window.transient(self.frame)
            stats_window.grab_set()
            
            # Frame principal con scroll
            main_frame = ttk.Frame(stats_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Canvas para scroll
            canvas = tk.Canvas(main_frame)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Título
            ttk.Label(scrollable_frame, text="📊 Estadísticas del Headcount", 
                     font=("Arial", 16, "bold")).pack(pady=(0, 20))
            
            # Estadísticas generales
            if 'generales' in stats:
                generales = stats['generales']
                ttk.Label(scrollable_frame, text="📈 Resumen General", 
                         font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
                
                generales_text = f"""
Total de Empleados: {generales.get('total_empleados', 0)}
Activos: {generales.get('activos', 0)}
Inactivos: {generales.get('inactivos', 0)}
Con Posición: {generales.get('con_posicion', 0)}
Con Unidad: {generales.get('con_unidad', 0)}
Con Fecha de Inicio: {generales.get('con_fecha_inicio', 0)}
Con Fecha de Inactivación: {generales.get('con_fecha_inactivacion', 0)}
Unidades Únicas: {generales.get('unidades_unicas', 0)}
Puestos Únicos: {generales.get('puestos_unicos', 0)}
                """
                ttk.Label(scrollable_frame, text=generales_text, 
                         font=("Arial", 10)).pack(anchor="w", pady=(0, 20))
            
            # Estadísticas por unidad
            if 'por_unidad' in stats and stats['por_unidad']:
                ttk.Label(scrollable_frame, text="🏢 Por Unidad", 
                         font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
                
                # Crear tabla para unidades
                unidad_frame = ttk.Frame(scrollable_frame)
                unidad_frame.pack(fill=tk.X, pady=(0, 20))
                
                # Headers
                headers = ["Unidad", "Total", "Activos", "Inactivos", "Con Posición", "Con Fecha Inicio"]
                for i, header in enumerate(headers):
                    ttk.Label(unidad_frame, text=header, font=("Arial", 10, "bold")).grid(
                        row=0, column=i, padx=5, pady=2, sticky="w")
                
                # Datos
                for row_idx, unidad in enumerate(stats['por_unidad'][:15]):  # Mostrar top 15
                    ttk.Label(unidad_frame, text=unidad.get('unidad', '')[:20]).grid(
                        row=row_idx+1, column=0, padx=5, pady=1, sticky="w")
                    ttk.Label(unidad_frame, text=str(unidad.get('total_empleados', 0))).grid(
                        row=row_idx+1, column=1, padx=5, pady=1, sticky="w")
                    ttk.Label(unidad_frame, text=str(unidad.get('activos', 0))).grid(
                        row=row_idx+1, column=2, padx=5, pady=1, sticky="w")
                    ttk.Label(unidad_frame, text=str(unidad.get('inactivos', 0))).grid(
                        row=row_idx+1, column=3, padx=5, pady=1, sticky="w")
                    ttk.Label(unidad_frame, text=str(unidad.get('con_posicion', 0))).grid(
                        row=row_idx+1, column=4, padx=5, pady=1, sticky="w")
                    ttk.Label(unidad_frame, text=str(unidad.get('con_fecha_inicio', 0))).grid(
                        row=row_idx+1, column=5, padx=5, pady=1, sticky="w")
            
            # Estadísticas por puesto
            if 'por_puesto' in stats and stats['por_puesto']:
                ttk.Label(scrollable_frame, text="👔 Por Puesto", 
                         font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
                
                # Crear tabla para puestos
                puesto_frame = ttk.Frame(scrollable_frame)
                puesto_frame.pack(fill=tk.X, pady=(0, 20))
                
                # Headers
                headers = ["Puesto", "Unidad", "Total", "Activos", "Inactivos", "Con Fecha Inicio"]
                for i, header in enumerate(headers):
                    ttk.Label(puesto_frame, text=header, font=("Arial", 10, "bold")).grid(
                        row=0, column=i, padx=5, pady=2, sticky="w")
                
                # Datos
                for row_idx, puesto in enumerate(stats['por_puesto'][:15]):  # Mostrar top 15
                    ttk.Label(puesto_frame, text=puesto.get('puesto', '')[:15]).grid(
                        row=row_idx+1, column=0, padx=5, pady=1, sticky="w")
                    ttk.Label(puesto_frame, text=puesto.get('unidad', '')[:15]).grid(
                        row=row_idx+1, column=1, padx=5, pady=1, sticky="w")
                    ttk.Label(puesto_frame, text=str(puesto.get('total_empleados', 0))).grid(
                        row=row_idx+1, column=2, padx=5, pady=1, sticky="w")
                    ttk.Label(puesto_frame, text=str(puesto.get('activos', 0))).grid(
                        row=row_idx+1, column=3, padx=5, pady=1, sticky="w")
                    ttk.Label(puesto_frame, text=str(puesto.get('inactivos', 0))).grid(
                        row=row_idx+1, column=4, padx=5, pady=1, sticky="w")
                    ttk.Label(puesto_frame, text=str(puesto.get('con_fecha_inicio', 0))).grid(
                        row=row_idx+1, column=5, padx=5, pady=1, sticky="w")
            
            # Detalle por unidad (lista de empleados)
            if 'detalle_por_unidad' in stats and stats['detalle_por_unidad']:
                ttk.Label(scrollable_frame, text="👥 Detalle por Unidad - Lista de Empleados", 
                         font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
                
                # Agrupar por unidad
                unidades_empleados = {}
                for emp in stats['detalle_por_unidad']:
                    unidad = emp.get('unidad', 'Sin Unidad')
                    if unidad not in unidades_empleados:
                        unidades_empleados[unidad] = []
                    unidades_empleados[unidad].append(emp)
                
                # Mostrar cada unidad
                for unidad, empleados in list(unidades_empleados.items())[:5]:  # Mostrar top 5 unidades
                    ttk.Label(scrollable_frame, text=f"🏢 {unidad} ({len(empleados)} empleados)", 
                             font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
                    
                    # Crear tabla para empleados de esta unidad
                    emp_frame = ttk.Frame(scrollable_frame)
                    emp_frame.pack(fill=tk.X, pady=(0, 15))
                    
                    # Headers
                    headers = ["ID", "Nombre", "Puesto", "Manager", "Estado", "Fecha Inicio"]
                    for i, header in enumerate(headers):
                        ttk.Label(emp_frame, text=header, font=("Arial", 9, "bold")).grid(
                            row=0, column=i, padx=3, pady=1, sticky="w")
                    
                    # Datos de empleados
                    for row_idx, emp in enumerate(empleados[:10]):  # Mostrar max 10 empleados por unidad
                        ttk.Label(emp_frame, text=emp.get('scotia_id', '')[:8]).grid(
                            row=row_idx+1, column=0, padx=3, pady=1, sticky="w")
                        ttk.Label(emp_frame, text=emp.get('full_name', '')[:20]).grid(
                            row=row_idx+1, column=1, padx=3, pady=1, sticky="w")
                        ttk.Label(emp_frame, text=emp.get('puesto', '')[:15]).grid(
                            row=row_idx+1, column=2, padx=3, pady=1, sticky="w")
                        ttk.Label(emp_frame, text=emp.get('manager', '')[:15]).grid(
                            row=row_idx+1, column=3, padx=3, pady=1, sticky="w")
                        ttk.Label(emp_frame, text=emp.get('estado', '')[:8]).grid(
                            row=row_idx+1, column=4, padx=3, pady=1, sticky="w")
                        # Formatear fecha correctamente
                        start_date = emp.get('start_date', '')
                        if start_date and hasattr(start_date, 'strftime'):
                            start_date_str = start_date.strftime('%Y-%m-%d')
                        else:
                            start_date_str = str(start_date)[:10] if start_date else ''
                        ttk.Label(emp_frame, text=start_date_str).grid(
                            row=row_idx+1, column=5, padx=3, pady=1, sticky="w")
                    
                    if len(empleados) > 10:
                        ttk.Label(emp_frame, text=f"... y {len(empleados) - 10} empleados más", 
                                 font=("Arial", 9, "italic")).grid(
                            row=len(empleados)+1, column=0, columnspan=6, padx=3, pady=1, sticky="w")
            
            # Botón de cerrar
            ttk.Button(scrollable_frame, text="Cerrar", command=stats_window.destroy).pack(pady=20)
            
            # Configurar scroll
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrando estadísticas: {str(e)}")

    def exportar_estadisticas_headcount(self):
        """Exporta las estadísticas del headcount a Excel"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
            from access_management_service import access_service
            from export_service import export_service
            
            # Obtener estadísticas
            stats = access_service.get_headcount_statistics()
            
            if "error" in stats:
                messagebox.showerror("Error", stats["error"])
                return
            
            # Exportar a Excel
            filepath = export_service.export_headcount_statistics(stats)
            
            messagebox.showinfo("Éxito", f"Estadísticas del headcount exportadas exitosamente a:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando estadísticas: {str(e)}")
    
    def _on_busqueda_change(self, *args):
        """Maneja cambios en la búsqueda"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            # Si no hay término de búsqueda, mostrar todos los registros
            self.actualizar_tabla()
        else:
            # Realizar búsqueda en tiempo real
            try:
                resultados = self.service.buscar_en_headcount(search_term)
                self.mostrar_resultados_busqueda(resultados, search_term)
            except Exception as e:
                messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")


class PersonaDialog:
    """Diálogo para agregar/editar personas"""
    
    def __init__(self, parent, title: str, persona_data: dict = None,
                 unidades: Optional[List[str]] = None,
                 unidades_sub: Optional[List[str]] = None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar el diálogo
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.persona_data = persona_data
        self.unidades = sorted(unidades or ["Tecnología", "Recursos Humanos", "Finanzas", "Marketing", "Operaciones", "Ventas", "Legal"])
        self.unidades_sub = sorted(unidades_sub or ["Tecnología/Desarrollo", "Recursos Humanos/RRHH"])
        self.result = None
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Configura la interfaz del diálogo"""
        # Frame principal con scroll
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título
        title_label = ttk.Label(scrollable_frame, text="Información de la Persona", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Campos del formulario
        campos = [
            ("SID (Scotia ID):", "scotia_id", "entry"),
            ("Eikon ID:", "eikon_id", "entry"),
            ("Employee Number:", "employee_number", "entry"),
            ("Nombre:", "employee_name", "entry"),
            ("Apellido:", "employee_last_name", "entry"),
            ("Business Email:", "business_email", "entry"),
            ("Office:", "office", "entry"),
            ("Department:", "department", "combobox", self.unidades),
            ("Current Position Title:", "current_position_title", "combobox", self.unidades_sub),
            ("Current Position Level:", "current_position_level", "entry"),
            ("Hiring Date BNS:", "hiring_date_bns", "entry"),
            ("Hiring Date GBS:", "hiring_date_gbs", "entry"),
            ("Hiring Date AML:", "hiring_date_aml", "entry"),
            ("Supervisor Name:", "supervisor_name", "entry"),
            ("Supervisor Last Name:", "supervisor_last_name", "entry"),
            ("Address:", "address", "entry"),
            ("Brigade:", "brigade", "entry"),
            ("Begdate:", "begdate", "entry"),
            ("Status:", "status", "combobox", ["Active", "Inactive", "On Leave"]),
            ("Exit Date:", "exit_date", "entry"),
            ("Modality as Today:", "modality_as_today", "entry"),
            ("Action Item:", "action_item", "entry"),
            ("Exit Reason:", "exit_reason", "entry"),
            ("Modality Reason:", "modality_reason", "entry"),
            ("Gender:", "gender", "combobox", ["Female", "Male", "Non-binary", "Prefer not to say"]),
            ("DOB:", "dob", "entry"),
            ("Position Code:", "position_code", "entry")
        ]
        
        # Crear campos dinámicamente
        self.variables = {}
        self.widgets = {}
        for i, campo in enumerate(campos):
            label_text, var_name, tipo = campo[:3]
            ttk.Label(scrollable_frame, text=label_text).grid(row=i+1, column=0, sticky="w", pady=5)
            
            if tipo == "entry":
                self.variables[var_name] = tk.StringVar()
                entry = ttk.Entry(scrollable_frame, textvariable=self.variables[var_name], width=40)
                entry.grid(row=i+1, column=1, sticky="ew", pady=5, padx=(10, 0))
                self.widgets[var_name] = entry
            elif tipo == "combobox":
                valores = campo[3] if len(campo) > 3 else []
                self.variables[var_name] = tk.StringVar()
                combo = ttk.Combobox(scrollable_frame, textvariable=self.variables[var_name], values=valores, width=37)
                combo.grid(row=i+1, column=1, sticky="ew", pady=5, padx=(10, 0))
                self.widgets[var_name] = combo
        
        # Configurar grid
        scrollable_frame.columnconfigure(1, weight=1)
        
        # Canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botones
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ttk.Button(button_frame, text="Guardar", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Configurar validación
        if 'scotia_id' in self.widgets:
            self.widgets['scotia_id'].focus()
        
        self.dialog.bind('<Return>', lambda e: self._save())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
    
    def _load_data(self):
        """Carga los datos existentes si es una edición"""
        if self.persona_data:
            data = dict(self.persona_data)
            full_name = data.get('full_name') or ''
            if not data.get('employee_name') and full_name:
                parts = full_name.split(' ', 1)
                data['employee_name'] = parts[0]
                if len(parts) > 1:
                    data['employee_last_name'] = parts[1]
            if not data.get('business_email') and data.get('email'):
                data['business_email'] = data['email']
            if not data.get('department') and data.get('unit'):
                data['department'] = data['unit']
            if not data.get('current_position_title') and data.get('position'):
                data['current_position_title'] = data['position']
            if not data.get('status'):
                data['status'] = 'Active' if data.get('activo', True) else 'Inactive'
            if not data.get('employee_number') and data.get('employee'):
                data['employee_number'] = data['employee']
            for var_name, var in self.variables.items():
                value = data.get(var_name)
                if value is not None:
                    var.set(str(value))
    
    def _save(self):
        """Guarda los datos del formulario"""
        required_fields = [
            ('scotia_id', "El SID es obligatorio"),
            ('employee_number', "El número de empleado es obligatorio"),
            ('employee_name', "El nombre es obligatorio"),
            ('business_email', "El correo corporativo es obligatorio"),
            ('department', "El departamento es obligatorio"),
            ('current_position_title', "El cargo actual es obligatorio")
        ]
        for field, message_text in required_fields:
            if not self.variables[field].get().strip():
                messagebox.showerror("Error", message_text)
                return
        
        # Preparar datos
        self.result = {}
        for var_name, var in self.variables.items():
            self.result[var_name] = var.get().strip()
        
        # Normalizar campos legacy para compatibilidad con el servicio
        self.result['status'] = self.result.get('status') or 'Active'
        full_name = f"{self.result.get('employee_name', '').strip()} {self.result.get('employee_last_name', '').strip()}".strip()
        self.result['full_name'] = full_name
        self.result['email'] = self.result.get('business_email')
        self.result['employee'] = self.result.get('employee_number')
        self.result['unit'] = self.result.get('department')
        self.result['position'] = self.result.get('current_position_title')
        self.result['activo'] = self.result['status'].lower() == 'active'
        
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancela la operación"""
        self.dialog.destroy()


class HistorialDialog:
    """Diálogo para editar registros del historial"""
    
    def __init__(self, parent, title: str, historial_data: dict = None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("800x700")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar el diálogo
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.historial_data = historial_data
        self.result = None
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Configura la interfaz del diálogo"""
        # Frame principal con scroll
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título
        title_label = ttk.Label(scrollable_frame, text="Editar Registro de Historial", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Campos del formulario - Todos los campos de la tabla historico
        campos = [
            ("ID:", "id", "entry", True),  # Solo lectura
            ("SID:", "scotia_id", "entry"),
            ("ID de Caso:", "case_id", "entry"),
            ("Responsable:", "responsible", "entry"),
            ("Fecha de Registro:", "record_date", "entry"),
            ("Fecha de Solicitud:", "request_date", "entry"),
            ("Proceso de Acceso:", "process_access", "combobox", ["onboarding", "offboarding", "lateral_movement"]),
            ("Sub Unidad:", "subunit", "entry"),
            ("Descripción del Evento:", "event_description", "text"),
            ("Email del Ticket:", "ticket_email", "entry"),
            ("Nombre de Aplicación:", "app_access_name", "entry"),
            ("Tipo de Sistema:", "computer_system_type", "entry"),
            ("Duración del Acceso:", "duration_of_access", "combobox", ["Permanente", "Temporal", "Por Proyecto"]),
            ("Estado:", "status", "combobox", ["cancelled", "closed completed", "closed incompleted", "in progress", "in validation", "to validate"]),
            ("Fecha de Cierre App:", "closing_date_app", "entry"),
            ("Fecha de Cierre Ticket:", "closing_date_ticket", "entry"),
            ("Calidad de App:", "app_quality", "combobox", ["Excelente", "Buena", "Regular", "Mala"]),
            ("Confirmación por Usuario:", "confirmation_by_user", "date"),
            ("Comentario:", "comment", "text"),
            ("Comentario TQ:", "comment_tq", "text"),
            ("Calidad del Ticket:", "ticket_quality", "combobox", ["Excelente", "Buena", "Regular", "Mala"]),
            ("Estado General Ticket:", "general_status_ticket", "combobox", ["Pendiente", "En Proceso", "Completado", "Cancelado"]),
            ("Estado General Caso:", "general_status_case", "combobox", ["Pendiente", "En Proceso", "Completado", "Cancelado"]),
            ("Tiempo Promedio de Apertura:", "average_time_open_ticket", "entry"),
            ("SLA App:", "sla_app", "combobox", ["Cumplido", "Incumplido", "Pendiente"]),
            ("SLA Ticket:", "sla_ticket", "combobox", ["Cumplido", "Incumplido", "Pendiente"]),
            ("SLA Caso:", "sla_case", "combobox", ["Cumplido", "Incumplido", "Pendiente"])
        ]
        
        # Crear campos dinámicamente
        self.variables = {}
        self.widgets = {}
        for i, campo in enumerate(campos):
            label_text, var_name, tipo = campo[:3]
            solo_lectura = campo[3] if len(campo) > 3 and isinstance(campo[3], bool) else False
            
            ttk.Label(scrollable_frame, text=label_text).grid(row=i+1, column=0, sticky="w", pady=5)
            
            if tipo == "entry":
                self.variables[var_name] = tk.StringVar()
                entry = ttk.Entry(scrollable_frame, textvariable=self.variables[var_name], width=50, state="readonly" if solo_lectura else "normal")
                entry.grid(row=i+1, column=1, sticky="ew", pady=5, padx=(10, 0))
                self.widgets[var_name] = entry
            elif tipo == "combobox":
                valores = campo[3] if len(campo) > 3 and not isinstance(campo[3], bool) else (campo[4] if len(campo) > 4 else [])
                self.variables[var_name] = tk.StringVar()
                combo = ttk.Combobox(scrollable_frame, textvariable=self.variables[var_name], values=valores, width=47, state="readonly" if solo_lectura else "normal")
                combo.grid(row=i+1, column=1, sticky="ew", pady=5, padx=(10, 0))
                self.widgets[var_name] = combo
            elif tipo == "text":
                text_widget = tk.Text(scrollable_frame, height=3, width=50, state="disabled" if solo_lectura else "normal")
                text_widget.grid(row=i+1, column=1, sticky="ew", pady=5, padx=(10, 0))
                self.variables[var_name] = text_widget  # Para Text widgets, guardamos el widget directamente
                self.widgets[var_name] = text_widget
            elif tipo == "checkbox":
                self.variables[var_name] = tk.BooleanVar()
                checkbox = ttk.Checkbutton(scrollable_frame, variable=self.variables[var_name], state="disabled" if solo_lectura else "normal")
                checkbox.grid(row=i+1, column=1, sticky="w", pady=5, padx=(10, 0))
                self.widgets[var_name] = checkbox
            elif tipo == "date":
                self.variables[var_name] = tk.StringVar()
                entry = ttk.Entry(scrollable_frame, textvariable=self.variables[var_name], state="disabled" if solo_lectura else "normal")
                entry.grid(row=i+1, column=1, sticky="ew", pady=5, padx=(10, 0))
                entry.insert(0, "YYYY-MM-DD")
                entry.configure(foreground="gray")
                
                def on_focus_in(event):
                    if entry.get() == "YYYY-MM-DD":
                        entry.delete(0, tk.END)
                        entry.configure(foreground="black")
                
                def on_focus_out(event):
                    if not entry.get():
                        entry.insert(0, "YYYY-MM-DD")
                        entry.configure(foreground="gray")
                
                entry.bind("<FocusIn>", on_focus_in)
                entry.bind("<FocusOut>", on_focus_out)
                self.widgets[var_name] = entry
        
        # Configurar grid
        scrollable_frame.columnconfigure(1, weight=1)
        
        # Canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botones
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ttk.Button(button_frame, text="Guardar", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Configurar validación
        if 'scotia_id' in self.widgets:
            self.widgets['scotia_id'].focus()
        
        self.dialog.bind('<Return>', lambda e: self._save())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
    
    def _load_data(self):
        """Carga los datos existentes si es una edición"""
        if self.historial_data:
            for var_name, var in self.variables.items():
                if var_name in self.historial_data:
                    if isinstance(var, tk.StringVar):
                        var.set(str(self.historial_data[var_name]) if self.historial_data[var_name] is not None else '')
                    elif isinstance(var, tk.Text):
                        var.delete('1.0', tk.END)
                        var.insert('1.0', str(self.historial_data[var_name]) if self.historial_data[var_name] is not None else '')
                    elif isinstance(var, tk.BooleanVar):
                        var.set(bool(self.historial_data[var_name]) if self.historial_data[var_name] is not None else False)
    
    def _save(self):
        """Guarda los datos del formulario"""
        # Validaciones básicas
        if not self.variables['scotia_id'].get().strip():
            messagebox.showerror("Error", "El SID es obligatorio")
            return
        
        if not self.variables['process_access'].get().strip():
            messagebox.showerror("Error", "El proceso de acceso es obligatorio")
            return
        
        # Preparar datos
        self.result = {}
        for var_name, var in self.variables.items():
            if isinstance(var, tk.StringVar):
                self.result[var_name] = var.get().strip()
            elif isinstance(var, tk.Text):
                self.result[var_name] = var.get('1.0', tk.END).strip()
            elif isinstance(var, tk.BooleanVar):
                self.result[var_name] = var.get()
        
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancela la operación"""
        self.dialog.destroy()
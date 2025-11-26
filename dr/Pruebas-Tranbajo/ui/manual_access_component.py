"""
Componente para crear registros manuales de acceso
"""
import tkinter as tk
from tkinter import ttk, messagebox
from services.dropdown_service import dropdown_service


class ManualAccessDialog:
    """Diálogo para crear registros manuales de acceso"""
    
    def __init__(self, parent, service=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("➕ Crear Registro Manual de Acceso")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.service = service
        self.result = None
        
        # Variables
        self.variables = {
            'scotia_id': tk.StringVar(),
            'app_name': tk.StringVar(),
            'position': tk.StringVar(),
            'responsible': tk.StringVar(value="Manual"),
            'description': tk.StringVar()
        }
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz del diálogo"""
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="➕ Crear Registro Manual de Acceso", 
                 font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="ew")
        
        # Campos del formulario
        campos = [
            ("ID de Empleado (Scotia ID):", "scotia_id", "entry"),
            ("Posición:", "position", "combobox"),
            ("Aplicación:", "app_name", "combobox"),
            ("Responsable:", "responsible", "entry"),
            ("Descripción (opcional):", "description", "entry")
        ]
        
        for i, (label_text, var_name, widget_type) in enumerate(campos):
            # Label
            ttk.Label(main_frame, text=label_text, font=("Arial", 10, "bold")).grid(
                row=i+1, column=0, sticky="w", pady=5, padx=(0, 10))
            
            # Widget
            if widget_type == "entry":
                widget = ttk.Entry(main_frame, textvariable=self.variables[var_name], width=40)
            elif widget_type == "combobox":
                widget = ttk.Combobox(main_frame, textvariable=self.variables[var_name], width=37, state="readonly")
                if var_name == "position":
                    # Cargar posiciones disponibles
                    self._load_positions(widget)
                elif var_name == "app_name":
                    # Cargar aplicaciones disponibles (se actualizará cuando se seleccione posición)
                    self._load_applications(widget)
            else:
                widget = ttk.Entry(main_frame, textvariable=self.variables[var_name], width=40)
            
            widget.grid(row=i+1, column=1, sticky="ew", pady=5)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(campos)+1, column=0, columnspan=2, pady=20, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        ttk.Button(button_frame, text="Crear Registro", command=self._create_record, 
                  style="Success.TButton").grid(row=0, column=0, padx=(0, 10), sticky="ew")
        ttk.Button(button_frame, text="Cancelar", command=self._cancel, 
                  style="Danger.TButton").grid(row=0, column=1, padx=(10, 0), sticky="ew")
        
        # Información adicional
        info_text = """
ℹ️ Información:
• Este registro se creará como "manual_access" en el historial
• El empleado debe existir en el headcount
• Seleccione la posición para filtrar las aplicaciones disponibles
• La aplicación se puede seleccionar de la lista filtrada o escribir una nueva
• El registro quedará en estado "Pendiente" para su procesamiento
• Los dropdowns se cargan automáticamente desde la base de datos
        """
        ttk.Label(main_frame, text=info_text, font=("Arial", 9), 
                 foreground="gray").grid(row=len(campos)+2, column=0, columnspan=2, 
                                       pady=(10, 0), sticky="w")
    
    def _load_positions(self, combobox):
        """Carga las posiciones disponibles en el combobox usando dropdown_service"""
        try:
            # Usar el dropdown_service para obtener posiciones
            positions = dropdown_service.get_unique_positions()
            
            # Si no hay posiciones en la base de datos, usar valores por defecto
            if not positions:
                positions = [
                    "ANALISTA SENIOR",
                    "DESARROLLADOR",
                    "GERENTE",
                    "ADMINISTRADOR",
                    "COORDINADOR",
                    "ESPECIALISTA",
                    "CONSULTOR",
                    "DIRECTOR",
                    "SUPERVISOR",
                    "TÉCNICO"
                ]
            
            combobox['values'] = positions
            # Configurar evento para actualizar aplicaciones cuando cambie la posición
            combobox.bind('<<ComboboxSelected>>', self._on_position_changed)
            
        except Exception as e:
            print(f"Error cargando posiciones: {e}")
            # En caso de error, usar valores por defecto
            combobox['values'] = [
                "ANALISTA SENIOR",
                "DESARROLLADOR", 
                "GERENTE",
                "ADMINISTRADOR",
                "COORDINADOR"
            ]
    
    def _load_applications(self, combobox):
        """Carga las aplicaciones disponibles en el combobox usando access_service"""
        try:
            if self.service:
                applications = self.service.get_available_applications()
                app_names = [app['name'] for app in applications]
                
                # Si no hay aplicaciones en la base de datos, usar valores por defecto
                if not app_names:
                    app_names = [
                        "JIRA",
                        "CONFLUENCE", 
                        "GITLAB",
                        "POWER BI",
                        "SAP",
                        "OFFICE 365",
                        "SALESFORCE",
                        "SERVICENOW",
                        "TABLEAU",
                        "SHAREPOINT"
                    ]
                
                combobox['values'] = app_names
            else:
                # Valores por defecto si no hay servicio
                combobox['values'] = [
                    "JIRA",
                    "CONFLUENCE",
                    "GITLAB", 
                    "POWER BI",
                    "SAP",
                    "OFFICE 365"
                ]
                
        except Exception as e:
            print(f"Error cargando aplicaciones: {e}")
            # En caso de error, usar valores por defecto
            combobox['values'] = [
                "JIRA",
                "CONFLUENCE",
                "GITLAB",
                "POWER BI",
                "SAP"
            ]
    
    def _on_position_changed(self, event):
        """Se ejecuta cuando se cambia la posición seleccionada"""
        try:
            position = self.variables['position'].get().strip()
            if position and self.service:
                # Obtener aplicaciones filtradas por posición
                applications = self.service.get_applications_by_position_simple(position)
                app_names = [app['logical_access_name'] for app in applications]
                
                # Si no hay aplicaciones específicas para esta posición, mostrar todas las disponibles
                if not app_names:
                    all_applications = self.service.get_available_applications()
                    app_names = [app['name'] for app in all_applications]
                
                # Si aún no hay aplicaciones, usar valores por defecto
                if not app_names:
                    app_names = [
                        "JIRA",
                        "CONFLUENCE", 
                        "GITLAB",
                        "POWER BI",
                        "SAP",
                        "OFFICE 365",
                        "SALESFORCE",
                        "SERVICENOW",
                        "TABLEAU",
                        "SHAREPOINT"
                    ]
                
                # Actualizar el combobox de aplicaciones
                app_combobox = self._find_app_combobox()
                
                if app_combobox:
                    app_combobox['values'] = app_names
                    app_combobox.set('')  # Limpiar selección anterior
                    
                    # Mostrar mensaje informativo
                    print(f"Aplicaciones filtradas para posición '{position}': {len(app_names)} encontradas")
                    
        except Exception as e:
            print(f"Error actualizando aplicaciones por posición: {e}")
    
    def _find_app_combobox(self):
        """Encuentra el combobox de aplicaciones en la interfaz"""
        try:
            # Buscar el combobox de aplicaciones de manera más robusta
            for child in self.dialog.winfo_children():
                if isinstance(child, ttk.Frame):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, ttk.Combobox):
                            # Verificar si es el combobox de aplicaciones por su posición en el grid
                            grid_info = grandchild.grid_info()
                            if grid_info.get('row') == 3:  # La aplicación está en la fila 3 (índice 3)
                                return grandchild
            return None
        except Exception as e:
            print(f"Error encontrando combobox de aplicaciones: {e}")
            return None
    
    def _create_record(self):
        """Crea el registro manual"""
        try:
            # Validar campos obligatorios
            scotia_id = self.variables['scotia_id'].get().strip()
            position = self.variables['position'].get().strip()
            app_name = self.variables['app_name'].get().strip()
            responsible = self.variables['responsible'].get().strip()
            description = self.variables['description'].get().strip()
            
            if not scotia_id:
                messagebox.showerror("Error", "El ID de empleado es obligatorio")
                return
            
            if not position:
                messagebox.showerror("Error", "La posición es obligatoria")
                return
            
            if not app_name:
                messagebox.showerror("Error", "El nombre de la aplicación es obligatorio")
                return
            
            if not responsible:
                responsible = "Manual"
            
            if not description:
                description = None
            
            # Crear el registro
            if self.service:
                success, message = self.service.create_manual_access_record(
                    scotia_id, app_name, responsible, description, position
                )
                
                if success:
                    messagebox.showinfo("Éxito", message)
                    self.result = {
                        'scotia_id': scotia_id,
                        'position': position,
                        'app_name': app_name,
                        'responsible': responsible,
                        'description': description
                    }
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Error", message)
            else:
                messagebox.showerror("Error", "Servicio no disponible")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error creando registro: {str(e)}")
    
    def _cancel(self):
        """Cancela la operación"""
        self.dialog.destroy()

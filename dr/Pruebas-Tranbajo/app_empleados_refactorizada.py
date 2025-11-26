import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import pyodbc
from PIL import Image, ImageTk

from services import export_service, history_service, access_service, search_service
from ui import (CamposGeneralesFrame, OnboardingFrame, OffboardingFrame, 
                LateralMovementFrame, FlexStaffFrame, EdicionBusquedaFrame, CreacionPersonaFrame)
from ui.styles import aplicar_estilos_personalizados


class AppEmpleadosRefactorizada:
    """Aplicación principal integrada con sistema de conciliación"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("GAMLO - Sistema Integrado de Gestión de Empleados y Conciliación de Accesos")
        
        # Configuración responsive
        self.configurar_ventana_responsive()
        
        aplicar_estilos_personalizados()
        
        # Inicializar servicios (ya no se usa EmpleadoService)
        
        # Variables de control
        self.tipo_proceso_var = tk.StringVar()
        self.componentes = {}
        

        
        self.crear_interfaz()
    
    def configurar_ventana_responsive(self):
        """Configura la ventana para ser responsive"""
        # Obtener dimensiones de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Configurar dimensiones estándar
        window_width = min(int(screen_width * 0.8), 1400)
        window_height = min(int(screen_height * 0.8), 800)
        
        # Asegurar tamaño mínimo
        window_width = max(window_width, 800)
        window_height = max(window_height, 500)
        
        # Centrar la ventana
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Configurar tamaño mínimo
        self.root.minsize(800, 500)
        
        # Permitir redimensionamiento
        self.root.resizable(True, True)
    

        
    def crear_interfaz(self):
        """Crea la interfaz principal"""
        # Guardar referencia al frame principal para ajustes responsive
        self.main_frame = ttk.Frame(self.root, padding="25", style="Main.TFrame")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=25, pady=25)
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=0)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=0)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=0)
        
        # Frame para el header con título
        header_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 35), sticky="ew")
        header_frame.columnconfigure(0, weight=1)
        
        # Título con GAMLO
        titulo_label = ttk.Label(header_frame, text="GAMLO - Sistema Integrado de Gestión", 
                                style="Title.TLabel")
        titulo_label.grid(row=0, column=0, pady=(0, 0), sticky="ew")
        
        self.crear_botones_laterales(self.main_frame)
        self.crear_contenido_principal(self.main_frame)
        
        # Footer con logo GAMLO (abajo a la izquierda)
        self.crear_footer_con_logo(self.main_frame)
    
    def crear_footer_con_logo(self, parent):
        """Crea el footer con el logo GAMLO en la parte inferior izquierda"""
        # Frame para el footer
        footer_frame = ttk.Frame(parent, style="Main.TFrame")
        footer_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0), sticky="ew")
        footer_frame.columnconfigure(0, weight=0)
        footer_frame.columnconfigure(1, weight=1)
        
        # Logo GAMLO (abajo a la izquierda)
        self.crear_logo_gamlo_footer(footer_frame)
        
        # Espacio en blanco para empujar el logo a la izquierda
        ttk.Frame(footer_frame).grid(row=0, column=1, sticky="ew")
    
    def crear_logo_gamlo_footer(self, parent):
        """Crea el logo de GAMLO para el footer"""
        try:
            # Intentar cargar imagen del logo
            logo_path = os.path.join("images", "gamlo_logo.png")
            if os.path.exists(logo_path):
                # Cargar imagen real
                image = Image.open(logo_path)
                image = image.resize((48, 48), Image.Resampling.LANCZOS)  # Más pequeño para el footer
                self.logo_photo_footer = ImageTk.PhotoImage(image)
                logo_label = ttk.Label(parent, image=self.logo_photo_footer)
            else:
                # Crear logo de texto si no hay imagen
                logo_label = ttk.Label(parent, text="GAMLO", 
                                     font=("Arial", 12, "bold"),
                                     foreground="#2E86AB",
                                     background="#F8F9FA")
                # Crear un frame con borde para simular un logo
                logo_frame = ttk.Frame(parent, style="Logo.TFrame")
                logo_frame.grid(row=0, column=0, padx=(0, 10), pady=5)
                logo_label = ttk.Label(logo_frame, text="GAMLO", 
                                     font=("Arial", 10, "bold"),
                                     foreground="#2E86AB")
                logo_label.pack(padx=8, pady=8)
                return
            
            logo_label.grid(row=0, column=0, padx=(0, 10), pady=5)
            
        except Exception as e:
            # Fallback: crear logo de texto si hay error
            logo_label = ttk.Label(parent, text="GAMLO", 
                                 font=("Arial", 10, "bold"),
                                 foreground="#2E86AB")
            logo_label.grid(row=0, column=0, padx=(0, 10), pady=5)
    
    def crear_botones_laterales(self, parent):
        """Crea la navegación lateral"""
        # Guardar referencia al frame de navegación para ajustes responsive
        self.nav_frame = ttk.LabelFrame(parent, text="Navegación", padding="25", style="Nav.TLabelframe")
        self.nav_frame.grid(row=1, column=0, sticky="n", padx=(0, 30), pady=(0, 20))
        self.nav_frame.columnconfigure(0, weight=1)
        
        # Botones de navegación
        opciones = [
            ("📋 Gestión de Procesos", "gestion"),
            ("🔍 Edición y Búsqueda", "edicion"),
            ("👤 Crear Persona", "creacion"),
            ("🔐 Conciliación de Accesos", "conciliacion"),
            ("📱 Gestión de Aplicaciones", "aplicaciones")
        ]
        
        self.botones_navegacion = {}
        for i, (texto, valor) in enumerate(opciones):
            btn_container = ttk.Frame(self.nav_frame)
            btn_container.grid(row=i, column=0, pady=12, sticky="ew")
            btn_container.columnconfigure(0, weight=1)
            
            btn = ttk.Button(btn_container, text=texto, width=25, 
                           command=lambda v=valor: self.cambiar_contenido(v), style="Nav.TButton")
            btn.grid(row=0, column=0, sticky="ew", pady=5)
            self.botones_navegacion[valor] = btn
        
        # Botón de salida
        ttk.Button(self.nav_frame, text="🚪 Salir", width=25, 
                  command=self.root.quit, style="Salir.TButton").grid(row=len(opciones), column=0, pady=(20, 5))
        
        self.cambiar_contenido("gestion")
    
    def crear_contenido_principal(self, parent):
        """Crea el área de contenido principal"""
        self.contenido_principal_frame = ttk.Frame(parent)
        self.contenido_principal_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 30), pady=(0, 20))
        self.contenido_principal_frame.columnconfigure(0, weight=1)
        self.contenido_principal_frame.rowconfigure(0, weight=1)
        
        # Crear componentes
        self.crear_componente_gestion()
        self.crear_componente_edicion()
        self.crear_componente_creacion()
        self.crear_componente_conciliacion()
        self.crear_componente_aplicaciones()
        

    

        

    
    def crear_componente_gestion(self):
        """Crea el componente de gestión de procesos"""
        gestion_frame = ttk.Frame(self.contenido_principal_frame)
        gestion_frame.columnconfigure(0, weight=1)
        gestion_frame.rowconfigure(0, weight=0)
        gestion_frame.rowconfigure(1, weight=1)
        
        # Título
        ttk.Label(gestion_frame, text="Gestión de Procesos", 
                  style="Section.TLabel").grid(row=0, column=0, pady=(0, 25), sticky="ew")
        
        # Contenido
        contenido_frame = ttk.Frame(gestion_frame)
        contenido_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 25))
        contenido_frame.columnconfigure(0, weight=0)
        contenido_frame.columnconfigure(1, weight=1)
        contenido_frame.columnconfigure(2, weight=0)
        
        ttk.Label(contenido_frame, text="Complete la información del proceso", 
                 style="Subsection.TLabel").grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="ew")
        
        # Campos generales
        self.componentes['generales'] = CamposGeneralesFrame(contenido_frame)
        self.componentes['generales'].frame.grid(row=1, column=0, sticky="ew", pady=(0, 20), padx=(25, 15))
        
        # Pestañas de proceso
        self.crear_pestanas_proceso(contenido_frame)
        
        # Botones de acción
        self.crear_botones_accion(contenido_frame)
        
        self.componentes['gestion_frame'] = gestion_frame
        

    

    
    def crear_pestanas_proceso(self, parent):
        """Crea el sistema de pestañas para tipos de proceso"""
        pestanas_frame = ttk.LabelFrame(parent, text="Tipo de Proceso", padding="15")
        pestanas_frame.grid(row=1, column=1, sticky="ew", pady=(0, 20), padx=(15, 25))
        pestanas_frame.columnconfigure(0, weight=1)
        pestanas_frame.rowconfigure(1, weight=1)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(pestanas_frame)
        self.notebook.grid(row=1, column=0, sticky="ew", pady=(15, 0), padx=15)
        
        # Pestaña de selección
        seleccion_frame = ttk.Frame(self.notebook)
        self.notebook.add(seleccion_frame, text="Seleccionar Proceso")
        seleccion_frame.columnconfigure(0, weight=1)
        
        ttk.Label(seleccion_frame, text="Seleccione el tipo de proceso:", 
                 style="Normal.TLabel").grid(row=0, column=0, pady=20, sticky="ew")
        
        # Opciones de proceso
        opciones = [("Onboarding", "onboarding"), ("Offboarding", "offboarding"), ("Lateral Movement", "lateral"), ("Flex Staff", "flex_staff")]
        for i, (texto, valor) in enumerate(opciones):
            ttk.Radiobutton(seleccion_frame, text=texto, variable=self.tipo_proceso_var, 
                           value=valor, command=self.cambiar_pestana).grid(row=i+1, column=0, pady=8, sticky="ew")
        
        # Inicializar pestañas dinámicas
        self.pestanas_dinamicas = {'onboarding': None, 'offboarding': None, 'lateral': None}
    
    def cambiar_pestana(self):
        """Cambia la pestaña según la selección"""
        # Ocultar todas las pestañas dinámicas
        for pestana in self.pestanas_dinamicas.values():
            if pestana:
                self.notebook.hide(pestana)
        
        tipo_seleccionado = self.tipo_proceso_var.get()
        
        # Crear y mostrar pestaña correspondiente
        if tipo_seleccionado in self.pestanas_dinamicas:
            if not self.pestanas_dinamicas[tipo_seleccionado]:
                self.crear_pestana_dinamica(tipo_seleccionado)
            self.notebook.add(self.pestanas_dinamicas[tipo_seleccionado], text=tipo_seleccionado.title())
    
    def crear_pestana_dinamica(self, tipo):
        """Crea una pestaña dinámica según el tipo"""
        try:
            frame_classes = {
                'onboarding': OnboardingFrame,
                'offboarding': OffboardingFrame,
                'lateral': LateralMovementFrame,
                'flex_staff': FlexStaffFrame
            }
            
            if tipo in frame_classes:
                self.componentes[tipo] = frame_classes[tipo](self.notebook)
                self.pestanas_dinamicas[tipo] = self.componentes[tipo].frame
            else:
                print(f"Error: Tipo {tipo} no soportado")
                
        except Exception as e:
            print(f"Error creando pestaña {tipo}: {e}")
    

    
    def crear_botones_accion(self, parent):
        """Crea los botones de acción"""
        botones_frame = ttk.Frame(parent)
        botones_frame.grid(row=1, column=2, pady=40, padx=(30, 0), sticky="n")  # Aumentar espaciado
        botones_frame.columnconfigure(0, weight=1)
        
        # Botones con estilos predefinidos
        botones_info = [
            ("💾 Guardar", self.guardar_datos, "Success.TButton"),
            ("🧹 Limpiar", self.limpiar_campos, "Info.TButton"),
            ("🚪 Salir", self.root.quit, "Danger.TButton")
        ]
        
        for i, (texto, comando, estilo) in enumerate(botones_info):
            btn = ttk.Button(botones_frame, text=texto, command=comando, width=25, style=estilo)  # Aumentar ancho
            btn.grid(row=i, column=0, pady=12, sticky="ew")  # Aumentar espaciado
    
    def crear_componente_edicion(self):
        """Crea el componente de edición y búsqueda"""
        self.componentes['edicion_busqueda'] = EdicionBusquedaFrame(self.contenido_principal_frame, access_service)
        self.componentes['edicion_busqueda'].frame.grid(row=0, column=0, sticky="nsew")
        self.componentes['edicion_busqueda'].frame.grid_remove()
    
    def crear_componente_creacion(self):
        """Crea el componente de creación de persona"""
        try:
            print("Creando componente de creación...")
            self.componentes['creacion_persona'] = CreacionPersonaFrame(self.contenido_principal_frame, search_service)
            self.componentes['creacion_persona'].frame.grid(row=0, column=0, sticky="nsew")
            self.componentes['creacion_persona'].frame.grid_remove()
            print("Componente de creación creado exitosamente")
        except Exception as e:
            print(f"Error creando componente de creación: {e}")
            import traceback
            traceback.print_exc()
    
    def crear_componente_conciliacion(self):
        """Crea el componente de conciliación de accesos"""
        self.componentes['conciliacion'] = ConciliacionFrame(self.contenido_principal_frame)
        self.componentes['conciliacion'].frame.grid(row=0, column=0, sticky="nsew")
        self.componentes['conciliacion'].frame.grid_remove()
    
    def crear_componente_aplicaciones(self):
        """Crea el componente de gestión de aplicaciones"""
        self.componentes['aplicaciones'] = AplicacionesFrame(self.contenido_principal_frame)
        self.componentes['aplicaciones'].frame.grid(row=0, column=0, sticky="nsew")
        self.componentes['aplicaciones'].frame.grid_remove()
    
    
    def cambiar_contenido(self, tipo_contenido):
        """Cambia el contenido mostrado según el botón seleccionado"""
        # Ocultar todos los componentes
        componentes_a_ocultar = ['gestion_frame', 'edicion_busqueda', 'creacion_persona', 'conciliacion', 'aplicaciones']
        for comp in componentes_a_ocultar:
            if comp in self.componentes:
                if comp == 'gestion_frame':
                    self.componentes[comp].grid_remove()
                else:
                    self.componentes[comp].frame.grid_remove()
        
        # Mostrar el componente seleccionado
        if tipo_contenido == "gestion" and 'gestion_frame' in self.componentes:
            self.componentes['gestion_frame'].grid()
        elif tipo_contenido == "edicion" and 'edicion_busqueda' in self.componentes:
            self.componentes['edicion_busqueda'].frame.grid()
        elif tipo_contenido == "creacion" and 'creacion_persona' in self.componentes:
            self.componentes['creacion_persona'].frame.grid()
        elif tipo_contenido == "conciliacion" and 'conciliacion' in self.componentes:
            self.componentes['conciliacion'].frame.grid()
        elif tipo_contenido == "aplicaciones" and 'aplicaciones' in self.componentes:
            self.componentes['aplicaciones'].frame.grid()
        
        # Actualizar estado visual de los botones
        for valor, btn in self.botones_navegacion.items():
            btn.state(['pressed'] if valor == tipo_contenido else ['!pressed'])
    
    def guardar_datos(self):
        """Guarda los datos del formulario en la nueva estructura de base de datos"""
        try:
            # Obtener datos generales
            if 'generales' not in self.componentes:
                messagebox.showerror("Error", "No se encontró el componente de campos generales")
                return
                
            datos_generales = self.componentes['generales'].obtener_datos()
            
            # Validar campos obligatorios
            campos_vacios = self.componentes['generales'].validar_campos_obligatorios()
            if campos_vacios:
                messagebox.showerror("Error", f"Por favor complete los campos obligatorios: {', '.join(campos_vacios)}")
                return
            
            # Obtener tipo de proceso
            tipo_proceso = self.tipo_proceso_var.get()
            if not tipo_proceso:
                messagebox.showerror("Error", "Por favor seleccione un tipo de proceso")
                return
            
            # Obtener datos específicos según el tipo
            datos_especificos = {}
            if tipo_proceso in self.componentes:
                try:
                    if hasattr(self.componentes[tipo_proceso], 'obtener_datos'):
                        datos_especificos = self.componentes[tipo_proceso].obtener_datos()
                except Exception as e:
                    print(f"Error obteniendo datos específicos de {tipo_proceso}: {e}")
            
            # Obtener SID del empleado
            scotia_id = datos_generales.get('sid', '')
            if not scotia_id:
                messagebox.showerror("Error", "El SID es obligatorio")
                return
            
            # Obtener responsable del formulario
            responsable = datos_generales.get('ingreso_por', 'Sistema')
            if not responsable:
                responsable = 'Sistema'
            
            # Procesar según el tipo de proceso usando la nueva estructura
            if tipo_proceso == 'onboarding':
                # Para onboarding, solo procesamos los accesos (el empleado debe existir previamente)
                # o se debe crear desde la sección "Crear Persona"
                
                # Verificar si el empleado existe
                empleado_existente = access_service.get_employee_by_id(scotia_id)
                if not empleado_existente:
                    messagebox.showerror("Error", 
                        f"El empleado {scotia_id} no existe en el headcount.\n"
                        "Por favor, cree primero el empleado en la sección 'Crear Persona'.")
                    return
                
                # Procesar onboarding
                success, message, records = access_service.process_employee_onboarding(
                    scotia_id, 
                    datos_generales.get('nuevo_cargo', ''), 
                    datos_generales.get('nueva_unidad_subunidad', ''),  # Corregir nombre del campo
                    responsable
                )
                
                if success:
                    messagebox.showinfo("Éxito", f"Onboarding procesado exitosamente.\n{message}")
                    self.limpiar_campos()
                else:
                    messagebox.showerror("Error", message)
                    
            elif tipo_proceso == 'offboarding':
                # Procesar offboarding
                success, message, records = access_service.process_employee_offboarding(scotia_id, responsable)
                
                if success:
                    messagebox.showinfo("Éxito", f"Offboarding procesado exitosamente.\n{message}")
                    self.limpiar_campos()
                else:
                    messagebox.showerror("Error", message)
                    
            elif tipo_proceso == 'lateral':
                # Procesar movimiento lateral
                nueva_unidad_subunidad = datos_generales.get('nueva_unidad_subunidad', '')
                # Separar unidad y subunidad si es necesario
                if '/' in nueva_unidad_subunidad:
                    nueva_unidad, nueva_subunidad = nueva_unidad_subunidad.split('/', 1)
                else:
                    nueva_unidad = nueva_unidad_subunidad
                    nueva_subunidad = None
                
                success, message, records = access_service.process_lateral_movement(
                    scotia_id,
                    datos_generales.get('nuevo_cargo', ''),
                    nueva_unidad,
                    responsable,
                    nueva_subunidad
                )
                
                if success:
                    messagebox.showinfo("Éxito", f"Movimiento lateral procesado exitosamente.\n{message}")
                    self.limpiar_campos()
                else:
                    messagebox.showerror("Error", message)
                    
            elif tipo_proceso == 'flex_staff':
                # Procesar asignación flex staff
                datos_flex = self.componentes.get('flex_staff', {}).obtener_datos() if 'flex_staff' in self.componentes else {}
                
                # Mapear nombres a los nombres reales de la BD
                temp_position = datos_generales.get('nuevo_cargo', '')
                temp_unit = datos_generales.get('nueva_unidad_subunidad', '')  # Corregir nombre del campo
                mapped_position, mapped_unit, mapped_unidad_subunidad = self.mapear_nombres_bd(temp_position, temp_unit)
                
                print(f"FLEX STAFF - Mapeo de nombres:")
                print(f"  Original: '{temp_position}' + '{temp_unit}'")
                print(f"  Mapeado: '{mapped_position}' + '{mapped_unit}' + '{mapped_unidad_subunidad}'")
                
                success, message, records = access_service.process_flex_staff_assignment(
                    scotia_id,
                    mapped_position,  # temporary_position (mapeado)
                    mapped_unit,  # temporary_unit (mapeado)
                    mapped_unit,  # temporary_subunit (mapeado)
                    datos_flex.get('duracion_dias'),  # duration_days
                    responsable  # responsible
                )
                
                if success:
                    messagebox.showinfo("Éxito", f"Asignación flex staff procesada exitosamente.\n{message}")
                    self.limpiar_campos()
                else:
                    messagebox.showerror("Error", message)
            else:
                messagebox.showerror("Error", f"Tipo de proceso no soportado: {tipo_proceso}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
            print(f"Error en guardar_datos: {e}")
    
    def limpiar_campos(self):
        """Limpia todos los campos del formulario"""
        try:
            # Limpiar campos generales
            if 'generales' in self.componentes:
                self.componentes['generales'].limpiar()
            
            # Limpiar campos específicos
            for componente in self.componentes.values():
                if hasattr(componente, 'limpiar'):
                    componente.limpiar()
            
            # Limpiar selección de tipo de proceso
            self.tipo_proceso_var.set("")
            
            # Ocultar pestañas dinámicas
            if hasattr(self, 'pestanas_dinamicas'):
                for pestana in self.pestanas_dinamicas.values():
                    if pestana:
                        self.notebook.hide(pestana)
                        
        except Exception as e:
            print(f"Error en limpiar_campos: {e}")
    
    
    def mapear_nombres_bd(self, position, unit):
        """Mapea los nombres de los desplegables a los nombres reales de la BD"""
        # Mapeo de unidades
        unit_mapping = {
            'RRHH': 'Recursos Humanos',
            'TECNOLOGÍA': 'Tecnologia',
            'TECNOLOGIA': 'Tecnologia'
        }
        
        # Mapeo de posiciones
        position_mapping = {
            'GERENTE DE RECURSOS HUMANOS': 'Gerente',
            'GERENTE RECURSOS HUMANOS': 'Gerente',
            'GERENTE RRHH': 'Gerente',
            'ANALISTA SENIOR': 'Analista',
            'DESARROLLADOR': 'Desarrollador',
            'ADMINISTRADOR': 'Administrador'
        }
        
        # Aplicar mapeos
        mapped_unit = unit_mapping.get(unit.upper(), unit)
        mapped_position = position_mapping.get(position.upper(), position)
        
        # Construir unidad_subunidad
        if mapped_unit == 'Tecnologia':
            unidad_subunidad = 'Tecnología/Desarrollo'
        elif mapped_unit == 'Recursos Humanos':
            unidad_subunidad = 'Recursos Humanos/RRHH'
        else:
            unidad_subunidad = f"{mapped_unit}/General"
        
        return mapped_position, mapped_unit, unidad_subunidad
    
class ConciliacionFrame:
    """Frame simplificado para la conciliación de accesos"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
        # Variables de control
        self.sid_var = tk.StringVar()
        self.resultado_conciliacion = None
        
        self._crear_interfaz()
    
    def _crear_interfaz(self):
        """Crea la interfaz de conciliación"""
        # Título principal
        ttk.Label(self.frame, text="🔐 Sistema de Conciliación de Accesos", 
                  style="Title.TLabel").grid(row=0, column=0, pady=(0, 30), sticky="ew")
        
        # Frame principal con dos columnas
        main_content = ttk.Frame(self.frame)
        main_content.grid(row=1, column=0, sticky="nsew", padx=20)
        main_content.columnconfigure(0, weight=1)
        main_content.columnconfigure(1, weight=1)
        main_content.rowconfigure(1, weight=1)
        
        # Columna izquierda - Entrada de datos
        self._crear_seccion_entrada(main_content)
        
        # Columna derecha - Resultados y acciones
        self._crear_seccion_acciones(main_content)
    
    def _crear_seccion_entrada(self, parent):
        """Crea la sección de entrada de datos"""
        entrada_frame = ttk.LabelFrame(parent, text="📝 Datos de Entrada", padding="20")
        entrada_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 20))
        entrada_frame.columnconfigure(0, weight=1)
        
        # Campo SID
        ttk.Label(entrada_frame, text="SID del Empleado:", 
                 style="Subsection.TLabel").grid(row=0, column=0, pady=(0, 10), sticky="w")
        
        sid_entry = ttk.Entry(entrada_frame, textvariable=self.sid_var, width=30)
        sid_entry.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        
        # Botones de conciliación
        ttk.Button(entrada_frame, text="🔍 Conciliar Accesos", 
                  command=self._conciliar_accesos, style="Success.TButton").grid(row=2, column=0, pady=(0, 10), sticky="ew")
        
        ttk.Button(entrada_frame, text="⚡ Asignar Accesos Automáticamente", 
                  command=self._asignar_accesos_automaticos, style="Warning.TButton").grid(row=3, column=0, pady=(0, 10), sticky="ew")
        
        
        # Información adicional
        info_text = ("Este sistema compara los accesos actuales de un empleado\n"
                    "con los accesos que debería tener según su puesto.\n"
                    "Identifica accesos faltantes y excesivos.")
        ttk.Label(entrada_frame, text=info_text, style="Subsection.TLabel", 
                 justify="center").grid(row=4, column=0, pady=(20, 0), sticky="ew")
    
    def _crear_seccion_acciones(self, parent):
        """Crea la sección de acciones y resultados"""
        acciones_frame = ttk.LabelFrame(parent, text="⚡ Acciones y Resultados", padding="20")
        acciones_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 20))
        acciones_frame.columnconfigure(0, weight=1)
        acciones_frame.rowconfigure(2, weight=1)
        
        # Botones de acción
        botones_frame = ttk.Frame(acciones_frame)
        botones_frame.grid(row=0, column=0, pady=(0, 15), sticky="ew")
        botones_frame.columnconfigure(0, weight=1)
        botones_frame.columnconfigure(1, weight=1)
        
        ttk.Button(botones_frame, text="📤 Exportar Excel", 
                  command=self._exportar_excel, style="Warning.TButton").grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        ttk.Button(botones_frame, text="👁️ Ver Accesos Actuales", 
                  command=self._ver_accesos_actuales, style="Success.TButton").grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        # Panel de estadísticas resumidas
        self._crear_panel_estadisticas(acciones_frame)
        
        # Área de resultados
        resultados_frame = ttk.LabelFrame(acciones_frame, text="📊 Resultados de Conciliación", padding="15")
        resultados_frame.grid(row=2, column=0, sticky="nsew")
        resultados_frame.columnconfigure(0, weight=1)
        resultados_frame.rowconfigure(0, weight=1)
        
        # Treeview para mostrar resultados con campos de conciliación estricta
        columns = ('Acceso', 'Unidad', 'Subunidad', 'Posición', 'Rol', 'Estado', 'Acción')
        self.tree_resultados = ttk.Treeview(resultados_frame, columns=columns, show='headings', height=8)
        
        # Configurar columnas con anchos específicos y minwidth
        column_widths = {
            'Acceso': 200,
            'Unidad': 150,
            'Subunidad': 150,
            'Posición': 150,
            'Rol': 120,
            'Estado': 100,
            'Acción': 100
        }
        
        for col in columns:
            self.tree_resultados.heading(col, text=col)
            self.tree_resultados.column(col, width=column_widths.get(col, 120), minwidth=100, anchor="center")
        
        # Scrollbars (vertical y horizontal)
        vsb = ttk.Scrollbar(resultados_frame, orient="vertical", command=self.tree_resultados.yview)
        hsb = ttk.Scrollbar(resultados_frame, orient="horizontal", command=self.tree_resultados.xview)
        self.tree_resultados.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid
        self.tree_resultados.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Mensaje inicial
        self.tree_resultados.insert('', 'end', values=('', '', '', '', '', 'Sin datos', ''))
    
    def _conciliar_accesos(self):
        """Ejecuta la conciliación de accesos para un SID específico usando la nueva estructura"""
        sid = self.sid_var.get().strip()
        if not sid:
            messagebox.showerror("Error", "Por favor ingrese un SID válido")
            return
        
        try:
            # Verificar si el empleado existe y tiene datos necesarios
            empleado = access_service.get_employee_by_id(sid)
            if not empleado:
                messagebox.showerror("Error", f"El empleado {sid} no existe en el headcount")
                return
            
            # Verificar si tiene posición y unidad
            if not empleado.get('position') or not empleado.get('unit'):
                respuesta = messagebox.askyesno(
                    "Datos Incompletos", 
                    f"El empleado {sid} no tiene posición o unidad definida.\n\n"
                    "¿Desea usar datos de ejemplo para probar la conciliación?\n"
                    "(Se asignará: ANALISTA SENIOR - TECNOLOGÍA)"
                )
                
                if respuesta:
                    # Actualizar con datos de ejemplo
                    conn = access_service.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE headcount 
                        SET position = 'ANALISTA SENIOR', unit = 'TECNOLOGÍA'
                        WHERE scotia_id = ?
                    """, (sid,))
                    conn.commit()
                    conn.close()
                    
                    # Crear aplicaciones de ejemplo si no existen
                    
                    messagebox.showinfo("Datos Actualizados", 
                        "Se han asignado datos de ejemplo al empleado.\n"
                        "Ahora puede proceder con la conciliación.")
                else:
                    return
            
            # Usar el nuevo servicio de conciliación
            reporte = access_service.get_access_reconciliation_report(sid)
            
            if "error" in reporte:
                messagebox.showerror("Error", reporte["error"])
                return
            
            self.resultado_conciliacion = reporte
            if reporte.get('success', False):
                data = reporte.get('data', {})
                self._mostrar_resultados_nuevos(data)
                messagebox.showinfo("Éxito", f"Conciliación completada para {sid}")
            else:
                messagebox.showerror("Error", reporte.get('message', 'Error desconocido'))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la conciliación: {str(e)}")
    
    
    def _asignar_accesos_automaticos(self):
        """Asigna accesos automáticamente según la unit y position del empleado"""
        sid = self.sid_var.get().strip()
        if not sid:
            messagebox.showerror("Error", "Por favor ingrese un SID válido")
            return
        
        try:
            # Confirmar la acción
            result = messagebox.askyesno(
                "Confirmar Asignación Automática",
                f"¿Está seguro de que desea asignar accesos automáticamente para {sid}?\n\n"
                "Esto creará tickets 'Pendiente' para los accesos que faltan y revocará los excesivos."
            )
            
            if not result:
                return
            
            # Llamar al método assign_accesses del servicio
            success, message, counts = access_service.assign_accesses(sid, "Sistema")
            
            if success:
                # Mostrar resultados
                resultado_texto = f"✅ {message}\n\n"
                resultado_texto += f"📊 Resumen:\n"
                resultado_texto += f"• Accesos otorgados: {counts['granted']}\n"
                resultado_texto += f"• Accesos revocados: {counts['revoked']}\n\n"
                resultado_texto += f"Los tickets han sido creados con estado 'Pendiente' en el historial."
                
                messagebox.showinfo("Asignación Completada", resultado_texto)
                
                # Actualizar la conciliación para mostrar los cambios
                self._conciliar_accesos()
                
            else:
                messagebox.showerror("Error", f"Error en la asignación automática: {message}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la asignación automática: {str(e)}")
    
    
    def _exportar_excel(self):
        """Exporta los resultados de conciliación a Excel con información detallada"""
        # Verificar si hay un SID ingresado
        sid = self.sid_var.get().strip()
        if not sid:
            messagebox.showwarning("Advertencia", "Por favor ingrese un SID antes de exportar")
            return
        
        # Si no hay resultados de conciliación, ejecutar conciliación primero
        if not self.resultado_conciliacion:
            respuesta = messagebox.askyesno("Sin resultados", 
                                          "No hay resultados de conciliación. ¿Desea ejecutar la conciliación primero?")
            if respuesta:
                self._conciliar_accesos()
                # Verificar si ahora hay resultados
                if not self.resultado_conciliacion:
                    messagebox.showwarning("Advertencia", "No se pudieron obtener resultados de conciliación")
                    return
            else:
                return
        
        try:
            # Crear archivo Excel personalizado con información detallada
            output_path = self._crear_excel_detallado()
            
            messagebox.showinfo("Éxito", f"Archivo exportado exitosamente a:\n{output_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    def _crear_excel_detallado(self):
        """Crea un archivo Excel detallado con la conciliación de accesos"""
        import pandas as pd
        from datetime import datetime
        import os
        from pathlib import Path
        
        # Determinar carpeta de descargas del usuario
        downloads_dir = Path.home() / "Downloads"
        fallback_dir = Path("output")
        
        try:
            downloads_dir.mkdir(parents=True, exist_ok=True)
            output_dir = downloads_dir
        except Exception as e:
            # Si no se puede crear en Descargas, usar carpeta local output
            fallback_dir.mkdir(parents=True, exist_ok=True)
            output_dir = fallback_dir
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sid = self.sid_var.get().strip()
        filename = f"conciliacion_accesos_{sid}_{timestamp}.xlsx"
        filepath = str(Path(output_dir) / filename)
        
        # Obtener datos del reporte
        reporte = self.resultado_conciliacion
        if reporte.get('success', False):
            data = reporte.get('data', {})
            employee = data.get('employee', {})
            current_access = data.get('current_access', [])
            to_grant = data.get('to_grant', [])
            to_revoke = data.get('to_revoke', [])
        else:
            messagebox.showerror("Error", "No hay datos de conciliación para exportar")
            return None
        
        # Función para agrupar accesos (misma lógica que en la tabla)
        def agrupar_accesos_para_excel(accesos):
            grupos = {}
            for acceso in accesos:
                app_name = acceso.get('app_name', '')
                if app_name not in grupos:
                    grupos[app_name] = {
                        'app_name': app_name,
                        'unit': acceso.get('unit', ''),
                        'subunit': acceso.get('subunit', ''),
                        'position_role': acceso.get('position_role', ''),
                        'roles': set(),
                        'description': acceso.get('description', '')
                    }
                # Agregar rol si existe
                role_name = acceso.get('role_name', '')
                if role_name and role_name != 'Sin rol':
                    grupos[app_name]['roles'].add(role_name)
            return list(grupos.values())
        
        # Agrupar accesos
        current_grouped = agrupar_accesos_para_excel(current_access)
        to_grant_grouped = agrupar_accesos_para_excel(to_grant)
        to_revoke_grouped = agrupar_accesos_para_excel(to_revoke)
        
        # Crear DataFrame para accesos actuales
        current_df = pd.DataFrame([
            {
                'Acceso': acceso['app_name'],
                'Unidad': acceso['unit'],
                'Subunidad': acceso['subunit'],
                'Posición': acceso['position_role'],
                'Rol': ', '.join(sorted(acceso['roles'])) if acceso['roles'] else 'Sin rol',
                'Estado': '✅ Activo',
                'Acción': 'Mantener',
                'Descripción': acceso['description']
            }
            for acceso in current_grouped
        ])
        
        # Crear DataFrame para accesos a otorgar
        grant_df = pd.DataFrame([
            {
                'Acceso': acceso['app_name'],
                'Unidad': acceso['unit'],
                'Subunidad': acceso['subunit'],
                'Posición': acceso['position_role'],
                'Rol': ', '.join(sorted(acceso['roles'])) if acceso['roles'] else 'Sin rol',
                'Estado': '❌ Faltante',
                'Acción': '🟢 Otorgar',
                'Descripción': acceso['description']
            }
            for acceso in to_grant_grouped
        ])
        
        # Crear DataFrame para accesos a revocar
        revoke_df = pd.DataFrame([
            {
                'Acceso': acceso['app_name'],
                'Unidad': acceso['unit'],
                'Subunidad': acceso['subunit'],
                'Posición': acceso['position_role'],
                'Rol': ', '.join(sorted(acceso['roles'])) if acceso['roles'] else 'Sin rol',
                'Estado': '⚠️ Excesivo',
                'Acción': '🔴 Revocar',
                'Descripción': acceso['description']
            }
            for acceso in to_revoke_grouped
        ])
        
        # Crear DataFrame de resumen
        total_actions = len(to_grant_grouped) + len(to_revoke_grouped)
        summary_data = {
            'Métrica': [
                'Total Accesos Activos',
                'Accesos a Otorgar',
                'Accesos a Revocar',
                'Total Acciones Requeridas',
                'Estado de Conciliación'
            ],
            'Cantidad': [
                len(current_grouped),
                len(to_grant_grouped),
                len(to_revoke_grouped),
                total_actions,
                '✅ Conciliado' if total_actions == 0 else '⚠️ Requiere Acción'
            ],
            'Descripción': [
                'Accesos que el empleado tiene actualmente y debe mantener',
                'Accesos que faltan y deben ser otorgados',
                'Accesos excesivos que deben ser revocados',
                'Total de cambios requeridos en los accesos',
                'Estado general de la conciliación de accesos'
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        
        # Crear archivo Excel con múltiples hojas
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Hoja de resumen
            summary_df.to_excel(writer, sheet_name='Resumen', index=False)
            
            # Hoja de accesos actuales
            if not current_df.empty:
                current_df.to_excel(writer, sheet_name='Accesos Activos', index=False)
            else:
                pd.DataFrame(columns=['Acceso', 'Unidad', 'Subunidad', 'Posición', 'Rol', 'Estado', 'Acción', 'Descripción']).to_excel(writer, sheet_name='Accesos Activos', index=False)
            
            # Hoja de accesos a otorgar
            if not grant_df.empty:
                grant_df.to_excel(writer, sheet_name='A Otorgar', index=False)
            else:
                pd.DataFrame(columns=['Acceso', 'Unidad', 'Subunidad', 'Posición', 'Rol', 'Estado', 'Acción', 'Descripción']).to_excel(writer, sheet_name='A Otorgar', index=False)
            
            # Hoja de accesos a revocar
            if not revoke_df.empty:
                revoke_df.to_excel(writer, sheet_name='A Revocar', index=False)
            else:
                pd.DataFrame(columns=['Acceso', 'Unidad', 'Subunidad', 'Posición', 'Rol', 'Estado', 'Acción', 'Descripción']).to_excel(writer, sheet_name='A Revocar', index=False)
            
            # Hoja de información del empleado
            employee_info = pd.DataFrame([
                {'Campo': 'SID', 'Valor': employee.get('scotia_id', '')},
                {'Campo': 'Nombre', 'Valor': employee.get('full_name', '')},
                {'Campo': 'Email', 'Valor': employee.get('email', '')},
                {'Campo': 'Unidad', 'Valor': employee.get('unit', '')},
                {'Campo': 'Subunidad', 'Valor': employee.get('subunit', '')},
                {'Campo': 'Posición', 'Valor': employee.get('position', '')},
                {'Campo': 'Fecha Conciliación', 'Valor': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            ])
            employee_info.to_excel(writer, sheet_name='Info Empleado', index=False)
            
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
        
        return filepath
    
    def _mostrar_resultados_nuevos(self, reporte):
        """Muestra los resultados de conciliación usando la nueva estructura con campos estrictos"""
        # Limpiar treeview
        self.tree_resultados.delete(*self.tree_resultados.get_children())
        
        # Agrupar accesos por nombre para evitar duplicados
        def agrupar_accesos(accesos):
            grupos = {}
            for acceso in accesos:
                app_name = acceso.get('app_name', '')
                if app_name not in grupos:
                    grupos[app_name] = {
                        'app_name': app_name,
                        'unit': acceso.get('unit', ''),
                        'subunit': acceso.get('subunit', ''),
                        'position_role': acceso.get('position_role', ''),
                        'roles': set(),
                        'status': acceso.get('status', ''),
                        'date': acceso.get('date')
                    }
                # Agregar rol si existe
                role_name = acceso.get('role_name', '')
                if role_name and role_name != 'Sin rol':
                    grupos[app_name]['roles'].add(role_name)
            return list(grupos.values())
        
        # Mostrar accesos actuales
        current_access = reporte.get('current_access', [])
        current_grouped = agrupar_accesos(current_access)
        for acceso in current_grouped:
            roles_text = ', '.join(sorted(acceso['roles'])) if acceso['roles'] else 'Sin rol'
            self.tree_resultados.insert('', 'end', values=(
                acceso['app_name'],
                acceso['unit'],
                acceso['subunit'],
                acceso['position_role'],
                roles_text,
                '✅ Activo',
                'Mantener'
            ))
        
        # Mostrar accesos a otorgar
        to_grant = reporte.get('to_grant', [])
        to_grant_grouped = agrupar_accesos(to_grant)
        for acceso in to_grant_grouped:
            roles_text = ', '.join(sorted(acceso['roles'])) if acceso['roles'] else 'Sin rol'
            self.tree_resultados.insert('', 'end', values=(
                acceso['app_name'],
                acceso['unit'],
                acceso['subunit'],
                acceso['position_role'],
                roles_text,
                '❌ Faltante',
                '🟢 Otorgar'
            ))
        
        # Mostrar accesos a revocar
        to_revoke = reporte.get('to_revoke', [])
        to_revoke_grouped = agrupar_accesos(to_revoke)
        for acceso in to_revoke_grouped:
            roles_text = ', '.join(sorted(acceso['roles'])) if acceso['roles'] else 'Sin rol'
            self.tree_resultados.insert('', 'end', values=(
                acceso['app_name'],
                acceso['unit'],
                acceso['subunit'],
                acceso['position_role'],
                roles_text,
                '⚠️ Excesivo',
                '🔴 Revocar'
            ))
        
        # Si no hay datos, mostrar mensaje
        if not current_access and not to_grant and not to_revoke:
            self.tree_resultados.insert('', 'end', values=('', '', '', '', '', 'Sin datos', ''))
        
        # Actualizar estadísticas
        self._actualizar_estadisticas(reporte)
    
    def _crear_panel_estadisticas(self, parent):
        """Crea el panel de estadísticas resumidas"""
        stats_frame = ttk.LabelFrame(parent, text="📈 Resumen de Conciliación", padding="10")
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        
        # Labels para estadísticas
        self.label_activos = ttk.Label(stats_frame, text="✅ Activos: 0", 
                                      style="Success.TLabel", font=("Arial", 10, "bold"))
        self.label_activos.grid(row=0, column=0, padx=5, pady=5)
        
        self.label_otorgar = ttk.Label(stats_frame, text="🟢 A Otorgar: 0", 
                                      style="Info.TLabel", font=("Arial", 10, "bold"))
        self.label_otorgar.grid(row=0, column=1, padx=5, pady=5)
        
        self.label_revocar = ttk.Label(stats_frame, text="🔴 A Revocar: 0", 
                                      style="Danger.TLabel", font=("Arial", 10, "bold"))
        self.label_revocar.grid(row=0, column=2, padx=5, pady=5)
    
    def _actualizar_estadisticas(self, reporte):
        """Actualiza las estadísticas del panel"""
        current_access = reporte.get('current_access', [])
        to_grant = reporte.get('to_grant', [])
        to_revoke = reporte.get('to_revoke', [])
        
        self.label_activos.config(text=f"✅ Activos: {len(current_access)}")
        self.label_otorgar.config(text=f"🟢 A Otorgar: {len(to_grant)}")
        self.label_revocar.config(text=f"🔴 A Revocar: {len(to_revoke)}")
    
    def actualizar_conciliacion_empleado(self, scotia_id):
        """Actualiza la conciliación para un empleado específico"""
        if scotia_id and scotia_id.strip():
            self.sid_var.set(scotia_id.strip())
            self._conciliar_accesos()
    
    def _ver_accesos_actuales(self):
        """Muestra los accesos actuales del empleado en una ventana separada"""
        sid = self.sid_var.get().strip()
        if not sid:
            messagebox.showwarning("Advertencia", "Por favor ingrese un SID")
            return
        
        try:
            # Obtener información del empleado
            empleado = access_service.get_employee_by_id(sid)
            if not empleado:
                messagebox.showerror("Error", f"Empleado {sid} no encontrado")
                return
            
            # Obtener todos los tipos de accesos actuales
            accesos_actuales = access_service.get_employee_current_position_access(sid)
            
            # Formatear datos para la ventana
            accesos_formateados = []
            for acceso in accesos_actuales:
                # Formatear fecha
                fecha = acceso.get('record_date', '')
                try:
                    if fecha:
                        fecha_obj = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
                        fecha_formateada = fecha_obj.strftime('%d/%m/%Y %H:%M')
                    else:
                        fecha_formateada = 'N/A'
                except:
                    fecha_formateada = fecha or 'N/A'
                
                accesos_formateados.append({
                    'app_name': acceso.get('logical_access_name', ''),
                    'unit': acceso.get('unit', ''),
                    'position': acceso.get('position_role', ''),
                    'process': acceso.get('process_access', ''),
                    'date': fecha_formateada,
                    'description': acceso.get('event_description', ''),
                    'status': acceso.get('status', ''),
                    'role': acceso.get('role_name', ''),
                    'access_type': acceso.get('access_type', 'Otro')
                })
            
            # Crear ventana de accesos actuales
            self._crear_ventana_accesos_actuales(sid, empleado, accesos_formateados)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error obteniendo accesos actuales: {str(e)}")

    def _crear_ventana_accesos_actuales(self, sid, empleado, accesos_actuales):
        """Crea una ventana para mostrar los accesos actuales del empleado"""
        # Crear ventana
        ventana = tk.Toplevel(self.parent)
        ventana.title(f"Accesos Actuales - {sid}")
        ventana.geometry("800x600")
        ventana.resizable(True, True)
        
        # Configurar grid
        ventana.columnconfigure(0, weight=1)
        ventana.rowconfigure(1, weight=1)
        
        # Header con información del empleado
        header_frame = ttk.Frame(ventana, padding="15")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.columnconfigure(1, weight=1)
        
        ttk.Label(header_frame, text="👤 Empleado:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(header_frame, text=f"{empleado.get('full_name', 'N/A')} ({sid})", 
                 font=("Arial", 10)).grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(header_frame, text="🏢 Unidad:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w")
        ttk.Label(header_frame, text=empleado.get('unit', 'N/A'), 
                 font=("Arial", 10)).grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(header_frame, text="💼 Posición Actual:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w")
        ttk.Label(header_frame, text=empleado.get('position', 'N/A'), 
                 font=("Arial", 10, "bold"), foreground="blue").grid(row=2, column=1, sticky="w", padx=(10, 0))
        
        # Información adicional sobre accesos por tipo
        accesos_aplicacion = [a for a in accesos_actuales if a.get('access_type') == 'Aplicación']
        accesos_manuales = [a for a in accesos_actuales if a.get('access_type') == 'Manual']
        accesos_flex = [a for a in accesos_actuales if a.get('access_type') == 'Flex Staff']
        
        ttk.Label(header_frame, text="📋 Accesos:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w")
        info_text = f"Aplicación: {len(accesos_aplicacion)}"
        if accesos_manuales:
            info_text += f" | Manuales: {len(accesos_manuales)}"
        if accesos_flex:
            info_text += f" | Flex Staff: {len(accesos_flex)}"
        ttk.Label(header_frame, text=info_text, 
                 font=("Arial", 10)).grid(row=3, column=1, sticky="w", padx=(10, 0))
        
        # Separador
        ttk.Separator(ventana, orient='horizontal').grid(row=1, column=0, sticky="ew", padx=10)
        
        # Frame principal con treeview
        main_frame = ttk.Frame(ventana, padding="10")
        main_frame.grid(row=2, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Treeview para mostrar accesos
        columns = ('Aplicación', 'Tipo', 'Unidad', 'Posición', 'Proceso', 'Fecha', 'Descripción')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas con minwidth
        column_widths = {
            'Aplicación': 180,
            'Tipo': 100,
            'Unidad': 120,
            'Posición': 120,
            'Proceso': 100,
            'Fecha': 120,
            'Descripción': 250
        }
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=column_widths.get(col, 120), minwidth=100, anchor="w")
        
        # Scrollbars (vertical y horizontal)
        vsb = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Insertar datos con colores por tipo
        for acceso in accesos_actuales:
            access_type = acceso.get('access_type', 'Otro')
            
            # Determinar tag basado en el tipo de acceso
            if access_type == 'Aplicación':
                tag = 'app_access'
            elif access_type == 'Manual':
                tag = 'manual_access'
            elif access_type == 'Flex Staff':
                tag = 'flex_access'
            else:
                tag = 'other_access'
            
            tree.insert('', 'end', values=(
                acceso.get('app_name', ''),
                access_type,
                acceso.get('unit', ''),
                acceso.get('position', ''),
                acceso.get('process', ''),
                acceso.get('date', ''),
                acceso.get('description', '')
            ), tags=(tag,))
        
        # Configurar colores de las filas
        tree.tag_configure('app_access', background='#e8f5e8')  # Verde claro para aplicaciones
        tree.tag_configure('manual_access', background='#fff3cd')  # Amarillo claro para manuales
        tree.tag_configure('flex_access', background='#d1ecf1')  # Azul claro para flex staff
        tree.tag_configure('other_access', background='#f8f9fa')  # Gris claro para otros
        
        # Frame de botones de acción
        action_frame = ttk.Frame(ventana, padding="10")
        action_frame.grid(row=3, column=0, sticky="ew")
        
        # Botón para revocar accesos
        revoke_btn = ttk.Button(action_frame, text="🔴 Revocar Acceso", 
                               command=lambda: self._revocar_acceso_seleccionado(tree, sid, ventana))
        revoke_btn.pack(side="left", padx=(0, 10))
        
        # Botón para actualizar
        refresh_btn = ttk.Button(action_frame, text="🔄 Actualizar", 
                                command=lambda: self._actualizar_accesos_ventana(ventana, sid, empleado))
        refresh_btn.pack(side="left", padx=(0, 10))
        
        # Footer con estadísticas detalladas
        footer_frame = ttk.Frame(ventana, padding="10")
        footer_frame.grid(row=4, column=0, sticky="ew")
        
        # Estadísticas por tipo
        stats_text = f"📊 Total: {len(accesos_actuales)} | "
        stats_text += f"🟢 Aplicación: {len(accesos_aplicacion)} | "
        if accesos_manuales:
            stats_text += f"🟡 Manual: {len(accesos_manuales)} | "
        if accesos_flex:
            stats_text += f"🔵 Flex Staff: {len(accesos_flex)}"
        
        ttk.Label(footer_frame, text=stats_text, 
                 font=("Arial", 10, "bold")).pack(side="left")
        
        # Botón cerrar
        ttk.Button(footer_frame, text="Cerrar", 
                  command=ventana.destroy).pack(side="right")
        
        # Guardar referencia a la ventana para actualizaciones
        ventana._tree = tree
        ventana._sid = sid
        ventana._empleado = empleado

    def _revocar_acceso_seleccionado(self, tree, sid, ventana):
        """Revoca el acceso seleccionado en el treeview"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un acceso para revocar")
            return
        
        item = selection[0]
        values = tree.item(item, 'values')
        
        if not values or len(values) < 2:
            messagebox.showerror("Error", "No se pudo obtener la información del acceso")
            return
        
        app_name = values[0]
        access_type = values[1]
        
        # Verificar que el acceso es revocable (flex staff o manual)
        if access_type not in ['Flex Staff', 'Manual']:
            messagebox.showwarning("Advertencia", 
                                 f"Los accesos de tipo '{access_type}' no pueden ser revocados desde aquí.\n"
                                 f"Solo se pueden revocar accesos de tipo 'Flex Staff' y 'Manual'")
            return
        
        # Confirmar revocación
        result = messagebox.askyesno(
            "Confirmar Revocación",
            f"¿Está seguro de que desea revocar el acceso '{access_type}' para '{app_name}'?\n\n"
            f"Esta acción creará un registro de offboarding en el historial."
        )
        
        if not result:
            return
        
        # Mapear tipos de acceso
        access_type_map = {
            'Flex Staff': 'flex_staff',
            'Manual': 'manual_access'
        }
        
        try:
            # Obtener responsable (podría ser desde un campo de entrada)
            responsible = "Sistema"  # Por defecto, se puede mejorar para obtener del usuario
            
            # Revocar el acceso
            result = access_service.revoke_specific_access(
                scotia_id=sid,
                app_name=app_name,
                access_type=access_type_map[access_type],
                responsible=responsible
            )
            
            if result['success']:
                messagebox.showinfo("Éxito", result['message'])
                # Actualizar la ventana
                self._actualizar_accesos_ventana(ventana, sid, ventana._empleado)
            else:
                messagebox.showerror("Error", result['message'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Error revocando acceso: {str(e)}")

    def _actualizar_accesos_ventana(self, ventana, sid, empleado):
        """Actualiza la ventana de accesos actuales"""
        try:
            # Obtener accesos actualizados
            accesos_actuales = access_service.get_employee_current_position_access(sid)
            
            # Limpiar el treeview
            tree = ventana._tree
            for item in tree.get_children():
                tree.delete(item)
            
            # Insertar datos actualizados
            for acceso in accesos_actuales:
                access_type = acceso.get('access_type', 'Otro')
                
                # Determinar tag basado en el tipo de acceso
                if access_type == 'Aplicación':
                    tag = 'app_access'
                elif access_type == 'Manual':
                    tag = 'manual_access'
                elif access_type == 'Flex Staff':
                    tag = 'flex_access'
                else:
                    tag = 'other_access'
                
                tree.insert('', 'end', values=(
                    acceso.get('app_name', ''),
                    access_type,
                    acceso.get('unit', ''),
                    acceso.get('position', ''),
                    acceso.get('process', ''),
                    acceso.get('date', ''),
                    acceso.get('description', '')
                ), tags=(tag,))
            
            # Actualizar estadísticas en el footer
            accesos_aplicacion = [a for a in accesos_actuales if a.get('access_type') == 'Aplicación']
            accesos_manuales = [a for a in accesos_actuales if a.get('access_type') == 'Manual']
            accesos_flex = [a for a in accesos_actuales if a.get('access_type') == 'Flex Staff']
            
            stats_text = f"📊 Total: {len(accesos_actuales)} | "
            stats_text += f"🟢 Aplicación: {len(accesos_aplicacion)} | "
            if accesos_manuales:
                stats_text += f"🟡 Manual: {len(accesos_manuales)} | "
            if accesos_flex:
                stats_text += f"🔵 Flex Staff: {len(accesos_flex)}"
            
            # Actualizar el label de estadísticas
            for widget in ventana.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Label) and "📊 Total:" in child.cget("text"):
                            child.config(text=stats_text)
                            break
            
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando accesos: {str(e)}")


class AplicacionesFrame:
    """Frame para la gestión de aplicaciones del sistema"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
        # Usar el nuevo servicio de gestión de accesos
        # self.app_manager = ApplicationManager()  # Comentado para usar el nuevo servicio
        
        # Variables
        self.applications = []
        self.filtered_applications = []
        self.current_filter = ""
        
        # Variables para filtros múltiples
        self.filtros_activos = {}
        self.campos_filtro = {
            "ID": "id",
            "Jurisdicción": "jurisdiction",
            "Unidad": "unit",
            "Subunidad": "subunit",
            "Unidad/Subunidad": "unidad_subunidad",
            "Nombre Lógico": "logical_access_name",
            "Alias": "alias",
            "Path/Email/URL": "path_email_url",
            "Rol de Posición": "position_role",
            "Exception Tracking": "exception_tracking",
            "Fulfillment Action": "fulfillment_action",
            "Propietario del Sistema": "system_owner",
            "Nombre del Rol": "role_name",
            "Tipo de Acceso": "access_type",
            "Categoría": "category",
            "Datos Adicionales": "additional_data",
            "Código AD": "ad_code",
            "Estado": "access_status",
            "Fecha Última Actualización": "last_update_date",
            "Requiere Licencia": "require_licensing",
            "Descripción": "description",
            "Método de Autenticación": "authentication_method"
        }
        
        self._crear_interfaz()
        self._cargar_aplicaciones() 
    
    def _crear_interfaz(self):
        """Crea la interfaz de gestión de aplicaciones"""
        # Título principal
        ttk.Label(self.frame, text="📱 Gestión de Aplicaciones del Sistema", 
                  style="Title.TLabel").grid(row=0, column=0, pady=(0, 25), sticky="ew")
        
        # Frame principal
        main_content = ttk.Frame(self.frame)
        main_content.grid(row=1, column=0, sticky="nsew", padx=20)
        main_content.columnconfigure(0, weight=1)
        main_content.rowconfigure(2, weight=1)  # Cambiar de row 1 a row 2 para la tabla
        
        # Barra de herramientas
        self._crear_barra_herramientas(main_content)
        
        # Panel de filtros múltiples
        self._crear_panel_filtros_aplicaciones(main_content)
        
        # Tabla de aplicaciones
        self._crear_tabla_aplicaciones(main_content)
        
        # Barra de estado
        self._crear_barra_estado(main_content)
    
    def _crear_barra_herramientas(self, parent):
        """Crea la barra de herramientas"""
        toolbar = ttk.Frame(parent)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Botones principales
        ttk.Button(toolbar, text="➕ Nueva Aplicación", command=self._agregar_aplicacion, 
                  style="Success.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="✏️ Editar", command=self._editar_aplicacion, 
                  style="Info.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="🗑️ Eliminar", command=self._eliminar_aplicacion, 
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
        ttk.Button(toolbar, text="🔄 Actualizar", command=self._actualizar_datos).pack(side=tk.LEFT)
        
        # Botón de exportar
        ttk.Button(toolbar, text="📊 Exportar", command=self._exportar_datos).pack(side=tk.LEFT, padx=(10, 0))
    
    def _crear_panel_filtros_aplicaciones(self, parent):
        """Crea el panel de filtros múltiples para aplicaciones"""
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
        
        ttk.Button(botones_filtros, text="Eliminar", command=self._eliminar_filtro_seleccionado_apps).pack(side=tk.TOP, pady=2)
        ttk.Button(botones_filtros, text="Limpiar", command=self._limpiar_todos_filtros_apps).pack(side=tk.TOP, pady=2)
        
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
        ttk.Button(nuevo_filtro_frame, text="Agregar Filtro", command=self._agregar_filtro_apps).grid(row=0, column=4, padx=(0, 5), pady=5)
        
        # Botones de acción
        botones_accion = ttk.Frame(filtros_frame)
        botones_accion.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        
        ttk.Button(botones_accion, text="Aplicar Filtros", command=self._aplicar_filtros_multiples_apps).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(botones_accion, text="Mostrar Todas", command=self._mostrar_todas_aplicaciones).pack(side=tk.LEFT)
        
        # Bind para Enter en el campo de texto
        self.entry_filtro.bind('<Return>', lambda e: self._agregar_filtro_apps())
    
    def _agregar_filtro_apps(self):
        """Agrega un nuevo filtro a la lista de aplicaciones"""
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
            self._actualizar_lista_filtros_apps()
            
            # Limpiar campos
            self.entry_filtro.delete(0, tk.END)
            self.combo_campo.set("")
    
    def _eliminar_filtro_seleccionado_apps(self):
        """Elimina el filtro seleccionado de la lista de aplicaciones"""
        seleccion = self.filtros_listbox.curselection()
        if seleccion:
            indice = seleccion[0]
            campo = list(self.filtros_activos.keys())[indice]
            del self.filtros_activos[campo]
            self._actualizar_lista_filtros_apps()
    
    def _limpiar_todos_filtros_apps(self):
        """Limpia todos los filtros activos de aplicaciones"""
        self.filtros_activos.clear()
        self._actualizar_lista_filtros_apps()
    
    def _actualizar_lista_filtros_apps(self):
        """Actualiza la lista visual de filtros activos de aplicaciones"""
        self.filtros_listbox.delete(0, tk.END)
        for campo, valor in self.filtros_activos.items():
            self.filtros_listbox.insert(tk.END, f"{campo}: {valor}")
    
    def _aplicar_filtros_multiples_apps(self):
        """Aplica todos los filtros activos para aplicaciones"""
        if not self.filtros_activos:
            messagebox.showwarning("Advertencia", "No hay filtros activos para aplicar")
            return
        
        try:
            # Aplicar filtros múltiples
            resultados_filtrados = self._aplicar_filtros_en_memoria_apps(self.applications)
            
            # Mostrar resultados
            if resultados_filtrados:
                self.filtered_applications = resultados_filtrados
                self._actualizar_tabla()
                self._actualizar_estado(f"🔍 Mostrando {len(resultados_filtrados)} de {len(self.applications)} aplicaciones con filtros aplicados")
            else:
                messagebox.showinfo("Filtros", "No se encontraron aplicaciones que coincidan con los filtros aplicados")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error aplicando filtros: {str(e)}")
    
    def _aplicar_filtros_en_memoria_apps(self, aplicaciones):
        """Aplica los filtros activos a las aplicaciones en memoria"""
        if not aplicaciones:
            return aplicaciones
        
        resultados_filtrados = []
        for app in aplicaciones:
            cumple_filtros = True
            
            for campo_ui, valor_filtro in self.filtros_activos.items():
                campo_bd = self.campos_filtro.get(campo_ui)
                if campo_bd:
                    valor_campo = str(app.get(campo_bd, '')).lower()
                    if valor_filtro.lower() not in valor_campo:
                        cumple_filtros = False
                        break
            
            if cumple_filtros:
                resultados_filtrados.append(app)
        
        return resultados_filtrados
    
    def _mostrar_todas_aplicaciones(self):
        """Muestra todas las aplicaciones sin filtros"""
        self.filtros_activos.clear()
        self._actualizar_lista_filtros_apps()
        self.filtered_applications = self.applications.copy()
        self._actualizar_tabla()
        self._actualizar_estado(f"✅ Mostrando todas las {len(self.applications)} aplicaciones")
    
    def _crear_tabla_aplicaciones(self, parent):
        """Crea la tabla de aplicaciones"""
        # Frame para la tabla
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 15))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Crear Treeview - Actualizado para coincidir con tabla applications
        columns = ('ID', 'Logical Access Name', 'Alias', 'Unit', 'Unidad/Subunidad', 'Position Role', 'System Owner', 'Access Status', 'Category')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.tree.heading('ID', text='ID')
        self.tree.heading('Logical Access Name', text='Logical Access Name')
        self.tree.heading('Alias', text='Alias')
        self.tree.heading('Unit', text='Unit')
        self.tree.heading('Unidad/Subunidad', text='Unidad/Subunidad')
        self.tree.heading('Position Role', text='Position Role')
        self.tree.heading('System Owner', text='System Owner')
        self.tree.heading('Access Status', text='Access Status')
        self.tree.heading('Category', text='Category')
        
        # Configurar anchos de columna
        self.tree.column('ID', width=50, minwidth=50)
        self.tree.column('Logical Access Name', width=180, minwidth=150)
        self.tree.column('Alias', width=120, minwidth=100)
        self.tree.column('Unit', width=100, minwidth=80)
        self.tree.column('Unidad/Subunidad', width=150, minwidth=120)
        self.tree.column('Position Role', width=150, minwidth=120)
        self.tree.column('System Owner', width=120, minwidth=100)
        self.tree.column('Access Status', width=100, minwidth=80)
        self.tree.column('Category', width=120, minwidth=100)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid de la tabla
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Eventos
        self.tree.bind('<Double-1>', self._on_doble_clic)
        self.tree.bind('<Delete>', lambda e: self._eliminar_aplicacion())
    
    def _crear_barra_estado(self, parent):
        """Crea la barra de estado"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, sticky="ew", pady=(15, 0))
        
        self.status_label = ttk.Label(status_frame, text="Listo", style="Success.TLabel")
        self.status_label.pack(side=tk.LEFT)
        
        # Información de la base de datos
        self.db_info_label = ttk.Label(status_frame, text="", style="Header.TLabel")
        self.db_info_label.pack(side=tk.RIGHT)
    
    def _cargar_aplicaciones(self):
        """Carga las aplicaciones desde la nueva estructura de base de datos"""
        try:
            self.applications = access_service.get_all_applications()
            self.filtered_applications = self.applications.copy()
            self._actualizar_tabla()
            self._actualizar_estado(f"✅ Cargadas {len(self.applications)} aplicaciones")
            self._actualizar_info_bd()
        except Exception as e:
            self._actualizar_estado(f"❌ Error al cargar aplicaciones: {str(e)}", error=True)
    
    def _actualizar_tabla(self):
        """Actualiza la tabla con los datos actuales"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insertar datos filtrados
        for app in self.filtered_applications:
            # Formatear fecha
            fecha = app.get('fecha_creacion', '')
            try:
                fecha_formatted = datetime.fromisoformat(fecha).strftime('%d/%m/%Y %H:%M') if fecha else 'N/A'
            except:
                fecha_formatted = fecha or 'N/A'
            
            # Determinar color del estado
            status = app.get('status', 'Active')
            tags = ('active',) if status == 'Active' else ('inactive',) if status == 'Inactive' else ('maintenance',)
            
            self.tree.insert('', 'end', values=(
                app.get('id', ''),
                app.get('logical_access_name', ''),
                app.get('alias', ''),
                app.get('unit', ''),
                app.get('unidad_subunidad', ''),
                app.get('position_role', ''),
                app.get('system_owner', ''),
                app.get('access_status', ''),
                app.get('category', '')
            ), tags=tags)
        
        # Configurar colores de las filas
        self.tree.tag_configure('active', background='#d4edda')
        self.tree.tag_configure('inactive', background='#f8d7da')
        self.tree.tag_configure('maintenance', background='#fff3cd')
    
    def _on_busqueda_change(self, *args):
        """Maneja cambios en la búsqueda"""
        search_term = self.search_var.get().lower()
        self.current_filter = search_term
        
        if not search_term:
            self.filtered_applications = self.applications.copy()
        else:
            self.filtered_applications = [
                app for app in self.applications
                if (search_term in app.get('logical_access_name', '').lower() or
                    search_term in app.get('alias', '').lower() or
                    search_term in app.get('unit', '').lower() or
                    search_term in app.get('position_role', '').lower() or
                    search_term in app.get('system_owner', '').lower() or
                    search_term in app.get('category', '').lower())
            ]
        
        self._actualizar_tabla()
        self._actualizar_estado(f"🔍 Mostrando {len(self.filtered_applications)} de {len(self.applications)} aplicaciones")
    
    def _agregar_aplicacion(self):
        """Abre diálogo para agregar nueva aplicación usando la nueva estructura"""
        # Usar valores por defecto para categorías y propietarios
        categories = ["RRHH", "Tecnología", "Finanzas", "Operaciones", "Marketing", "Comunicaciones"]
        owners = ["Admin", "RRHH", "Tecnología", "Finanzas", "Operaciones", "Marketing", "Comunicaciones"]
        
        dialog = ApplicationDialog(self.frame, "Nueva Aplicación", categories=categories, owners=owners,
                                   unidades=self._obtener_unidades_headcount(),
                                   unidades_sub=self._obtener_unidades_sub_headcount())
        self.frame.wait_window(dialog.dialog)
        
        if dialog.result:
            success, message = access_service.create_application(dialog.result)
            
            if success:
                self._actualizar_estado("✅ Aplicación agregada correctamente")
                self._cargar_aplicaciones()
                # Actualizar dropdowns para futuras aplicaciones
                self._actualizar_dropdowns()
            else:
                self._actualizar_estado(f"❌ Error al agregar aplicación: {message}", error=True)
    
    def _editar_aplicacion(self):
        """Edita la aplicación seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione una aplicación para editar")
            return
        
        item = self.tree.item(selection[0])
        app_id = item['values'][0]
        
        # Buscar la aplicación en la lista
        app_data = None
        for app in self.applications:
            if app['id'] == app_id:
                app_data = app
                break
        
        if not app_data:
            messagebox.showerror("Error", "No se pudo encontrar la aplicación seleccionada")
            return
        
        # Usar valores por defecto para categorías y propietarios
        categories = ["RRHH", "Tecnología", "Finanzas", "Operaciones", "Marketing", "Comunicaciones"]
        owners = ["Admin", "RRHH", "Tecnología", "Finanzas", "Operaciones", "Marketing", "Comunicaciones"]
        
        dialog = ApplicationDialog(self.frame, "Editar Aplicación", app_data, categories, owners,
                                   unidades=self._obtener_unidades_headcount(),
                                   unidades_sub=self._obtener_unidades_sub_headcount())
        self.frame.wait_window(dialog.dialog)
        
        if dialog.result:
            # Usar el access_service para actualizar la aplicación
            success, message = access_service.update_application(app_id, dialog.result)
            
            if success:
                self._actualizar_estado("✅ Aplicación actualizada correctamente")
                self._cargar_aplicaciones()
            else:
                self._actualizar_estado(f"❌ Error al actualizar aplicación: {message}", error=True)
    
    def _eliminar_aplicacion(self):
        """Elimina la aplicación seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione una aplicación para eliminar")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        if len(values) < 2:
            messagebox.showerror("Error", "Datos de aplicación no válidos")
            return
            
        app_id = values[0]  # ID está en la posición 0
        app_name = values[1]  # Nombre está en la posición 1
        
        # Confirmar eliminación
        result = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar la aplicación '{app_name}'?\n\n"
            "Esta acción no se puede deshacer."
        )
        
        if result:
            # Usar el access_service para eliminar la aplicación
            success, message = access_service.delete_application(app_id)
            if success:
                self._actualizar_estado("✅ Aplicación eliminada correctamente")
                self._cargar_aplicaciones()
            else:
                self._actualizar_estado(f"❌ Error al eliminar aplicación: {message}", error=True)
    
    def _on_doble_clic(self, event):
        """Maneja doble clic en la tabla"""
        self._editar_aplicacion()
    
    def _actualizar_datos(self):
        """Actualiza los datos desde la base de datos"""
        self._cargar_aplicaciones()
        self._actualizar_estado("🔄 Datos actualizados")
    
    def _actualizar_dropdowns(self):
        """Actualiza los valores de los dropdowns con los datos más recientes de la base de datos"""
        try:
            # Forzar actualización de los valores únicos
            from services.dropdown_service import dropdown_service
            dropdown_service.get_all_dropdown_values()  # Esto actualiza la caché si existe
            self._actualizar_estado("🔄 Dropdowns actualizados con valores de la base de datos")
        except Exception as e:
            print(f"Error actualizando dropdowns: {e}")
    
    def _exportar_datos(self):
        """Exporta los datos a un archivo CSV"""
        try:
            import csv
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Guardar como CSV"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['ID', 'Logical Access Name', 'Alias', 'Unit', 'Unidad/Subunidad', 'Position Role', 'System Owner', 'Access Status', 'Category']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for app in self.filtered_applications:
                        writer.writerow({
                            'ID': app.get('id', ''),
                            'Logical Access Name': app.get('logical_access_name', ''),
                            'Alias': app.get('alias', ''),
                            'Unit': app.get('unit', ''),
                            'Unidad/Subunidad': app.get('unidad_subunidad', ''),
                            'Position Role': app.get('position_role', ''),
                            'System Owner': app.get('system_owner', ''),
                            'Access Status': app.get('access_status', ''),
                            'Category': app.get('category', '')
                        })
                
                self._actualizar_estado(f"📊 Datos exportados a {filename}")
                messagebox.showinfo("Éxito", f"Los datos se exportaron correctamente a:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar datos: {str(e)}")
            self._actualizar_estado("❌ Error al exportar datos", error=True)
    
    def _actualizar_estado(self, message: str, error: bool = False):
        """Actualiza el mensaje de estado"""
        if error:
            self.status_label.config(text=message, style="Error.TLabel")
        else:
            self.status_label.config(text=message, style="Success.TLabel")
    
    def _actualizar_info_bd(self):
        """Actualiza la información de la base de datos usando la nueva estructura"""
        try:
            stats = access_service.db_manager.get_database_stats()
            total_apps = stats.get('applications', 0)
            self.db_info_label.config(text=f"Total aplicaciones: {total_apps}")
        except:
            self.db_info_label.config(text="Base de datos no disponible")


class ApplicationDialog:
    """Diálogo para agregar/editar aplicaciones"""
    
    def __init__(self, parent, title: str, app_data: dict = None, categories: list = None, owners: list = None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("700x600")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar el diálogo
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.app_data = app_data
        self.categories = categories or []
        self.owners = owners or []
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
        title_label = ttk.Label(scrollable_frame, text="Información de la Aplicación", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Obtener valores únicos de la base de datos
        from services.dropdown_service import dropdown_service
        dropdown_values = dropdown_service.get_all_dropdown_values()
        
        # Campos actualizados para coincidir con tabla applications
        campos = [
            ("Jurisdiction:", "jurisdiction", "combobox", dropdown_values['jurisdictions']),
            ("Unit:", "unit", "combobox", dropdown_values['units']),
            ("Subunit:", "subunit", "combobox", dropdown_values['subunits']),
            ("Unidad/Subunidad:", "unidad_subunidad", "combobox", dropdown_values['unidad_subunidad']),
            ("Logical Access Name:", "logical_access_name", "entry"),
            ("Alias:", "alias", "entry"),
            ("Path/Email/URL:", "path_email_url", "entry"),
            ("Position Role:", "position_role", "combobox", dropdown_values['positions']),
            ("Exception Tracking:", "exception_tracking", "entry"),
            ("Fulfillment Action:", "fulfillment_action", "entry"),
            ("System Owner:", "system_owner", "combobox", dropdown_values['system_owners']),
            ("Role Name:", "role_name", "combobox", dropdown_values['roles']),
            ("Access Type:", "access_type", "combobox", dropdown_values['access_types']),
            ("Category:", "category", "combobox", dropdown_values['categories']),
            ("Additional Data:", "additional_data", "entry"),
            ("AD Code:", "ad_code", "entry"),
            ("Access Status:", "access_status", "combobox", dropdown_values['access_statuses']),
            ("Require Licensing:", "require_licensing", "entry"),
            ("Description:", "description", "text"),
            ("Authentication Method:", "authentication_method", "combobox", dropdown_values['authentication_methods'])
        ]
        
        # Crear campos dinámicamente
        self.variables = {}
        self.widgets = {}
        for i, campo in enumerate(campos):
            label_text, var_name, tipo = campo[:3]
            ttk.Label(scrollable_frame, text=label_text).grid(row=i+1, column=0, sticky="w", pady=5)
            
            if tipo == "entry":
                self.variables[var_name] = tk.StringVar()
                entry = ttk.Entry(scrollable_frame, textvariable=self.variables[var_name], width=50)
                entry.grid(row=i+1, column=1, sticky="ew", pady=5, padx=(10, 0))
                self.widgets[var_name] = entry
            elif tipo == "combobox":
                valores = campo[3] if len(campo) > 3 else []
                self.variables[var_name] = tk.StringVar()
                combo = ttk.Combobox(scrollable_frame, textvariable=self.variables[var_name], values=valores, width=47)
                combo.grid(row=i+1, column=1, sticky="ew", pady=5, padx=(10, 0))
                self.widgets[var_name] = combo
            elif tipo == "text":
                text_widget = tk.Text(scrollable_frame, height=3, width=50)
                text_widget.grid(row=i+1, column=1, sticky="ew", pady=5, padx=(10, 0))
                self.variables[var_name] = text_widget  # Para Text widgets, guardamos el widget directamente
                self.widgets[var_name] = text_widget
        
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
        if 'logical_access_name' in self.widgets:
            self.widgets['logical_access_name'].focus()
        
        self.dialog.bind('<Return>', lambda e: self._save())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
    
    def _load_data(self):
        """Carga los datos existentes si es una edición"""
        if self.app_data:
            for var_name, var in self.variables.items():
                if var_name in self.app_data:
                    if isinstance(var, tk.StringVar):
                        var.set(str(self.app_data[var_name]) if self.app_data[var_name] is not None else '')
                    elif isinstance(var, tk.Text):
                        var.delete('1.0', tk.END)
                        var.insert('1.0', str(self.app_data[var_name]) if self.app_data[var_name] is not None else '')
    
    def _save(self):
        """Guarda los datos del formulario"""
        # Validaciones básicas
        if not self.variables['logical_access_name'].get().strip():
            messagebox.showerror("Error", "El Logical Access Name es obligatorio")
            return
        
        if not self.variables['unit'].get().strip():
            messagebox.showerror("Error", "La Unit es obligatoria")
            return
        
        # Preparar datos
        self.result = {}
        for var_name, var in self.variables.items():
            if isinstance(var, tk.StringVar):
                self.result[var_name] = var.get().strip()
            elif isinstance(var, tk.Text):
                self.result[var_name] = var.get('1.0', tk.END).strip()
        
        # Establecer valores por defecto si están vacíos
        if not self.result.get('access_status'):
            self.result['access_status'] = 'Active'
        if not self.result.get('jurisdiction'):
            self.result['jurisdiction'] = 'Global'
        
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancela la operación"""
        self.dialog.destroy()


def main():
    """Función principal para ejecutar la aplicación"""
    root = tk.Tk()
    app = AppEmpleadosRefactorizada(root)
    root.mainloop()


if __name__ == "__main__":
    main()
"""
Estilos personalizados para la aplicación de empleados
"""
from tkinter import ttk

def aplicar_estilos_personalizados():
    """Aplica estilos personalizados a toda la aplicación"""
    style = ttk.Style()
    
    # Configurar tema base
    try:
        style.theme_use('clam')
    except:
        pass
    
    # Estilos para botones de navegación
    style.configure('Nav.TButton', 
                   font=('Arial', 11, 'bold'),
                   padding=(15, 12),
                   relief='raised',
                   borderwidth=2)
    
    style.map('Nav.TButton',
              background=[('active', '#ffcdd2'), ('pressed', '#ef9a9a')],
              relief=[('pressed', 'sunken'), ('active', 'raised')])
    
    # Estilos para botón de salida
    style.configure('Salir.TButton', 
                   font=('Arial', 11, 'bold'),
                   padding=(15, 12),
                   relief='raised',
                   borderwidth=2,
                   foreground='#d32f2f')
    
    style.map('Salir.TButton',
              background=[('active', '#ffcdd2'), ('pressed', '#ef9a9a')],
              relief=[('pressed', 'sunken'), ('active', 'raised')])
    
    # Estilos para botones de acción - Cambiados a tonos de rojo
    estilos_botones = {
        'Success.TButton': {'background': '#ffebee', 'foreground': '#d32f2f'},
        'Info.TButton': {'background': '#ffebee', 'foreground': '#c62828'},
        'Warning.TButton': {'background': '#ffcdd2', 'foreground': '#b71c1c'},
        'Danger.TButton': {'background': '#ffcdd2', 'foreground': '#d32f2f'}
    }
    
    for nombre, colores in estilos_botones.items():
        style.configure(nombre, 
                       font=('Arial', 10, 'bold'),
                       padding=(12, 8),
                       relief='raised',
                       borderwidth=2,
                       **colores)
    
    # Estilos para labels - Cambiados a tonos de rojo
    estilos_labels = {
        'Title.TLabel': {'font': ('Arial', 20, 'bold'), 'foreground': '#d32f2f'},
        'Section.TLabel': {'font': ('Arial', 18, 'bold'), 'foreground': '#c62828'},
        'Subsection.TLabel': {'font': ('Arial', 14, 'bold'), 'foreground': '#b71c1c'},
        'Info.TLabel': {'font': ('Arial', 10, 'italic'), 'foreground': '#7f8c8d'}
    }
    
    for nombre, config in estilos_labels.items():
        style.configure(nombre, **config)
    
    # Estilos para frames
    style.configure('Main.TFrame', relief='flat', borderwidth=0)
    style.configure('Nav.TLabelframe', relief='raised', borderwidth=2)
    
    # Estilos para pestañas - Cambiados a tonos de rojo
    style.configure('TNotebook.Tab',
                   font=('Arial', 10, 'bold'),
                   padding=(15, 8))
    
    style.map('TNotebook.Tab',
              background=[('selected', '#ffebee'), ('active', '#ffcdd2')],
              foreground=[('selected', '#d32f2f'), ('active', '#b71c1c')])
    
    # Estilos para el logo GAMLO
    style.configure('Logo.TFrame',
                   relief='raised',
                   borderwidth=2,
                   background='#F8F9FA')
    
    style.map('Logo.TFrame',
              background=[('active', '#E3F2FD'), ('pressed', '#BBDEFB')])
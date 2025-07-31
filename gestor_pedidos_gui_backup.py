import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from datetime import datetime
import json
import os
import subprocess
import platform
from main import ReferenciaPieza, Oferta, Eproc, PedidoStatus


class ProgressBar(tk.Canvas):
    """Barra de progreso personalizada estilo tracking de Amazon"""
    
    def __init__(self, parent, width=400, height=40, bg='white', **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg, 
                        highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        
        # Estados del pedido en orden
        self.estados = [
            ("Oferta", PedidoStatus.OFERTA),
            ("Borrador", PedidoStatus.PEDIDO_EPROC_BORRADOR),
            ("Enviado", PedidoStatus.PEDIDO_EPROC_ENVIADO_NO_FIRMADO),
            ("Firmado", PedidoStatus.PEDIDO_EPROC_ENVIADO_FIRMADO),
            ("TAR", PedidoStatus.TAR_LANZADO_NO_ETIQUETAS),
            ("Etiquetas", PedidoStatus.TAR_LANZADO_SI_ETIQUETAS),
            ("Enviado", PedidoStatus.ETIQUETAS_ENVIADAS),
            ("Recogido", PedidoStatus.PAQUETE_RECOGIDO),
            ("En Camino", PedidoStatus.PAQUETE_EN_CAMINO),
            ("Entregado", PedidoStatus.COMPLETADO)
        ]
        
        self.colors = {
            'completed': '#27AE60',
            'current': '#3498DB', 
            'pending': '#BDC3C7',
            'line_completed': '#27AE60',
            'line_pending': '#E9ECEF'
        }
    
    def update_progress(self, current_status):
        """Actualiza la barra con el estado actual"""
        self.delete("all")
        
        # Encontrar el índice del estado actual
        current_index = -1
        for i, (_, status) in enumerate(self.estados):
            if status == current_status:
                current_index = i
                break
        
        if current_index == -1:
            current_index = 0
        
        # Calcular posiciones
        num_estados = len(self.estados)
        step_width = (self.width - 40) / (num_estados - 1)
        y_center = self.height // 2
        
        # Dibujar líneas de conexión
        for i in range(num_estados - 1):
            x1 = 20 + i * step_width
            x2 = 20 + (i + 1) * step_width
            
            color = self.colors['line_completed'] if i < current_index else self.colors['line_pending']
            self.create_line(x1, y_center, x2, y_center, 
                           width=3, fill=color, capstyle='round')
        
        # Dibujar círculos y etiquetas
        for i, (label, _) in enumerate(self.estados):
            x = 20 + i * step_width
            
            # Determinar color del círculo
            if i < current_index:
                circle_color = self.colors['completed']
                text_color = 'white'
                symbol = "✓"
            elif i == current_index:
                circle_color = self.colors['current']
                text_color = 'white'
                symbol = str(i + 1)
            else:
                circle_color = self.colors['pending']
                text_color = '#7F8C8D'
                symbol = str(i + 1)
            
            # Dibujar círculo
            self.create_oval(x-8, y_center-8, x+8, y_center+8,
                           fill=circle_color, outline=circle_color, width=2)
            
            # Dibujar símbolo en el círculo
            self.create_text(x, y_center, text=symbol, 
                           fill=text_color, font=('Segoe UI', 8, 'bold'))
            
            # Etiqueta debajo
            self.create_text(x, y_center + 18, text=label,
                           fill='#2C3E50', font=('Segoe UI', 7))


class PedidoManager:
    def __init__(self, archivo_datos="pedidos_data.json"):
        self.pedidos = []
        self.archivo_datos = archivo_datos
        self.cargar_datos()

    def agregar_pedido(self, pedido):
        self.pedidos.append(pedido)
        self.guardar_datos()

    def actualizar_pedido(self, pedido):
        # Guardar cambios cuando se actualiza un pedido
        if self.guardar_datos():
            # Notificar a la GUI que los datos se han guardado
            if hasattr(self, '_gui_callback'):
                self._gui_callback()

    def set_gui_callback(self, callback):
        """Establece una función callback para notificar a la GUI"""
        self._gui_callback = callback

    def buscar_por_oferta(self, numero_oferta):
        return [p for p in self.pedidos if p.numero_oferta == numero_oferta]

    def pedido_to_dict(self, pedido):
        """Convierte un objeto Pedido a diccionario para JSON"""
        return {
            'numero_oferta': pedido.numero_oferta,
            'requisition_id': pedido.requisition_id,
            'oi': pedido.oi,
            'numero_pedido': pedido.numero_pedido,
            'proveedor': pedido.proveedor,
            'status': pedido.status,
            'historial': pedido.historial,
            'fecha_creacion': pedido.fecha_creacion.isoformat() if pedido.fecha_creacion else None,
            'fecha_eproc_borrador': pedido.fecha_eproc_borrador.isoformat() if pedido.fecha_eproc_borrador else None,
            'fecha_eproc_firmado': pedido.fecha_eproc_firmado.isoformat() if pedido.fecha_eproc_firmado else None,
            'po_pdf': pedido.po_pdf,
            'numero_po': pedido.numero_po,
            'etiquetas_pdf': pedido.etiquetas_pdf,
            'numero_bultos': pedido.numero_bultos,
            'peso_total': pedido.peso_total,
            'dimensiones': pedido.dimensiones,
            'tracking_number': pedido.tracking_number,
            'referencias': [
                {
                    'codigo': ref.codigo,
                    'descripcion': ref.descripcion,
                    'cantidad': ref.cantidad,
                    'proyecto': ref.proyecto
                } for ref in pedido.referencias
            ]
        }

    def dict_to_pedido(self, data):
        """Convierte un diccionario de JSON a objeto Pedido"""
        referencias = [
            ReferenciaPieza(
                codigo=ref['codigo'],
                descripcion=ref['descripcion'],
                cantidad=ref['cantidad'],
                proyecto=ref['proyecto']
            ) for ref in data.get('referencias', [])
        ]
        
        pedido = Eproc(
            numero_oferta=data['numero_oferta'],
            requisition_id=data.get('requisition_id', ''),
            oi=data.get('oi', 0),
            numero_pedido=data.get('numero_pedido', ''),
            proveedor=data.get('proveedor', ''),
            referencias=referencias,
            status=data.get('status', PedidoStatus.OFERTA),
            po_pdf=data.get('po_pdf', ''),
            numero_po=data.get('numero_po', ''),
            etiquetas_pdf=data.get('etiquetas_pdf', ''),
            numero_bultos=data.get('numero_bultos', 0),
            peso_total=data.get('peso_total', 0.0),
            dimensiones=data.get('dimensiones', ''),
            tracking_number=data.get('tracking_number', '')
        )
        
        # Restaurar historial y fechas
        pedido.historial = data.get('historial', [])
        if data.get('fecha_creacion'):
            pedido.fecha_creacion = datetime.fromisoformat(data['fecha_creacion'])
        if data.get('fecha_eproc_borrador'):
            pedido.fecha_eproc_borrador = datetime.fromisoformat(data['fecha_eproc_borrador'])
        if data.get('fecha_eproc_firmado'):
            pedido.fecha_eproc_firmado = datetime.fromisoformat(data['fecha_eproc_firmado'])
        
        return pedido

    def guardar_datos(self):
        """Guarda todos los pedidos en un archivo JSON"""
        try:
            data = {
                'pedidos': [self.pedido_to_dict(pedido) for pedido in self.pedidos],
                'fecha_guardado': datetime.now().isoformat()
            }
            with open(self.archivo_datos, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar datos: {e}")
            return False

    def cargar_datos(self):
        """Carga los pedidos desde el archivo JSON"""
        if not os.path.exists(self.archivo_datos):
            print(f"Archivo {self.archivo_datos} no encontrado. Iniciando con datos vacíos.")
            return
        
        try:
            with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                data = json.load(f)
                pedidos_data = data.get('pedidos', [])
                self.pedidos = []
                
                for pedido_data in pedidos_data:
                    try:
                        pedido = self.dict_to_pedido(pedido_data)
                        self.pedidos.append(pedido)
                    except Exception as e:
                        print(f"Error al cargar pedido {pedido_data.get('numero_oferta', 'desconocido')}: {e}")
                        continue
                
                print(f"Datos cargados exitosamente: {len(self.pedidos)} pedido(s)")
                fecha_guardado = data.get('fecha_guardado')
                if fecha_guardado:
                    print(f"Última actualización: {fecha_guardado}")
                    
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            print("El archivo de datos puede estar corrupto. Iniciando con datos vacíos.")
            self.pedidos = []
            # Crear backup del archivo corrupto
            backup_name = f"{self.archivo_datos}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                import shutil
                shutil.copy2(self.archivo_datos, backup_name)
                print(f"Backup del archivo corrupto creado: {backup_name}")
            except:
                pass
        except Exception as e:
            print(f"Error inesperado al cargar datos: {e}")
            self.pedidos = []

class PedidoApp(tk.Tk):
    def __init__(self, manager):
        super().__init__()
        self.title("🚛 Gestor de Pedidos - Sistema Profesional")
        self.geometry("1200x700")
        self.manager = manager
        
        # Configurar tema y colores
        self.configure_theme()
        
        # Configurar callback para actualizar la barra de estado
        self.manager.set_gui_callback(self.actualizar_status_bar)
        self.create_widgets()

    def configure_theme(self):
        """Configura el tema minimalista de la aplicación"""
        # Colores minimalistas
        self.colors = {
            'primary': '#2C3E50',       # Azul gris oscuro
            'secondary': '#3498DB',     # Azul claro
            'success': '#27AE60',       # Verde
            'danger': '#E74C3C',        # Rojo
            'background': '#FFFFFF',    # Blanco puro
            'surface': '#F8F9FA',       # Gris muy claro
            'border': '#E9ECEF',        # Gris claro para bordes
            'text': '#2C3E50',          # Texto oscuro
            'text_secondary': '#6C757D', # Texto secundario
        }
        
        # Configurar el fondo principal
        self.configure(bg=self.colors['background'])
        
        # Configurar estilos ttk minimalistas
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilo para treeview
        style.configure('Clean.Treeview',
                       font=('Segoe UI', 10),
                       background=self.colors['background'],
                       foreground=self.colors['text'],
                       rowheight=28,
                       borderwidth=0)
        
        style.configure('Clean.Treeview.Heading',
                       font=('Segoe UI', 10, 'bold'),
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       borderwidth=1,
                       relief='solid')

    def actualizar_status_bar(self):
        """Actualiza la barra de estado con información moderna"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        num_pedidos = len(self.manager.pedidos)
        self.status_bar.config(text=f"💾 Guardado automático: {timestamp} | 📊 Total: {num_pedidos} pedidos | 📁 {self.manager.archivo_datos}")

    def create_widgets(self):
        # Título simple
        title_frame = tk.Frame(self, bg=self.colors['background'], height=60)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, 
                              text="Gestor de Pedidos", 
                              font=('Segoe UI', 18, 'bold'),
                              bg=self.colors['background'],
                              fg=self.colors['primary'])
        title_label.pack(pady=15)

        # Barra de herramientas minimalista
        toolbar = tk.Frame(self, bg=self.colors['background'], height=50)
        toolbar.pack(fill="x", padx=20, pady=(0, 10))
        toolbar.pack_propagate(False)
        
        # Búsqueda simple
        search_frame = tk.Frame(toolbar, bg=self.colors['background'])
        search_frame.pack(side="left", fill="y")
        
        tk.Label(search_frame, text="Buscar:", 
                font=('Segoe UI', 10),
                bg=self.colors['background'],
                fg=self.colors['text']).pack(side="left", padx=(0, 8), pady=12)
        
        self.buscar_entry = tk.Entry(search_frame,
                                    font=('Segoe UI', 10),
                                    width=20,
                                    relief='solid',
                                    bd=1,
                                    bg=self.colors['background'])
        self.buscar_entry.pack(side="left", padx=(0, 8), pady=12, ipady=4)
        
        # Botones simples
        tk.Button(search_frame, text="Buscar",
                 command=self.buscar_pedido,
                 font=('Segoe UI', 9),
                 bg=self.colors['secondary'],
                 fg='white',
                 relief='flat',
                 padx=12, pady=6,
                 cursor='hand2').pack(side="left", padx=(0, 4), pady=12)
        
        tk.Button(search_frame, text="Mostrar Todos",
                 command=self.mostrar_todos,
                 font=('Segoe UI', 9),
                 bg=self.colors['text_secondary'],
                 fg='white',
                 relief='flat',
                 padx=12, pady=6,
                 cursor='hand2').pack(side="left", padx=(0, 4), pady=12)
        
        # Botón principal
        tk.Button(toolbar, text="Nuevo Pedido",
                 command=self.nuevo_pedido,
                 font=('Segoe UI', 10, 'bold'),
                 bg=self.colors['success'],
                 fg='white',
                 relief='flat',
                 padx=20, pady=8,
                 cursor='hand2').pack(side="right", pady=12)

        # Tabla simple y limpia
        table_frame = tk.Frame(self, bg=self.colors['background'])
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
        
        self.tabla = ttk.Treeview(table_frame, 
                                 columns=("oferta", "pedido", "proveedor", "estado"),
                                 show="headings",
                                 style='Clean.Treeview',
                                 yscrollcommand=v_scrollbar.set,
                                 xscrollcommand=h_scrollbar.set)
        
        # Headers simples
        self.tabla.heading("oferta", text="Nº Oferta")
        self.tabla.heading("pedido", text="Nº Pedido") 
        self.tabla.heading("proveedor", text="Proveedor")
        self.tabla.heading("estado", text="Estado")
        
        # Ancho de columnas
        self.tabla.column("oferta", width=100, anchor="center")
        self.tabla.column("pedido", width=100, anchor="center")
        self.tabla.column("proveedor", width=200, anchor="w")
        self.tabla.column("estado", width=300, anchor="w")
        
        # Configurar scrollbars
        v_scrollbar.config(command=self.tabla.yview)
        h_scrollbar.config(command=self.tabla.xview)
        
        # Grid layout
        self.tabla.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.tabla.bind("<Double-1>", self.ver_detalle_pedido)
        
        # Filas alternadas sutiles
        self.tabla.tag_configure('even', background='#FDFDFD')
        self.tabla.tag_configure('odd', background='#FFFFFF')

        # Barra de estado simple
        status_frame = tk.Frame(self, bg=self.colors['surface'], height=30)
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)
        
        num_pedidos = len(self.manager.pedidos)
        self.status_bar = tk.Label(status_frame, 
                                  text=f"Total: {num_pedidos} pedidos",
                                  font=('Segoe UI', 9),
                                  bg=self.colors['surface'],
                                  fg=self.colors['text_secondary'],
                                  anchor="w")
        self.status_bar.pack(fill="x", padx=10, pady=6)

        # Menú de backup discreto (click derecho)
        def show_backup_menu(event):
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label="Crear Backup", command=self.hacer_backup)
            menu.tk_popup(event.x_root, event.y_root)
        
        self.bind("<Button-3>", show_backup_menu)  # Click derecho para backup

        self.refrescar_tabla()

    def hacer_backup(self):
        """Crea una copia de seguridad de los datos"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"pedidos_backup_{timestamp}.json"
            backup_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                initialfilename=backup_filename,
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Guardar backup de datos"
            )
            
            if backup_path:
                import shutil
                shutil.copy2(self.manager.archivo_datos, backup_path)
                messagebox.showinfo("Backup", f"Backup guardado exitosamente en:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear backup: {str(e)}")

    def mostrar_todos(self):
        """Muestra todos los pedidos en la tabla"""
        self.buscar_entry.delete(0, "end")
        self.refrescar_tabla()

    def abrir_archivo(self, ruta_archivo):
        """Abre un archivo con la aplicación predeterminada del sistema"""
        if not ruta_archivo or not os.path.exists(ruta_archivo):
            messagebox.showerror("Error", "El archivo no existe o la ruta está vacía")
            return
        
        try:
            if platform.system() == 'Windows':
                os.startfile(ruta_archivo)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', ruta_archivo])
            else:  # Linux
                subprocess.call(['xdg-open', ruta_archivo])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {str(e)}")

    def refrescar_tabla(self):
        # Limpiar tabla
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        
        # Agregar pedidos con colores alternados
        for i, pedido in enumerate(self.manager.pedidos):
            fecha_str = ""
            if pedido.fecha_creacion:
                fecha_str = pedido.fecha_creacion.strftime("%d/%m/%Y")
            
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            self.tabla.insert("", "end", values=(
                pedido.numero_oferta, 
                pedido.numero_pedido or "-", 
                pedido.proveedor, 
                pedido.status,
                fecha_str
            ), tags=(tag,))
        
        # Actualizar estadísticas en tiempo real
        self.actualizar_estadisticas()
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas mostradas en el panel de control"""
        total_pedidos = len(self.manager.pedidos)
        
        # Contar estados
        estados_count = {}
        for pedido in self.manager.pedidos:
            estado = pedido.status
            estados_count[estado] = estados_count.get(estado, 0) + 1

    def buscar_pedido(self):
        num_oferta = self.buscar_entry.get().strip()
        if not num_oferta:
            self.mostrar_todos()
            return
            
        resultados = self.manager.buscar_por_oferta(num_oferta)
        
        # Limpiar tabla
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        
        # Mostrar resultados con resaltado
        for i, pedido in enumerate(resultados):
            fecha_str = ""
            if pedido.fecha_creacion:
                fecha_str = pedido.fecha_creacion.strftime("%d/%m/%Y")
            
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            self.tabla.insert("", "end", values=(
                pedido.numero_oferta, 
                pedido.numero_pedido or "-", 
                pedido.proveedor, 
                pedido.status,
                fecha_str
            ), tags=(tag,))
        
        # Actualizar barra de estado con resultados de búsqueda
        if resultados:
            self.status_bar.config(text=f"🔍 Búsqueda: {len(resultados)} resultado(s) para '{num_oferta}'")
        else:
            self.status_bar.config(text=f"⚠️ No se encontraron pedidos con oferta '{num_oferta}'")

    def mostrar_todos(self):
        """Muestra todos los pedidos en la tabla"""
        self.buscar_entry.delete(0, "end")
        self.refrescar_tabla()
        num_pedidos = len(self.manager.pedidos)
        self.status_bar.config(text=f"📋 Mostrando todos los pedidos ({num_pedidos} total)")

    def nuevo_pedido(self):
        # Ventana moderna para crear pedido
        top = tk.Toplevel(self)
        top.title("➕ Crear Nuevo Pedido")
        top.geometry("600x500")
        top.configure(bg=self.colors['background'])
        
        # Configurar ventana modal
        top.transient(self)
        top.grab_set()
        top.lift()
        top.attributes('-topmost', True)
        
        # Centrar ventana
        top.update_idletasks()
        x = (top.winfo_screenwidth() // 2) - (600 // 2)
        y = (top.winfo_screenheight() // 2) - (500 // 2)
        top.geometry(f"600x500+{x}+{y}")
        top.after(100, lambda: top.attributes('-topmost', False))

        # Header de la ventana
        header_frame = tk.Frame(top, bg=self.colors['primary'], height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame,
                               text="➕ CREAR NUEVO PEDIDO",
                               font=('Segoe UI', 16, 'bold'),
                               bg=self.colors['primary'],
                               fg='white')
        header_label.pack(pady=15)

        # Contenedor principal
        main_frame = tk.Frame(top, bg=self.colors['background'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Formulario en card
        form_card = tk.Frame(main_frame, bg=self.colors['surface'], relief='solid', bd=1)
        form_card.pack(fill="x", pady=(0, 15))
        
        form_title = tk.Label(form_card,
                             text="📋 Información Básica",
                             font=('Segoe UI', 12, 'bold'),
                             bg=self.colors['surface'],
                             fg=self.colors['primary'])
        form_title.pack(anchor="w", padx=15, pady=(15, 10))

        # Grid para el formulario
        form_grid = tk.Frame(form_card, bg=self.colors['surface'])
        form_grid.pack(fill="x", padx=15, pady=(0, 15))

        # Empresa
        tk.Label(form_grid, text="🏢 Empresa:", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['surface'], fg=self.colors['text']).grid(row=0, column=0, sticky="w", pady=5)
        entry_empresa = tk.Entry(form_grid, font=('Segoe UI', 10), width=30, relief='solid', bd=1)
        entry_empresa.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5, ipady=3)

        # Número de Oferta
        tk.Label(form_grid, text="📋 Nº Oferta:", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['surface'], fg=self.colors['text']).grid(row=1, column=0, sticky="w", pady=5)
        entry_num_oferta = tk.Entry(form_grid, font=('Segoe UI', 10), width=30, relief='solid', bd=1)
        entry_num_oferta.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5, ipady=3)

        # Email Comercial
        tk.Label(form_grid, text="📧 Email Comercial:", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['surface'], fg=self.colors['text']).grid(row=2, column=0, sticky="w", pady=5)
        entry_email = tk.Entry(form_grid, font=('Segoe UI', 10), width=30, relief='solid', bd=1)
        entry_email.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5, ipady=3)

        # PDF Oferta
        tk.Label(form_grid, text="📄 PDF Oferta:", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['surface'], fg=self.colors['text']).grid(row=3, column=0, sticky="w", pady=5)
        
        pdf_frame = tk.Frame(form_grid, bg=self.colors['surface'])
        pdf_frame.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        pdf_var = tk.StringVar()
        entry_pdf = tk.Entry(pdf_frame, textvariable=pdf_var, font=('Segoe UI', 10), 
                           state="readonly", relief='solid', bd=1)
        entry_pdf.pack(side="left", fill="x", expand=True, ipady=3)
        
        def seleccionar_pdf():
            path = filedialog.askopenfilename(title="Selecciona PDF de Oferta",
                                            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
            if path:
                pdf_var.set(path)
        
        btn_pdf = tk.Button(pdf_frame, text="📁 Seleccionar",
                           command=seleccionar_pdf,
                           font=('Segoe UI', 9),
                           bg=self.colors['secondary'],
                           fg='white',
                           relief='flat',
                           padx=10,
                           cursor='hand2')
        btn_pdf.pack(side="right", padx=(5, 0))

        form_grid.columnconfigure(1, weight=1)

        # Sección de referencias
        ref_card = tk.Frame(main_frame, bg=self.colors['surface'], relief='solid', bd=1)
        ref_card.pack(fill="both", expand=True, pady=(0, 15))
        
        ref_header = tk.Frame(ref_card, bg=self.colors['surface'])
        ref_header.pack(fill="x", padx=15, pady=(15, 10))
        
        ref_title = tk.Label(ref_header,
                            text="📦 Referencias de Piezas",
                            font=('Segoe UI', 12, 'bold'),
                            bg=self.colors['surface'],
                            fg=self.colors['primary'])
        ref_title.pack(side="left")
        
        # Lista de referencias
        referencias = []
        
        ref_listbox = tk.Listbox(ref_card, font=('Segoe UI', 9), height=4,
                               relief='solid', bd=1, bg='#F8F9FA')
        ref_listbox.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        def actualizar_lista_referencias():
            ref_listbox.delete(0, "end")
            for i, ref in enumerate(referencias, 1):
                ref_listbox.insert("end", f"{i}. {ref.codigo} - {ref.descripcion} (Cant: {ref.cantidad}, Proyecto: {ref.proyecto})")
        
        def agregar_referencia():
            try:
                codigo = simple_input("🔧 Código de pieza:", top)
                if not codigo: return
                descripcion = simple_input("📝 Descripción:", top)
                if not descripcion: return
                cantidad_str = simple_input("🔢 Cantidad:", top)
                if not cantidad_str: return
                cantidad = int(cantidad_str)
                proyecto = simple_input("📁 Proyecto:", top)
                if not proyecto: return
                
                referencias.append(ReferenciaPieza(codigo, descripcion, cantidad, proyecto))
                actualizar_lista_referencias()
                
                # Mensaje de éxito más moderno
                msg_window = tk.Toplevel(top)
                msg_window.title("✅ Éxito")
                msg_window.geometry("300x100")
                msg_window.configure(bg=self.colors['success'])
                msg_window.transient(top)
                msg_window.grab_set()
                
                msg_label = tk.Label(msg_window,
                                   text=f"✅ Referencia {codigo} añadida correctamente",
                                   font=('Segoe UI', 10),
                                   bg=self.colors['success'],
                                   fg='white')
                msg_label.pack(expand=True)
                
                msg_window.after(1500, msg_window.destroy)
                
            except ValueError:
                messagebox.showerror("❌ Error", "La cantidad debe ser un número entero", parent=top)
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al añadir referencia: {str(e)}", parent=top)

        btn_add_ref = tk.Button(ref_card,
                               text="➕ Añadir Referencia",
                               command=agregar_referencia,
                               font=('Segoe UI', 10, 'bold'),
                               bg=self.colors['secondary'],
                               fg='white',
                               relief='flat',
                               padx=20,
                               pady=8,
                               cursor='hand2')
        btn_add_ref.pack(pady=(0, 15))

        # Botones de acción
        button_frame = tk.Frame(main_frame, bg=self.colors['background'])
        button_frame.pack(fill="x")

        def crear():
            try:
                # Validar campos obligatorios
                if not entry_num_oferta.get().strip():
                    messagebox.showerror("❌ Error", "El número de oferta es obligatorio", parent=top)
                    return
                if not entry_empresa.get().strip():
                    messagebox.showerror("❌ Error", "La empresa es obligatoria", parent=top)
                    return
                
                oferta = Oferta(
                    numero_oferta=entry_num_oferta.get().strip(),
                    empresa=entry_empresa.get().strip(),
                    quotation_pdf=pdf_var.get(),
                    email_comercial=entry_email.get().strip()
                )
                
                pedido = Eproc(
                    numero_oferta=oferta.numero_oferta,
                    requisition_id="",
                    oi=0,
                    numero_pedido="",
                    proveedor=oferta.empresa,
                    referencias=referencias,
                )
                
                self.manager.agregar_pedido(pedido)
                self.refrescar_tabla()
                
                # Mensaje de éxito moderno
                success_window = tk.Toplevel(top)
                success_window.title("✅ Pedido Creado")
                success_window.geometry("350x150")
                success_window.configure(bg=self.colors['success'])
                success_window.transient(top)
                success_window.grab_set()
                
                success_label = tk.Label(success_window,
                                       text=f"✅ Pedido {pedido.numero_oferta}\ncreado correctamente",
                                       font=('Segoe UI', 12, 'bold'),
                                       bg=self.colors['success'],
                                       fg='white',
                                       justify='center')
                success_label.pack(expand=True)
                
                success_window.after(2000, lambda: [success_window.destroy(), top.destroy()])
                
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al crear el pedido: {str(e)}", parent=top)

        # Botón Crear
        btn_crear = tk.Button(button_frame,
                             text="✅ CREAR PEDIDO",
                             command=crear,
                             font=('Segoe UI', 12, 'bold'),
                             bg=self.colors['success'],
                             fg='white',
                             relief='flat',
                             padx=30,
                             pady=12,
                             cursor='hand2')
        btn_crear.pack(side="right", padx=(10, 0))

        # Botón Cancelar
        btn_cancelar = tk.Button(button_frame,
                                text="❌ Cancelar",
                                command=top.destroy,
                                font=('Segoe UI', 10),
                                bg=self.colors['text_light'],
                                fg='white',
                                relief='flat',
                                padx=20,
                                pady=10,
                                cursor='hand2')
        btn_cancelar.pack(side="right")

    def ver_detalle_pedido(self, event):
        if not self.tabla.selection():
            return
        item = self.tabla.selection()[0]
        values = self.tabla.item(item, "values")
        pedido = next((p for p in self.manager.pedidos if p.numero_oferta == values[0]), None)
        if pedido:
            top = tk.Toplevel(self)
            top.title(f"Detalle de Pedido {pedido.numero_oferta}")
            top.geometry("800x600")
            top.configure(bg='white')
            
            # Configurar ventana modal
            top.transient(self)
            top.grab_set()
            top.lift()
            
            # Centrar la ventana
            top.update_idletasks()
            x = (top.winfo_screenwidth() // 2) - (400)
            y = (top.winfo_screenheight() // 2) - (300)
            top.geometry(f"800x600+{x}+{y}")

            # Frame principal con scroll
            canvas = tk.Canvas(top, bg='white')
            scrollbar = ttk.Scrollbar(top, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='white')
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Header con título
            header_frame = tk.Frame(scrollable_frame, bg='#3498DB', height=80)
            header_frame.pack(fill="x", pady=(0, 20))
            header_frame.pack_propagate(False)
            
            tk.Label(header_frame, 
                    text=f"Pedido #{pedido.numero_oferta}",
                    font=('Segoe UI', 18, 'bold'),
                    bg='#3498DB', fg='white').pack(pady=15)
            
            tk.Label(header_frame,
                    text=f"Proveedor: {pedido.proveedor}",
                    font=('Segoe UI', 11),
                    bg='#3498DB', fg='#BDC3C7').pack()

            # BARRA DE PROGRESO - Característica principal
            progress_frame = tk.Frame(scrollable_frame, bg='white', pady=20)
            progress_frame.pack(fill="x", padx=20, pady=(0, 30))
            
            tk.Label(progress_frame,
                    text="Estado del Pedido",
                    font=('Segoe UI', 14, 'bold'),
                    bg='white', fg='#2C3E50').pack(pady=(0, 15))
            
            # Crear y mostrar barra de progreso
            progress_bar = ProgressBar(progress_frame, width=750, height=60, bg='white')
            progress_bar.pack(pady=(0, 10))
            progress_bar.update_progress(pedido.status)
            
            # Estado actual texto
            tk.Label(progress_frame,
                    text=f"Estado actual: {pedido.status}",
                    font=('Segoe UI', 11),
                    bg='white', fg='#7F8C8D').pack()

            # Información del pedido
            info_frame = tk.Frame(scrollable_frame, bg='#F8F9FA', relief='solid', bd=1)
            info_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            tk.Label(info_frame,
                    text="Información del Pedido",
                    font=('Segoe UI', 12, 'bold'),
                    bg='#F8F9FA', fg='#2C3E50').pack(pady=(15, 10))
            
            # Grid de información
            info_grid = tk.Frame(info_frame, bg='#F8F9FA')
            info_grid.pack(padx=20, pady=(0, 15))
            
            # Datos básicos
            datos = [
                ("Nº Oferta:", pedido.numero_oferta),
                ("Nº Pedido:", pedido.numero_pedido or "Pendiente"),
                ("Requisition ID:", pedido.requisition_id or "Pendiente"),
                ("OI:", str(pedido.oi) if pedido.oi > 0 else "Pendiente"),
                ("Tracking:", pedido.tracking_number or "Pendiente"),
                ("Fecha Creación:", pedido.fecha_creacion.strftime("%d/%m/%Y %H:%M") if pedido.fecha_creacion else "N/A")
            ]
            
            for i, (label, value) in enumerate(datos):
                row = i // 2
                col = (i % 2) * 2
                
                tk.Label(info_grid, text=label, font=('Segoe UI', 10, 'bold'),
                        bg='#F8F9FA', fg='#2C3E50', anchor='w').grid(
                        row=row, column=col, sticky='w', padx=(0, 10), pady=2)
                
                tk.Label(info_grid, text=value, font=('Segoe UI', 10),
                        bg='#F8F9FA', fg='#7F8C8D', anchor='w').grid(
                        row=row, column=col+1, sticky='w', padx=(0, 40), pady=2)

            # Campos editables según el estado
            campos_requeridos = pedido.get_campos_requeridos()
            entries = {}
            
            if campos_requeridos:
                edit_frame = tk.Frame(scrollable_frame, bg='#FFFFFF', relief='solid', bd=1)
                edit_frame.pack(fill="x", padx=20, pady=(0, 20))
                
                tk.Label(edit_frame,
                        text="✏️ Campos para Avanzar al Siguiente Estado",
                        font=('Segoe UI', 12, 'bold'),
                        bg='#FFFFFF', fg='#E74C3C').pack(pady=(15, 10))
                
                edit_grid = tk.Frame(edit_frame, bg='#FFFFFF')
                edit_grid.pack(padx=20, pady=(0, 15))
                
                row = 0
                if "requisition_id" in campos_requeridos:
                    tk.Label(edit_grid, text="Requisition ID:", 
                            font=('Segoe UI', 10, 'bold'),
                            bg='#FFFFFF').grid(row=row, column=0, sticky='w', pady=5)
                    entries["requisition_id"] = tk.Entry(edit_grid, width=40, font=('Segoe UI', 10))
                    entries["requisition_id"].grid(row=row, column=1, sticky='w', padx=10, pady=5)
                    entries["requisition_id"].insert(0, pedido.requisition_id)
                    row += 1
                
                if "oi" in campos_requeridos:
                    tk.Label(edit_grid, text="OI (número):", 
                            font=('Segoe UI', 10, 'bold'),
                            bg='#FFFFFF').grid(row=row, column=0, sticky='w', pady=5)
                    entries["oi"] = tk.Entry(edit_grid, width=40, font=('Segoe UI', 10))
                    entries["oi"].grid(row=row, column=1, sticky='w', padx=10, pady=5)
                    entries["oi"].insert(0, str(pedido.oi) if pedido.oi > 0 else "")
                    row += 1
                
                if "numero_pedido" in campos_requeridos:
                    tk.Label(edit_grid, text="Número de Pedido:", 
                            font=('Segoe UI', 10, 'bold'),
                            bg='#FFFFFF').grid(row=row, column=0, sticky='w', pady=5)
                    entries["numero_pedido"] = tk.Entry(edit_grid, width=40, font=('Segoe UI', 10))
                    entries["numero_pedido"].grid(row=row, column=1, sticky='w', padx=10, pady=5)
                    entries["numero_pedido"].insert(0, pedido.numero_pedido)
                    row += 1
                
                if "po_pdf" in campos_requeridos:
                    tk.Label(edit_grid, text="PDF del PO:", 
                            font=('Segoe UI', 10, 'bold'),
                            bg='#FFFFFF').grid(row=row, column=0, sticky='w', pady=5)
                    
                    pdf_frame = tk.Frame(edit_grid, bg='#FFFFFF')
                    pdf_frame.grid(row=row, column=1, sticky='w', padx=10, pady=5)
                    
                    entries["po_pdf"] = tk.Entry(pdf_frame, width=30, font=('Segoe UI', 10))
                    entries["po_pdf"].pack(side="left")
                    entries["po_pdf"].insert(0, pedido.po_pdf)
                    
                    def seleccionar_po_pdf():
                        path = filedialog.askopenfilename(title="Selecciona PDF del PO", filetypes=[("PDF files", "*.pdf")])
                        if path:
                            entries["po_pdf"].delete(0, tk.END)
                            entries["po_pdf"].insert(0, path)
                    
                    tk.Button(pdf_frame, text="📁 Buscar", command=seleccionar_po_pdf,
                             font=('Segoe UI', 9), bg='#3498DB', fg='white',
                             relief='flat', padx=10).pack(side="left", padx=(5, 0))

            # Botones de acción
            button_frame = tk.Frame(scrollable_frame, bg='white')
            button_frame.pack(fill="x", padx=20, pady=20)
            
            def guardar_y_avanzar():
                try:
                    # Actualizar campos
                    for campo, entry in entries.items():
                        if campo == "oi":
                            try:
                                pedido.oi = int(entry.get()) if entry.get().strip() else 0
                            except ValueError:
                                pedido.oi = 0
                        else:
                            setattr(pedido, campo, entry.get().strip())
                    
                    # Avanzar estado
                    if pedido.puede_avanzar_estado():
                        pedido.avanzar_estado()
                        self.manager.guardar_datos()
                        self.refrescar_tabla()
                        
                        # Actualizar barra de progreso
                        progress_bar.update_progress(pedido.status)
                        
                        messagebox.showinfo("Éxito", "Estado avanzado correctamente")
                    else:
                        messagebox.showwarning("Advertencia", "Complete los campos requeridos para avanzar")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
            
            def solo_guardar():
                try:
                    for campo, entry in entries.items():
                        if campo == "oi":
                            try:
                                pedido.oi = int(entry.get()) if entry.get().strip() else 0
                            except ValueError:
                                pedido.oi = 0
                        else:
                            setattr(pedido, campo, entry.get().strip())
                    
                    self.manager.guardar_datos()
                    self.refrescar_tabla()
                    messagebox.showinfo("Éxito", "Datos guardados correctamente")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error al guardar: {str(e)}")
            
            # Botones
            if entries:
                tk.Button(button_frame, text="💾 Guardar Cambios", command=solo_guardar,
                         font=('Segoe UI', 11, 'bold'), bg='#3498DB', fg='white',
                         relief='flat', padx=20, pady=10).pack(side="left", padx=(0, 10))
                
                if pedido.puede_avanzar_estado():
                    tk.Button(button_frame, text="⬆️ Guardar y Avanzar Estado", command=guardar_y_avanzar,
                             font=('Segoe UI', 11, 'bold'), bg='#27AE60', fg='white',
                             relief='flat', padx=20, pady=10).pack(side="left", padx=(0, 10))
            
            tk.Button(button_frame, text="❌ Cerrar", command=top.destroy,
                     font=('Segoe UI', 11), bg='#95A5A6', fg='white',
                     relief='flat', padx=20, pady=10).pack(side="right")

            # Empaquetar canvas y scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
                            entries["po_pdf"].delete(0, "end")
                            entries["po_pdf"].insert(0, path)
                    ttk.Button(pdf_frame, text="Seleccionar", command=seleccionar_po_pdf).pack(side="left", padx=(5,0))
                
                if "etiquetas_pdf" in campos_requeridos:
                    ttk.Label(main_frame, text="PDF de Etiquetas:").pack(anchor="w")
                    etiq_frame = ttk.Frame(main_frame)
                    etiq_frame.pack(anchor="w", padx=(20,0), fill="x")
                    entries["etiquetas_pdf"] = ttk.Entry(etiq_frame, width=40)
                    entries["etiquetas_pdf"].pack(side="left")
                    entries["etiquetas_pdf"].insert(0, pedido.etiquetas_pdf)
                    def seleccionar_etiq_pdf():
                        path = filedialog.askopenfilename(title="Selecciona PDF de Etiquetas", filetypes=[("PDF files", "*.pdf")])
                        if path:
                            entries["etiquetas_pdf"].delete(0, "end")
                            entries["etiquetas_pdf"].insert(0, path)
                    ttk.Button(etiq_frame, text="Seleccionar", command=seleccionar_etiq_pdf).pack(side="left", padx=(5,0))
                
                if "numero_bultos" in campos_requeridos:
                    ttk.Label(main_frame, text="Número de Bultos:").pack(anchor="w")
                    entries["numero_bultos"] = ttk.Entry(main_frame, width=50)
                    entries["numero_bultos"].pack(anchor="w", padx=(20,0))
                    entries["numero_bultos"].insert(0, str(pedido.numero_bultos) if pedido.numero_bultos > 0 else "")
                
                if "peso_total" in campos_requeridos:
                    ttk.Label(main_frame, text="Peso Total (kg):").pack(anchor="w")
                    entries["peso_total"] = ttk.Entry(main_frame, width=50)
                    entries["peso_total"].pack(anchor="w", padx=(20,0))
                    entries["peso_total"].insert(0, str(pedido.peso_total) if pedido.peso_total > 0 else "")
                
                if "dimensiones" in campos_requeridos:
                    ttk.Label(main_frame, text="Dimensiones (LxAxA):").pack(anchor="w")
                    entries["dimensiones"] = ttk.Entry(main_frame, width=50)
                    entries["dimensiones"].pack(anchor="w", padx=(20,0))
                    entries["dimensiones"].insert(0, pedido.dimensiones)
                
                # Botón para guardar cambios
                def guardar_cambios():
                    try:
                        if "requisition_id" in entries:
                            pedido.requisition_id = entries["requisition_id"].get().strip()
                        if "oi" in entries:
                            oi_text = entries["oi"].get().strip()
                            pedido.oi = int(oi_text) if oi_text else 0
                        if "numero_pedido" in entries:
                            pedido.numero_pedido = entries["numero_pedido"].get().strip()
                        if "po_pdf" in entries:
                            pedido.po_pdf = entries["po_pdf"].get().strip()
                        if "etiquetas_pdf" in entries:
                            pedido.etiquetas_pdf = entries["etiquetas_pdf"].get().strip()
                        if "numero_bultos" in entries:
                            bultos_text = entries["numero_bultos"].get().strip()
                            pedido.numero_bultos = int(bultos_text) if bultos_text else 0
                        if "peso_total" in entries:
                            peso_text = entries["peso_total"].get().strip()
                            pedido.peso_total = float(peso_text) if peso_text else 0.0
                        if "dimensiones" in entries:
                            pedido.dimensiones = entries["dimensiones"].get().strip()
                        
                        self.manager.actualizar_pedido(pedido)  # Guardar cambios
                        self.refrescar_tabla()
                        messagebox.showinfo("Éxito", "Cambios guardados correctamente", parent=top)
                    except ValueError as e:
                        messagebox.showerror("Error", "Por favor, introduce valores numéricos válidos", parent=top)
                    except Exception as e:
                        messagebox.showerror("Error", f"Error al guardar: {str(e)}", parent=top)
                
                ttk.Button(main_frame, text="Guardar Cambios", command=guardar_cambios).pack(pady=10)
            
            # Separador
            ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=5)
            
            # Mostrar información completa
            info_frame = ttk.LabelFrame(main_frame, text="Información Completa del Pedido")
            info_frame.pack(fill="x", pady=5)
            
            # Crear un frame con scroll para la información
            info_canvas = tk.Canvas(info_frame, height=150)
            info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=info_canvas.yview)
            info_scrollable_frame = ttk.Frame(info_canvas)
            
            info_scrollable_frame.bind(
                "<Configure>",
                lambda e: info_canvas.configure(scrollregion=info_canvas.bbox("all"))
            )
            
            info_canvas.create_window((0, 0), window=info_scrollable_frame, anchor="nw")
            info_canvas.configure(yscrollcommand=info_scrollbar.set)
            
            # Información básica
            ttk.Label(info_scrollable_frame, text=f"Requisition ID: {pedido.requisition_id or '-'}", font=("Arial", 9)).pack(anchor="w")
            ttk.Label(info_scrollable_frame, text=f"OI: {pedido.oi if pedido.oi > 0 else '-'}", font=("Arial", 9)).pack(anchor="w")
            ttk.Label(info_scrollable_frame, text=f"Nº Pedido: {pedido.numero_pedido or '-'}", font=("Arial", 9)).pack(anchor="w")
            ttk.Label(info_scrollable_frame, text=f"Nº PO: {pedido.numero_po or '-'}", font=("Arial", 9)).pack(anchor="w")
            
            # PDFs con botones para abrir
            if pedido.po_pdf:
                pdf_frame = ttk.Frame(info_scrollable_frame)
                pdf_frame.pack(anchor="w", fill="x")
                ttk.Label(pdf_frame, text=f"PDF PO: {os.path.basename(pedido.po_pdf)}", font=("Arial", 9)).pack(side="left")
                ttk.Button(pdf_frame, text="Abrir", command=lambda: self.abrir_archivo(pedido.po_pdf)).pack(side="left", padx=(5,0))
            else:
                ttk.Label(info_scrollable_frame, text="PDF PO: -", font=("Arial", 9)).pack(anchor="w")
            
            if pedido.etiquetas_pdf:
                etiq_frame = ttk.Frame(info_scrollable_frame)
                etiq_frame.pack(anchor="w", fill="x")
                ttk.Label(etiq_frame, text=f"PDF Etiquetas: {os.path.basename(pedido.etiquetas_pdf)}", font=("Arial", 9)).pack(side="left")
                ttk.Button(etiq_frame, text="Abrir", command=lambda: self.abrir_archivo(pedido.etiquetas_pdf)).pack(side="left", padx=(5,0))
            else:
                ttk.Label(info_scrollable_frame, text="PDF Etiquetas: -", font=("Arial", 9)).pack(anchor="w")
            
            # Información del paquete
            ttk.Label(info_scrollable_frame, text=f"Número de Bultos: {pedido.numero_bultos if pedido.numero_bultos > 0 else '-'}", font=("Arial", 9)).pack(anchor="w")
            ttk.Label(info_scrollable_frame, text=f"Peso Total: {pedido.peso_total if pedido.peso_total > 0 else '-'} kg", font=("Arial", 9)).pack(anchor="w")
            ttk.Label(info_scrollable_frame, text=f"Dimensiones: {pedido.dimensiones or '-'}", font=("Arial", 9)).pack(anchor="w")
            ttk.Label(info_scrollable_frame, text=f"Tracking: {pedido.tracking_number or '-'}", font=("Arial", 9)).pack(anchor="w")
            
            # Referencias
            if pedido.referencias:
                ttk.Label(info_scrollable_frame, text="Referencias:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,5))
                for i, ref in enumerate(pedido.referencias, 1):
                    ttk.Label(info_scrollable_frame, text=f"  {i}. {ref.codigo} - {ref.descripcion} (Cant: {ref.cantidad}, Proyecto: {ref.proyecto})", font=("Arial", 8)).pack(anchor="w")
            
            # Fechas importantes
            if pedido.fecha_creacion:
                ttk.Label(info_scrollable_frame, text=f"Fecha creación: {pedido.fecha_creacion.strftime('%d/%m/%Y %H:%M')}", font=("Arial", 9)).pack(anchor="w")
            if pedido.fecha_eproc_borrador:
                ttk.Label(info_scrollable_frame, text=f"Fecha borrador: {pedido.fecha_eproc_borrador.strftime('%d/%m/%Y %H:%M')}", font=("Arial", 9)).pack(anchor="w")
            if pedido.fecha_eproc_firmado:
                ttk.Label(info_scrollable_frame, text=f"Fecha firmado: {pedido.fecha_eproc_firmado.strftime('%d/%m/%Y %H:%M')}", font=("Arial", 9)).pack(anchor="w")
            
            info_canvas.pack(side="left", fill="both", expand=True)
            info_scrollbar.pack(side="right", fill="y")
            
            # Mostrar historial
            ttk.Label(main_frame, text="Historial:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10,5))
            historial_text = tk.Text(main_frame, height=6, width=70)
            historial_text.pack(fill="x")
            historial_text.insert("end", "\n".join(pedido.historial) if pedido.historial else "Sin historial")
            historial_text.config(state="disabled")
            
            # Botón para avanzar estado
            def avanzar():
                if not pedido.puede_avanzar_estado():
                    campos = pedido.get_campos_requeridos()
                    messagebox.showerror("Error", f"Para avanzar al siguiente estado, debes completar los campos: {', '.join(campos)}", parent=top)
                    return
                
                estados = [
                    PedidoStatus.OFERTA,
                    PedidoStatus.PEDIDO_EPROC_BORRADOR,
                    PedidoStatus.PEDIDO_EPROC_ENVIADO_NO_FIRMADO,
                    PedidoStatus.PEDIDO_EPROC_ENVIADO_FIRMADO,
                    PedidoStatus.TAR_LANZADO_NO_ETIQUETAS,
                    PedidoStatus.TAR_LANZADO_SI_ETIQUETAS,
                    PedidoStatus.ETIQUETAS_ENVIADAS,
                    PedidoStatus.PAQUETE_RECOGIDO,
                    PedidoStatus.PAQUETE_EN_CAMINO,
                    PedidoStatus.PAQUETE_EN_CASA,
                    PedidoStatus.COMPLETADO
                ]
                try:
                    idx = estados.index(pedido.status)
                    if idx < len(estados) - 1:
                        pedido.status = estados[idx+1]
                        pedido.historial.append(f"{datetime.now()} - Estado cambiado a: {pedido.status}")
                        self.manager.actualizar_pedido(pedido)  # Guardar cambios
                        self.refrescar_tabla()
                        messagebox.showinfo("Estado", f"Avanzado a: {pedido.status}", parent=top)
                        top.destroy()
                    else:
                        messagebox.showinfo("Estado", "El pedido ya está en el estado final", parent=top)
                except ValueError:
                    messagebox.showerror("Error", "Estado actual no válido", parent=top)
            
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(pady=10)
            ttk.Button(button_frame, text="Avanzar Estado", command=avanzar).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Cerrar", command=top.destroy).pack(side="left", padx=5)

def simple_input(prompt, parent=None):
    if parent:
        # Usar la ventana padre si se proporciona
        root = parent
    else:
        # Crear ventana temporal si no hay padre
        root = tk.Tk()
        root.withdraw()
    
    result = simpledialog.askstring("Input", prompt, parent=root)
    
    if not parent:
        root.destroy()
    
    return result

if __name__ == "__main__":
    manager = PedidoManager()
    app = PedidoApp(manager)
    app.mainloop()
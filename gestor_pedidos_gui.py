import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
from datetime import date
from typing import List, Dict, Any

class GestorPedidosGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Pedidos")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f8fafc')
        
        # Archivo para guardar datos
        self.data_file = "pedidos_data.json"
        
        # Cargar datos
        self.pedidos = self.cargar_datos()
        self.next_id = self.get_next_id()
        
        # Estados del workflow según especificación
        self.estados = ['oferta_recibida', 'eproc_lanzado_no_firmado', 'eproc_firmado', 
                       'packing_list', 'tar_lanzado', 'etiquetas_enviadas', 
                       'paquete_recogido_proveedor', 'paquete_en_almacen', 
                       'paquete_recogido', 'completado']
        self.nombres_estados = {
            'oferta_recibida': 'Oferta\nRecibida',
            'eproc_lanzado_no_firmado': 'Eproc\nLanzado',
            'eproc_firmado': 'Eproc\nFirmado',
            'packing_list': 'Packing\nList',
            'tar_lanzado': 'TAR\nLanzado',
            'etiquetas_enviadas': 'Etiquetas\nEnviadas',
            'paquete_recogido_proveedor': 'Recogido\nProveedor',
            'paquete_en_almacen': 'En\nAlmacén',
            'paquete_recogido': 'Paquete\nRecogido',
            'completado': 'Completado'
        }
        
        self.setup_styles()
        self.create_widgets()
        self.actualizar_lista_pedidos()

    def setup_styles(self):
        """Configurar estilos para la aplicación"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f8fafc')
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), background='white')
        style.configure('Custom.TButton', font=('Arial', 10))
        style.configure('Success.TButton', background='#10b981')
        style.configure('Danger.TButton', background='#ef4444')

    def create_widgets(self):
        """Crear la interfaz principal"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f8fafc', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Gestor de Pedidos", style='Title.TLabel')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        btn_crear = ttk.Button(header_frame, text="+ Crear Pedido", 
                              command=self.abrir_crear_pedido, style='Custom.TButton')
        btn_crear.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Panel de pedidos
        pedidos_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=1)
        pedidos_frame.pack(fill=tk.BOTH, expand=True)
        
        panel_title = ttk.Label(pedidos_frame, text="Panel de Pedidos", style='Heading.TLabel')
        panel_title.pack(anchor=tk.W, padx=20, pady=(15, 10))
        
        # Frame para la lista con scrollbar
        list_container = tk.Frame(pedidos_frame, bg='white')
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Canvas y scrollbar para scroll vertical
        self.canvas = tk.Canvas(list_container, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        """Manejar scroll con rueda del mouse"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def cargar_datos(self) -> List[Dict]:
        """Cargar datos desde archivo JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def guardar_datos(self):
        """Guardar datos en archivo JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.pedidos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {e}")

    def get_next_id(self) -> int:
        """Obtener el próximo ID disponible"""
        if not self.pedidos:
            return 1
        return max(pedido['id'] for pedido in self.pedidos) + 1

    def actualizar_lista_pedidos(self):
        """Actualizar la visualización de pedidos"""
        # Limpiar frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.pedidos:
            # Estado vacío
            empty_frame = tk.Frame(self.scrollable_frame, bg='white')
            empty_frame.pack(fill=tk.X, pady=50)
            
            empty_label = tk.Label(empty_frame, text="📋", font=('Arial', 48), bg='white')
            empty_label.pack()
            
            no_pedidos_label = tk.Label(empty_frame, text="No hay pedidos registrados", 
                                      font=('Arial', 16), bg='white', fg='#6b7280')
            no_pedidos_label.pack(pady=(10, 5))
            
            subtitle_label = tk.Label(empty_frame, text="Comience creando su primer pedido", 
                                    font=('Arial', 12), bg='white', fg='#6b7280')
            subtitle_label.pack(pady=(0, 15))
            
            btn_first = ttk.Button(empty_frame, text="+ Crear primer pedido", 
                                 command=self.abrir_crear_pedido)
            btn_first.pack()
        else:
            # Mostrar pedidos
            for pedido in self.pedidos:
                self.crear_tarjeta_pedido(pedido)

    def crear_tarjeta_pedido(self, pedido: Dict):
        """Crear una tarjeta visual para un pedido"""
        # Frame principal de la tarjeta - Mayor padding y spacing
        card_frame = tk.Frame(self.scrollable_frame, bg='white', relief=tk.RAISED, bd=1)
        card_frame.pack(fill=tk.X, pady=15, padx=15)  # Aumentado padding
        
        # Header del pedido - Mayor espacio vertical
        header_frame = tk.Frame(card_frame, bg='white')
        header_frame.pack(fill=tk.X, padx=25, pady=(20, 15))  # Aumentado padding
        
        # Información del pedido
        info_frame = tk.Frame(header_frame, bg='white')
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = tk.Label(info_frame, text=f"Pedido #{pedido['id']}", 
                              font=('Arial', 16, 'bold'), bg='white', fg='#1f2937')  # Fuente más grande
        title_label.pack(anchor=tk.W, pady=(0, 5))  # Añadido espaciado
        
        subtitle_text = f"{pedido['fecha_creacion']} - {pedido['proveedor']} - €{pedido['total']:.2f}"
        subtitle_label = tk.Label(info_frame, text=subtitle_text, 
                                font=('Arial', 11), bg='white', fg='#6b7280')  # Fuente más grande
        subtitle_label.pack(anchor=tk.W)
        
        # Botones de acción - Mejorados con iconos y mejor spacing
        actions_frame = tk.Frame(header_frame, bg='white')
        actions_frame.pack(side=tk.RIGHT)
        
        btn_toggle = ttk.Button(actions_frame, text="📋 ▼", width=6,
                               command=lambda: self.toggle_detalles(pedido['id']))
        btn_toggle.pack(side=tk.LEFT, padx=8)  # Más espacio entre botones
        
        btn_detalle = ttk.Button(actions_frame, text="👁️ Ver", width=6,
                               command=lambda: self.mostrar_detalle_completo(pedido))
        btn_detalle.pack(side=tk.LEFT, padx=8)
        
        btn_eliminar = ttk.Button(actions_frame, text="🗑️ Eliminar", width=9,
                                command=lambda: self.eliminar_pedido(pedido['id']))
        btn_eliminar.pack(side=tk.LEFT, padx=8)
        
        # Timeline de estados - Más espacio
        self.crear_timeline(card_frame, pedido)
        
        # Botones de navegación - Más espacio
        self.crear_botones_navegacion(card_frame, pedido)
        
        # Panel de detalles (inicialmente oculto) - Más espaciado
        detalles_frame = tk.Frame(card_frame, bg='#f9fafb')
        detalles_frame.pack(fill=tk.X, padx=25, pady=15)  # Aumentado padding
        detalles_frame.pack_forget()  # Ocultar inicialmente
        
        # Guardar referencia para toggle
        setattr(card_frame, f'detalles_frame_{pedido["id"]}', detalles_frame)
        setattr(card_frame, f'toggle_btn_{pedido["id"]}', btn_toggle)
        
        self.crear_panel_detalles(detalles_frame, pedido)

    def crear_timeline(self, parent: tk.Frame, pedido: Dict):
        """Crear timeline visual de estados"""
        timeline_frame = tk.Frame(parent, bg='white', height=90)  # Aumentada altura
        timeline_frame.pack(fill=tk.X, padx=25, pady=15)  # Aumentado padding
        timeline_frame.pack_propagate(False)
        
        estado_actual_index = self.estados.index(pedido['estado'])
        
        # Crear pasos del timeline
        for i, estado in enumerate(self.estados):
            step_frame = tk.Frame(timeline_frame, bg='white')
            step_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Círculo del estado
            is_active = i <= estado_actual_index
            circle_color = '#10b981' if is_active else '#e5e7eb'
            text_color = 'white' if is_active else '#6b7280'
            
            circle_frame = tk.Frame(step_frame, bg='white')
            circle_frame.pack(expand=True)
            
            if i < estado_actual_index:
                circle_text = "✓"
            else:
                circle_text = str(i + 1)
                
            circle_label = tk.Label(circle_frame, text=circle_text, 
                                  bg=circle_color, fg=text_color, 
                                  font=('Arial', 10, 'bold'),
                                  width=3, height=1)
            circle_label.pack()
            
            # Etiqueta del estado
            label_color = '#10b981' if is_active else '#6b7280'
            weight = 'bold' if i == estado_actual_index else 'normal'
            
            label_text = self.nombres_estados[estado].replace(' ', '\n')
            state_label = tk.Label(step_frame, text=label_text, 
                                 font=('Arial', 8, weight), 
                                 bg='white', fg=label_color)
            state_label.pack(pady=(5, 0))

    def crear_botones_navegacion(self, parent: tk.Frame, pedido: Dict):
        """Crear botones de navegación de estados"""
        nav_frame = tk.Frame(parent, bg='white')
        nav_frame.pack(pady=15)  # Aumentado padding
        
        # Botón retroceder
        if pedido['estado'] != 'oferta_recibida':
            btn_anterior = ttk.Button(nav_frame, text="← Anterior", 
                                    command=lambda: self.retroceder_estado(pedido['id']))
            btn_anterior.pack(side=tk.LEFT, padx=8)  # Aumentado padding
        
        # Botón principal según estado
        if pedido['estado'] == 'oferta_recibida':
            btn_eproc = ttk.Button(nav_frame, text="🚀 Lanzar Eproc", 
                                 command=lambda: self.lanzar_eproc(pedido['id']))
            btn_eproc.pack(side=tk.LEFT, padx=8)
        elif pedido['estado'] == 'eproc_lanzado_no_firmado':
            btn_firmar = ttk.Button(nav_frame, text="✍️ Firmar Eproc", 
                                  command=lambda: self.firmar_eproc(pedido['id']))
            btn_firmar.pack(side=tk.LEFT, padx=8)
        elif pedido['estado'] == 'eproc_firmado':
            btn_packing = ttk.Button(nav_frame, text="📦 Crear Packing List", 
                                   command=lambda: self.crear_packing_list(pedido['id']))
            btn_packing.pack(side=tk.LEFT, padx=8)
        elif pedido['estado'] == 'packing_list':
            btn_tar = ttk.Button(nav_frame, text="🚚 Lanzar TAR", 
                               command=lambda: self.lanzar_tar(pedido['id']))
            btn_tar.pack(side=tk.LEFT, padx=8)
        elif pedido['estado'] == 'tar_lanzado':
            btn_etiquetas = ttk.Button(nav_frame, text="🏷️ Enviar Etiquetas", 
                                     command=lambda: self.enviar_etiquetas(pedido['id']))
            btn_etiquetas.pack(side=tk.LEFT, padx=8)
        elif pedido['estado'] != 'completado':
            btn_siguiente = ttk.Button(nav_frame, text="▶️ Siguiente", 
                                     command=lambda: self.avanzar_estado(pedido['id']))
            btn_siguiente.pack(side=tk.LEFT, padx=8)
        else:
            btn_completado = tk.Label(nav_frame, text="✅ Completado", 
                                    bg='#10b981', fg='white', 
                                    font=('Arial', 10, 'bold'), 
                                    padx=15, pady=8)  # Aumentado padding
            btn_completado.pack(side=tk.LEFT, padx=8)

    def crear_panel_detalles(self, parent: tk.Frame, pedido: Dict):
        """Crear panel de detalles expandible"""
        # Título
        title_label = tk.Label(parent, text="Información del proceso", 
                             font=('Arial', 12, 'bold'), bg='#f9fafb', fg='#374151')
        title_label.pack(anchor=tk.W, pady=(10, 5))
        
        # Información de la oferta
        oferta_frame = tk.LabelFrame(parent, text="OFERTA RECIBIDA", 
                                   font=('Arial', 9, 'bold'), 
                                   bg='#f9fafb', fg='#6b7280')
        oferta_frame.pack(fill=tk.X, pady=5)
        
        oferta_info = tk.Frame(oferta_frame, bg='#f9fafb')
        oferta_info.pack(fill=tk.X, padx=10, pady=5)
        
        # Columna izquierda
        left_col = tk.Frame(oferta_info, bg='#f9fafb')
        left_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(left_col, text=f"Número: {pedido['numero_oferta']}", 
                bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)
        tk.Label(left_col, text=f"Email: {pedido.get('email_proveedor', 'N/A')}", 
                bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)
        
        # Columna derecha
        right_col = tk.Frame(oferta_info, bg='#f9fafb')
        right_col.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        tk.Label(right_col, text=f"Items: {len(pedido['piezas'])}", 
                bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)
        tk.Label(right_col, text=f"Total: €{pedido['total']:.2f}", 
                bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)
        
        # Información del Eproc si existe
        if 'eproc' in pedido and pedido['eproc']:
            eproc_frame = tk.LabelFrame(parent, text="EPROC LANZADO", 
                                      font=('Arial', 9, 'bold'), 
                                      bg='#f9fafb', fg='#6b7280')
            eproc_frame.pack(fill=tk.X, pady=5)
            
            eproc_info = tk.Frame(eproc_frame, bg='#f9fafb')
            eproc_info.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(eproc_info, text=f"Número: {pedido['eproc']['numero']}", 
                    bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)
            if pedido['eproc'].get('oi'):
                tk.Label(eproc_info, text=f"OI: {pedido['eproc']['oi']}", 
                        bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)
            if pedido['eproc'].get('fecha'):
                tk.Label(eproc_info, text=f"Fecha: {pedido['eproc']['fecha']}", 
                        bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)

        # Información del Eproc Firmado si existe
        if 'eproc_firmado' in pedido and pedido['eproc_firmado']:
            firmado_frame = tk.LabelFrame(parent, text="EPROC FIRMADO", 
                                        font=('Arial', 9, 'bold'), 
                                        bg='#f9fafb', fg='#6b7280')
            firmado_frame.pack(fill=tk.X, pady=5)
            
            firmado_info = tk.Frame(firmado_frame, bg='#f9fafb')
            firmado_info.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(firmado_info, text=f"PO: {pedido['eproc_firmado']['po']}", 
                    bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)
            tk.Label(firmado_info, text=f"Fecha: {pedido['eproc_firmado']['fecha']}", 
                    bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)
            if pedido['eproc_firmado'].get('pdf'):
                tk.Label(firmado_info, text=f"PDF: {pedido['eproc_firmado']['pdf']}", 
                        bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)

        # Información del Packing List si existe
        if 'packing_list' in pedido and pedido['packing_list']:
            packing_frame = tk.LabelFrame(parent, text="PACKING LIST", 
                                        font=('Arial', 9, 'bold'), 
                                        bg='#f9fafb', fg='#6b7280')
            packing_frame.pack(fill=tk.X, pady=5)
            
            packing_info = tk.Frame(packing_frame, bg='#f9fafb')
            packing_info.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(packing_info, text=f"Dirección: {pedido['packing_list']['direccion']}", 
                    bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)
            tk.Label(packing_info, text=f"Bultos: {pedido['packing_list']['bultos']}", 
                    bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)
            if pedido['packing_list'].get('pdf'):
                tk.Label(packing_info, text=f"PDF: {pedido['packing_list']['pdf']}", 
                        bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)

        # Información del TAR si existe
        if 'tar' in pedido and pedido['tar']:
            tar_frame = tk.LabelFrame(parent, text="TAR LANZADO", 
                                    font=('Arial', 9, 'bold'), 
                                    bg='#f9fafb', fg='#6b7280')
            tar_frame.pack(fill=tk.X, pady=5)
            
            tar_info = tk.Frame(tar_frame, bg='#f9fafb')
            tar_info.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(tar_info, text=f"Número TAR: {pedido['tar']['numero']}", 
                    bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)
            tk.Label(tar_info, text=f"Email: {pedido['tar']['email']}", 
                    bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)
            if pedido['tar'].get('url'):
                tk.Label(tar_info, text=f"URL: {pedido['tar']['url']}", 
                        bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)

        # Información de las Etiquetas si existe
        if 'etiquetas' in pedido and pedido['etiquetas']:
            etiquetas_frame = tk.LabelFrame(parent, text="ETIQUETAS ENVIADAS", 
                                          font=('Arial', 9, 'bold'), 
                                          bg='#f9fafb', fg='#6b7280')
            etiquetas_frame.pack(fill=tk.X, pady=5)
            
            etiquetas_info = tk.Frame(etiquetas_frame, bg='#f9fafb')
            etiquetas_info.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(etiquetas_info, text=f"Tracking: {pedido['etiquetas']['tracking']}", 
                    bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)
            if pedido['etiquetas'].get('pdf'):
                tk.Label(etiquetas_info, text=f"PDF: {pedido['etiquetas']['pdf']}", 
                        bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)

        # Información de Estados Posteriores
        if pedido['estado'] in ['paquete_recogido_proveedor', 'paquete_en_almacen', 'paquete_recogido', 'completado']:
            estados_frame = tk.LabelFrame(parent, text="ESTADOS POSTERIORES", 
                                        font=('Arial', 9, 'bold'), 
                                        bg='#f9fafb', fg='#6b7280')
            estados_frame.pack(fill=tk.X, pady=5)
            
            estados_info = tk.Frame(estados_frame, bg='#f9fafb')
            estados_info.pack(fill=tk.X, padx=10, pady=5)
            
            estado_actual = self.nombres_estados.get(pedido['estado'], pedido['estado'])
            tk.Label(estados_info, text=f"Estado actual: {estado_actual}", 
                    bg='#f9fafb', font=('Arial', 9, 'bold')).pack(anchor=tk.W)
            
            if pedido['estado'] == 'paquete_recogido_proveedor':
                tk.Label(estados_info, text="✓ Paquete recogido del proveedor", 
                        bg='#f9fafb', font=('Arial', 9), fg='#10b981').pack(anchor=tk.W)
            elif pedido['estado'] == 'paquete_en_almacen':
                tk.Label(estados_info, text="✓ Paquete recogido del proveedor", 
                        bg='#f9fafb', font=('Arial', 9), fg='#10b981').pack(anchor=tk.W)
                tk.Label(estados_info, text="✓ Paquete en almacén", 
                        bg='#f9fafb', font=('Arial', 9), fg='#10b981').pack(anchor=tk.W)
            elif pedido['estado'] == 'paquete_recogido':
                tk.Label(estados_info, text="✓ Paquete recogido del proveedor", 
                        bg='#f9fafb', font=('Arial', 9), fg='#10b981').pack(anchor=tk.W)
                tk.Label(estados_info, text="✓ Paquete en almacén", 
                        bg='#f9fafb', font=('Arial', 9), fg='#10b981').pack(anchor=tk.W)
                tk.Label(estados_info, text="✓ Paquete recogido", 
                        bg='#f9fafb', font=('Arial', 9), fg='#10b981').pack(anchor=tk.W)
            elif pedido['estado'] == 'completado':
                tk.Label(estados_info, text="✅ PROCESO COMPLETADO", 
                        bg='#f9fafb', font=('Arial', 9, 'bold'), fg='#10b981').pack(anchor=tk.W)

        # Sección de documentos
        docs_frame = tk.LabelFrame(parent, text="DOCUMENTOS", 
                                 font=('Arial', 9, 'bold'), 
                                 bg='#f9fafb', fg='#6b7280')
        docs_frame.pack(fill=tk.X, pady=(10, 5))
        
        docs_info = tk.Frame(docs_frame, bg='#f9fafb')
        docs_info.pack(fill=tk.X, padx=10, pady=5)
        
        # Lista de documentos según el estado
        documentos = [f"📄 Oferta_{pedido['numero_oferta']}.pdf"]
        
        if 'eproc' in pedido and pedido['eproc']:
            documentos.append(f"📄 Eproc_{pedido['eproc']['numero']}.pdf")
        
        if 'eproc_firmado' in pedido and pedido['eproc_firmado']:
            documentos.append(f"📄 PO_{pedido['eproc_firmado']['po']}.pdf")
        
        if 'packing_list' in pedido and pedido['packing_list']:
            documentos.append(f"📄 PackingList_{pedido['id']}.pdf")
        
        if 'etiquetas' in pedido and pedido['etiquetas']:
            documentos.append(f"📄 Etiquetas_{pedido['etiquetas']['tracking']}.pdf")
        
        for doc in documentos:
            tk.Label(docs_info, text=doc, bg='#f9fafb', font=('Arial', 9)).pack(anchor=tk.W)

    def toggle_detalles(self, pedido_id: int):
        """Alternar visualización de detalles"""
        for widget in self.scrollable_frame.winfo_children():
            if hasattr(widget, f'detalles_frame_{pedido_id}'):
                detalles_frame = getattr(widget, f'detalles_frame_{pedido_id}')
                toggle_btn = getattr(widget, f'toggle_btn_{pedido_id}')
                
                if detalles_frame.winfo_viewable():
                    detalles_frame.pack_forget()
                    toggle_btn.config(text="📋 ▼")
                else:
                    detalles_frame.pack(fill=tk.X, padx=25, pady=15)
                    toggle_btn.config(text="📋 ▲")
                break

    def abrir_crear_pedido(self):
        """Abrir ventana para crear nuevo pedido"""
        CrearPedidoWindow(self.root, self.agregar_pedido)

    def agregar_pedido(self, pedido_data: Dict):
        """Agregar nuevo pedido"""
        pedido_data['id'] = self.next_id
        pedido_data['fecha_creacion'] = date.today().strftime("%d/%m/%Y")
        pedido_data['estado'] = 'oferta_recibida'
        
        self.pedidos.append(pedido_data)
        self.next_id += 1
        self.guardar_datos()
        self.actualizar_lista_pedidos()

    def crear_eproc(self, pedido_id: int):
        """Abrir ventana para lanzar Eproc"""
        pedido = next((p for p in self.pedidos if p['id'] == pedido_id), None)
        if pedido:
            LanzarEprocWindow(self.root, pedido, self.actualizar_eproc)

    def actualizar_eproc(self, pedido_id: int, eproc_data: Dict):
        """Actualizar pedido con datos del Eproc"""
        for pedido in self.pedidos:
            if pedido['id'] == pedido_id:
                pedido['eproc'] = eproc_data
                pedido['estado'] = 'eproc_lanzado_no_firmado'
                break
        
        self.guardar_datos()
        self.actualizar_lista_pedidos()

    def lanzar_eproc(self, pedido_id: int):
        """Abrir ventana para lanzar Eproc"""
        pedido = next((p for p in self.pedidos if p['id'] == pedido_id), None)
        if pedido:
            LanzarEprocWindow(self.root, pedido, self.actualizar_eproc)

    def firmar_eproc(self, pedido_id: int):
        """Abrir ventana para firmar Eproc"""
        pedido = next((p for p in self.pedidos if p['id'] == pedido_id), None)
        if pedido:
            FirmarEprocWindow(self.root, pedido, self.actualizar_firma_eproc)

    def actualizar_firma_eproc(self, pedido_id: int, firma_data: Dict):
        """Actualizar pedido con datos de firma"""
        for pedido in self.pedidos:
            if pedido['id'] == pedido_id:
                if 'eproc' not in pedido:
                    pedido['eproc'] = {}
                pedido['eproc'].update(firma_data)
                pedido['estado'] = 'eproc_firmado'
                break
        
        self.guardar_datos()
        self.actualizar_lista_pedidos()

    def crear_packing_list(self, pedido_id: int):
        """Abrir ventana para crear packing list"""
        pedido = next((p for p in self.pedidos if p['id'] == pedido_id), None)
        if pedido:
            CrearPackingListWindow(self.root, pedido, self.actualizar_packing_list)

    def actualizar_packing_list(self, pedido_id: int, packing_data: Dict):
        """Actualizar pedido con packing list"""
        for pedido in self.pedidos:
            if pedido['id'] == pedido_id:
                pedido['packing_list'] = packing_data
                pedido['estado'] = 'packing_list'
                break
        
        self.guardar_datos()
        self.actualizar_lista_pedidos()

    def lanzar_tar(self, pedido_id: int):
        """Abrir ventana para lanzar TAR"""
        pedido = next((p for p in self.pedidos if p['id'] == pedido_id), None)
        if pedido:
            LanzarTarWindow(self.root, pedido, self.actualizar_tar)

    def actualizar_tar(self, pedido_id: int, tar_data: Dict):
        """Actualizar pedido con TAR"""
        for pedido in self.pedidos:
            if pedido['id'] == pedido_id:
                pedido['tar'] = tar_data
                pedido['estado'] = 'tar_lanzado'
                break
        
        self.guardar_datos()
        self.actualizar_lista_pedidos()

    def enviar_etiquetas(self, pedido_id: int):
        """Abrir ventana para enviar etiquetas"""
        pedido = next((p for p in self.pedidos if p['id'] == pedido_id), None)
        if pedido:
            EnviarEtiquetasWindow(self.root, pedido, self.actualizar_etiquetas)

    def actualizar_etiquetas(self, pedido_id: int, etiquetas_data: Dict):
        """Actualizar pedido con etiquetas"""
        for pedido in self.pedidos:
            if pedido['id'] == pedido_id:
                pedido['etiquetas'] = etiquetas_data
                pedido['estado'] = 'etiquetas_enviadas'
                break
        
        self.guardar_datos()
        self.actualizar_lista_pedidos()

    def eliminar_pedido(self, pedido_id: int):
        """Eliminar un pedido"""
        if messagebox.askyesno("Confirmar Eliminación", 
                              f"¿Está seguro de que desea eliminar el pedido #{pedido_id}?\n\nEsta acción no se puede deshacer."):
            self.pedidos = [p for p in self.pedidos if p['id'] != pedido_id]
            self.guardar_datos()
            self.actualizar_lista_pedidos()
            messagebox.showinfo("Pedido Eliminado", f"El pedido #{pedido_id} ha sido eliminado exitosamente.")

    def avanzar_estado(self, pedido_id: int):
        """Avanzar estado del pedido"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea avanzar al siguiente estado?"):
            for pedido in self.pedidos:
                if pedido['id'] == pedido_id:
                    estado_index = self.estados.index(pedido['estado'])
                    if estado_index < len(self.estados) - 1:
                        nuevo_estado = self.estados[estado_index + 1]
                        pedido['estado'] = nuevo_estado
                        
                        # Agregar datos automáticos según el estado
                        if nuevo_estado == 'paquete_recogido_proveedor':
                            pedido['fechas'] = pedido.get('fechas', {})
                            pedido['fechas']['recogido_proveedor'] = date.today().strftime("%d/%m/%Y")
                        elif nuevo_estado == 'paquete_en_almacen':
                            pedido['fechas'] = pedido.get('fechas', {})
                            pedido['fechas']['en_almacen'] = date.today().strftime("%d/%m/%Y")
                        elif nuevo_estado == 'paquete_recogido':
                            pedido['fechas'] = pedido.get('fechas', {})
                            pedido['fechas']['recogido'] = date.today().strftime("%d/%m/%Y")
                    break
            
            self.guardar_datos()
            self.actualizar_lista_pedidos()

    def retroceder_estado(self, pedido_id: int):
        """Retroceder estado del pedido"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea retroceder al estado anterior?"):
            for pedido in self.pedidos:
                if pedido['id'] == pedido_id:
                    estado_index = self.estados.index(pedido['estado'])
                    if estado_index > 0:
                        pedido['estado'] = self.estados[estado_index - 1]
                    break
            
            self.guardar_datos()
            self.actualizar_lista_pedidos()

    def mostrar_detalle_completo(self, pedido: Dict):
        """Mostrar ventana de detalle completo"""
        DetallePedidoWindow(self.root, pedido)


class CrearPedidoWindow:
    def __init__(self, parent, callback):
        self.callback = callback
        self.piezas = []
        
        # Crear ventana modal
        self.window = tk.Toplevel(parent)
        self.window.title("Crear Nuevo Pedido")
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()

    def create_widgets(self):
        """Crear widgets de la ventana"""
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(main_frame, text="Crear Nuevo Pedido", 
                             font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Información básica
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(info_frame, text="Número de Oferta *", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.numero_oferta = tk.Entry(info_frame, width=30)
        self.numero_oferta.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(info_frame, text="Proveedor *", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.proveedor = tk.Entry(info_frame, width=30)
        self.proveedor.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(info_frame, text="Email Proveedor", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=5)
        self.email_proveedor = tk.Entry(info_frame, width=30)
        self.email_proveedor.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(info_frame, text="PDF Oferta", font=('Arial', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=5)
        pdf_frame = tk.Frame(info_frame)
        pdf_frame.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W+tk.E)
        self.pdf_oferta = tk.Entry(pdf_frame, width=25)
        self.pdf_oferta.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(pdf_frame, text="Buscar...", 
                 command=self.buscar_pdf_oferta).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Piezas
        piezas_frame = tk.LabelFrame(main_frame, text="Piezas del Pedido", 
                                   font=('Arial', 12, 'bold'))
        piezas_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Botón agregar pieza
        btn_frame = tk.Frame(piezas_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="+ Agregar Pieza", 
                 command=self.agregar_pieza).pack(side=tk.LEFT)
        
        # Lista de piezas
        self.piezas_listbox = tk.Listbox(piezas_frame, height=8)
        self.piezas_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Total
        self.total_label = tk.Label(piezas_frame, text="Total: €0.00", 
                                  font=('Arial', 12, 'bold'))
        self.total_label.pack(pady=5)
        
        # Botones
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(buttons_frame, text="Cancelar", 
                 command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(buttons_frame, text="Crear Pedido", 
                 command=self.crear_pedido).pack(side=tk.RIGHT, padx=5)

    def agregar_pieza(self):
        """Agregar nueva pieza"""
        AgregarPiezaWindow(self.window, self.on_pieza_agregada)

    def on_pieza_agregada(self, pieza_data):
        """Callback cuando se agrega una pieza"""
        self.piezas.append(pieza_data)
        self.actualizar_lista_piezas()

    def actualizar_lista_piezas(self):
        """Actualizar la visualización de piezas"""
        self.piezas_listbox.delete(0, tk.END)
        total = 0
        
        for pieza in self.piezas:
            precio_total = pieza['cantidad'] * pieza['precio_unitario']
            total += precio_total
            
            texto = f"{pieza['referencia']} - {pieza['descripcion']} | Cant: {pieza['cantidad']} | €{precio_total:.2f}"
            self.piezas_listbox.insert(tk.END, texto)
        
        self.total_label.config(text=f"Total: €{total:.2f}")

    def buscar_pdf_oferta(self):
        """Buscar archivo PDF de la oferta"""
        filename = filedialog.askopenfilename(
            title="Seleccionar PDF de la Oferta",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.pdf_oferta.delete(0, tk.END)
            self.pdf_oferta.insert(0, filename)

    def crear_pedido(self):
        """Crear el pedido"""
        if not self.numero_oferta.get() or not self.proveedor.get():
            messagebox.showerror("Error", "Los campos marcados con * son obligatorios")
            return
        
        if not self.piezas:
            messagebox.showerror("Error", "Debe agregar al menos una pieza")
            return
        
        total = sum(p['cantidad'] * p['precio_unitario'] for p in self.piezas)
        
        pedido_data = {
            'numero_oferta': self.numero_oferta.get(),
            'proveedor': self.proveedor.get(),
            'email_proveedor': self.email_proveedor.get(),
            'pdf_oferta': self.pdf_oferta.get(),
            'piezas': self.piezas,
            'total': total
        }
        
        self.callback(pedido_data)
        self.window.destroy()


class AgregarPiezaWindow:
    def __init__(self, parent, callback):
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Agregar Pieza")
        self.window.geometry("400x300")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos
        tk.Label(main_frame, text="Referencia *", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.referencia = tk.Entry(main_frame, width=30)
        self.referencia.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(main_frame, text="Descripción *", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.descripcion = tk.Entry(main_frame, width=30)
        self.descripcion.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(main_frame, text="Proyecto", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=5)
        self.proyecto = tk.Entry(main_frame, width=30)
        self.proyecto.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(main_frame, text="Cantidad *", font=('Arial', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=5)
        self.cantidad = tk.Spinbox(main_frame, from_=1, to=999, width=28)
        self.cantidad.grid(row=3, column=1, padx=10, pady=5)
        
        tk.Label(main_frame, text="Precio Unitario *", font=('Arial', 10, 'bold')).grid(
            row=4, column=0, sticky=tk.W, pady=5)
        self.precio = tk.Entry(main_frame, width=30)
        self.precio.grid(row=4, column=1, padx=10, pady=5)
        
        # Botones
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        tk.Button(buttons_frame, text="Cancelar", 
                 command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(buttons_frame, text="Agregar", 
                 command=self.agregar).pack(side=tk.RIGHT, padx=5)

    def agregar(self):
        if not all([self.referencia.get(), self.descripcion.get(), 
                   self.cantidad.get(), self.precio.get()]):
            messagebox.showerror("Error", "Los campos marcados con * son obligatorios")
            return
        
        try:
            pieza_data = {
                'referencia': self.referencia.get(),
                'descripcion': self.descripcion.get(),
                'proyecto': self.proyecto.get(),
                'cantidad': int(self.cantidad.get()),
                'precio_unitario': float(self.precio.get())
            }
            
            self.callback(pieza_data)
            self.window.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Cantidad y precio deben ser números válidos")


class CrearEprocWindow:
    def __init__(self, parent, pedido, callback):
        self.pedido = pedido
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Crear Eproc")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(main_frame, text="Crear Eproc", 
                             font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(main_frame, 
                                text=f"Pedido #{self.pedido['id']} - {self.pedido['proveedor']}", 
                                font=('Arial', 12))
        subtitle_label.pack(pady=(0, 20))
        
        # Información de la oferta
        info_frame = tk.LabelFrame(main_frame, text="Información de la Oferta Base", 
                                 font=('Arial', 10, 'bold'))
        info_frame.pack(fill=tk.X, pady=10)
        
        info_text = f"""Número Oferta: {self.pedido['numero_oferta']}
Proveedor: {self.pedido['proveedor']}
Email: {self.pedido.get('email_proveedor', 'N/A')}
Total: €{self.pedido['total']:.2f}
Piezas: {len(self.pedido['piezas'])}"""
        
        tk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(padx=10, pady=10)
        
        # Campos del Eproc
        form_frame = tk.LabelFrame(main_frame, text="Datos del Eproc", 
                                 font=('Arial', 10, 'bold'))
        form_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(form_frame, text="Número Eproc *", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.eproc_number = tk.Entry(form_frame, width=30)
        self.eproc_number.grid(row=0, column=1, padx=10, pady=5)
        
        # Auto-completar número
        año = date.today().year
        numero_auto = f"EP{año}-{str(self.pedido['id']).zfill(3)}"
        self.eproc_number.insert(0, numero_auto)
        
        tk.Label(form_frame, text="Número OI (Orden Interna)", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.oi = tk.Entry(form_frame, width=30)
        self.oi.grid(row=1, column=1, padx=10, pady=5)
        
        # Botones
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(buttons_frame, text="Cancelar", 
                 command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(buttons_frame, text="Crear Eproc", 
                 command=self.crear_eproc).pack(side=tk.RIGHT, padx=5)

    def crear_eproc(self):
        if not self.eproc_number.get():
            messagebox.showerror("Error", "El número de Eproc es obligatorio")
            return
        
        eproc_data = {
            'numero': self.eproc_number.get(),
            'oi': self.oi.get(),
            'fecha_creacion': date.today().strftime("%d/%m/%Y")
        }
        
        self.callback(self.pedido['id'], eproc_data)
        self.window.destroy()


class DetallePedidoWindow:
    def __init__(self, parent, pedido):
        self.pedido = pedido
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"Detalle del Pedido #{pedido['id']}")
        self.window.geometry("800x600")
        self.window.transient(parent)
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(main_frame, 
                             text=f"Pedido #{self.pedido['id']} - {self.pedido['proveedor']}", 
                             font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Notebook para pestañas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de información general
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="Información General")
        
        # Pestaña de piezas
        piezas_frame = ttk.Frame(notebook)
        notebook.add(piezas_frame, text="Piezas")
        
        self.create_info_tab(info_frame)
        self.create_piezas_tab(piezas_frame)

    def create_info_tab(self, parent):
        """Crear pestaña de información general"""
        # Crear canvas con scrollbar
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Información básica
        basic_frame = tk.LabelFrame(scrollable_frame, text="Información Básica", 
                                  font=('Arial', 12, 'bold'))
        basic_frame.pack(fill=tk.X, padx=10, pady=10)
        
        basic_info = f"""Número de Oferta: {self.pedido['numero_oferta']}
Proveedor: {self.pedido['proveedor']}
Email Proveedor: {self.pedido.get('email_proveedor', 'N/A')}
Fecha Creación: {self.pedido['fecha_creacion']}
Estado Actual: {self.pedido['estado'].replace('_', ' ').title()}
Total: €{self.pedido['total']:.2f}"""
        
        tk.Label(basic_frame, text=basic_info, justify=tk.LEFT, 
                font=('Arial', 10)).pack(padx=10, pady=10, anchor=tk.W)
        
        # Información del Eproc si existe
        if 'eproc' in self.pedido and self.pedido['eproc']:
            eproc_frame = tk.LabelFrame(scrollable_frame, text="Información del Eproc", 
                                      font=('Arial', 12, 'bold'))
            eproc_frame.pack(fill=tk.X, padx=10, pady=10)
            
            eproc_info = f"""Número Eproc: {self.pedido['eproc']['numero']}
Fecha Creación: {self.pedido['eproc']['fecha_creacion']}"""
            
            if self.pedido['eproc'].get('oi'):
                eproc_info += f"\nOI: {self.pedido['eproc']['oi']}"
            
            tk.Label(eproc_frame, text=eproc_info, justify=tk.LEFT, 
                    font=('Arial', 10)).pack(padx=10, pady=10, anchor=tk.W)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_piezas_tab(self, parent):
        """Crear pestaña de piezas"""
        # Crear Treeview para mostrar piezas en tabla
        columns = ('Referencia', 'Descripción', 'Proyecto', 'Cantidad', 'Precio Unit.', 'Total')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Agregar datos
        for pieza in self.pedido['piezas']:
            precio_total = pieza['cantidad'] * pieza['precio_unitario']
            tree.insert('', tk.END, values=(
                pieza['referencia'],
                pieza['descripcion'],
                pieza.get('proyecto', ''),
                pieza['cantidad'],
                f"€{pieza['precio_unitario']:.2f}",
                f"€{precio_total:.2f}"
            ))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack
        tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Total
        total_label = tk.Label(parent, text=f"TOTAL: €{self.pedido['total']:.2f}", 
                             font=('Arial', 12, 'bold'))
        total_label.grid(row=2, column=0, columnspan=2, pady=10)


class LanzarEprocWindow:
    def __init__(self, parent, pedido, callback):
        self.pedido = pedido
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Lanzar Eproc")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(main_frame, text="Lanzar Eproc", 
                             font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Información del pedido
        info_label = tk.Label(main_frame, 
                            text=f"Pedido #{self.pedido['id']} - {self.pedido['proveedor']}", 
                            font=('Arial', 12))
        info_label.pack(pady=(0, 20))
        
        # Campos
        tk.Label(main_frame, text="Número Eproc *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        self.numero_eproc = tk.Entry(main_frame, width=40)
        self.numero_eproc.pack(pady=5)
        
        tk.Label(main_frame, text="OI *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        self.oi = tk.Entry(main_frame, width=40)
        self.oi.pack(pady=5)
        
        tk.Label(main_frame, text="Fecha *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        self.fecha = tk.Entry(main_frame, width=40)
        self.fecha.pack(pady=5)
        self.fecha.insert(0, date.today().strftime("%d/%m/%Y"))
        
        # Botones
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        tk.Button(buttons_frame, text="Cancelar", 
                 command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(buttons_frame, text="Lanzar", 
                 command=self.lanzar).pack(side=tk.RIGHT, padx=5)

    def lanzar(self):
        if not all([self.numero_eproc.get(), self.oi.get(), self.fecha.get()]):
            messagebox.showerror("Error", "Todos los campos marcados con * son obligatorios")
            return
        
        eproc_data = {
            'numero': self.numero_eproc.get(),
            'oi': self.oi.get(),
            'fecha': self.fecha.get()
        }
        
        self.callback(self.pedido['id'], eproc_data)
        self.window.destroy()


class FirmarEprocWindow:
    def __init__(self, parent, pedido, callback):
        self.pedido = pedido
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Firmar Eproc")
        self.window.geometry("500x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(main_frame, text="Firmar Eproc", 
                             font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Información del pedido
        info_label = tk.Label(main_frame, 
                            text=f"Pedido #{self.pedido['id']} - {self.pedido['proveedor']}", 
                            font=('Arial', 12))
        info_label.pack(pady=(0, 20))
        
        # Campos
        tk.Label(main_frame, text="PO PDF *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        pdf_frame = tk.Frame(main_frame)
        pdf_frame.pack(fill=tk.X, pady=5)
        self.po_pdf = tk.Entry(pdf_frame, width=35)
        self.po_pdf.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(pdf_frame, text="Buscar...", 
                 command=self.buscar_po_pdf).pack(side=tk.RIGHT, padx=(5, 0))
        
        tk.Label(main_frame, text="PO Number *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        self.po_number = tk.Entry(main_frame, width=40)
        self.po_number.pack(pady=5)
        
        tk.Label(main_frame, text="Fecha *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        self.fecha = tk.Entry(main_frame, width=40)
        self.fecha.pack(pady=5)
        self.fecha.insert(0, date.today().strftime("%d/%m/%Y"))
        
        # Botones
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        tk.Button(buttons_frame, text="Cancelar", 
                 command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(buttons_frame, text="Firmar", 
                 command=self.firmar).pack(side=tk.RIGHT, padx=5)

    def buscar_po_pdf(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar PO PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.po_pdf.delete(0, tk.END)
            self.po_pdf.insert(0, filename)

    def firmar(self):
        if not all([self.po_pdf.get(), self.po_number.get(), self.fecha.get()]):
            messagebox.showerror("Error", "Todos los campos marcados con * son obligatorios")
            return
        
        firma_data = {
            'po_pdf': self.po_pdf.get(),
            'po_number': self.po_number.get(),
            'fecha_firma': self.fecha.get()
        }
        
        self.callback(self.pedido['id'], firma_data)
        self.window.destroy()


class CrearPackingListWindow:
    def __init__(self, parent, pedido, callback):
        self.pedido = pedido
        self.callback = callback
        self.bultos = []
        
        self.window = tk.Toplevel(parent)
        self.window.title("Crear Packing List")
        self.window.geometry("700x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(main_frame, text="Crear Packing List", 
                             font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Información del pedido
        info_label = tk.Label(main_frame, 
                            text=f"Pedido #{self.pedido['id']} - {self.pedido['proveedor']}", 
                            font=('Arial', 12))
        info_label.pack(pady=(0, 20))
        
        # Campos básicos
        basic_frame = tk.Frame(main_frame)
        basic_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(basic_frame, text="Packing List PDF *", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=5)
        pdf_frame = tk.Frame(basic_frame)
        pdf_frame.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W+tk.E)
        self.packing_pdf = tk.Entry(pdf_frame, width=30)
        self.packing_pdf.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(pdf_frame, text="Buscar...", 
                 command=self.buscar_pdf).pack(side=tk.RIGHT, padx=(5, 0))
        
        tk.Label(basic_frame, text="Dirección de Envío *", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.direccion = tk.Text(basic_frame, width=40, height=3)
        self.direccion.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(basic_frame, text="Número de Bultos *", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=5)
        self.num_bultos = tk.Spinbox(basic_frame, from_=1, to=50, width=38)
        self.num_bultos.grid(row=2, column=1, padx=10, pady=5)
        
        # Gestión de bultos
        bultos_frame = tk.LabelFrame(main_frame, text="Configuración de Bultos", 
                                   font=('Arial', 12, 'bold'))
        bultos_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        btn_frame = tk.Frame(bultos_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="Configurar Bultos", 
                 command=self.configurar_bultos).pack(side=tk.LEFT)
        
        # Lista de bultos configurados
        self.bultos_listbox = tk.Listbox(bultos_frame, height=8)
        self.bultos_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Botones
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        tk.Button(buttons_frame, text="Cancelar", 
                 command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(buttons_frame, text="Crear", 
                 command=self.crear).pack(side=tk.RIGHT, padx=5)

    def buscar_pdf(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar Packing List PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.packing_pdf.delete(0, tk.END)
            self.packing_pdf.insert(0, filename)

    def configurar_bultos(self):
        try:
            num_bultos = int(self.num_bultos.get())
            if num_bultos <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Número de bultos debe ser un número positivo")
            return
        
        ConfigurarBultosWindow(self.window, self.pedido['piezas'], num_bultos, self.actualizar_bultos)

    def actualizar_bultos(self, bultos_config):
        self.bultos = bultos_config
        self.bultos_listbox.delete(0, tk.END)
        for i, bulto in enumerate(self.bultos, 1):
            self.bultos_listbox.insert(tk.END, f"Bulto {i}: {len(bulto)} piezas")

    def crear(self):
        if not all([self.packing_pdf.get(), self.direccion.get("1.0", tk.END).strip(), 
                   self.num_bultos.get()]):
            messagebox.showerror("Error", "Todos los campos marcados con * son obligatorios")
            return
        
        if not self.bultos:
            messagebox.showerror("Error", "Debe configurar los bultos")
            return
        
        packing_data = {
            'packing_pdf': self.packing_pdf.get(),
            'direccion_envio': self.direccion.get("1.0", tk.END).strip(),
            'num_bultos': int(self.num_bultos.get()),
            'bultos': self.bultos
        }
        
        self.callback(self.pedido['id'], packing_data)
        self.window.destroy()


class ConfigurarBultosWindow:
    def __init__(self, parent, piezas, num_bultos, callback):
        self.piezas = piezas
        self.num_bultos = num_bultos
        self.callback = callback
        self.bultos_config = [[] for _ in range(num_bultos)]
        
        self.window = tk.Toplevel(parent)
        self.window.title("Configurar Bultos")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(main_frame, text="Asignar Piezas a Bultos", 
                             font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Frame para la lista de piezas
        piezas_frame = tk.LabelFrame(main_frame, text="Piezas Disponibles")
        piezas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.piezas_listbox = tk.Listbox(piezas_frame, selectmode=tk.MULTIPLE)
        self.piezas_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        for pieza in self.piezas:
            self.piezas_listbox.insert(tk.END, f"{pieza['referencia']} - {pieza['descripcion']}")
        
        # Frame para bultos
        bultos_frame = tk.LabelFrame(main_frame, text="Bultos")
        bultos_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Botones de bultos
        for i in range(self.num_bultos):
            btn = tk.Button(bultos_frame, text=f"Asignar a Bulto {i+1}", 
                           command=lambda x=i: self.asignar_a_bulto(x))
            btn.pack(fill=tk.X, padx=5, pady=2)
        
        # Botones finales
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        tk.Button(buttons_frame, text="Cancelar", 
                 command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(buttons_frame, text="Confirmar", 
                 command=self.confirmar).pack(side=tk.RIGHT, padx=5)

    def asignar_a_bulto(self, bulto_idx):
        seleccionadas = self.piezas_listbox.curselection()
        if not seleccionadas:
            messagebox.showwarning("Advertencia", "Seleccione al menos una pieza")
            return
        
        for idx in reversed(seleccionadas):
            pieza = self.piezas[idx]
            self.bultos_config[bulto_idx].append(pieza)
            self.piezas_listbox.delete(idx)
            del self.piezas[idx]
        
        messagebox.showinfo("Éxito", f"Piezas asignadas al Bulto {bulto_idx + 1}")

    def confirmar(self):
        if self.piezas:  # Si quedan piezas sin asignar
            if not messagebox.askyesno("Confirmar", "Hay piezas sin asignar. ¿Continuar?"):
                return
        
        self.callback(self.bultos_config)
        self.window.destroy()


class LanzarTarWindow:
    def __init__(self, parent, pedido, callback):
        self.pedido = pedido
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Lanzar TAR")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(main_frame, text="Lanzar TAR", 
                             font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Información del pedido
        info_label = tk.Label(main_frame, 
                            text=f"Pedido #{self.pedido['id']} - {self.pedido['proveedor']}", 
                            font=('Arial', 12))
        info_label.pack(pady=(0, 20))
        
        # Campos
        tk.Label(main_frame, text="Número de TAR *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        self.numero_tar = tk.Entry(main_frame, width=40)
        self.numero_tar.pack(pady=5)
        
        tk.Label(main_frame, text="Email Logística *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        self.email_logistica = tk.Entry(main_frame, width=40)
        self.email_logistica.pack(pady=5)
        
        tk.Label(main_frame, text="Fecha *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        self.fecha = tk.Entry(main_frame, width=40)
        self.fecha.pack(pady=5)
        self.fecha.insert(0, date.today().strftime("%d/%m/%Y"))
        
        tk.Label(main_frame, text="URL Resguardo Google Forms *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        self.url_resguardo = tk.Entry(main_frame, width=40)
        self.url_resguardo.pack(pady=5)
        
        # Botones
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        tk.Button(buttons_frame, text="Cancelar", 
                 command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(buttons_frame, text="Lanzar", 
                 command=self.lanzar).pack(side=tk.RIGHT, padx=5)

    def lanzar(self):
        if not all([self.numero_tar.get(), self.email_logistica.get(), 
                   self.fecha.get(), self.url_resguardo.get()]):
            messagebox.showerror("Error", "Todos los campos marcados con * son obligatorios")
            return
        
        tar_data = {
            'numero_tar': self.numero_tar.get(),
            'email_logistica': self.email_logistica.get(),
            'fecha': self.fecha.get(),
            'url_resguardo': self.url_resguardo.get()
        }
        
        self.callback(self.pedido['id'], tar_data)
        self.window.destroy()


class EnviarEtiquetasWindow:
    def __init__(self, parent, pedido, callback):
        self.pedido = pedido
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Enviar Etiquetas")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(main_frame, text="Enviar Etiquetas", 
                             font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Información del pedido
        info_label = tk.Label(main_frame, 
                            text=f"Pedido #{self.pedido['id']} - {self.pedido['proveedor']}", 
                            font=('Arial', 12))
        info_label.pack(pady=(0, 20))
        
        # Campos
        tk.Label(main_frame, text="Etiquetas PDF *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        pdf_frame = tk.Frame(main_frame)
        pdf_frame.pack(fill=tk.X, pady=5)
        self.etiquetas_pdf = tk.Entry(pdf_frame, width=35)
        self.etiquetas_pdf.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(pdf_frame, text="Buscar...", 
                 command=self.buscar_pdf).pack(side=tk.RIGHT, padx=(5, 0))
        
        tk.Label(main_frame, text="Fecha *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        self.fecha = tk.Entry(main_frame, width=40)
        self.fecha.pack(pady=5)
        self.fecha.insert(0, date.today().strftime("%d/%m/%Y"))
        
        tk.Label(main_frame, text="Tracking Number *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        self.tracking_number = tk.Entry(main_frame, width=40)
        self.tracking_number.pack(pady=5)
        
        # Botones
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        tk.Button(buttons_frame, text="Cancelar", 
                 command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(buttons_frame, text="Enviar", 
                 command=self.enviar).pack(side=tk.RIGHT, padx=5)

    def buscar_pdf(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar Etiquetas PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.etiquetas_pdf.delete(0, tk.END)
            self.etiquetas_pdf.insert(0, filename)

    def enviar(self):
        if not all([self.etiquetas_pdf.get(), self.fecha.get(), 
                   self.tracking_number.get()]):
            messagebox.showerror("Error", "Todos los campos marcados con * son obligatorios")
            return
        
        etiquetas_data = {
            'etiquetas_pdf': self.etiquetas_pdf.get(),
            'fecha': self.fecha.get(),
            'tracking_number': self.tracking_number.get()
        }
        
        self.callback(self.pedido['id'], etiquetas_data)
        self.window.destroy()


def main():
    root = tk.Tk()
    app = GestorPedidosGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

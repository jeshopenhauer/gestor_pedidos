from datetime import datetime
from typing import Optional


class ReferenciaPieza:
    def __init__(self, codigo: str, descripcion: str, cantidad: int, proyecto: str):
        self.codigo = codigo
        self.descripcion = descripcion
        self.cantidad = cantidad
        self.proyecto = proyecto


class Oferta:
    def __init__(
        self,
        numero_oferta: str,
        empresa: str,
        quotation_pdf: str,  # ruta o URL al PDF
        email_comercial: str,
        fecha_oferta: Optional[datetime] = None
    ):
        from datetime import datetime
        self.numero_oferta = numero_oferta
        self.empresa = empresa
        self.quotation_pdf = quotation_pdf
        self.email_comercial = email_comercial
        self.fecha_oferta = fecha_oferta or datetime.now()


class PedidoStatus:
    RECEPCION_OFERTA = "Oferta recibida"
    PEDIDO_TRAMITACION_EPROC_BORRADOR = "Pedido en borrador"
    PEDIDO_TRAMITACION_EPROC_ENVIADO_NO_FIRMADO = "Pedido en plataforma (no firmado)"
    PEDIDO_TRAMITACION_EPROC_ENVIADO_FIRMADO = "Pedido en plataforma (firmado)"
    TAR_LANZADO_NO_ETIQUETAS = "Formulario de recogida rellenado y logistica no ha dado las etiquetas"
    ETIQUETAS_RECIVIDAS = "Formulario de recogida rellenado y logistica ha dado las etiquetas"
    ETIQUETAS_ENVIADAS = "Etiquetas enviadas al proveedor y seguimiento"
    PAQUETE_RECOGIDO = "Paquete recogido al proveedor"
    PAQUETE_EN_CAMINO = "Paquete en camino a nuestra oficina"
    PAQUETE_EN_CASA = "Paquete en el almacen"
    PAQUETE_EN_CASA_Y_RECOGIDO = "Paquete en el almacen y recogido"
    COMPLETADO = "Completado"
 
    @classmethod
    def estados_ordenados(cls):
        return [
            cls.RECEPCION_OFERTA,
            cls.PEDIDO_TRAMITACION_EPROC_BORRADOR,
            cls.PEDIDO_TRAMITACION_EPROC_ENVIADO_NO_FIRMADO,
            cls.PEDIDO_TRAMITACION_EPROC_ENVIADO_FIRMADO,
            cls.TAR_LANZADO_NO_ETIQUETAS,
            cls.ETIQUETAS_RECIVIDAS,
            cls.ETIQUETAS_ENVIADAS,
            cls.PAQUETE_RECOGIDO,
            cls.PAQUETE_EN_CAMINO,
            cls.PAQUETE_EN_CASA,
            cls.PAQUETE_EN_CASA_Y_RECOGIDO,
            cls.COMPLETADO,
        ]

    @classmethod
    def avanzar_estado(cls, estado_actual):
        estados = cls.estados_ordenados()
        try:
            idx = estados.index(estado_actual)
            if idx < len(estados) - 1:
                return estados[idx + 1]
            return estado_actual
        except ValueError:
            return estados[0]

    @classmethod
    def retroceder_estado(cls, estado_actual):
        estados = cls.estados_ordenados()
        try:
            idx = estados.index(estado_actual)
            if idx > 0:
                return estados[idx - 1]
            return estado_actual
        except ValueError:
            return estados[0]
            
    @classmethod
    def get_porcentaje_progreso(cls, estado_actual):
        """Calcula el porcentaje de progreso del pedido"""
        estados = cls.estados_ordenados()
        try:
            idx = estados.index(estado_actual)
            return int((idx / (len(estados) - 1)) * 100)
        except ValueError:
            return 0


class Eproc:
    def __init__(
        self,
        numero_oferta: str,
        requisition_id: str = "",
        oi: int = 0,
        numero_pedido: str = "",
        proveedor: str = "",
        referencias: list = None,
        status: PedidoStatus = None,
        fecha_eproc_borrador: Optional[datetime] = None,
        fecha_eproc_firmado: Optional[datetime] = None,
        po_pdf: str = "",
        numero_po: str = "",
        etiquetas_pdf: str = "",
        numero_bultos: int = 0,
        peso_total: float = 0.0,
        dimensiones: str = "",
        tracking_number: str = "",
    ):
        from datetime import datetime
        self.numero_oferta = numero_oferta
        self.requisition_id = requisition_id
        self.oi = oi
        self.numero_pedido = numero_pedido
        self.proveedor = proveedor
        self.referencias = referencias or []
        self.status = status if status is not None else PedidoStatus.RECEPCION_OFERTA
        self.historial = []
        self.fecha_creacion = datetime.now()
        self.fecha_eproc_borrador = fecha_eproc_borrador
        self.fecha_eproc_firmado = fecha_eproc_firmado
        self.po_pdf = po_pdf
        self.numero_po = numero_po
        self.etiquetas_pdf = etiquetas_pdf
        self.numero_bultos = numero_bultos
        self.peso_total = peso_total
        self.dimensiones = dimensiones
        self.tracking_number = tracking_number
        # Datos adicionales para etapas 3 y 4:
        self.fecha_recogida = None  # datetime
        
        # Agregar entrada inicial al historial
        self.historial.append({
            'estado': self.status,
            'fecha': self.fecha_creacion,
            'comentario': 'Pedido creado'
        })
    
    def avanzar_estado(self, comentario=""):
        """Avanza al siguiente estado en el flujo"""
        nuevo_estado = PedidoStatus.avanzar_estado(self.status)
        if nuevo_estado != self.status:
            self.status = nuevo_estado
            self.historial.append({
                'estado': nuevo_estado,
                'fecha': datetime.now(),
                'comentario': comentario or f'Avanzado a {nuevo_estado}'
            })
            return True
        return False
    
    def retroceder_estado(self, comentario=""):
        """Retrocede al estado anterior en el flujo"""
        estado_anterior = PedidoStatus.retroceder_estado(self.status)
        if estado_anterior != self.status:
            self.status = estado_anterior
            self.historial.append({
                'estado': estado_anterior,
                'fecha': datetime.now(),
                'comentario': comentario or f'Retrocedido a {estado_anterior}'
            })
            return True
        return False
    
    def get_porcentaje_progreso(self):
        """Obtiene el porcentaje de progreso del pedido"""
        return PedidoStatus.get_porcentaje_progreso(self.status)
    
    def get_posicion_estado(self):
        """Obtiene la posición actual en el flujo (empezando en 1)"""
        estados = PedidoStatus.estados_ordenados()
        try:
            return estados.index(self.status) + 1
        except ValueError:
            return 1
    
    def get_total_estados(self):
        """Obtiene el total de estados en el flujo"""
        return len(PedidoStatus.estados_ordenados())
    
    def puede_avanzar_estado(self):
        """Verifica si el pedido puede avanzar al siguiente estado"""
        if self.status == PedidoStatus.RECEPCION_OFERTA:
            return True  # Siempre puede avanzar de oferta a borrador
        elif self.status == PedidoStatus.PEDIDO_TRAMITACION_EPROC_BORRADOR:
            # Para avanzar de borrador a enviado, necesita requisition_id y oi
            return bool(self.requisition_id.strip() and self.oi > 0)
        elif self.status == PedidoStatus.PEDIDO_TRAMITACION_EPROC_ENVIADO_NO_FIRMADO:
            return True  # Puede avanzar a firmado sin campos adicionales
        elif self.status == PedidoStatus.PEDIDO_TRAMITACION_EPROC_ENVIADO_FIRMADO:
            # Para avanzar de firmado, necesita po_pdf y numero_pedido
            return bool(self.po_pdf.strip() and self.numero_pedido.strip())
        elif self.status == PedidoStatus.TAR_LANZADO_NO_ETIQUETAS:
            return True  # Puede avanzar a etiquetas recibidas
        elif self.status == PedidoStatus.ETIQUETAS_RECIVIDAS:
            # Para avanzar después de etiquetas, necesita datos del paquete
            return bool(self.etiquetas_pdf.strip() and self.numero_bultos > 0 and 
                       self.peso_total > 0 and self.dimensiones.strip())
        else:
            return True  # Para otros estados, puede avanzar libremente
    
    def get_campos_requeridos(self):
        """Devuelve los campos requeridos para el estado actual"""
        if self.status == PedidoStatus.PEDIDO_TRAMITACION_EPROC_BORRADOR:
            return ["requisition_id", "oi"]
        elif self.status == PedidoStatus.PEDIDO_TRAMITACION_EPROC_ENVIADO_FIRMADO:
            return ["po_pdf", "numero_pedido"]
        elif self.status == PedidoStatus.ETIQUETAS_RECIVIDAS:
            return ["etiquetas_pdf", "numero_bultos", "peso_total", "dimensiones"]
        else:
            return []


class Etiquetas:
    def __init__(
        self,
        numero_bultos: int,
        peso_total: float,
        dimensiones: str,  # Formato: "Largo x Ancho x Alto"
        declared_value: float,
        tracking_number: str,
        direccion_recogida: str,
        direccion_entrega: str,
        fecha_recogida: Optional[datetime] = None,
        fecha_entrega: Optional[datetime] = None,
    ):
        from datetime import datetime
        self.numero_bultos = numero_bultos
        self.peso_total = peso_total
        self.dimensiones = dimensiones
        self.declared_value = declared_value
        self.tracking_number = tracking_number
        self.direccion_recogida = direccion_recogida
        self.direccion_entrega = direccion_entrega
        self.fecha_recogida = fecha_recogida
        self.fecha_entrega = fecha_entrega





   

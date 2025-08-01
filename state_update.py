class PedidoStatus:
    # Los estados del pedido en orden
    RECEPCION_OFERTA = "Oferta recibida"
    PEDIDO_BORRADOR = "Pedido en borrador"
    PEDIDO_ENVIADO = "Pedido enviado"
    PEDIDO_FIRMADO = "Pedido firmado"
    ETIQUETAS_SOLICITADAS = "Etiquetas solicitadas"
    ETIQUETAS_RECIBIDAS = "Etiquetas recibidas"
    PAQUETE_RECOGIDO = "Paquete recogido"
    PAQUETE_EN_CAMINO = "Paquete en camino"
    PAQUETE_ENTREGADO = "Paquete entregado"
    COMPLETADO = "Completado"

    # Lista de todos los estados en orden
    TODOS_LOS_ESTADOS = [
        RECEPCION_OFERTA,
        PEDIDO_BORRADOR,
        PEDIDO_ENVIADO,
        PEDIDO_FIRMADO,
        ETIQUETAS_SOLICITADAS,
        ETIQUETAS_RECIBIDAS,
        PAQUETE_RECOGIDO,
        PAQUETE_EN_CAMINO,
        PAQUETE_ENTREGADO,
        COMPLETADO
    ]

    @classmethod
    def siguiente_estado(cls, estado_actual):
        """Devuelve el siguiente estado"""
        try:
            posicion = cls.TODOS_LOS_ESTADOS.index(estado_actual)
            if posicion < len(cls.TODOS_LOS_ESTADOS) - 1:
                return cls.TODOS_LOS_ESTADOS[posicion + 1]
            else:
                return estado_actual  # Ya es el último
        except:
            return cls.RECEPCION_OFERTA  # Si hay error, empezar desde el principio

    @classmethod
    def estado_anterior(cls, estado_actual):
        """Devuelve el estado anterior"""
        try:
            posicion = cls.TODOS_LOS_ESTADOS.index(estado_actual)
            if posicion > 0:
                return cls.TODOS_LOS_ESTADOS[posicion - 1]
            else:
                return estado_actual  # Ya es el primero
        except:
            return cls.RECEPCION_OFERTA  # Si hay error, empezar desde el principio


class Pedido:
    """Clase simple para manejar un pedido"""
    
    def __init__(self, numero, proveedor):
        self.numero = numero
        self.proveedor = proveedor
        self.estado = PedidoStatus.RECEPCION_OFERTA  # Siempre empieza aquí
        print(f"✅ Pedido {numero} creado para {proveedor}")
        print(f"   Estado inicial: {self.estado}")
    
    def avanzar(self):
        """Avanza al siguiente estado"""
        estado_anterior = self.estado
        self.estado = PedidoStatus.siguiente_estado(self.estado)
        
        if self.estado != estado_anterior:
            print(f"⬆️  Pedido {self.numero} avanzó:")
            print(f"   De: {estado_anterior}")
            print(f"   A:  {self.estado}")
        else:
            print(f"🏁 Pedido {self.numero} ya está en el estado final: {self.estado}")
    
    def retroceder(self):
        """Retrocede al estado anterior"""
        estado_anterior = self.estado
        self.estado = PedidoStatus.estado_anterior(self.estado)
        
        if self.estado != estado_anterior:
            print(f"⬇️  Pedido {self.numero} retrocedió:")
            print(f"   De: {estado_anterior}")
            print(f"   A:  {self.estado}")
        else:
            print(f"🚩 Pedido {self.numero} ya está en el primer estado: {self.estado}")
    
    def mostrar_info(self):
        """Muestra información del pedido"""
        print(f"\n📋 INFORMACIÓN DEL PEDIDO:")
        print(f"   Número: {self.numero}")
        print(f"   Proveedor: {self.proveedor}")
        print(f"   Estado actual: {self.estado}")


# Función simple para probar
def crear_pedido_seso():
    """Crea un pedido de SESO.SL y lo prueba"""
    print("� CREANDO PEDIDO DE SESO.SL")
    print("=" * 40)
    
    # Crear pedido
    pedido = Pedido("PED-001", "SESO.SL")
    
    # Mostrar información
    pedido.mostrar_info()
    
    print(f"\n🔄 PROBANDO NAVEGACIÓN:")
    print("Presiona ENTER para avanzar estado...")
    
    # Avanzar algunos estados
    for i in range(3):
        input()  # Esperar ENTER
        pedido.avanzar()
    
    print(f"\nProbando retroceder...")
    input()  # Esperar ENTER
    pedido.retroceder()
    
    pedido.mostrar_info()
    
    return pedido


if __name__ == "__main__":
    # Ejecutar cuando se corra el archivo
    crear_pedido_seso()

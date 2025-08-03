# main.py
from datetime import date


class Pieza:
    def __init__(self, referencia: str, descripcion: str, proyecto: str):
        self.referencia = referencia
        self.descripcion = descripcion
        self.proyecto = proyecto

    def __str__(self):
        return f"Pieza: {self.referencia} - {self.descripcion} (Proyecto: {self.proyecto})"


class ItemOferta:
    """Representa una pieza específica dentro de una oferta con su precio"""
    def __init__(self, pieza: Pieza, precio_unitario: float, cantidad: int = 1):
        self.pieza = pieza
        self.precio_unitario = precio_unitario
        self.cantidad = cantidad

    @property
    def precio_total_item(self) -> float:
        return self.precio_unitario * self.cantidad
    

class Oferta:
    def __init__(self, numero_oferta: str, proveedor: str, fecha_oferta: str = None, email_proveedor: str = None, oferta_pdf: str = None):
        from datetime import date  # Importación local para evitar problemas
        self.estado_oferta = "Oferta recibida"
        self.numero_oferta = numero_oferta
        self.proveedor = proveedor
        self.fecha_oferta = fecha_oferta if fecha_oferta is not None else date.today().isoformat()
        self.email_proveedor = email_proveedor
        self.oferta_pdf = oferta_pdf
        self.items = []  # Lista de ItemOferta

    def agregar_pieza(self, pieza: Pieza, precio_unitario: float, cantidad: int = 1):
        item = ItemOferta(pieza, precio_unitario, cantidad)
        self.items.append(item)
        print(f"Pieza {pieza.referencia} agregada a la oferta {self.numero_oferta} con precio unitario €{precio_unitario:.2f} y cantidad {cantidad}")

    def eliminar_pieza(self, pieza: Pieza):
        self.items = [item for item in self.items if item.pieza.referencia != pieza.referencia]
        print(f"Pieza {pieza.referencia} eliminada de la oferta {self.numero_oferta}")

    def modificar_cantidad(self, pieza: Pieza, nueva_cantidad: int):
        for item in self.items:
            if item.pieza.referencia == pieza.referencia:
                item.cantidad = nueva_cantidad
                break    

    def modificar_precio(self, pieza: Pieza, nuevo_precio_unitario: float):
        for item in self.items:
            if item.pieza.referencia == pieza.referencia:
                item.precio_unitario = nuevo_precio_unitario
                break


    def mostrar_oferta(self):
        print(f"Oferta {self.numero_oferta} de {self.proveedor} - Fecha: {self.fecha_oferta}")
        for item in self.items:
            print(f"{item.pieza.referencia}: {item.pieza.descripcion} - "
                  f"Precio unitario: €{item.precio_unitario:.2f}, "
                  f"Cantidad: {item.cantidad}, "
                  f"Total: €{item.precio_total_item:.2f}")
        print(f"Total oferta: €{self.precio_total_oferta:.2f}")

    @property
    def precio_total_oferta(self) -> float:
        return sum(item.precio_total_item for item in self.items)

    def __str__(self):
       return f"Oferta {self.numero_oferta} de {self.proveedor}"

# cuando se termina de crear una oferta, se procede a crear una solicitud de pedido, que llamaremos Eproc
# oi es el numero de cuenta de mi empresa, que le compra al proveedor
# proveedor es el nombre del proveedor, y oferta_pdf es el pdf de la oferta que me han enviado



class Eproc(Oferta):
    def __init__(self, numero_oferta: str, proveedor: str, oi: float = None , eproc_number: str = None, oferta_pdf: str = None):
        super().__init__(numero_oferta, proveedor, oferta_pdf)
        self.oi = oi
        self.eproc_number = eproc_number
        self.estado_eproc = "Borrador"
        self.po_number = None
        self.po_pdf = None

    @property
    def estado_actual(self):
        """Devuelve el estado actual del proceso completo"""
        return self.estado_eproc

    def avanzar_estado(self):
        """Avanza al siguiente estado del pedido"""
        estados = ["Borrador", "Enviado_no_firmado", "Enviado_firmado"]
        if self.estado_eproc in estados:
            indice_actual = estados.index(self.estado_eproc)
            if indice_actual < len(estados) - 1:
                if self.estado_eproc == "Borrador":
                    if not self._puede_enviar():
                        return False
                self.estado_eproc = estados[indice_actual + 1]
                print(f"Estado cambiado a: {self.estado_eproc}")
                return True
        return print("Ya esta firmado el Eproc, no hay mas estados a avanzar")

    def _puede_enviar(self):
        """Verifica si se puede pasar de Borrador a Enviado_no_firmado"""
        errores = []
        if self.oi is None or self.oi == "":
            errores.append("- OI (Número de cuenta) es obligatorio")
        if self.eproc_number is None or self.eproc_number == "":
            errores.append("- Número de Eproc es obligatorio")
        if errores:
            print("❌ No se puede enviar el Eproc. Faltan campos obligatorios:")
            for error in errores:
                print(error)
            return False
        print("✅ Validación exitosa. Todos los campos obligatorios están completos.")
        return True

    def validar_campos_obligatorios(self):
        """Método público para verificar qué campos faltan"""
        if self.estado_eproc == "Borrador":
            return self._puede_enviar()
        return True

    def retroceder_estado(self):
        """Retrocede al estado anterior del pedido"""
        estados = ["Borrador", "Enviado_no_firmado", "Enviado_firmado"]
        if self.estado_eproc in estados:
            indice_actual = estados.index(self.estado_eproc)
            if indice_actual > 0:
                self.estado_eproc = estados[indice_actual - 1]
                print(f"Estado cambiado a: {self.estado_eproc}")

    def ingresar_po(self):
        """Ingresa el número de PO y el archivo po.pdf"""
        # Aquí deberías pedir o asignar el número de PO y el PDF
        self.po_number = input("Introduce el número de PO: ")
        self.po_pdf = input("Introduce la ruta al archivo po.pdf: ")
        print(f"PO generado: {self.po_number}, archivo: {self.po_pdf}")



# Ahora que la solicitud de pedido (Eproc) está creada, podemos avanzar en el flujo de trabajo
# El siguiente paso es enviar un TAR a logistica, para que nos envien las etiquetas que tenemos que 
# dar al proveedor para que nos envien las piezas

class Bulto(Pieza):
    def __init__(self, referencia: str, descripcion: str, proyecto: str):
        super().__init__(referencia, descripcion, proyecto)
        self.piezas = []  # Lista de piezas dentro del bulto

    def agregar_pieza(self, pieza: Pieza):
        """Agrega una pieza al bulto."""
        self.piezas.append(pieza)
        print(f"Pieza {pieza.referencia} agregada al bulto {self.referencia}.")

    def eliminar_pieza(self, pieza: Pieza):
        """Elimina una pieza del bulto."""
        self.piezas = [p for p in self.piezas if p.referencia != pieza.referencia]
        print(f"Pieza {pieza.referencia} eliminada del bulto {self.referencia}.")



    def listar_piezas(self):
        """Lista todas las piezas dentro del bulto."""
        if self.piezas:
            print(f"Bulto {self.referencia} contiene las siguientes piezas:")
            for pieza in self.piezas:
                print(f"  - {pieza.referencia}: {pieza.descripcion}")
        else:
            print(f"Bulto {self.referencia} no contiene piezas.")

    
#un paquete es un conjunto de bultos que se envian al proveedor, y que tienen un packing list
class Paquete:
    def __init__(self, numero_paquete: str, bultos: list, packing_list_pdf: str):
        self.numero_paquete = numero_paquete
        self.bultos = bultos  # Lista de objetos Bulto
        self.packing_list_pdf = packing_list_pdf
    
    def agregar_bulto(self, bulto: Bulto):
        """Agrega un bulto al paquete."""
        self.bultos.append(bulto)
        print(f"Bulto {bulto.referencia} agregado al paquete {self.numero_paquete}.")

    def mostrar_informacion(self):
        """Muestra la información del paquete y sus bultos."""
        print(f"Paquete {self.numero_paquete} contiene los siguientes bultos:")
        for bulto in self.bultos:
            print(f"  - {bulto.referencia}: {bulto.descripcion}")


    # un TAR es un formulario que se envía a logística para que nos envíen las etiquetas de envío
    # un TAR contiene un número de po,oi,packing list, direccion de envio y mostrar_informacion del paquete

class Tar:
    def __init__(self, numero_tar: str, fecha_lanzamiento_tar: str, eproc: Eproc, 
                 paquetes: list, persona_contacto: str, persona_logistica: str, 
                 direccion_envio: str):
        # Validación: el Eproc debe tener PO y estar firmado
        if not eproc.po_number or not eproc.po_pdf:
            raise ValueError("❌ No se puede crear el TAR: El Eproc debe tener número de PO y archivo po.pdf")
        if eproc.estado_eproc != "Enviado_firmado":
            raise ValueError("❌ No se puede crear el TAR: El Eproc debe estar en estado 'Enviado_firmado'")
        
        self.numero_tar = numero_tar
        self.fecha_lanzamiento_tar = fecha_lanzamiento_tar  
        self.oi = str(eproc.oi)
        self.po_number = eproc.po_number
        self.eproc = eproc  # Referencia al Eproc
        self.paquetes = paquetes  # Lista de objetos Paquete
        self.persona_contacto = persona_contacto
        self.persona_logistica = persona_logistica
        self.direccion_envio = direccion_envio
        self.estado_tar = "Enviado"

    def mostrar_informacion(self):
        """Muestra la información del TAR."""
        print("=" * 50)
        print("INFORMACIÓN DEL TAR")
        print("=" * 50)
        print(f"TAR: {self.numero_tar} - Estado: {self.estado_tar}")
        print(f"OI: {self.oi} | PO: {self.po_number}")
        print(f"Persona de contacto: {self.persona_contacto}")
        print(f"Persona de logística: {self.persona_logistica}")
        print(f"Dirección de envío: {self.direccion_envio}")
        print(f"Fecha de lanzamiento: {self.fecha_lanzamiento_tar}")
        
        print("\n--- PAQUETES INCLUIDOS ---")
        for i, paquete in enumerate(self.paquetes, 1):
            print(f"\nPaquete {i}: {paquete.numero_paquete}")
            print(f"Packing List PDF: {paquete.packing_list_pdf}")
            print("Bultos contenidos:")
            for bulto in paquete.bultos:
                print(f"  • {bulto.referencia}: {bulto.descripcion}")
                for pieza in bulto.piezas:
                    print(f"    - {pieza.referencia}: {pieza.descripcion}")

    def obtener_todos_los_bultos(self):
        """Devuelve una lista con todos los bultos de todos los paquetes"""
        todos_los_bultos = []
        for paquete in self.paquetes:
            todos_los_bultos.extend(paquete.bultos)
        return todos_los_bultos

    def contar_bultos_total(self):
        """Cuenta el total de bultos en el TAR"""
        return sum(len(paquete.bultos) for paquete in self.paquetes)

    def contar_piezas_total(self):
        """Cuenta el total de piezas en el TAR"""
        total_piezas = 0
        for paquete in self.paquetes:
            for bulto in paquete.bultos:
                total_piezas += len(bulto.piezas)
        return total_piezas

    def mostrar_resumen(self):
        """Muestra un resumen del TAR"""
        print(f"\n📋 RESUMEN TAR {self.numero_tar}")
        print(f"   • {len(self.paquetes)} paquete(s)")
        print(f"   • {self.contar_bultos_total()} bulto(s) total")
        print(f"   • {self.contar_piezas_total()} pieza(s) total")
        print(f"   • Estado: {self.estado_tar}")
        

# Cuando el tar se lanza, logistica nos da las etiquetas y nosotros se las enviamos al proveedor
#cad bulto tiene una etiqueta, con un codigo del pdf de las etiquetas que nos pasan
class Etiqueta(Oferta):
    def __init__(self, codigo: str, bulto: Bulto):
        self.codigo = codigo
        self.bulto = bulto
        self.estado_etiqueta = "recibida"

    def mostrar_informacion(self):
        """Muestra la información de la etiqueta."""
        print(f"Etiqueta - Código: {self.codigo}")
        print(f"Bulto asociado: {self.bulto.referencia}")


    def enviar_etiqueta(self, oferta: Oferta):
        """Simula el envío de la etiqueta al proveedor usando el email de la oferta."""
        email_proveedor = getattr(oferta, "email_proveedor", None)
        if not email_proveedor:
            print("No se ha especificado el email del proveedor en la oferta.")
            return
        print(f"Enviando etiqueta {self.codigo} al proveedor {email_proveedor}...")
        self.estado_etiqueta = "enviada"
        print(f"Etiqueta {self.codigo} enviada al proveedor {email_proveedor}.")
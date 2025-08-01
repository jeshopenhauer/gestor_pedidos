class Guerrero:
    def __init__(self, nombre, nivel:int=1):
        self.nombre = nombre
        self.nivel = nivel  

    def subir_nivel(self):
        if self.nivel < 10:
            self.nivel += 1
            print(f"{self.nombre} ha subido al nivel {self.nivel}!")
        else:
            print(f"{self.nombre} ya está en el nivel máximo (10).")

class Ejercito:
    def __init__(self):
        self.guerreros = []  # Lista para almacenar los objetos Guerrero

    def agregar_guerrero(self, guerrero):
        self.guerreros.append(guerrero)
        print(f"Guerrero {guerrero.nombre} agregado al ejército.")

    def mostrar_ejercito(self):
        print("Ejército compuesto por:")
        for guerrero in self.guerreros:
            print(f"- {guerrero.nombre} (Nivel {guerrero.nivel})")

# Ejemplo de uso
g1 = Guerrero("Aragorn", 5)
g2 = Guerrero("Legolas", 7)

losbuenos = Ejercito()
losbuenos.agregar_guerrero(g1)
losbuenos.agregar_guerrero(g2)

losbuenos.mostrar_ejercito()
# Salida:
# Guerrero Aragorn agregado al ejército.
# Guerrero Legolas agregado al ejército.
# Ejército compuesto por:
# - Aragorn (Nivel 5)
# - Legolas (Nivel 7)
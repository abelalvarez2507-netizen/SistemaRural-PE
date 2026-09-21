class Persona:
    def __init__(self, nombre, edad): self.nombre, self.edad = nombre, edad
    def mostrar_informacion(self): return f"Nombre: {self.nombre} | Edad: {self.edad}"

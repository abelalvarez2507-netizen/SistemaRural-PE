from servicios.validaciones import edad_valida, texto_requerido


class Persona:
    def __init__(self, nombre, edad):
        self.nombre = texto_requerido(nombre, "El nombre")
        self.edad = edad_valida(edad)

    def mostrar_informacion(self):
        return f"Nombre: {self.nombre} | Edad: {self.edad}"

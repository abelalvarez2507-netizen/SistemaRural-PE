from servicios.validaciones import validar_edad, validar_nombre


class Persona:
    """Clase base para las personas que interactúan con SaluPro."""

    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = validar_nombre(valor)

    @property
    def edad(self):
        return self._edad

    @edad.setter
    def edad(self, valor):
        self._edad = validar_edad(valor)

    def mostrar_informacion(self):
        return f"Nombre: {self.nombre} | Edad: {self.edad}"

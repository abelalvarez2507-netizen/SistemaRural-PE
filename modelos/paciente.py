from modelos.persona import Persona
from servicios.validaciones import codigo_valido, dni_valido


class Paciente(Persona):
    def __init__(self, codigo, dni, nombre, edad):
        super().__init__(nombre, edad)
        self.codigo = codigo_valido(codigo, "El código del paciente")
        self.dni = dni_valido(dni)

    def mostrar_informacion(self):
        return f"Código de paciente: {self.codigo} | DNI: {self.dni} | Nombre: {self.nombre} | Edad: {self.edad}"

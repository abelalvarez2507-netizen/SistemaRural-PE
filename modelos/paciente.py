from modelos.persona import Persona
class Paciente(Persona):
    def __init__(self, codigo, dni, nombre, edad):
        super().__init__(nombre, edad); self.codigo, self.dni = codigo, dni
    def mostrar_informacion(self): return f"Código de paciente: {self.codigo} | DNI: {self.dni} | Nombre: {self.nombre} | Edad: {self.edad}"

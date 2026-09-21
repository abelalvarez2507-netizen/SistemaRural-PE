from modelos.persona import Persona
class Paciente(Persona):
    def __init__(self, codigo, nombre, edad): super().__init__(nombre, edad); self.codigo = codigo

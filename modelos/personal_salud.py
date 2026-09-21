from modelos.persona import Persona
class PersonalSalud(Persona):
    def __init__(self, codigo_profesional, nombre, edad, especialidad):
        super().__init__(nombre, edad); self.codigo_profesional = codigo_profesional; self.especialidad = especialidad

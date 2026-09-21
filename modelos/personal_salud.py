from modelos.persona import Persona
class PersonalSalud(Persona):
    def __init__(self, codigo_profesional, dni, nombre, edad, especialidad):
        super().__init__(nombre, edad); self.codigo_profesional, self.dni, self.especialidad = codigo_profesional, dni, especialidad
    def mostrar_informacion(self): return f"Código profesional: {self.codigo_profesional} | DNI: {self.dni} | Nombre: {self.nombre} | Edad: {self.edad} | Especialidad: {self.especialidad}"

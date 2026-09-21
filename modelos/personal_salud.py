from modelos.persona import Persona
from servicios.validaciones import codigo_valido, dni_valido, texto_requerido


class PersonalSalud(Persona):
    def __init__(self, codigo_profesional, dni, nombre, edad, especialidad):
        super().__init__(nombre, edad)
        self.codigo_profesional = codigo_valido(codigo_profesional, "El código profesional")
        self.dni = dni_valido(dni)
        self.especialidad = texto_requerido(especialidad, "La especialidad")

    def mostrar_informacion(self):
        return f"Código profesional: {self.codigo_profesional} | DNI: {self.dni} | Nombre: {self.nombre} | Edad: {self.edad} | Especialidad: {self.especialidad}"

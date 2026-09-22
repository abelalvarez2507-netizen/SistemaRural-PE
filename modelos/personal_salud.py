from modelos.persona import Persona
from servicios.seguridad import SeguridadDatos
from servicios.validaciones import validar_codigo, validar_dni, validar_especialidad


class PersonalSalud(Persona):
    """Entidad profesional de salud con protección del DNI."""

    def __init__(self, codigo_profesional, dni, nombre, edad, especialidad):
        super().__init__(nombre, edad)
        self._codigo_profesional = validar_codigo(
            codigo_profesional,
            "El código profesional",
        )
        self._especialidad = validar_especialidad(especialidad)
        self.dni = dni

    @classmethod
    def desde_datos_protegidos(
        cls,
        codigo_profesional,
        dni_hash,
        dni_salt,
        nombre,
        edad,
        especialidad,
    ):
        """Construye un profesional sin reconstruir el DNI original."""
        profesional = cls.__new__(cls)
        Persona.__init__(profesional, nombre, edad)
        profesional._codigo_profesional = validar_codigo(
            codigo_profesional,
            "El código profesional",
        )
        profesional._especialidad = validar_especialidad(especialidad)
        profesional._dni = None
        profesional._dni_hash = dni_hash
        profesional._dni_salt = dni_salt
        return profesional

    @property
    def codigo_profesional(self):
        return self._codigo_profesional

    @property
    def especialidad(self):
        return self._especialidad

    @property
    def dni(self):
        if self._dni is None:
            return "********"
        return self._dni

    @dni.setter
    def dni(self, valor):
        valor = validar_dni(valor)
        self._dni = valor
        self._dni_salt, self._dni_hash = SeguridadDatos.proteger(valor)

    @property
    def dni_hash(self):
        return self._dni_hash

    @property
    def dni_salt(self):
        return self._dni_salt

    @property
    def dni_mascarado(self):
        return "********"

    def verificar_dni(self, valor):
        return SeguridadDatos.verificar(valor, self.dni_salt, self.dni_hash)

    def mostrar_informacion(self):
        return (
            f"Código profesional: {self.codigo_profesional} | "
            f"DNI: {self.dni_mascarado} | "
            f"Nombre: {self.nombre} | "
            f"Edad: {self.edad} | "
            f"Especialidad: {self.especialidad}"
        )

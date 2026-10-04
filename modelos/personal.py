"""Entidad base para el personal que trabaja en el establecimiento."""

from modelos.persona import Persona
from servicios.seguridad import SeguridadDatos
from servicios.validaciones import validar_codigo, validar_dni


class Personal(Persona):
    """Datos e identidad compartidos por profesionales y enfermería."""

    def __init__(self, codigo_personal, dni, nombre, edad):
        super().__init__(nombre, edad)
        self._codigo_personal = validar_codigo(
            codigo_personal,
            "El código del personal",
        )
        self.dni = dni

    @classmethod
    def desde_datos_protegidos(
        cls,
        codigo_personal,
        dni_hash,
        dni_salt,
        nombre,
        edad,
    ):
        """Reconstruye el registro desde SQLite sin recuperar el DNI."""
        personal = cls.__new__(cls)
        Persona.__init__(personal, nombre, edad)
        personal._codigo_personal = validar_codigo(
            codigo_personal,
            "El código del personal",
        )
        personal._dni = None
        personal._dni_hash = dni_hash
        personal._dni_salt = dni_salt
        return personal

    @property
    def codigo_personal(self):
        return self._codigo_personal

    @property
    def dni(self):
        return "********" if self._dni is None else self._dni

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
            f"Código de personal: {self.codigo_personal} | "
            f"DNI: {self.dni_mascarado} | "
            f"Nombre: {self.nombre} | Edad: {self.edad}"
        )

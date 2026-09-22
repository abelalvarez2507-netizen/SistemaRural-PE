from modelos.persona import Persona
from servicios.seguridad import SeguridadDatos
from servicios.validaciones import validar_codigo, validar_dni


class Paciente(Persona):
    """Entidad paciente con protección del DNI."""

    def __init__(self, codigo, dni, nombre, edad):
        super().__init__(nombre, edad)
        self._codigo = validar_codigo(codigo, "El código del paciente")
        self.dni = dni

    @classmethod
    def desde_datos_protegidos(
        cls,
        codigo,
        dni_hash,
        dni_salt,
        nombre,
        edad,
    ):
        """Construye un paciente desde SQLite sin recuperar el DNI original."""
        paciente = cls.__new__(cls)
        Persona.__init__(paciente, nombre, edad)
        paciente._codigo = validar_codigo(codigo, "El código del paciente")
        paciente._dni = None
        paciente._dni_hash = dni_hash
        paciente._dni_salt = dni_salt
        return paciente

    @property
    def codigo(self):
        return self._codigo

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
            f"Código de paciente: {self.codigo} | "
            f"DNI: {self.dni_mascarado} | "
            f"Nombre: {self.nombre} | "
            f"Edad: {self.edad}"
        )

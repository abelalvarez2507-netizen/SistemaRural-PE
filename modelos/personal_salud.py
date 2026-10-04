from modelos.personal import Personal
from servicios.validaciones import validar_especialidad


class PersonalSalud(Personal):
    """Profesional o integrante de enfermería con una especialidad."""

    def __init__(self, codigo_profesional, dni, nombre, edad, especialidad):
        super().__init__(codigo_profesional, dni, nombre, edad)
        self._especialidad = validar_especialidad(especialidad)

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
        personal = Personal.desde_datos_protegidos.__func__(
            cls,
            codigo_profesional,
            dni_hash,
            dni_salt,
            nombre,
            edad,
        )
        personal._especialidad = validar_especialidad(especialidad)
        return personal

    @property
    def codigo_profesional(self):
        """Alias mantenido para citas y cuentas de acceso existentes."""
        return self.codigo_personal

    @property
    def especialidad(self):
        return self._especialidad

    def mostrar_informacion(self):
        return (
            f"Código profesional: {self.codigo_profesional} | "
            f"DNI: {self.dni_mascarado} | "
            f"Nombre: {self.nombre} | "
            f"Edad: {self.edad} | "
            f"Especialidad: {self.especialidad}"
        )

from modelos.personal_salud import PersonalSalud


class PersonalEnfermeria(PersonalSalud):
    """Registro de enfermería dentro de la jerarquía común de Personal."""

    def __init__(self, codigo_personal, dni, nombre, edad, especialidad="Enfermería"):
        if "enfermer" not in str(especialidad).casefold():
            raise ValueError("La especialidad del personal de enfermería debe ser Enfermería.")
        super().__init__(codigo_personal, dni, nombre, edad, especialidad)

    def mostrar_informacion(self):
        return (
            f"Código de enfermería: {self.codigo_personal} | "
            f"DNI: {self.dni_mascarado} | "
            f"Nombre: {self.nombre} | "
            f"Edad: {self.edad} | "
            f"Especialidad: {self.especialidad}"
        )

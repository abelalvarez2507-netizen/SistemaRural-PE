from modelos.paciente import Paciente
from modelos.personal_salud import PersonalSalud

class FabricaPersonas:
    """Primera incorporación de Factory, todavía sencilla y con errores de diseño."""
    def crear(self, tipo, *datos):
        if tipo == "paciente":
            return Paciente(*datos)
        elif tipo == "personal":
            return PersonalSalud(*datos)
        raise ValueError("Tipo no reconocido")

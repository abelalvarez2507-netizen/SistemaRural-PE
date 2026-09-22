from modelos.paciente import Paciente
from modelos.personal_salud import PersonalSalud


class FabricaPersonas:
    """Factory centralizada para crear los tipos de persona del sistema."""

    _tipos = {
        "paciente": Paciente,
        "personal": PersonalSalud,
    }

    def crear(self, tipo, *datos):
        clase = self._tipos.get(tipo.lower())
        if clase is None:
            raise ValueError(f"Tipo de persona no reconocido: {tipo}")
        return clase(*datos)

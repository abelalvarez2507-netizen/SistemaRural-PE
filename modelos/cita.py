from datetime import datetime

from modelos.paciente import Paciente
from modelos.personal_salud import PersonalSalud
from servicios.validaciones import (
    normalizar_fecha,
    normalizar_hora,
    validar_codigo,
    validar_motivo,
)


class Cita:
    """Representa una cita entre un paciente y un profesional."""

    ESTADOS_VALIDOS = {
        "Pendiente",
        "Atendida",
        "Reprogramada",
        "No atendida",
        "Cancelada",
    }

    def __init__(
        self,
        codigo,
        paciente,
        profesional,
        fecha,
        motivo,
        estado="Pendiente",
        hora="09:00",
    ):
        if paciente is None or not isinstance(paciente, Paciente):
            raise ValueError("La cita debe tener un paciente válido.")
        if profesional is None or not isinstance(profesional, PersonalSalud):
            raise ValueError("La cita debe tener un profesional válido.")

        self._codigo = validar_codigo(codigo, "El código de la cita")
        self._paciente = paciente
        self._profesional = profesional
        self.fecha = fecha
        self.hora = hora
        self.motivo = motivo
        self.estado = estado

    @property
    def codigo(self):
        return self._codigo

    @property
    def paciente(self):
        return self._paciente

    @property
    def profesional(self):
        return self._profesional

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, valor):
        self._fecha = normalizar_fecha(valor)

    @property
    def hora(self):
        return self._hora

    @hora.setter
    def hora(self, valor):
        self._hora = normalizar_hora(valor)

    @property
    def fecha_hora(self):
        return datetime.strptime(
            f"{self.fecha} {self.hora}",
            "%d/%m/%Y %H:%M",
        )

    @property
    def motivo(self):
        return self._motivo

    @motivo.setter
    def motivo(self, valor):
        self._motivo = validar_motivo(valor)

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, valor):
        if valor == "Reprogramar":
            valor = "Reprogramada"
        if valor not in self.ESTADOS_VALIDOS:
            raise ValueError(
                "Estado inválido. Use: Pendiente, Atendida, Reprogramada, "
                "No atendida o Cancelada."
            )
        self._estado = valor

    def mostrar_informacion(self):
        return (
            f"Cita: {self.codigo} | "
            f"Paciente: {self.paciente.nombre} | "
            f"Profesional: {self.profesional.nombre} | "
            f"Fecha: {self.fecha} | "
            f"Hora: {self.hora} | "
            f"Motivo: {self.motivo} | "
            f"Estado: {self.estado}"
        )

from modelos.cita import Cita
from servicios.validaciones import validar_codigo, validar_diagnostico


class AtencionMedica:
    """Representa la atención clínica asociada a una cita."""

    ESTADOS_VALIDOS = {"Pendiente", "En proceso", "Finalizada"}

    def __init__(self, codigo, cita, diagnostico, estado="Pendiente"):
        if cita is None or not isinstance(cita, Cita):
            raise ValueError("La atención debe estar asociada a una cita válida.")

        self._codigo = validar_codigo(codigo, "El código de atención")
        self._cita = cita
        self._diagnostico = validar_diagnostico(diagnostico)
        self.estado = estado

    @property
    def codigo(self):
        return self._codigo

    @property
    def cita(self):
        return self._cita

    @property
    def paciente(self):
        return self._cita.paciente

    @property
    def profesional(self):
        return self._cita.profesional

    @property
    def fecha(self):
        return self._cita.fecha

    @property
    def diagnostico(self):
        return self._diagnostico

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, valor):
        if valor not in self.ESTADOS_VALIDOS:
            raise ValueError(
                "Estado inválido. Use: Pendiente, En proceso o Finalizada."
            )
        self._estado = valor

    def mostrar_informacion(self):
        return (
            f"Atención: {self.codigo} | "
            f"Cita: {self.cita.codigo} | "
            f"Paciente: {self.paciente.nombre} | "
            f"Profesional: {self.profesional.nombre} | "
            f"Fecha: {self.fecha} | "
            f"Diagnóstico: {self.diagnostico} | "
            f"Estado: {self.estado}"
        )

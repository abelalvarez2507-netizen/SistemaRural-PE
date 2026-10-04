from modelos.cita import Cita
from modelos.medicamento_recetado import MedicamentoRecetado
from modelos.personal_salud import PersonalSalud
from servicios.validaciones import validar_codigo, validar_diagnostico


class AtencionMedica:
    """Representa la atención clínica asociada a una cita."""

    ESTADOS_VALIDOS = {"Pendiente", "En proceso", "Finalizada"}

    def __init__(
        self,
        codigo,
        cita,
        diagnostico,
        estado="Pendiente",
        recetas=None,
        profesional_derivado=None,
    ):
        if cita is None or not isinstance(cita, Cita):
            raise ValueError("La atención debe estar asociada a una cita válida.")

        self._codigo = validar_codigo(codigo, "El código de atención")
        self._cita = cita
        self._diagnostico = validar_diagnostico(diagnostico)
        self.estado = estado
        self.recetas = recetas or []
        self.profesional_derivado = profesional_derivado

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

    @diagnostico.setter
    def diagnostico(self, valor):
        self._diagnostico = validar_diagnostico(valor)

    @property
    def recetas(self):
        return list(self._recetas)

    @recetas.setter
    def recetas(self, valores):
        valores = list(valores or [])
        if not all(isinstance(item, MedicamentoRecetado) for item in valores):
            raise TypeError("Las recetas deben ser objetos MedicamentoRecetado.")
        self._recetas = valores

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

    @property
    def profesional_derivado(self):
        return self._profesional_derivado

    @profesional_derivado.setter
    def profesional_derivado(self, valor):
        if valor is not None and not isinstance(valor, PersonalSalud):
            raise TypeError("La derivación debe apuntar a un profesional válido.")
        if valor is not None and (
            valor.codigo_profesional == self.profesional.codigo_profesional
            or "enfermer" in valor.especialidad.casefold()
        ):
            raise ValueError("La derivación debe dirigirse a otro profesional médico.")
        self._profesional_derivado = valor

    def mostrar_informacion(self):
        informacion = (
            f"Atención: {self.codigo} | "
            f"Cita: {self.cita.codigo} | "
            f"Paciente: {self.paciente.nombre} | "
            f"Profesional: {self.profesional.nombre} | "
            f"Fecha: {self.fecha} | Hora: {self.cita.hora} | "
            f"Diagnóstico: {self.diagnostico} | "
            f"Estado: {self.estado}"
        )
        if self.profesional_derivado:
            informacion += (
                f" | Derivación: {self.profesional_derivado.nombre} "
                f"({self.profesional_derivado.especialidad})"
            )
        return informacion

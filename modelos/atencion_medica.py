from servicios.validaciones import codigo_valido, texto_requerido


class AtencionMedica:
    def __init__(self, codigo, cita, diagnostico, estado="Pendiente"):
        self.codigo = codigo_valido(codigo, "El código de atención")
        self.cita = cita
        self.diagnostico = texto_requerido(diagnostico, "El diagnóstico")
        self.estado = texto_requerido(estado, "El estado")

    @property
    def paciente(self):
        return self.cita.paciente

    @property
    def profesional(self):
        return self.cita.profesional

    @property
    def fecha(self):
        return self.cita.fecha

    def mostrar_informacion(self):
        return f"Atención: {self.codigo} | Cita: {self.cita.codigo} | Paciente: {self.paciente.nombre} | Profesional: {self.profesional.nombre} | Fecha: {self.fecha} | Diagnóstico: {self.diagnostico} | Estado: {self.estado}"

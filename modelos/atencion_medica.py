class AtencionMedica:
    def __init__(self, codigo, cita, diagnostico, estado="Pendiente"):
        self.codigo, self.cita, self.diagnostico, self.estado = codigo, cita, diagnostico, estado
    @property
    def paciente(self): return self.cita.paciente
    @property
    def profesional(self): return self.cita.profesional
    @property
    def fecha(self): return self.cita.fecha
    def mostrar_informacion(self): return f"Atención: {self.codigo} | Cita: {self.cita.codigo} | Paciente: {self.paciente.nombre} | Profesional: {self.profesional.nombre} | Fecha: {self.fecha} | Diagnóstico: {self.diagnostico} | Estado: {self.estado}"

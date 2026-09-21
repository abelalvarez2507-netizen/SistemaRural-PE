class Cita:
    def __init__(self, codigo, paciente, profesional, fecha, motivo, estado="Pendiente"):
        self.codigo, self.paciente, self.profesional, self.fecha, self.motivo, self.estado = codigo, paciente, profesional, fecha, motivo, estado
    def mostrar_informacion(self): return f"Cita: {self.codigo} | Paciente: {self.paciente.nombre} | Profesional: {self.profesional.nombre} | Fecha: {self.fecha} | Motivo: {self.motivo} | Estado: {self.estado}"

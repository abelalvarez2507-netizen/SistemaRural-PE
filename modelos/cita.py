from servicios.validaciones import codigo_valido, fecha_valida, texto_requerido


class Cita:
    def __init__(self, codigo, paciente, profesional, fecha, motivo, estado="Pendiente"):
        self.codigo = codigo_valido(codigo, "El código de la cita")
        self.paciente = paciente
        self.profesional = profesional
        self.fecha = fecha_valida(fecha)
        self.motivo = texto_requerido(motivo, "El motivo")
        self.estado = texto_requerido(estado, "El estado")

    def mostrar_informacion(self):
        return f"Cita: {self.codigo} | Paciente: {self.paciente.nombre} | Profesional: {self.profesional.nombre} | Fecha: {self.fecha} | Motivo: {self.motivo} | Estado: {self.estado}"

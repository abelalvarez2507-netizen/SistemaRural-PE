class SistemaSalud:
    def __init__(self): self.pacientes=[]; self.personal=[]; self.citas=[]; self.atenciones=[]
    def registrar_paciente(self, paciente): self.pacientes.append(paciente)
    def registrar_personal(self, profesional): self.personal.append(profesional)
    def registrar_cita(self, cita): self.citas.append(cita)
    def registrar_atencion(self, atencion): self.atenciones.append(atencion)

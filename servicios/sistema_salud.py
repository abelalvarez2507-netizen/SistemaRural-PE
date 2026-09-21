from modelos.atencion_medica import AtencionMedica
from modelos.cita import Cita
from modelos.paciente import Paciente
from modelos.personal_salud import PersonalSalud

class SistemaSalud:
    """V2: relaciones y operaciones básicas de gestión."""
    def __init__(self): self.pacientes, self.personal, self.citas, self.atenciones = [], [], [], []
    def registrar_paciente(self, paciente):
        if not isinstance(paciente, Paciente): raise TypeError("Debe registrar un objeto Paciente.")
        self.pacientes.append(paciente); return paciente
    def registrar_personal(self, profesional):
        if not isinstance(profesional, PersonalSalud): raise TypeError("Debe registrar un objeto PersonalSalud.")
        self.personal.append(profesional); return profesional
    def registrar_cita(self, cita):
        if not isinstance(cita, Cita): raise TypeError("Debe registrar un objeto Cita.")
        if cita.paciente not in self.pacientes: raise ValueError("El paciente de la cita no está registrado.")
        if cita.profesional not in self.personal: raise ValueError("El profesional de la cita no está registrado.")
        self.citas.append(cita); return cita
    def registrar_atencion(self, atencion):
        if not isinstance(atencion, AtencionMedica): raise TypeError("Debe registrar un objeto AtencionMedica.")
        if atencion.cita not in self.citas: raise ValueError("La cita de la atención no está registrada.")
        self.atenciones.append(atencion); return atencion
    def buscar_paciente_por_codigo(self, codigo): return next((p for p in self.pacientes if p.codigo == codigo), None)
    def buscar_personal_por_codigo(self, codigo): return next((p for p in self.personal if p.codigo_profesional == codigo), None)
    def buscar_cita_por_codigo(self, codigo): return next((c for c in self.citas if c.codigo == codigo), None)
    def buscar_atencion_por_codigo(self, codigo): return next((a for a in self.atenciones if a.codigo == codigo), None)
    def listar_citas_de_paciente(self, codigo):
        p = self.buscar_paciente_por_codigo(codigo); return [] if p is None else [c for c in self.citas if c.paciente is p]
    def listar_atenciones_de_paciente(self, codigo):
        p = self.buscar_paciente_por_codigo(codigo); return [] if p is None else [a for a in self.atenciones if a.paciente is p]
    def obtener_pacientes(self): return self.pacientes
    def obtener_personal(self): return self.personal
    def obtener_citas(self): return self.citas
    def obtener_atenciones(self): return self.atenciones

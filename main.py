from modelos.atencion_medica import AtencionMedica
from modelos.cita import Cita
from modelos.paciente import Paciente
from modelos.personal_salud import PersonalSalud
from servicios.sistema_salud import SistemaSalud

def main():
    sistema = SistemaSalud()
    paciente = Paciente("P001", "12345678", "Juan Perez", 35)
    profesional = PersonalSalud("PS001", "87654321", "Ana Lopez", 40, "Medicina General")
    cita = Cita("C001", paciente, profesional, "15/09/2026", "Consulta general")
    atencion = AtencionMedica("A001", cita, "Evaluación general")
    sistema.registrar_paciente(paciente); sistema.registrar_personal(profesional)
    sistema.registrar_cita(cita); sistema.registrar_atencion(atencion)
    print("=== SistemaRural-PE - Versión 2 ===")
    print(paciente.mostrar_informacion()); print(profesional.mostrar_informacion())
    print(cita.mostrar_informacion()); print(atencion.mostrar_informacion())
    print("Paciente encontrado:", sistema.buscar_paciente_por_codigo("P001").nombre)
    print("Citas del paciente:", len(sistema.listar_citas_de_paciente("P001")))
    print("Atenciones del paciente:", len(sistema.listar_atenciones_de_paciente("P001")))
if __name__ == "__main__": main()

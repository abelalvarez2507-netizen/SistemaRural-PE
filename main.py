from modelos.paciente import Paciente
from modelos.personal_salud import PersonalSalud
from servicios.sistema_salud import SistemaSalud

sistema = SistemaSalud()
sistema.registrar_paciente(Paciente("P01", "Ana", 20))
sistema.registrar_personal(PersonalSalud("M01", "Luis", 35, "Medicina"))
print("SistemaRural-PE V1")
print("Pacientes:", len(sistema.pacientes))
print("Personal:", len(sistema.personal))

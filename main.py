from modelos.paciente import Paciente
from modelos.personal_salud import PersonalSalud
from modelos.cita import Cita
from servicios.persistencia import Persistencia

# V4: primera incorporación de SQLite.
# Esta versión contiene errores de principiante que se corregirán en V4.1.
persistencia = Persistencia(":memory:")

paciente = Paciente("P001", "12345678", "Juan Perez", 30)
profesional = PersonalSalud("PS001", "87654321", "Ana Lopez", 35, "Medicina General")
cita = Cita("C001", paciente, profesional, "2026-09-20", "Control")

persistencia.guardar_paciente(paciente)
persistencia.guardar_personal(profesional)
persistencia.guardar_cita(cita)

print("=== SistemaRural-PE V4 ===")
print("Persistencia SQLite incorporada.")
print("Pacientes guardados:", persistencia.contar_pacientes())

# Problema intencional de esta etapa: el mismo paciente puede guardarse otra vez.
persistencia.guardar_paciente(paciente)
print("Pacientes después de guardar el mismo registro otra vez:", persistencia.contar_pacientes())
print("Nota: en V4.1 se corregirá el problema de duplicados y otros detalles de persistencia.")

persistencia.cerrar()

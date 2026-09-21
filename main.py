import os

from modelos.paciente import Paciente
from modelos.personal_salud import PersonalSalud
from modelos.cita import Cita
from servicios.sistema_salud import SistemaSalud
from servicios.persistencia import Persistencia
from servicios.seguridad_datos import SeguridadDatos
from servicios.fabrica import FabricaPersonas
from servicios.configuracion import Configuracion


def main():
    archivo = "sistema_rural_v5.db"
    if os.path.exists(archivo):
        os.remove(archivo)

    sistema = SistemaSalud()

    # Primera prueba de Factory.
    fabrica = FabricaPersonas()
    paciente = fabrica.crear("paciente", "P001", "12345678", "Juan Perez", 35)
    profesional = fabrica.crear("personal", "PS001", "87654321", "Ana Lopez", 40, "Medicina General")

    # Error de principiante: en otra parte todavía se crean objetos directamente.
    paciente_prueba = Paciente("P002", "11112222", "Maria Ruiz", 28)
    cita = Cita("C001", paciente, profesional, "15/09/2026", "Consulta general")

    sistema.registrar_paciente(paciente)
    sistema.registrar_paciente(paciente_prueba)
    sistema.registrar_personal(profesional)
    sistema.registrar_cita(cita)

    db = Persistencia(archivo)
    db.guardar_paciente(paciente)
    db.guardar_personal(profesional)
    db.guardar_cita(cita)

    config1 = Configuracion.obtener_instancia()
    config2 = Configuracion()  # Error intencional: no se obliga el Singleton.

    print("=== SistemaRural-PE - Versión 5.1 ===")
    print("Factory utilizada:", type(paciente).__name__, type(profesional).__name__)
    print("¿Las configuraciones son la misma instancia?:", config1 is config2)
    print(paciente.mostrar_informacion())
    print("DNI protegido en memoria de prueba:", SeguridadDatos.proteger_dni(paciente.dni)[:25] + "...")
    print("DNI correcto:", db.verificar_dni_paciente("P001", "12345678"))
    print("DNI incorrecto:", db.verificar_dni_paciente("P001", "00000000"))
    print("DNI mostrado de forma segura:", SeguridadDatos.enmascarar_dni(paciente.dni))
    print("Pacientes almacenados en SQLite:", db.contar_pacientes())

    try:
        db.guardar_paciente(paciente)
    except ValueError as error:
        print("Duplicado controlado:", error)

    db.cerrar()


if __name__ == "__main__":
    main()

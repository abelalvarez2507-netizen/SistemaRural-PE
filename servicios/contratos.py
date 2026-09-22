from typing import Protocol


class RepositorioSaludProtocol(Protocol):
    """
    Contrato que define las operaciones que
    SistemaSalud necesita del repositorio.

    Permite aplicar inversión de dependencias (DIP):
    SistemaSalud depende de una abstracción,
    no de una implementación concreta.
    """

    def obtener_pacientes(self):
        ...

    def obtener_personal(self):
        ...

    def obtener_citas(self):
        ...

    def obtener_atenciones(self):
        ...

    def guardar_paciente(self, paciente):
        ...

    def guardar_personal(self, profesional):
        ...

    def guardar_cita(self, cita):
        ...

    def guardar_atencion(self, atencion):
        ...

    def existe_dni_paciente(self, dni):
        ...

    def existe_dni_personal(self, dni):
        ...

    def actualizar_estado_cita(
        self,
        codigo_cita,
        nuevo_estado
    ):
        ...

    def actualizar_estado_atencion(
        self,
        codigo_atencion,
        nuevo_estado
    ):
        ...

    def cerrar(self):
        ...
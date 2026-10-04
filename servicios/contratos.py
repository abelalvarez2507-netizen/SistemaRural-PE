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

    def actualizar_agenda_cita(self, codigo_cita, fecha, hora, estado):
        ...

    def actualizar_estado_atencion(
        self,
        codigo_atencion,
        nuevo_estado
    ):
        ...

    def actualizar_diagnostico_atencion(self, codigo_atencion, diagnostico):
        ...

    def guardar_recetas_atencion(self, codigo_atencion, recetas):
        ...

    def obtener_recetas_atencion(self, codigo_atencion):
        ...

    def guardar_medicamento(self, *datos):
        ...

    def obtener_medicamentos(self):
        ...

    def obtener_medicamentos_disponibles(self, fecha_actual):
        ...

    def registrar_venta_medicamento(self, *datos):
        ...

    def obtener_ventas_medicamentos(self, limite=100):
        ...

    def obtener_ventas_paciente(self, codigo_paciente):
        ...

    def obtener_estadisticas_medicamentos(self, fecha_actual):
        ...

    def cerrar(self):
        ...

from modelos.paciente import Paciente
from modelos.cita import Cita
from modelos.personal_salud import PersonalSalud
from modelos.atencion_medica import AtencionMedica

from servicios.repositorio import RepositorioSalud
from servicios.fabrica import FabricaEntidades
from servicios.contratos import RepositorioSaludProtocol


class SistemaSalud:
    """
    Coordina las operaciones principales del sistema.

    Responsabilidades:
    - Coordinar entidades.
    - Aplicar reglas de negocio.
    - Delegar la persistencia al repositorio.

    La persistencia no se implementa directamente aquí.
    """

    def __init__(
        self,
        repositorio: RepositorioSaludProtocol | None = None
    ):
        """
        Permite inyectar un repositorio.

        Si no se proporciona uno, se utiliza
        el repositorio SQLite del sistema.
        """

        if repositorio is None:
            repositorio = RepositorioSalud()

        self._repositorio = repositorio

        self._pacientes = []
        self._personal = []
        self._citas = []
        self._atenciones = []

        self._cargar_pacientes()
        self._cargar_personal()
        self._cargar_citas()
        self._cargar_atenciones()

    # =========================================================
    # CARGAR PACIENTES
    # =========================================================

    def _cargar_pacientes(self):

        datos = (
            self._repositorio
            .obtener_pacientes()
        )

        self._pacientes = [

            FabricaEntidades
            .crear_paciente_desde_datos_protegidos(
                codigo,
                dni_hash,
                dni_salt,
                nombre,
                edad
            )

            for (
                codigo,
                dni_hash,
                dni_salt,
                nombre,
                edad
            ) in datos
        ]

    # =========================================================
    # CARGAR PERSONAL
    # =========================================================

    def _cargar_personal(self):

        datos = (
            self._repositorio
            .obtener_personal()
        )

        self._personal = [

            FabricaEntidades
            .crear_personal_desde_datos_protegidos(
                codigo_profesional,
                dni_hash,
                dni_salt,
                nombre,
                edad,
                especialidad
            )

            for (
                codigo_profesional,
                dni_hash,
                dni_salt,
                nombre,
                edad,
                especialidad
            ) in datos
        ]

    # =========================================================
    # CARGAR CITAS
    # =========================================================

    def _cargar_citas(self):

        datos = (
            self._repositorio
            .obtener_citas()
        )

        for (
            codigo,
            paciente_codigo,
            profesional_codigo,
            fecha,
            motivo,
            estado
        ) in datos:

            paciente = next(
                (
                    paciente
                    for paciente in self._pacientes
                    if paciente.codigo
                    == paciente_codigo
                ),
                None
            )

            profesional = next(
                (
                    profesional
                    for profesional in self._personal
                    if (
                        profesional.codigo_profesional
                        == profesional_codigo
                    )
                ),
                None
            )

            if paciente is None:
                raise ValueError(
                    "Se encontró una cita con "
                    "un paciente inexistente."
                )

            if profesional is None:
                raise ValueError(
                    "Se encontró una cita con "
                    "un profesional inexistente."
                )

            cita = (
                FabricaEntidades.crear_cita(
                    codigo,
                    paciente,
                    profesional,
                    fecha,
                    motivo,
                    estado
                )
            )

            self._citas.append(cita)

    # =========================================================
    # CARGAR ATENCIONES
    # =========================================================

    def _cargar_atenciones(self):

        datos = (
            self._repositorio
            .obtener_atenciones()
        )

        for (
            codigo,
            cita_codigo,
            diagnostico,
            estado
        ) in datos:

            cita = next(
                (
                    cita
                    for cita in self._citas
                    if cita.codigo
                    == cita_codigo
                ),
                None
            )

            if cita is None:
                raise ValueError(
                    "Se encontró una atención con "
                    "una cita inexistente."
                )

            atencion = (
                FabricaEntidades.crear_atencion(
                    codigo,
                    cita,
                    diagnostico,
                    estado
                )
            )

            self._atenciones.append(atencion)

    # =========================================================
    # GENERAR CÓDIGOS
    # =========================================================

    def generar_codigo_paciente(self):

        numeros_ocupados = set()

        for paciente in self._pacientes:

            codigo = paciente.codigo.upper()

            if codigo.startswith("P"):

                try:
                    numero = int(codigo[1:])
                    numeros_ocupados.add(numero)

                except ValueError:
                    continue

        numero = 1

        while numero in numeros_ocupados:
            numero += 1

        return f"P{numero:03d}"

    def generar_codigo_cita(self):

        numeros_ocupados = set()

        for cita in self._citas:

            codigo = cita.codigo.upper()

            if codigo.startswith("C"):

                try:
                    numero = int(codigo[1:])
                    numeros_ocupados.add(numero)

                except ValueError:
                    continue

        numero = 1

        while numero in numeros_ocupados:
            numero += 1

        return f"C{numero:03d}"

    def generar_codigo_atencion(self):

        numeros_ocupados = set()

        for atencion in self._atenciones:

            codigo = atencion.codigo.upper()

            if codigo.startswith("A"):

                try:
                    numero = int(codigo[1:])
                    numeros_ocupados.add(numero)

                except ValueError:
                    continue

        numero = 1

        while numero in numeros_ocupados:
            numero += 1

        return f"A{numero:03d}"

    # =========================================================
    # REGISTRAR PACIENTE
    # =========================================================

    def registrar_paciente(self, paciente):

        if not isinstance(
            paciente,
            Paciente
        ):
            raise TypeError(
                "El registro debe ser "
                "un objeto Paciente."
            )

        existe_codigo = any(
            existente.codigo == paciente.codigo
            for existente in self._pacientes
        )

        if existe_codigo:
            raise ValueError(
                "Ya existe un paciente "
                "con ese código."
            )

        if self._repositorio.existe_dni_paciente(
            paciente.dni
        ):
            raise ValueError(
                "Ya existe un paciente "
                "con ese DNI."
            )

        self._repositorio.guardar_paciente(
            paciente
        )

        self._pacientes.append(
            paciente
        )

    # =========================================================
    # REGISTRAR PERSONAL
    # =========================================================

    def registrar_personal(
        self,
        profesional
    ):

        if not isinstance(
            profesional,
            PersonalSalud
        ):
            raise TypeError(
                "El registro debe ser "
                "un objeto PersonalSalud."
            )

        existe_codigo = any(
            existente.codigo_profesional
            == profesional.codigo_profesional
            for existente in self._personal
        )

        if existe_codigo:
            raise ValueError(
                "Ya existe un profesional "
                "con ese código."
            )

        if self._repositorio.existe_dni_personal(
            profesional.dni
        ):
            raise ValueError(
                "Ya existe un profesional "
                "con ese DNI."
            )

        self._repositorio.guardar_personal(
            profesional
        )

        self._personal.append(
            profesional
        )

    # =========================================================
    # REGISTRAR CITA
    # =========================================================

    def registrar_cita(self, cita):

        if not isinstance(
            cita,
            Cita
        ):
            raise TypeError(
                "El registro debe ser "
                "un objeto Cita."
            )

        paciente_existe = any(
            paciente.codigo
            == cita.paciente.codigo
            for paciente in self._pacientes
        )

        profesional_existe = any(
            profesional.codigo_profesional
            == cita.profesional.codigo_profesional
            for profesional in self._personal
        )

        if not paciente_existe:
            raise ValueError(
                "El paciente no está registrado."
            )

        if not profesional_existe:
            raise ValueError(
                "El profesional no está registrado."
            )

        codigo_existe = any(
            existente.codigo
            == cita.codigo
            for existente in self._citas
        )

        if codigo_existe:
            raise ValueError(
                "El código de cita "
                "ya está ocupado."
            )

        self._repositorio.guardar_cita(
            cita
        )

        self._citas.append(
            cita
        )

    # =========================================================
    # REGISTRAR ATENCIÓN
    # =========================================================

    def registrar_atencion(
        self,
        atencion
    ):

        if not isinstance(
            atencion,
            AtencionMedica
        ):
            raise TypeError(
                "El registro debe ser "
                "un objeto AtencionMedica."
            )

        cita = next(
            (
                existente
                for existente in self._citas
                if existente.codigo
                == atencion.cita.codigo
            ),
            None
        )

        if cita is None:
            raise ValueError(
                "La cita no está registrada."
            )

        codigo_existe = any(
            existente.codigo
            == atencion.codigo
            for existente in self._atenciones
        )

        if codigo_existe:
            raise ValueError(
                "Ya existe una atención "
                "con ese código."
            )

        atencion_existente = any(
            existente.cita.codigo
            == cita.codigo
            for existente in self._atenciones
        )

        if atencion_existente:
            raise ValueError(
                "La cita ya tiene una "
                "atención médica registrada."
            )

        self._repositorio.guardar_atencion(
            atencion
        )

        self._atenciones.append(
            atencion
        )

    # =========================================================
    # ESTADOS DE CITAS
    # =========================================================

    def actualizar_estado_cita(
        self,
        codigo_cita,
        nuevo_estado
    ):

        if nuevo_estado not in Cita.ESTADOS_VALIDOS:
            raise ValueError(
                "Estado inválido. Use: "
                "Pendiente, Atendida o Reprogramar."
            )

        cita = next(
            (
                existente
                for existente in self._citas
                if existente.codigo
                == codigo_cita
            ),
            None
        )

        if cita is None:
            raise ValueError(
                "No se encontró la cita."
            )

        self._repositorio.actualizar_estado_cita(
            codigo_cita,
            nuevo_estado
        )

        cita.estado = nuevo_estado

    # =========================================================
    # ESTADOS DE ATENCIONES
    # =========================================================

    def actualizar_estado_atencion(
        self,
        codigo_atencion,
        nuevo_estado
    ):

        if (
            nuevo_estado
            not in AtencionMedica.ESTADOS_VALIDOS
        ):
            raise ValueError(
                "Estado inválido. Use: "
                "Pendiente, En proceso o Finalizada."
            )

        atencion = next(
            (
                existente
                for existente in self._atenciones
                if existente.codigo
                == codigo_atencion
            ),
            None
        )

        if atencion is None:
            raise ValueError(
                "No se encontró la atención."
            )

        self._repositorio.actualizar_estado_atencion(
            codigo_atencion,
            nuevo_estado
        )

        atencion.estado = nuevo_estado

    # =========================================================
    # CONSULTAS
    # =========================================================

    def obtener_pacientes(self):
        return list(self._pacientes)

    def obtener_personal(self):
        return list(self._personal)

    def obtener_citas(self):
        return list(self._citas)

    def obtener_atenciones(self):
        return list(self._atenciones)

    # =========================================================
    # CITAS POR ESTADO
    # =========================================================

    def obtener_citas_pendientes(self):

        return list(
            filter(
                lambda cita:
                    cita.estado == "Pendiente",
                self._citas
            )
        )

    def obtener_citas_atendidas(self):

        return list(
            filter(
                lambda cita:
                    cita.estado == "Atendida",
                self._citas
            )
        )

    def obtener_citas_reprogramadas(self):

        return list(
            filter(
                lambda cita:
                    cita.estado == "Reprogramar",
                self._citas
            )
        )

    # =========================================================
    # ATENCIONES POR ESTADO
    # =========================================================

    def obtener_atenciones_pendientes(self):

        return list(
            filter(
                lambda atencion:
                    atencion.estado == "Pendiente",
                self._atenciones
            )
        )

    def obtener_atenciones_en_proceso(self):

        return list(
            filter(
                lambda atencion:
                    atencion.estado == "En proceso",
                self._atenciones
            )
        )

    def obtener_atenciones_finalizadas(self):

        return list(
            filter(
                lambda atencion:
                    atencion.estado == "Finalizada",
                self._atenciones
            )
        )

    # =========================================================
    # HISTORIAL CLÍNICO
    # =========================================================

    def obtener_historial_paciente(
        self,
        codigo_paciente
    ):

        paciente = next(
            (
                paciente
                for paciente in self._pacientes
                if paciente.codigo
                == codigo_paciente
            ),
            None
        )

        if paciente is None:
            raise ValueError(
                "No se encontró el paciente."
            )

        citas = list(
            filter(
                lambda cita:
                    (
                        cita.paciente.codigo
                        == codigo_paciente
                    )
                    and
                    cita.estado == "Atendida",
                self._citas
            )
        )

        atenciones = list(
            filter(
                lambda atencion:
                    (
                        atencion.cita.paciente.codigo
                        == codigo_paciente
                    )
                    and
                    atencion.estado == "Finalizada",
                self._atenciones
            )
        )

        return {
            "paciente": paciente,
            "citas": citas,
            "atenciones": atenciones
        }

    # =========================================================
    # BÚSQUEDA DE PACIENTES
    # =========================================================

    def buscar_paciente_por_codigo(
        self,
        codigo
    ):

        codigo = codigo.strip()

        return list(
            filter(
                lambda paciente:
                    paciente.codigo.lower()
                    == codigo.lower(),
                self._pacientes
            )
        )

    def buscar_paciente_por_dni(
        self,
        dni
    ):
        """Busca pacientes verificando el DNI contra su huella protegida."""

        dni = str(dni).strip()

        return list(
            filter(
                lambda paciente:
                    paciente.verificar_dni(dni),
                self._pacientes
            )
        )

    def buscar_pacientes_por_edad(
        self,
        edad_minima
    ):

        return list(
            filter(
                lambda paciente:
                    paciente.edad >= edad_minima,
                self._pacientes
            )
        )

    # =========================================================
    # BÚSQUEDA DE PERSONAL
    # =========================================================

    def buscar_personal_por_codigo(
        self,
        codigo
    ):

        codigo = codigo.strip()

        return list(
            filter(
                lambda profesional:
                    (
                        profesional.codigo_profesional
                        .lower()
                        == codigo.lower()
                    ),
                self._personal
            )
        )

    def buscar_personal_por_dni(
        self,
        dni
    ):
        """Busca profesionales verificando el DNI contra su huella protegida."""

        dni = str(dni).strip()

        return list(
            filter(
                lambda profesional:
                    profesional.verificar_dni(dni),
                self._personal
            )
        )

    # =========================================================
    # PROGRAMACIÓN FUNCIONAL
    # =========================================================

    def obtener_nombres_pacientes(self):

        return list(
            map(
                lambda paciente:
                    paciente.nombre,
                self._pacientes
            )
        )

    # =========================================================
    # ESTADÍSTICAS
    # =========================================================

    def total_pacientes(self):
        return len(self._pacientes)

    def total_personal(self):
        return len(self._personal)

    def total_citas(self):
        return len(self._citas)

    def total_citas_pendientes(self):
        return len(
            self.obtener_citas_pendientes()
        )

    def total_citas_atendidas(self):
        return len(
            self.obtener_citas_atendidas()
        )

    def total_citas_reprogramadas(self):
        return len(
            self.obtener_citas_reprogramadas()
        )

    def total_atenciones(self):
        return len(self._atenciones)

    def total_atenciones_finalizadas(self):
        return len(
            self.obtener_atenciones_finalizadas()
        )

    # =========================================================
    # CIERRE
    # =========================================================

    def cerrar(self):
        self._repositorio.cerrar()
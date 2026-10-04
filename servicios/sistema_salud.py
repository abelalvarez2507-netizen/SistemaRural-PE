from modelos.paciente import Paciente
from modelos.cita import Cita
from modelos.personal_salud import PersonalSalud
from modelos.atencion_medica import AtencionMedica
from modelos.medicamento_recetado import MedicamentoRecetado
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import random

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
        self.actualizar_citas_vencidas()

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

        for fila in datos:
            if len(fila) == 6:
                (
                    codigo,
                    paciente_codigo,
                    profesional_codigo,
                    fecha,
                    motivo,
                    estado,
                ) = fila
                hora = "09:00"
            else:
                (
                    codigo,
                    paciente_codigo,
                    profesional_codigo,
                    fecha,
                    hora,
                    motivo,
                    estado,
                ) = fila

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
                    estado,
                    hora,
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

        for fila in datos:
            codigo, cita_codigo, diagnostico, estado = fila[:4]
            profesional_derivado_codigo = fila[4] if len(fila) > 4 else None

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

            recetas = [
                MedicamentoRecetado(medicamento, dias, cada_cuanto)
                for medicamento, dias, cada_cuanto
                in self._repositorio.obtener_recetas_atencion(codigo)
            ] if hasattr(self._repositorio, "obtener_recetas_atencion") else []
            profesional_derivado = next(
                (
                    profesional
                    for profesional in self._personal
                    if profesional.codigo_profesional
                    == profesional_derivado_codigo
                ),
                None,
            )
            atencion = FabricaEntidades.crear_atencion(
                codigo,
                cita,
                diagnostico,
                estado,
                recetas,
                profesional_derivado,
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

    def generar_codigo_personal(self, prefijo):
        """Devuelve el siguiente código libre para un prefijo, sin tope de cifras."""
        prefijo = str(prefijo or "").strip().upper()
        if not prefijo.isalpha():
            raise ValueError("El prefijo del código de personal no es válido.")
        ocupados = set()
        for persona in self._personal:
            codigo = persona.codigo_personal.upper()
            if codigo.startswith(prefijo) and codigo[len(prefijo):].isdigit():
                ocupados.add(int(codigo[len(prefijo):]))
        numero = 1
        while numero in ocupados:
            numero += 1
        return f"{prefijo}{numero:03d}"

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
        profesional,
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

        if cita.hora not in self.HORARIOS_ATENCION:
            raise ValueError(
                "El horario de atención es de 07:00 a 18:00, con turnos cada 30 minutos."
            )

        self._validar_fecha_hora_futura(cita.fecha_hora)
        self._validar_disponibilidad(
            cita.profesional.codigo_profesional,
            cita.fecha,
            cita.hora,
            paciente_codigo=cita.paciente.codigo,
        )

        self._repositorio.guardar_cita(
            cita
        )

        self._citas.append(
            cita
        )

    HORARIOS_ATENCION = tuple(
        (datetime.strptime("07:00", "%H:%M") + timedelta(minutes=30 * paso))
        .strftime("%H:%M")
        for paso in range(22)
    )

    def _validar_fecha_hora_futura(self, fecha_hora):
        if fecha_hora <= datetime.now():
            raise ValueError(
                "La cita debe ser posterior a la fecha y hora actuales."
            )

    def _validar_disponibilidad(
        self,
        profesional_codigo,
        fecha,
        hora,
        paciente_codigo=None,
        excluir_codigo=None,
    ):
        for cita in self._citas:
            if cita.codigo == excluir_codigo:
                continue
            if cita.estado not in {"Pendiente", "Reprogramada"}:
                continue
            if cita.fecha != fecha or cita.hora != hora:
                continue
            if cita.profesional.codigo_profesional == profesional_codigo:
                raise ValueError(
                    "Ese horario ya está reservado para el profesional. "
                    "Elige otro horario disponible."
                )
            if paciente_codigo and cita.paciente.codigo == paciente_codigo:
                raise ValueError(
                    "El paciente ya tiene una cita en ese horario."
                )

    def horarios_disponibles(
        self,
        profesional_codigo,
        fecha,
        excluir_codigo=None,
    ):
        from servicios.validaciones import normalizar_fecha

        fecha_normalizada = normalizar_fecha(fecha)
        fecha_base = datetime.strptime(fecha_normalizada, "%d/%m/%Y").date()
        ahora = datetime.now()
        if fecha_base < ahora.date():
            return []

        ocupados = {
            cita.hora
            for cita in self._citas
            if cita.codigo != excluir_codigo
            and cita.estado in {"Pendiente", "Reprogramada"}
            and cita.fecha == fecha_normalizada
            and cita.profesional.codigo_profesional == profesional_codigo
        }
        disponibles = []
        for hora in self.HORARIOS_ATENCION:
            momento = datetime.strptime(
                f"{fecha_normalizada} {hora}",
                "%d/%m/%Y %H:%M",
            )
            if hora not in ocupados and momento > ahora:
                disponibles.append(hora)
        return disponibles

    def horarios_disponibles_para_cita(self, fecha, paciente_codigo=None):
        """Devuelve horas con algún médico libre; la asignación prefiere medicina general."""
        from servicios.validaciones import normalizar_fecha

        fecha_normalizada = normalizar_fecha(fecha)
        medicos = [
            profesional
            for profesional in self._personal
            if "enfermer" not in profesional.especialidad.casefold()
        ]
        horarios = {
            hora
            for profesional in medicos
            for hora in self.horarios_disponibles(
                profesional.codigo_profesional,
                fecha_normalizada,
            )
        }

        if paciente_codigo:
            horarios = {
                hora
                for hora in horarios
                if not any(
                    cita.paciente.codigo == paciente_codigo
                    and cita.fecha == fecha_normalizada
                    and cita.hora == hora
                    and cita.estado in {"Pendiente", "Reprogramada"}
                    for cita in self._citas
                )
            }

        return sorted(horarios)

    def profesionales_disponibles_para_cita(
        self, fecha, hora, paciente_codigo=None
    ):
        """Prefiere médicos generales disponibles y usa otro médico si hace falta."""
        from servicios.validaciones import normalizar_fecha, normalizar_hora

        fecha_normalizada = normalizar_fecha(fecha)
        hora_normalizada = normalizar_hora(hora)
        if hora_normalizada not in self.HORARIOS_ATENCION:
            return []

        if paciente_codigo and any(
            cita.paciente.codigo == paciente_codigo
            and cita.fecha == fecha_normalizada
            and cita.hora == hora_normalizada
            and cita.estado in {"Pendiente", "Reprogramada"}
            for cita in self._citas
        ):
            return []

        medicos = [
            profesional
            for profesional in self._personal
            if "enfermer" not in profesional.especialidad.casefold()
        ]
        generales = [
            profesional
            for profesional in medicos
            if profesional.especialidad.strip().casefold() == "medicina general"
        ]

        def disponibles(profesionales):
            return [
                profesional
                for profesional in profesionales
                if hora_normalizada in self.horarios_disponibles(
                    profesional.codigo_profesional,
                    fecha_normalizada,
                )
            ]

        candidatos = disponibles(generales)
        return candidatos or disponibles(medicos)

    def crear_cita_asignacion_automatica(self, paciente, fecha, motivo, hora):
        """Reserva con asignación aleatoria entre médicos que tienen ese turno libre."""
        from servicios.validaciones import normalizar_fecha, normalizar_hora

        fecha_normalizada = normalizar_fecha(fecha)
        hora_normalizada = normalizar_hora(hora)
        candidatos = self.profesionales_disponibles_para_cita(
            fecha_normalizada,
            hora_normalizada,
            paciente_codigo=paciente.codigo,
        )
        if not candidatos:
            raise ValueError(
                "Ese horario ya no está disponible. Actualiza la lista y elige otro."
            )

        cita = Cita(
            self.generar_codigo_cita(),
            paciente,
            random.choice(candidatos),
            fecha_normalizada,
            motivo,
            "Pendiente",
            hora_normalizada,
        )
        self.registrar_cita(cita)
        return cita

    def reprogramar_cita(self, codigo_cita, fecha, hora):
        cita = next(
            (item for item in self._citas if item.codigo == codigo_cita),
            None,
        )
        if cita is None:
            raise ValueError("No se encontró la cita.")
        if cita.estado in {"Atendida", "No atendida", "Cancelada"}:
            raise ValueError("Esta cita ya no se puede reprogramar.")

        from servicios.validaciones import normalizar_fecha, normalizar_hora

        fecha_nueva = normalizar_fecha(fecha)
        hora_nueva = normalizar_hora(hora)
        if hora_nueva not in self.HORARIOS_ATENCION:
            raise ValueError(
                "El horario de atención es de 07:00 a 18:00, con turnos cada 30 minutos."
            )
        momento = datetime.strptime(
            f"{fecha_nueva} {hora_nueva}",
            "%d/%m/%Y %H:%M",
        )
        self._validar_fecha_hora_futura(momento)
        self._validar_disponibilidad(
            cita.profesional.codigo_profesional,
            fecha_nueva,
            hora_nueva,
            paciente_codigo=cita.paciente.codigo,
            excluir_codigo=cita.codigo,
        )
        self._repositorio.actualizar_agenda_cita(
            cita.codigo,
            fecha_nueva,
            hora_nueva,
            "Reprogramada",
        )
        cita.fecha = fecha_nueva
        cita.hora = hora_nueva
        cita.estado = "Reprogramada"

    def cancelar_cita(self, codigo_cita):
        self.actualizar_estado_cita(codigo_cita, "Cancelada")

    def actualizar_citas_vencidas(self):
        ahora = datetime.now()
        vencidas = [
            cita
            for cita in self._citas
            if cita.estado in {"Pendiente", "Reprogramada"}
            and cita.fecha_hora <= ahora
        ]
        for cita in vencidas:
            self.actualizar_estado_cita(cita.codigo, "Cancelada")
        return len(vencidas)

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

        # La visita marca la cita como Atendida; el avance clínico conserva
        # su propio estado (Pendiente, En proceso o Finalizada).
        self.actualizar_estado_cita(cita.codigo, "Atendida")

    def actualizar_atencion(
        self,
        codigo_atencion,
        diagnostico,
        recetas=None,
        profesional_derivado=None,
    ):
        atencion = next(
            (item for item in self._atenciones if item.codigo == codigo_atencion),
            None,
        )
        if atencion is None:
            raise ValueError("No se encontró la atención médica.")
        atencion.diagnostico = diagnostico
        atencion.profesional_derivado = profesional_derivado
        self._repositorio.actualizar_diagnostico_atencion(
            codigo_atencion,
            atencion.diagnostico,
            (
                atencion.profesional_derivado.codigo_profesional
                if atencion.profesional_derivado
                else None
            ),
        )
        if recetas is not None:
            atencion.recetas = self._validar_recetas(recetas)
            self._repositorio.guardar_recetas_atencion(
                codigo_atencion,
                atencion.recetas,
            )
        self.actualizar_estado_atencion(codigo_atencion, "Finalizada")
        self.actualizar_estado_cita(atencion.cita.codigo, "Atendida")

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
                "Pendiente, Atendida, Reprogramada, No atendida o Cancelada."
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

    @staticmethod
    def _validar_recetas(recetas):
        resultado = []
        for receta in recetas or []:
            if isinstance(receta, MedicamentoRecetado):
                resultado.append(receta)
            else:
                resultado.append(MedicamentoRecetado(*receta))
        return resultado

    # =========================================================
    # MEDICAMENTOS Y VENTAS
    # =========================================================

    @staticmethod
    def _entero_no_negativo(valor, etiqueta):
        try:
            numero = int(str(valor).strip())
        except (TypeError, ValueError):
            raise ValueError(f"{etiqueta} debe ser un número entero.") from None
        if numero < 0:
            raise ValueError(f"{etiqueta} no puede ser negativo.")
        return numero

    @staticmethod
    def _precio_medicamento(valor):
        try:
            texto = str(valor).strip()
            if "," in texto and "." not in texto:
                texto = texto.replace(",", ".")
            precio = Decimal(texto).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("El precio debe ser un importe válido.") from None
        if not precio.is_finite() or precio < 0:
            raise ValueError("El precio no puede ser negativo.")
        return float(precio)

    def registrar_medicamento(
        self,
        nombre,
        principio_activo,
        presentacion,
        lote,
        vencimiento,
        stock,
        stock_minimo,
        precio_venta,
        registrado_por,
        fecha_fabricacion=None,
    ):
        nombre = str(nombre or "").strip()
        principio_activo = str(principio_activo or "").strip()
        presentacion = str(presentacion or "").strip()
        lote = str(lote or "").strip()
        registrado_por = str(registrado_por or "").strip()
        if not nombre:
            raise ValueError("Ingresa el nombre del medicamento.")
        if not lote:
            raise ValueError("Ingresa el número de lote.")
        if not registrado_por:
            raise ValueError("No se pudo identificar a quien registra el medicamento.")
        def normalizar_fecha(valor, etiqueta):
            texto = str(valor or "").strip()
            for formato in ("%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(texto, formato).date()
                except (TypeError, ValueError):
                    continue
            raise ValueError(f"Usa la fecha de {etiqueta} DD/MM/AAAA.")

        fecha_vencimiento = normalizar_fecha(vencimiento, "vencimiento")
        fecha_fabricacion_normalizada = None
        if fecha_fabricacion is not None:
            fecha_fabricacion_normalizada = normalizar_fecha(
                fecha_fabricacion, "fabricación"
            )
            if fecha_fabricacion_normalizada > date.today():
                raise ValueError("La fecha de fabricación no puede estar en el futuro.")
            if fecha_vencimiento < fecha_fabricacion_normalizada:
                raise ValueError(
                    "El vencimiento no puede ser anterior a la fecha de fabricación."
                )
            lote = f"lot-{fecha_fabricacion_normalizada:%d%m%Y}-b"
        vencimiento = fecha_vencimiento.isoformat()
        stock = self._entero_no_negativo(stock, "El stock")
        if stock == 0:
            raise ValueError("El stock inicial debe ser mayor que cero.")
        stock_minimo = self._entero_no_negativo(
            stock_minimo, "El stock mínimo"
        )
        if fecha_vencimiento < date.today():
            raise ValueError("La fecha de vencimiento no puede estar en el pasado.")
        precio_venta = self._precio_medicamento(precio_venta)
        return self._repositorio.guardar_medicamento(
            nombre,
            principio_activo,
            presentacion,
            lote,
            vencimiento,
            stock,
            stock_minimo,
            precio_venta,
            registrado_por,
        )

    def obtener_medicamentos(self):
        return self._repositorio.obtener_medicamentos()

    def obtener_medicamentos_disponibles(self):
        return self._repositorio.obtener_medicamentos_disponibles(
            date.today().isoformat()
        )

    def vender_medicamento(self, medicamento_id, cantidad, paciente_codigo, vendido_por):
        try:
            medicamento_id = int(medicamento_id)
        except (TypeError, ValueError):
            raise ValueError("Selecciona un medicamento registrado.") from None
        if medicamento_id <= 0:
            raise ValueError("Selecciona un medicamento registrado.")
        cantidad = self._entero_no_negativo(cantidad, "La cantidad")
        if cantidad == 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        paciente_codigo = str(paciente_codigo or "").strip()
        paciente = next(
            (p for p in self._pacientes if p.codigo.casefold() == paciente_codigo.casefold()),
            None,
        )
        if paciente is None:
            raise ValueError("Ingresa el código de un paciente registrado.")
        vendido_por = str(vendido_por or "").strip()
        if not vendido_por:
            raise ValueError("No se pudo identificar a quien registra la venta.")
        return self._repositorio.registrar_venta_medicamento(
            medicamento_id,
            cantidad,
            paciente.codigo,
            vendido_por,
            datetime.now().isoformat(timespec="seconds"),
        )

    def obtener_ventas_medicamentos(self, limite=100):
        return self._repositorio.obtener_ventas_medicamentos(limite)

    def obtener_estadisticas_medicamentos(self):
        return self._repositorio.obtener_estadisticas_medicamentos(
            date.today().isoformat()
        )

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
                    cita.estado == "Reprogramada",
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
            "atenciones": atenciones,
            "ventas_medicamentos": (
                self._repositorio.obtener_ventas_paciente(paciente.codigo)
                if hasattr(self._repositorio, "obtener_ventas_paciente")
                else []
            ),
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

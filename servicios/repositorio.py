import sqlite3

from servicios.gestor_bd import GestorBaseDatos
from servicios.seguridad import SeguridadDatos


class RepositorioSalud:

    def __init__(
        self,
        ruta_bd="datos/salud.db"
    ):

        self._ruta_bd = ruta_bd

        self._gestor_bd = (
            GestorBaseDatos()
        )

        self._conexion = (
            self._gestor_bd.conectar(
                ruta_bd
            )
        )

        self._conexion.execute("PRAGMA foreign_keys = ON")
        self._crear_tablas()
        self._migrar_base_datos()

    # =========================================================
    # CREAR TABLAS
    # =========================================================

    def _crear_tablas(self):

        cursor = self._conexion.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pacientes (
                codigo TEXT PRIMARY KEY,
                dni TEXT,
                dni_hash TEXT,
                dni_salt TEXT,
                nombre TEXT NOT NULL,
                edad INTEGER NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS personal (
                codigo_profesional TEXT PRIMARY KEY,
                dni TEXT,
                dni_hash TEXT,
                dni_salt TEXT,
                nombre TEXT NOT NULL,
                edad INTEGER NOT NULL,
                especialidad TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS citas (
                codigo TEXT PRIMARY KEY,
                paciente_codigo TEXT NOT NULL,
                profesional_codigo TEXT NOT NULL,
                fecha TEXT NOT NULL,
                motivo TEXT NOT NULL,
                estado TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS atenciones (
                codigo TEXT PRIMARY KEY,
                cita_codigo TEXT NOT NULL,
                diagnostico TEXT NOT NULL,
                estado TEXT NOT NULL
            )
            """
        )

        self._conexion.commit()

    # =========================================================
    # MIGRACIÓN
    # =========================================================

    def _migrar_base_datos(self):

        cursor = self._conexion.cursor()

        # -----------------------------------------------------
        # PACIENTES
        # -----------------------------------------------------

        columnas_pacientes = [
            fila[1]
            for fila in cursor.execute(
                "PRAGMA table_info(pacientes)"
            ).fetchall()
        ]

        if "dni" not in columnas_pacientes:

            cursor.execute(
                """
                ALTER TABLE pacientes
                ADD COLUMN dni TEXT
                """
            )

        if "dni_hash" not in columnas_pacientes:

            cursor.execute(
                """
                ALTER TABLE pacientes
                ADD COLUMN dni_hash TEXT
                """
            )

        if "dni_salt" not in columnas_pacientes:

            cursor.execute(
                """
                ALTER TABLE pacientes
                ADD COLUMN dni_salt TEXT
                """
            )

        # -----------------------------------------------------
        # PERSONAL
        # -----------------------------------------------------

        columnas_personal = [
            fila[1]
            for fila in cursor.execute(
                "PRAGMA table_info(personal)"
            ).fetchall()
        ]

        if "dni" not in columnas_personal:

            cursor.execute(
                """
                ALTER TABLE personal
                ADD COLUMN dni TEXT
                """
            )

        if "dni_hash" not in columnas_personal:

            cursor.execute(
                """
                ALTER TABLE personal
                ADD COLUMN dni_hash TEXT
                """
            )

        if "dni_salt" not in columnas_personal:

            cursor.execute(
                """
                ALTER TABLE personal
                ADD COLUMN dni_salt TEXT
                """
            )

        # -----------------------------------------------------
        # MIGRACIÓN DE DNI DE PACIENTES
        # -----------------------------------------------------

        pacientes = cursor.execute(
            """
            SELECT
                codigo,
                dni
            FROM pacientes
            WHERE dni IS NOT NULL
              AND dni != ''
              AND (
                    dni_hash IS NULL
                    OR dni_salt IS NULL
                  )
            """
        ).fetchall()

        for codigo, dni in pacientes:

            sal, resumen = (
                SeguridadDatos.proteger(
                    str(dni)
                )
            )

            cursor.execute(
                """
                UPDATE pacientes
                SET
                    dni = NULL,
                    dni_hash = ?,
                    dni_salt = ?
                WHERE codigo = ?
                """,
                (
                    resumen,
                    sal,
                    codigo
                )
            )

        # Limpiar cualquier copia antigua del DNI en texto plano cuando
        # ya existe una huella protegida. La columna histórica se mantiene
        # únicamente por compatibilidad con bases de datos anteriores.
        cursor.execute(
            """
            UPDATE pacientes
            SET dni = NULL
            WHERE dni_hash IS NOT NULL
              AND dni_salt IS NOT NULL
              AND dni IS NOT NULL
            """
        )

        # -----------------------------------------------------
        # MIGRACIÓN DE DNI DE PERSONAL
        # -----------------------------------------------------

        profesionales = cursor.execute(
            """
            SELECT
                codigo_profesional,
                dni
            FROM personal
            WHERE dni IS NOT NULL
              AND dni != ''
              AND (
                    dni_hash IS NULL
                    OR dni_salt IS NULL
                  )
            """
        ).fetchall()

        for codigo, dni in profesionales:

            sal, resumen = (
                SeguridadDatos.proteger(
                    str(dni)
                )
            )

            cursor.execute(
                """
                UPDATE personal
                SET
                    dni = NULL,
                    dni_hash = ?,
                    dni_salt = ?
                WHERE codigo_profesional = ?
                """,
                (
                    resumen,
                    sal,
                    codigo
                )
            )

        cursor.execute(
            """
            UPDATE personal
            SET dni = NULL
            WHERE dni_hash IS NOT NULL
              AND dni_salt IS NOT NULL
              AND dni IS NOT NULL
            """
        )

        # -----------------------------------------------------
        # ESTADOS
        # -----------------------------------------------------

        cursor.execute(
            """
            UPDATE citas
            SET estado = 'Reprogramar'
            WHERE estado = 'Reprogramada'
            """
        )

        cursor.execute(
            """
            UPDATE citas
            SET estado = 'Pendiente'
            WHERE estado = 'Cancelada'
            """
        )

        self._conexion.commit()

    # =========================================================
    # PACIENTES
    # =========================================================

    def guardar_paciente(
        self,
        paciente
    ):

        try:

            with self._conexion:

                self._conexion.execute(
                    """
                    INSERT INTO pacientes
                    (
                        codigo,
                        dni_hash,
                        dni_salt,
                        nombre,
                        edad
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        paciente.codigo,
                        paciente.dni_hash,
                        paciente.dni_salt,
                        paciente.nombre,
                        paciente.edad
                    )
                )

        except sqlite3.IntegrityError as error:

            raise ValueError(
                "No se pudo guardar el paciente. "
                "El código puede estar duplicado."
            ) from error

    def obtener_pacientes(self):

        cursor = self._conexion.cursor()

        return cursor.execute(
            """
            SELECT
                codigo,
                dni_hash,
                dni_salt,
                nombre,
                edad
            FROM pacientes
            ORDER BY codigo
            """
        ).fetchall()

    def existe_dni_paciente(
        self,
        dni
    ):

        filas = self._conexion.execute(
            """
            SELECT
                dni_hash,
                dni_salt
            FROM pacientes
            WHERE dni_hash IS NOT NULL
              AND dni_salt IS NOT NULL
            """
        ).fetchall()

        return any(
            SeguridadDatos.verificar(
                dni,
                sal,
                resumen
            )
            for (
                resumen,
                sal
            ) in filas
        )

    # =========================================================
    # PERSONAL
    # =========================================================

    def guardar_personal(
        self,
        profesional
    ):

        try:

            with self._conexion:

                self._conexion.execute(
                    """
                    INSERT INTO personal
                    (
                        codigo_profesional,
                        dni_hash,
                        dni_salt,
                        nombre,
                        edad,
                        especialidad
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        profesional.codigo_profesional,
                        profesional.dni_hash,
                        profesional.dni_salt,
                        profesional.nombre,
                        profesional.edad,
                        profesional.especialidad
                    )
                )

        except sqlite3.IntegrityError as error:

            raise ValueError(
                "No se pudo guardar el profesional. "
                "El código puede estar duplicado."
            ) from error

    def obtener_personal(self):

        cursor = self._conexion.cursor()

        return cursor.execute(
            """
            SELECT
                codigo_profesional,
                dni_hash,
                dni_salt,
                nombre,
                edad,
                especialidad
            FROM personal
            ORDER BY codigo_profesional
            """
        ).fetchall()

    def existe_dni_personal(
        self,
        dni
    ):

        filas = self._conexion.execute(
            """
            SELECT
                dni_hash,
                dni_salt
            FROM personal
            WHERE dni_hash IS NOT NULL
              AND dni_salt IS NOT NULL
            """
        ).fetchall()

        return any(
            SeguridadDatos.verificar(
                dni,
                sal,
                resumen
            )
            for (
                resumen,
                sal
            ) in filas
        )

    # =========================================================
    # CITAS
    # =========================================================

    def guardar_cita(
        self,
        cita
    ):

        try:

            with self._conexion:

                self._conexion.execute(
                    """
                    INSERT INTO citas
                    (
                        codigo,
                        paciente_codigo,
                        profesional_codigo,
                        fecha,
                        motivo,
                        estado
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        cita.codigo,
                        cita.paciente.codigo,
                        cita.profesional.codigo_profesional,
                        cita.fecha,
                        cita.motivo,
                        cita.estado
                    )
                )

        except sqlite3.IntegrityError as error:

            raise ValueError(
                "No se pudo guardar la cita."
            ) from error

    def obtener_citas(self):

        cursor = self._conexion.cursor()

        return cursor.execute(
            """
            SELECT
                codigo,
                paciente_codigo,
                profesional_codigo,
                fecha,
                motivo,
                estado
            FROM citas
            ORDER BY codigo
            """
        ).fetchall()

    def actualizar_estado_cita(
        self,
        codigo_cita,
        nuevo_estado
    ):

        with self._conexion:

            self._conexion.execute(
                """
                UPDATE citas
                SET estado = ?
                WHERE codigo = ?
                """,
                (
                    nuevo_estado,
                    codigo_cita
                )
            )

    # =========================================================
    # ATENCIONES
    # =========================================================

    def guardar_atencion(
        self,
        atencion
    ):

        try:

            with self._conexion:

                self._conexion.execute(
                    """
                    INSERT INTO atenciones
                    (
                        codigo,
                        cita_codigo,
                        diagnostico,
                        estado
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        atencion.codigo,
                        atencion.cita.codigo,
                        atencion.diagnostico,
                        atencion.estado
                    )
                )

        except sqlite3.IntegrityError as error:

            raise ValueError(
                "No se pudo guardar la atención."
            ) from error

    def obtener_atenciones(self):

        cursor = self._conexion.cursor()

        return cursor.execute(
            """
            SELECT
                codigo,
                cita_codigo,
                diagnostico,
                estado
            FROM atenciones
            ORDER BY codigo
            """
        ).fetchall()

    def actualizar_estado_atencion(
        self,
        codigo_atencion,
        nuevo_estado
    ):

        with self._conexion:

            self._conexion.execute(
                """
                UPDATE atenciones
                SET estado = ?
                WHERE codigo = ?
                """,
                (
                    nuevo_estado,
                    codigo_atencion
                )
            )

    # =========================================================
    # CERRAR
    # =========================================================

    def cerrar(self):

        self._gestor_bd.cerrar(
            self._ruta_bd
        )
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
                hora TEXT NOT NULL DEFAULT '09:00',
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
                estado TEXT NOT NULL,
                profesional_derivado_codigo TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recetas_medicas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                atencion_codigo TEXT NOT NULL,
                medicamento TEXT NOT NULL,
                dias INTEGER NOT NULL CHECK (dias > 0),
                cada_cuanto TEXT NOT NULL,
                FOREIGN KEY (atencion_codigo) REFERENCES atenciones(codigo) ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cuentas_acceso (
                usuario TEXT PRIMARY KEY COLLATE NOCASE,
                rol TEXT NOT NULL CHECK (
                    rol IN (
                        'paciente',
                        'administrativa',
                        'profesional',
                        'enfermeria'
                    )
                ),
                codigo_referencia TEXT,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                activo INTEGER NOT NULL DEFAULT 1,
                creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (rol, codigo_referencia)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS medicamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                principio_activo TEXT NOT NULL DEFAULT '',
                presentacion TEXT NOT NULL DEFAULT '',
                lote TEXT NOT NULL,
                vencimiento TEXT NOT NULL,
                stock INTEGER NOT NULL CHECK (stock >= 0),
                stock_minimo INTEGER NOT NULL DEFAULT 0 CHECK (stock_minimo >= 0),
                precio_venta REAL NOT NULL CHECK (precio_venta >= 0),
                registrado_por TEXT NOT NULL,
                creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (nombre COLLATE NOCASE, lote COLLATE NOCASE)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ventas_medicamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicamento_id INTEGER NOT NULL,
                medicamento_nombre TEXT NOT NULL,
                lote TEXT NOT NULL,
                cantidad INTEGER NOT NULL CHECK (cantidad > 0),
                precio_unitario REAL NOT NULL CHECK (precio_unitario >= 0),
                total REAL NOT NULL CHECK (total >= 0),
                cliente TEXT NOT NULL DEFAULT '',
                paciente_codigo TEXT NOT NULL,
                vendido_por TEXT NOT NULL,
                vendido_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id),
                FOREIGN KEY (paciente_codigo) REFERENCES pacientes(codigo)
            )
            """
        )
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS una_cuenta_administrativa
            ON cuentas_acceso (rol)
            WHERE rol = 'administrativa'
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

        columnas_ventas = [
            fila[1]
            for fila in cursor.execute(
                "PRAGMA table_info(ventas_medicamentos)"
            ).fetchall()
        ]
        if "paciente_codigo" not in columnas_ventas:
            cursor.execute(
                "ALTER TABLE ventas_medicamentos ADD COLUMN paciente_codigo TEXT"
            )
        # Preserve older rows when the former free-text client field already
        # contains an exact patient code; names are never guessed or matched.
        cursor.execute(
            """
            UPDATE ventas_medicamentos
            SET paciente_codigo = (
                SELECT codigo FROM pacientes
                WHERE codigo = ventas_medicamentos.cliente COLLATE NOCASE
            )
            WHERE paciente_codigo IS NULL
              AND EXISTS (
                SELECT 1 FROM pacientes
                WHERE codigo = ventas_medicamentos.cliente COLLATE NOCASE
              )
            """
        )

        columnas_citas = [
            fila[1]
            for fila in cursor.execute(
                "PRAGMA table_info(citas)"
            ).fetchall()
        ]

        if "hora" not in columnas_citas:
            cursor.execute(
                "ALTER TABLE citas ADD COLUMN hora TEXT NOT NULL DEFAULT '09:00'"
            )

        columnas_atenciones = [
            fila[1]
            for fila in cursor.execute(
                "PRAGMA table_info(atenciones)"
            ).fetchall()
        ]
        if "profesional_derivado_codigo" not in columnas_atenciones:
            cursor.execute(
                "ALTER TABLE atenciones ADD COLUMN profesional_derivado_codigo TEXT"
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
            SET estado = 'Reprogramada'
            WHERE estado IN ('Reprogramar', 'Reprogramada')
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

    def eliminar_paciente(self, codigo):
        """Deshace el alta de un paciente recién creado (sin citas)."""
        with self._conexion:
            self._conexion.execute(
                "DELETE FROM pacientes WHERE codigo = ?",
                (codigo,),
            )

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

    def guardar_personal_con_cuenta(
        self,
        profesional,
        usuario,
        rol,
        password_hash,
        password_salt,
    ):
        """Guarda el registro nuevo y su cuenta dentro de una sola transacción."""
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
                        profesional.especialidad,
                    ),
                )
                self._conexion.execute(
                    """
                    INSERT INTO cuentas_acceso
                    (usuario, rol, codigo_referencia, password_hash, password_salt)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        usuario,
                        rol,
                        profesional.codigo_profesional,
                        password_hash,
                        password_salt,
                    ),
                )
        except sqlite3.IntegrityError as error:
            raise ValueError(
                "No se pudo crear la cuenta. El usuario, el DNI o el código "
                "ya están registrados."
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

    def obtener_datos_paciente_acceso(self, codigo):
        """Devuelve solo los datos necesarios para comprobar la identidad."""
        return self._conexion.execute(
            """
            SELECT codigo, dni_hash, dni_salt
            FROM pacientes
            WHERE codigo = ? COLLATE NOCASE
            """,
            (codigo.strip(),),
        ).fetchone()

    def obtener_datos_personal_acceso(self, codigo):
        """Devuelve solo los datos necesarios para comprobar la identidad."""
        return self._conexion.execute(
            """
            SELECT codigo_profesional, dni_hash, dni_salt, especialidad
            FROM personal
            WHERE codigo_profesional = ? COLLATE NOCASE
            """,
            (codigo.strip(),),
        ).fetchone()

    def obtener_datos_personal_por_dni(self, dni):
        """Busca el registro de personal verificando el DNI protegido."""
        filas = self._conexion.execute(
            """
            SELECT codigo_profesional, dni_hash, dni_salt, especialidad
            FROM personal
            WHERE dni_hash IS NOT NULL AND dni_salt IS NOT NULL
            """
        ).fetchall()
        for codigo, resumen, sal, especialidad in filas:
            if SeguridadDatos.verificar(dni, sal, resumen):
                return codigo, resumen, sal, especialidad
        return None

    def obtener_cuenta_acceso(self, usuario):
        return self._conexion.execute(
            """
            SELECT usuario, rol, codigo_referencia, password_hash, password_salt, activo
            FROM cuentas_acceso
            WHERE usuario = ? COLLATE NOCASE
            """,
            (usuario.strip(),),
        ).fetchone()

    def contar_cuentas_acceso(self, rol):
        fila = self._conexion.execute(
            "SELECT COUNT(*) FROM cuentas_acceso WHERE rol = ?",
            (rol,),
        ).fetchone()
        return fila[0]

    def guardar_cuenta_acceso(
        self,
        usuario,
        rol,
        codigo_referencia,
        password_hash,
        password_salt,
        solo_primera_administrativa=False,
    ):
        """Guarda una cuenta y permite crear solo una cuenta administrativa inicial."""
        try:
            with self._conexion:
                if (
                    solo_primera_administrativa
                    and self.contar_cuentas_acceso("administrativa")
                ):
                    raise ValueError(
                        "Ya existe una cuenta administrativa configurada."
                    )
                self._conexion.execute(
                    """
                    INSERT INTO cuentas_acceso
                        (usuario, rol, codigo_referencia, password_hash, password_salt)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        usuario,
                        rol,
                        codigo_referencia,
                        password_hash,
                        password_salt,
                    ),
                )
        except sqlite3.IntegrityError as error:
            raise ValueError(
                "El usuario ya existe o ya tiene una cuenta para este rol."
            ) from error

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
                        hora,
                        motivo,
                        estado
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        cita.codigo,
                        cita.paciente.codigo,
                        cita.profesional.codigo_profesional,
                        cita.fecha,
                        cita.hora,
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
                hora,
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

    def actualizar_agenda_cita(
        self,
        codigo_cita,
        fecha,
        hora,
        estado,
    ):
        with self._conexion:
            self._conexion.execute(
                "UPDATE citas SET fecha = ?, hora = ?, estado = ? WHERE codigo = ?",
                (fecha, hora, estado, codigo_cita),
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
                        estado,
                        profesional_derivado_codigo
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        atencion.codigo,
                        atencion.cita.codigo,
                        atencion.diagnostico,
                        atencion.estado,
                        (
                            atencion.profesional_derivado.codigo_profesional
                            if atencion.profesional_derivado
                            else None
                        ),
                    )
                )
                self._guardar_recetas_en_transaccion(atencion.codigo, atencion.recetas)

        except sqlite3.IntegrityError as error:

            raise ValueError(
                "No se pudo guardar la atención."
            ) from error

    def _guardar_recetas_en_transaccion(self, codigo_atencion, recetas):
        self._conexion.execute(
            "DELETE FROM recetas_medicas WHERE atencion_codigo = ?",
            (codigo_atencion,),
        )
        self._conexion.executemany(
            """
            INSERT INTO recetas_medicas (atencion_codigo, medicamento, dias, cada_cuanto)
            VALUES (?, ?, ?, ?)
            """,
            [
                (codigo_atencion, receta.medicamento, receta.dias, receta.cada_cuanto)
                for receta in recetas
            ],
        )

    def guardar_recetas_atencion(self, codigo_atencion, recetas):
        try:
            with self._conexion:
                existe = self._conexion.execute(
                    "SELECT 1 FROM atenciones WHERE codigo = ?",
                    (codigo_atencion,),
                ).fetchone()
                if existe is None:
                    raise ValueError("No se encontró la atención para guardar sus recetas.")
                self._guardar_recetas_en_transaccion(codigo_atencion, recetas)
        except sqlite3.IntegrityError as error:
            raise ValueError("No se pudieron guardar las recetas médicas.") from error

    def obtener_recetas_atencion(self, codigo_atencion):
        return self._conexion.execute(
            """
            SELECT medicamento, dias, cada_cuanto
            FROM recetas_medicas
            WHERE atencion_codigo = ?
            ORDER BY id
            """,
            (codigo_atencion,),
        ).fetchall()

    def obtener_atenciones(self):

        cursor = self._conexion.cursor()

        return cursor.execute(
            """
            SELECT
                codigo,
                cita_codigo,
                diagnostico,
                estado,
                profesional_derivado_codigo
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

    def actualizar_diagnostico_atencion(
        self,
        codigo_atencion,
        diagnostico,
        profesional_derivado_codigo=None,
    ):
        with self._conexion:
            self._conexion.execute(
                """
                UPDATE atenciones
                SET diagnostico = ?, profesional_derivado_codigo = ?
                WHERE codigo = ?
                """,
                (diagnostico, profesional_derivado_codigo, codigo_atencion),
            )

    # =========================================================
    # MEDICAMENTOS Y VENTAS
    # =========================================================

    def guardar_medicamento(
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
    ):
        try:
            with self._conexion:
                cursor = self._conexion.execute(
                    """
                    INSERT INTO medicamentos (
                        nombre, principio_activo, presentacion, lote,
                        vencimiento, stock, stock_minimo, precio_venta,
                        registrado_por
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        nombre,
                        principio_activo,
                        presentacion,
                        lote,
                        vencimiento,
                        stock,
                        stock_minimo,
                        precio_venta,
                        registrado_por,
                    ),
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError as error:
            raise ValueError(
                "Ya existe un registro con ese medicamento y lote."
            ) from error

    def obtener_medicamentos(self):
        return self._conexion.execute(
            """
            SELECT id, nombre, principio_activo, presentacion, lote,
                   vencimiento, stock, stock_minimo, precio_venta,
                   registrado_por, creado_en
            FROM medicamentos
            ORDER BY nombre COLLATE NOCASE, vencimiento, lote
            """
        ).fetchall()

    def obtener_medicamentos_disponibles(self, fecha_actual):
        return self._conexion.execute(
            """
            SELECT id, nombre, principio_activo, presentacion, lote,
                   vencimiento, stock, stock_minimo, precio_venta,
                   registrado_por, creado_en
            FROM medicamentos
            WHERE stock > 0 AND vencimiento >= ?
            ORDER BY nombre COLLATE NOCASE, vencimiento, lote
            """,
            (fecha_actual,),
        ).fetchall()

    def registrar_venta_medicamento(
        self,
        medicamento_id,
        cantidad,
        paciente_codigo,
        vendido_por,
        fecha_hora,
    ):
        try:
            with self._conexion:
                medicamento = self._conexion.execute(
                    """
                    SELECT nombre, lote, vencimiento, stock, precio_venta
                    FROM medicamentos WHERE id = ?
                    """,
                    (medicamento_id,),
                ).fetchone()
                if medicamento is None:
                    raise ValueError("El medicamento seleccionado ya no existe.")
                nombre, lote, vencimiento, stock, precio = medicamento
                if vencimiento < fecha_hora[:10]:
                    raise ValueError("No se puede vender un medicamento vencido.")
                if cantidad > stock:
                    raise ValueError(
                        f"Stock insuficiente. Solo quedan {stock} unidad(es)."
                    )
                total = round(float(precio) * cantidad, 2)
                actualizacion = self._conexion.execute(
                    """
                    UPDATE medicamentos
                    SET stock = stock - ?
                    WHERE id = ? AND stock >= ? AND vencimiento >= ?
                    """,
                    (cantidad, medicamento_id, cantidad, fecha_hora[:10]),
                )
                if actualizacion.rowcount != 1:
                    stock_actual = self._conexion.execute(
                        "SELECT stock FROM medicamentos WHERE id = ?",
                        (medicamento_id,),
                    ).fetchone()
                    if stock_actual is None:
                        raise ValueError("El medicamento seleccionado ya no existe.")
                    raise ValueError(
                        f"Stock insuficiente. Solo quedan {stock_actual[0]} unidad(es)."
                    )
                cursor = self._conexion.execute(
                    """
                    INSERT INTO ventas_medicamentos (
                        medicamento_id, medicamento_nombre, lote, cantidad,
                        precio_unitario, total, cliente, paciente_codigo,
                        vendido_por, vendido_en
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        medicamento_id,
                        nombre,
                        lote,
                        cantidad,
                        precio,
                        total,
                        paciente_codigo,
                        paciente_codigo,
                        vendido_por,
                        fecha_hora,
                    ),
                )
                return cursor.lastrowid, total, stock - cantidad
        except sqlite3.IntegrityError as error:
            raise ValueError("No se pudo guardar la venta.") from error

    def obtener_ventas_medicamentos(self, limite=100):
        return self._conexion.execute(
            """
            SELECT id, medicamento_nombre, lote, cantidad, precio_unitario,
                   total, cliente, vendido_por, vendido_en, paciente_codigo
            FROM ventas_medicamentos
            ORDER BY datetime(vendido_en) DESC, id DESC
            LIMIT ?
            """,
            (int(limite),),
        ).fetchall()

    def obtener_ventas_paciente(self, codigo_paciente):
        return self._conexion.execute(
            """
            SELECT id, medicamento_nombre, lote, cantidad, precio_unitario,
                   total, paciente_codigo, vendido_por, vendido_en
            FROM ventas_medicamentos
            WHERE paciente_codigo = ? COLLATE NOCASE
            ORDER BY datetime(vendido_en) DESC, id DESC
            """,
            (codigo_paciente,),
        ).fetchall()

    def obtener_estadisticas_medicamentos(self, fecha_actual):
        disponibles = self._conexion.execute(
            """
            SELECT COUNT(*), COALESCE(SUM(stock), 0)
            FROM medicamentos
            WHERE stock > 0 AND vencimiento >= ?
            """,
            (fecha_actual,),
        ).fetchone()
        ventas = self._conexion.execute(
            """
            SELECT COUNT(*), COALESCE(SUM(total), 0)
            FROM ventas_medicamentos
            WHERE substr(vendido_en, 1, 10) = ?
            """,
            (fecha_actual,),
        ).fetchone()
        return {
            "lotes_disponibles": disponibles[0],
            "unidades_disponibles": disponibles[1],
            "ventas_hoy": ventas[0],
            "monto_ventas_hoy": ventas[1],
        }

    # =========================================================
    # CERRAR
    # =========================================================

    def cerrar(self):

        self._gestor_bd.cerrar(
            self._ruta_bd
        )

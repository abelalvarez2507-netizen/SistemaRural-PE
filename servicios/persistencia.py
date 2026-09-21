import sqlite3
from servicios.seguridad_datos import SeguridadDatos


class Persistencia:
    """Persistencia SQLite con restricciones y protección del DNI."""

    def __init__(self, archivo="sistema_rural.db"):
        self.conexion = sqlite3.connect(archivo)
        self.crear_tablas()

    def crear_tablas(self):
        cursor = self.conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pacientes (
                codigo TEXT PRIMARY KEY,
                dni_protegido TEXT NOT NULL,
                nombre TEXT NOT NULL,
                edad INTEGER NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personal (
                codigo TEXT PRIMARY KEY,
                dni_protegido TEXT NOT NULL,
                nombre TEXT NOT NULL,
                edad INTEGER NOT NULL,
                especialidad TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS citas (
                codigo TEXT PRIMARY KEY,
                paciente_codigo TEXT NOT NULL,
                profesional_codigo TEXT NOT NULL,
                fecha TEXT NOT NULL,
                motivo TEXT NOT NULL
            )
        """)
        self.conexion.commit()

    def guardar_paciente(self, paciente):
        try:
            self.conexion.execute(
                "INSERT INTO pacientes VALUES (?, ?, ?, ?)",
                (paciente.codigo, SeguridadDatos.proteger_dni(paciente.dni), paciente.nombre, paciente.edad)
            )
            self.conexion.commit()
        except sqlite3.IntegrityError as error:
            self.conexion.rollback()
            raise ValueError(f"No se pudo guardar el paciente: {error}") from error

    def guardar_personal(self, profesional):
        try:
            self.conexion.execute(
                "INSERT INTO personal VALUES (?, ?, ?, ?, ?)",
                (profesional.codigo_profesional, SeguridadDatos.proteger_dni(profesional.dni),
                 profesional.nombre, profesional.edad, profesional.especialidad)
            )
            self.conexion.commit()
        except sqlite3.IntegrityError as error:
            self.conexion.rollback()
            raise ValueError(f"No se pudo guardar el profesional: {error}") from error

    def guardar_cita(self, cita):
        try:
            self.conexion.execute(
                "INSERT INTO citas VALUES (?, ?, ?, ?, ?)",
                (cita.codigo, cita.paciente.codigo, cita.profesional.codigo_profesional,
                 cita.fecha, cita.motivo)
            )
            self.conexion.commit()
        except sqlite3.IntegrityError as error:
            self.conexion.rollback()
            raise ValueError(f"No se pudo guardar la cita: {error}") from error

    def contar_pacientes(self):
        return self.conexion.execute("SELECT COUNT(*) FROM pacientes").fetchone()[0]

    def verificar_dni_paciente(self, codigo, dni):
        fila = self.conexion.execute(
            "SELECT dni_protegido FROM pacientes WHERE codigo = ?", (codigo,)
        ).fetchone()
        return fila is not None and SeguridadDatos.verificar_dni(dni, fila[0])

    def cerrar(self):
        self.conexion.close()

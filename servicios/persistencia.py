import sqlite3

class Persistencia:
    """Primera aproximación a SQLite; contiene errores que se corregirán en V4.1."""
    def __init__(self, archivo="sistema_rural.db"):
        self.conexion = sqlite3.connect(archivo)
        self.crear_tablas()

    def crear_tablas(self):
        cursor = self.conexion.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS pacientes (codigo TEXT, dni TEXT, nombre TEXT, edad INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS personal (codigo TEXT, dni TEXT, nombre TEXT, edad INTEGER, especialidad TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS citas (codigo TEXT, paciente_codigo TEXT, profesional_codigo TEXT, fecha TEXT, motivo TEXT)")
        self.conexion.commit()

    def guardar_paciente(self, paciente):
        # Error de principiante: no se comprueba si el código ya existe.
        self.conexion.execute(
            "INSERT INTO pacientes VALUES (?, ?, ?, ?)",
            (paciente.codigo, paciente.dni, paciente.nombre, paciente.edad)
        )
        self.conexion.commit()

    def guardar_personal(self, profesional):
        # Error de principiante: se permite duplicar códigos.
        self.conexion.execute(
            "INSERT INTO personal VALUES (?, ?, ?, ?, ?)",
            (profesional.codigo_profesional, profesional.dni, profesional.nombre,
             profesional.edad, profesional.especialidad)
        )
        self.conexion.commit()

    def guardar_cita(self, cita):
        self.conexion.execute(
            "INSERT INTO citas VALUES (?, ?, ?, ?, ?)",
            (cita.codigo, cita.paciente.codigo, cita.profesional.codigo_profesional,
             cita.fecha, cita.motivo)
        )
        self.conexion.commit()

    def contar_pacientes(self):
        return self.conexion.execute("SELECT COUNT(*) FROM pacientes").fetchone()[0]

    def cerrar(self):
        self.conexion.close()

import os
import sqlite3


class GestorBaseDatos:
    """
    Singleton responsable de administrar las conexiones
    a las bases de datos SQLite del sistema.

    Solo existe una instancia de esta clase durante
    la ejecución de la aplicación.
    """

    _instancia = None

    def __new__(cls, *args, **kwargs):

        if cls._instancia is None:

            cls._instancia = super().__new__(
                cls
            )

            cls._instancia._conexiones = {}

        return cls._instancia

    def conectar(
        self,
        ruta_bd="datos/salud.db"
    ):
        """
        Devuelve una única conexión para cada ruta
        de base de datos.
        """

        ruta_absoluta = os.path.abspath(
            ruta_bd
        )

        carpeta = os.path.dirname(
            ruta_absoluta
        )

        if carpeta:
            os.makedirs(
                carpeta,
                exist_ok=True
            )

        if ruta_absoluta not in self._conexiones:

            self._conexiones[
                ruta_absoluta
            ] = sqlite3.connect(
                ruta_absoluta
            )

        return self._conexiones[
            ruta_absoluta
        ]

    def cerrar(
        self,
        ruta_bd="datos/salud.db"
    ):
        """
        Cierra la conexión correspondiente.
        """

        ruta_absoluta = os.path.abspath(
            ruta_bd
        )

        conexion = self._conexiones.pop(
            ruta_absoluta,
            None
        )

        if conexion is not None:

            conexion.close()

    def cerrar_todas(self):
        """
        Cierra todas las conexiones administradas
        por el Singleton.
        """

        for conexion in self._conexiones.values():

            conexion.close()

        self._conexiones.clear()
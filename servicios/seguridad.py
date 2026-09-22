import hashlib
import hmac
import os


class SeguridadDatos:
    """
    Gestiona la protección de datos personales.

    El DNI no se almacena en texto plano.
    Se genera una huella derivada mediante PBKDF2-HMAC-SHA256
    usando una sal aleatoria.
    """

    ITERACIONES = 120000
    LONGITUD_SAL = 16
    LONGITUD_HASH = 32

    @staticmethod
    def generar_sal():
        """Genera una sal aleatoria para proteger un dato."""
        return os.urandom(
            SeguridadDatos.LONGITUD_SAL
        )

    @staticmethod
    def generar_hash(valor, sal):
        """
        Genera una huella segura para el valor recibido.
        """

        return hashlib.pbkdf2_hmac(
            "sha256",
            valor.encode("utf-8"),
            sal,
            SeguridadDatos.ITERACIONES,
            dklen=SeguridadDatos.LONGITUD_HASH
        )

    @staticmethod
    def proteger(valor):
        """
        Protege un valor y devuelve:

        - sal en hexadecimal
        - hash en hexadecimal
        """

        sal = SeguridadDatos.generar_sal()

        resumen = SeguridadDatos.generar_hash(
            valor,
            sal
        )

        return (
            sal.hex(),
            resumen.hex()
        )

    @staticmethod
    def verificar(
        valor,
        sal_hex,
        hash_hex
    ):
        """
        Verifica si el valor recibido coincide
        con el hash almacenado.
        """

        try:

            sal = bytes.fromhex(
                sal_hex
            )

            esperado = bytes.fromhex(
                hash_hex
            )

        except (
            ValueError,
            TypeError
        ):

            return False

        obtenido = SeguridadDatos.generar_hash(
            valor,
            sal
        )

        return hmac.compare_digest(
            obtenido,
            esperado
        )
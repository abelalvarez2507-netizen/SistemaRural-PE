import hashlib
import hmac
import os


class SeguridadDatos:
    """Protección básica de DNI mediante PBKDF2-HMAC-SHA256."""

    ITERACIONES = 100_000

    @staticmethod
    def proteger_dni(dni):
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256", str(dni).encode("utf-8"), salt, SeguridadDatos.ITERACIONES
        )
        return f"{salt.hex()}:{digest.hex()}"

    @staticmethod
    def verificar_dni(dni, valor_protegido):
        try:
            salt_hex, digest_hex = valor_protegido.split(":", 1)
            salt = bytes.fromhex(salt_hex)
            esperado = bytes.fromhex(digest_hex)
        except (ValueError, TypeError):
            return False

        actual = hashlib.pbkdf2_hmac(
            "sha256", str(dni).encode("utf-8"), salt, SeguridadDatos.ITERACIONES
        )
        return hmac.compare_digest(actual, esperado)

    @staticmethod
    def enmascarar_dni(dni):
        dni = str(dni)
        return "*" * max(0, len(dni) - 2) + dni[-2:]

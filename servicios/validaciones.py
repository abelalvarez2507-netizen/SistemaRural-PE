"""Validaciones y normalizaciones compartidas del dominio SaluPro."""

import re
import unicodedata
from datetime import datetime


PATRON_CODIGO = re.compile(r"^[A-Za-z0-9_-]{2,}$")


def texto_requerido(valor, campo, maximo=200):
    """Normaliza un texto obligatorio y limita su longitud."""
    if valor is None:
        raise ValueError(f"{campo} es obligatorio.")

    texto = str(valor).strip()

    if not texto:
        raise ValueError(f"{campo} no puede estar vacío.")

    if len(texto) > maximo:
        raise ValueError(
            f"{campo} no puede superar los {maximo} caracteres."
        )

    return texto


def validar_nombre(valor):
    """Valida nombres formados únicamente por letras y espacios."""
    nombre = unicodedata.normalize(
        "NFC",
        texto_requerido(valor, "El nombre", 100),
    )

    if not all(caracter.isalpha() or caracter == " " for caracter in nombre):
        raise ValueError(
            "El nombre solo puede contener letras, tildes, ñ y espacios."
        )

    return nombre


def validar_nombre_en_edicion(valor):
    """Permite escribir nombres con letras, espacios y tildes en curso."""
    marcas_tilde = {"\u0300", "\u0301", "\u0303", "\u0308"}
    anterior_es_letra = False

    for caracter in valor:
        if caracter.isalpha():
            anterior_es_letra = True
        elif caracter == " ":
            anterior_es_letra = False
        elif caracter in marcas_tilde and anterior_es_letra:
            continue
        else:
            return False

    return True


def validar_edad(valor):
    """Valida la edad en el rango razonable del dominio."""
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError("La edad debe ser un número entero.")

    if valor < 0 or valor > 120:
        raise ValueError("La edad debe estar entre 0 y 120 años.")

    return valor


def validar_dni(valor):
    """Valida un DNI de exactamente ocho dígitos."""
    if valor is None:
        raise ValueError("El DNI es obligatorio.")

    dni = str(valor).strip()

    if not dni.isdigit():
        raise ValueError("El DNI debe contener únicamente números.")

    if len(dni) != 8:
        raise ValueError("El DNI debe contener exactamente 8 dígitos.")

    return dni


def validar_codigo(valor, campo="El código"):
    """Valida códigos internos sin limitar la cantidad de dígitos."""
    if valor is None:
        raise ValueError(f"{campo} es obligatorio.")
    codigo = str(valor).strip()
    if not codigo:
        raise ValueError(f"{campo} no puede estar vacío.")
    if not PATRON_CODIGO.fullmatch(codigo):
        raise ValueError(
            f"{campo} debe contener al menos 2 caracteres alfanuméricos, guion o guion bajo."
        )
    return codigo


def validar_especialidad(valor):
    return texto_requerido(valor, "La especialidad", 100)


def validar_motivo(valor):
    return texto_requerido(valor, "El motivo de la cita", 200)


def validar_diagnostico(valor):
    return texto_requerido(valor, "El diagnóstico", 500)


def normalizar_fecha(valor):
    """Acepta DD/MM/AAAA o AAAA-MM-DD y devuelve DD/MM/AAAA."""
    fecha = texto_requerido(valor, "La fecha de la cita", 10)

    formatos = ("%d/%m/%Y", "%Y-%m-%d")
    for formato in formatos:
        try:
            fecha_objeto = datetime.strptime(fecha, formato)
            return fecha_objeto.strftime("%d/%m/%Y")
        except ValueError:
            continue

    raise ValueError(
        "La fecha debe tener el formato DD/MM/AAAA. Ejemplo: 15/09/2026."
    )


def normalizar_hora(valor):
    """Valida y normaliza una hora en formato de 24 horas HH:MM."""
    hora = texto_requerido(valor, "La hora de la cita", 5)
    try:
        hora_objeto = datetime.strptime(hora, "%H:%M")
    except ValueError as error:
        raise ValueError(
            "La hora debe tener el formato HH:MM, por ejemplo 09:30."
        ) from error
    return hora_objeto.strftime("%H:%M")

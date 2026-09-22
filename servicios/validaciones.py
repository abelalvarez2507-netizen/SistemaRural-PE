"""Validaciones y normalizaciones compartidas del dominio SaluPro."""

import re
from datetime import datetime


PATRON_CODIGO = re.compile(r"^[A-Za-z0-9_-]{2,10}$")


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
    """Valida un nombre humano sin aceptar números."""
    nombre = texto_requerido(valor, "El nombre", 100)

    if not any(caracter.isalpha() for caracter in nombre):
        raise ValueError("El nombre debe contener letras.")

    permitidos = set(" .-'ÁÉÍÓÚÜÑáéíóúüñ")
    if not all(caracter.isalpha() or caracter in permitidos for caracter in nombre):
        raise ValueError(
            "El nombre solo puede contener letras, espacios, apóstrofes, puntos o guiones."
        )

    return nombre


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
    """Valida códigos internos alfanuméricos."""
    codigo = texto_requerido(valor, campo, 10)

    if not PATRON_CODIGO.fullmatch(codigo):
        raise ValueError(
            f"{campo} debe contener entre 2 y 10 caracteres alfanuméricos, guion o guion bajo."
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

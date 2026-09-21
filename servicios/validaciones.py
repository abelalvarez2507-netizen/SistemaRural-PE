def texto_requerido(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} es obligatorio.")
    return valor.strip()


def dni_valido(dni):
    dni = str(dni).strip()
    if not dni.isdigit() or len(dni) != 8:
        raise ValueError("El DNI debe contener exactamente 8 dígitos.")
    return dni


def edad_valida(edad):
    if not isinstance(edad, int) or edad < 0 or edad > 120:
        raise ValueError("La edad debe ser un entero entre 0 y 120.")
    return edad


def codigo_valido(codigo, campo="Código"):
    codigo = texto_requerido(codigo, campo)
    return codigo


def fecha_valida(fecha):
    return texto_requerido(fecha, "La fecha")

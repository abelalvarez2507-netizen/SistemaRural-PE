"""Widgets compartidos para la captura de datos en las pantallas."""

import tkinter as tk


def configurar_mascara_fecha(campo, al_cambiar=None):
    """Inserta las barras DD/MM/AAAA y limita la captura a ocho dígitos."""
    validacion = campo.register(
        lambda valor: valor == getattr(campo, "placeholder_texto", None)
        or (
            len(valor) <= 10
            and all(
                caracter.isascii()
                and (caracter.isdigit() or caracter == "/")
                for caracter in valor
            )
        )
    )
    campo.configure(validate="key", validatecommand=(validacion, "%P"))

    def bloquear_barra_manual(evento):
        if evento.char == "/":
            return "break"
        return None

    def aplicar_mascara(evento=None):
        if getattr(campo, "placeholder_activo", False):
            return

        if evento and evento.keysym in {
            "Left", "Right", "Up", "Down", "Home", "End", "Tab",
            "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R",
        }:
            return

        actual = campo.get()
        posicion = campo.index(tk.INSERT)
        digitos_antes = sum("0" <= caracter <= "9" for caracter in actual[:posicion])
        digitos = "".join(caracter for caracter in actual if "0" <= caracter <= "9")[:8]

        nuevo = digitos[:2]
        if len(digitos) >= 2:
            nuevo += "/"
        if len(digitos) > 2:
            nuevo += digitos[2:4]
        if len(digitos) >= 4:
            nuevo += "/"
        if len(digitos) > 4:
            nuevo += digitos[4:8]

        if nuevo != actual:
            campo.configure(validate="none")
            campo.delete(0, tk.END)
            campo.insert(0, nuevo)
            campo.configure(validate="key", validatecommand=(validacion, "%P"))
            posicion_nueva = digitos_antes
            if digitos_antes >= 2:
                posicion_nueva += 1
            if digitos_antes >= 4:
                posicion_nueva += 1
            campo.icursor(min(posicion_nueva, len(nuevo)))

        if al_cambiar:
            al_cambiar()

    campo.bind("<KeyPress>", bloquear_barra_manual, add="+")
    campo.bind("<KeyRelease>", aplicar_mascara, add="+")
    campo.bind("<<Paste>>", lambda _evento: campo.after_idle(aplicar_mascara), add="+")
    return campo

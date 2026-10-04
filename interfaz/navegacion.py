"""Herramientas comunes de desplazamiento y navegación para SaluPro."""

import time
import tkinter as tk


# =========================================================
# SENSIBILIDAD DEL DESPLAZAMIENTO (ajusta aquí)
# =========================================================

# Rueda de un mouse: píxeles que baja la pantalla por cada "clic".
PIXELES_POR_CLIC = 20

# Touchpad de laptop: píxeles por cada unidad que envía el touchpad.
# Más alto = más rápido; más bajo = más lento y fino.
SENSIBILIDAD_TOUCHPAD = 0.4

# Mac: píxeles por cada unidad de desplazamiento.
PIXELES_POR_UNIDAD_MAC = 8

# Los lienzos desplazables avanzan de 1 en 1 píxel para que el touchpad se
# sienta suave. Las flechas de la barra se escalan con PIXELES_POR_CLIC.
PASO_FINO = 1

# Si llegan eventos "no múltiplos de 120", son de un touchpad: durante este
# tiempo (segundos) se sigue tratando el gesto como touchpad.
VENTANA_TOUCHPAD = 0.35


def comando_barra(canvas):
    """Comando para una Scrollbar que respeta PIXELES_POR_CLIC en las flechas."""

    def comando(*argumentos):
        if (
            len(argumentos) == 3
            and argumentos[0] == "scroll"
            and argumentos[2] == "units"
        ):
            canvas.yview(
                "scroll",
                int(argumentos[1]) * PIXELES_POR_CLIC,
                "units",
            )
        else:
            canvas.yview(*argumentos)

    return comando


def _pixeles_del_evento(canvas, evento):
    """Convierte un evento de rueda/touchpad en píxeles (positivo = bajar).

    Devuelve None si el evento no es de desplazamiento.
    """
    numero = getattr(evento, "num", None)
    if numero == 4:
        return -PIXELES_POR_CLIC
    if numero == 5:
        return PIXELES_POR_CLIC

    delta = getattr(evento, "delta", 0)
    if not delta:
        return None

    raiz = canvas._root()
    try:
        sistema = raiz.tk.call("tk", "windowingsystem")
    except tk.TclError:
        sistema = ""
    if sistema == "aqua":
        # En Mac el delta ya viene en unidades pequeñas (mouse y trackpad).
        return -delta * PIXELES_POR_UNIDAD_MAC

    ahora = time.monotonic()
    if delta % 120 != 0:
        # Un mouse envía múltiplos de 120; un touchpad envía valores pequeños.
        raiz._salupro_ultimo_touchpad = ahora
    es_touchpad = (
        ahora - getattr(raiz, "_salupro_ultimo_touchpad", -10.0)
        < VENTANA_TOUCHPAD
    )
    if es_touchpad:
        return -delta * SENSIBILIDAD_TOUCHPAD
    return -delta * PIXELES_POR_CLIC / 120


def _paso_en_pixeles(canvas):
    try:
        paso = float(canvas.cget("yscrollincrement"))
    except (tk.TclError, ValueError):
        paso = 0.0
    if paso <= 0:
        # Sin incremento fijo, una "unidad" es una décima parte de la altura.
        paso = max(1.0, canvas.winfo_height() / 10)
    return paso


def desplazar_por_evento(canvas, evento):
    """Desplaza un lienzo según un evento de rueda o touchpad.

    Devuelve None si el evento no es de desplazamiento, True si el
    movimiento se aplicó (o quedó pendiente por ser muy pequeño) y False si
    el lienzo ya estaba en el límite.
    """
    pixeles = _pixeles_del_evento(canvas, evento)
    if pixeles is None:
        return None

    # Los movimientos pequeños del touchpad se acumulan hasta completar
    # una unidad, así no se pierde ningún gesto.
    total = getattr(canvas, "_salupro_resto", 0.0) + pixeles / _paso_en_pixeles(
        canvas
    )
    unidades = int(total)
    canvas._salupro_resto = total - unidades
    if unidades == 0:
        return True

    antes = canvas.yview()
    canvas.yview_scroll(unidades, "units")
    if canvas.yview() == antes:
        canvas._salupro_resto = 0.0
        return False
    return True


class VistaDesplazable(tk.Frame):
    """Contenedor vertical con barra, rueda del mouse y touchpad."""

    def __init__(self, master, color_fondo):
        super().__init__(master, bg=color_fondo)
        self._color_fondo = color_fondo
        self.canvas = tk.Canvas(
            self,
            bg=color_fondo,
            highlightthickness=0,
            bd=0,
            yscrollincrement=PASO_FINO,
        )
        self.barra = tk.Scrollbar(
            self,
            orient="vertical",
            command=comando_barra(self.canvas),
            bg=color_fondo,
            troughcolor=color_fondo,
            activebackground="#347B65",
        )
        self.contenido = tk.Frame(self.canvas, bg=color_fondo)
        self._ventana_canvas = self.canvas.create_window(
            (0, 0),
            window=self.contenido,
            anchor="nw",
        )
        self.canvas.configure(yscrollcommand=self.barra.set)
        self.barra.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.contenido.bind("<Configure>", self._actualizar_region)
        self.canvas.bind("<Configure>", self._ajustar_ancho)

        raiz = self._root()
        _registrar_vista(raiz, self)

    def _actualizar_region(self, _evento=None):
        try:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except tk.TclError:
            pass

    def _ajustar_ancho(self, evento):
        try:
            self.canvas.itemconfigure(self._ventana_canvas, width=evento.width)
        except tk.TclError:
            pass

    def destroy(self):
        raiz = self._root()
        _quitar_vista(raiz, self)
        super().destroy()


def instalar_navegacion(ventana, volver=None, inicio=None):
    """Activa Alt+Izquierda para volver y Alt+Inicio para ir al inicio."""

    if not getattr(ventana, "_salupro_navegacion_instalada", False):
        ventana._salupro_navegacion_instalada = True

        def volver_teclado(_evento=None):
            secundaria = _ventana_secundaria_activa(ventana)
            if secundaria is not None:
                callback_secundario = getattr(
                    secundaria,
                    "_salupro_volver",
                    None,
                )
                if callable(callback_secundario):
                    callback_secundario()
                else:
                    secundaria.destroy()
                return "break"
            callback = getattr(ventana, "_salupro_volver", None)
            if callable(callback):
                callback()
            return "break"

        def inicio_teclado(_evento=None):
            secundaria = _ventana_secundaria_activa(ventana)
            if secundaria is not None:
                secundaria.destroy()
            callback = getattr(ventana, "_salupro_inicio", None)
            if callable(callback):
                callback()
            return "break"

        ventana.bind_all("<Alt-Left>", volver_teclado, add="+")
        ventana.bind_all("<Alt-Home>", inicio_teclado, add="+")

    if volver is not None:
        ventana._salupro_volver = volver
    if inicio is not None:
        ventana._salupro_inicio = inicio


def _ventana_secundaria_activa(ventana):
    try:
        foco = ventana.focus_get()
        if foco is None:
            return None
        secundaria = foco.winfo_toplevel()
        return secundaria if secundaria is not ventana else None
    except tk.TclError:
        return None


def _registrar_vista(raiz, vista):
    vistas = getattr(raiz, "_salupro_vistas_desplazables", None)
    if vistas is None:
        vistas = []
        raiz._salupro_vistas_desplazables = vistas

        def desplazar(evento):
            widget = getattr(evento, "widget", None)
            if widget is None:
                return None

            vistas_en_ruta = []
            actual = widget
            while actual is not None:
                if actual in vistas:
                    vistas_en_ruta.append(actual)
                actual = getattr(actual, "master", None)

            if not vistas_en_ruta:
                return None

            for candidata in vistas_en_ruta:
                try:
                    resultado = desplazar_por_evento(candidata.canvas, evento)
                except tk.TclError:
                    continue
                if resultado is None:
                    return None
                if resultado:
                    return "break"
            return None

        raiz._salupro_manejador_rueda = desplazar
        raiz.bind_all("<MouseWheel>", desplazar, add="+")
        raiz.bind_all("<Button-4>", desplazar, add="+")
        raiz.bind_all("<Button-5>", desplazar, add="+")

    if vista not in vistas:
        vistas.append(vista)


def _quitar_vista(raiz, vista):
    vistas = getattr(raiz, "_salupro_vistas_desplazables", None)
    if vistas is not None and vista in vistas:
        vistas.remove(vista)

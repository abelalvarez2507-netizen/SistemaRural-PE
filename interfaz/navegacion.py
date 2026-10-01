"""Herramientas comunes de desplazamiento y navegación para SaluPro."""

import tkinter as tk


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
            yscrollincrement=20,
        )
        self.barra = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
            bg=color_fondo,
            troughcolor=color_fondo,
            activebackground="#b32732",
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

            delta = getattr(evento, "delta", 0)
            if delta:
                raiz._salupro_delta_rueda = (
                    getattr(raiz, "_salupro_delta_rueda", 0) + delta
                )
                unidades = int(raiz._salupro_delta_rueda / 120)
                if not unidades:
                    return "break"
                raiz._salupro_delta_rueda -= unidades * 120
                movimiento = -unidades
            elif getattr(evento, "num", None) == 4:
                movimiento = -1
            elif getattr(evento, "num", None) == 5:
                movimiento = 1
            else:
                return None

            for candidata in vistas_en_ruta:
                try:
                    antes = candidata.canvas.yview()
                    candidata.canvas.yview_scroll(movimiento, "units")
                    despues = candidata.canvas.yview()
                    if despues != antes:
                        return "break"
                except tk.TclError:
                    continue
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

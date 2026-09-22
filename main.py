import tkinter as tk

from interfaz.estilos import inicializar_estilos
from interfaz.pantalla_inicio import PantallaInicio


def main():
    """
    Punto de entrada principal de SaluPro.
    """

    ventana = tk.Tk()

    try:
        ventana.state("zoomed")
    except tk.TclError:
        pass

    def alternar_pantalla_completa(evento=None):
        try:
            actual = bool(ventana.attributes("-fullscreen"))
            ventana.attributes("-fullscreen", not actual)
        except tk.TclError:
            try:
                estado = ventana.state()
                ventana.state("normal" if estado == "zoomed" else "zoomed")
            except tk.TclError:
                pass

    ventana.bind("<F11>", alternar_pantalla_completa)

    # Configurar estilos generales
    inicializar_estilos(ventana)

    # Crear pantalla inicial
    PantallaInicio(ventana)

    # Iniciar aplicación
    ventana.mainloop()


if __name__ == "__main__":
    main()
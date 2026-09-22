import tkinter as tk
from tkinter import ttk


# =========================================================
# COLORES PRINCIPALES DE SALUPRO
# =========================================================

COLOR_FONDO = "#0B1117"
COLOR_FONDO_SECUNDARIO = "#111A22"

COLOR_PANEL = "#151F28"
COLOR_PANEL_CLARO = "#1C2933"

COLOR_ROJO = "#E3262E"
COLOR_ROJO_CLARO = "#FF4B52"
COLOR_ROJO_OSCURO = "#A9161D"

COLOR_NEGRO = "#05080B"

COLOR_BLANCO = "#FFFFFF"
COLOR_GRIS_CLARO = "#E5E7EB"
COLOR_GRIS = "#AAB4BE"
COLOR_GRIS_OSCURO = "#68737D"

COLOR_VERDE = "#20C77A"
COLOR_AMARILLO = "#F5B942"
COLOR_AZUL = "#3498DB"


# =========================================================
# FUENTES
# =========================================================

FUENTE_LOGO = ("Arial", 24, "bold")

FUENTE_TITULO = ("Arial", 28, "bold")

FUENTE_SUBTITULO = ("Arial", 14)

FUENTE_SECCION = ("Arial", 16, "bold")

FUENTE_NORMAL = ("Arial", 11)

FUENTE_NORMAL_BOLD = ("Arial", 11, "bold")

FUENTE_BOTON = ("Arial", 11, "bold")

FUENTE_BOTON_GRANDE = ("Arial", 13, "bold")

FUENTE_PEQUENA = ("Arial", 9)

FUENTE_CODIGO = ("Arial", 14, "bold")


# =========================================================
# CONFIGURACIÓN GENERAL DE LA VENTANA
# =========================================================

def configurar_ventana(ventana):
    """
    Configura los aspectos visuales generales de una ventana.
    """

    ventana.configure(
        bg=COLOR_FONDO
    )


# =========================================================
# CONFIGURACIÓN DE ESTILOS TTk
# =========================================================

def configurar_estilos():
    """
    Configura los estilos generales utilizados por SaluPro.
    """

    estilo = ttk.Style()

    try:
        estilo.theme_use("clam")
    except tk.TclError:
        pass

    # -----------------------------------------------------
    # BOTÓN PRINCIPAL
    # -----------------------------------------------------

    estilo.configure(
        "SaluPro.TButton",
        font=FUENTE_BOTON,
        foreground=COLOR_BLANCO,
        background=COLOR_ROJO,
        padding=(18, 10),
        borderwidth=0,
        relief="flat"
    )

    estilo.map(
        "SaluPro.TButton",
        background=[
            ("active", COLOR_ROJO_CLARO),
            ("pressed", COLOR_ROJO_OSCURO)
        ],
        foreground=[
            ("disabled", COLOR_GRIS_OSCURO),
            ("!disabled", COLOR_BLANCO)
        ]
    )

    # -----------------------------------------------------
    # BOTÓN GRANDE
    # -----------------------------------------------------

    estilo.configure(
        "SaluPro.Grande.TButton",
        font=FUENTE_BOTON_GRANDE,
        foreground=COLOR_BLANCO,
        background=COLOR_ROJO,
        padding=(25, 15),
        borderwidth=0,
        relief="flat"
    )

    estilo.map(
        "SaluPro.Grande.TButton",
        background=[
            ("active", COLOR_ROJO_CLARO),
            ("pressed", COLOR_ROJO_OSCURO)
        ]
    )

    # -----------------------------------------------------
    # LABEL NORMAL
    # -----------------------------------------------------

    estilo.configure(
        "SaluPro.TLabel",
        background=COLOR_FONDO,
        foreground=COLOR_BLANCO,
        font=FUENTE_NORMAL
    )

    # -----------------------------------------------------
    # LABEL DE TÍTULO
    # -----------------------------------------------------

    estilo.configure(
        "SaluPro.Titulo.TLabel",
        background=COLOR_FONDO,
        foreground=COLOR_BLANCO,
        font=FUENTE_TITULO
    )

    # -----------------------------------------------------
    # LABEL DE SUBTÍTULO
    # -----------------------------------------------------

    estilo.configure(
        "SaluPro.Subtitulo.TLabel",
        background=COLOR_FONDO,
        foreground=COLOR_GRIS_CLARO,
        font=FUENTE_SUBTITULO
    )

    # -----------------------------------------------------
    # LABEL DE SECCIÓN
    # -----------------------------------------------------

    estilo.configure(
        "SaluPro.Seccion.TLabel",
        background=COLOR_PANEL,
        foreground=COLOR_BLANCO,
        font=FUENTE_SECCION
    )

    # -----------------------------------------------------
    # ENTRY
    # -----------------------------------------------------

    estilo.configure(
        "SaluPro.TEntry",
        font=FUENTE_NORMAL,
        fieldbackground=COLOR_PANEL_CLARO,
        foreground=COLOR_BLANCO,
        insertcolor=COLOR_BLANCO,
        borderwidth=1,
        padding=8
    )

    # -----------------------------------------------------
    # COMBOBOX
    # -----------------------------------------------------

    estilo.configure(
        "SaluPro.TCombobox",
        font=FUENTE_NORMAL,
        fieldbackground=COLOR_PANEL_CLARO,
        background=COLOR_PANEL_CLARO,
        foreground=COLOR_BLANCO,
        borderwidth=1,
        padding=7
    )

    # -----------------------------------------------------
    # NOTEBOOK
    # -----------------------------------------------------

    estilo.configure(
        "SaluPro.TNotebook",
        background=COLOR_FONDO,
        borderwidth=0
    )

    estilo.configure(
        "SaluPro.TNotebook.Tab",
        font=FUENTE_NORMAL_BOLD,
        background=COLOR_PANEL,
        foreground=COLOR_GRIS_CLARO,
        padding=(15, 8)
    )

    estilo.map(
        "SaluPro.TNotebook.Tab",
        background=[
            ("selected", COLOR_ROJO)
        ],
        foreground=[
            ("selected", COLOR_BLANCO)
        ]
    )


# =========================================================
# CREAR BOTÓN PERSONALIZADO
# =========================================================

def crear_boton(
    parent,
    texto,
    comando,
    ancho=25,
    alto=1,
    grande=False
):
    """
    Crea un botón con el estilo visual de SaluPro.

    Parámetros:
        parent   -> ventana o Frame donde aparecerá
        texto    -> texto del botón
        comando  -> función que ejecutará
        ancho    -> ancho del botón
        alto     -> alto del botón
        grande   -> utiliza un tamaño de fuente mayor
    """

    boton = tk.Button(
        parent,
        text=texto,
        command=comando,
        width=ancho,
        height=alto,

        font=(
            FUENTE_BOTON_GRANDE
            if grande
            else FUENTE_BOTON
        ),

        bg=COLOR_ROJO,
        fg=COLOR_BLANCO,

        activebackground=COLOR_ROJO_CLARO,
        activeforeground=COLOR_BLANCO,

        relief="flat",
        bd=0,

        cursor="hand2",

        padx=10,
        pady=8
    )

    return boton


# =========================================================
# BOTÓN CON EFECTO HOVER
# =========================================================

def crear_boton_hover(
    parent,
    texto,
    comando,
    ancho=25,
    alto=1,
    grande=False
):
    """
    Crea un botón con efecto visual al pasar
    el mouse por encima.
    """

    boton = crear_boton(
        parent=parent,
        texto=texto,
        comando=comando,
        ancho=ancho,
        alto=alto,
        grande=grande
    )

    def entrar_mouse(evento):
        boton.configure(
            bg=COLOR_ROJO_CLARO
        )

    def salir_mouse(evento):
        boton.configure(
            bg=COLOR_ROJO
        )

    boton.bind(
        "<Enter>",
        entrar_mouse
    )

    boton.bind(
        "<Leave>",
        salir_mouse
    )

    return boton


# =========================================================
# CREAR PANEL
# =========================================================

def crear_panel(parent):
    """
    Crea un panel oscuro reutilizable.
    """

    panel = tk.Frame(
        parent,
        bg=COLOR_PANEL,
        bd=0,
        relief="flat"
    )

    return panel


# =========================================================
# CREAR TÍTULO
# =========================================================

def crear_titulo(
    parent,
    texto="SALUPRO"
):
    """
    Crea un título principal.
    """

    titulo = tk.Label(
        parent,
        text=texto,
        font=FUENTE_TITULO,
        fg=COLOR_BLANCO,
        bg=COLOR_FONDO
    )

    return titulo


# =========================================================
# CREAR SUBTÍTULO
# =========================================================

def crear_subtitulo(
    parent,
    texto
):
    """
    Crea un subtítulo.
    """

    subtitulo = tk.Label(
        parent,
        text=texto,
        font=FUENTE_SUBTITULO,
        fg=COLOR_GRIS_CLARO,
        bg=COLOR_FONDO
    )

    return subtitulo


# =========================================================
# CREAR TÍTULO DE SECCIÓN
# =========================================================

def crear_titulo_seccion(
    parent,
    texto
):
    """
    Crea un título para una sección.
    """

    titulo = tk.Label(
        parent,
        text=texto,
        font=FUENTE_SECCION,
        fg=COLOR_BLANCO,
        bg=COLOR_PANEL
    )

    return titulo


# =========================================================
# CREAR TEXTO NORMAL
# =========================================================

def crear_label(
    parent,
    texto,
    fondo=None,
    color=None,
    fuente=None
):
    """
    Crea un Label reutilizable.
    """

    if fondo is None:
        fondo = COLOR_FONDO

    if color is None:
        color = COLOR_BLANCO

    if fuente is None:
        fuente = FUENTE_NORMAL

    etiqueta = tk.Label(
        parent,
        text=texto,
        bg=fondo,
        fg=color,
        font=fuente
    )

    return etiqueta


# =========================================================
# CREAR CAMPO DE TEXTO
# =========================================================

def crear_entry(
    parent,
    ancho=30
):
    """
    Crea un campo de texto con el estilo de SaluPro.
    """

    entrada = tk.Entry(
        parent,
        width=ancho,
        font=FUENTE_NORMAL,

        bg=COLOR_PANEL_CLARO,
        fg=COLOR_BLANCO,

        insertbackground=COLOR_BLANCO,

        relief="flat",
        bd=1,

        highlightthickness=1,
        highlightbackground=COLOR_GRIS_OSCURO,
        highlightcolor=COLOR_ROJO
    )

    return entrada


# =========================================================
# CREAR ÁREA DE TEXTO
# =========================================================

def crear_texto(
    parent,
    ancho=80,
    alto=20
):
    """
    Crea un área de texto para mostrar información.
    """

    texto = tk.Text(
        parent,
        width=ancho,
        height=alto,

        font=FUENTE_NORMAL,

        bg=COLOR_PANEL_CLARO,
        fg=COLOR_BLANCO,

        insertbackground=COLOR_BLANCO,

        relief="flat",
        bd=0,

        padx=10,
        pady=10,

        selectbackground=COLOR_ROJO,
        selectforeground=COLOR_BLANCO
    )

    return texto


# =========================================================
# CREAR BARRA SUPERIOR
# =========================================================

def crear_barra_superior(
    parent,
    texto="SALUPRO"
):
    """
    Crea una barra superior roja/oscura.
    """

    barra = tk.Frame(
        parent,
        bg=COLOR_NEGRO,
        height=65
    )

    barra.pack_propagate(False)

    logo = tk.Label(
        barra,
        text=texto,
        font=FUENTE_LOGO,
        bg=COLOR_NEGRO,
        fg=COLOR_BLANCO
    )

    logo.pack(
        side="left",
        padx=25
    )

    return barra


# =========================================================
# CREAR LÍNEA DECORATIVA
# =========================================================

def crear_linea_roja(parent):
    """
    Crea una línea decorativa roja.
    """

    linea = tk.Frame(
        parent,
        bg=COLOR_ROJO,
        height=3
    )

    return linea


# =========================================================
# CONFIGURACIÓN INICIAL DE SALUPRO
# =========================================================

def inicializar_estilos(ventana):
    """
    Función general para iniciar los estilos de SaluPro.
    """

    configurar_ventana(
        ventana
    )

    configurar_estilos()
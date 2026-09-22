import tkinter as tk

from interfaz.estilos import (
    COLOR_FONDO,
    COLOR_PANEL,
    COLOR_ROJO,
    COLOR_ROJO_CLARO,
    COLOR_ROJO_OSCURO,
    COLOR_BLANCO,
    COLOR_GRIS_CLARO,
    COLOR_GRIS,
    FUENTE_TITULO,
    FUENTE_SUBTITULO,
    FUENTE_BOTON_GRANDE
)


class PantallaInicio:

    def __init__(self, ventana):

        self.ventana = ventana

        # =====================================================
        # CONFIGURACIÓN DE LA VENTANA
        # =====================================================

        self.ventana.title(
            "SaluPro - Sistema de Salud Rural"
        )

        self.ventana.geometry(
            "900x650"
        )

        self.ventana.configure(
            bg=COLOR_FONDO
        )

        self.ventana.resizable(
            True,
            True
        )
        self.ventana.minsize(
            850,
            600
        )

        self.ventana.bind(
            "<F11>",
            self._alternar_pantalla_completa
        )

        try:
            self.ventana.state("zoomed")
        except tk.TclError:
            pass

        # =====================================================
        # CREAR INTERFAZ
        # =====================================================

        self.crear_interfaz()


    def _alternar_pantalla_completa(self, evento=None):
        """Alterna entre ventana maximizada y pantalla completa."""
        try:
            actual = bool(self.ventana.attributes("-fullscreen"))
            self.ventana.attributes("-fullscreen", not actual)
        except tk.TclError:
            try:
                estado = self.ventana.state()
                self.ventana.state("normal" if estado == "zoomed" else "zoomed")
            except tk.TclError:
                pass

    # =========================================================
    # MOSTRAR PANTALLA DE INICIO
    # =========================================================

    def mostrar(self):

        # Elimina cualquier contenido anterior
        # de la ventana principal.

        for widget in self.ventana.winfo_children():
            widget.destroy()

        self.crear_interfaz()

    # =========================================================
    # INTERFAZ PRINCIPAL
    # =========================================================

    def crear_interfaz(self):

        # =====================================================
        # CONTENEDOR PRINCIPAL
        # =====================================================

        contenedor = tk.Frame(
            self.ventana,
            bg=COLOR_FONDO
        )

        contenedor.pack(
            fill="both",
            expand=True
        )

        # =====================================================
        # LOGO / NOMBRE SALUPRO
        # =====================================================

        logo = tk.Label(
            contenedor,
            text="SALUPRO",
            font=("Arial", 34, "bold"),
            fg=COLOR_BLANCO,
            bg=COLOR_FONDO
        )

        logo.pack(
            pady=(55, 10)
        )

        # =====================================================
        # LÍNEA DECORATIVA
        # =====================================================

        linea = tk.Frame(
            contenedor,
            bg=COLOR_ROJO,
            height=4,
            width=180
        )

        linea.pack(
            pady=(0, 25)
        )

        # =====================================================
        # TÍTULO
        # =====================================================

        titulo = tk.Label(
            contenedor,
            text="BIENVENIDO A SALUPRO",
            font=FUENTE_TITULO,
            fg=COLOR_BLANCO,
            bg=COLOR_FONDO
        )

        titulo.pack(
            pady=5
        )

        # =====================================================
        # SUBTÍTULO
        # =====================================================

        subtitulo = tk.Label(
            contenedor,
            text="Selecciona tu tipo de acceso",
            font=FUENTE_SUBTITULO,
            fg=COLOR_GRIS_CLARO,
            bg=COLOR_FONDO
        )

        subtitulo.pack(
            pady=(5, 30)
        )

        # =====================================================
        # PANEL DE BOTONES
        # =====================================================

        panel_botones = tk.Frame(
            contenedor,
            bg=COLOR_FONDO
        )

        panel_botones.pack(
            pady=10
        )

        # =====================================================
        # BOTÓN PACIENTE
        # =====================================================

        boton_paciente = tk.Button(
            panel_botones,
            text="PACIENTE",
            font=FUENTE_BOTON_GRANDE,
            width=20,
            height=3,

            bg=COLOR_PANEL,
            fg=COLOR_BLANCO,

            activebackground=COLOR_ROJO,
            activeforeground=COLOR_BLANCO,

            relief="flat",
            bd=0,

            cursor="hand2",

            command=self.abrir_paciente
        )

        boton_paciente.grid(
            row=0,
            column=0,
            padx=15,
            pady=10
        )

        # =====================================================
        # BOTÓN ADMINISTRATIVA
        # =====================================================

        boton_administrativa = tk.Button(
            panel_botones,
            text="ADMINISTRATIVA",
            font=FUENTE_BOTON_GRANDE,
            width=20,
            height=3,

            bg=COLOR_ROJO,
            fg=COLOR_BLANCO,

            activebackground=COLOR_ROJO_CLARO,
            activeforeground=COLOR_BLANCO,

            relief="flat",
            bd=0,

            cursor="hand2",

            command=self.abrir_administrativa
        )

        boton_administrativa.grid(
            row=0,
            column=1,
            padx=15,
            pady=10
        )

        # =====================================================
        # EFECTO HOVER - PACIENTE
        # =====================================================

        def paciente_entrar(evento):

            boton_paciente.configure(
                bg=COLOR_ROJO
            )

        def paciente_salir(evento):

            boton_paciente.configure(
                bg=COLOR_PANEL
            )

        boton_paciente.bind(
            "<Enter>",
            paciente_entrar
        )

        boton_paciente.bind(
            "<Leave>",
            paciente_salir
        )

        # =====================================================
        # EFECTO HOVER - ADMINISTRATIVA
        # =====================================================

        def administrativa_entrar(evento):

            boton_administrativa.configure(
                bg=COLOR_ROJO_CLARO
            )

        def administrativa_salir(evento):

            boton_administrativa.configure(
                bg=COLOR_ROJO
            )

        boton_administrativa.bind(
            "<Enter>",
            administrativa_entrar
        )

        boton_administrativa.bind(
            "<Leave>",
            administrativa_salir
        )

        # =====================================================
        # INFORMACIÓN INFERIOR
        # =====================================================

        separador = tk.Frame(
            contenedor,
            bg=COLOR_ROJO_OSCURO,
            height=1,
            width=500
        )

        separador.pack(
            pady=(45, 20)
        )

        texto_gestion = tk.Label(
            contenedor,
            text="Gestión Integral de Salud",
            font=("Arial", 11, "bold"),
            fg=COLOR_GRIS_CLARO,
            bg=COLOR_FONDO
        )

        texto_gestion.pack(
            pady=3
        )

        texto_calidad = tk.Label(
            contenedor,
            text="Atención de Calidad",
            font=("Arial", 10),
            fg=COLOR_GRIS,
            bg=COLOR_FONDO
        )

        texto_calidad.pack(
            pady=3
        )

        # =====================================================
        # PIE DE PÁGINA
        # =====================================================

        pie = tk.Label(
            contenedor,
            text="Sistema de Salud Rural",
            font=("Arial", 9),
            fg=COLOR_GRIS,
            bg=COLOR_FONDO
        )

        pie.pack(
            pady=(25, 0)
        )

        # =====================================================
        # BOTÓN SALIR
        # =====================================================

        boton_salir = tk.Button(
            contenedor,
            text="Salir",
            font=("Arial", 9, "bold"),
            bg=COLOR_ROJO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO_OSCURO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=4,
            command=self.salir
        )

        boton_salir.place(
            relx=1.0,
            rely=1.0,
            anchor="se",
            x=-20,
            y=-20
        )

        def salir_entrar(evento):
            boton_salir.configure(
                bg=COLOR_ROJO_OSCURO
            )

        def salir_salir(evento):
            boton_salir.configure(
                bg=COLOR_ROJO
            )

        boton_salir.bind(
            "<Enter>",
            salir_entrar
        )

        boton_salir.bind(
            "<Leave>",
            salir_salir
        )

    # =========================================================
    # SALIR DEL PROGRAMA
    # =========================================================

    def salir(self):
        """Cierra completamente SaluPro y todas sus ventanas."""
        try:
            self.ventana.quit()
        except tk.TclError:
            pass

        try:
            self.ventana.destroy()
        except tk.TclError:
            pass

    # =========================================================
    # BOTÓN PACIENTE
    # =========================================================

    def abrir_paciente(self):

        # Importamos aquí para evitar
        # problemas de importación circular.

        from interfaz.pantalla_paciente import PantallaPaciente

        # Limpiamos la ventana principal.

        for widget in self.ventana.winfo_children():
            widget.destroy()

        # Abrimos el módulo paciente.

        PantallaPaciente(
            self.ventana,
            self
        )

    # =========================================================
    # BOTÓN ADMINISTRATIVA
    # =========================================================

    def abrir_administrativa(self):

        # Reemplaza el contenido de la misma ventana raíz.
        # No se crea una segunda ventana administrativa.
        from interfaz.ventana_principal import VentanaPrincipal

        for widget in self.ventana.winfo_children():
            widget.destroy()

        VentanaPrincipal(
            self.ventana,
            pantalla_inicio=self
        )

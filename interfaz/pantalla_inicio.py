import math
import os
import tkinter as tk
import tkinter.font as tkfont

try:  # Pillow solo se usa para el fondo decorativo; si falta, se usa color liso.
    from PIL import Image, ImageTk
except ImportError:  # pragma: no cover
    Image = None
    ImageTk = None

from interfaz.estilos import (
    COLOR_FONDO,
    COLOR_PANEL,
    COLOR_PANEL_CLARO,
    COLOR_ROJO,
    COLOR_ROJO_CLARO,
    COLOR_ROJO_OSCURO,
    COLOR_BLANCO,
    COLOR_TEXTO,
    COLOR_GRIS_CLARO,
    COLOR_GRIS,
    FUENTE_TITULO,
    FUENTE_SUBTITULO,
    FUENTE_BOTON_GRANDE
)
from interfaz.navegacion import VistaDesplazable, instalar_navegacion

RUTA_IMAGENES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "imagenes",
)

# Color de la imagen de fondo (se usa mientras carga o si no hay Pillow).
COLOR_LIENZO_IMAGEN = "#F9FAFC"

# Colores del logo SaluPro (azul y verde de la imagen de referencia).
COLOR_LOGO_AZUL = "#1B7FC4"
COLOR_LOGO_VERDE = "#1E9F5F"
COLOR_LINEA_LOGO = "#4CAF73"
FUENTE_LOGO_INICIO = ("Arial", 38, "bold")
ALTO_ICONO = 120


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

        instalar_navegacion(
            self.ventana,
            volver=lambda: None,
            inicio=self.mostrar,
        )

        # =====================================================
        # CONTENEDOR PRINCIPAL (misma vista desplazable)
        # =====================================================

        vista = VistaDesplazable(
            self.ventana,
            COLOR_FONDO,
        )
        vista.pack(fill="both", expand=True)
        contenedor = vista.contenido

        # =====================================================
        # FONDO DECORATIVO
        # Lienzo que ocupa todo el contenedor. La imagen se dibuja
        # al fondo y el texto/botones van encima.
        # =====================================================

        self._fondo_original = self._cargar_imagen("fondo_inicio.png")
        self._icono_original = self._cargar_imagen("icono_inicio.png")
        self._foto_icono = None
        self._foto_fondo = None
        self._tamano_fondo = None
        self._after_fondo = None

        hay_fondo = self._fondo_original is not None
        lienzo = tk.Canvas(
            contenedor,
            bg=COLOR_LIENZO_IMAGEN if hay_fondo else COLOR_FONDO,
            highlightthickness=0,
            bd=0,
        )
        lienzo.pack(fill="both", expand=True)
        self._lienzo = lienzo

        self._id_fondo = lienzo.create_image(0, 0, anchor="nw")

        # =====================================================
        # LOGO / NOMBRE SALUPRO (icono + nombre en azul y verde)
        # =====================================================

        self._id_icono = None
        if self._icono_original is not None and ImageTk is not None:
            alto_icono = ALTO_ICONO
            ancho_icono = round(
                self._icono_original.width
                * alto_icono / self._icono_original.height
            )
            icono = self._icono_original.resize(
                (ancho_icono, alto_icono), Image.LANCZOS
            )
            self._foto_icono = ImageTk.PhotoImage(icono)
            self._id_icono = lienzo.create_image(
                0, 0, anchor="n", image=self._foto_icono
            )

        self._fuente_logo = tkfont.Font(
            root=self.ventana, font=FUENTE_LOGO_INICIO
        )
        self._id_logo_salu = lienzo.create_text(
            0, 0,
            text="Salu",
            anchor="w",
            font=FUENTE_LOGO_INICIO,
            fill=COLOR_LOGO_AZUL,
        )
        self._id_logo_pro = lienzo.create_text(
            0, 0,
            text="Pro",
            anchor="w",
            font=FUENTE_LOGO_INICIO,
            fill=COLOR_LOGO_VERDE,
        )

        # =====================================================
        # LÍNEA DECORATIVA
        # =====================================================

        self._id_linea = lienzo.create_rectangle(
            0, 0, 0, 0,
            fill=COLOR_LINEA_LOGO,
            width=0,
        )

        # =====================================================
        # TÍTULO
        # =====================================================

        self._id_titulo = lienzo.create_text(
            0, 0,
            text="BIENVENIDO A SALUPRO",
            font=FUENTE_TITULO,
            fill=COLOR_TEXTO,
        )

        # =====================================================
        # SUBTÍTULO
        # =====================================================

        self._id_subtitulo = lienzo.create_text(
            0, 0,
            text="Selecciona tu rol. Cada acceso requiere una cuenta verificada.",
            font=FUENTE_SUBTITULO,
            fill=COLOR_GRIS_CLARO,
        )

        # =====================================================
        # BOTONES DE ROL (mismos botones y comandos de siempre)
        # =====================================================

        roles = (
            ("PACIENTE", self.abrir_paciente, COLOR_PANEL, COLOR_TEXTO),
            (
                "ADMINISTRATIVA",
                self.abrir_administrativa,
                COLOR_ROJO,
                COLOR_BLANCO,
            ),
            ("PROFESIONAL", self.abrir_profesional, COLOR_PANEL, COLOR_TEXTO),
            (
                "ENFERMERÍA",
                self.abrir_enfermeria,
                COLOR_PANEL_CLARO,
                COLOR_TEXTO,
            ),
        )
        self._ids_botones = []
        for texto, comando, fondo, primer_plano in roles:
            boton = tk.Button(
                lienzo,
                text=texto,
                font=FUENTE_BOTON_GRANDE,
                width=20,
                height=3,
                bg=fondo,
                fg=primer_plano,
                activebackground=COLOR_ROJO_CLARO,
                activeforeground=COLOR_BLANCO,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground="#D3E2D8",
                highlightcolor=COLOR_ROJO_CLARO,
                cursor="hand2",
                takefocus=True,
                command=comando,
            )
            boton.bind(
                "<Enter>",
                lambda _evento, control=boton: control.configure(
                    bg=COLOR_ROJO, fg=COLOR_BLANCO
                ),
            )
            boton.bind(
                "<Leave>",
                lambda _evento, control=boton, color=fondo, texto_color=primer_plano:
                    control.configure(bg=color, fg=texto_color),
            )
            identificador = lienzo.create_window(
                0, 0, anchor="nw", window=boton
            )
            self._ids_botones.append((identificador, boton))

        # =====================================================
        # INFORMACIÓN INFERIOR
        # =====================================================

        self._id_separador = lienzo.create_rectangle(
            0, 0, 0, 0,
            fill=COLOR_ROJO_OSCURO,
            width=0,
        )

        self._id_gestion = lienzo.create_text(
            0, 0,
            text="Gestión Integral de Salud",
            font=("Arial", 11, "bold"),
            fill=COLOR_GRIS_CLARO,
        )

        self._id_calidad = lienzo.create_text(
            0, 0,
            text="Atención de Calidad",
            font=("Arial", 10),
            fill=COLOR_GRIS,
        )

        # =====================================================
        # PIE DE PÁGINA
        # =====================================================

        self._id_pie = lienzo.create_text(
            0, 0,
            text="Sistema de Salud Rural · acceso protegido por roles",
            font=("Arial", 9),
            fill=COLOR_GRIS,
        )

        # =====================================================
        # BOTÓN SALIR
        # =====================================================

        boton_salir = tk.Button(
            lienzo,
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

        self._id_salir = lienzo.create_window(
            0, 0, anchor="se", window=boton_salir
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

        # =====================================================
        # DISTRIBUCIÓN Y AJUSTE AL TAMAÑO DE LA VENTANA
        # =====================================================

        self._medir_bloque()

        def ajustar_alto(evento):
            # Si la ventana es muy baja, el contenido conserva una
            # altura mínima y se puede desplazar como antes.
            try:
                vista.canvas.itemconfigure(
                    vista._ventana_canvas,
                    height=max(evento.height, self._alto_minimo),
                )
            except tk.TclError:
                pass

        def al_redimensionar(_evento=None):
            self._distribuir()
            self._programar_fondo()

        # Primero se enlazan los avisos de tamaño y después se fuerza un
        # ajuste: al volver desde otra pantalla la ventana ya tiene su tamaño
        # final y no llegaría ningún aviso nuevo, dejando todo apilado arriba.
        vista.canvas.bind("<Configure>", ajustar_alto, add="+")
        lienzo.bind("<Configure>", al_redimensionar)

        def forzar_ajuste():
            try:
                if not lienzo.winfo_exists():
                    return
                vista.update_idletasks()
                alto_vista = vista.canvas.winfo_height()
                if alto_vista > 1:
                    vista.canvas.itemconfigure(
                        vista._ventana_canvas,
                        height=max(alto_vista, self._alto_minimo),
                    )
                vista.update_idletasks()
                self._tamano_fondo = None
                self._distribuir()
                self._pintar_fondo()
            except tk.TclError:
                pass

        self.ventana.after_idle(forzar_ajuste)
        self.ventana.after(120, forzar_ajuste)

    # =========================================================
    # FONDO DECORATIVO
    # =========================================================

    def _cargar_imagen(self, nombre):
        """Carga una imagen de la carpeta imagenes o devuelve None."""
        if Image is None:
            return None
        try:
            imagen = Image.open(os.path.join(RUTA_IMAGENES, nombre))
            imagen.load()
            return imagen.convert("RGBA")
        except (OSError, ValueError):
            return None

    def _programar_fondo(self):
        """Redibuja el fondo poco después de dejar de cambiar el tamaño."""
        if self._fondo_original is None:
            return
        try:
            if self._after_fondo is not None:
                self._lienzo.after_cancel(self._after_fondo)
            self._after_fondo = self._lienzo.after(40, self._pintar_fondo)
        except tk.TclError:
            pass

    def _pintar_fondo(self):
        self._after_fondo = None
        if self._fondo_original is None or ImageTk is None:
            return
        try:
            ancho = self._lienzo.winfo_width()
            alto = self._lienzo.winfo_height()
        except tk.TclError:
            return
        if ancho < 50 or alto < 50 or (ancho, alto) == self._tamano_fondo:
            return

        original = self._fondo_original
        escala = max(ancho / original.width, alto / original.height)
        nuevo_ancho = math.ceil(original.width * escala)
        nuevo_alto = math.ceil(original.height * escala)
        imagen = original.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
        izquierda = (nuevo_ancho - ancho) // 2
        arriba = (nuevo_alto - alto) // 2
        imagen = imagen.crop(
            (izquierda, arriba, izquierda + ancho, arriba + alto)
        )

        try:
            self._foto_fondo = ImageTk.PhotoImage(imagen.convert("RGB"))
            self._lienzo.itemconfigure(self._id_fondo, image=self._foto_fondo)
            self._lienzo.tag_lower(self._id_fondo)
            self._tamano_fondo = (ancho, alto)
        except tk.TclError:
            pass

    # =========================================================
    # DISTRIBUCIÓN DEL CONTENIDO
    # =========================================================

    def _medir_bloque(self):
        """Calcula el alto total del contenido centrado."""
        self._alto_botones = max(
            (boton.winfo_reqheight() for _id, boton in self._ids_botones),
            default=80,
        )
        self._ancho_botones = max(
            (boton.winfo_reqwidth() for _id, boton in self._ids_botones),
            default=210,
        )
        self._alto_bloque = 340 + 2 * self._alto_botones + 20 + 150
        self._alto_minimo = self._alto_bloque + 90

    def _distribuir(self):
        lienzo = self._lienzo
        try:
            ancho = lienzo.winfo_width()
            alto = lienzo.winfo_height()
        except tk.TclError:
            return
        if ancho < 50 or alto < 50:
            return

        centro = ancho // 2
        y0 = max(40, (alto - self._alto_bloque) // 2 - 10)

        if self._id_icono is not None:
            lienzo.coords(self._id_icono, centro, y0)
        y_nombre = y0 + ALTO_ICONO + 38
        ancho_salu = self._fuente_logo.measure("Salu")
        ancho_total = ancho_salu + self._fuente_logo.measure("Pro")
        x_nombre = centro - ancho_total // 2
        lienzo.coords(self._id_logo_salu, x_nombre, y_nombre)
        lienzo.coords(self._id_logo_pro, x_nombre + ancho_salu, y_nombre)
        lienzo.coords(
            self._id_linea,
            centro - 70, y0 + ALTO_ICONO + 78,
            centro + 70, y0 + ALTO_ICONO + 81,
        )
        lienzo.coords(self._id_titulo, centro, y0 + 250)
        lienzo.coords(self._id_subtitulo, centro, y0 + 297)

        bw = self._ancho_botones
        bh = self._alto_botones
        separacion_x = 24
        separacion_y = 20
        izquierda = centro - (2 * bw + separacion_x) // 2
        arriba = y0 + 340
        for indice, (identificador, boton) in enumerate(self._ids_botones):
            fila, columna = divmod(indice, 2)
            x = izquierda + columna * (bw + separacion_x)
            y = arriba + fila * (bh + separacion_y)
            lienzo.coords(identificador, x, y)
            lienzo.itemconfigure(identificador, width=bw, height=bh)

        base = arriba + 2 * bh + separacion_y
        lienzo.coords(
            self._id_separador,
            centro - 250, base + 45, centro + 250, base + 46,
        )
        lienzo.coords(self._id_gestion, centro, base + 75)
        lienzo.coords(self._id_calidad, centro, base + 103)
        lienzo.coords(self._id_pie, centro, base + 143)

        lienzo.coords(self._id_salir, ancho - 20, alto - 20)

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
        self._solicitar_acceso("paciente")

    # =========================================================
    # BOTÓN ADMINISTRATIVA
    # =========================================================

    def abrir_administrativa(self):
        self._solicitar_acceso("administrativa")

    def abrir_profesional(self):
        """Abre el portal privado del profesional de salud."""
        self._solicitar_acceso("profesional")

    def abrir_enfermeria(self):
        """Abre el portal de acceso restringido para enfermería."""
        self._solicitar_acceso("enfermeria")

    def _solicitar_acceso(self, rol):
        from componentes.modal_verificador import ModalVerificador

        ModalVerificador(self.ventana, rol, self._acceso_concedido)

    def _acceso_concedido(self, sesion):
        for widget in self.ventana.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

        if sesion.rol == "paciente":
            from interfaz.pantalla_paciente import PantallaPaciente

            PantallaPaciente(self.ventana, self, sesion)
        elif sesion.rol == "administrativa":
            from interfaz.pantalla_administrativa import VentanaPrincipal

            VentanaPrincipal(
                self.ventana,
                pantalla_inicio=self,
                sesion=sesion,
            )
        elif sesion.rol == "profesional":
            from interfaz.pantalla_profesional import PantallaProfesional

            PantallaProfesional(self.ventana, self, sesion)
        elif sesion.rol == "enfermeria":
            from interfaz.pantalla_enfermeria import PantallaEnfermeria

            PantallaEnfermeria(self.ventana, self, sesion)

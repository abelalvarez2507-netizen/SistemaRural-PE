import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from modelos.paciente import Paciente
from modelos.personal_salud import PersonalSalud
from modelos.cita import Cita
from modelos.atencion_medica import AtencionMedica

from servicios.sistema_salud import SistemaSalud
from servicios.reportes import Reportes
from servicios.validaciones import validar_dni as validar_dni_valor

from interfaz.estilos import (
    COLOR_FONDO,
    COLOR_FONDO_SECUNDARIO,
    COLOR_PANEL,
    COLOR_PANEL_CLARO,
    COLOR_ROJO,
    COLOR_ROJO_CLARO,
    COLOR_ROJO_OSCURO,
    COLOR_BLANCO,
    COLOR_GRIS_CLARO,
    COLOR_GRIS,
    COLOR_GRIS_OSCURO,
    FUENTE_LOGO,
    FUENTE_TITULO,
    FUENTE_SUBTITULO,
    FUENTE_SECCION,
    FUENTE_NORMAL,
    FUENTE_NORMAL_BOLD,
    FUENTE_BOTON,
    FUENTE_BOTON_GRANDE,
    FUENTE_CODIGO,
    FUENTE_PEQUENA,
)


class PantallaInterna(tk.Frame):
    """Frame que reemplaza una Toplevel sin abrir una ventana nueva.

    Conserva los métodos más usados por el código original (title, geometry,
    minsize, transient, register) y hace que destroy() regrese a la pantalla
    anterior en lugar de cerrar la aplicación.
    """

    def __init__(self, master, volver_callback=None, titulo="SaluPro"):
        super().__init__(master, bg=COLOR_FONDO)
        self._root = master
        self._volver_callback = volver_callback
        self._titulo = titulo
        self._cerrando = False

    def title(self, titulo=None):
        if titulo is not None:
            self._titulo = titulo
        return self._titulo

    def geometry(self, *_args, **_kwargs):
        return None

    def minsize(self, *_args, **_kwargs):
        return None

    def transient(self, *_args, **_kwargs):
        return None

    def register(self, *args, **kwargs):
        return self._root.register(*args, **kwargs)

    def cerrar_sin_volver(self):
        self._cerrando = True
        tk.Frame.destroy(self)

    def destroy(self):
        if self._cerrando:
            return

        callback = self._volver_callback
        self._cerrando = True

        try:
            tk.Frame.destroy(self)
        finally:
            if callback is not None:
                callback()



class VentanaPrincipal:

    def __init__(self, ventana, pantalla_inicio=None):

        self.ventana = ventana
        self.pantalla_inicio = pantalla_inicio
        self._pantalla_principal = None
        self._pantalla_actual = None
        self._callback_volver_actual = None

        self.ventana.title(
            "SaluPro - Sistema de Salud Rural"
        )

        self.ventana.geometry(
            "1100x760"
        )
        self.ventana.minsize(
            950,
            680
        )
        self.ventana.resizable(
            True,
            True
        )

        try:
            self.ventana.state("zoomed")
        except tk.TclError:
            pass

        self.ventana.bind(
            "<F11>",
            self._alternar_pantalla_completa
        )

        self.ventana.configure(
            bg=COLOR_FONDO
        )

        # Apariencia general de los widgets Tkinter.
        self.ventana.option_add(
            "*Font",
            FUENTE_NORMAL
        )
        self.ventana.option_add(
            "*Background",
            COLOR_FONDO
        )
        self.ventana.option_add(
            "*Foreground",
            COLOR_BLANCO
        )
        self.ventana.option_add(
            "*Entry.Background",
            COLOR_PANEL_CLARO
        )
        self.ventana.option_add(
            "*Entry.Foreground",
            COLOR_BLANCO
        )
        self.ventana.option_add(
            "*Entry.InsertBackground",
            COLOR_BLANCO
        )
        self.ventana.option_add(
            "*Text.Background",
            COLOR_PANEL_CLARO
        )
        self.ventana.option_add(
            "*Text.Foreground",
            COLOR_BLANCO
        )
        self.ventana.option_add(
            "*Text.InsertBackground",
            COLOR_BLANCO
        )
        self.ventana.option_add(
            "*Button.Background",
            COLOR_ROJO
        )
        self.ventana.option_add(
            "*Button.Foreground",
            COLOR_BLANCO
        )
        self.ventana.option_add(
            "*Button.ActiveBackground",
            COLOR_ROJO_CLARO
        )
        self.ventana.option_add(
            "*Button.ActiveForeground",
            COLOR_BLANCO
        )
        self.ventana.option_add(
            "*OptionMenu.Background",
            COLOR_PANEL_CLARO
        )
        self.ventana.option_add(
            "*OptionMenu.Foreground",
            COLOR_BLANCO
        )
        self.ventana.option_add(
            "*OptionMenu.ActiveBackground",
            COLOR_ROJO
        )
        self.ventana.option_add(
            "*OptionMenu.ActiveForeground",
            COLOR_BLANCO
        )

        self.sistema = SistemaSalud()

        self.reportes = Reportes(
            self.sistema
        )

        self.crear_interfaz()

    # =========================================================
    # INTERFAZ PRINCIPAL
    # =========================================================

    def crear_interfaz(self):
        """Construye el panel administrativo principal de SaluPro."""

        # Siempre que se muestre el panel administrativo, ocupa toda la ventana.
        for widget in self.ventana.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

        self._pantalla_principal = None
        self._pantalla_actual = None
        self._callback_volver_actual = self.volver_panel_principal

        # =====================================================
        # CONTENEDOR CON SCROLL
        # =====================================================
        contenedor = tk.Frame(self.ventana, bg=COLOR_FONDO)
        contenedor.pack(fill="both", expand=True)

        self._pantalla_principal = contenedor
        self._pantalla_actual = contenedor

        canvas = tk.Canvas(
            contenedor,
            bg=COLOR_FONDO,
            highlightthickness=0,
            bd=0
        )
        scrollbar = tk.Scrollbar(
            contenedor,
            orient="vertical",
            command=canvas.yview
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        contenido = tk.Frame(canvas, bg=COLOR_FONDO)
        ventana_canvas = canvas.create_window(
            (0, 0),
            window=contenido,
            anchor="nw"
        )

        def actualizar_scroll(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def ajustar_ancho(event):
            canvas.itemconfigure(ventana_canvas, width=event.width)

        contenido.bind("<Configure>", actualizar_scroll)
        canvas.bind("<Configure>", ajustar_ancho)

        def rueda_mouse(event):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", rueda_mouse)

        interior = tk.Frame(contenido, bg=COLOR_FONDO)
        interior.pack(fill="both", expand=True, padx=30, pady=22)

        # =====================================================
        # DATOS DEL SISTEMA
        # =====================================================
        pacientes = self.sistema.obtener_pacientes()
        personal = self.sistema.obtener_personal()
        citas = self.sistema.obtener_citas()
        atenciones = self.sistema.obtener_atenciones()

        pendientes = [cita for cita in citas if cita.estado == "Pendiente"]
        reprogramar = [cita for cita in citas if cita.estado == "Reprogramar"]
        citas_atendidas = [cita for cita in citas if cita.estado == "Atendida"]
        finalizadas = [atencion for atencion in atenciones if atencion.estado == "Finalizada"]
        atenciones_proceso = [atencion for atencion in atenciones if atencion.estado == "En proceso"]

        def obtener_fecha_cita(cita):
            for formato in ("%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(str(cita.fecha), formato)
                except (ValueError, TypeError):
                    pass
            return datetime.max

        proximas = sorted(citas, key=obtener_fecha_cita)

        # =====================================================
        # ENCABEZADO / NAVEGACIÓN
        # =====================================================
        encabezado = tk.Frame(interior, bg=COLOR_FONDO)
        encabezado.pack(fill="x", pady=(0, 10))

        izquierda = tk.Frame(encabezado, bg=COLOR_FONDO)
        izquierda.pack(side="left")

        tk.Label(
            izquierda,
            text="SALUPRO",
            font=FUENTE_LOGO,
            bg=COLOR_FONDO,
            fg=COLOR_BLANCO
        ).pack(side="left")

        tk.Label(
            izquierda,
            text="  |  PANEL ADMINISTRATIVO",
            font=FUENTE_NORMAL_BOLD,
            bg=COLOR_FONDO,
            fg=COLOR_GRIS_CLARO
        ).pack(side="left", pady=7)

        acciones = tk.Frame(encabezado, bg=COLOR_FONDO)
        acciones.pack(side="right")

        boton_inicio = tk.Button(
            acciones,
            text="←  Volver",
            command=self.volver_a_inicio,
            font=FUENTE_BOTON,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=13,
            pady=8
        )
        boton_inicio.pack(side="left", padx=(0, 8))

        boton_actualizar = tk.Button(
            acciones,
            text="↻  Actualizar",
            command=self.actualizar_dashboard,
            font=FUENTE_BOTON,
            bg=COLOR_ROJO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO_CLARO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=13,
            pady=8
        )
        boton_actualizar.pack(side="left")

        for boton, color in (
            (boton_inicio, COLOR_PANEL_CLARO),
            (boton_actualizar, COLOR_ROJO),
        ):
            boton.bind(
                "<Enter>",
                lambda evento, b=boton, c=COLOR_ROJO_CLARO: b.configure(bg=c)
            )
            boton.bind(
                "<Leave>",
                lambda evento, b=boton, c=color: b.configure(bg=c)
            )

        tk.Frame(interior, bg=COLOR_ROJO, height=3).pack(fill="x", pady=(0, 18))

        # =====================================================
        # TÍTULO PRINCIPAL
        # =====================================================
        titulo_fila = tk.Frame(interior, bg=COLOR_FONDO)
        titulo_fila.pack(fill="x", pady=(0, 15))

        titulo_info = tk.Frame(titulo_fila, bg=COLOR_FONDO)
        titulo_info.pack(side="left", fill="x", expand=True)

        tk.Label(
            titulo_info,
            text="Gestión integral de salud",
            font=FUENTE_TITULO,
            bg=COLOR_FONDO,
            fg=COLOR_BLANCO
        ).pack(anchor="w")

        tk.Label(
            titulo_info,
            text="Todo el centro de salud en un solo lugar: pacientes, profesionales, citas, atenciones y reportes.",
            font=FUENTE_SUBTITULO,
            bg=COLOR_FONDO,
            fg=COLOR_GRIS
        ).pack(anchor="w", pady=(4, 0))

        # =====================================================
        # BÚSQUEDA GLOBAL
        # =====================================================
        busqueda = tk.Frame(
            interior,
            bg=COLOR_PANEL,
            highlightbackground=COLOR_PANEL_CLARO,
            highlightthickness=1
        )
        busqueda.pack(fill="x", pady=(0, 16))

        tk.Label(
            busqueda,
            text="⌕",
            font=("Arial", 22, "bold"),
            bg=COLOR_PANEL,
            fg=COLOR_ROJO
        ).pack(side="left", padx=(16, 8), pady=12)

        info_busqueda = tk.Frame(busqueda, bg=COLOR_PANEL)
        info_busqueda.pack(side="left", fill="x", expand=True, pady=10)

        tk.Label(
            info_busqueda,
            text="BÚSQUEDA RÁPIDA",
            font=FUENTE_NORMAL_BOLD,
            bg=COLOR_PANEL,
            fg=COLOR_BLANCO
        ).pack(anchor="w")

        tk.Label(
            info_busqueda,
            text="Busca un paciente o profesional por código o DNI.",
            font=FUENTE_PEQUENA,
            bg=COLOR_PANEL,
            fg=COLOR_GRIS
        ).pack(anchor="w")

        entrada_global = tk.Entry(
            busqueda,
            width=30,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            insertbackground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            font=FUENTE_NORMAL
        )
        entrada_global.pack(side="left", padx=8, ipady=7)
        self.configurar_limite_busqueda(entrada_global)

        boton_buscar_global = tk.Button(
            busqueda,
            text="Buscar",
            command=lambda: self.buscar_global(entrada_global.get()),
            font=FUENTE_BOTON,
            bg=COLOR_ROJO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO_CLARO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=16,
            pady=7
        )
        boton_buscar_global.pack(side="right", padx=16)
        entrada_global.bind(
            "<Return>",
            lambda evento: self.buscar_global(entrada_global.get())
        )

        # =====================================================
        # TARJETAS DE RESUMEN
        # =====================================================
        tk.Label(
            interior,
            text="RESUMEN DEL CENTRO",
            font=FUENTE_SECCION,
            bg=COLOR_FONDO,
            fg=COLOR_BLANCO
        ).pack(anchor="w", pady=(0, 6))

        resumen = tk.Frame(interior, bg=COLOR_FONDO)
        resumen.pack(fill="x", pady=(0, 15))

        for columna in range(3):
            resumen.columnconfigure(columna, weight=1, uniform="resumen")

        datos_resumen = [
            ("👥", "TOTAL DE PACIENTES", len(pacientes), "registrados"),
            ("⚕", "TOTAL DE PROFESIONALES", len(personal), "registrados"),
            ("📅", "CITAS PENDIENTES", len(pendientes), "por atender"),
            ("🔄", "CITAS PARA REPROGRAMAR", len(reprogramar), "requieren seguimiento"),
            ("🩺", "TOTAL DE ATENCIONES", len(atenciones), f"{len(finalizadas)} finalizadas"),
            ("🕐", "PRÓXIMAS CITAS", len(proximas), "en la agenda"),
        ]

        for indice, (icono, titulo, valor, detalle) in enumerate(datos_resumen):
            fila = indice // 3
            columna = indice % 3

            tarjeta = tk.Frame(
                resumen,
                bg=COLOR_PANEL,
                highlightbackground=COLOR_PANEL_CLARO,
                highlightthickness=1
            )
            tarjeta.grid(
                row=fila,
                column=columna,
                sticky="nsew",
                padx=5,
                pady=5
            )

            cabecera = tk.Frame(tarjeta, bg=COLOR_PANEL)
            cabecera.pack(fill="x", padx=14, pady=(11, 0))

            tk.Label(
                cabecera,
                text=icono,
                font=("Arial", 19, "bold"),
                bg=COLOR_PANEL,
                fg=COLOR_ROJO
            ).pack(side="left")

            tk.Label(
                cabecera,
                text=titulo,
                font=FUENTE_PEQUENA,
                bg=COLOR_PANEL,
                fg=COLOR_GRIS_CLARO,
                wraplength=210,
                justify="left"
            ).pack(side="left", padx=8)

            tk.Label(
                tarjeta,
                text=str(valor),
                font=("Arial", 25, "bold"),
                bg=COLOR_PANEL,
                fg=COLOR_BLANCO
            ).pack(anchor="w", padx=14, pady=(2, 0))

            tk.Label(
                tarjeta,
                text=detalle,
                font=FUENTE_PEQUENA,
                bg=COLOR_PANEL,
                fg=COLOR_GRIS
            ).pack(anchor="w", padx=14, pady=(0, 11))

        # =====================================================
        # AGENDA + ESTADO GENERAL
        # =====================================================
        centro = tk.Frame(interior, bg=COLOR_FONDO)
        centro.pack(fill="x", pady=(0, 16))
        centro.columnconfigure(0, weight=3, uniform="centro")
        centro.columnconfigure(1, weight=2, uniform="centro")

        panel_citas = tk.Frame(
            centro,
            bg=COLOR_PANEL,
            highlightbackground=COLOR_PANEL_CLARO,
            highlightthickness=1
        )
        panel_citas.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        tk.Label(
            panel_citas,
            text="PRÓXIMAS CITAS",
            font=FUENTE_SECCION,
            bg=COLOR_PANEL,
            fg=COLOR_BLANCO
        ).pack(anchor="w", padx=16, pady=(13, 2))

        tk.Label(
            panel_citas,
            text="Vista rápida de la agenda registrada.",
            font=FUENTE_PEQUENA,
            bg=COLOR_PANEL,
            fg=COLOR_GRIS
        ).pack(anchor="w", padx=16, pady=(0, 9))

        lista_citas = tk.Frame(panel_citas, bg=COLOR_PANEL)
        lista_citas.pack(fill="x", padx=16, pady=(0, 13))

        if proximas:
            for cita in proximas[:6]:
                fila_cita = tk.Frame(lista_citas, bg=COLOR_PANEL_CLARO)
                fila_cita.pack(fill="x", pady=2)

                tk.Label(
                    fila_cita,
                    text=str(cita.fecha),
                    font=FUENTE_NORMAL_BOLD,
                    bg=COLOR_PANEL_CLARO,
                    fg=COLOR_ROJO_CLARO,
                    width=13,
                    anchor="w"
                ).pack(side="left", padx=10, pady=7)

                nombre_paciente = getattr(
                    getattr(cita, "paciente", None),
                    "nombre",
                    "Paciente"
                )
                nombre_profesional = getattr(
                    getattr(cita, "profesional", None),
                    "nombre",
                    "Profesional"
                )

                datos = tk.Frame(fila_cita, bg=COLOR_PANEL_CLARO)
                datos.pack(side="left", fill="x", expand=True, padx=4, pady=5)

                tk.Label(
                    datos,
                    text=str(nombre_paciente),
                    font=FUENTE_NORMAL_BOLD,
                    bg=COLOR_PANEL_CLARO,
                    fg=COLOR_BLANCO,
                    anchor="w"
                ).pack(anchor="w")

                tk.Label(
                    datos,
                    text=str(nombre_profesional),
                    font=FUENTE_PEQUENA,
                    bg=COLOR_PANEL_CLARO,
                    fg=COLOR_GRIS_CLARO,
                    anchor="w"
                ).pack(anchor="w")

                tk.Label(
                    fila_cita,
                    text=str(cita.estado),
                    font=FUENTE_PEQUENA,
                    bg=COLOR_PANEL_CLARO,
                    fg=COLOR_GRIS_CLARO,
                    width=14
                ).pack(side="right", padx=10)
        else:
            tk.Label(
                lista_citas,
                text="No hay citas registradas todavía.",
                font=FUENTE_NORMAL,
                bg=COLOR_PANEL,
                fg=COLOR_GRIS
            ).pack(anchor="w", pady=10)

        panel_estado = tk.Frame(
            centro,
            bg=COLOR_PANEL,
            highlightbackground=COLOR_PANEL_CLARO,
            highlightthickness=1
        )
        panel_estado.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        tk.Label(
            panel_estado,
            text="📊 ESTADO DEL CENTRO",
            font=FUENTE_SECCION,
            bg=COLOR_PANEL,
            fg=COLOR_BLANCO
        ).pack(anchor="w", padx=16, pady=(13, 10))

        estado_resumen = [
            ("Pacientes registrados", len(pacientes)),
            ("Profesionales registrados", len(personal)),
            ("Citas registradas", len(citas)),
            ("Citas pendientes", len(pendientes)),
            ("Citas atendidas", len(citas_atendidas)),
            ("Para reprogramar", len(reprogramar)),
            ("Atenciones en proceso", len(atenciones_proceso)),
            ("Atenciones finalizadas", len(finalizadas)),
        ]

        for nombre, cantidad in estado_resumen:
            fila_estado = tk.Frame(panel_estado, bg=COLOR_PANEL)
            fila_estado.pack(fill="x", padx=16, pady=3)

            tk.Label(
                fila_estado,
                text=nombre,
                font=FUENTE_PEQUENA,
                bg=COLOR_PANEL,
                fg=COLOR_GRIS_CLARO
            ).pack(side="left")

            tk.Label(
                fila_estado,
                text=str(cantidad),
                font=FUENTE_NORMAL_BOLD,
                bg=COLOR_PANEL,
                fg=COLOR_BLANCO
            ).pack(side="right")

        aviso = (
            "Hay citas pendientes de atención."
            if pendientes
            else "No hay citas pendientes actualmente."
        )

        tk.Label(
            panel_estado,
            text=aviso,
            font=FUENTE_PEQUENA,
            bg=COLOR_PANEL,
            fg=COLOR_GRIS,
            wraplength=330,
            justify="left"
        ).pack(anchor="w", padx=16, pady=(9, 13))

        # =====================================================
        # MÓDULOS PRINCIPALES
        # =====================================================
        tk.Label(
            interior,
            text="MÓDULOS DEL SISTEMA",
            font=FUENTE_SECCION,
            bg=COLOR_FONDO,
            fg=COLOR_BLANCO
        ).pack(anchor="w", pady=(0, 6))

        zona = tk.Frame(interior, bg=COLOR_FONDO)
        zona.pack(fill="x", pady=(0, 12))

        for columna in range(3):
            zona.columnconfigure(columna, weight=1, uniform="modulos")

        def crear_modulo(
            fila,
            columna,
            icono,
            titulo,
            descripcion,
            cantidad,
            detalle,
            texto_boton,
            comando
        ):
            tarjeta = tk.Frame(
                zona,
                bg=COLOR_PANEL,
                highlightbackground=COLOR_PANEL_CLARO,
                highlightthickness=1
            )
            tarjeta.grid(
                row=fila,
                column=columna,
                sticky="nsew",
                padx=7,
                pady=7
            )

            superior = tk.Frame(tarjeta, bg=COLOR_PANEL)
            superior.pack(fill="x", padx=16, pady=(15, 5))

            tk.Label(
                superior,
                text=icono,
                font=("Arial", 22, "bold"),
                bg=COLOR_PANEL,
                fg=COLOR_ROJO
            ).pack(side="left")

            tk.Label(
                superior,
                text=titulo,
                font=FUENTE_SECCION,
                bg=COLOR_PANEL,
                fg=COLOR_BLANCO,
                wraplength=235,
                justify="left"
            ).pack(side="left", padx=9)

            tk.Label(
                tarjeta,
                text=descripcion,
                font=FUENTE_PEQUENA,
                bg=COLOR_PANEL,
                fg=COLOR_GRIS,
                wraplength=290,
                justify="left"
            ).pack(anchor="w", padx=16, pady=(0, 10))

            estadistica = tk.Frame(tarjeta, bg=COLOR_PANEL_CLARO)
            estadistica.pack(fill="x", padx=16, pady=(0, 12))

            tk.Label(
                estadistica,
                text=str(cantidad),
                font=("Arial", 17, "bold"),
                bg=COLOR_PANEL_CLARO,
                fg=COLOR_BLANCO
            ).pack(side="left", padx=10, pady=7)

            tk.Label(
                estadistica,
                text=detalle,
                font=FUENTE_PEQUENA,
                bg=COLOR_PANEL_CLARO,
                fg=COLOR_GRIS_CLARO
            ).pack(side="left", padx=(0, 8))

            boton = tk.Button(
                tarjeta,
                text=texto_boton,
                command=comando,
                font=FUENTE_BOTON,
                bg=COLOR_ROJO,
                fg=COLOR_BLANCO,
                activebackground=COLOR_ROJO_CLARO,
                activeforeground=COLOR_BLANCO,
                relief="flat",
                bd=0,
                cursor="hand2",
                padx=12,
                pady=8,
                width=22
            )
            boton.pack(anchor="center", pady=(0, 15), ipadx=5)

            boton.bind(
                "<Enter>",
                lambda evento, b=boton: b.configure(bg=COLOR_ROJO_CLARO)
            )
            boton.bind(
                "<Leave>",
                lambda evento, b=boton: b.configure(bg=COLOR_ROJO)
            )

        crear_modulo(
            0, 0, "👥", "GESTIÓN DE PACIENTES",
            "Registre pacientes, consulte sus datos y revise su historial clínico.",
            len(pacientes), "pacientes registrados",
            "Gestionar pacientes", self.gestion_pacientes
        )

        crear_modulo(
            0, 1, "⚕", "GESTIÓN DE PROFESIONALES",
            "Administre el personal de salud y consulte la actividad registrada.",
            len(personal), "profesionales registrados",
            "Gestionar profesionales", self.gestion_profesionales
        )

        crear_modulo(
            0, 2, "📅", "GESTIÓN DE CITAS",
            "Administre la agenda, los estados y las citas que requieren seguimiento.",
            len(citas), "citas en agenda",
            "Gestionar citas", self.gestion_citas
        )

        crear_modulo(
            1, 0, "🩺", "ATENCIONES MÉDICAS",
            "Registre diagnósticos, consulte atenciones y actualice sus estados.",
            len(atenciones), "atenciones registradas",
            "Gestionar atenciones", self.gestion_atenciones
        )

        crear_modulo(
            1, 1, "📊", "REPORTES Y ESTADÍSTICAS",
            "Consulte indicadores generales y reportes de pacientes, citas y atenciones.",
            len(finalizadas), "atenciones finalizadas",
            "Ver reportes", self.gestion_reportes
        )

        crear_modulo(
            1, 2, "⌕", "BÚSQUEDA GLOBAL",
            "Acceda rápidamente a pacientes o profesionales usando código o DNI.",
            len(pacientes) + len(personal), "registros consultables",
            "Buscar registros", lambda: self.buscar_global_desde_panel()
        )

        # =====================================================
        # PIE DEL PANEL
        # =====================================================
        pie = tk.Frame(interior, bg=COLOR_FONDO)
        pie.pack(fill="x", pady=(5, 8))

        tk.Frame(pie, bg=COLOR_PANEL_CLARO, height=1).pack(fill="x", pady=(0, 9))

        tk.Label(
            pie,
            text="SaluPro • Sistema de Salud Rural • Panel administrativo",
            font=FUENTE_PEQUENA,
            bg=COLOR_FONDO,
            fg=COLOR_GRIS_OSCURO
        ).pack(side="left")

        tk.Button(
            pie,
            text="Salir",
            command=self.ventana.destroy,
            font=FUENTE_PEQUENA,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=5
        ).pack(side="right")

        for widget in (contenido, interior, zona):
            widget.bind("<MouseWheel>", rueda_mouse)

        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _alternar_pantalla_completa(self, evento=None):
        try:
            actual = bool(self.ventana.attributes("-fullscreen"))
            self.ventana.attributes("-fullscreen", not actual)
        except tk.TclError:
            try:
                estado = self.ventana.state()
                self.ventana.state("normal" if estado == "zoomed" else "zoomed")
            except tk.TclError:
                pass

    def volver_panel_principal(self):
        """Regresa al panel administrativo dentro de la misma ventana."""
        actual = self._pantalla_actual

        if actual is not None and actual is not self._pantalla_principal:
            try:
                actual._cerrando = True
                tk.Frame.destroy(actual)
            except (tk.TclError, AttributeError):
                pass

        if self._pantalla_principal is not None:
            try:
                self._pantalla_principal.pack(fill="both", expand=True)
                self._pantalla_principal.lift()
            except tk.TclError:
                pass

        self._pantalla_actual = self._pantalla_principal
        self._callback_volver_actual = self.volver_panel_principal

    def volver_a_inicio(self):
        """Reemplaza la pantalla administrativa por la pantalla de inicio."""
        try:
            self.sistema.cerrar()
        except Exception:
            pass

        if self.pantalla_inicio is not None:
            self._pantalla_actual = None
            self._pantalla_principal = None
            self._callback_volver_actual = None
            self.pantalla_inicio.mostrar()
            return

        from interfaz.pantalla_inicio import PantallaInicio
        PantallaInicio(self.ventana).mostrar()

    def _limpiar_pantalla_actual(self):
        """Elimina la pantalla actual sin abrir ni cerrar ventanas."""
        actual = self._pantalla_actual

        if actual is None:
            return

        if actual is self._pantalla_principal:
            try:
                actual.pack_forget()
            except tk.TclError:
                pass
            return

        try:
            actual.cerrar_sin_volver()
        except AttributeError:
            try:
                actual.destroy()
            except tk.TclError:
                pass

    def _crear_pantalla_interna(self, titulo="SaluPro"):
        """Crea una pantalla dentro de la misma ventana principal."""
        callback = self._callback_volver_actual or self.volver_panel_principal

        self._limpiar_pantalla_actual()

        ventana = PantallaInterna(
            self.ventana,
            volver_callback=callback,
            titulo=titulo
        )
        ventana.pack(fill="both", expand=True)
        self._pantalla_actual = ventana

        barra = tk.Frame(ventana, bg=COLOR_FONDO)
        barra.pack(fill="x", padx=24, pady=(18, 0))

        boton_volver = tk.Button(
            barra,
            text="←  Volver",
            command=ventana.destroy,
            font=FUENTE_BOTON,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=13,
            pady=8
        )
        boton_volver.pack(side="left")

        boton_volver.bind(
            "<Enter>",
            lambda evento: boton_volver.configure(bg=COLOR_ROJO_CLARO)
        )
        boton_volver.bind(
            "<Leave>",
            lambda evento: boton_volver.configure(bg=COLOR_PANEL_CLARO)
        )

        return ventana

    def _abrir_desde_menu(self, comando, volver_callback):
        """Ejecuta una opción de menú conservando el destino de Volver."""
        self._callback_volver_actual = volver_callback
        comando()

    def buscar_global(self, valor):
        """Busca un paciente o profesional por código o DNI."""
        valor = str(valor).strip()

        if not valor:
            messagebox.showwarning(
                "Búsqueda rápida",
                "Ingrese un código o DNI para realizar la búsqueda."
            )
            return

        pacientes_encontrados = list(
            self.sistema.buscar_paciente_por_codigo(valor)
        )

        profesionales_encontrados = list(
            self.sistema.buscar_personal_por_codigo(valor)
        )

        if valor.isdigit() and len(valor) == 8:
            for paciente in self.sistema.buscar_paciente_por_dni(valor):
                if paciente not in pacientes_encontrados:
                    pacientes_encontrados.append(paciente)

            for profesional in self.sistema.buscar_personal_por_dni(valor):
                if profesional not in profesionales_encontrados:
                    profesionales_encontrados.append(profesional)

        if not pacientes_encontrados and not profesionales_encontrados:
            messagebox.showinfo(
                "Búsqueda rápida",
                "No se encontraron pacientes ni profesionales con ese código o DNI."
            )
            return

        ventana = self._crear_pantalla_interna()
        ventana.title("Búsqueda rápida - SaluPro")
        ventana.geometry("760x560")
        ventana.configure(bg=COLOR_FONDO)
        ventana.transient(self.ventana)

        marco = tk.Frame(ventana, bg=COLOR_FONDO)
        marco.pack(fill="both", expand=True, padx=25, pady=22)

        tk.Label(
            marco,
            text="RESULTADO DE BÚSQUEDA",
            font=FUENTE_TITULO,
            bg=COLOR_FONDO,
            fg=COLOR_BLANCO
        ).pack(pady=(0, 5))

        valor_mostrado = (
            "********"
            if valor.isdigit() and len(valor) == 8
            else valor
        )

        tk.Label(
            marco,
            text=f"Coincidencias para: {valor_mostrado}",
            font=FUENTE_SUBTITULO,
            bg=COLOR_FONDO,
            fg=COLOR_GRIS
        ).pack(pady=(0, 15))

        texto = tk.Text(
            marco,
            wrap="word",
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            insertbackground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            font=FUENTE_NORMAL,
            padx=14,
            pady=12
        )
        texto.pack(fill="both", expand=True)

        if pacientes_encontrados:
            texto.insert(tk.END, "PACIENTES\n")
            texto.insert(tk.END, "=" * 60 + "\n\n")
            for paciente in pacientes_encontrados:
                texto.insert(tk.END, paciente.mostrar_informacion() + "\n\n")

        if profesionales_encontrados:
            texto.insert(tk.END, "PROFESIONALES\n")
            texto.insert(tk.END, "=" * 60 + "\n\n")
            for profesional in profesionales_encontrados:
                texto.insert(tk.END, profesional.mostrar_informacion() + "\n\n")

        texto.config(state="disabled")

        tk.Button(
            marco,
            text="←  Volver",
            command=ventana.destroy,
            font=FUENTE_BOTON,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            width=18,
            pady=7
        ).pack(pady=(14, 0))

    def buscar_global_desde_panel(self):
        """Abre una ventana de búsqueda global desde el módulo del dashboard."""
        ventana = self._crear_pantalla_interna()
        ventana.title("Búsqueda global - SaluPro")
        ventana.geometry("520x250")
        ventana.configure(bg=COLOR_FONDO)
        ventana.transient(self.ventana)

        marco = tk.Frame(ventana, bg=COLOR_FONDO)
        marco.pack(fill="both", expand=True, padx=30, pady=28)

        tk.Label(
            marco,
            text="BÚSQUEDA GLOBAL",
            font=FUENTE_TITULO,
            bg=COLOR_FONDO,
            fg=COLOR_BLANCO
        ).pack(pady=(0, 5))

        tk.Label(
            marco,
            text="Código de paciente/profesional o DNI",
            font=FUENTE_NORMAL,
            bg=COLOR_FONDO,
            fg=COLOR_GRIS
        ).pack(pady=(0, 12))

        entrada = tk.Entry(
            marco,
            width=35,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            insertbackground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            font=FUENTE_NORMAL
        )
        entrada.pack(ipady=8)
        self.configurar_limite_busqueda(entrada)

        def ejecutar_busqueda():
            valor = entrada.get()
            if not valor.strip():
                messagebox.showwarning(
                    "Búsqueda global",
                    "Ingrese un código o DNI."
                )
                return
            ventana.cerrar_sin_volver()
            self.buscar_global(valor)

        tk.Button(
            marco,
            text="🔎  Buscar",
            command=ejecutar_busqueda,
            font=FUENTE_BOTON,
            bg=COLOR_ROJO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO_CLARO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            width=20,
            pady=8
        ).pack(pady=18)

        entrada.bind("<Return>", lambda evento: ejecutar_busqueda())
        entrada.focus_set()

    def _crear_menu_gestion(self, titulo, descripcion, opciones, ancho=500, alto=500):
        """Muestra el menú de gestión dentro de la misma ventana principal."""

        # El botón Volver de este menú regresa al panel administrativo.
        self._callback_volver_actual = self.volver_panel_principal
        self._limpiar_pantalla_actual()

        ventana = tk.Frame(
            self.ventana,
            bg=COLOR_FONDO
        )
        ventana.pack(
            fill="both",
            expand=True
        )

        self._pantalla_actual = ventana

        contenedor = tk.Frame(
            ventana,
            bg=COLOR_FONDO
        )
        contenedor.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=25
        )

        barra_navegacion = tk.Frame(
            contenedor,
            bg=COLOR_FONDO
        )
        barra_navegacion.pack(
            fill="x",
            pady=(0, 8)
        )

        boton_panel = tk.Button(
            barra_navegacion,
            text="←  Volver",
            command=self.volver_panel_principal,
            font=FUENTE_BOTON,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=7
        )
        boton_panel.pack(side="left")

        boton_panel.bind(
            "<Enter>",
            lambda evento: boton_panel.configure(bg=COLOR_ROJO_CLARO)
        )
        boton_panel.bind(
            "<Leave>",
            lambda evento: boton_panel.configure(bg=COLOR_PANEL_CLARO)
        )

        tk.Label(
            contenedor,
            text=titulo.upper(),
            font=FUENTE_TITULO,
            bg=COLOR_FONDO,
            fg=COLOR_BLANCO
        ).pack(
            pady=(5, 6)
        )

        tk.Label(
            contenedor,
            text=descripcion,
            font=FUENTE_SUBTITULO,
            bg=COLOR_FONDO,
            fg=COLOR_GRIS,
            wraplength=650,
            justify="center"
        ).pack(
            pady=(0, 20)
        )

        tk.Frame(
            contenedor,
            bg=COLOR_ROJO,
            height=2
        ).pack(
            fill="x",
            pady=(0, 18)
        )

        def ejecutar_opcion(comando):
            # Al entrar a un submódulo, Volver reconstruye exactamente este menú.
            callback_menu = lambda: self._crear_menu_gestion(
                titulo,
                descripcion,
                opciones,
                ancho,
                alto
            )
            self._abrir_desde_menu(comando, callback_menu)

        for texto, comando in opciones:
            boton = tk.Button(
                contenedor,
                text=texto,
                command=lambda c=comando: ejecutar_opcion(c),
                font=FUENTE_BOTON_GRANDE,
                bg=COLOR_ROJO,
                fg=COLOR_BLANCO,
                activebackground=COLOR_ROJO_CLARO,
                activeforeground=COLOR_BLANCO,
                relief="flat",
                bd=0,
                cursor="hand2",
                width=30,
                pady=10
            )
            boton.pack(
                pady=6
            )

            boton.bind(
                "<Enter>",
                lambda evento, b=boton: b.configure(bg=COLOR_ROJO_CLARO)
            )
            boton.bind(
                "<Leave>",
                lambda evento, b=boton: b.configure(bg=COLOR_ROJO)
            )

        return ventana

    def gestion_pacientes(self):
        """Agrupa todas las funciones relacionadas con pacientes."""
        self._crear_menu_gestion(
            "Gestión de pacientes",
            "Administre los pacientes registrados y consulte su historial.",
            [
                ("Registrar paciente", self.registrar_paciente),
                ("Ver pacientes", self.ver_pacientes),
                ("Buscar paciente", self.buscar_paciente),
                ("Historial de pacientes", self.historial_pacientes),
            ],
            ancho=520,
            alto=520
        )

    def gestion_profesionales(self):
        """Agrupa todas las funciones relacionadas con profesionales."""
        self._crear_menu_gestion(
            "Gestión de profesionales",
            "Administre el personal de salud y consulte su actividad registrada.",
            [
                ("Registrar profesional", self.registrar_personal),
                ("Ver profesionales", self.ver_personal),
                ("Buscar profesional", self.buscar_personal),
                ("Historial de profesionales", self.historial_profesionales),
            ],
            ancho=540,
            alto=520
        )

    def gestion_citas(self):
        """Agrupa las funciones de agenda y estados de citas."""
        self._crear_menu_gestion(
            "Gestión de citas",
            "Administre la agenda, consulte citas y actualice sus estados.",
            [
                ("Registrar cita", self.registrar_cita),
                ("Citas pendientes", self.ver_citas),
                ("Cambiar estado", self.cambiar_estado_cita),
                ("Citas para reprogramar", self.ver_citas_reprogramadas),
            ],
            ancho=520,
            alto=520
        )

    def gestion_atenciones(self):
        """Agrupa las funciones de atenciones médicas."""
        self._crear_menu_gestion(
            "Atenciones médicas",
            "Consulte, registre y actualice las atenciones asociadas a las citas.",
            [
                ("Registrar atención", self.registrar_atencion),
                ("Ver atenciones", self.ver_atenciones),
                ("Cambiar estado", self.cambiar_estado_atencion),
            ],
            ancho=520,
            alto=460
        )

    def gestion_reportes(self):
        """Agrupa estadísticas y reportes del sistema."""
        self._crear_menu_gestion(
            "Reportes y estadísticas",
            "Consulte los principales indicadores y reportes generados por SaluPro.",
            [
                ("Ver estadísticas", self.ver_estadisticas),
                ("Ver reportes", self.ver_reportes),
            ],
            ancho=520,
            alto=400
        )

    def actualizar_dashboard(self):
        """Recarga el panel para mostrar los datos actuales."""
        for widget in self.ventana.winfo_children():
            widget.destroy()

        self.crear_interfaz()

    # =========================================================
    # VALIDACIÓN DNI
    # =========================================================

    def validar_dni(self, dni):
        """Delega la validación del DNI a la capa común de dominio."""
        return validar_dni_valor(dni)

    # =========================================================
    # CREAR CAMPO DNI
    # =========================================================

    def crear_campo_dni(self, ventana):

        marco = tk.Frame(
            ventana
        )

        marco.pack(
            pady=5
        )

        tk.Label(
            marco,
            text="DNI:"
        ).pack()

        entrada = tk.Entry(
            marco,
            width=35
        )

        entrada.pack()

        def validar_caracteres(nuevo_valor):

            if nuevo_valor == "":
                return True

            return (
                nuevo_valor.isdigit()
                and len(nuevo_valor) <= 8
            )

        validacion = (
            ventana.register(
                validar_caracteres
            )
        )

        entrada.config(
            validate="key",
            validatecommand=(
                validacion,
                "%P"
            )
        )

        return entrada

    def validar_entrada_busqueda(self, nuevo_valor, maximo=8):
        """Valida entradas de búsqueda sin permitir símbolos ni exceso de longitud."""
        if nuevo_valor == "":
            return True
        return nuevo_valor.isalnum() and len(nuevo_valor) <= maximo

    def configurar_limite_busqueda(self, entrada, ventana=None, maximo=8):
        """Configura el límite de caracteres de un campo de búsqueda."""
        registro = ventana if ventana is not None else self.ventana

        validacion = registro.register(
            lambda valor: self.validar_entrada_busqueda(valor, maximo)
        )

        entrada.config(
            validate="key",
            validatecommand=(validacion, "%P")
        )
        return entrada

    # =========================================================
    # FECHA
    # =========================================================

    def crear_campo_fecha(self, ventana):

        marco = tk.Frame(
            ventana
        )

        marco.pack(
            pady=5
        )

        entrada = tk.Entry(
            marco,
            width=25,
            fg="gray"
        )

        entrada.pack()

        entrada.insert(
            0,
            "DD/MM/AAAA"
        )

        entrada.placeholder_activo = True

        def entrar(evento):

            if entrada.placeholder_activo:

                entrada.delete(
                    0,
                    tk.END
                )

                entrada.config(
                    fg="black"
                )

                entrada.placeholder_activo = False

        def salir(evento):

            if not entrada.get():

                entrada.insert(
                    0,
                    "DD/MM/AAAA"
                )

                entrada.config(
                    fg="gray"
                )

                entrada.placeholder_activo = True

        def formatear(evento):

            if entrada.placeholder_activo:
                return

            if evento.keysym in (
                "BackSpace",
                "Delete",
                "Left",
                "Right",
                "Up",
                "Down",
                "Tab"
            ):

                return

            contenido = entrada.get()

            solo_numeros = "".join(
                caracter
                for caracter in contenido
                if caracter.isdigit()
            )

            solo_numeros = solo_numeros[:8]

            if len(solo_numeros) >= 5:

                contenido_formateado = (
                    solo_numeros[:2]
                    + "/"
                    + solo_numeros[2:4]
                    + "/"
                    + solo_numeros[4:]
                )

            elif len(solo_numeros) >= 3:

                contenido_formateado = (
                    solo_numeros[:2]
                    + "/"
                    + solo_numeros[2:]
                )

            else:

                contenido_formateado = (
                    solo_numeros
                )

            entrada.delete(
                0,
                tk.END
            )

            entrada.insert(
                0,
                contenido_formateado
            )

        entrada.bind(
            "<FocusIn>",
            entrar
        )

        entrada.bind(
            "<FocusOut>",
            salir
        )

        entrada.bind(
            "<KeyRelease>",
            formatear
        )

        return entrada

    # =========================================================
    # VALIDAR FECHA
    # =========================================================

    def validar_fecha(self, fecha):

        try:

            fecha = fecha.strip()

            fecha_convertida = datetime.strptime(
                fecha,
                "%d/%m/%Y"
            )

        except ValueError:

            raise ValueError(
                "La fecha debe tener el formato "
                "DD/MM/AAAA y ser una fecha válida."
            )

        año = fecha_convertida.year

        if año < 2026 or año > 2035:

            raise ValueError(
                "El año debe estar entre 2026 y 2035."
            )

        return True

    # =========================================================
    # GENERAR CÓDIGO PROFESIONAL
    # =========================================================

    def generar_codigo_profesional(self):

        personal = (
            self.sistema.obtener_personal()
        )

        numero = 1

        while True:

            codigo = f"CMP{numero:03d}"

            existe = any(
                profesional.codigo_profesional
                == codigo
                for profesional in personal
            )

            if not existe:

                return codigo

            numero += 1

    # =========================================================
    # VER PACIENTES
    # =========================================================

    def ver_pacientes(self):

        ventana = self._crear_pantalla_interna()

        ventana.title(
            "Pacientes registrados"
        )

        ventana.geometry(
            "750x450"
        )

        texto = tk.Text(
            ventana,
            width=90,
            height=23
        )

        texto.pack(
            padx=10,
            pady=10
        )

        pacientes = (
            self.sistema.obtener_pacientes()
        )

        if not pacientes:

            texto.insert(
                tk.END,
                "No existen pacientes registrados."
            )

            return

        for paciente in pacientes:

            texto.insert(
                tk.END,
                paciente.mostrar_informacion()
                + "\n\n"
            )

    # =========================================================
    # REGISTRAR PACIENTE
    # =========================================================

    def registrar_paciente(self):

        ventana = self._crear_pantalla_interna()

        ventana.title(
            "Registrar paciente"
        )

        ventana.geometry(
            "450x430"
        )

        codigo_generado = (
            self.sistema.generar_codigo_paciente()
        )

        tk.Label(
            ventana,
            text="Código de paciente:"
        ).pack(
            pady=5
        )

        tk.Label(
            ventana,
            text=codigo_generado,
            font=("Arial", 14, "bold")
        ).pack(
            pady=5
        )

        tk.Label(
            ventana,
            text="DNI:"
        ).pack(
            pady=5
        )

        entrada_dni = tk.Entry(
            ventana,
            width=35
        )

        entrada_dni.pack()

        def validar_dni_tecla(nuevo_valor):

            if nuevo_valor == "":
                return True

            return (
                nuevo_valor.isdigit()
                and len(nuevo_valor) <= 8
            )

        validacion = ventana.register(
            validar_dni_tecla
        )

        entrada_dni.config(
            validate="key",
            validatecommand=(
                validacion,
                "%P"
            )
        )

        tk.Label(
            ventana,
            text="Nombre:"
        ).pack(
            pady=5
        )

        entrada_nombre = tk.Entry(
            ventana,
            width=35
        )

        entrada_nombre.pack()

        tk.Label(
            ventana,
            text="Edad:"
        ).pack(
            pady=5
        )

        entrada_edad = tk.Entry(
            ventana,
            width=35
        )

        entrada_edad.pack()

        def guardar():

            try:

                dni = self.validar_dni(
                    entrada_dni.get()
                )

                paciente = Paciente(
                    codigo_generado,
                    dni,
                    entrada_nombre.get(),
                    int(entrada_edad.get())
                )

                self.sistema.registrar_paciente(
                    paciente
                )

                messagebox.showinfo(
                    "Éxito",
                    (
                        "Paciente registrado correctamente.\n\n"
                        f"Código asignado: "
                        f"{codigo_generado}\n"
                        "DNI almacenado de forma protegida."
                    )
                )

                ventana.destroy()

            except (
                ValueError,
                TypeError
            ) as error:

                messagebox.showerror(
                    "Error",
                    str(error)
                )

        tk.Button(
            ventana,
            text="Guardar",
            width=20,
            command=guardar
        ).pack(
            pady=20
        )

    # =========================================================
    # BUSCAR PACIENTE
    # =========================================================

    def buscar_paciente(self):
        """Muestra la búsqueda de pacientes dentro de la ventana principal."""
        self._mostrar_busqueda_personas(
            titulo="Buscar paciente",
            etiqueta="Buscar paciente por:",
            tipo_profesional=False
        )

    def _mostrar_busqueda_personas(self, titulo, etiqueta, tipo_profesional=False):
        """Construye una búsqueda de pacientes/profesionales en la misma ventana."""

        self._limpiar_pantalla_actual()

        ventana = tk.Frame(self.ventana, bg=COLOR_FONDO)
        ventana.pack(fill="both", expand=True)
        self._pantalla_actual = ventana

        contenedor = tk.Frame(ventana, bg=COLOR_FONDO)
        contenedor.pack(fill="both", expand=True, padx=35, pady=25)

        barra = tk.Frame(contenedor, bg=COLOR_FONDO)
        barra.pack(fill="x", pady=(0, 18))

        boton_volver = tk.Button(
            barra,
            text="←  Volver",
            command=self._callback_volver_actual or self.volver_panel_principal,
            font=FUENTE_BOTON,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=14,
            pady=8
        )
        boton_volver.pack(side="left")

        tk.Label(
            contenedor,
            text=titulo,
            font=FUENTE_TITULO,
            bg=COLOR_FONDO,
            fg=COLOR_BLANCO
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            contenedor,
            text=etiqueta,
            font=FUENTE_NORMAL_BOLD,
            bg=COLOR_FONDO,
            fg=COLOR_GRIS_CLARO
        ).pack(anchor="w", pady=(0, 8))

        tipo_var = tk.StringVar(value="Código")
        fila_busqueda = tk.Frame(contenedor, bg=COLOR_FONDO)
        fila_busqueda.pack(fill="x", pady=(0, 15))

        tk.OptionMenu(
            fila_busqueda,
            tipo_var,
            "Código",
            "DNI"
        ).pack(side="left", padx=(0, 10))

        entrada_busqueda = tk.Entry(
            fila_busqueda,
            width=35,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            insertbackground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            font=FUENTE_NORMAL
        )
        entrada_busqueda.pack(side="left", ipady=8)
        self.configurar_limite_busqueda(entrada_busqueda, self.ventana)

        # El botón Buscar queda junto al campo para que la acción sea visible
        # y también se mantiene el acceso mediante la tecla Enter.
        boton_buscar = tk.Button(
            fila_busqueda,
            text="🔎  Buscar",
            command=lambda: buscar(),
            font=FUENTE_BOTON,
            bg=COLOR_ROJO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO_CLARO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=14,
            pady=7
        )
        boton_buscar.pack(side="left", padx=(10, 0))

        resultado = tk.Text(
            contenedor,
            height=18,
            wrap="word",
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            insertbackground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            font=FUENTE_NORMAL
        )
        resultado.pack(fill="both", expand=True, pady=(5, 12))

        def limpiar_entrada(*args):
            entrada_busqueda.delete(0, tk.END)
            resultado.delete("1.0", tk.END)

        tipo_var.trace_add("write", limpiar_entrada)

        def buscar():
            try:
                tipo = tipo_var.get()
                valor = entrada_busqueda.get().strip()

                if not valor:
                    raise ValueError("Debe ingresar un valor para realizar la búsqueda.")

                if tipo_profesional:
                    if tipo == "Código":
                        registros = self.sistema.buscar_personal_por_codigo(valor)
                    else:
                        registros = self.sistema.buscar_personal_por_dni(
                            self.validar_dni(valor)
                        )
                    mensaje_vacio = "No se encontró personal."
                else:
                    if tipo == "Código":
                        registros = self.sistema.buscar_paciente_por_codigo(valor)
                    else:
                        registros = self.sistema.buscar_paciente_por_dni(
                            self.validar_dni(valor)
                        )
                    mensaje_vacio = "No se encontraron pacientes."

                resultado.delete("1.0", tk.END)

                if not registros:
                    resultado.insert(tk.END, mensaje_vacio)
                    return

                for registro in registros:
                    resultado.insert(
                        tk.END,
                        registro.mostrar_informacion() + "\n\n"
                    )

            except (ValueError, TypeError) as error:
                messagebox.showerror("Error", str(error))

        boton_buscar.configure(
            width=18
        )

        boton_buscar.bind(
            "<Enter>",
            lambda evento: boton_buscar.configure(
                bg=COLOR_ROJO_CLARO
            )
        )
        boton_buscar.bind(
            "<Leave>",
            lambda evento: boton_buscar.configure(
                bg=COLOR_ROJO
            )
        )

        barra_acciones = tk.Frame(contenedor, bg=COLOR_FONDO)
        barra_acciones.pack(fill="x", pady=(0, 5))

        boton_volver_inferior = tk.Button(
            barra_acciones,
            text="←  Volver",
            command=boton_volver.invoke,
            font=FUENTE_BOTON,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            width=15,
            pady=9
        )
        boton_volver_inferior.pack(side="left")

        entrada_busqueda.bind("<Return>", lambda evento: buscar())
        entrada_busqueda.focus_set()

    # =========================================================
    # VER PERSONAL
    # =========================================================

    def ver_personal(self):

        ventana = self._crear_pantalla_interna()

        ventana.title(
            "Personal de salud"
        )

        ventana.geometry(
            "850x450"
        )

        texto = tk.Text(
            ventana,
            width=100,
            height=23
        )

        texto.pack(
            padx=10,
            pady=10
        )

        personal = (
            self.sistema.obtener_personal()
        )

        if not personal:

            texto.insert(
                tk.END,
                "No existe personal registrado."
            )

            return

        for profesional in personal:

            texto.insert(
                tk.END,
                profesional.mostrar_informacion()
                + "\n\n"
            )

    # =========================================================
    # REGISTRAR PERSONAL
    # =========================================================

    def registrar_personal(self):

        ventana = self._crear_pantalla_interna()

        ventana.title(
            "Registrar personal"
        )

        ventana.geometry(
            "500x500"
        )

        codigo_generado = (
            self.generar_codigo_profesional()
        )

        tk.Label(
            ventana,
            text="Código profesional:"
        ).pack(
            pady=5
        )

        tk.Label(
            ventana,
            text=codigo_generado,
            font=("Arial", 14, "bold")
        ).pack(
            pady=5
        )

        tk.Label(
            ventana,
            text="DNI:"
        ).pack(
            pady=5
        )

        entrada_dni = tk.Entry(
            ventana,
            width=35
        )

        entrada_dni.pack()

        def validar_dni_tecla(nuevo_valor):

            if nuevo_valor == "":
                return True

            return (
                nuevo_valor.isdigit()
                and len(nuevo_valor) <= 8
            )

        validacion = ventana.register(
            validar_dni_tecla
        )

        entrada_dni.config(
            validate="key",
            validatecommand=(
                validacion,
                "%P"
            )
        )

        tk.Label(
            ventana,
            text="Nombre:"
        ).pack(
            pady=5
        )

        entrada_nombre = tk.Entry(
            ventana,
            width=35
        )

        entrada_nombre.pack()

        tk.Label(
            ventana,
            text="Edad:"
        ).pack(
            pady=5
        )

        entrada_edad = tk.Entry(
            ventana,
            width=35
        )

        entrada_edad.pack()

        tk.Label(
            ventana,
            text="Especialidad:"
        ).pack(
            pady=5
        )

        especialidades = [
            "Medicina General",
            "Enfermería",
            "Obstetricia",
            "Odontología",
            "Psicología",
            "Nutrición",
            "Medicina Familiar",
            "Urología",
            "Pediatría",
            "Neurología"
        ]

        especialidad_var = tk.StringVar()

        especialidad_var.set(
            especialidades[0]
        )

        tk.OptionMenu(
            ventana,
            especialidad_var,
            *especialidades
        ).pack()

        def guardar():

            try:

                dni = self.validar_dni(
                    entrada_dni.get()
                )

                profesional = PersonalSalud(
                    codigo_generado,
                    dni,
                    entrada_nombre.get(),
                    int(entrada_edad.get()),
                    especialidad_var.get()
                )

                self.sistema.registrar_personal(
                    profesional
                )

                messagebox.showinfo(
                    "Éxito",
                    (
                        "Personal registrado correctamente.\n\n"
                        f"Código asignado: "
                        f"{codigo_generado}\n"
                        "DNI almacenado de forma protegida."
                    )
                )

                ventana.destroy()

            except (
                ValueError,
                TypeError
            ) as error:

                messagebox.showerror(
                    "Error",
                    str(error)
                )

        tk.Button(
            ventana,
            text="Guardar",
            width=20,
            command=guardar
        ).pack(
            pady=20
        )

    # =========================================================
    # BUSCAR PERSONAL
    # =========================================================

    def buscar_personal(self):
        """Muestra la búsqueda de profesionales dentro de la ventana principal."""
        self._mostrar_busqueda_personas(
            titulo="Buscar profesional",
            etiqueta="Buscar profesional por:",
            tipo_profesional=True
        )

    # =========================================================
    # VER CITAS PENDIENTES
    # =========================================================

    def ver_citas(self):

        ventana = self._crear_pantalla_interna()

        ventana.title(
            "Citas pendientes"
        )

        ventana.geometry(
            "850x500"
        )

        texto = tk.Text(
            ventana,
            width=95,
            height=25
        )

        texto.pack(
            padx=10,
            pady=10
        )

        citas = (
            self.sistema.obtener_citas_pendientes()
        )

        if not citas:

            texto.insert(
                tk.END,
                "No existen citas pendientes."
            )

            return

        texto.insert(
            tk.END,
            "CITAS PENDIENTES\n"
        )

        texto.insert(
            tk.END,
            "========================================\n\n"
        )

        for cita in citas:

            texto.insert(
                tk.END,
                cita.mostrar_informacion()
                + "\n\n"
            )

    # =========================================================
    # CITAS PARA REPROGRAMAR
    # =========================================================

    def ver_citas_reprogramadas(self):

        ventana = self._crear_pantalla_interna()

        ventana.title(
            "Citas para reprogramar"
        )

        ventana.geometry(
            "850x500"
        )

        texto = tk.Text(
            ventana,
            width=95,
            height=25
        )

        texto.pack(
            padx=10,
            pady=10
        )

        citas = (
            self.sistema
            .obtener_citas_reprogramadas()
        )

        if not citas:

            texto.insert(
                tk.END,
                "No existen citas para reprogramar."
            )

            return

        texto.insert(
            tk.END,
            "CITAS PARA REPROGRAMAR\n"
        )

        texto.insert(
            tk.END,
            "========================================\n\n"
        )

        for cita in citas:

            texto.insert(
                tk.END,
                cita.mostrar_informacion()
                + "\n\n"
            )

    # =========================================================
    # REGISTRAR CITA
    # =========================================================

    def registrar_cita(self):

        pacientes = (
            self.sistema.obtener_pacientes()
        )

        personal = (
            self.sistema.obtener_personal()
        )

        if not pacientes:

            messagebox.showwarning(
                "Aviso",
                "Primero debe registrar un paciente."
            )

            return

        if not personal:

            messagebox.showwarning(
                "Aviso",
                "Primero debe registrar personal de salud."
            )

            return

        ventana = self._crear_pantalla_interna()

        ventana.title(
            "Registrar cita"
        )

        ventana.geometry(
            "500x600"
        )

        codigo_generado = (
            self.sistema.generar_codigo_cita()
        )

        tk.Label(
            ventana,
            text="Código de cita:"
        ).pack(
            pady=5
        )

        tk.Label(
            ventana,
            text=codigo_generado,
            font=("Arial", 14, "bold")
        ).pack(
            pady=5
        )

        tk.Label(
            ventana,
            text="Paciente:"
        ).pack(
            pady=5
        )

        paciente_var = tk.StringVar()

        pacientes_texto = [
            f"{p.codigo} - {p.nombre}"
            for p in pacientes
        ]

        paciente_var.set(
            pacientes_texto[0]
        )

        tk.OptionMenu(
            ventana,
            paciente_var,
            *pacientes_texto
        ).pack()

        tk.Label(
            ventana,
            text="Profesional:"
        ).pack(
            pady=5
        )

        profesional_var = tk.StringVar()

        personal_texto = [
            (
                f"{p.codigo_profesional} - "
                f"{p.nombre} - "
                f"{p.especialidad}"
            )
            for p in personal
        ]

        profesional_var.set(
            personal_texto[0]
        )

        tk.OptionMenu(
            ventana,
            profesional_var,
            *personal_texto
        ).pack()

        tk.Label(
            ventana,
            text="Fecha:"
        ).pack(
            pady=5
        )

        entrada_fecha = (
            self.crear_campo_fecha(
                ventana
            )
        )

        tk.Label(
            ventana,
            text="Motivo:"
        ).pack(
            pady=5
        )

        entrada_motivo = tk.Entry(
            ventana,
            width=40
        )

        entrada_motivo.pack()

        def guardar():

            try:

                if entrada_fecha.placeholder_activo:

                    raise ValueError(
                        "Debe ingresar una fecha."
                    )

                fecha = (
                    entrada_fecha.get()
                )

                self.validar_fecha(
                    fecha
                )

                paciente_codigo = (
                    paciente_var
                    .get()
                    .split(" - ")[0]
                )

                profesional_codigo = (
                    profesional_var
                    .get()
                    .split(" - ")[0]
                )

                paciente = next(
                    p
                    for p in pacientes
                    if p.codigo
                    == paciente_codigo
                )

                profesional = next(
                    p
                    for p in personal
                    if (
                        p.codigo_profesional
                        == profesional_codigo
                    )
                )

                cita = Cita(
                    codigo_generado,
                    paciente,
                    profesional,
                    fecha,
                    entrada_motivo.get(),
                    "Pendiente"
                )

                self.sistema.registrar_cita(
                    cita
                )

                messagebox.showinfo(
                    "Éxito",
                    (
                        "Cita registrada correctamente.\n\n"
                        f"Código: {codigo_generado}"
                    )
                )

                ventana.destroy()

            except (
                ValueError,
                TypeError
            ) as error:

                messagebox.showerror(
                    "Error",
                    str(error)
                )

        tk.Button(
            ventana,
            text="Guardar cita",
            width=25,
            command=guardar
        ).pack(
            pady=25
        )

    # =========================================================
    # CAMBIAR ESTADO DE CITA
    # =========================================================

    def cambiar_estado_cita(self):

        citas = [
            cita
            for cita in self.sistema.obtener_citas()
            if cita.estado != "Atendida"
        ]

        if not citas:

            messagebox.showwarning(
                "Aviso",
                (
                    "No existen citas disponibles "
                    "para cambiar de estado."
                )
            )

            return

        ventana = self._crear_pantalla_interna()

        ventana.title(
            "Cambiar estado de cita"
        )

        ventana.geometry(
            "650x450"
        )

        tk.Label(
            ventana,
            text="Seleccione la cita:"
        ).pack(
            pady=10
        )

        cita_var = tk.StringVar()

        citas_texto = [
            (
                f"{c.codigo} | "
                f"{c.paciente.nombre} | "
                f"{c.profesional.nombre} | "
                f"{c.fecha} | "
                f"{c.estado}"
            )
            for c in citas
        ]

        cita_var.set(
            citas_texto[0]
        )

        tk.OptionMenu(
            ventana,
            cita_var,
            *citas_texto
        ).pack()

        tk.Label(
            ventana,
            text="Nuevo estado:"
        ).pack(
            pady=15
        )

        estado_var = tk.StringVar(
            value="Pendiente"
        )

        tk.OptionMenu(
            ventana,
            estado_var,
            "Pendiente",
            "Atendida",
            "Reprogramar"
        ).pack()

        informacion = tk.Label(
            ventana,
            text="",
            justify="left"
        )

        informacion.pack(
            pady=20
        )

        def mostrar_informacion(*args):

            try:

                codigo = (
                    cita_var
                    .get()
                    .split(" | ")[0]
                )

                cita = next(
                    c
                    for c in citas
                    if c.codigo == codigo
                )

                informacion.config(
                    text=(
                        f"Paciente: "
                        f"{cita.paciente.nombre}\n"
                        f"Profesional: "
                        f"{cita.profesional.nombre}\n"
                        f"Fecha: {cita.fecha}\n"
                        f"Motivo: {cita.motivo}\n"
                        f"Estado actual: {cita.estado}"
                    )
                )

            except (
                ValueError,
                StopIteration
            ):

                pass

        cita_var.trace_add(
            "write",
            mostrar_informacion
        )

        mostrar_informacion()

        def actualizar():

            try:

                codigo_cita = (
                    cita_var
                    .get()
                    .split(" | ")[0]
                )

                nuevo_estado = (
                    estado_var.get()
                )

                self.sistema.actualizar_estado_cita(
                    codigo_cita,
                    nuevo_estado
                )

                if nuevo_estado == "Atendida":

                    mensaje = (
                        "La cita fue marcada como atendida.\n\n"
                        "El registro NO fue eliminado.\n"
                        "Ahora aparecerá en el "
                        "Historial Clínico y ya no "
                        "aparecerá en este selector."
                    )

                elif nuevo_estado == "Reprogramar":

                    mensaje = (
                        "La cita fue marcada para "
                        "reprogramar.\n\n"
                        "El registro se conserva."
                    )

                else:

                    mensaje = (
                        "La cita volvió a estar pendiente."
                    )

                messagebox.showinfo(
                    "Estado actualizado",
                    mensaje
                )

                ventana.destroy()

            except (
                ValueError,
                TypeError
            ) as error:

                messagebox.showerror(
                    "Error",
                    str(error)
                )

        tk.Button(
            ventana,
            text="Actualizar estado",
            width=25,
            command=actualizar
        ).pack(
            pady=20
        )

    # =========================================================
    # VER ATENCIONES
    # =========================================================

    def ver_atenciones(self):

        ventana = self._crear_pantalla_interna()

        ventana.title(
            "Atenciones médicas"
        )

        ventana.geometry(
            "900x500"
        )

        texto = tk.Text(
            ventana,
            width=105,
            height=25
        )

        texto.pack(
            padx=10,
            pady=10
        )

        atenciones = (
            self.sistema.obtener_atenciones()
        )

        if not atenciones:

            texto.insert(
                tk.END,
                "No existen atenciones registradas."
            )

            return

        texto.insert(
            tk.END,
            "ATENCIONES MÉDICAS\n"
        )

        texto.insert(
            tk.END,
            "========================================\n\n"
        )

        for atencion in atenciones:

            texto.insert(
                tk.END,
                atencion.mostrar_informacion()
                + "\n\n"
            )

    # =========================================================
    # REGISTRAR ATENCIÓN
    # =========================================================

    def registrar_atencion(self):

        citas = (
            self.sistema.obtener_citas()
        )

        if not citas:

            messagebox.showwarning(
                "Aviso",
                "Primero debe registrar una cita."
            )

            return

        citas_disponibles = [
            cita
            for cita in citas
            if not any(
                atencion.cita.codigo
                == cita.codigo
                for atencion
                in self.sistema.obtener_atenciones()
            )
            and cita.estado != "Atendida"
        ]

        if not citas_disponibles:

            messagebox.showwarning(
                "Aviso",
                (
                    "No existen citas disponibles "
                    "para registrar una atención."
                )
            )

            return

        ventana = self._crear_pantalla_interna()

        ventana.title(
            "Registrar atención"
        )

        ventana.geometry(
            "550x500"
        )

        codigo_generado = (
            self.sistema.generar_codigo_atencion()
        )

        tk.Label(
            ventana,
            text="Código de atención:"
        ).pack(
            pady=5
        )

        tk.Label(
            ventana,
            text=codigo_generado,
            font=("Arial", 14, "bold")
        ).pack(
            pady=5
        )

        tk.Label(
            ventana,
            text="Cita:"
        ).pack(
            pady=5
        )

        cita_var = tk.StringVar()

        citas_texto = [
            (
                f"{c.codigo} | "
                f"{c.paciente.nombre} | "
                f"{c.profesional.nombre} | "
                f"{c.fecha}"
            )
            for c in citas_disponibles
        ]

        cita_var.set(
            citas_texto[0]
        )

        tk.OptionMenu(
            ventana,
            cita_var,
            *citas_texto
        ).pack()

        tk.Label(
            ventana,
            text="Diagnóstico:"
        ).pack(
            pady=5
        )

        entrada_diagnostico = tk.Entry(
            ventana,
            width=45
        )

        entrada_diagnostico.pack()

        tk.Label(
            ventana,
            text="Estado:"
        ).pack(
            pady=5
        )

        estado_var = tk.StringVar(
            value="Pendiente"
        )

        tk.OptionMenu(
            ventana,
            estado_var,
            "Pendiente",
            "En proceso",
            "Finalizada"
        ).pack()

        def guardar():

            try:

                cita_codigo = (
                    cita_var
                    .get()
                    .split(" | ")[0]
                )

                cita = next(
                    c
                    for c in citas_disponibles
                    if c.codigo
                    == cita_codigo
                )

                atencion = AtencionMedica(
                    codigo_generado,
                    cita,
                    entrada_diagnostico.get(),
                    estado_var.get()
                )

                self.sistema.registrar_atencion(
                    atencion
                )

                messagebox.showinfo(
                    "Éxito",
                    (
                        "Atención registrada correctamente.\n\n"
                        f"Código: {codigo_generado}"
                    )
                )

                ventana.destroy()

            except (
                ValueError,
                TypeError
            ) as error:

                messagebox.showerror(
                    "Error",
                    str(error)
                )

        tk.Button(
            ventana,
            text="Guardar atención",
            width=25,
            command=guardar
        ).pack(
            pady=25
        )

    # =========================================================
    # CAMBIAR ESTADO DE ATENCIÓN
    # =========================================================

    def cambiar_estado_atencion(self):

        atenciones = [
            atencion
            for atencion
            in self.sistema.obtener_atenciones()
            if atencion.estado != "Finalizada"
        ]

        if not atenciones:

            messagebox.showwarning(
                "Aviso",
                (
                    "No existen atenciones disponibles "
                    "para cambiar de estado."
                )
            )

            return

        ventana = self._crear_pantalla_interna()

        ventana.title(
            "Cambiar estado de atención"
        )

        ventana.geometry(
            "700x450"
        )

        tk.Label(
            ventana,
            text="Seleccione la atención:"
        ).pack(
            pady=10
        )

        atencion_var = tk.StringVar()

        atenciones_texto = [
            (
                f"{a.codigo} | "
                f"{a.paciente.nombre} | "
                f"{a.profesional.nombre} | "
                f"{a.estado}"
            )
            for a in atenciones
        ]

        atencion_var.set(
            atenciones_texto[0]
        )

        tk.OptionMenu(
            ventana,
            atencion_var,
            *atenciones_texto
        ).pack()

        tk.Label(
            ventana,
            text="Nuevo estado:"
        ).pack(
            pady=15
        )

        estado_var = tk.StringVar(
            value="Pendiente"
        )

        tk.OptionMenu(
            ventana,
            estado_var,
            "Pendiente",
            "En proceso",
            "Finalizada"
        ).pack()

        informacion = tk.Label(
            ventana,
            text="",
            justify="left"
        )

        informacion.pack(
            pady=20
        )

        def mostrar_informacion(*args):

            try:

                codigo = (
                    atencion_var
                    .get()
                    .split(" | ")[0]
                )

                atencion = next(
                    a
                    for a in atenciones
                    if a.codigo == codigo
                )

                informacion.config(
                    text=(
                        f"Paciente: "
                        f"{atencion.paciente.nombre}\n"
                        f"Profesional: "
                        f"{atencion.profesional.nombre}\n"
                        f"Fecha: {atencion.fecha}\n"
                        f"Diagnóstico: "
                        f"{atencion.diagnostico}\n"
                        f"Estado actual: "
                        f"{atencion.estado}"
                    )
                )

            except (
                ValueError,
                StopIteration
            ):

                pass

        atencion_var.trace_add(
            "write",
            mostrar_informacion
        )

        mostrar_informacion()

        def actualizar():

            try:

                codigo_atencion = (
                    atencion_var
                    .get()
                    .split(" | ")[0]
                )

                nuevo_estado = (
                    estado_var.get()
                )

                self.sistema.actualizar_estado_atencion(
                    codigo_atencion,
                    nuevo_estado
                )

                if nuevo_estado == "Finalizada":

                    mensaje = (
                        "La atención fue finalizada.\n\n"
                        "El registro NO fue eliminado.\n"
                        "Ahora aparecerá en el "
                        "Historial Clínico y ya no "
                        "aparecerá en este selector."
                    )

                elif nuevo_estado == "En proceso":

                    mensaje = (
                        "La atención está en proceso."
                    )

                else:

                    mensaje = (
                        "La atención volvió a estar pendiente."
                    )

                messagebox.showinfo(
                    "Estado actualizado",
                    mensaje
                )

                ventana.destroy()

            except (
                ValueError,
                TypeError
            ) as error:

                messagebox.showerror(
                    "Error",
                    str(error)
                )

        tk.Button(
            ventana,
            text="Actualizar estado",
            width=25,
            command=actualizar
        ).pack(
            pady=20
        )

    # =========================================================
    # HISTORIAL CLÍNICO - MENÚ PRINCIPAL
    # =========================================================

    def historial_clinico(self):

        pacientes = (
            self.sistema.obtener_pacientes()
        )

        personal = (
            self.sistema.obtener_personal()
        )

        if not pacientes and not personal:

            messagebox.showwarning(
                "Aviso",
                "No existen pacientes ni profesionales registrados."
            )

            return

        ventana = self._crear_pantalla_interna()

        ventana.title(
            "Historial clínico"
        )

        ventana.geometry(
            "500x400"
        )

        tk.Label(
            ventana,
            text="HISTORIAL CLÍNICO",
            font=("Arial", 22, "bold")
        ).pack(
            pady=30
        )

        tk.Label(
            ventana,
            text=(
                "Seleccione qué historial desea consultar:"
            ),
            font=("Arial", 12)
        ).pack(
            pady=10
        )

        # =====================================================
        # BOTÓN PACIENTES
        # =====================================================

        tk.Button(
            ventana,
            text="PACIENTES",
            width=30,
            height=3,
            font=("Arial", 13, "bold"),
            command=self.historial_pacientes
        ).pack(
            pady=15
        )

        # =====================================================
        # BOTÓN PROFESIONALES
        # =====================================================

        tk.Button(
            ventana,
            text="PROFESIONALES",
            width=30,
            height=3,
            font=("Arial", 13, "bold"),
            command=self.historial_profesionales
        ).pack(
            pady=15
        )

        tk.Button(
            ventana,
            text="Cerrar",
            width=20,
            command=ventana.destroy
        ).pack(
            pady=20
        )

    # =========================================================
    # HISTORIAL DE PACIENTES
    # =========================================================

    def historial_pacientes(self):

        pacientes = (
            self.sistema.obtener_pacientes()
        )

        if not pacientes:

            messagebox.showwarning(
                "Aviso",
                "No existen pacientes registrados."
            )

            return

        ventana = self._crear_pantalla_interna()

        ventana.title(
            "Historial de pacientes"
        )

        ventana.geometry(
            "1050x720"
        )

        ventana.minsize(
            850,
            600
        )

        tk.Label(
            ventana,
            text="HISTORIAL DE PACIENTES",
            font=("Arial", 20, "bold")
        ).pack(
            pady=(15, 8)
        )

        tk.Label(
            ventana,
            text=(
                "Consulte las citas y atenciones médicas registradas "
                "del paciente."
            ),
            font=("Arial", 11)
        ).pack(
            pady=(0, 12)
        )

        # =====================================================
        # BÚSQUEDA DEL PACIENTE
        # =====================================================

        marco_busqueda = tk.Frame(
            ventana
        )

        marco_busqueda.pack(
            pady=5,
            padx=15
        )

        tk.Label(
            marco_busqueda,
            text="Buscar por:"
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        tipo_var = tk.StringVar(
            value="Código"
        )

        tk.OptionMenu(
            marco_busqueda,
            tipo_var,
            "Código",
            "DNI"
        ).grid(
            row=0,
            column=1,
            padx=5
        )

        entrada_busqueda = tk.Entry(
            marco_busqueda,
            width=30
        )

        entrada_busqueda.grid(
            row=0,
            column=2,
            padx=5
        )
        self.configurar_limite_busqueda(entrada_busqueda, ventana)

        # =====================================================
        # ÁREA DE RESULTADOS CON SCROLL
        # =====================================================

        marco_resultado = tk.Frame(
            ventana
        )

        marco_resultado.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        texto = tk.Text(
            marco_resultado,
            wrap="word",
            font=("Arial", 10),
            padx=10,
            pady=10
        )

        texto.pack(
            side="left",
            fill="both",
            expand=True
        )

        barra = tk.Scrollbar(
            marco_resultado,
            command=texto.yview
        )

        barra.pack(
            side="right",
            fill="y"
        )

        texto.config(
            yscrollcommand=barra.set
        )

        def mostrar_historial(*args):

            try:

                tipo = tipo_var.get()

                valor = (
                    entrada_busqueda
                    .get()
                    .strip()
                )

                if not valor:

                    raise ValueError(
                        "Ingrese el código o DNI del paciente."
                    )

                paciente = None

                if tipo == "Código":

                    resultados = (
                        self.sistema
                        .buscar_paciente_por_codigo(valor)
                    )

                else:

                    dni = self.validar_dni(
                        valor
                    )

                    resultados = (
                        self.sistema
                        .buscar_paciente_por_dni(dni)
                    )

                paciente = resultados[0] if resultados else None

                if paciente is None:

                    raise ValueError(
                        "No se encontró el paciente."
                    )

                texto.config(
                    state="normal"
                )

                texto.delete(
                    "1.0",
                    tk.END
                )

                # =================================================
                # OBTENER TODOS LOS REGISTROS DEL PACIENTE
                # =================================================

                citas = [
                    cita
                    for cita in self.sistema.obtener_citas()
                    if cita.paciente.codigo == paciente.codigo
                ]

                atenciones = [
                    atencion
                    for atencion in self.sistema.obtener_atenciones()
                    if atencion.paciente.codigo == paciente.codigo
                ]

                # =================================================
                # DATOS DEL PACIENTE
                # =================================================

                texto.insert(
                    tk.END,
                    "==================================================\n"
                )

                texto.insert(
                    tk.END,
                    "              HISTORIAL DEL PACIENTE\n"
                )

                texto.insert(
                    tk.END,
                    "==================================================\n\n"
                )

                texto.insert(
                    tk.END,
                    "DATOS DEL PACIENTE\n"
                )

                texto.insert(
                    tk.END,
                    "--------------------------------------------------\n"
                )

                texto.insert(
                    tk.END,
                    f"Código: {paciente.codigo}\n"
                )

                texto.insert(
                    tk.END,
                    f"DNI: {paciente.dni}\n"
                )

                texto.insert(
                    tk.END,
                    f"Nombre: {paciente.nombre}\n"
                )

                texto.insert(
                    tk.END,
                    f"Edad: {paciente.edad} años\n\n"
                )

                # =================================================
                # CITAS Y CONSULTAS
                # =================================================

                texto.insert(
                    tk.END,
                    "CITAS Y CONSULTAS DEL PACIENTE\n"
                )

                texto.insert(
                    tk.END,
                    "--------------------------------------------------\n"
                )

                if not citas:

                    texto.insert(
                        tk.END,
                        "El paciente no tiene citas registradas.\n\n"
                    )

                else:

                    for numero, cita in enumerate(
                        citas,
                        start=1
                    ):

                        texto.insert(
                            tk.END,
                            f"Consulta N.° {numero}\n"
                        )

                        texto.insert(
                            tk.END,
                            f"Código de cita: {cita.codigo}\n"
                        )

                        texto.insert(
                            tk.END,
                            f"Fecha: {cita.fecha}\n"
                        )

                        texto.insert(
                            tk.END,
                            (
                                f"Profesional: "
                                f"{cita.profesional.nombre}\n"
                            )
                        )

                        texto.insert(
                            tk.END,
                            (
                                f"Código profesional: "
                                f"{cita.profesional.codigo_profesional}\n"
                            )
                        )

                        texto.insert(
                            tk.END,
                            (
                                f"Especialidad: "
                                f"{cita.profesional.especialidad}\n"
                            )
                        )

                        texto.insert(
                            tk.END,
                            f"Motivo: {cita.motivo}\n"
                        )

                        texto.insert(
                            tk.END,
                            f"Estado: {cita.estado}\n"
                        )

                        texto.insert(
                            tk.END,
                            "--------------------------------------------------\n"
                        )

                texto.insert(
                    tk.END,
                    "\n"
                )

                # =================================================
                # ATENCIONES MÉDICAS
                # =================================================

                texto.insert(
                    tk.END,
                    "ATENCIONES MÉDICAS DEL PACIENTE\n"
                )

                texto.insert(
                    tk.END,
                    "--------------------------------------------------\n"
                )

                if not atenciones:

                    texto.insert(
                        tk.END,
                        "El paciente no tiene atenciones registradas.\n"
                    )

                else:

                    for numero, atencion in enumerate(
                        atenciones,
                        start=1
                    ):

                        texto.insert(
                            tk.END,
                            f"Atención N.° {numero}\n"
                        )

                        texto.insert(
                            tk.END,
                            (
                                f"Código de atención: "
                                f"{atencion.codigo}\n"
                            )
                        )

                        texto.insert(
                            tk.END,
                            (
                                f"Cita relacionada: "
                                f"{atencion.cita.codigo}\n"
                            )
                        )

                        texto.insert(
                            tk.END,
                            f"Fecha: {atencion.fecha}\n"
                        )

                        texto.insert(
                            tk.END,
                            (
                                f"Profesional: "
                                f"{atencion.profesional.nombre}\n"
                            )
                        )

                        texto.insert(
                            tk.END,
                            (
                                f"Código profesional: "
                                f"{atencion.profesional.codigo_profesional}\n"
                            )
                        )

                        texto.insert(
                            tk.END,
                            (
                                f"Especialidad: "
                                f"{atencion.profesional.especialidad}\n"
                            )
                        )

                        texto.insert(
                            tk.END,
                            (
                                f"Diagnóstico: "
                                f"{atencion.diagnostico}\n"
                            )
                        )

                        texto.insert(
                            tk.END,
                            f"Estado: {atencion.estado}\n"
                        )

                        texto.insert(
                            tk.END,
                            "--------------------------------------------------\n"
                        )

                texto.insert(
                    tk.END,
                    "\nResumen: "
                    f"{len(citas)} cita(s) y "
                    f"{len(atenciones)} atención(es) registrada(s).\n"
                )

                texto.config(
                    state="disabled"
                )

                texto.see(
                    "1.0"
                )

            except (
                ValueError,
                TypeError,
                AttributeError
            ) as error:

                texto.config(
                    state="normal"
                )

                messagebox.showerror(
                    "Error",
                    str(error)
                )

        def limpiar():

            entrada_busqueda.delete(
                0,
                tk.END
            )

            texto.config(
                state="normal"
            )

            texto.delete(
                "1.0",
                tk.END
            )

            texto.config(
                state="disabled"
            )

            entrada_busqueda.focus_set()

        # =====================================================
        # BOTONES DE CONSULTA
        # =====================================================

        tk.Button(
            marco_busqueda,
            text="Consultar historial",
            width=20,
            command=mostrar_historial
        ).grid(
            row=0,
            column=3,
            padx=8
        )

        tk.Button(
            marco_busqueda,
            text="Limpiar",
            width=12,
            command=limpiar
        ).grid(
            row=0,
            column=4,
            padx=5
        )

        entrada_busqueda.bind(
            "<Return>",
            mostrar_historial
        )

        entrada_busqueda.focus_set()

        texto.config(
            state="disabled"
        )

    # =========================================================
    # HISTORIAL DE PROFESIONALES
    # =========================================================

    def historial_profesionales(self):

        personal = (
            self.sistema.obtener_personal()
        )

        if not personal:

            messagebox.showwarning(
                "Aviso",
                "No existe personal registrado."
            )

            return

        ventana = self._crear_pantalla_interna()

        ventana.title(
            "Historial de profesionales"
        )

        ventana.geometry(
            "1000x700"
        )

        tk.Label(
            ventana,
            text="HISTORIAL DE PROFESIONALES",
            font=("Arial", 20, "bold")
        ).pack(
            pady=15
        )

        # =====================================================
        # BÚSQUEDA
        # =====================================================

        marco_busqueda = tk.Frame(
            ventana
        )

        marco_busqueda.pack(
            pady=5
        )

        tk.Label(
            marco_busqueda,
            text="Buscar profesional por:"
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        tipo_var = tk.StringVar(
            value="Código"
        )

        tk.OptionMenu(
            marco_busqueda,
            tipo_var,
            "Código",
            "DNI"
        ).grid(
            row=0,
            column=1,
            padx=5
        )

        entrada_busqueda = tk.Entry(
            marco_busqueda,
            width=30
        )

        entrada_busqueda.grid(
            row=0,
            column=2,
            padx=5
        )
        self.configurar_limite_busqueda(entrada_busqueda, ventana)

        texto = tk.Text(
            ventana,
            width=115,
            height=32
        )

        texto.pack(
            padx=10,
            pady=15
        )

        def mostrar_historial():

            try:

                tipo = tipo_var.get()

                valor = (
                    entrada_busqueda
                    .get()
                    .strip()
                )

                if not valor:

                    raise ValueError(
                        "Ingrese el código o DNI del profesional."
                    )

                if tipo == "Código":

                    profesional = next(
                        (
                            p
                            for p in personal
                            if p.codigo_profesional == valor
                        ),
                        None
                    )

                else:

                    dni = self.validar_dni(
                        valor
                    )

                    profesional = next(
                        (
                            p
                            for p in personal
                            if p.dni == dni
                        ),
                        None
                    )

                if profesional is None:

                    raise ValueError(
                        "No se encontró el profesional."
                    )

                texto.delete(
                    "1.0",
                    tk.END
                )

                citas = [
                    cita
                    for cita
                    in self.sistema.obtener_citas()
                    if (
                        cita.profesional.codigo_profesional
                        == profesional.codigo_profesional
                    )
                ]

                atenciones = [
                    atencion
                    for atencion
                    in self.sistema.obtener_atenciones()
                    if (
                        atencion.profesional.codigo_profesional
                        == profesional.codigo_profesional
                    )
                ]

                # =================================================
                # DATOS DEL PROFESIONAL
                # =================================================

                texto.insert(
                    tk.END,
                    "==================================================\n"
                )

                texto.insert(
                    tk.END,
                    "              HISTORIAL DEL PROFESIONAL\n"
                )

                texto.insert(
                    tk.END,
                    "==================================================\n\n"
                )

                texto.insert(
                    tk.END,
                    "DATOS DEL PROFESIONAL\n"
                )

                texto.insert(
                    tk.END,
                    "--------------------------------------------------\n"
                )

                texto.insert(
                    tk.END,
                    (
                        f"Código profesional: "
                        f"{profesional.codigo_profesional}\n"
                    )
                )

                texto.insert(
                    tk.END,
                    f"DNI: {profesional.dni}\n"
                )

                texto.insert(
                    tk.END,
                    f"Nombre: {profesional.nombre}\n"
                )

                texto.insert(
                    tk.END,
                    f"Edad: {profesional.edad} años\n"
                )

                texto.insert(
                    tk.END,
                    f"Especialidad: {profesional.especialidad}\n\n"
                )

                # =================================================
                # CITAS DEL PROFESIONAL
                # =================================================

                texto.insert(
                    tk.END,
                    "CITAS Y ACTIVIDADES DEL PROFESIONAL\n"
                )

                texto.insert(
                    tk.END,
                    "--------------------------------------------------\n"
                )

                if not citas:

                    texto.insert(
                        tk.END,
                        "El profesional no tiene citas registradas.\n\n"
                    )

                else:

                    for cita in citas:

                        texto.insert(
                            tk.END,
                            f"Código de cita: {cita.codigo}\n"
                        )

                        texto.insert(
                            tk.END,
                            f"Fecha: {cita.fecha}\n"
                        )

                        texto.insert(
                            tk.END,
                            (
                                f"Paciente: "
                                f"{cita.paciente.nombre}\n"
                            )
                        )

                        texto.insert(
                            tk.END,
                            (
                                f"DNI del paciente: "
                                f"{cita.paciente.dni}\n"
                            )
                        )

                        texto.insert(
                            tk.END,
                            f"Motivo: {cita.motivo}\n"
                        )

                        texto.insert(
                            tk.END,
                            f"Estado: {cita.estado}\n"
                        )

                        texto.insert(
                            tk.END,
                            "--------------------------------------------------\n"
                        )

                texto.insert(
                    tk.END,
                    "\n"
                )

                # =================================================
                # ATENCIONES REALIZADAS
                # =================================================

                texto.insert(
                    tk.END,
                    "ATENCIONES MÉDICAS REALIZADAS\n"
                )

                texto.insert(
                    tk.END,
                    "--------------------------------------------------\n"
                )

                if not atenciones:

                    texto.insert(
                        tk.END,
                        "El profesional no tiene atenciones registradas.\n"
                    )

                else:

                    for atencion in atenciones:

                        texto.insert(
                            tk.END,
                            (
                                f"Código de atención: "
                                f"{atencion.codigo}\n"
                            )
                        )

                        texto.insert(
                            tk.END,
                            (
                                f"Cita relacionada: "
                                f"{atencion.cita.codigo}\n"
                            )
                        )

                        texto.insert(
                            tk.END,
                            f"Fecha: {atencion.fecha}\n"
                        )

                        texto.insert(
                            tk.END,
                            (
                                f"Paciente: "
                                f"{atencion.paciente.nombre}\n"
                            )
                        )

                        texto.insert(
                            tk.END,
                            (
                                f"DNI del paciente: "
                                f"{atencion.paciente.dni}\n"
                            )
                        )

                        texto.insert(
                            tk.END,
                            (
                                f"Diagnóstico: "
                                f"{atencion.diagnostico}\n"
                            )
                        )

                        texto.insert(
                            tk.END,
                            f"Estado: {atencion.estado}\n"
                        )

                        texto.insert(
                            tk.END,
                            "--------------------------------------------------\n"
                        )

            except (
                ValueError,
                TypeError
            ) as error:

                messagebox.showerror(
                    "Error",
                    str(error)
                )

        tk.Button(
            marco_busqueda,
            text="Consultar historial",
            width=20,
            command=mostrar_historial
        ).grid(
            row=0,
            column=3,
            padx=10
        )

    # =========================================================
    # ESTADÍSTICAS
    # =========================================================

    def ver_estadisticas(self):

        ventana = self._crear_pantalla_interna()

        ventana.title(
            "Estadísticas del sistema"
        )

        ventana.geometry(
            "550x550"
        )

        tk.Label(
            ventana,
            text="ESTADÍSTICAS",
            font=("Arial", 20, "bold")
        ).pack(
            pady=20
        )

        reporte = (
            self.reportes.reporte_general()
        )

        reporte_citas = (
            self.reportes.reporte_citas()
        )

        reporte_atenciones = (
            self.reportes.reporte_atenciones()
        )

        estadisticas = [
            (
                "Total de pacientes",
                reporte["pacientes"]
            ),
            (
                "Total de personal",
                reporte["profesionales"]
            ),
            (
                "Total de citas",
                reporte["citas"]
            ),
            (
                "Citas pendientes",
                reporte_citas["pendientes"]
            ),
            (
                "Citas atendidas",
                reporte_citas["atendidas"]
            ),
            (
                "Citas para reprogramar",
                reporte_citas["reprogramar"]
            ),
            (
                "Total de atenciones",
                reporte["atenciones"]
            ),
            (
                "Atenciones finalizadas",
                reporte_atenciones["finalizadas"]
            )
        ]

        for nombre, cantidad in estadisticas:

            marco = tk.Frame(
                ventana
            )

            marco.pack(
                fill="x",
                padx=40,
                pady=6
            )

            tk.Label(
                marco,
                text=nombre + ":",
                font=("Arial", 12)
            ).pack(
                side="left"
            )

            tk.Label(
                marco,
                text=str(cantidad),
                font=("Arial", 12, "bold")
            ).pack(
                side="right"
            )

    # =========================================================
    # REPORTES
    # =========================================================

    def ver_reportes(self):

        ventana = self._crear_pantalla_interna()

        ventana.title(
            "Reportes del sistema"
        )

        ventana.geometry(
            "850x650"
        )

        texto = tk.Text(
            ventana,
            width=100,
            height=35
        )

        texto.pack(
            padx=10,
            pady=10
        )

        reporte_pacientes = (
            self.reportes.reporte_pacientes()
        )

        reporte_profesionales = (
            self.reportes.reporte_profesionales()
        )

        reporte_citas = (
            self.reportes.reporte_citas()
        )

        reporte_atenciones = (
            self.reportes.reporte_atenciones()
        )

        reporte_general = (
            self.reportes.reporte_general()
        )

        texto.insert(
            tk.END,
            "========================================\n"
        )

        texto.insert(
            tk.END,
            "             REPORTES SALUPRO\n"
        )

        texto.insert(
            tk.END,
            "========================================\n\n"
        )

        # =====================================================
        # GENERAL
        # =====================================================

        texto.insert(
            tk.END,
            "REPORTE GENERAL\n"
        )

        texto.insert(
            tk.END,
            "----------------------------------------\n"
        )

        texto.insert(
            tk.END,
            f"Pacientes: "
            f"{reporte_general['pacientes']}\n"
        )

        texto.insert(
            tk.END,
            f"Profesionales: "
            f"{reporte_general['profesionales']}\n"
        )

        texto.insert(
            tk.END,
            f"Citas: "
            f"{reporte_general['citas']}\n"
        )

        texto.insert(
            tk.END,
            f"Atenciones: "
            f"{reporte_general['atenciones']}\n\n"
        )

        # =====================================================
        # PACIENTES
        # =====================================================

        texto.insert(
            tk.END,
            "REPORTE DE PACIENTES\n"
        )

        texto.insert(
            tk.END,
            "----------------------------------------\n"
        )

        texto.insert(
            tk.END,
            f"Total: "
            f"{reporte_pacientes['total_pacientes']}\n"
        )

        texto.insert(
            tk.END,
            "Nombres registrados:\n"
        )

        for nombre in (
            reporte_pacientes["nombres"]
        ):

            texto.insert(
                tk.END,
                f"- {nombre}\n"
            )

        texto.insert(
            tk.END,
            "\n"
        )

        # =====================================================
        # PROFESIONALES
        # =====================================================

        texto.insert(
            tk.END,
            "REPORTE DE PROFESIONALES\n"
        )

        texto.insert(
            tk.END,
            "----------------------------------------\n"
        )

        texto.insert(
            tk.END,
            (
                f"Total: "
                f"{reporte_profesionales['total_profesionales']}\n"
            )
        )

        texto.insert(
            tk.END,
            "Especialidades:\n"
        )

        for especialidad in (
            reporte_profesionales["especialidades"]
        ):

            texto.insert(
                tk.END,
                f"- {especialidad}\n"
            )

        texto.insert(
            tk.END,
            "\n"
        )

        # =====================================================
        # CITAS
        # =====================================================

        texto.insert(
            tk.END,
            "REPORTE DE CITAS\n"
        )

        texto.insert(
            tk.END,
            "----------------------------------------\n"
        )

        texto.insert(
            tk.END,
            f"Total: "
            f"{reporte_citas['total_citas']}\n"
        )

        texto.insert(
            tk.END,
            f"Pendientes: "
            f"{reporte_citas['pendientes']}\n"
        )

        texto.insert(
            tk.END,
            f"Atendidas: "
            f"{reporte_citas['atendidas']}\n"
        )

        texto.insert(
            tk.END,
            f"Para reprogramar: "
            f"{reporte_citas['reprogramar']}\n\n"
        )

        # =====================================================
        # ATENCIONES
        # =====================================================

        texto.insert(
            tk.END,
            "REPORTE DE ATENCIONES\n"
        )

        texto.insert(
            tk.END,
            "----------------------------------------\n"
        )

        texto.insert(
            tk.END,
            (
                f"Total: "
                f"{reporte_atenciones['total_atenciones']}\n"
            )
        )

        texto.insert(
            tk.END,
            (
                f"Pendientes: "
                f"{reporte_atenciones['pendientes']}\n"
            )
        )

        texto.insert(
            tk.END,
            (
                f"En proceso: "
                f"{reporte_atenciones['en_proceso']}\n"
            )
        )

        texto.insert(
            tk.END,
            (
                f"Finalizadas: "
                f"{reporte_atenciones['finalizadas']}\n\n"
            )
        )

        texto.insert(
            tk.END,
            "Diagnósticos registrados:\n"
        )

        for diagnostico in (
            reporte_atenciones["diagnosticos"]
        ):

            texto.insert(
                tk.END,
                f"- {diagnostico}\n"
            )


# =============================================================
# EJECUCIÓN
# =============================================================

if __name__ == "__main__":

    ventana = tk.Tk()

    aplicacion = VentanaPrincipal(
        ventana
    )

    ventana.mainloop()
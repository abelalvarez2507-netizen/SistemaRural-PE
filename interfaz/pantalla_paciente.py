import tkinter as tk
from tkinter import messagebox

from servicios.sistema_salud import SistemaSalud
from servicios.validaciones import validar_dni as validar_dni_valor

from interfaz.estilos import (
    COLOR_FONDO,
    COLOR_PANEL,
    COLOR_PANEL_CLARO,
    COLOR_ROJO,
    COLOR_ROJO_CLARO,
    COLOR_BLANCO,
    COLOR_GRIS_CLARO,
    COLOR_GRIS,
    FUENTE_LOGO,
    FUENTE_TITULO,
    FUENTE_SUBTITULO,
    FUENTE_SECCION,
    FUENTE_BOTON
)


class PantallaPaciente:

    def __init__(
        self,
        ventana,
        pantalla_inicio
    ):

        self.ventana = ventana
        self.pantalla_inicio = pantalla_inicio

        # Sistema principal del portal.
        self.sistema = SistemaSalud()

        # Paciente autenticado durante la sesión.
        self.paciente_actual = None

        # Pantalla actualmente mostrada dentro de la misma ventana.
        self.pantalla_actual = None

        # =====================================================
        # CONFIGURACIÓN
        # =====================================================

        self.ventana.title(
            "SaluPro - Portal del Paciente"
        )

        self.ventana.geometry(
            "950x700"
        )

        self.ventana.minsize(
            850,
            600
        )

        self.ventana.configure(
            bg=COLOR_FONDO
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

        self.crear_interfaz()

    # =========================================================
    # INTERFAZ PRINCIPAL
    # =========================================================

    def crear_interfaz(self):

        self._limpiar_contenido()

        contenedor = tk.Frame(
            self.ventana,
            bg=COLOR_FONDO
        )

        contenedor.pack(
            fill="both",
            expand=True
        )

        self.pantalla_actual = contenedor

        # =====================================================
        # BARRA SUPERIOR
        # =====================================================

        barra_superior = tk.Frame(
            contenedor,
            bg=COLOR_FONDO
        )

        barra_superior.pack(
            fill="x",
            padx=30,
            pady=(20, 10)
        )

        boton_volver = tk.Button(
            barra_superior,
            text="← Volver",
            font=FUENTE_BOTON,
            bg=COLOR_PANEL,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=15,
            pady=8,
            command=self.volver_a_inicio
        )

        boton_volver.pack(
            side="left"
        )

        logo = tk.Label(
            barra_superior,
            text="SALUPRO",
            font=FUENTE_LOGO,
            fg=COLOR_BLANCO,
            bg=COLOR_FONDO
        )

        logo.pack(
            side="right"
        )

        linea = tk.Frame(
            contenedor,
            bg=COLOR_ROJO,
            height=3
        )

        linea.pack(
            fill="x",
            padx=30,
            pady=(0, 25)
        )

        # =====================================================
        # TÍTULO
        # =====================================================

        titulo = tk.Label(
            contenedor,
            text="Portal del paciente",
            font=FUENTE_TITULO,
            fg=COLOR_BLANCO,
            bg=COLOR_FONDO
        )

        titulo.pack(
            pady=(5, 5)
        )

        subtitulo = tk.Label(
            contenedor,
            text=(
                "Consulta tus servicios de salud "
                "de manera segura."
            ),
            font=FUENTE_SUBTITULO,
            fg=COLOR_GRIS_CLARO,
            bg=COLOR_FONDO
        )

        subtitulo.pack(
            pady=(0, 20)
        )

        # =====================================================
        # PANEL DE IDENTIFICACIÓN
        # =====================================================

        panel_identificacion = tk.Frame(
            contenedor,
            bg=COLOR_PANEL
        )

        panel_identificacion.pack(
            fill="x",
            padx=80,
            pady=10
        )

        tk.Label(
            panel_identificacion,
            text="Identificación del paciente",
            font=FUENTE_SECCION,
            fg=COLOR_BLANCO,
            bg=COLOR_PANEL
        ).pack(
            pady=(18, 8)
        )

        tk.Label(
            panel_identificacion,
            text=(
                "Seleccione DNI o Código para acceder "
                "a su información."
            ),
            font=("Arial", 10),
            fg=COLOR_GRIS_CLARO,
            bg=COLOR_PANEL
        ).pack(
            pady=(0, 10)
        )

        fila_dni = tk.Frame(
            panel_identificacion,
            bg=COLOR_PANEL
        )

        fila_dni.pack(
            pady=(0, 15)
        )

        self.etiqueta_busqueda = tk.Label(
            fila_dni,
            text="Buscar por:",
            font=FUENTE_BOTON,
            fg=COLOR_BLANCO,
            bg=COLOR_PANEL
        )
        self.etiqueta_busqueda.pack(
            side="left",
            padx=(0, 8)
        )

        self.tipo_busqueda = tk.StringVar(
            value="DNI"
        )

        selector_busqueda = tk.OptionMenu(
            fila_dni,
            self.tipo_busqueda,
            "DNI",
            "Código",
            command=self._cambiar_tipo_busqueda
        )

        selector_busqueda.configure(
            font=FUENTE_BOTON,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2"
        )

        selector_busqueda["menu"].configure(
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO,
            activeforeground=COLOR_BLANCO
        )

        selector_busqueda.pack(
            side="left",
            padx=5
        )

        self.campo_dni = tk.Entry(
            fila_dni,
            width=18,
            font=("Arial", 12),
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            insertbackground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            justify="center"
        )

        self.campo_dni.pack(
            side="left",
            padx=5,
            ipady=7
        )

        # DNI o código: la cantidad de caracteres depende del selector.
        validacion_busqueda = self.ventana.register(
            self._validar_busqueda_tecla
        )

        self.campo_dni.config(
            validate="key",
            validatecommand=(
                validacion_busqueda,
                "%P"
            )
        )

        boton_ingresar = tk.Button(
            fila_dni,
            text="Ingresar",
            font=FUENTE_BOTON,
            bg=COLOR_ROJO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO_CLARO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=16,
            pady=7,
            command=self.autenticar_paciente
        )

        boton_ingresar.pack(
            side="left",
            padx=(10, 0)
        )

        boton_ingresar.bind(
            "<Enter>",
            lambda evento: boton_ingresar.configure(
                bg=COLOR_ROJO_CLARO
            )
        )

        boton_ingresar.bind(
            "<Leave>",
            lambda evento: boton_ingresar.configure(
                bg=COLOR_ROJO
            )
        )

        self.campo_dni.bind(
            "<Return>",
            lambda evento: self.autenticar_paciente()
        )

        # =====================================================
        # ESTADO DE SESIÓN
        # =====================================================

        self.etiqueta_sesion = tk.Label(
            contenedor,
            text="No hay paciente autenticado.",
            font=("Arial", 10, "bold"),
            fg=COLOR_GRIS_CLARO,
            bg=COLOR_FONDO
        )

        self.etiqueta_sesion.pack(
            pady=(8, 15)
        )

        # =====================================================
        # PANEL DE OPCIONES
        # =====================================================

        panel_opciones = tk.Frame(
            contenedor,
            bg=COLOR_FONDO
        )

        panel_opciones.pack(
            pady=5
        )

        tarjeta_citas = self.crear_tarjeta(
            panel_opciones,
            "Mis citas",
            "Consulta tus citas médicas.",
            self.mostrar_citas
        )

        tarjeta_citas.grid(
            row=0,
            column=0,
            padx=15,
            pady=10
        )

        tarjeta_historial = self.crear_tarjeta(
            panel_opciones,
            "Mi historial clínico",
            "Consulta tu historial médico.",
            self.mostrar_historial
        )

        tarjeta_historial.grid(
            row=0,
            column=1,
            padx=15,
            pady=10
        )

        tarjeta_datos = self.crear_tarjeta(
            panel_opciones,
            "Mis datos",
            "Consulta tus datos personales.",
            self.mostrar_datos
        )

        tarjeta_datos.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=15,
            pady=10
        )

        # =====================================================
        # INFORMACIÓN
        # =====================================================

        informacion = tk.Label(
            contenedor,
            text=(
                "Por seguridad, el DNI no se muestra "
                "completo después de la autenticación."
            ),
            font=("Arial", 9),
            fg=COLOR_GRIS,
            bg=COLOR_FONDO,
            justify="center"
        )

        informacion.pack(
            pady=(15, 0)
        )

    # =========================================================
    # UTILIDADES DE NAVEGACIÓN
    # =========================================================

    def _limpiar_contenido(self):
        """Elimina la pantalla actual sin cerrar la ventana principal."""
        for widget in self.ventana.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

        self.pantalla_actual = None

    def _crear_pantalla_interna(self, titulo):
        """
        Crea una pantalla interna dentro del mismo Tk.
        No abre una ventana nueva.
        """
        self._limpiar_contenido()

        pantalla = tk.Frame(
            self.ventana,
            bg=COLOR_FONDO
        )

        pantalla.pack(
            fill="both",
            expand=True
        )

        self.pantalla_actual = pantalla

        barra = tk.Frame(
            pantalla,
            bg=COLOR_FONDO
        )

        barra.pack(
            fill="x",
            padx=30,
            pady=(20, 10)
        )

        boton_volver = tk.Button(
            barra,
            text="← Volver",
            font=FUENTE_BOTON,
            bg=COLOR_PANEL,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=15,
            pady=8,
            command=self.crear_interfaz
        )

        boton_volver.pack(
            side="left"
        )

        tk.Label(
            barra,
            text="SALUPRO",
            font=FUENTE_LOGO,
            fg=COLOR_BLANCO,
            bg=COLOR_FONDO
        ).pack(
            side="right"
        )

        tk.Frame(
            pantalla,
            bg=COLOR_ROJO,
            height=3
        ).pack(
            fill="x",
            padx=30,
            pady=(0, 20)
        )

        tk.Label(
            pantalla,
            text=titulo,
            font=FUENTE_TITULO,
            fg=COLOR_BLANCO,
            bg=COLOR_FONDO
        ).pack(
            pady=(5, 5)
        )

        return pantalla

    def _alternar_pantalla_completa(self, evento=None):
        try:
            actual = bool(
                self.ventana.attributes("-fullscreen")
            )

            self.ventana.attributes(
                "-fullscreen",
                not actual
            )

        except tk.TclError:

            try:
                estado = self.ventana.state()

                self.ventana.state(
                    "normal"
                    if estado == "zoomed"
                    else "zoomed"
                )

            except tk.TclError:
                pass

    def _validar_busqueda_tecla(self, nuevo_valor):
        if nuevo_valor == "":
            return True

        tipo = self.tipo_busqueda.get()

        if tipo == "DNI":
            return (
                nuevo_valor.isdigit()
                and len(nuevo_valor) <= 8
            )

        return (
            nuevo_valor.isalnum()
            and len(nuevo_valor) <= 4
        )

    def _validar_dni_tecla(self, nuevo_valor):
        if nuevo_valor == "":
            return True

        return (
            nuevo_valor.isdigit()
            and len(nuevo_valor) <= 8
        )

    def _cambiar_tipo_busqueda(self, valor):
        self.campo_dni.delete(
            0,
            tk.END
        )

        if valor == "DNI":
            self.etiqueta_busqueda.configure(
                text="Buscar por DNI:"
            )
        else:
            self.etiqueta_busqueda.configure(
                text="Buscar por código:"
            )

        self.campo_dni.focus_set()

    # =========================================================
    # CREAR TARJETA
    # =========================================================

    def crear_tarjeta(
        self,
        padre,
        titulo,
        descripcion,
        comando
    ):

        tarjeta = tk.Frame(
            padre,
            bg=COLOR_PANEL,
            width=280,
            height=125
        )

        tarjeta.pack_propagate(
            False
        )

        etiqueta_titulo = tk.Label(
            tarjeta,
            text=titulo,
            font=FUENTE_SECCION,
            fg=COLOR_BLANCO,
            bg=COLOR_PANEL
        )

        etiqueta_titulo.pack(
            pady=(16, 5)
        )

        etiqueta_descripcion = tk.Label(
            tarjeta,
            text=descripcion,
            font=("Arial", 10),
            fg=COLOR_GRIS_CLARO,
            bg=COLOR_PANEL,
            wraplength=230
        )

        etiqueta_descripcion.pack(
            pady=(0, 8)
        )

        boton = tk.Button(
            tarjeta,
            text="Ingresar",
            font=FUENTE_BOTON,
            bg=COLOR_ROJO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO_CLARO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=15,
            pady=5,
            command=comando
        )

        boton.pack(
            pady=3
        )

        boton.bind(
            "<Enter>",
            lambda evento: boton.configure(
                bg=COLOR_ROJO_CLARO
            )
        )

        boton.bind(
            "<Leave>",
            lambda evento: boton.configure(
                bg=COLOR_ROJO
            )
        )

        return tarjeta

    # =========================================================
    # AUTENTICACIÓN
    # =========================================================

    def autenticar_paciente(self):

        valor = self.campo_dni.get().strip()
        tipo = self.tipo_busqueda.get()

        if not valor:

            messagebox.showwarning(
                "Dato requerido",
                f"Ingresa tu {tipo.lower()}."
            )

            return

        if tipo == "DNI":
            try:
                valor = validar_dni_valor(valor)
            except ValueError as error:
                messagebox.showerror("DNI inválido", str(error))
                return
        else:
            if (
                not valor.isalnum()
                or len(valor) != 4
            ):

                messagebox.showerror(
                    "Código inválido",
                    "El código debe contener exactamente 4 caracteres "
                    "entre letras y números."
                )

                return

        if tipo == "DNI":
            pacientes = (
                self.sistema
                .buscar_paciente_por_dni(valor)
            )
        else:
            pacientes = (
                self.sistema
                .buscar_paciente_por_codigo(valor)
            )

        if not pacientes:

            self.paciente_actual = None

            tipo_nombre = "DNI" if tipo == "DNI" else "código"

            self.etiqueta_sesion.configure(
                text=(
                    "No se encontró un paciente con ese "
                    f"{tipo_nombre}."
                ),
                fg=COLOR_ROJO_CLARO
            )

            messagebox.showerror(
                "Acceso no autorizado",
                "No se encontró un paciente "
                f"registrado con ese {tipo_nombre}."
            )

            return

        self.paciente_actual = pacientes[0]

        self.etiqueta_sesion.configure(
            text=(
                "Paciente identificado: "
                f"{self.paciente_actual.nombre}"
            ),
            fg=COLOR_BLANCO
        )

        self.campo_dni.delete(
            0,
            tk.END
        )

        messagebox.showinfo(
            "Acceso correcto",
            "Paciente autenticado correctamente."
        )

    # =========================================================
    # VALIDAR SESIÓN
    # =========================================================

    def paciente_autenticado(self):

        if self.paciente_actual is None:

            messagebox.showwarning(
                "Acceso requerido",
                "Primero debes ingresar tu DNI "
                "para consultar esta información."
            )

            self.campo_dni.focus_set()

            return False

        return True

    # =========================================================
    # VOLVER
    # =========================================================

    def volver_a_inicio(self):

        try:
            if self.sistema is not None:
                self.sistema.cerrar()
        except Exception:
            pass

        try:
            self._limpiar_contenido()
            self.paciente_actual = None
            self.pantalla_inicio.mostrar()
        except tk.TclError:
            pass

    # =========================================================
    # MIS CITAS
    # =========================================================

    def mostrar_citas(self):

        if not self.paciente_autenticado():
            return

        paciente = self.paciente_actual

        citas = list(
            filter(
                lambda cita:
                    cita.paciente.codigo
                    == paciente.codigo,
                self.sistema.obtener_citas()
            )
        )

        citas = sorted(
            citas,
            key=lambda cita: str(cita.fecha)
        )

        ventana = self._crear_pantalla_interna(
            "Mis citas"
        )

        tk.Label(
            ventana,
            text=paciente.nombre,
            font=FUENTE_SUBTITULO,
            fg=COLOR_GRIS_CLARO,
            bg=COLOR_FONDO
        ).pack(
            pady=(0, 15)
        )

        marco_resultado = tk.Frame(
            ventana,
            bg=COLOR_FONDO
        )

        marco_resultado.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=10
        )

        texto = tk.Text(
            marco_resultado,
            width=78,
            height=17,
            font=("Arial", 10),
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            insertbackground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            padx=15,
            pady=15
        )

        texto.pack(
            fill="both",
            expand=True
        )

        if not citas:

            texto.insert(
                tk.END,
                "No tienes citas registradas."
            )

        else:

            for indice, cita in enumerate(
                citas,
                start=1
            ):

                texto.insert(
                    tk.END,
                    f"{indice}. "
                    f"Cita: {cita.codigo}\n"
                )

                texto.insert(
                    tk.END,
                    f"Fecha: {cita.fecha}\n"
                )

                texto.insert(
                    tk.END,
                    f"Motivo: {cita.motivo}\n"
                )

                texto.insert(
                    tk.END,
                    (
                        "Profesional: "
                        f"{cita.profesional.nombre}\n"
                    )
                )

                texto.insert(
                    tk.END,
                    (
                        "Especialidad: "
                        f"{cita.profesional.especialidad}\n"
                    )
                )

                texto.insert(
                    tk.END,
                    f"Estado: {cita.estado}\n"
                )

                texto.insert(
                    tk.END,
                    "\n"
                )

        texto.configure(
            state="disabled"
        )

    # =========================================================
    # HISTORIAL
    # =========================================================

    def mostrar_historial(self):

        if not self.paciente_autenticado():
            return

        paciente = self.paciente_actual

        try:

            historial = (
                self.sistema
                .obtener_historial_paciente(
                    paciente.codigo
                )
            )

        except ValueError as error:

            messagebox.showerror(
                "Historial",
                str(error)
            )

            return

        ventana = self._crear_pantalla_interna(
            "Mi historial clínico"
        )

        tk.Label(
            ventana,
            text=paciente.nombre,
            font=FUENTE_SUBTITULO,
            fg=COLOR_GRIS_CLARO,
            bg=COLOR_FONDO
        ).pack(
            pady=(0, 15)
        )

        marco_resultado = tk.Frame(
            ventana,
            bg=COLOR_FONDO
        )

        marco_resultado.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=10
        )

        texto = tk.Text(
            marco_resultado,
            width=82,
            height=20,
            font=("Arial", 10),
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO,
            insertbackground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            padx=15,
            pady=15
        )

        texto.pack(
            fill="both",
            expand=True
        )

        citas = historial["citas"]
        atenciones = historial["atenciones"]

        texto.insert(
            tk.END,
            "=== CITAS ATENDIDAS ===\n\n"
        )

        if not citas:

            texto.insert(
                tk.END,
                "No existen citas atendidas registradas.\n\n"
            )

        else:

            for cita in citas:

                texto.insert(
                    tk.END,
                    f"Cita: {cita.codigo}\n"
                )

                texto.insert(
                    tk.END,
                    f"Fecha: {cita.fecha}\n"
                )

                texto.insert(
                    tk.END,
                    f"Motivo: {cita.motivo}\n"
                )

                texto.insert(
                    tk.END,
                    (
                        "Profesional: "
                        f"{cita.profesional.nombre}\n"
                    )
                )

                texto.insert(
                    tk.END,
                    "\n"
                )

        texto.insert(
            tk.END,
            "=== ATENCIONES FINALIZADAS ===\n\n"
        )

        if not atenciones:

            texto.insert(
                tk.END,
                "No existen atenciones finalizadas.\n"
            )

        else:

            for atencion in atenciones:

                texto.insert(
                    tk.END,
                    f"Atención: {atencion.codigo}\n"
                )

                texto.insert(
                    tk.END,
                    f"Cita: {atencion.cita.codigo}\n"
                )

                texto.insert(
                    tk.END,
                    (
                        "Diagnóstico: "
                        f"{atencion.diagnostico}\n"
                    )
                )

                texto.insert(
                    tk.END,
                    f"Estado: {atencion.estado}\n"
                )

                texto.insert(
                    tk.END,
                    "\n"
                )

        texto.configure(
            state="disabled"
        )

    # =========================================================
    # MIS DATOS
    # =========================================================

    def mostrar_datos(self):

        if not self.paciente_autenticado():
            return

        paciente = self.paciente_actual

        ventana = self._crear_pantalla_interna(
            "Mis datos"
        )

        panel = tk.Frame(
            ventana,
            bg=COLOR_PANEL
        )

        panel.pack(
            padx=40,
            pady=15,
            fill="both",
            expand=True
        )

        datos = [
            (
                "Código",
                paciente.codigo
            ),
            (
                "Nombre",
                paciente.nombre
            ),
            (
                "Edad",
                str(paciente.edad)
            ),
            (
                "DNI",
                "********"
            )
        ]

        for etiqueta, valor in datos:

            fila = tk.Frame(
                panel,
                bg=COLOR_PANEL
            )

            fila.pack(
                fill="x",
                padx=30,
                pady=9
            )

            tk.Label(
                fila,
                text=f"{etiqueta}:",
                font=FUENTE_BOTON,
                fg=COLOR_GRIS_CLARO,
                bg=COLOR_PANEL,
                width=12,
                anchor="w"
            ).pack(
                side="left"
            )

            tk.Label(
                fila,
                text=valor,
                font=FUENTE_BOTON,
                fg=COLOR_BLANCO,
                bg=COLOR_PANEL,
                anchor="w"
            ).pack(
                side="left"
            )

        tk.Label(
            panel,
            text=(
                "El DNI se muestra protegido por "
                "seguridad de los datos personales."
            ),
            font=("Arial", 9),
            fg=COLOR_GRIS_CLARO,
            bg=COLOR_PANEL,
            justify="center"
        ).pack(
            pady=(20, 10)
        )
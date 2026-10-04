import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from modelos.cita import Cita
from servicios.sistema_salud import SistemaSalud
from servicios.validaciones import normalizar_fecha
from interfaz.campos import configurar_mascara_fecha
from servicios.validaciones import validar_dni as validar_dni_valor

from interfaz.estilos import (
    COLOR_FONDO,
    COLOR_PANEL,
    COLOR_PANEL_CLARO,
    COLOR_ROJO,
    COLOR_ROJO_CLARO,
    COLOR_BLANCO,
    COLOR_ERROR,
    COLOR_TEXTO,
    COLOR_GRIS_CLARO,
    COLOR_GRIS,
    FUENTE_LOGO,
    FUENTE_TITULO,
    FUENTE_SUBTITULO,
    FUENTE_SECCION,
    FUENTE_BOTON
)
from interfaz.navegacion import VistaDesplazable, instalar_navegacion


class PantallaPaciente:

    def __init__(
        self,
        ventana,
        pantalla_inicio,
        sesion,
    ):

        if sesion is None or sesion.rol != "paciente":
            raise ValueError("Se requiere una sesión autenticada de paciente.")

        self.ventana = ventana
        self.pantalla_inicio = pantalla_inicio
        self.sesion = sesion

        # Sistema principal del portal.
        self.sistema = SistemaSalud()

        # Paciente autenticado durante la sesión.
        pacientes = self.sistema.buscar_paciente_por_codigo(
            sesion.codigo_referencia or ""
        )
        if not pacientes:
            self.sistema.cerrar()
            raise ValueError("La cuenta ya no está vinculada a un paciente activo.")
        self.paciente_actual = pacientes[0]

        # Pantalla actualmente mostrada dentro de la misma ventana.
        self.pantalla_actual = None
        self._pantalla_titulo = "Inicio"
        self._temporizador = None

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
        self._temporizador = self.ventana.after(
            60000,
            self._revisar_citas_vencidas,
        )

    def _revisar_citas_vencidas(self):
        try:
            vencidas = self.sistema.actualizar_citas_vencidas()
            if vencidas and self._pantalla_titulo == "Mis citas" and self.paciente_actual:
                self.mostrar_citas()
            self._temporizador = self.ventana.after(
                60000,
                self._revisar_citas_vencidas,
            )
        except tk.TclError:
            self._temporizador = None

    # =========================================================
    # INTERFAZ PRINCIPAL
    # =========================================================

    def crear_interfaz(self):

        self._limpiar_contenido()
        self._pantalla_titulo = "Inicio"
        instalar_navegacion(
            self.ventana,
            volver=self.volver_a_inicio,
            inicio=self.volver_a_inicio,
        )

        vista = VistaDesplazable(
            self.ventana,
            COLOR_FONDO,
        )
        vista.pack(fill="both", expand=True)
        contenedor = vista.contenido
        self.pantalla_actual = vista

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
            fg=COLOR_TEXTO,
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
            fg=COLOR_TEXTO,
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
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO
        )

        titulo.pack(
            pady=(5, 5)
        )

        # La autenticación ocurre antes de abrir este portal; no se permite
        # cambiar a otro paciente desde una sesión ya iniciada.
        panel_identificacion = tk.Frame(contenedor, bg=COLOR_PANEL, padx=24, pady=16)
        panel_identificacion.pack(fill="x", padx=80, pady=10)
        tk.Label(
            panel_identificacion,
            text=f"{self.paciente_actual.nombre}  ·  Cuenta {self.sesion.usuario}",
            font=("Arial", 11),
            fg=COLOR_GRIS_CLARO,
            bg=COLOR_PANEL,
        ).pack()

        self.etiqueta_sesion = tk.Label(
            contenedor,
            text="",
            font=("Arial", 10, "bold"),
            fg=COLOR_GRIS_CLARO,
            bg=COLOR_FONDO,
        )
        self.etiqueta_sesion.pack(pady=(8, 15))

        # =====================================================
        # ESTADO DE SESIÓN
        # =====================================================

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
        panel_opciones.columnconfigure(0, weight=1, uniform="opciones_paciente")
        panel_opciones.columnconfigure(1, weight=1, uniform="opciones_paciente")

        tarjeta_citas = self.crear_tarjeta(
            panel_opciones,
            "Mis citas",
            "",
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
            "",
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
            "",
            self.mostrar_datos
        )

        tarjeta_datos.grid(
            row=1,
            column=0,
            padx=15,
            pady=10
        )

        tarjeta_reservar = self.crear_tarjeta(
            panel_opciones,
            "Solicitar una cita",
            "",
            self.solicitar_cita
        )

        tarjeta_reservar.grid(
            row=1,
            column=1,
            padx=15,
            pady=10
        )

        # =====================================================
        # INFORMACIÓN
        # =====================================================

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

        vista = VistaDesplazable(
            self.ventana,
            COLOR_FONDO,
        )
        vista.pack(fill="both", expand=True)
        pantalla = vista.contenido

        self.pantalla_actual = vista
        self._pantalla_titulo = titulo
        instalar_navegacion(
            self.ventana,
            volver=self.crear_interfaz,
            inicio=self.volver_a_inicio,
        )

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
            fg=COLOR_TEXTO,
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
            fg=COLOR_TEXTO,
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
            fg=COLOR_TEXTO,
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
        return (
            all(
                caracter.isalnum() or caracter in "-_"
                for caracter in nuevo_valor
            )
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
            fg=COLOR_TEXTO,
            bg=COLOR_PANEL
        )

        etiqueta_titulo.pack(
            pady=(16, 5)
        )

        if descripcion:
            etiqueta_descripcion = tk.Label(
                tarjeta,
                text=descripcion,
                font=("Arial", 10),
                fg=COLOR_GRIS_CLARO,
                bg=COLOR_PANEL,
                wraplength=230
            )
            etiqueta_descripcion.pack(pady=(0, 8))

        boton = tk.Button(
            tarjeta,
            text="Abrir",
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

        # La identidad se valida en el modal de acceso, antes de abrir el
        # portal. La sesión actual no puede cambiarse desde esta pantalla.
        if self.paciente_actual is not None:
            return

        valor = self.campo_dni.get().strip()

        if not valor:

            messagebox.showwarning(
                "Dato requerido",
                "Ingresa tu código o DNI."
            )

            return

        es_dni = valor.isdigit() and len(valor) == 8
        tipo = "DNI" if es_dni else "Código"
        self.tipo_busqueda.set(tipo)

        if es_dni:
            try:
                valor = validar_dni_valor(valor)
            except ValueError as error:
                messagebox.showerror("DNI inválido", str(error))
                return
        else:
            if (
                not self._validar_busqueda_tecla(valor)
                or len(valor) < 2
            ):

                messagebox.showerror(
                    "Código inválido",
                    "El código debe tener 2 o más letras, números, "
                    "guiones o guiones bajos."
                )

                return

        if es_dni:
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
                fg=COLOR_ERROR
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
            fg=COLOR_TEXTO
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
                "Primero debes ingresar tu código o DNI "
                "para consultar esta información."
            )

            self.campo_dni.focus_set()

            return False

        return True

    # =========================================================
    # VOLVER
    # =========================================================

    def volver_a_inicio(self):

        if self._temporizador:
            try:
                self.ventana.after_cancel(self._temporizador)
            except tk.TclError:
                pass
            self._temporizador = None

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
    # SOLICITAR CITA
    # =========================================================

    def solicitar_cita(self):
        if not self.paciente_autenticado():
            return

        medicos = [
            profesional
            for profesional in self.sistema.obtener_personal()
            if "enfermer" not in profesional.especialidad.casefold()
        ]
        if not medicos:
            messagebox.showwarning(
                "Sin profesionales",
                "Todavía no hay médicos registrados para reservar una cita.",
            )
            return

        pantalla = self._crear_pantalla_interna("Solicitar una cita")
        tk.Label(
            pantalla,
            text=f"Paciente: {self.paciente_actual.nombre}",
            font=FUENTE_SUBTITULO,
            fg=COLOR_GRIS_CLARO,
            bg=COLOR_FONDO,
        ).pack(pady=(0, 12))

        formulario = tk.Frame(pantalla, bg=COLOR_PANEL, padx=24, pady=18)
        formulario.pack(fill="x", padx=60, pady=10)

        tk.Label(
            formulario,
            text="Atención médica general",
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            font=FUENTE_BOTON,
        ).pack(anchor="w")

        tk.Label(formulario, text="Fecha (DD/MM/AAAA):", bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(anchor="w")
        entrada_fecha = tk.Entry(
            formulario,
            width=20,
            justify="center",
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            relief="flat",
        )
        entrada_fecha.pack(anchor="w", pady=(4, 12), ipady=6)
        configurar_mascara_fecha(entrada_fecha)

        tk.Label(
            formulario,
            text="Horarios disponibles (turnos de 30 minutos):",
            font=FUENTE_BOTON,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
        ).pack(anchor="w")
        tk.Label(
            formulario,
            text="Atención de 07:00 a 18:00",
            font=("Arial", 9),
            bg=COLOR_PANEL,
            fg=COLOR_GRIS,
        ).pack(anchor="w", pady=(2, 6))

        hora_var = tk.StringVar(value="")
        menu_hora = tk.OptionMenu(formulario, hora_var, "")
        menu_hora.configure(bg=COLOR_PANEL_CLARO, fg=COLOR_TEXTO, relief="flat")
        menu_hora.pack(anchor="w", pady=(0, 12))

        def actualizar_horarios(event=None):
            try:
                fecha = normalizar_fecha(entrada_fecha.get())
                horarios = self.sistema.horarios_disponibles_para_cita(
                    fecha,
                    paciente_codigo=self.paciente_actual.codigo,
                )
            except ValueError:
                horarios = []
            menu = menu_hora["menu"]
            menu.delete(0, "end")
            if horarios:
                for hora in horarios:
                    menu.add_command(
                        label=hora,
                        command=lambda valor=hora: hora_var.set(valor),
                    )
                hora_var.set(horarios[0])
            else:
                menu.add_command(
                    label="Ingrese una fecha valida",
                    command=lambda: None,
                )
                hora_var.set("")

        self._boton_cita = tk.Button(
            formulario,
            text="Ver horarios disponibles",
            command=actualizar_horarios,
            font=FUENTE_BOTON,
            bg=COLOR_ROJO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO_CLARO,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
        )
        self._boton_cita.pack(anchor="w", pady=(0, 12))
        entrada_fecha.bind("<FocusOut>", actualizar_horarios)
        entrada_fecha.bind("<Return>", actualizar_horarios)

        tk.Label(formulario, text="Motivo de la cita:", bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(anchor="w")
        entrada_motivo = tk.Entry(
            formulario,
            width=55,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            relief="flat",
        )
        entrada_motivo.pack(anchor="w", pady=(4, 8), ipady=6)

        def guardar():
            try:
                fecha = normalizar_fecha(entrada_fecha.get())
                if not hora_var.get():
                    raise ValueError("Selecciona un horario disponible.")
                cita = self.sistema.crear_cita_asignacion_automatica(
                    self.paciente_actual,
                    fecha,
                    entrada_motivo.get(),
                    hora_var.get(),
                )
                messagebox.showinfo(
                    "Cita solicitada",
                    f"Tu cita quedó registrada para el {cita.fecha} a las {cita.hora} con {cita.profesional.nombre} ({cita.profesional.especialidad}).",
                )
                self.crear_interfaz()
            except ValueError as error:
                messagebox.showerror("No se pudo registrar la cita", str(error))

        tk.Button(
            formulario,
            text="Confirmar cita",
            command=guardar,
            font=FUENTE_BOTON,
            bg=COLOR_ROJO,
            fg=COLOR_BLANCO,
            activebackground=COLOR_ROJO_CLARO,
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=8,
        ).pack(anchor="w", pady=(8, 0))

    # =========================================================
    # MIS CITAS
    # =========================================================

    def mostrar_citas(self):

        if not self.paciente_autenticado():
            return

        self.sistema.actualizar_citas_vencidas()
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
            key=lambda cita: cita.fecha_hora
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
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
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
                    f"Fecha y hora: {cita.fecha} · {cita.hora}\n"
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
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
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
        ventas_medicamentos = historial.get("ventas_medicamentos", [])

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
                    f"Fecha y hora: {cita.fecha} · {cita.hora}\n"
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
                "No hay atenciones finalizadas ni derivaciones en curso.\n"
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

                if (
                    atencion.informe_derivacion
                    and atencion.informe_derivacion != atencion.diagnostico
                ):
                    texto.insert(
                        tk.END,
                        f"Informe de derivación: {atencion.informe_derivacion}\n",
                    )

                if atencion.profesional_derivado:
                    texto.insert(
                        tk.END,
                        "Derivación: "
                        f"{atencion.profesional_derivado.nombre} · "
                        f"{atencion.profesional_derivado.especialidad}\n",
                    )

                texto.insert(
                    tk.END,
                    f"Estado: {atencion.estado}\n"
                )

                if atencion.recetas:
                    texto.insert(tk.END, "Medicamentos recetados:\n")
                    for receta in atencion.recetas:
                        texto.insert(tk.END, f"  • {receta.mostrar_informacion()}\n")

                texto.insert(
                    tk.END,
                    "\n"
                )

        texto.insert(tk.END, "=== MEDICAMENTOS REGISTRADOS EN VENTA ===\n\n")
        if not ventas_medicamentos:
            texto.insert(tk.END, "No hay medicamentos de venta vinculados a tu historial.\n")
        else:
            for venta in ventas_medicamentos:
                (_id, medicamento, lote, cantidad, _precio, total, codigo, vendedor, fecha_hora) = venta
                texto.insert(
                    tk.END,
                    f"{fecha_hora} · {medicamento} · Lote {lote} · "
                    f"{cantidad} unidad(es) · S/ {float(total):.2f} · "
                    f"Paciente {codigo}\n",
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
                fg=COLOR_TEXTO,
                bg=COLOR_PANEL,
                anchor="w"
            ).pack(
                side="left"
            )


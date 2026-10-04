from datetime import date
import tkinter as tk
from tkinter import messagebox

from modelos.atencion_medica import AtencionMedica
from modelos.medicamento_recetado import MedicamentoRecetado
from servicios.sistema_salud import SistemaSalud
from servicios.validaciones import validar_diagnostico
from interfaz.campos import configurar_mascara_fecha

from interfaz.estilos import (
    COLOR_FONDO,
    COLOR_PANEL,
    COLOR_PANEL_CLARO,
    COLOR_ROJO,
    COLOR_ROJO_CLARO,
    COLOR_BLANCO,
    COLOR_TEXTO,
    COLOR_GRIS_CLARO,
    COLOR_GRIS,
    FUENTE_LOGO,
    FUENTE_TITULO,
    FUENTE_SUBTITULO,
    FUENTE_SECCION,
    FUENTE_BOTON,
)
from interfaz.navegacion import (
    PASO_FINO,
    VistaDesplazable,
    comando_barra,
    desplazar_por_evento,
    instalar_navegacion,
)


class PantallaProfesional:
    """Portal de agenda y registro de atenciones del profesional."""

    def __init__(self, ventana, pantalla_inicio, sesion):
        if sesion is None or sesion.rol != "profesional":
            raise ValueError("Se requiere una sesión profesional autenticada.")
        self.ventana = ventana
        self.pantalla_inicio = pantalla_inicio
        self.sesion = sesion
        self.sistema = SistemaSalud()
        profesionales = self.sistema.buscar_personal_por_codigo(
            sesion.codigo_referencia or ""
        )
        if not profesionales:
            self.sistema.cerrar()
            raise ValueError("La cuenta ya no está vinculada a personal activo.")
        self.profesional_actual = profesionales[0]
        self._temporizador = None
        self._pantalla_en_edicion = False
        self._vista_actual = "agenda"
        self.ventana.title("SaluPro - Portal del Profesional")
        self.ventana.configure(bg=COLOR_FONDO)
        self.mostrar_agenda()

    def _limpiar(self):
        for widget in self.ventana.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

    def _boton(self, padre, texto, comando, color=COLOR_ROJO):
        boton = tk.Button(
            padre,
            text=texto,
            command=comando,
            font=FUENTE_BOTON,
            bg=color,
            fg=(
                COLOR_BLANCO
                if color == COLOR_ROJO
                else COLOR_TEXTO
            ),
            activebackground=COLOR_ROJO_CLARO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            takefocus=True,
            padx=14,
            pady=8,
        )
        boton.bind(
            "<Enter>",
            lambda evento: boton.configure(
                bg=COLOR_ROJO_CLARO,
                fg=COLOR_BLANCO,
            ),
        )
        boton.bind(
            "<Leave>",
            lambda evento: boton.configure(
                bg=color,
                fg=(
                    COLOR_BLANCO
                    if color == COLOR_ROJO
                    else COLOR_TEXTO
                ),
            ),
        )
        return boton

    def _marco_base(self, titulo, subtitulo=None, volver=None):
        self._limpiar()
        vista = VistaDesplazable(self.ventana, COLOR_FONDO)
        vista.pack(fill="both", expand=True)
        contenedor = vista.contenido
        contenedor.configure(padx=32, pady=22)
        instalar_navegacion(
            self.ventana,
            volver=volver or self.volver_a_inicio,
            inicio=self.volver_a_inicio,
        )
        barra = tk.Frame(contenedor, bg=COLOR_FONDO)
        barra.pack(fill="x", pady=(0, 18))
        self._boton(
            barra,
            "← Volver a la agenda" if volver else "← Volver al inicio",
            volver or self.volver_a_inicio,
            COLOR_PANEL,
        ).pack(side="left")
        tk.Label(
            barra,
            text="SALUPRO",
            font=FUENTE_LOGO,
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO,
        ).pack(side="right")
        tk.Frame(contenedor, bg=COLOR_ROJO, height=3).pack(fill="x")
        tk.Label(
            contenedor,
            text=titulo,
            font=FUENTE_TITULO,
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO,
        ).pack(pady=(20, 5))
        if subtitulo:
            tk.Label(
                contenedor,
                text=subtitulo,
                font=FUENTE_SUBTITULO,
                fg=COLOR_GRIS_CLARO,
                bg=COLOR_FONDO,
            ).pack(pady=(0, 15))
        return contenedor

    def mostrar_acceso(self):
        contenedor = self._marco_base(
            "Acceso del profesional",
            "Ingresa tu código profesional o DNI.",
        )
        tarjeta = tk.Frame(contenedor, bg=COLOR_PANEL, padx=28, pady=24)
        tarjeta.pack(pady=24)
        tk.Label(
            tarjeta,
            text="Código profesional o DNI",
            font=FUENTE_SECCION,
            fg=COLOR_TEXTO,
            bg=COLOR_PANEL,
        ).pack(pady=(0, 12))
        self.entrada_identificacion = tk.Entry(
            tarjeta,
            width=28,
            font=("Arial", 14),
            justify="center",
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            relief="flat",
        )
        self.entrada_identificacion.pack(ipady=8)
        validacion = self.ventana.register(self._validar_identificacion)
        self.entrada_identificacion.configure(
            validate="key",
            validatecommand=(validacion, "%P"),
        )
        self._boton(tarjeta, "Ingresar", self.autenticar).pack(pady=(15, 0))
        tk.Label(
            tarjeta,
            text="Por seguridad, el DNI no se muestra por completo después de la autenticación.",
            font=("Arial", 9),
            fg=COLOR_GRIS,
            bg=COLOR_PANEL,
            justify="center",
            wraplength=380,
        ).pack(pady=(12, 0))
        self.entrada_identificacion.bind(
            "<Return>",
            lambda evento: self.autenticar(),
        )
        self.entrada_identificacion.focus_set()

    @staticmethod
    def _validar_identificacion(valor):
        return all(
            caracter.isalnum() or caracter in "-_" for caracter in valor
        )

    def autenticar(self):
        if self.profesional_actual is not None:
            return
        valor = self.entrada_identificacion.get().strip()
        if not valor:
            messagebox.showwarning("Dato requerido", "Ingresa tu código o DNI.")
            return
        if valor.isdigit() and len(valor) == 8:
            profesionales = self.sistema.buscar_personal_por_dni(valor)
        elif self._validar_identificacion(valor) and len(valor) >= 2:
            profesionales = self.sistema.buscar_personal_por_codigo(valor)
        else:
            profesionales = []
        if not profesionales:
            messagebox.showerror(
                "Acceso no autorizado",
                "No se encontró un profesional registrado con ese código o DNI.",
            )
            return
        self.profesional_actual = profesionales[0]
        self.mostrar_agenda()

    def mostrar_agenda(self):
        self._pantalla_en_edicion = False
        self._vista_actual = "agenda"
        profesional = self.profesional_actual
        self.sistema.actualizar_citas_vencidas()
        contenedor = self._marco_base(
            "Agenda profesional",
            f"{profesional.nombre} · {profesional.especialidad} · Código {profesional.codigo_profesional}",
        )
        citas = sorted(
            [
                cita
                for cita in self._citas_para_profesional()
                if not self._derivada_a_otro(cita)
                and not (
                    self._atencion_de(cita)
                    and self._atencion_de(cita).estado == "Finalizada"
                )
                and (
                    cita.estado not in {"Atendida", "No atendida", "Cancelada"}
                    or self._derivada_a_actual(cita)
                )
            ],
            key=lambda cita: cita.fecha_hora,
        )
        tk.Label(
            contenedor,
            text=f"Atenciones activas: {len(citas)}",
            font=FUENTE_SECCION,
            fg=COLOR_ROJO_CLARO,
            bg=COLOR_FONDO,
        ).pack(anchor="w", pady=(6, 12))

        accesos = tk.Frame(contenedor, bg=COLOR_FONDO)
        accesos.pack(fill="x", pady=(0, 12))
        self._boton(
            accesos, "Atenciones de hoy", self.mostrar_atenciones_hoy, COLOR_PANEL
        ).pack(side="left", padx=(0, 8))
        self._boton(
            accesos, "Historial y derivaciones", self.mostrar_historial, COLOR_PANEL
        ).pack(side="left")

        agenda = tk.Frame(contenedor, bg=COLOR_FONDO)
        agenda.pack(fill="both", expand=True)
        canvas = tk.Canvas(
            agenda,
            bg=COLOR_FONDO,
            highlightthickness=0,
            yscrollincrement=PASO_FINO,
            height=640,
        )
        barra = tk.Scrollbar(
            agenda, orient="vertical", command=comando_barra(canvas)
        )
        contenido = tk.Frame(canvas, bg=COLOR_FONDO)
        ventana_canvas = canvas.create_window(
            (0, 0), window=contenido, anchor="nw"
        )
        contenido.bind(
            "<Configure>",
            lambda evento: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda evento: canvas.itemconfigure(ventana_canvas, width=evento.width),
        )
        canvas.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self._enlazar_rueda(canvas, contenido)

        if not citas:
            tk.Label(
                contenido,
                text="No tienes atenciones activas asignadas.",
                font=FUENTE_SUBTITULO,
                fg=COLOR_GRIS,
                bg=COLOR_FONDO,
            ).pack(pady=24)
        for cita in citas:
            tarjeta = tk.Frame(
                contenido,
                bg=COLOR_PANEL,
                highlightbackground=COLOR_PANEL_CLARO,
                highlightthickness=1,
                padx=22,
                pady=18,
            )
            tarjeta.pack(fill="x", pady=6, padx=4)
            tk.Label(
                tarjeta,
                text=f"{cita.fecha}   ·   {cita.hora}",
                font=("Arial", 16, "bold"),
                fg=COLOR_ROJO_CLARO,
                bg=COLOR_PANEL,
            ).pack(anchor="w")
            tk.Label(
                tarjeta,
                text=(
                    f"Paciente: {cita.paciente.nombre}   ·   "
                    f"Motivo: {cita.motivo}   ·   Estado: {cita.estado}"
                ),
                font=("Arial", 12),
                fg=COLOR_TEXTO,
                bg=COLOR_PANEL,
                wraplength=900,
                justify="left",
            ).pack(anchor="w", pady=(5, 8))
            acciones = tk.Frame(tarjeta, bg=COLOR_PANEL)
            acciones.pack(anchor="w")
            if self._derivada_a_actual(cita):
                self._boton(
                    acciones,
                    "Registrar veredicto final",
                    lambda item=cita: self.editar_atencion(item),
                ).pack(side="left", padx=(0, 6))
            elif (
                cita.profesional.codigo_profesional
                == profesional.codigo_profesional
                and cita.estado in {"Pendiente", "Reprogramada", "En proceso"}
            ):
                self._boton(
                    acciones,
                    "Registrar opinión",
                    lambda item=cita: self.editar_atencion(item),
                ).pack(side="left", padx=(0, 6))
                if cita.estado in {"Pendiente", "Reprogramada"}:
                    self._boton(
                        acciones,
                        "Reprogramar",
                        lambda item=cita: self.reprogramar(item),
                        COLOR_PANEL_CLARO,
                    ).pack(side="left", padx=6)
                    self._boton(
                        acciones,
                        "Cancelar",
                        lambda item=cita: self.cancelar(item),
                        COLOR_PANEL_CLARO,
                    ).pack(side="left", padx=6)
            else:
                atencion = self._atencion_de(cita)
                if atencion:
                    self._boton(
                        acciones,
                        "Modificar opinión médica",
                        lambda item=cita: self.editar_atencion(item),
                        COLOR_PANEL_CLARO,
                    ).pack(side="left")

            atencion = self._atencion_de(cita)
            if atencion and self._derivada_a_actual(cita):
                tk.Label(
                    tarjeta,
                    text=(
                        "Informe remitente: "
                        f"{atencion.informe_derivacion or atencion.diagnostico}"
                    ),
                    font=("Arial", 10),
                    fg=COLOR_GRIS,
                    bg=COLOR_PANEL,
                    wraplength=1050,
                    justify="left",
                ).pack(anchor="w", pady=(10, 0))

        if self._temporizador:
            try:
                self.ventana.after_cancel(self._temporizador)
            except tk.TclError:
                pass
        self._temporizador = self.ventana.after(60000, self._actualizar_si_activo)

    def _citas_para_profesional(self):
        codigo = self.profesional_actual.codigo_profesional
        atenciones = {
            atencion.cita.codigo: atencion
            for atencion in self.sistema.obtener_atenciones()
        }
        return [
            cita
            for cita in self.sistema.obtener_citas()
            if cita.profesional.codigo_profesional == codigo
            or (
                atenciones.get(cita.codigo)
                and atenciones[cita.codigo].profesional_derivado
                and atenciones[cita.codigo].profesional_derivado.codigo_profesional
                == codigo
            )
        ]

    def _derivada_a_actual(self, cita):
        atencion = self._atencion_de(cita)
        return bool(
            atencion
            and atencion.profesional_derivado
            and atencion.profesional_derivado.codigo_profesional
            == self.profesional_actual.codigo_profesional
        )

    def _derivada_a_otro(self, cita):
        atencion = self._atencion_de(cita)
        return bool(
            atencion
            and atencion.profesional_derivado
            and cita.profesional.codigo_profesional
            == self.profesional_actual.codigo_profesional
            and atencion.profesional_derivado.codigo_profesional
            != self.profesional_actual.codigo_profesional
        )

    def _tarjeta_cita_profesional(self, padre, cita, permitir_edicion=False):
        atencion = self._atencion_de(cita)
        recibida = self._derivada_a_actual(cita)
        transferida = self._derivada_a_otro(cita)
        tarjeta = tk.Frame(
            padre,
            bg=COLOR_PANEL,
            highlightbackground=COLOR_PANEL_CLARO,
            highlightthickness=1,
            padx=20,
            pady=16,
        )
        tarjeta.pack(fill="x", pady=7, padx=4)
        tk.Label(
            tarjeta,
            text=f"{cita.fecha}   ·   {cita.hora}",
            font=("Arial", 15, "bold"),
            fg=COLOR_ROJO_CLARO,
            bg=COLOR_PANEL,
        ).pack(anchor="w")
        tk.Label(
            tarjeta,
            text=(
                f"Paciente: {cita.paciente.nombre}   ·   Motivo: {cita.motivo}"
            ),
            font=("Arial", 12),
            fg=COLOR_TEXTO,
            bg=COLOR_PANEL,
            wraplength=1050,
            justify="left",
        ).pack(anchor="w", pady=(6, 4))

        estado = (
            "Derivación recibida · en espera de veredicto"
            if recibida and atencion and atencion.estado != "Finalizada"
            else f"Atención: {atencion.estado}"
            if atencion
            else f"Cita: {cita.estado}"
        )
        if transferida and atencion:
            estado = f"Derivada a {atencion.profesional_derivado.nombre} · {atencion.estado}"
        tk.Label(
            tarjeta,
            text=estado,
            font=("Arial", 10, "bold"),
            fg=COLOR_ROJO if recibida or transferida else COLOR_GRIS,
            bg=COLOR_PANEL,
        ).pack(anchor="w", pady=(0, 6))

        if atencion and atencion.informe_derivacion:
            tk.Label(
                tarjeta,
                text=f"Informe remitente: {atencion.informe_derivacion}",
                font=("Arial", 10),
                fg=COLOR_GRIS,
                bg=COLOR_PANEL,
                wraplength=1050,
                justify="left",
            ).pack(anchor="w", pady=(2, 4))
        if (
            atencion
            and not transferida
            and atencion.diagnostico != atencion.informe_derivacion
        ):
            tk.Label(
                tarjeta,
                text=f"Veredicto / diagnóstico: {atencion.diagnostico}",
                font=("Arial", 11),
                fg=COLOR_TEXTO,
                bg=COLOR_PANEL,
                wraplength=1050,
                justify="left",
            ).pack(anchor="w", pady=(2, 6))

        if (
            permitir_edicion
            and not transferida
            and cita.estado in {"Pendiente", "Reprogramada", "En proceso"}
            and not (atencion and atencion.estado == "Finalizada")
        ):
            acciones = tk.Frame(tarjeta, bg=COLOR_PANEL)
            acciones.pack(anchor="w", pady=(8, 0))
            if recibida:
                self._boton(
                    acciones,
                    "Registrar veredicto final",
                    lambda item=cita: self.editar_atencion(item),
                ).pack(side="left")
            elif cita.profesional.codigo_profesional == self.profesional_actual.codigo_profesional:
                self._boton(
                    acciones,
                    "Registrar opinión",
                    lambda item=cita: self.editar_atencion(item),
                ).pack(side="left", padx=(0, 7))
                if cita.estado in {"Pendiente", "Reprogramada"}:
                    self._boton(
                        acciones,
                        "Reprogramar",
                        lambda item=cita: self.reprogramar(item),
                        COLOR_PANEL,
                    ).pack(side="left", padx=4)
                    self._boton(
                        acciones,
                        "Cancelar",
                        lambda item=cita: self.cancelar(item),
                        COLOR_PANEL,
                    ).pack(side="left", padx=4)

    def mostrar_atenciones_hoy(self):
        self._pantalla_en_edicion = False
        self._vista_actual = "hoy"
        self.sistema.actualizar_citas_vencidas()
        hoy = date.today().strftime("%d/%m/%Y")
        contenido = self._marco_base(
            "Atenciones de hoy",
            f"Agenda y atenciones del {hoy} · {self.profesional_actual.nombre}",
            volver=self.mostrar_agenda,
        )
        citas = sorted(
            [
                cita for cita in self._citas_para_profesional()
                if cita.fecha == hoy and not self._derivada_a_otro(cita)
            ],
            key=lambda cita: cita.fecha_hora,
        )
        if not citas:
            tk.Label(
                contenido,
                text="No tienes atenciones registradas para hoy.",
                font=FUENTE_SUBTITULO,
                fg=COLOR_GRIS,
                bg=COLOR_FONDO,
            ).pack(anchor="w", pady=20)
        for cita in citas:
            self._tarjeta_cita_profesional(contenido, cita, permitir_edicion=True)

    def mostrar_historial(self):
        self._pantalla_en_edicion = False
        self._vista_actual = "historial"
        self.sistema.actualizar_citas_vencidas()
        contenido = self._marco_base(
            "Historial y derivaciones",
            "",
            volver=self.mostrar_agenda,
        )
        citas = []
        for cita in self._citas_para_profesional():
            atencion = self._atencion_de(cita)
            if (
                self._derivada_a_otro(cita)
                or (atencion and atencion.estado == "Finalizada")
                or cita.estado in {"Atendida", "No atendida", "Cancelada"}
            ):
                citas.append(cita)
        citas.sort(key=lambda cita: cita.fecha_hora, reverse=True)
        if not citas:
            tk.Label(
                contenido,
                text="Todavía no hay atenciones en el historial.",
                font=FUENTE_SUBTITULO,
                fg=COLOR_GRIS,
                bg=COLOR_FONDO,
            ).pack(anchor="w", pady=20)
        for cita in citas:
            self._tarjeta_cita_profesional(contenido, cita)

    def _actualizar_si_activo(self):
        if self.profesional_actual is not None:
            try:
                vencidas = self.sistema.actualizar_citas_vencidas()
                if vencidas and not self._pantalla_en_edicion:
                    if self._vista_actual == "hoy":
                        self.mostrar_atenciones_hoy()
                    elif self._vista_actual == "historial":
                        self.mostrar_historial()
                    else:
                        self.mostrar_agenda()
                self._temporizador = self.ventana.after(
                    60000,
                    self._actualizar_si_activo,
                )
            except tk.TclError:
                pass

    @staticmethod
    def _enlazar_rueda(canvas, contenedor):
        def desplazar(evento):
            resultado = desplazar_por_evento(canvas, evento)
            return "break" if resultado else None

        def enlazar(widget):
            try:
                for secuencia in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                    widget.bind(secuencia, desplazar, add="+")
                for hijo in widget.winfo_children():
                    enlazar(hijo)
            except tk.TclError:
                pass

        enlazar(canvas)
        enlazar(contenedor)

    def _atencion_de(self, cita):
        return next(
            (
                atencion
                for atencion in self.sistema.obtener_atenciones()
                if atencion.cita.codigo == cita.codigo
            ),
            None,
        )

    def editar_atencion(self, cita):
        atencion = self._atencion_de(cita)
        self._pantalla_en_edicion = True
        contenido = self._marco_base(
            "Opinión médica",
            f"Atención a {cita.paciente.nombre} · {cita.fecha} {cita.hora}",
            volver=self.mostrar_agenda,
        )
        tk.Label(
            contenido,
            text=f"Atención a {cita.paciente.nombre} · {cita.fecha} {cita.hora}",
            font=FUENTE_SECCION,
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO,
        ).pack(padx=22, pady=(18, 10))
        if atencion and self._derivada_a_actual(cita):
            marco_informe = tk.Frame(contenido, bg=COLOR_PANEL, padx=14, pady=12)
            marco_informe.pack(fill="x", padx=22, pady=(0, 10))
            tk.Label(
                marco_informe,
                text="Informe del profesional remitente",
                font=("Arial", 16, "bold"),
                fg=COLOR_TEXTO,
                bg=COLOR_PANEL,
            ).pack(anchor="w")
            tk.Label(
                marco_informe,
                text=atencion.informe_derivacion or atencion.diagnostico,
                font=("Arial", 12),
                fg=COLOR_TEXTO,
                bg=COLOR_PANEL,
                wraplength=1000,
                justify="left",
            ).pack(anchor="w", pady=(4, 0))
        tk.Label(
            contenido,
            text="Opinión médica / diagnóstico:",
            font=FUENTE_BOTON,
            fg=COLOR_GRIS_CLARO,
            bg=COLOR_FONDO,
        ).pack(anchor="w", padx=22)
        texto = tk.Text(
            contenido,
            width=62,
            height=7,
            wrap="word",
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            relief="flat",
        )
        texto.pack(fill="x", padx=22, pady=8)
        if atencion and not self._derivada_a_actual(cita):
            texto.insert("1.0", atencion.diagnostico)

        es_medico_general = (
            self.profesional_actual.especialidad.strip().casefold()
            == "medicina general"
        )
        opciones_derivacion = {}
        derivacion_var = None
        if es_medico_general:
            panel_derivacion = tk.Frame(contenido, bg=COLOR_PANEL, padx=14, pady=12)
            panel_derivacion.pack(fill="x", padx=22, pady=(4, 10))
            tk.Label(
                panel_derivacion,
                text="Derivar a",
                font=("Arial", 16, "bold"),
                fg=COLOR_TEXTO,
                bg=COLOR_PANEL,
            ).pack(anchor="w")
            especialistas = [
                profesional
                for profesional in self.sistema.obtener_personal()
                if profesional.codigo_profesional
                != self.profesional_actual.codigo_profesional
                and "enfermer" not in profesional.especialidad.casefold()
                and profesional.especialidad.strip().casefold()
                != "medicina general"
            ]
            etiqueta_vacia = "-- Selecciona el profesional derivado --"
            opciones_derivacion[etiqueta_vacia] = None
            for profesional in especialistas:
                etiqueta = (
                    f"{profesional.codigo_profesional} · {profesional.nombre} · "
                    f"{profesional.especialidad}"
                )
                opciones_derivacion[etiqueta] = profesional

            if atencion and atencion.profesional_derivado:
                profesional_guardado = atencion.profesional_derivado
                etiqueta_guardada = (
                    f"{profesional_guardado.codigo_profesional} · "
                    f"{profesional_guardado.nombre} · "
                    f"{profesional_guardado.especialidad}"
                )
                opciones_derivacion[etiqueta_guardada] = profesional_guardado
                valor_inicial = etiqueta_guardada
            else:
                valor_inicial = etiqueta_vacia

            derivacion_var = tk.StringVar(value=valor_inicial)
            menu_derivacion = tk.OptionMenu(
                panel_derivacion,
                derivacion_var,
                *opciones_derivacion,
            )
            menu_derivacion.configure(
                bg=COLOR_PANEL_CLARO,
                fg=COLOR_TEXTO,
                relief="flat",
            )
            menu_derivacion.pack(anchor="w")
            if not especialistas:
                tk.Label(
                    panel_derivacion,
                    text="No hay profesionales disponibles para derivación.",
                    font=("Arial", 9),
                    fg=COLOR_ROJO,
                    bg=COLOR_PANEL,
                ).pack(anchor="w", pady=(5, 0))

        panel_recetas = tk.Frame(contenido, bg=COLOR_PANEL, padx=14, pady=12)
        panel_recetas.pack(fill="x", padx=22, pady=(4, 10))
        tk.Label(
            panel_recetas,
            text="Medicamentos recetados",
            font=FUENTE_SECCION,
            fg=COLOR_TEXTO,
            bg=COLOR_PANEL,
        ).pack(anchor="w")
        encabezados = tk.Frame(panel_recetas, bg=COLOR_PANEL)
        encabezados.pack(fill="x")
        for columna, (titulo, peso) in enumerate((("Medicamento", 3), ("Días", 1), ("Cada cuánto", 2))):
            encabezados.columnconfigure(columna, weight=peso)
            tk.Label(
                encabezados,
                text=titulo,
                font=FUENTE_BOTON,
                fg=COLOR_GRIS_CLARO,
                bg=COLOR_PANEL,
            ).grid(row=0, column=columna, sticky="w", padx=3)

        filas_recetas = []
        contenedor_filas = tk.Frame(panel_recetas, bg=COLOR_PANEL)
        contenedor_filas.pack(fill="x")

        def agregar_fila_receta(medicamento="", dias="", cada_cuanto=""):
            fila = tk.Frame(contenedor_filas, bg=COLOR_PANEL)
            fila.pack(fill="x", pady=3)
            campos = []
            for columna, (valor, peso) in enumerate(((medicamento, 3), (dias, 1), (cada_cuanto, 2))):
                entrada = tk.Entry(
                    fila,
                    font=FUENTE_BOTON,
                    bg=COLOR_PANEL_CLARO,
                    fg=COLOR_TEXTO,
                    insertbackground=COLOR_TEXTO,
                    relief="flat",
                )
                entrada.grid(row=0, column=columna, sticky="ew", padx=3, ipady=6)
                fila.columnconfigure(columna, weight=peso)
                if valor:
                    entrada.insert(0, str(valor))
                campos.append(entrada)
            def quitar():
                fila.destroy()
                filas_recetas.remove(campos)
            tk.Button(
                fila,
                text="Quitar",
                command=quitar,
                font=FUENTE_BOTON,
                bg=COLOR_PANEL_CLARO,
                fg=COLOR_TEXTO,
                relief="flat",
                bd=0,
                cursor="hand2",
                padx=8,
            ).grid(row=0, column=3, padx=(4, 0))
            filas_recetas.append(campos)

        if atencion and atencion.recetas:
            for receta in atencion.recetas:
                agregar_fila_receta(receta.medicamento, receta.dias, receta.cada_cuanto)
        else:
            agregar_fila_receta()

        self._boton(
            panel_recetas,
            "+ Agregar medicamento",
            agregar_fila_receta,
            COLOR_PANEL_CLARO,
        ).pack(anchor="w", pady=(8, 0))

        def leer_recetas():
            recetas = []
            for medicamento, dias, cada_cuanto in filas_recetas:
                valores = (medicamento.get().strip(), dias.get().strip(), cada_cuanto.get().strip())
                if not any(valores):
                    continue
                recetas.append(MedicamentoRecetado(*valores))
            return recetas

        def guardar():
            try:
                diagnostico = validar_diagnostico(texto.get("1.0", "end-1c"))
                recetas = leer_recetas()
                profesional_derivado = None
                if es_medico_general:
                    profesional_derivado = opciones_derivacion.get(
                        derivacion_var.get()
                    )
                    if profesional_derivado is None:
                        raise ValueError(
                            "Selecciona al especialista al que se derivará al paciente."
                        )
                if atencion:
                    self.sistema.actualizar_atencion(
                        atencion.codigo,
                        diagnostico,
                        recetas,
                        profesional_derivado,
                        profesional_autor=self.profesional_actual,
                    )
                else:
                    atencion_nueva = AtencionMedica(
                        self.sistema.generar_codigo_atencion(),
                        cita,
                        diagnostico,
                        "En proceso" if profesional_derivado else "Finalizada",
                        recetas,
                        profesional_derivado,
                    )
                    self.sistema.registrar_atencion(atencion_nueva)
                messagebox.showinfo(
                    "Atención guardada",
                    (
                        "El informe y la derivación se guardaron. La atención sigue "
                        "en proceso en la agenda del profesional derivado."
                        if profesional_derivado
                        else "La opinión médica y las recetas se guardaron; "
                        "la cita quedó marcada como atendida."
                    ),
                    parent=self.ventana,
                )
                self.mostrar_agenda()
            except (TypeError, ValueError) as error:
                messagebox.showerror("No se pudo guardar", str(error), parent=self.ventana)

        self._boton(contenido, "Guardar opinión y receta", guardar).pack(pady=(0, 18))

    def marcar_no_atendida(self, cita):
        if not messagebox.askyesno(
            "Confirmar estado",
            f"¿Marcar como no atendida la cita de {cita.paciente.nombre}?",
        ):
            return
        try:
            self.sistema.actualizar_estado_cita(cita.codigo, "No atendida")
            self.mostrar_agenda()
        except ValueError as error:
            messagebox.showerror("No se pudo actualizar", str(error))

    def cancelar(self, cita):
        if not messagebox.askyesno(
            "Cancelar cita",
            f"¿Cancelar la cita de {cita.paciente.nombre} del {cita.fecha} a las {cita.hora}?",
        ):
            return
        try:
            self.sistema.cancelar_cita(cita.codigo)
            self.mostrar_agenda()
        except ValueError as error:
            messagebox.showerror("No se pudo cancelar", str(error))

    def reprogramar(self, cita):
        self._pantalla_en_edicion = True
        contenido = self._marco_base(
            "Reprogramar cita",
            f"Nueva fecha y horario · {cita.paciente.nombre}",
            volver=self.mostrar_agenda,
        )
        tk.Label(
            contenido,
            text=f"Nueva fecha y horario · {cita.paciente.nombre}",
            font=FUENTE_SECCION,
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO,
        ).pack(padx=20, pady=(18, 10))
        tk.Label(contenido, text="Fecha (DD/MM/AAAA):", bg=COLOR_FONDO, fg=COLOR_GRIS_CLARO).pack()
        entrada_fecha = tk.Entry(contenido, width=18, justify="center")
        entrada_fecha.pack(pady=(4, 10), ipady=5)
        configurar_mascara_fecha(entrada_fecha)
        tk.Label(
            contenido,
            text="Horarios disponibles (se actualizan al salir de la fecha):",
            bg=COLOR_FONDO,
            fg=COLOR_GRIS_CLARO,
        ).pack(pady=(0, 5))
        hora_var = tk.StringVar(value="")
        opcion = tk.OptionMenu(contenido, hora_var, "")
        opcion.configure(bg=COLOR_PANEL_CLARO, fg=COLOR_TEXTO, relief="flat")
        opcion.pack(pady=(0, 12))

        def actualizar_horarios(event=None):
            try:
                horas = self.sistema.horarios_disponibles(
                    cita.profesional.codigo_profesional,
                    entrada_fecha.get(),
                    excluir_codigo=cita.codigo,
                )
            except ValueError:
                horas = []
            menu = opcion["menu"]
            menu.delete(0, "end")
            if horas:
                for hora in horas:
                    menu.add_command(
                        label=hora,
                        command=lambda valor=hora: hora_var.set(valor),
                    )
                hora_var.set(horas[0])
            else:
                menu.add_command(label="Sin horarios disponibles", command=lambda: None)
                hora_var.set("")

        entrada_fecha.bind("<FocusOut>", actualizar_horarios)
        entrada_fecha.bind("<Return>", actualizar_horarios)

        def guardar():
            try:
                if not hora_var.get():
                    raise ValueError("Selecciona un horario disponible.")
                self.sistema.reprogramar_cita(
                    cita.codigo,
                    entrada_fecha.get(),
                    hora_var.get(),
                )
                self.mostrar_agenda()
            except ValueError as error:
                messagebox.showerror("No se pudo reprogramar", str(error), parent=self.ventana)

        self._boton(contenido, "Guardar nueva fecha", guardar).pack(pady=(0, 18))

    def volver_a_inicio(self):
        if self._temporizador:
            try:
                self.ventana.after_cancel(self._temporizador)
            except tk.TclError:
                pass
        try:
            self.sistema.cerrar()
        except Exception:
            pass
        self.profesional_actual = None
        self.pantalla_inicio.mostrar()

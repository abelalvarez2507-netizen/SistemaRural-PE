import tkinter as tk
from tkinter import messagebox

from modelos.atencion_medica import AtencionMedica
from servicios.sistema_salud import SistemaSalud
from servicios.validaciones import validar_diagnostico

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
from interfaz.navegacion import VistaDesplazable, instalar_navegacion


class PantallaProfesional:
    """Portal de agenda y registro de atenciones del profesional."""

    def __init__(self, ventana, pantalla_inicio):
        self.ventana = ventana
        self.pantalla_inicio = pantalla_inicio
        self.sistema = SistemaSalud()
        self.profesional_actual = None
        self._temporizador = None
        self.ventana.title("SaluPro - Portal del Profesional")
        self.ventana.configure(bg=COLOR_FONDO)
        self.mostrar_acceso()

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

    def _marco_base(self, titulo, subtitulo=None):
        self._limpiar()
        vista = VistaDesplazable(self.ventana, COLOR_FONDO)
        vista.pack(fill="both", expand=True)
        contenedor = vista.contenido
        contenedor.configure(padx=32, pady=22)
        instalar_navegacion(
            self.ventana,
            volver=self.volver_a_inicio,
            inicio=self.volver_a_inicio,
        )
        barra = tk.Frame(contenedor, bg=COLOR_FONDO)
        barra.pack(fill="x", pady=(0, 18))
        self._boton(
            barra,
            "← Volver al inicio",
            self.volver_a_inicio,
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
            "Ingresa tu código profesional o tu DNI de 8 dígitos.",
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
        return len(valor) <= 10 and all(
            caracter.isalnum() or caracter in "-_" for caracter in valor
        )

    def autenticar(self):
        valor = self.entrada_identificacion.get().strip()
        if not valor:
            messagebox.showwarning("Dato requerido", "Ingresa tu código o DNI.")
            return
        if valor.isdigit() and len(valor) == 8:
            profesionales = self.sistema.buscar_personal_por_dni(valor)
        elif self._validar_identificacion(valor) and 2 <= len(valor) <= 10:
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
        profesional = self.profesional_actual
        self.sistema.actualizar_citas_vencidas()
        contenedor = self._marco_base(
            "Agenda profesional",
            f"{profesional.nombre} · {profesional.especialidad} · Código {profesional.codigo_profesional}",
        )
        citas = sorted(
            [
                cita
                for cita in self.sistema.obtener_citas()
                if cita.profesional.codigo_profesional
                == profesional.codigo_profesional
            ],
            key=lambda cita: cita.fecha_hora,
        )
        pendientes = [
            cita
            for cita in citas
            if cita.estado in {"Pendiente", "Reprogramada"}
        ]
        tk.Label(
            contenedor,
            text=f"Citas pendientes: {len(pendientes)}",
            font=FUENTE_SECCION,
            fg=COLOR_ROJO_CLARO,
            bg=COLOR_FONDO,
        ).pack(anchor="w", pady=(6, 12))

        agenda = tk.Frame(contenedor, bg=COLOR_FONDO)
        agenda.pack(fill="both", expand=True)
        canvas = tk.Canvas(
            agenda,
            bg=COLOR_FONDO,
            highlightthickness=0,
            yscrollincrement=20,
        )
        barra = tk.Scrollbar(agenda, orient="vertical", command=canvas.yview)
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
                text="No tienes citas registradas.",
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
                padx=16,
                pady=12,
            )
            tarjeta.pack(fill="x", pady=6, padx=4)
            tk.Label(
                tarjeta,
                text=f"{cita.fecha}   ·   {cita.hora}",
                font=FUENTE_SECCION,
                fg=COLOR_ROJO_CLARO,
                bg=COLOR_PANEL,
            ).pack(anchor="w")
            tk.Label(
                tarjeta,
                text=(
                    f"Paciente: {cita.paciente.nombre}   ·   "
                    f"Motivo: {cita.motivo}   ·   Estado: {cita.estado}"
                ),
                font=FUENTE_BOTON,
                fg=COLOR_TEXTO,
                bg=COLOR_PANEL,
                wraplength=900,
                justify="left",
            ).pack(anchor="w", pady=(5, 8))
            acciones = tk.Frame(tarjeta, bg=COLOR_PANEL)
            acciones.pack(anchor="w")
            if cita.estado in {"Pendiente", "Reprogramada"}:
                self._boton(
                    acciones,
                    "Registrar / editar opinión médica",
                    lambda item=cita: self.editar_atencion(item),
                ).pack(side="left", padx=(0, 6))
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
                self._boton(
                    acciones,
                    "No atendida",
                    lambda item=cita: self.marcar_no_atendida(item),
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

        tk.Label(
            contenedor,
            text="Agenda por fecha y horario. Los turnos duran 30 minutos, de 08:00 a 17:00.",
            font=("Arial", 9),
            fg=COLOR_GRIS,
            bg=COLOR_FONDO,
        ).pack(anchor="w", pady=(8, 0))
        if self._temporizador:
            try:
                self.ventana.after_cancel(self._temporizador)
            except tk.TclError:
                pass
        self._temporizador = self.ventana.after(60000, self._actualizar_si_activo)

    def _actualizar_si_activo(self):
        if self.profesional_actual is not None:
            try:
                vencidas = self.sistema.actualizar_citas_vencidas()
                if vencidas:
                    self.mostrar_agenda()
                else:
                    self._temporizador = self.ventana.after(
                        60000,
                        self._actualizar_si_activo,
                    )
            except tk.TclError:
                pass

    @staticmethod
    def _enlazar_rueda(canvas, contenedor):
        delta_acumulado = [0]

        def desplazar(evento):
            delta = getattr(evento, "delta", 0)
            if delta:
                delta_acumulado[0] += delta
                unidades = int(delta_acumulado[0] / 120)
                if unidades:
                    canvas.yview_scroll(-unidades, "units")
                    delta_acumulado[0] -= unidades * 120
                return "break"
            if getattr(evento, "num", None) == 4:
                canvas.yview_scroll(-1, "units")
                return "break"
            if getattr(evento, "num", None) == 5:
                canvas.yview_scroll(1, "units")
                return "break"
            return None

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
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Opinión médica")
        ventana.configure(bg=COLOR_FONDO)
        ventana.geometry("720x560")
        ventana.minsize(600, 420)
        ventana.transient(self.ventana)
        ventana.grab_set()
        vista = VistaDesplazable(ventana, COLOR_FONDO)
        vista.pack(fill="both", expand=True)
        contenido = vista.contenido
        tk.Label(
            contenido,
            text=f"Atención a {cita.paciente.nombre} · {cita.fecha} {cita.hora}",
            font=FUENTE_SECCION,
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO,
        ).pack(padx=22, pady=(18, 10))
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
            height=10,
            wrap="word",
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            relief="flat",
        )
        texto.pack(fill="both", expand=True, padx=22, pady=8)
        if atencion:
            texto.insert("1.0", atencion.diagnostico)

        def guardar():
            try:
                diagnostico = validar_diagnostico(texto.get("1.0", "end-1c"))
                if atencion:
                    self.sistema.actualizar_atencion(atencion.codigo, diagnostico)
                else:
                    atencion_nueva = AtencionMedica(
                        self.sistema.generar_codigo_atencion(),
                        cita,
                        diagnostico,
                        "Finalizada",
                    )
                    self.sistema.registrar_atencion(atencion_nueva)
                messagebox.showinfo(
                    "Atención guardada",
                    "La opinión médica se guardó y la cita quedó marcada como atendida.",
                    parent=ventana,
                )
                ventana.destroy()
                self.mostrar_agenda()
            except (TypeError, ValueError) as error:
                messagebox.showerror("No se pudo guardar", str(error), parent=ventana)

        self._boton(
            contenido,
            "← Volver",
            ventana.destroy,
            COLOR_PANEL,
        ).pack(pady=(4, 6))
        self._boton(contenido, "Guardar opinión", guardar).pack(pady=(0, 18))

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
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Reprogramar cita")
        ventana.configure(bg=COLOR_FONDO)
        ventana.geometry("560x500")
        ventana.minsize(480, 400)
        ventana.transient(self.ventana)
        ventana.grab_set()
        vista = VistaDesplazable(ventana, COLOR_FONDO)
        vista.pack(fill="both", expand=True)
        contenido = vista.contenido
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
                ventana.destroy()
                self.mostrar_agenda()
            except ValueError as error:
                messagebox.showerror("No se pudo reprogramar", str(error), parent=ventana)

        self._boton(
            contenido,
            "← Volver",
            ventana.destroy,
            COLOR_PANEL,
        ).pack(pady=(2, 6))
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

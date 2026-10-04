import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from modelos.paciente import Paciente
from modelos.personal_salud import PersonalSalud
from modelos.personal_enfermeria import PersonalEnfermeria
from modelos.cita import Cita
from modelos.atencion_medica import AtencionMedica
from modelos.medicamento_recetado import MedicamentoRecetado

from servicios.sistema_salud import SistemaSalud
from servicios.reportes import Reportes
from servicios.validaciones import (
    validar_dni as validar_dni_valor,
    validar_dni_en_edicion,
    validar_nombre_en_edicion,
)
from interfaz.campos import configurar_mascara_fecha

from interfaz.estilos import (
    COLOR_FONDO,
    COLOR_FONDO_SECUNDARIO,
    COLOR_PANEL,
    COLOR_PANEL_CLARO,
    COLOR_ROJO,
    COLOR_ROJO_CLARO,
    COLOR_ROJO_OSCURO,
    COLOR_BLANCO,
    COLOR_ERROR,
    COLOR_TEXTO,
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
from interfaz.navegacion import VistaDesplazable, instalar_navegacion


class PantallaInterna(tk.Frame):
    """Frame que reemplaza una Toplevel sin abrir una ventana nueva.

    Conserva los métodos más usados por el código original (title, geometry,
    minsize, transient, register) y hace que destroy() regrese a la pantalla
    anterior en lugar de cerrar la aplicación.
    """

    def __init__(self, master, volver_callback=None, titulo="SaluPro"):
        super().__init__(
            master,
            bg=COLOR_FONDO
        )

        self._root = master
        self._volver_callback = volver_callback
        self._titulo = titulo
        self._cerrando = False
        self._vista = VistaDesplazable(self, COLOR_FONDO)
        self._vista.pack(fill="both", expand=True)

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
        """Destruye la pantalla sin ejecutar el callback de regreso."""

        self._cerrando = True

        try:
            tk.Frame.destroy(self)
        except tk.TclError:
            pass

    def destroy(self):
        """Destruye la pantalla y regresa a la pantalla anterior."""

        if self._cerrando:
            return

        callback = self._volver_callback

        self._cerrando = True

        try:
            tk.Frame.destroy(self)
        except tk.TclError:
            pass
        finally:
            if callback is not None:
                callback()


class ContenidoPantallaInterna(tk.Frame):
    """Contenido desplazable que conserva el regreso de su pantalla padre."""

    def __init__(self, pantalla):
        self._pantalla = pantalla
        super().__init__(pantalla._vista.contenido, bg=COLOR_FONDO)
        self.pack(fill="both", expand=True, padx=24, pady=(18, 24))

    def title(self, titulo=None):
        return self._pantalla.title(titulo)

    def geometry(self, *args, **kwargs):
        return self._pantalla.geometry(*args, **kwargs)

    def minsize(self, *args, **kwargs):
        return self._pantalla.minsize(*args, **kwargs)

    def transient(self, *args, **kwargs):
        return self._pantalla.transient(*args, **kwargs)

    def register(self, *args, **kwargs):
        return self._pantalla.register(*args, **kwargs)

    def cerrar_sin_volver(self):
        self._pantalla.cerrar_sin_volver()

    def destroy(self):
        if self._pantalla._cerrando:
            tk.Frame.destroy(self)
        else:
            self._pantalla.destroy()


class VentanaPrincipal:

    def __init__(
        self,
        ventana,
        pantalla_inicio=None,
        sesion=None,
    ):

        if sesion is None or sesion.rol != "administrativa":
            raise ValueError("Se requiere una sesión administrativa autenticada.")

        self.ventana = ventana
        self.pantalla_inicio = pantalla_inicio
        self.sesion = sesion

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
            720,
            560
        )

        self.ventana.resizable(
            True,
            True
        )

        try:
            self.ventana.state(
                "zoomed"
            )
        except tk.TclError:
            pass

        self.ventana.bind(
            "<F11>",
            self._alternar_pantalla_completa
        )

        self.ventana.configure(
            bg=COLOR_FONDO
        )

        # =====================================================
        # APARIENCIA GENERAL DE TKINTER
        # =====================================================

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
            COLOR_TEXTO
        )

        self.ventana.option_add(
            "*Entry.Background",
            COLOR_PANEL_CLARO
        )

        self.ventana.option_add(
            "*Entry.Foreground",
            COLOR_TEXTO
        )

        self.ventana.option_add(
            "*Entry.InsertBackground",
            COLOR_TEXTO
        )

        self.ventana.option_add(
            "*Text.Background",
            COLOR_PANEL_CLARO
        )

        self.ventana.option_add(
            "*Text.Foreground",
            COLOR_TEXTO
        )

        self.ventana.option_add(
            "*Text.InsertBackground",
            COLOR_TEXTO
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
            COLOR_TEXTO
        )

        self.ventana.option_add(
            "*OptionMenu.ActiveBackground",
            COLOR_ROJO
        )

        self.ventana.option_add(
            "*OptionMenu.ActiveForeground",
            COLOR_BLANCO
        )

        # =====================================================
        # SERVICIOS
        # =====================================================

        self.sistema = SistemaSalud()

        self.reportes = Reportes(
            self.sistema
        )

        self.crear_interfaz()
        self._vencimiento_after = self.ventana.after(
            60000,
            self._revisar_citas_vencidas,
        )

    def _revisar_citas_vencidas(self):
        try:
            vencidas = self.sistema.actualizar_citas_vencidas()
            if vencidas and self._pantalla_actual is self._pantalla_principal:
                self.crear_interfaz()
            self._vencimiento_after = self.ventana.after(
                60000,
                self._revisar_citas_vencidas,
            )
        except tk.TclError:
            self._vencimiento_after = None

    # =========================================================
    # INTERFAZ PRINCIPAL
    # =========================================================

    def crear_interfaz(self):
        """Construye el panel administrativo principal de SaluPro."""

        self.sistema.actualizar_citas_vencidas()
        instalar_navegacion(
            self.ventana,
            volver=self.volver_a_inicio,
            inicio=self.volver_a_inicio,
        )

        # Siempre que se muestre el panel administrativo,
        # ocupa toda la ventana.
        for widget in self.ventana.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

        self._pantalla_principal = None
        self._pantalla_actual = None
        self._callback_volver_actual = (
            self.volver_panel_principal
        )

        # =====================================================
        # CONTENEDOR CON SCROLL
        # =====================================================

        contenedor = VistaDesplazable(
            self.ventana,
            COLOR_FONDO,
        )

        contenedor.pack(
            fill="both",
            expand=True
        )

        self._pantalla_principal = contenedor
        self._pantalla_actual = contenedor

        contenido = contenedor.contenido

        # =====================================================
        # INTERIOR
        # =====================================================

        interior = tk.Frame(
            contenido,
            bg=COLOR_FONDO
        )

        interior.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=22
        )

        # =====================================================
        # DATOS DEL SISTEMA
        # =====================================================

        pacientes = self.sistema.obtener_pacientes()
        personal = self.sistema.obtener_personal()
        citas = self.sistema.obtener_citas()
        atenciones = self.sistema.obtener_atenciones()

        pendientes = [
            cita
            for cita in citas
            if cita.estado == "Pendiente"
        ]

        reprogramar = [
            cita
            for cita in citas
            if cita.estado == "Reprogramada"
        ]

        citas_atendidas = [
            cita
            for cita in citas
            if cita.estado == "Atendida"
        ]

        finalizadas = [
            atencion
            for atencion in atenciones
            if atencion.estado == "Finalizada"
        ]

        atenciones_proceso = [
            atencion
            for atencion in atenciones
            if atencion.estado == "En proceso"
        ]

        def obtener_fecha_cita(cita):
            return cita.fecha_hora

        # =====================================================
        # PRÓXIMAS CITAS
        # =====================================================

        hoy = datetime.now()

        proximas = [
            cita
            for cita in citas
            if cita.estado in {"Pendiente", "Reprogramada"}
            and obtener_fecha_cita(cita) >= hoy
        ]

        proximas = sorted(
            proximas,
            key=obtener_fecha_cita
        )

        # =====================================================
        # ENCABEZADO / NAVEGACIÓN
        # =====================================================

        encabezado = tk.Frame(
            interior,
            bg=COLOR_FONDO
        )

        encabezado.pack(
            fill="x",
            pady=(0, 10)
        )

        izquierda = tk.Frame(
            encabezado,
            bg=COLOR_FONDO
        )

        izquierda.pack(
            side="left"
        )

        tk.Label(
            izquierda,
            text="SALUPRO",
            font=FUENTE_LOGO,
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO
        ).pack(
            side="left"
        )

        tk.Label(
            izquierda,
            text=f"  |  PANEL ADMINISTRATIVO · {self.sesion.usuario}",
            font=FUENTE_NORMAL_BOLD,
            bg=COLOR_FONDO,
            fg=COLOR_GRIS_CLARO
        ).pack(
            side="left",
            pady=7
        )

        acciones = tk.Frame(
            encabezado,
            bg=COLOR_FONDO
        )

        acciones.pack(
            side="right"
        )

        boton_inicio = tk.Button(
            acciones,
            text="←  Volver",
            command=self.volver_a_inicio,
            font=FUENTE_BOTON,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            activebackground=COLOR_ROJO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=13,
            pady=8
        )

        boton_inicio.pack(
            side="left",
            padx=(0, 8)
        )

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

        boton_actualizar.pack(
            side="left"
        )

        for boton, color in (
            (
                boton_inicio,
                COLOR_PANEL_CLARO
            ),
            (
                boton_actualizar,
                COLOR_ROJO
            ),
        ):
            boton.bind(
                "<Enter>",
                lambda evento,
                b=boton,
                c=COLOR_ROJO_CLARO:
                b.configure(bg=c, fg=COLOR_BLANCO)
            )

            boton.bind(
                "<Leave>",
                lambda evento,
                b=boton,
                c=color:
                b.configure(
                    bg=c,
                    fg=(
                        COLOR_BLANCO
                        if c == COLOR_ROJO
                        else COLOR_TEXTO
                    ),
                )
            )

        tk.Frame(
            interior,
            bg=COLOR_ROJO,
            height=3
        ).pack(
            fill="x",
            pady=(0, 18)
        )

        # =====================================================
        # TÍTULO PRINCIPAL
        # =====================================================

        titulo_fila = tk.Frame(
            interior,
            bg=COLOR_FONDO
        )

        titulo_fila.pack(
            fill="x",
            pady=(0, 15)
        )

        titulo_info = tk.Frame(
            titulo_fila,
            bg=COLOR_FONDO
        )

        titulo_info.pack(
            side="left",
            fill="x",
            expand=True
        )

        tk.Label(
            titulo_info,
            text="Gestión integral de salud",
            font=FUENTE_TITULO,
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO
        ).pack(
            anchor="w"
        )

        tk.Label(
            titulo_info,
            text=(
                "Todo el centro de salud en un solo lugar: "
                "pacientes, profesionales, citas, atenciones y reportes."
            ),
            font=FUENTE_SUBTITULO,
            bg=COLOR_FONDO,
            fg=COLOR_GRIS
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        # =====================================================
        # BÚSQUEDA RÁPIDA
        # =====================================================

        tarjeta_busqueda = tk.Frame(
            interior,
            bg=COLOR_PANEL,
            highlightbackground=COLOR_PANEL_CLARO,
            highlightthickness=1,
        )

        tarjeta_busqueda.pack(
            fill="x",
            pady=(0, 15),
        )

        cabecera_busqueda = tk.Frame(
            tarjeta_busqueda,
            bg=COLOR_PANEL,
        )

        cabecera_busqueda.pack(
            fill="x",
            padx=14,
            pady=(10, 2),
        )

        tk.Label(
            cabecera_busqueda,
            text="🔎",
            font=("Arial", 16, "bold"),
            bg=COLOR_PANEL,
            fg=COLOR_ROJO,
        ).pack(side="left")

        instrucciones_busqueda = tk.Frame(
            cabecera_busqueda,
            bg=COLOR_PANEL,
        )

        instrucciones_busqueda.pack(
            side="left",
            padx=(9, 0),
        )

        tk.Label(
            instrucciones_busqueda,
            text="BÚSQUEDA RÁPIDA",
            font=FUENTE_NORMAL_BOLD,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
        ).pack(anchor="w")

        tk.Label(
            instrucciones_busqueda,
            text="Código de paciente, profesional o enfermería, o DNI de 8 dígitos.",
            font=FUENTE_PEQUENA,
            bg=COLOR_PANEL,
            fg=COLOR_GRIS,
        ).pack(anchor="w")

        fila_busqueda_rapida = tk.Frame(
            tarjeta_busqueda,
            bg=COLOR_PANEL,
        )

        fila_busqueda_rapida.pack(
            fill="x",
            padx=14,
            pady=(6, 12),
        )

        fila_busqueda_rapida.columnconfigure(0, weight=1)

        valor_busqueda_rapida = tk.StringVar(
            master=self.ventana,
        )

        entrada_busqueda_rapida = tk.Entry(
            fila_busqueda_rapida,
            textvariable=valor_busqueda_rapida,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            relief="flat",
            bd=0,
            font=FUENTE_NORMAL,
        )

        entrada_busqueda_rapida.grid(
            row=0,
            column=0,
            sticky="ew",
            ipady=9,
            padx=(0, 10),
        )

        self.configurar_limite_busqueda(
            entrada_busqueda_rapida,
            self.ventana,
            maximo=None,
        )

        mensaje_busqueda = tk.Label(
            interior,
            text="",
            font=FUENTE_PEQUENA,
            bg=COLOR_FONDO,
            fg=COLOR_ERROR,
            anchor="w",
        )

        def mostrar_mensaje_busqueda(mensaje):
            mensaje_busqueda.configure(text=mensaje)
            if not mensaje_busqueda.winfo_manager():
                mensaje_busqueda.pack(
                    fill="x",
                    padx=14,
                    pady=(0, 12),
                    after=tarjeta_busqueda,
                )

        def limpiar_mensaje_busqueda(*_args):
            mensaje_busqueda.configure(text="")
            if mensaje_busqueda.winfo_manager():
                mensaje_busqueda.pack_forget()

        def presentar_resultado_busqueda(contenido):
            pantalla_resultado = self._crear_pantalla_interna(
                "Resultado de búsqueda rápida"
            )

            tk.Label(
                pantalla_resultado,
                text="RESULTADO DE BÚSQUEDA",
                font=FUENTE_TITULO,
                bg=COLOR_FONDO,
                fg=COLOR_TEXTO,
            ).pack(
                anchor="w",
                padx=24,
                pady=(20, 10),
            )

            marco_resultado = tk.Frame(
                pantalla_resultado,
                bg=COLOR_PANEL,
                highlightbackground=COLOR_PANEL_CLARO,
                highlightthickness=1,
            )

            marco_resultado.pack(
                fill="both",
                expand=True,
                padx=24,
                pady=(0, 24),
            )

            texto_resultado = tk.Text(
                marco_resultado,
                height=24,
                wrap="word",
                bg=COLOR_PANEL,
                fg=COLOR_TEXTO,
                insertbackground=COLOR_TEXTO,
                relief="flat",
                bd=0,
                padx=14,
                pady=12,
                font=FUENTE_NORMAL,
            )

            barra_resultado = tk.Scrollbar(
                marco_resultado,
                orient="vertical",
                command=texto_resultado.yview,
            )

            texto_resultado.configure(
                yscrollcommand=barra_resultado.set,
            )
            texto_resultado.pack(
                side="left",
                fill="both",
                expand=True,
            )
            barra_resultado.pack(
                side="right",
                fill="y",
            )
            texto_resultado.insert(tk.END, contenido)
            texto_resultado.configure(state="disabled")
            texto_resultado.see("1.0")

        def buscar_rapido(evento=None):
            valor = entrada_busqueda_rapida.get().strip()

            if len(valor) < 2:
                return "break"

            if not self.validar_entrada_busqueda(valor):
                mostrar_mensaje_busqueda(
                    "Usa únicamente letras, números, guion o guion bajo."
                )
                return "break"

            limpiar_mensaje_busqueda()

            try:
                pacientes_encontrados = (
                    self.sistema.buscar_paciente_por_codigo(valor)
                )
                profesionales_encontrados = (
                    self.sistema.buscar_personal_por_codigo(valor)
                )

                if valor.isdigit() and len(valor) == 8:
                    dni = self.validar_dni(valor)
                    pacientes_por_dni = self.sistema.buscar_paciente_por_dni(dni)
                    profesionales_por_dni = (
                        self.sistema.buscar_personal_por_dni(dni)
                    )
                    pacientes_encontrados.extend(
                        paciente
                        for paciente in pacientes_por_dni
                        if all(
                            existente.codigo != paciente.codigo
                            for existente in pacientes_encontrados
                        )
                    )
                    profesionales_encontrados.extend(
                        profesional
                        for profesional in profesionales_por_dni
                        if all(
                            existente.codigo_profesional
                            != profesional.codigo_profesional
                            for existente in profesionales_encontrados
                        )
                    )
            except (ValueError, TypeError) as error:
                mostrar_mensaje_busqueda(str(error))
                return "break"

            citas = self.sistema.obtener_citas()
            atenciones = self.sistema.obtener_atenciones()
            atenciones_por_cita = {
                atencion.cita.codigo: atencion
                for atencion in atenciones
            }
            bloques = []

            for paciente in pacientes_encontrados:
                citas_paciente = sorted(
                    (
                        cita
                        for cita in citas
                        if cita.paciente.codigo == paciente.codigo
                    ),
                    key=lambda cita: cita.fecha_hora,
                    reverse=True,
                )
                ventas_paciente = self.sistema.obtener_historial_paciente(
                    paciente.codigo
                ).get("ventas_medicamentos", [])

                bloques.extend((
                    "FICHA DEL PACIENTE",
                    f"Código: {paciente.codigo}",
                    f"DNI: {paciente.dni_mascarado}",
                    f"Nombre: {paciente.nombre}",
                    f"Edad: {paciente.edad} años",
                    "",
                    "CITAS Y ATENCIONES",
                ))

                if not citas_paciente:
                    bloques.append("No tiene citas registradas.")

                for cita in citas_paciente:
                    bloques.extend((
                        "",
                        f"Cita {cita.codigo} · {cita.fecha} {cita.hora}",
                        f"Motivo: {cita.motivo}",
                        f"Estado de la cita: {cita.estado}",
                        (
                            f"Profesional asignado: {cita.profesional.nombre} "
                            f"({cita.profesional.codigo_profesional})"
                        ),
                        f"Especialidad: {cita.profesional.especialidad}",
                    ))

                    atencion = atenciones_por_cita.get(cita.codigo)
                    if atencion is None:
                        bloques.append("Atención: todavía no registrada.")
                    else:
                        bloques.extend((
                            f"Código de atención: {atencion.codigo}",
                            (
                                f"Atendido por: {atencion.profesional.nombre} "
                                f"({atencion.profesional.codigo_profesional})"
                            ),
                            f"Diagnóstico: {atencion.diagnostico}",
                            f"Estado de la atención: {atencion.estado}",
                        ))
                        if atencion.recetas:
                            bloques.append("Medicamentos recetados:")
                            bloques.extend(
                                f"  • {receta.mostrar_informacion()}"
                                for receta in atencion.recetas
                            )

                bloques.append("MEDICAMENTOS REGISTRADOS EN VENTA")
                if not ventas_paciente:
                    bloques.append("No hay ventas de medicamentos vinculadas.")
                else:
                    for venta in ventas_paciente:
                        (_id, medicamento, lote, cantidad, _precio, total, codigo, vendedor, fecha_hora) = venta
                        bloques.append(
                            f"{fecha_hora} · {medicamento} · Lote {lote} · "
                            f"{cantidad} unidad(es) · S/ {float(total):.2f} · Paciente {codigo}"
                        )

                bloques.extend((
                    "",
                    f"Resumen: {len(citas_paciente)} cita(s), "
                    f"{sum(cita.codigo in atenciones_por_cita for cita in citas_paciente)} "
                    "atención(es).",
                    "",
                ))

            for profesional in profesionales_encontrados:
                citas_profesional = sorted(
                    (
                        cita
                        for cita in citas
                        if (
                            cita.profesional.codigo_profesional
                            == profesional.codigo_profesional
                        )
                    ),
                    key=lambda cita: cita.fecha_hora,
                    reverse=True,
                )

                bloques.extend((
                    "FICHA DEL PROFESIONAL",
                    f"Código profesional: {profesional.codigo_profesional}",
                    f"DNI: {profesional.dni_mascarado}",
                    f"Nombre: {profesional.nombre}",
                    f"Edad: {profesional.edad} años",
                    f"Especialidad: {profesional.especialidad}",
                    "",
                    "PACIENTES, CITAS Y ATENCIONES",
                ))

                if not citas_profesional:
                    bloques.append("No tiene citas registradas.")

                for cita in citas_profesional:
                    bloques.extend((
                        "",
                        f"Paciente: {cita.paciente.nombre}",
                        f"Código de paciente: {cita.paciente.codigo}",
                        f"DNI: {cita.paciente.dni_mascarado}",
                        f"Edad: {cita.paciente.edad} años",
                        f"Cita {cita.codigo} · {cita.fecha} {cita.hora}",
                        f"Motivo: {cita.motivo}",
                        f"Estado de la cita: {cita.estado}",
                    ))

                    atencion = atenciones_por_cita.get(cita.codigo)
                    if atencion is None:
                        bloques.append("Atención: todavía no registrada.")
                    else:
                        bloques.extend((
                            (
                                f"Atendido por: {atencion.profesional.nombre} "
                                f"({atencion.profesional.codigo_profesional})"
                            ),
                            f"Diagnóstico: {atencion.diagnostico}",
                            f"Estado de la atención: {atencion.estado}",
                        ))

                bloques.extend((
                    "",
                    f"Resumen: {len(citas_profesional)} cita(s), "
                    f"{sum(cita.codigo in atenciones_por_cita for cita in citas_profesional)} "
                    "atención(es).",
                    "",
                ))

            if not bloques:
                mostrar_mensaje_busqueda(
                    "No se encontró un paciente ni profesional con ese "
                    "código o DNI."
                )
            else:
                presentar_resultado_busqueda("\n".join(bloques).strip())

            return "break"

        boton_buscar_rapido = tk.Button(
            fila_busqueda_rapida,
            text="Buscar",
            command=buscar_rapido,
            font=FUENTE_BOTON,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_GRIS,
            disabledforeground=COLOR_GRIS,
            state=tk.DISABLED,
            activebackground=COLOR_ROJO_CLARO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=22,
            pady=8,
        )

        boton_buscar_rapido.grid(
            row=0,
            column=1,
            sticky="e",
        )

        def actualizar_estado_busqueda(*_args):
            valor = valor_busqueda_rapida.get().strip()
            habilitado = (
                len(valor) >= 2
                and self.validar_entrada_busqueda(valor)
            )
            boton_buscar_rapido.configure(
                state=(tk.NORMAL if habilitado else tk.DISABLED),
                bg=(COLOR_ROJO if habilitado else COLOR_PANEL_CLARO),
                fg=(COLOR_BLANCO if habilitado else COLOR_GRIS),
            )
            limpiar_mensaje_busqueda()

        valor_busqueda_rapida.trace_add(
            "write",
            actualizar_estado_busqueda,
        )

        def resaltar_boton_buscar(_evento):
            if boton_buscar_rapido["state"] != tk.DISABLED:
                boton_buscar_rapido.configure(bg=COLOR_ROJO_CLARO)

        def restaurar_boton_buscar(_evento):
            habilitado = boton_buscar_rapido["state"] != tk.DISABLED
            boton_buscar_rapido.configure(
                bg=(COLOR_ROJO if habilitado else COLOR_PANEL_CLARO),
            )

        boton_buscar_rapido.bind(
            "<Enter>",
            resaltar_boton_buscar,
        )
        boton_buscar_rapido.bind(
            "<Leave>",
            restaurar_boton_buscar,
        )
        entrada_busqueda_rapida.bind("<Return>", buscar_rapido)
        entrada_busqueda_rapida.focus_set()

        # =====================================================
        # TARJETAS DE RESUMEN
        # =====================================================

        tk.Label(
            interior,
            text="RESUMEN DEL CENTRO",
            font=FUENTE_SECCION,
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO
        ).pack(
            anchor="w",
            pady=(0, 6)
        )

        resumen = tk.Frame(
            interior,
            bg=COLOR_FONDO
        )

        resumen.pack(
            fill="x",
            pady=(0, 15)
        )

        for columna in range(2):
            resumen.columnconfigure(
                columna,
                weight=1,
                uniform="resumen"
            )

        datos_resumen = [
            (
                "👥",
                "TOTAL DE PACIENTES",
                len(pacientes),
                "registrados"
            ),
            (
                "⚕",
                "TOTAL DE PROFESIONALES",
                len(personal),
                "registrados"
            ),
            (
                "📅",
                "CITAS PENDIENTES",
                len(pendientes),
                "por atender"
            ),
            (
                "🔄",
                "CITAS REPROGRAMADAS",
                len(reprogramar),
                "requieren seguimiento"
            ),
            (
                "🩺",
                "TOTAL DE ATENCIONES",
                len(atenciones),
                f"{len(finalizadas)} finalizadas"
            ),
            (
                "🕐",
                "PRÓXIMAS CITAS",
                len(proximas),
                "en la agenda"
            ),
        ]

        for indice, (
            icono,
            titulo,
            valor,
            detalle
        ) in enumerate(
            datos_resumen
        ):

            fila = indice // 2
            columna = indice % 2

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

            cabecera = tk.Frame(
                tarjeta,
                bg=COLOR_PANEL
            )

            cabecera.pack(
                fill="x",
                padx=14,
                pady=(11, 0)
            )

            tk.Label(
                cabecera,
                text=icono,
                font=("Arial", 19, "bold"),
                bg=COLOR_PANEL,
                fg=COLOR_ROJO
            ).pack(
                side="left"
            )

            tk.Label(
                cabecera,
                text=titulo,
                font=FUENTE_PEQUENA,
                bg=COLOR_PANEL,
                fg=COLOR_GRIS_CLARO,
                wraplength=210,
                justify="left"
            ).pack(
                side="left",
                padx=8
            )

            tk.Label(
                tarjeta,
                text=str(valor),
                font=("Arial", 25, "bold"),
                bg=COLOR_PANEL,
                fg=COLOR_TEXTO
            ).pack(
                anchor="w",
                padx=14,
                pady=(2, 0)
            )

            tk.Label(
                tarjeta,
                text=detalle,
                font=FUENTE_PEQUENA,
                bg=COLOR_PANEL,
                fg=COLOR_GRIS
            ).pack(
                anchor="w",
                padx=14,
                pady=(0, 11)
            )

        # =====================================================
        # AGENDA + ESTADO GENERAL
        # =====================================================

        centro = tk.Frame(
            interior,
            bg=COLOR_FONDO
        )

        centro.pack(
            fill="x",
            pady=(0, 16)
        )

        centro.columnconfigure(
            0,
            weight=3,
            uniform="centro"
        )

        centro.columnconfigure(
            1,
            weight=2,
            uniform="centro"
        )

        panel_citas = tk.Frame(
            centro,
            bg=COLOR_PANEL,
            highlightbackground=COLOR_PANEL_CLARO,
            highlightthickness=1
        )

        panel_citas.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 5)
        )

        tk.Label(
            panel_citas,
            text="PRÓXIMAS CITAS",
            font=FUENTE_SECCION,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO
        ).pack(
            anchor="w",
            padx=16,
            pady=(13, 2)
        )

        tk.Label(
            panel_citas,
            text="Vista rápida de la agenda registrada.",
            font=FUENTE_PEQUENA,
            bg=COLOR_PANEL,
            fg=COLOR_GRIS
        ).pack(
            anchor="w",
            padx=16,
            pady=(0, 9)
        )

        lista_citas = tk.Frame(
            panel_citas,
            bg=COLOR_PANEL
        )

        lista_citas.pack(
            fill="x",
            padx=16,
            pady=(0, 13)
        )

        if proximas:

            for cita in proximas[:6]:

                fila_cita = tk.Frame(
                    lista_citas,
                    bg=COLOR_PANEL_CLARO
                )

                fila_cita.pack(
                    fill="x",
                    pady=2
                )

                tk.Label(
                    fila_cita,
                    text=f"{cita.fecha} · {cita.hora}",
                    font=FUENTE_NORMAL_BOLD,
                    bg=COLOR_PANEL_CLARO,
                    fg=COLOR_ROJO_CLARO,
                    width=13,
                    anchor="w"
                ).pack(
                    side="left",
                    padx=10,
                    pady=7
                )

                nombre_paciente = getattr(
                    getattr(
                        cita,
                        "paciente",
                        None
                    ),
                    "nombre",
                    "Paciente"
                )

                nombre_profesional = getattr(
                    getattr(
                        cita,
                        "profesional",
                        None
                    ),
                    "nombre",
                    "Profesional"
                )

                datos = tk.Frame(
                    fila_cita,
                    bg=COLOR_PANEL_CLARO
                )

                datos.pack(
                    side="left",
                    fill="x",
                    expand=True,
                    padx=4,
                    pady=5
                )

                tk.Label(
                    datos,
                    text=str(nombre_paciente),
                    font=FUENTE_NORMAL_BOLD,
                    bg=COLOR_PANEL_CLARO,
                    fg=COLOR_TEXTO,
                    anchor="w"
                ).pack(
                    anchor="w"
                )

                tk.Label(
                    datos,
                    text=str(nombre_profesional),
                    font=FUENTE_PEQUENA,
                    bg=COLOR_PANEL_CLARO,
                    fg=COLOR_GRIS_CLARO,
                    anchor="w"
                ).pack(
                    anchor="w"
                )

                tk.Label(
                    fila_cita,
                    text=str(cita.estado),
                    font=FUENTE_PEQUENA,
                    bg=COLOR_PANEL_CLARO,
                    fg=COLOR_GRIS_CLARO,
                    width=14
                ).pack(
                    side="right",
                    padx=10
                )

        else:

            tk.Label(
                lista_citas,
                text="No hay citas futuras registradas.",
                font=FUENTE_NORMAL,
                bg=COLOR_PANEL,
                fg=COLOR_GRIS
            ).pack(
                anchor="w",
                pady=10
            )

        panel_estado = tk.Frame(
            centro,
            bg=COLOR_PANEL,
            highlightbackground=COLOR_PANEL_CLARO,
            highlightthickness=1
        )

        panel_estado.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(5, 0)
        )

        tk.Label(
            panel_estado,
            text="📊 ESTADO DEL CENTRO",
            font=FUENTE_SECCION,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO
        ).pack(
            anchor="w",
            padx=16,
            pady=(13, 10)
        )

        estado_resumen = [
            (
                "Pacientes registrados",
                len(pacientes)
            ),
            (
                "Profesionales registrados",
                sum(not self._es_personal_enfermeria(p) for p in personal)
            ),
            (
                "Personal de enfermería",
                sum(self._es_personal_enfermeria(p) for p in personal)
            ),
            (
                "Citas registradas",
                len(citas)
            ),
            (
                "Citas pendientes",
                len(pendientes)
            ),
            (
                "Citas atendidas",
                len(citas_atendidas)
            ),
            (
                "Citas reprogramadas",
                len(reprogramar)
            ),
                (
                    "Citas no atendidas",
                    sum(cita.estado == "No atendida" for cita in citas)
                ),
                (
                    "Citas canceladas",
                    sum(cita.estado == "Cancelada" for cita in citas)
                ),
            (
                "Atenciones en proceso",
                len(atenciones_proceso)
            ),
            (
                "Atenciones finalizadas",
                len(finalizadas)
            ),
        ]

        for nombre, cantidad in estado_resumen:

            fila_estado = tk.Frame(
                panel_estado,
                bg=COLOR_PANEL
            )

            fila_estado.pack(
                fill="x",
                padx=16,
                pady=3
            )

            tk.Label(
                fila_estado,
                text=nombre,
                font=FUENTE_PEQUENA,
                bg=COLOR_PANEL,
                fg=COLOR_GRIS_CLARO
            ).pack(
                side="left"
            )

            tk.Label(
                fila_estado,
                text=str(cantidad),
                font=FUENTE_NORMAL_BOLD,
                bg=COLOR_PANEL,
                fg=COLOR_TEXTO
            ).pack(
                side="right"
            )

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
        ).pack(
            anchor="w",
            padx=16,
            pady=(9, 13)
        )

        # =====================================================
        # MÓDULOS PRINCIPALES
        # =====================================================

        tk.Label(
            interior,
            text="MÓDULOS DEL SISTEMA",
            font=FUENTE_SECCION,
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO
        ).pack(
            anchor="w",
            pady=(0, 6)
        )

        zona = tk.Frame(
            interior,
            bg=COLOR_FONDO
        )

        zona.pack(
            fill="x",
            pady=(0, 12)
        )

        for columna in range(3):
            zona.columnconfigure(
                columna,
                weight=1,
                uniform="modulos"
            )

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

            superior = tk.Frame(
                tarjeta,
                bg=COLOR_PANEL
            )

            superior.pack(
                fill="x",
                padx=16,
                pady=(15, 5)
            )

            tk.Label(
                superior,
                text=icono,
                font=("Arial", 22, "bold"),
                bg=COLOR_PANEL,
                fg=COLOR_ROJO
            ).pack(
                side="left"
            )

            tk.Label(
                superior,
                text=titulo,
                font=FUENTE_SECCION,
                bg=COLOR_PANEL,
                fg=COLOR_TEXTO,
                wraplength=235,
                justify="left"
            ).pack(
                side="left",
                padx=9
            )

            tk.Label(
                tarjeta,
                text=descripcion,
                font=FUENTE_PEQUENA,
                bg=COLOR_PANEL,
                fg=COLOR_GRIS,
                wraplength=290,
                justify="left"
            ).pack(
                anchor="w",
                padx=16,
                pady=(0, 10)
            )

            estadistica = tk.Frame(
                tarjeta,
                bg=COLOR_PANEL_CLARO
            )

            estadistica.pack(
                fill="x",
                padx=16,
                pady=(0, 12)
            )

            tk.Label(
                estadistica,
                text=str(cantidad),
                font=("Arial", 17, "bold"),
                bg=COLOR_PANEL_CLARO,
                fg=COLOR_TEXTO
            ).pack(
                side="left",
                padx=10,
                pady=7
            )

            tk.Label(
                estadistica,
                text=detalle,
                font=FUENTE_PEQUENA,
                bg=COLOR_PANEL_CLARO,
                fg=COLOR_GRIS_CLARO
            ).pack(
                side="left",
                padx=(0, 8)
            )

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

            boton.pack(
                anchor="center",
                pady=(0, 15),
                ipadx=5
            )

            boton.bind(
                "<Enter>",
                lambda evento,
                b=boton:
                b.configure(
                    bg=COLOR_ROJO_CLARO
                )
            )

            boton.bind(
                "<Leave>",
                lambda evento,
                b=boton:
                b.configure(
                    bg=COLOR_ROJO
                )
            )

        crear_modulo(
            0,
            0,
            "👥",
            "GESTIÓN DE PACIENTES",
            (
                "Registre pacientes, consulte sus datos "
                "y revise su historial clínico."
            ),
            len(pacientes),
            "pacientes registrados",
            "Gestionar pacientes",
            self.gestion_pacientes
        )

        crear_modulo(
            0,
            1,
            "⚕",
            "GESTIÓN DE PROFESIONALES",
            (
                "Administre el personal de salud "
                "y consulte la actividad registrada."
            ),
            sum(not self._es_personal_enfermeria(p) for p in personal),
            "profesionales registrados",
            "Gestionar profesionales",
            self.gestion_profesionales
        )

        crear_modulo(
            1,
            0,
            "📅",
            "GESTIÓN DE CITAS",
            (
                "Administre la agenda, los estados "
                "y las citas que requieren seguimiento."
            ),
            len(citas),
            "citas en agenda",
            "Gestionar citas",
            self.gestion_citas
        )

        crear_modulo(
            0,
            2,
            "♧",
            "GESTIÓN DE ENFERMERÍA",
            "Registre, consulte y busque personal de enfermería.",
            sum(self._es_personal_enfermeria(p) for p in personal),
            "personas registradas",
            "Gestionar enfermería",
            self.gestion_enfermeria
        )

        crear_modulo(
            1,
            1,
            "🩺",
            "ATENCIONES MÉDICAS",
            (
                "Registre diagnósticos, consulte atenciones "
                "y actualice sus estados."
            ),
            len(atenciones),
            "atenciones registradas",
            "Gestionar atenciones",
            self.gestion_atenciones
        )

        crear_modulo(
            1,
            2,
            "📊",
            "REPORTES Y ESTADÍSTICAS",
            (
                "Consulte indicadores generales y reportes "
                "de pacientes, citas y atenciones."
            ),
            len(finalizadas),
            "atenciones finalizadas",
            "Ver reportes",
            self.gestion_reportes
        )

        # =====================================================
        # PIE DEL PANEL
        # =====================================================

        pie = tk.Frame(
            interior,
            bg=COLOR_FONDO
        )

        pie.pack(
            fill="x",
            pady=(5, 8)
        )

        tk.Frame(
            pie,
            bg=COLOR_PANEL_CLARO,
            height=1
        ).pack(
            fill="x",
            pady=(0, 9)
        )

        tk.Label(
            pie,
            text=(
                "SaluPro • Sistema de Salud Rural • "
                "Panel administrativo"
            ),
            font=FUENTE_PEQUENA,
            bg=COLOR_FONDO,
            fg=COLOR_GRIS_OSCURO
        ).pack(
            side="left"
        )

    # =========================================================
    # PANTALLA COMPLETA
    # =========================================================

    def _alternar_pantalla_completa(
        self,
        evento=None
    ):

        try:

            actual = bool(
                self.ventana.attributes(
                    "-fullscreen"
                )
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

    # =========================================================
    # VOLVER AL PANEL
    # =========================================================

    def volver_panel_principal(self):
        """Regresa al panel administrativo dentro de la misma ventana."""

        actual = self._pantalla_actual

        if (
            actual is not None
            and actual is not self._pantalla_principal
        ):

            try:

                if isinstance(actual, VistaDesplazable):
                    actual.destroy()
                else:
                    if hasattr(actual, "_cerrando"):
                        actual._cerrando = True
                    tk.Frame.destroy(actual)

            except (
                tk.TclError,
                AttributeError
            ):
                pass

        if self._pantalla_principal is not None:

            try:

                self._pantalla_principal.pack(
                    fill="both",
                    expand=True
                )

                self._pantalla_principal.lift()

            except tk.TclError:
                pass

        self._pantalla_actual = (
            self._pantalla_principal
        )

        self._callback_volver_actual = (
            self.volver_panel_principal
        )
        instalar_navegacion(
            self.ventana,
            volver=self.volver_panel_principal,
            inicio=self.volver_a_inicio,
        )

    # =========================================================
    # VOLVER A INICIO
    # =========================================================

    def volver_a_inicio(self):
        """Reemplaza la pantalla administrativa por la pantalla de inicio."""

        if self._vencimiento_after:
            try:
                self.ventana.after_cancel(self._vencimiento_after)
            except tk.TclError:
                pass
            self._vencimiento_after = None

        try:
            self.sistema.cerrar()
        except Exception:
            pass

        if self.pantalla_inicio is not None:

            actual = self._pantalla_actual
            if actual is not None and actual is not self._pantalla_principal:
                try:
                    if hasattr(actual, "cerrar_sin_volver"):
                        actual.cerrar_sin_volver()
                    else:
                        actual.destroy()
                except (tk.TclError, AttributeError):
                    pass

            self._pantalla_actual = None
            self._pantalla_principal = None
            self._callback_volver_actual = None

            self.pantalla_inicio.mostrar()

            return

        from interfaz.pantalla_inicio import PantallaInicio

        PantallaInicio(
            self.ventana
        ).mostrar()

    # =========================================================
    # LIMPIAR PANTALLA ACTUAL
    # =========================================================

    def _limpiar_pantalla_actual(self):
        """Elimina la pantalla actual de forma segura."""

        actual = self._pantalla_actual

        if actual is None:
            return

        try:

            if actual is self._pantalla_principal:

                actual.pack_forget()

            else:

                if hasattr(
                    actual,
                    "cerrar_sin_volver"
                ):

                    actual.cerrar_sin_volver()

                else:
                    actual.destroy()

        except (
            tk.TclError,
            AttributeError
        ):
            pass

        finally:
            self._pantalla_actual = None

    # =========================================================
    # CREAR PANTALLA INTERNA
    # =========================================================

    def _crear_pantalla_interna(
        self,
        titulo="SaluPro"
    ):
        """Crea una pantalla dentro de la misma ventana principal."""

        callback = (
            self._callback_volver_actual
            or self.volver_panel_principal
        )

        self._limpiar_pantalla_actual()

        ventana = PantallaInterna(
            self.ventana,
            volver_callback=callback,
            titulo=titulo
        )

        ventana.pack(
            fill="both",
            expand=True
        )

        self._pantalla_actual = ventana
        contenido = ContenidoPantallaInterna(ventana)
        instalar_navegacion(
            self.ventana,
            volver=contenido.destroy,
            inicio=self.volver_a_inicio,
        )

        barra = tk.Frame(
            contenido,
            bg=COLOR_FONDO
        )

        barra.pack(
            fill="x",
            padx=24,
            pady=(18, 0)
        )

        boton_volver = tk.Button(
            barra,
            text="←  Volver",
            command=ventana.destroy,
            font=FUENTE_BOTON,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            activebackground=COLOR_ROJO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=13,
            pady=8
        )

        boton_volver.pack(
            side="left"
        )

        boton_volver.bind(
            "<Enter>",
            lambda evento:
            boton_volver.configure(
                bg=COLOR_ROJO_CLARO,
                fg=COLOR_BLANCO,
            )
        )

        boton_volver.bind(
            "<Leave>",
            lambda evento:
            boton_volver.configure(
                bg=COLOR_PANEL_CLARO,
                fg=COLOR_TEXTO,
            )
        )

        return contenido

    # =========================================================
    # ABRIR DESDE MENÚ
    # =========================================================

    def _abrir_desde_menu(
        self,
        comando,
        volver_callback
    ):
        """Ejecuta una opción de menú conservando el destino de Volver."""

        self._callback_volver_actual = (
            volver_callback
        )

        comando()

    # =========================================================
    # MENÚ DE GESTIÓN
    # =========================================================

    def _crear_menu_gestion(
        self,
        titulo,
        descripcion,
        opciones,
        ancho=500,
        alto=500
    ):
        """Muestra el menú de gestión dentro de la misma ventana principal."""

        self._callback_volver_actual = (
            self.volver_panel_principal
        )
        instalar_navegacion(
            self.ventana,
            volver=self.volver_panel_principal,
            inicio=self.volver_a_inicio,
        )

        self._limpiar_pantalla_actual()

        vista = VistaDesplazable(
            self.ventana,
            COLOR_FONDO,
        )
        vista.pack(fill="both", expand=True)
        ventana = vista.contenido
        self._pantalla_actual = vista

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
            fg=COLOR_TEXTO,
            activebackground=COLOR_ROJO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=7
        )

        boton_panel.pack(
            side="left"
        )

        boton_panel.bind(
            "<Enter>",
            lambda evento:
            boton_panel.configure(
                bg=COLOR_ROJO_CLARO,
                fg=COLOR_BLANCO,
            )
        )

        boton_panel.bind(
            "<Leave>",
            lambda evento:
            boton_panel.configure(
                bg=COLOR_PANEL_CLARO,
                fg=COLOR_TEXTO,
            )
        )

        tk.Label(
            contenedor,
            text=titulo.upper(),
            font=FUENTE_TITULO,
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO
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

        def ejecutar_opcion(
            comando
        ):

            # Al entrar a un submódulo,
            # Volver reconstruye exactamente este menú.
            callback_menu = (
                lambda:
                self._crear_menu_gestion(
                    titulo,
                    descripcion,
                    opciones,
                    ancho,
                    alto
                )
            )

            self._abrir_desde_menu(
                comando,
                callback_menu
            )

        for texto_boton, comando in opciones:

            boton = tk.Button(
                contenedor,
                text=texto_boton,
                command=lambda c=comando:
                ejecutar_opcion(c),
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
                lambda evento,
                b=boton:
                b.configure(
                    bg=COLOR_ROJO_CLARO
                )
            )

            boton.bind(
                "<Leave>",
                lambda evento,
                b=boton:
                b.configure(
                    bg=COLOR_ROJO
                )
            )

        return ventana

    @staticmethod
    def _es_personal_enfermeria(personal):
        return "enfermer" in str(getattr(personal, "especialidad", "")).casefold()

    # =========================================================
    # GESTIÓN DE PACIENTES
    # =========================================================

    def gestion_pacientes(self):
        """Agrupa todas las funciones relacionadas con pacientes."""

        self._crear_menu_gestion(
            "Gestión de pacientes",
            (
                "Administre los pacientes registrados "
                "y consulte su historial."
            ),
            [
                (
                    "Registrar paciente",
                    self.registrar_paciente
                ),
                (
                    "Ver pacientes",
                    self.ver_pacientes
                ),
                (
                    "Buscar paciente",
                    self.buscar_paciente
                ),
                (
                    "Historial de pacientes",
                    self.historial_pacientes
                ),
            ],
            ancho=520,
            alto=520
        )

    # =========================================================
    # GESTIÓN DE PROFESIONALES
    # =========================================================

    def gestion_profesionales(self):
        """Agrupa todas las funciones relacionadas con profesionales."""

        self._crear_menu_gestion(
            "Gestión de profesionales",
            "Administre profesionales de salud y consulte su actividad registrada.",
            [
                ("Registrar profesional", self.registrar_personal),
                ("Ver profesionales", self.ver_personal),
                ("Buscar profesional", self.buscar_personal),
                ("Historial de profesionales", self.historial_profesionales),
            ],
            ancho=540,
            alto=520
        )

    def gestion_enfermeria(self):
        """Agrupa el alta, consulta y búsqueda de personal de enfermería."""
        self._crear_menu_gestion(
            "Gestión de enfermería",
            "Registre personal de enfermería y consulte sus datos registrados.",
            [
                ("Registrar personal", lambda: self.registrar_personal("enfermeria")),
                ("Ver personal", lambda: self.ver_personal("enfermeria")),
                ("Buscar personal", lambda: self.buscar_personal("enfermeria")),
            ],
            ancho=540,
            alto=460,
        )

    # =========================================================
    # GESTIÓN DE CITAS
    # =========================================================

    def gestion_citas(self):
        """Agrupa las funciones de agenda y seguimiento de citas."""

        self._crear_menu_gestion(
            "Gestión de citas",
            (
                "Registre, consulte, reprograme o cancele citas. "
                "El estado de atención se controla desde Atenciones médicas."
            ),
            [
                (
                    "Registrar cita",
                    self.registrar_cita
                ),
                (
                    "Citas pendientes",
                    self.ver_citas
                ),
                (
                    "Reprogramar cita",
                    self.reprogramar_cita
                ),
                (
                    "Cancelar cita",
                    self.cancelar_cita
                ),
                (
                    "Citas reprogramadas",
                    self.ver_citas_reprogramadas
                ),
            ],
            ancho=540,
            alto=640
        )

    # =========================================================
    # GESTIÓN DE ATENCIONES
    # =========================================================

    def gestion_atenciones(self):
        """Agrupa las funciones de atenciones médicas."""

        self._crear_menu_gestion(
            "Atenciones médicas",
            (
                "Registre y siga cada atención: Pendiente, En proceso o Finalizada. "
                "Al registrar una atención, su cita pasa a Atendida."
            ),
            [
                (
                    "Registrar atención",
                    self.registrar_atencion
                ),
                (
                    "Ver atenciones",
                    self.ver_atenciones
                ),
                (
                    "Cambiar estado",
                    self.cambiar_estado_atencion
                ),
            ],
            ancho=520,
            alto=460
        )

    # =========================================================
    # GESTIÓN DE REPORTES
    # =========================================================

    def gestion_reportes(self):
        """Agrupa estadísticas y reportes del sistema."""

        self._crear_menu_gestion(
            "Reportes y estadísticas",
            (
                "Consulte los principales indicadores "
                "y reportes generados por SaluPro."
            ),
            [
                (
                    "Ver estadísticas",
                    self.ver_estadisticas
                ),
                (
                    "Ver reportes",
                    self.ver_reportes
                ),
            ],
            ancho=520,
            alto=400
        )

    # =========================================================
    # ACTUALIZAR DASHBOARD
    # =========================================================

    def actualizar_dashboard(self):
        """Recarga el panel para mostrar los datos actuales."""

        for widget in self.ventana.winfo_children():

            try:
                widget.destroy()
            except tk.TclError:
                pass

        self._pantalla_actual = None
        self._pantalla_principal = None

        self.crear_interfaz()

    # =========================================================
    # VALIDACIÓN DNI
    # =========================================================

    def validar_dni(
        self,
        dni
    ):
        """Delega la validación del DNI a la capa común de dominio."""

        return validar_dni_valor(
            dni
        )

    # =========================================================
    # CREAR CAMPO DNI
    # =========================================================

    def crear_campo_dni(
        self,
        ventana
    ):

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

        validacion = ventana.register(
            validar_dni_en_edicion
        )

        entrada.config(
            validate="key",
            validatecommand=(
                validacion,
                "%P"
            )
        )

        return entrada

    # =========================================================
    # VALIDAR BÚSQUEDA
    # =========================================================

    def validar_entrada_busqueda(
        self,
        nuevo_valor,
        maximo=None
    ):
        """Valida entradas de búsqueda sin permitir símbolos ni exceso."""

        if nuevo_valor == "":
            return True

        return (maximo is None or len(nuevo_valor) <= maximo) and all(
            caracter.isalnum() or caracter in "-_"
            for caracter in nuevo_valor
        )

    # =========================================================
    # CONFIGURAR LÍMITE DE BÚSQUEDA
    # =========================================================

    def configurar_limite_busqueda(
        self,
        entrada,
        ventana=None,
        maximo=None
    ):
        """Configura la validación de un código o DNI de búsqueda."""

        registro = (
            ventana
            if ventana is not None
            else self.ventana
        )

        validacion = registro.register(
            lambda valor:
            self.validar_entrada_busqueda(
                valor,
                maximo
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

    # =========================================================
    # FECHA
    # =========================================================

    def crear_campo_fecha(
        self,
        ventana
    ):

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

        entrada.placeholder_texto = "DD/MM/AAAA"
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


        entrada.bind(
            "<FocusIn>",
            entrar
        )

        entrada.bind(
            "<FocusOut>",
            salir
        )

        return configurar_mascara_fecha(entrada)

    # =========================================================
    # VALIDAR FECHA
    # =========================================================

    def validar_fecha(
        self,
        fecha
    ):

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

        if fecha_convertida.date() < datetime.now().date():
            raise ValueError(
                "La fecha de la cita no puede ser anterior a hoy."
            )

        return True

    def crear_selector_horarios(
        self,
        contenedor,
        profesional_var,
        entrada_fecha,
        excluir_codigo=None,
    ):
        """Muestra debajo de la fecha los turnos libres del profesional."""
        tk.Label(
            contenedor,
            text="Horarios disponibles (turnos de 30 minutos, 07:00–18:00; último inicio 17:30):",
            font=FUENTE_NORMAL_BOLD,
        ).pack(pady=(8, 4))
        hora_var = tk.StringVar(value="")
        selector = tk.OptionMenu(contenedor, hora_var, "")
        selector.configure(cursor="hand2")
        selector.pack()

        def actualizar(event=None):
            codigo = profesional_var.get().split(" - ")[0]
            fecha = entrada_fecha.get().strip()
            if getattr(entrada_fecha, "placeholder_activo", False):
                fecha = ""
            try:
                self.validar_fecha(fecha)
                horarios = self.sistema.horarios_disponibles(
                    codigo,
                    fecha,
                    excluir_codigo=excluir_codigo,
                )
            except ValueError:
                horarios = []
            menu = selector["menu"]
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
                    label="Ingresa una fecha futura con turnos libres",
                    command=lambda: None,
                )
                hora_var.set("")

        entrada_fecha.bind("<FocusOut>", actualizar, add="+")
        entrada_fecha.bind("<Return>", actualizar, add="+")
        profesional_var.trace_add("write", lambda *_args: actualizar())
        return hora_var, actualizar

    # =========================================================
    # GENERAR CÓDIGO PROFESIONAL
    # =========================================================

    def generar_codigo_profesional(self):
        return self.sistema.generar_codigo_personal("CMP")

    def generar_codigo_enfermeria(self):
        return self.sistema.generar_codigo_personal("MTF")

    # =========================================================
    # VER PACIENTES
    # =========================================================

    def ver_pacientes(self):

        ventana = self._crear_pantalla_interna(
            "Pacientes registrados"
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

            texto.config(
                state="disabled"
            )

            return

        for paciente in pacientes:

            texto.insert(
                tk.END,
                paciente.mostrar_informacion()
                + "\n\n"
            )

        texto.config(
            state="disabled"
        )

    # =========================================================
    # REGISTRAR PACIENTE
    # =========================================================

    def registrar_paciente(self):

        ventana = self._crear_pantalla_interna(
            "Registrar paciente"
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

        validacion = ventana.register(
            validar_dni_en_edicion
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
            text="Nombres y apellidos:"
        ).pack(
            pady=5
        )

        entrada_nombre = tk.Entry(
            ventana,
            width=35
        )

        entrada_nombre.pack()
        validar_nombre = ventana.register(validar_nombre_en_edicion)
        entrada_nombre.configure(
            validate="key",
            validatecommand=(validar_nombre, "%P"),
        )

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
                    int(
                        entrada_edad.get()
                    )
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

    # =========================================================
    # BÚSQUEDA DE PERSONAS
    # =========================================================

    def _mostrar_busqueda_personas(
        self,
        titulo,
        etiqueta,
        tipo_profesional=False,
        categoria_personal="profesional",
    ):
        """Construye una búsqueda de pacientes/profesionales."""

        self._limpiar_pantalla_actual()

        vista = VistaDesplazable(
            self.ventana,
            COLOR_FONDO,
        )
        vista.pack(fill="both", expand=True)
        ventana = vista.contenido

        self._pantalla_actual = vista
        instalar_navegacion(
            self.ventana,
            volver=(
                self._callback_volver_actual
                or self.volver_panel_principal
            ),
            inicio=self.volver_a_inicio,
        )

        contenedor = tk.Frame(
            ventana,
            bg=COLOR_FONDO
        )

        contenedor.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=25
        )

        barra = tk.Frame(
            contenedor,
            bg=COLOR_FONDO
        )

        barra.pack(
            fill="x",
            pady=(0, 18)
        )

        boton_volver = tk.Button(
            barra,
            text="←  Volver",
            command=(
                self._callback_volver_actual
                or self.volver_panel_principal
            ),
            font=FUENTE_BOTON,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            activebackground=COLOR_ROJO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=14,
            pady=8
        )

        boton_volver.pack(
            side="left"
        )

        tk.Label(
            contenedor,
            text=titulo,
            font=FUENTE_TITULO,
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO
        ).pack(
            anchor="w",
            pady=(0, 4)
        )

        tk.Label(
            contenedor,
            text=etiqueta,
            font=FUENTE_NORMAL_BOLD,
            bg=COLOR_FONDO,
            fg=COLOR_GRIS_CLARO
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        tipo_var = tk.StringVar(
            value="Código"
        )

        fila_busqueda = tk.Frame(
            contenedor,
            bg=COLOR_FONDO
        )

        fila_busqueda.pack(
            fill="x",
            pady=(0, 15)
        )

        tk.OptionMenu(
            fila_busqueda,
            tipo_var,
            "Código",
            "DNI"
        ).pack(
            side="left",
            padx=(0, 10)
        )

        entrada_busqueda = tk.Entry(
            fila_busqueda,
            width=35,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            relief="flat",
            bd=0,
            font=FUENTE_NORMAL
        )

        entrada_busqueda.pack(
            side="left",
            ipady=8
        )

        self.configurar_limite_busqueda(
            entrada_busqueda,
            self.ventana
        )

        boton_buscar = tk.Button(
            fila_busqueda,
            text="🔎  Buscar",
            command=lambda:
            buscar(),
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

        boton_buscar.pack(
            side="left",
            padx=(10, 0)
        )

        resultado = tk.Text(
            contenedor,
            height=18,
            wrap="word",
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            relief="flat",
            bd=0,
            font=FUENTE_NORMAL
        )

        resultado.pack(
            fill="both",
            expand=True,
            pady=(5, 12)
        )

        def limpiar_entrada(*args):

            entrada_busqueda.delete(
                0,
                tk.END
            )

            resultado.config(
                state="normal"
            )

            resultado.delete(
                "1.0",
                tk.END
            )

            resultado.config(
                state="disabled"
            )

        tipo_var.trace_add(
            "write",
            limpiar_entrada
        )

        def buscar():

            try:

                tipo = tipo_var.get()

                valor = (
                    entrada_busqueda
                    .get()
                    .strip()
                )

                if not valor:

                    raise ValueError(
                        "Debe ingresar un valor "
                        "para realizar la búsqueda."
                    )

                if tipo_profesional:

                    if tipo == "Código":

                        registros = (
                            self.sistema
                            .buscar_personal_por_codigo(
                                valor
                            )
                        )

                    else:

                        registros = (
                            self.sistema
                            .buscar_personal_por_dni(
                                self.validar_dni(
                                    valor
                                )
                            )
                        )

                    registros = [
                        persona for persona in registros
                        if self._es_personal_enfermeria(persona)
                        == (categoria_personal == "enfermeria")
                    ]
                    mensaje_vacio = (
                        "No se encontró personal de enfermería."
                        if categoria_personal == "enfermeria"
                        else "No se encontró profesional."
                    )

                else:

                    if tipo == "Código":

                        registros = (
                            self.sistema
                            .buscar_paciente_por_codigo(
                                valor
                            )
                        )

                    else:

                        registros = (
                            self.sistema
                            .buscar_paciente_por_dni(
                                self.validar_dni(
                                    valor
                                )
                            )
                        )

                    mensaje_vacio = (
                        "No se encontraron pacientes."
                    )

                resultado.config(
                    state="normal"
                )

                resultado.delete(
                    "1.0",
                    tk.END
                )

                if not registros:

                    resultado.insert(
                        tk.END,
                        mensaje_vacio
                    )

                    resultado.config(
                        state="disabled"
                    )

                    return

                for registro in registros:

                    resultado.insert(
                        tk.END,
                        registro.mostrar_informacion()
                        + "\n\n"
                    )

                resultado.config(
                    state="disabled"
                )

            except (
                ValueError,
                TypeError
            ) as error:

                messagebox.showerror(
                    "Error",
                    str(error)
                )

        boton_buscar.configure(
            width=18
        )

        boton_buscar.bind(
            "<Enter>",
            lambda evento:
            boton_buscar.configure(
                bg=COLOR_ROJO_CLARO
            )
        )

        boton_buscar.bind(
            "<Leave>",
            lambda evento:
            boton_buscar.configure(
                bg=COLOR_ROJO
            )
        )

        entrada_busqueda.bind(
            "<Return>",
            lambda evento:
            buscar()
        )

        entrada_busqueda.focus_set()

        resultado.config(
            state="disabled"
        )

    # =========================================================
    # VER PERSONAL
    # =========================================================

    def ver_personal(self, categoria="profesional"):
        personal_es_enfermeria = categoria == "enfermeria"
        ventana = self._crear_pantalla_interna(
            "Personal de enfermería" if personal_es_enfermeria else "Profesionales registrados"
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

        personal = [
            persona for persona in self.sistema.obtener_personal()
            if self._es_personal_enfermeria(persona) == personal_es_enfermeria
        ]

        if not personal:

            texto.insert(
                tk.END,
                "No existe personal registrado."
            )

            texto.config(
                state="disabled"
            )

            return

        for profesional in personal:

            texto.insert(
                tk.END,
                profesional.mostrar_informacion()
                + "\n\n"
            )

        texto.config(
            state="disabled"
        )

    # =========================================================
    # REGISTRAR PERSONAL
    # =========================================================

    def registrar_personal(self, categoria="profesional"):
        es_enfermeria = categoria == "enfermeria"
        ventana = self._crear_pantalla_interna(
            "Registrar personal de enfermería" if es_enfermeria else "Registrar profesional"
        )

        codigo_generado = (
            self.generar_codigo_enfermeria()
            if es_enfermeria
            else self.generar_codigo_profesional()
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

        validacion = ventana.register(
            validar_dni_en_edicion
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
            text="Nombres y apellidos:"
        ).pack(
            pady=5
        )

        entrada_nombre = tk.Entry(
            ventana,
            width=35
        )

        entrada_nombre.pack()
        validar_nombre = ventana.register(validar_nombre_en_edicion)
        entrada_nombre.configure(
            validate="key",
            validatecommand=(validar_nombre, "%P"),
        )

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
            text="Área de enfermería:" if es_enfermeria else "Especialidad:",
        ).pack(
            pady=5
        )

        especialidades = [
            "Medicina General",
            "Obstetricia",
            "Odontología",
            "Psicología",
            "Nutrición",
            "Medicina Familiar",
            "Urología",
            "Pediatría",
            "Neurología",
        ]

        especialidad_var = tk.StringVar(value="Enfermería" if es_enfermeria else especialidades[0])
        if not es_enfermeria:
            tk.OptionMenu(ventana, especialidad_var, *especialidades).pack()

        def guardar():

            try:

                dni = self.validar_dni(
                    entrada_dni.get()
                )

                clase_personal = PersonalEnfermeria if es_enfermeria else PersonalSalud
                profesional = clase_personal(
                    codigo_generado,
                    dni,
                    entrada_nombre.get(),
                    int(entrada_edad.get()),
                    especialidad_var.get(),
                )

                self.sistema.registrar_personal(profesional)

                messagebox.showinfo(
                    "Éxito",
                    (
                        ("Personal de enfermería" if es_enfermeria else "Profesional")
                        + " registrado correctamente.\n\n"
                        f"Código asignado: {codigo_generado}\n"
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

    def buscar_personal(self, categoria="profesional"):
        es_enfermeria = categoria == "enfermeria"
        self._mostrar_busqueda_personas(
            titulo="Buscar personal de enfermería" if es_enfermeria else "Buscar profesional",
            etiqueta="Buscar personal por:" if es_enfermeria else "Buscar profesional por:",
            tipo_profesional=True,
            categoria_personal=categoria,
        )

    # =========================================================
    # VER CITAS PENDIENTES
    # =========================================================

    def ver_citas(self):

        ventana = self._crear_pantalla_interna(
            "Citas pendientes"
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
            .obtener_citas_pendientes()
        )

        if not citas:

            texto.insert(
                tk.END,
                "No existen citas pendientes."
            )

            texto.config(
                state="disabled"
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

        texto.config(
            state="disabled"
        )

    # =========================================================
    # CITAS PARA REPROGRAMAR
    # =========================================================

    def ver_citas_reprogramadas(self):

        ventana = self._crear_pantalla_interna(
            "Citas reprogramadas"
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
                "No existen citas reprogramadas."
            )

            texto.config(
                state="disabled"
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

        texto.config(
            state="disabled"
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

        ventana = self._crear_pantalla_interna(
            "Registrar cita"
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

        hora_var, actualizar_horarios = self.crear_selector_horarios(
            ventana,
            profesional_var,
            entrada_fecha,
        )

        tk.Button(
            ventana,
            text="Ver horarios disponibles",
            command=actualizar_horarios,
            cursor="hand2",
        ).pack(pady=(5, 8))

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

                if not hora_var.get():
                    raise ValueError(
                        "Selecciona un horario disponible para esta cita."
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
                    "Pendiente",
                    hora_var.get(),
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

    def reprogramar_cita(self):
        self.sistema.actualizar_citas_vencidas()
        citas = [
            cita
            for cita in self.sistema.obtener_citas()
            if cita.estado in {"Pendiente", "Reprogramada"}
        ]
        if not citas:
            messagebox.showinfo(
                "Reprogramar cita",
                "No hay citas pendientes que se puedan reprogramar.",
            )
            return

        ventana = self._crear_pantalla_interna("Reprogramar una cita")
        tk.Label(ventana, text="Selecciona la cita:").pack(pady=(8, 4))
        cita_var = tk.StringVar()
        opciones = [
            f"{cita.codigo} | {cita.paciente.nombre} | {cita.fecha} {cita.hora}"
            for cita in citas
        ]
        cita_var.set(opciones[0])
        tk.OptionMenu(ventana, cita_var, *opciones).pack()
        tk.Label(ventana, text="Nueva fecha:").pack(pady=(12, 2))
        entrada_fecha = self.crear_campo_fecha(ventana)

        profesional_var = tk.StringVar()
        hora_var, actualizar = self.crear_selector_horarios(
            ventana,
            profesional_var,
            entrada_fecha,
        )

        def cita_seleccionada(*_args):
            codigo = cita_var.get().split(" | ")[0]
            cita = next(item for item in citas if item.codigo == codigo)
            profesional_var.set(
                f"{cita.profesional.codigo_profesional} - {cita.profesional.nombre}"
            )

        cita_var.trace_add("write", cita_seleccionada)
        cita_seleccionada()

        tk.Button(
            ventana,
            text="Ver horarios disponibles",
            command=actualizar,
            cursor="hand2",
        ).pack(pady=(6, 10))

        def guardar():
            try:
                if entrada_fecha.placeholder_activo:
                    raise ValueError("Ingresa la nueva fecha de la cita.")
                if not hora_var.get():
                    raise ValueError("Selecciona un horario disponible.")
                codigo = cita_var.get().split(" | ")[0]
                self.sistema.reprogramar_cita(
                    codigo,
                    entrada_fecha.get(),
                    hora_var.get(),
                )
                messagebox.showinfo(
                    "Cita reprogramada",
                    "La cita se guardó con la nueva fecha y horario.",
                )
                ventana.destroy()
            except (ValueError, StopIteration) as error:
                messagebox.showerror(
                    "No se pudo reprogramar",
                    str(error),
                    parent=ventana,
                )

        tk.Button(
            ventana,
            text="Guardar nueva fecha",
            width=24,
            command=guardar,
            cursor="hand2",
        ).pack(pady=12)

    def cancelar_cita(self):
        self.sistema.actualizar_citas_vencidas()
        citas = [
            cita
            for cita in self.sistema.obtener_citas()
            if cita.estado in {"Pendiente", "Reprogramada"}
        ]
        if not citas:
            messagebox.showinfo(
                "Cancelar cita",
                "No hay citas pendientes que se puedan cancelar.",
            )
            return

        ventana = self._crear_pantalla_interna("Cancelar una cita")
        tk.Label(ventana, text="Selecciona la cita que deseas cancelar:").pack(pady=(8, 4))
        cita_var = tk.StringVar()
        opciones = [
            f"{cita.codigo} | {cita.paciente.nombre} | {cita.fecha} {cita.hora}"
            for cita in citas
        ]
        cita_var.set(opciones[0])
        tk.OptionMenu(ventana, cita_var, *opciones).pack()

        def cancelar():
            codigo = cita_var.get().split(" | ")[0]
            cita = next(item for item in citas if item.codigo == codigo)
            if not messagebox.askyesno(
                "Confirmar cancelación",
                f"¿Cancelar la cita de {cita.paciente.nombre} del {cita.fecha} a las {cita.hora}?",
                parent=ventana,
            ):
                return
            try:
                self.sistema.cancelar_cita(codigo)
                messagebox.showinfo(
                    "Cita cancelada",
                    "La cita se canceló correctamente.",
                    parent=ventana,
                )
                ventana.destroy()
            except ValueError as error:
                messagebox.showerror(
                    "No se pudo cancelar",
                    str(error),
                    parent=ventana,
                )

        tk.Button(
            ventana,
            text="Cancelar cita seleccionada",
            width=28,
            command=cancelar,
            cursor="hand2",
        ).pack(pady=18)

    # =========================================================
    # VER ATENCIONES
    # =========================================================

    def ver_atenciones(self):

        ventana = self._crear_pantalla_interna(
            "Atenciones médicas"
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

            texto.config(
                state="disabled"
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

        texto.config(
            state="disabled"
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
            and cita.estado in {"Pendiente", "Reprogramada"}
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

        ventana = self._crear_pantalla_interna(
            "Registrar atención"
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
                f"{c.fecha} {c.hora}"
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
            text="Estado de la atención:"
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

        ventana = self._crear_pantalla_interna(
            "Cambiar estado de atención"
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
            text="Nuevo estado de la atención:"
        ).pack(
            pady=15
        )

        estado_var = tk.StringVar()

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

                # Ahora el selector comienza con el estado real.
                estado_var.set(
                    atencion.estado
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

        self._callback_volver_actual = self.volver_panel_principal

        pacientes = (
            self.sistema.obtener_pacientes()
        )

        personal = (
            self.sistema.obtener_personal()
        )

        if not pacientes and not personal:

            messagebox.showwarning(
                "Aviso",
                (
                    "No existen pacientes ni "
                    "profesionales registrados."
                )
            )

            return

        ventana = self._crear_pantalla_interna(
            "Historial clínico"
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
            command=lambda: self._abrir_desde_menu(
                self.historial_pacientes,
                self.historial_clinico,
            )
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
            command=lambda: self._abrir_desde_menu(
                self.historial_profesionales,
                self.historial_clinico,
            )
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

        ventana = self._crear_pantalla_interna(
            "Historial de pacientes"
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
                "Consulte las citas y atenciones médicas "
                "registradas del paciente."
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

        self.configurar_limite_busqueda(
            entrada_busqueda,
            ventana
        )

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
                        .buscar_paciente_por_codigo(
                            valor
                        )
                    )

                else:

                    dni = self.validar_dni(
                        valor
                    )

                    resultados = (
                        self.sistema
                        .buscar_paciente_por_dni(
                            dni
                        )
                    )

                paciente = (
                    resultados[0]
                    if resultados
                    else None
                )

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
                # OBTENER REGISTROS
                # =================================================

                citas = [
                    cita
                    for cita
                    in self.sistema.obtener_citas()
                    if (
                        cita.paciente.codigo
                        == paciente.codigo
                    )
                ]

                atenciones = [
                    atencion
                    for atencion
                    in self.sistema.obtener_atenciones()
                    if (
                        atencion.paciente.codigo
                        == paciente.codigo
                    )
                ]
                ventas_medicamentos = self.sistema.obtener_historial_paciente(
                    paciente.codigo
                ).get("ventas_medicamentos", [])

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
                        (
                            "El paciente no tiene "
                            "citas registradas.\n\n"
                        )
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
                            f"Fecha y hora: {cita.fecha} {cita.hora}\n"
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
                        (
                            "El paciente no tiene "
                            "atenciones registradas.\n"
                        )
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
                        if atencion.recetas:
                            texto.insert(tk.END, "Medicamentos recetados:\n")
                            for receta in atencion.recetas:
                                texto.insert(tk.END, f"  • {receta.mostrar_informacion()}\n")

                        texto.insert(
                            tk.END,
                            "--------------------------------------------------\n"
                        )

                texto.insert(tk.END, "\nMEDICAMENTOS REGISTRADOS EN VENTA\n")
                texto.insert(tk.END, "--------------------------------------------------\n")
                if not ventas_medicamentos:
                    texto.insert(tk.END, "No hay ventas de medicamentos vinculadas a este paciente.\n")
                else:
                    for venta in ventas_medicamentos:
                        (_id, medicamento, lote, cantidad, _precio, total, codigo, vendedor, fecha_hora) = venta
                        texto.insert(
                            tk.END,
                            f"{fecha_hora} · {medicamento} · Lote {lote} · "
                            f"{cantidad} unidad(es) · S/ {float(total):.2f} · "
                            f"Paciente {codigo} · Registró: {vendedor}\n",
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

                texto.delete(
                    "1.0",
                    tk.END
                )

                texto.config(
                    state="disabled"
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

        personal = [
            p for p in self.sistema.obtener_personal()
            if not self._es_personal_enfermeria(p)
        ]

        if not personal:

            messagebox.showwarning(
                "Aviso",
                "No existe personal profesional registrado."
            )

            return

        ventana = self._crear_pantalla_interna(
            "Historial de profesionales"
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

        self.configurar_limite_busqueda(
            entrada_busqueda,
            ventana
        )

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
                            if (
                                p.codigo_profesional
                                == valor
                            )
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

                texto.config(
                    state="normal"
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
                # CITAS
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
                        (
                            "El profesional no tiene "
                            "citas registradas.\n\n"
                        )
                    )

                else:

                    for cita in citas:

                        texto.insert(
                            tk.END,
                            f"Código de cita: {cita.codigo}\n"
                        )

                        texto.insert(
                            tk.END,
                            f"Fecha y hora: {cita.fecha} {cita.hora}\n"
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
                # ATENCIONES
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
                        (
                            "El profesional no tiene "
                            "atenciones registradas.\n"
                        )
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

                texto.config(
                    state="disabled"
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

        ventana = self._crear_pantalla_interna(
            "Estadísticas del sistema"
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
                "Citas reprogramadas",
                reporte_citas["reprogramadas"]
            ),
            (
                "Citas no atendidas",
                reporte_citas["no_atendidas"]
            ),
            (
                "Citas canceladas",
                reporte_citas["canceladas"]
            ),
            (
                "Total de atenciones",
                reporte["atenciones"]
            ),
            (
                "Atenciones finalizadas",
                reporte_atenciones["finalizadas"]
            ),
            (
                "Atenciones en proceso",
                reporte_atenciones["en_proceso"]
            )
        ]

        zona = tk.Frame(ventana, bg=COLOR_FONDO)
        zona.pack(fill="x", padx=25, pady=(8, 16))
        columnas_actuales = [0]

        def distribuir_estadisticas(evento=None):
            ancho = evento.width if evento is not None else zona.winfo_width()
            if ancho < 100:
                return

            columnas = max(1, min(4, ancho // 280))
            if columnas == columnas_actuales[0]:
                return
            columnas_actuales[0] = columnas

            for widget in zona.winfo_children():
                widget.destroy()

            for columna in range(4):
                zona.columnconfigure(
                    columna,
                    weight=1 if columna < columnas else 0,
                    uniform="estadisticas" if columna < columnas else "",
                )

            for indice, (nombre, cantidad) in enumerate(estadisticas):
                tarjeta = tk.Frame(
                    zona,
                    bg=COLOR_PANEL,
                    highlightbackground=COLOR_PANEL_CLARO,
                    highlightthickness=1,
                    padx=12,
                    pady=8,
                )
                tarjeta.grid(
                    row=indice // columnas,
                    column=indice % columnas,
                    sticky="nsew",
                    padx=5,
                    pady=5,
                )
                tk.Label(
                    tarjeta,
                    text=nombre,
                    font=("Arial", 10, "bold"),
                    fg=COLOR_GRIS_CLARO,
                    bg=COLOR_PANEL,
                    anchor="w",
                ).pack(fill="x")
                tk.Label(
                    tarjeta,
                    text=str(cantidad),
                    font=("Arial", 20, "bold"),
                    fg=COLOR_TEXTO,
                    bg=COLOR_PANEL,
                    anchor="w",
                ).pack(fill="x", pady=(2, 0))

        zona.bind("<Configure>", distribuir_estadisticas)
        zona.after_idle(distribuir_estadisticas)

    # =========================================================
    # REPORTES
    # =========================================================

    def ver_reportes(self):

        ventana = self._crear_pantalla_interna(
            "Reportes del sistema"
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

        # =====================================================
        # ENCABEZADO
        # =====================================================

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
            f"Reprogramadas: "
            f"{reporte_citas['reprogramadas']}\n"
        )

        texto.insert(
            tk.END,
            f"No atendidas: "
            f"{reporte_citas['no_atendidas']}\n"
        )

        texto.insert(
            tk.END,
            f"Canceladas: "
            f"{reporte_citas['canceladas']}\n\n"
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

        texto.config(
            state="disabled"
        )


# =============================================================
# EJECUCIÓN
# =============================================================

if __name__ == "__main__":
    from main import main

    main()

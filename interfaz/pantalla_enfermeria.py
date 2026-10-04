"""Portal de enfermería con agenda, inventario y ventas de medicamentos."""

from datetime import date
import tkinter as tk
from tkinter import ttk

from interfaz.estilos import (
    COLOR_BLANCO,
    COLOR_FONDO,
    COLOR_GRIS,
    COLOR_GRIS_CLARO,
    COLOR_PANEL,
    COLOR_PANEL_CLARO,
    COLOR_ROJO,
    COLOR_ROJO_CLARO,
    COLOR_TEXTO,
    FUENTE_BOTON,
    FUENTE_LOGO,
    FUENTE_SUBTITULO,
    FUENTE_TITULO,
)
from interfaz.navegacion import VistaDesplazable, instalar_navegacion
from servicios.autenticacion import ServicioAutenticacion
from servicios.sistema_salud import SistemaSalud


class PantallaEnfermeria:
    """Muestra la agenda y las funciones de farmacia de enfermería."""

    def __init__(self, ventana, pantalla_inicio, sesion):
        if sesion is None or sesion.rol != "enfermeria":
            raise ValueError("Se requiere una sesión de enfermería autenticada.")

        self.ventana = ventana
        self.pantalla_inicio = pantalla_inicio
        self.sesion = sesion
        self.sistema = SistemaSalud()
        personal = self.sistema.buscar_personal_por_codigo(
            sesion.codigo_referencia or ""
        )
        if not personal or not ServicioAutenticacion._puede_entrar(
            personal[0].especialidad, "enfermeria"
        ):
            self.sistema.cerrar()
            raise ValueError("La cuenta ya no está asignada a enfermería.")
        self.enfermero_actual = personal[0]
        self.ventana.title("SaluPro - Portal de Enfermería")
        self.ventana.configure(bg=COLOR_FONDO)
        self.mostrar_inicio()

    def _limpiar(self):
        for widget in self.ventana.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

    def _boton(self, padre, texto, comando, principal=False):
        return tk.Button(
            padre,
            text=texto,
            command=comando,
            font=FUENTE_BOTON,
            bg=COLOR_ROJO if principal else COLOR_PANEL_CLARO,
            fg=COLOR_BLANCO if principal else COLOR_TEXTO,
            activebackground=COLOR_ROJO_CLARO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=14,
            pady=8,
        )

    def _iniciar_pantalla(self, titulo, subtitulo="", mostrar_volver=False):
        self._limpiar()
        instalar_navegacion(
            self.ventana,
            volver=self.cerrar_sesion if not mostrar_volver else self.mostrar_inicio,
            inicio=self.cerrar_sesion,
        )
        vista = VistaDesplazable(self.ventana, COLOR_FONDO)
        vista.pack(fill="both", expand=True)
        contenido = vista.contenido
        contenido.configure(padx=24, pady=18)

        barra = tk.Frame(contenido, bg=COLOR_FONDO)
        barra.pack(fill="x", pady=(0, 12))
        if mostrar_volver:
            self._boton(barra, "←  Inicio de enfermería", self.mostrar_inicio).pack(
                side="left"
            )
        self._boton(barra, "Cerrar sesión", self.cerrar_sesion).pack(side="right")
        tk.Label(
            barra,
            text="SALUPRO",
            font=FUENTE_LOGO,
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO,
        ).pack(side="right", padx=(0, 18))
        tk.Frame(contenido, bg=COLOR_ROJO, height=3).pack(fill="x", pady=(0, 18))
        tk.Label(
            contenido,
            text=titulo,
            font=FUENTE_TITULO,
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO,
            wraplength=900,
            justify="left",
        ).pack(anchor="w", pady=(0, 4))
        if subtitulo:
            tk.Label(
                contenido,
                text=subtitulo,
                font=FUENTE_SUBTITULO,
                fg=COLOR_GRIS_CLARO,
                bg=COLOR_FONDO,
                wraplength=900,
                justify="left",
            ).pack(anchor="w", pady=(0, 16))
        return contenido

    @staticmethod
    def _tarjeta(padre, titulo=None, fondo=COLOR_PANEL):
        tarjeta = tk.Frame(
            padre,
            bg=fondo,
            padx=16,
            pady=14,
            highlightthickness=1,
            highlightbackground="#DCE8E1",
        )
        if titulo:
            tk.Label(
                tarjeta,
                text=titulo,
                font=("Arial", 14, "bold"),
                fg=COLOR_TEXTO,
                bg=fondo,
            ).pack(anchor="w", pady=(0, 10))
        return tarjeta

    def _crear_estadisticas(self, padre, datos):
        zona = tk.Frame(padre, bg=COLOR_FONDO)
        zona.pack(fill="x", pady=(0, 16))
        for columna in range(len(datos)):
            zona.columnconfigure(columna, weight=1, uniform="estadisticas_enfermeria")
        for columna, (valor, etiqueta) in enumerate(datos):
            tarjeta = tk.Frame(
                zona,
                bg=COLOR_PANEL,
                padx=14,
                pady=13,
                highlightthickness=1,
                highlightbackground="#DCE8E1",
            )
            tarjeta.grid(row=0, column=columna, sticky="nsew", padx=5)
            tk.Label(
                tarjeta,
                text=str(valor),
                font=("Arial", 22, "bold"),
                fg=COLOR_ROJO,
                bg=COLOR_PANEL,
            ).pack(anchor="w")
            tk.Label(
                tarjeta,
                text=etiqueta,
                font=("Arial", 9),
                fg=COLOR_GRIS,
                bg=COLOR_PANEL,
                wraplength=190,
                justify="left",
            ).pack(anchor="w", pady=(4, 0))

    def _crear_modulo(self, padre, fila, columna, icono, titulo, descripcion, comando):
        tarjeta = tk.Frame(
            padre,
            bg=COLOR_PANEL,
            padx=16,
            pady=14,
            highlightthickness=1,
            highlightbackground="#DCE8E1",
        )
        tarjeta.grid(row=fila, column=columna, sticky="nsew", padx=6, pady=6)
        tarjeta.columnconfigure(0, weight=1)
        tk.Label(
            tarjeta,
            text=icono,
            font=("Arial", 21, "bold"),
            fg=COLOR_ROJO,
            bg=COLOR_PANEL,
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            tarjeta,
            text=titulo,
            font=("Arial", 13, "bold"),
            fg=COLOR_TEXTO,
            bg=COLOR_PANEL,
            wraplength=350,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(4, 3))
        tk.Label(
            tarjeta,
            text=descripcion,
            font=("Arial", 9),
            fg=COLOR_GRIS,
            bg=COLOR_PANEL,
            wraplength=350,
            justify="left",
        ).grid(row=2, column=0, sticky="w", pady=(0, 12))
        self._boton(tarjeta, "Abrir", comando, principal=True).grid(
            row=3, column=0, sticky="ew"
        )

    def _citas_asignadas(self):
        return sorted(
            (
                cita
                for cita in self.sistema.obtener_citas()
                if cita.profesional.codigo_profesional
                == self.enfermero_actual.codigo_profesional
                and cita.estado not in {"Cancelada", "No atendida"}
            ),
            key=lambda cita: cita.fecha_hora,
        )

    def mostrar_inicio(self):
        citas = self._citas_asignadas()
        farmacia = self.sistema.obtener_estadisticas_medicamentos()
        disponibles = self.sistema.obtener_medicamentos_disponibles()
        contenido = self._iniciar_pantalla(
            "Portal de Enfermería",
            f"{self.enfermero_actual.nombre} · Código "
            f"{self.enfermero_actual.codigo_profesional}",
        )

        tk.Label(
            contenido,
            text="Resumen de hoy",
            font=("Arial", 15, "bold"),
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO,
        ).pack(anchor="w", pady=(0, 8))
        self._crear_estadisticas(
            contenido,
            (
                (len(citas), "citas asignadas"),
                (farmacia["unidades_disponibles"], "unidades disponibles"),
                (farmacia["ventas_hoy"], "ventas registradas hoy"),
            ),
        )

        tk.Label(
            contenido,
            text="MÓDULOS DE ENFERMERÍA",
            font=("Arial", 14, "bold"),
            fg=COLOR_TEXTO,
            bg=COLOR_FONDO,
        ).pack(anchor="w", pady=(0, 4))
        modulos = tk.Frame(contenido, bg=COLOR_FONDO)
        modulos.pack(fill="x", pady=(0, 14))
        modulos.columnconfigure(0, weight=1, uniform="modulos_enfermeria")
        modulos.columnconfigure(1, weight=1, uniform="modulos_enfermeria")
        self._crear_modulo(
            modulos,
            0,
            0,
            "＋",
            "Registrar medicamentos",
            "Registra lote, vencimiento, stock inicial y precio de venta.",
            self.mostrar_registro_medicamentos,
        )
        self._crear_modulo(
            modulos,
            0,
            1,
            "▤",
            "Medicamentos disponibles",
            "Consulta lotes vigentes, existencias, precios y stock mínimo.",
            self.mostrar_medicamentos_disponibles,
        )
        self._crear_modulo(
            modulos,
            1,
            0,
            "S/",
            "Registrar venta",
            "Selecciona medicamentos del inventario y descuenta el stock al vender.",
            self.mostrar_ventas,
        )
        self._crear_modulo(
            modulos,
            1,
            1,
            "◷",
            "Agenda asignada",
            "Consulta las citas vinculadas a tu cuenta de enfermería.",
            self.mostrar_agenda,
        )

        panel = self._tarjeta(contenido, "Agenda asignada")
        panel.pack(fill="x", pady=(0, 12))
        if not citas:
            tk.Label(
                panel,
                text="No hay citas asignadas en este momento.",
                font=("Arial", 10),
                fg=COLOR_GRIS,
                bg=COLOR_PANEL,
            ).pack(anchor="w", pady=4)
        else:
            for cita in citas:
                fila = tk.Frame(panel, bg=COLOR_PANEL, padx=2, pady=8)
                fila.pack(fill="x")
                fila.columnconfigure(0, weight=1)
                fila.columnconfigure(1, weight=2)
                fila.columnconfigure(2, weight=1)
                tk.Label(
                    fila,
                    text=f"{cita.fecha} · {cita.hora}",
                    font=("Arial", 10, "bold"),
                    fg=COLOR_TEXTO,
                    bg=COLOR_PANEL,
                    anchor="w",
                ).grid(row=0, column=0, sticky="ew", padx=5)
                tk.Label(
                    fila,
                    text=f"{cita.paciente.nombre}\n{cita.motivo}",
                    font=("Arial", 10),
                    fg=COLOR_TEXTO,
                    bg=COLOR_PANEL,
                    anchor="w",
                    justify="left",
                    wraplength=420,
                ).grid(row=0, column=1, sticky="ew", padx=5)
                tk.Label(
                    fila,
                    text=cita.estado,
                    font=("Arial", 9, "bold"),
                    fg=COLOR_ROJO,
                    bg=COLOR_PANEL,
                    anchor="e",
                ).grid(row=0, column=2, sticky="ew", padx=5)
                tk.Frame(panel, bg=COLOR_PANEL_CLARO, height=1).pack(fill="x")

    def mostrar_agenda(self):
        citas = self._citas_asignadas()
        contenido = self._iniciar_pantalla(
            "Agenda asignada",
            "Citas vinculadas a tu cuenta de enfermería.",
            mostrar_volver=True,
        )
        panel = self._tarjeta(contenido, "Próximas atenciones")
        panel.pack(fill="x")
        if not citas:
            tk.Label(
                panel,
                text="No hay citas asignadas en este momento.",
                font=("Arial", 10),
                fg=COLOR_GRIS,
                bg=COLOR_PANEL,
            ).pack(anchor="w")
            return
        for cita in citas:
            fila = tk.Frame(panel, bg=COLOR_PANEL, pady=8)
            fila.pack(fill="x")
            fila.columnconfigure(0, weight=1)
            fila.columnconfigure(1, weight=2)
            fila.columnconfigure(2, weight=1)
            for col, texto in enumerate(
                (f"{cita.fecha} · {cita.hora}", cita.paciente.nombre, cita.estado)
            ):
                tk.Label(
                    fila,
                    text=texto,
                    font=("Arial", 10, "bold" if col == 2 else "normal"),
                    fg=COLOR_TEXTO,
                    bg=COLOR_PANEL,
                    anchor="w",
                    wraplength=300,
                ).grid(row=0, column=col, sticky="ew", padx=6)
            tk.Label(
                panel,
                text=cita.motivo,
                font=("Arial", 9),
                fg=COLOR_GRIS,
                bg=COLOR_PANEL,
                anchor="w",
                wraplength=850,
                justify="left",
            ).pack(fill="x", padx=6, pady=(0, 5))
            tk.Frame(panel, bg=COLOR_PANEL_CLARO, height=1).pack(fill="x")

    def _etiqueta_campo(self, padre, texto, fila, columna):
        tk.Label(
            padre,
            text=texto,
            font=("Arial", 10, "bold"),
            fg=COLOR_TEXTO,
            bg=COLOR_PANEL,
            anchor="w",
        ).grid(row=fila, column=columna, sticky="ew", padx=7, pady=(5, 2))

    def _entrada_campo(self, padre, campos, clave, texto, fila, columna):
        self._etiqueta_campo(padre, texto, fila, columna)
        entrada = tk.Entry(
            padre,
            font=("Arial", 11),
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            relief="flat",
            bd=0,
        )
        entrada.grid(row=fila + 1, column=columna, sticky="ew", padx=7, pady=(0, 7), ipady=7)
        campos[clave] = entrada
        return entrada

    def _lista_medicamentos(self, padre, medicamentos):
        if not medicamentos:
            tk.Label(
                padre,
                text="No hay medicamentos disponibles para mostrar.",
                font=("Arial", 10),
                fg=COLOR_GRIS,
                bg=COLOR_PANEL,
            ).pack(anchor="w", pady=5)
            return

        cabecera = tk.Frame(padre, bg=COLOR_PANEL_CLARO, padx=8, pady=7)
        cabecera.pack(fill="x", pady=(0, 4))
        for columna, texto in enumerate(("Medicamento / presentación", "Lote / vencimiento", "Stock / precio")):
            cabecera.columnconfigure(columna, weight=(2 if columna == 0 else 1))
            tk.Label(
                cabecera,
                text=texto,
                font=("Arial", 9, "bold"),
                fg=COLOR_TEXTO,
                bg=COLOR_PANEL_CLARO,
                anchor="w",
            ).grid(row=0, column=columna, sticky="ew", padx=4)
        for medicamento in medicamentos:
            (
                codigo,
                nombre,
                principio_activo,
                presentacion,
                lote,
                vencimiento,
                stock,
                stock_minimo,
                precio,
                registrado_por,
                creado_en,
            ) = medicamento
            fila = tk.Frame(padre, bg=COLOR_PANEL, padx=8, pady=8)
            fila.pack(fill="x")
            for columna, peso in enumerate((2, 1, 1)):
                fila.columnconfigure(columna, weight=peso)
            nombre_detalle = nombre
            if presentacion:
                nombre_detalle += f" · {presentacion}"
            if principio_activo:
                nombre_detalle += f"\n{principio_activo}"
            detalles = (
                nombre_detalle,
                f"{lote}\nVence: {vencimiento}",
                f"{stock} un. · S/ {float(precio):.2f}\nMínimo: {stock_minimo}",
            )
            for columna, texto in enumerate(detalles):
                tk.Label(
                    fila,
                    text=texto,
                    font=("Arial", 9),
                    fg=COLOR_TEXTO,
                    bg=COLOR_PANEL,
                    anchor="w",
                    justify="left",
                    wraplength=260,
                ).grid(row=0, column=columna, sticky="ew", padx=4)
            tk.Frame(padre, bg=COLOR_PANEL_CLARO, height=1).pack(fill="x")

    def mostrar_registro_medicamentos(self, mensaje=""):
        contenido = self._iniciar_pantalla(
            "Registrar medicamentos",
            "Agrega existencias por lote para que aparezcan en el inventario y en el formulario de venta.",
            mostrar_volver=True,
        )
        panel = self._tarjeta(contenido, "Datos del medicamento")
        panel.pack(fill="x", pady=(0, 12))
        formulario = tk.Frame(panel, bg=COLOR_PANEL)
        formulario.pack(fill="x")
        formulario.columnconfigure(0, weight=1, uniform="campos_medicamento")
        formulario.columnconfigure(1, weight=1, uniform="campos_medicamento")
        campos = {}
        self._entrada_campo(formulario, campos, "nombre", "Nombre del medicamento *", 0, 0)
        self._entrada_campo(formulario, campos, "principio_activo", "Principio activo", 0, 1)
        self._entrada_campo(formulario, campos, "presentacion", "Presentación (tableta, frasco...) ", 2, 0)
        self._entrada_campo(formulario, campos, "lote", "Número de lote *", 2, 1)
        vencimiento = self._entrada_campo(
            formulario, campos, "vencimiento", "Vencimiento (AAAA-MM-DD) *", 4, 0
        )
        vencimiento.insert(0, date.today().replace(year=date.today().year + 1).isoformat())
        self._entrada_campo(formulario, campos, "stock", "Stock inicial *", 4, 1)
        self._entrada_campo(formulario, campos, "stock_minimo", "Stock mínimo", 6, 0)
        self._entrada_campo(formulario, campos, "precio_venta", "Precio por unidad (S/) *", 6, 1)
        estado = tk.Label(
            panel,
            text=mensaje,
            font=("Arial", 9),
            fg=COLOR_ROJO if mensaje and not mensaje.startswith("Registrado") else COLOR_GRIS,
            bg=COLOR_PANEL,
            wraplength=850,
            justify="left",
        )
        estado.pack(fill="x", pady=(2, 8))

        def guardar():
            try:
                self.sistema.registrar_medicamento(
                    campos["nombre"].get(),
                    campos["principio_activo"].get(),
                    campos["presentacion"].get(),
                    campos["lote"].get(),
                    campos["vencimiento"].get(),
                    campos["stock"].get(),
                    campos["stock_minimo"].get() or "0",
                    campos["precio_venta"].get(),
                    self.enfermero_actual.nombre,
                )
            except Exception as error:
                estado.configure(text=str(error), fg=COLOR_ROJO)
                return
            self.mostrar_registro_medicamentos(
                "Registrado correctamente. Ya aparece en el inventario disponible y en ventas cuando tiene stock vigente."
            )

        self._boton(panel, "Guardar medicamento", guardar, principal=True).pack(
            fill="x", pady=(0, 4)
        )

        inventario = self._tarjeta(contenido, "Consulta de medicamentos disponibles")
        inventario.pack(fill="x", pady=(0, 12))
        disponibles = self.sistema.obtener_medicamentos_disponibles()
        self._lista_medicamentos(inventario, disponibles[:8])
        self._boton(
            inventario,
            "Ver inventario disponible",
            self.mostrar_medicamentos_disponibles,
        ).pack(anchor="e", pady=(10, 0))

    def mostrar_medicamentos_disponibles(self):
        contenido = self._iniciar_pantalla(
            "Medicamentos disponibles",
            "Solo se muestran lotes vigentes que tienen existencias.",
            mostrar_volver=True,
        )
        panel = self._tarjeta(contenido, "Buscar en inventario")
        panel.pack(fill="x")
        busqueda = tk.StringVar(master=self.ventana)
        campo = tk.Entry(
            panel,
            textvariable=busqueda,
            font=("Arial", 11),
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            relief="flat",
            bd=0,
        )
        campo.pack(fill="x", ipady=7, pady=(0, 10))
        listado = tk.Frame(panel, bg=COLOR_PANEL)
        listado.pack(fill="x")

        def actualizar(*_args):
            for widget in listado.winfo_children():
                widget.destroy()
            filtro = busqueda.get().strip().casefold()
            disponibles = self.sistema.obtener_medicamentos_disponibles()
            resultados = [
                med
                for med in disponibles
                if not filtro or filtro in " ".join(map(str, (med[1], med[2], med[3], med[4]))).casefold()
            ]
            self._lista_medicamentos(listado, resultados)

        busqueda.trace_add("write", actualizar)
        actualizar()

    def mostrar_ventas(self, mensaje=""):
        contenido = self._iniciar_pantalla(
            "Registrar venta de medicamentos",
            "La lista se alimenta del inventario registrado y vigente. Al guardar se descuenta la cantidad vendida.",
            mostrar_volver=True,
        )
        panel = self._tarjeta(contenido, "Nueva venta")
        panel.pack(fill="x", pady=(0, 12))
        panel.columnconfigure(0, weight=1)
        medicamentos = self.sistema.obtener_medicamentos_disponibles()
        opciones = {
            f"{med[1]} · Lote {med[4]} · {med[6]} un. · S/ {float(med[8]):.2f}": med
            for med in medicamentos
        }
        seleccion = tk.StringVar(master=self.ventana)
        combo = ttk.Combobox(
            panel,
            textvariable=seleccion,
            values=list(opciones),
            state="readonly" if opciones else "disabled",
            font=("Arial", 11),
        )
        combo.pack(fill="x", pady=(0, 8), ipady=4)
        if opciones:
            combo.current(0)
        else:
            seleccion.set("No hay medicamentos vigentes con stock disponible")

        tk.Label(
            panel,
            text="Cantidad",
            font=("Arial", 10, "bold"),
            fg=COLOR_TEXTO,
            bg=COLOR_PANEL,
        ).pack(anchor="w", pady=(3, 2))
        cantidad = tk.Entry(
            panel,
            font=("Arial", 11),
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            relief="flat",
            bd=0,
        )
        cantidad.pack(fill="x", ipady=7, pady=(0, 8))
        cantidad.insert(0, "1")
        tk.Label(
            panel,
            text="Código del paciente *",
            font=("Arial", 10, "bold"),
            fg=COLOR_TEXTO,
            bg=COLOR_PANEL,
        ).pack(anchor="w", pady=(3, 2))
        codigo_paciente = tk.Entry(
            panel,
            font=("Arial", 11),
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            relief="flat",
            bd=0,
        )
        codigo_paciente.pack(fill="x", ipady=7, pady=(0, 4))
        tk.Label(
            panel,
            text="La fecha y hora se guardan automáticamente al registrar.",
            font=("Arial", 9),
            fg=COLOR_GRIS,
            bg=COLOR_PANEL,
        ).pack(anchor="w", pady=(0, 8))
        estado = tk.Label(
            panel,
            text=mensaje,
            font=("Arial", 9),
            fg=COLOR_GRIS,
            bg=COLOR_PANEL,
            wraplength=850,
            justify="left",
        )
        estado.pack(anchor="w", pady=(0, 8))

        def guardar_venta():
            elegido = opciones.get(seleccion.get())
            if not elegido:
                estado.configure(text="Registra o selecciona un medicamento disponible.", fg=COLOR_ROJO)
                return
            try:
                _id, total, existencia = self.sistema.vender_medicamento(
                    elegido[0],
                    cantidad.get(),
                    codigo_paciente.get(),
                    self.enfermero_actual.nombre,
                )
            except Exception as error:
                estado.configure(text=str(error), fg=COLOR_ROJO)
                return
            self.mostrar_ventas(
                f"Venta registrada: S/ {total:.2f}. Existencia restante: {existencia} unidad(es)."
            )

        self._boton(panel, "Registrar venta", guardar_venta, principal=True).pack(
            fill="x"
        )

        inventario = self._tarjeta(contenido, "Medicamentos que puedes vender")
        inventario.pack(fill="x", pady=(0, 12))
        self._lista_medicamentos(inventario, medicamentos)

        historial = self._tarjeta(contenido, "Ventas recientes")
        historial.pack(fill="x", pady=(0, 12))
        ventas = self.sistema.obtener_ventas_medicamentos(50)
        if not ventas:
            tk.Label(
                historial,
                text="Todavía no hay ventas registradas.",
                font=("Arial", 10),
                fg=COLOR_GRIS,
                bg=COLOR_PANEL,
            ).pack(anchor="w")
        else:
            for venta in ventas:
                (_id, nombre, lote, unidades, precio, total, comprador, vendedor, fecha_hora, codigo_paciente) = venta
                detalle = (
                    f"{fecha_hora} · {nombre} · Lote {lote} · "
                    f"{unidades} un. · S/ {float(total):.2f}"
                )
                detalle += f" · Paciente {codigo_paciente or 'sin vincular'}"
                tk.Label(
                    historial,
                    text=detalle,
                    font=("Arial", 9),
                    fg=COLOR_TEXTO,
                    bg=COLOR_PANEL,
                    anchor="w",
                    justify="left",
                    wraplength=850,
                ).pack(fill="x", pady=4)
                tk.Frame(historial, bg=COLOR_PANEL_CLARO, height=1).pack(fill="x")

    def cerrar_sesion(self):
        try:
            self.sistema.cerrar()
        except Exception:
            pass
        self.pantalla_inicio.mostrar()

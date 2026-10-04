"""Pantalla de acceso y alta de cuentas dentro de la ventana principal."""

import tkinter as tk
from tkinter import messagebox

from servicios.autenticacion import ServicioAutenticacion
from servicios.validaciones import (
    validar_dni_en_edicion,
    validar_nombre_en_edicion,
)
from interfaz.navegacion import VistaDesplazable
from interfaz.estilos import (
    COLOR_BLANCO,
    COLOR_FONDO,
    COLOR_GRIS,
    COLOR_GRIS_CLARO,
    COLOR_PANEL_CLARO,
    COLOR_ROJO,
    COLOR_ROJO_CLARO,
    COLOR_TEXTO,
    FUENTE_BOTON,
    FUENTE_SUBTITULO,
)


FUENTE_TITULO_MODAL = ("Arial", 22, "bold")

TERMINOS_CONDICIONES = """TÉRMINOS Y CONDICIONES – RURAL SALUDPRO

Última actualización: octubre de 2026

1. Aceptación de los términos

Al ingresar y utilizar la plataforma Rural SaludPro, el usuario acepta estos términos y condiciones. Si no está de acuerdo con alguno de ellos, deberá evitar utilizar los servicios de la plataforma.

2. Finalidad de Rural SaludPro

Rural SaludPro es una plataforma digital diseñada para facilitar el acceso a información y servicios relacionados con la atención de salud en comunidades rurales.

La plataforma puede permitir el registro de pacientes, consulta de información, seguimiento de atenciones, comunicación con personal de salud y otras funciones relacionadas con la gestión de servicios de salud.

3. Uso adecuado de la plataforma

El usuario se compromete a:

• Proporcionar información verdadera y actualizada.
• Utilizar la plataforma únicamente para fines relacionados con los servicios ofrecidos.
• No utilizar información de otros usuarios sin autorización.
• No intentar acceder a cuentas, registros o información que no le correspondan.
• Mantener en confidencialidad sus credenciales de acceso.

4. Información de salud

La información relacionada con la salud es considerada información sensible. Rural SaludPro deberá utilizarla únicamente para las finalidades informadas al usuario y aplicar medidas de seguridad para evitar accesos no autorizados.

Cuando corresponda, el tratamiento de datos personales deberá contar con el consentimiento válido del titular, de acuerdo con la normativa peruana aplicable.

5. Protección de datos personales

Rural SaludPro se compromete a proteger los datos personales recopilados mediante la plataforma y utilizarlos únicamente para las finalidades informadas.

El usuario podrá ejercer los derechos que correspondan sobre sus datos personales, como acceso, rectificación, cancelación u oposición, conforme a la legislación peruana aplicable.

6. Seguridad

La plataforma implementará medidas técnicas y organizativas destinadas a proteger la información frente a pérdida, alteración, acceso o tratamiento no autorizado.

Los usuarios también son responsables de proteger sus contraseñas y evitar compartir sus credenciales.

7. Información médica

La información proporcionada por Rural SaludPro tiene como finalidad apoyar la gestión y atención de los servicios de salud.

La plataforma no sustituye la evaluación, diagnóstico o tratamiento realizado por un profesional de la salud.

8. Disponibilidad del servicio

Rural SaludPro buscará mantener disponible la plataforma, pero podrían producirse interrupciones por mantenimiento, problemas de conectividad, fallas técnicas o circunstancias externas.

9. Responsabilidad del usuario

El usuario será responsable del uso que realice de su cuenta y de la información que registre en la plataforma.

No deberá ingresar información falsa, utilizar cuentas de terceros ni realizar actividades que puedan afectar el funcionamiento o la seguridad del sistema.

10. Modificaciones

Rural SaludPro podrá actualizar estos términos cuando sea necesario para mejorar el servicio, incorporar nuevas funcionalidades o cumplir cambios en la normativa.

Las modificaciones serán comunicadas mediante la plataforma cuando corresponda.

11. Contacto

Para consultas, solicitudes relacionadas con los datos personales o problemas con la plataforma, el usuario podrá comunicarse mediante los canales oficiales de Rural SaludPro.

12. Aceptación

Al seleccionar “Acepto los términos y condiciones”, el usuario declara haber leído y comprendido las condiciones de uso de Rural SaludPro."""


class ModalVerificador(tk.Frame):
    ROLES = {
        "paciente": ("Paciente", "Accede a tu información personal."),
        "administrativa": (
            "Área administrativa",
            "Acceso de gestión con cuenta autorizada.",
        ),
        "profesional": (
            "Profesional de salud",
            "Ingresar cuenta ",
        ),
        "enfermeria": (
            "Área de enfermería",
            "Ingresar cuenta",
        ),
    }

    def __init__(self, parent, rol, al_autenticar):
        super().__init__(parent, bg=COLOR_FONDO)
        if rol not in self.ROLES:
            raise ValueError("El rol de acceso no es válido.")

        self.parent = parent
        self.rol = rol
        self.al_autenticar = al_autenticar
        self.servicio = ServicioAutenticacion()
        self._cerrado = False
        self._pagina_terminos = None
        self.acepta_terminos = None
        self.modo = "configurar_admin" if (
            rol == "administrativa" and not self.servicio.hay_administrador()
        ) else "login"
        self.campos = {}

        nombre, _ = self.ROLES[rol]
        parent.title(f"SaluPro · {nombre}")
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()
        self.bind("<Escape>", lambda _evento: self.destroy())
        self._construir()

    def _centrar(self):
        """Reinicia el desplazamiento al cambiar el contenido del formulario."""
        self.update_idletasks()
        self._vista.canvas.yview_moveto(0)

    def _construir(self):
        nombre, descripcion = self.ROLES[self.rol]
        self._vista = VistaDesplazable(self, COLOR_FONDO)
        self._vista.pack(fill="both", expand=True)
        exterior = tk.Frame(
            self._vista.contenido, bg=COLOR_FONDO, padx=24, pady=22
        )
        exterior.pack(fill="both", expand=True)
        self.exterior = exterior

        tarjeta = tk.Frame(
            exterior,
            bg=COLOR_BLANCO,
            width=540,
            padx=30,
            pady=26,
            highlightthickness=1,
            highlightbackground="#DCE8E1",
        )
        tarjeta.pack(anchor="center", expand=True, pady=18)

        tk.Button(
            tarjeta,
            text="←  Volver al inicio",
            command=self.destroy,
            font=("Arial", 10),
            bg=COLOR_BLANCO,
            fg=COLOR_ROJO,
            activebackground=COLOR_PANEL_CLARO,
            activeforeground=COLOR_ROJO,
            relief="flat",
            cursor="hand2",
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(
            tarjeta,
            text="SALUPRO",
            font=("Arial", 17, "bold"),
            fg=COLOR_ROJO,
            bg=COLOR_BLANCO,
        ).pack(pady=(0, 14))
        tk.Frame(tarjeta, bg=COLOR_ROJO, height=3).pack(fill="x")

        self.titulo = tk.Label(
            tarjeta,
            text="",
            font=FUENTE_TITULO_MODAL,
            fg=COLOR_TEXTO,
            bg=COLOR_BLANCO,
            wraplength=390,
            justify="center",
        )
        self.titulo.pack(pady=(20, 5))
        tk.Label(
            tarjeta,
            text=f"{nombre}  ·  {descripcion}",
            font=FUENTE_SUBTITULO,
            fg=COLOR_GRIS_CLARO,
            bg=COLOR_BLANCO,
            wraplength=390,
            justify="center",
        ).pack(pady=(0, 17))

        self.formulario = tk.Frame(tarjeta, bg=COLOR_BLANCO)
        self.formulario.pack(fill="x")
        self.error = tk.Label(
            tarjeta,
            text="",
            font=("Arial", 9),
            fg="#A33737",
            bg=COLOR_BLANCO,
            wraplength=390,
            justify="center",
        )
        self.error.pack(pady=(8, 0))
        self._mostrar_modo(self.modo)

    def _agregar_consentimiento(self):
        self.acepta_terminos = tk.BooleanVar(master=self, value=False)
        fila = tk.Frame(self.formulario, bg=COLOR_BLANCO)
        fila.pack(fill="x", pady=(8, 2))
        tk.Checkbutton(
            fila,
            text="Acepto los",
            variable=self.acepta_terminos,
            font=("Arial", 10),
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            activebackground=COLOR_BLANCO,
            selectcolor=COLOR_PANEL_CLARO,
            anchor="w",
        ).pack(side="left")
        enlace = tk.Label(
            fila,
            text="términos y condiciones",
            font=("Arial", 10, "underline"),
            fg=COLOR_ROJO,
            bg=COLOR_BLANCO,
            cursor="hand2",
        )
        enlace.pack(side="left")
        enlace.bind("<Button-1>", lambda _evento: self._mostrar_terminos())

    def _mostrar_terminos(self):
        if self._pagina_terminos is not None:
            return
        self.exterior.pack_forget()
        pagina = tk.Frame(self._vista.contenido, bg=COLOR_FONDO, padx=24, pady=22)
        pagina.pack(fill="both", expand=True)
        self._pagina_terminos = pagina
        tarjeta = tk.Frame(
            pagina,
            bg=COLOR_BLANCO,
            padx=22,
            pady=18,
            highlightthickness=1,
            highlightbackground="#DCE8E1",
        )
        tarjeta.pack(fill="both", expand=True)
        tk.Button(
            tarjeta,
            text="←  Volver al registro",
            command=self._cerrar_terminos,
            font=FUENTE_BOTON,
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            activebackground=COLOR_ROJO_CLARO,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            cursor="hand2",
        ).pack(anchor="w", pady=(0, 12))
        tk.Label(
            tarjeta,
            text="Términos y condiciones",
            font=("Arial", 19, "bold"),
            fg=COLOR_TEXTO,
            bg=COLOR_BLANCO,
        ).pack(anchor="w", pady=(0, 10))
        texto = tk.Text(
            tarjeta,
            wrap="word",
            font=("Arial", 10),
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            relief="flat",
            padx=8,
            pady=8,
            spacing1=2,
            spacing3=5,
        )
        barra = tk.Scrollbar(tarjeta, orient="vertical", command=texto.yview)
        texto.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        texto.pack(fill="both", expand=True)
        texto.insert("1.0", TERMINOS_CONDICIONES)
        texto.configure(state="disabled")

    def _cerrar_terminos(self):
        if self._pagina_terminos is not None:
            self._pagina_terminos.destroy()
            self._pagina_terminos = None
        self.exterior.pack(fill="both", expand=True)
        self._centrar()

    def _requiere_aceptacion(self):
        if self.acepta_terminos is not None and self.acepta_terminos.get():
            return True
        self.error.configure(text="Debes aceptar los términos y condiciones para crear tu cuenta.")
        return False

    def _campo(self, etiqueta, clave, secreto=False):
        fila = tk.Frame(self.formulario, bg=COLOR_BLANCO)
        compacto = self.modo.startswith("registro")
        fila.pack(fill="x", pady=3 if compacto else 6)
        tk.Label(
            fila,
            text=etiqueta,
            font=FUENTE_BOTON,
            fg=COLOR_TEXTO,
            bg=COLOR_BLANCO,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))
        entrada = tk.Entry(
            fila,
            font=("Arial", 12),
            bg=COLOR_PANEL_CLARO,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            relief="flat",
            bd=0,
            show="*" if secreto else "",
        )
        entrada.pack(fill="x", ipady=6 if compacto else 8)
        if clave == "dni":
            validacion = self.register(validar_dni_en_edicion)
            entrada.configure(
                validate="key",
                validatecommand=(validacion, "%P"),
            )
        elif clave == "nombre":
            validacion = self.register(validar_nombre_en_edicion)
            entrada.configure(
                validate="key",
                validatecommand=(validacion, "%P"),
            )
        elif clave == "edad":
            validacion = self.register(
                lambda valor: valor == ""
                or (len(valor) <= 3 and valor.isascii() and valor.isdigit())
            )
            entrada.configure(
                validate="key",
                validatecommand=(validacion, "%P"),
            )
        self.campos[clave] = entrada
        return entrada

    def _boton(self, texto, comando, principal=False):
        boton = tk.Button(
            self.formulario,
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
            padx=16,
            pady=9,
        )
        boton.pack(fill="x", pady=(10, 3))
        return boton

    def _enlace(self, texto, comando):
        enlace = tk.Label(
            self.formulario,
            text=texto,
            font=("Arial", 10, "underline"),
            fg=COLOR_ROJO,
            bg=COLOR_BLANCO,
            cursor="hand2",
        )
        enlace.pack(pady=(10, 0))
        enlace.bind("<Button-1>", lambda _evento: comando())

    def _limpiar_formulario(self):
        self.campos.clear()
        self.error.configure(text="")
        for widget in self.formulario.winfo_children():
            widget.destroy()

    def _mostrar_modo(self, modo):
        """Muestra un formulario y reajusta el tamaño de la ventana."""
        self._construir_modo(modo)
        self._centrar()

    def _construir_modo(self, modo):
        if modo == "registro" and self.rol in {"profesional", "enfermeria"}:
            modo = "registro_personal_nuevo"
        self.modo = modo
        self._limpiar_formulario()

        if modo == "login":
            self.acepta_terminos = None
            self.titulo.configure(text="INICIAR SESIÓN")
            self._campo("Usuario", "usuario")
            password = self._campo("Contraseña", "password", secreto=True)
            self._boton("Ingresar", self._iniciar_sesion, principal=True)
            if self.rol == "paciente":
                self._enlace(
                    "¿Eres nuevo?"
                    "Crear cuenta",
                    lambda: self._mostrar_modo("registro_nuevo"),
                )
            elif self.rol != "administrativa":
                self._enlace(
                    "¿Eres nuevo?"
                    "Crear cuenta",
                    lambda: self._mostrar_modo("registro_personal_nuevo"),
                )
            password.bind("<Return>", lambda _evento: self._iniciar_sesion())
            self.campos["usuario"].focus_set()
            return

        if modo == "configurar_admin":
            self.acepta_terminos = None
            self.titulo.configure(text="CONFIGURAR ACCESO ADMINISTRATIVO")
            tk.Label(
                self.formulario,
                text=(
                    "Crea la primera cuenta administrativa. Esta opción se "
                    "desactivará después de configurarla."
                ),
                font=("Arial", 10),
                fg=COLOR_GRIS,
                bg=COLOR_BLANCO,
                wraplength=390,
                justify="center",
            ).pack(pady=(0, 7))
            self._campo("Usuario", "usuario")
            self._campo("Contraseña", "password", secreto=True)
            confirmacion = self._campo(
                "Confirmar contraseña", "confirmacion", secreto=True
            )
            self._agregar_consentimiento()
            self._boton(
                "Crear cuenta administrativa",
                self._crear_administrador,
                principal=True,
            )
            confirmacion.bind(
                "<Return>", lambda _evento: self._crear_administrador()
            )
            return

        if modo == "registro_nuevo":
            self.acepta_terminos = None
            self.titulo.configure(text="CREAR MI CUENTA DE PACIENTE")
            self._campo("Nombre completo", "nombre")
            self._campo("Edad", "edad")
            self._campo("DNI", "dni")
            self._campo("Nuevo usuario", "usuario")
            self._campo("Nueva contraseña", "password", secreto=True)
            confirmacion = self._campo(
                "Confirmar contraseña", "confirmacion", secreto=True
            )
            self._agregar_consentimiento()
            tk.Label(
                self.formulario,
                text=(
                    "Si tu DNI ya está registrado, se vinculará a ese registro. "
                    "Si aún no lo está, se creará tu registro y un código "
                    "automático. El DNI lleva 8 dígitos. La contraseña debe "
                    "tener al menos 8 caracteres y un número."
                ),
                font=("Arial", 9),
                fg=COLOR_GRIS,
                bg=COLOR_BLANCO,
                wraplength=390,
                justify="center",
            ).pack(pady=(3, 0))
            self._boton(
                "Crear mi cuenta", self._crear_paciente_nuevo, principal=True
            )
            self._enlace(
                "Volver al inicio de sesión",
                lambda: self._mostrar_modo("login"),
            )
            confirmacion.bind(
                "<Return>", lambda _evento: self._crear_paciente_nuevo()
            )
            self.campos["nombre"].focus_set()
            return

        if modo == "registro_personal_nuevo":
            self.acepta_terminos = None
            self.titulo.configure(text="CREAR CUENTA DE PERSONAL")
            self._campo("Nombres y apellidos", "nombre")
            self._campo("Edad", "edad")
            self._campo("DNI", "dni")
            if self.rol == "profesional":
                tk.Label(
                    self.formulario,
                    text="Especialidad",
                    font=FUENTE_BOTON,
                    fg=COLOR_TEXTO,
                    bg=COLOR_BLANCO,
                    anchor="w",
                ).pack(fill="x", pady=(5, 2))
                especialidades = (
                    "Medicina General",
                    "Obstetricia",
                    "Odontología",
                    "Psicología",
                    "Nutrición",
                    "Medicina Familiar",
                    "Urología",
                    "Pediatría",
                    "Neurología",
                )
                self.especialidad_var = tk.StringVar(value=especialidades[0])
                tk.OptionMenu(
                    self.formulario,
                    self.especialidad_var,
                    *especialidades,
                ).pack(fill="x", pady=(0, 4))
            else:
                tk.Label(
                    self.formulario,
                    font=FUENTE_BOTON,
                    fg=COLOR_TEXTO,
                    bg=COLOR_BLANCO,
                    anchor="w",
                ).pack(fill="x", pady=(5, 2))
            self._campo("Código de autorización", "codigo_medico", secreto=True)
            self._campo("Nuevo usuario", "usuario")
            self._campo("Nueva contraseña", "password", secreto=True)
            confirmacion = self._campo(
                "Confirmar contraseña", "confirmacion", secreto=True
            )
            self._agregar_consentimiento()
            tk.Label(
                self.formulario,
                text=(
                    "Si ya tienes un registro, "
                    "se vinculará a tu cuenta; si no, se creará tu registro "
                    "con un código automático. Se requiere el código médico "
                    "autorizado."
                ),
                font=("Arial", 9),
                fg=COLOR_GRIS,
                bg=COLOR_BLANCO,
                wraplength=390,
                justify="center",
            ).pack(pady=(3, 0))
            self._boton(
                "Registrar y crear cuenta",
                self._crear_personal_nuevo,
                principal=True,
            )
            self._enlace(
                "Volver al inicio de sesión",
                lambda: self._mostrar_modo("login"),
            )
            confirmacion.bind(
                "<Return>", lambda _evento: self._crear_personal_nuevo()
            )
            self.campos["nombre"].focus_set()
            return

        self.titulo.configure(text="CREAR CUENTA DE ACCESO")
        if self.rol == "paciente":
            self._campo("Código de paciente", "codigo")
        self._campo("DNI", "dni", secreto=True)
        if self.rol in {"profesional", "enfermeria"}:
            self._campo("Código de verificacion", "codigo_medico", secreto=True)
        self._campo("Nuevo usuario", "usuario")
        self._campo("Nueva contraseña", "password", secreto=True)
        confirmacion = self._campo(
            "Confirmar contraseña", "confirmacion", secreto=True
        )
        self.acepta_terminos = None
        self._agregar_consentimiento()
        tk.Label(
            self.formulario,
            text=(
                    "El DNI debe coincidir con el registro administrativo. "
                    "Tu código de personal se asigna automáticamente; ingresa "
                    "el código médico autorizado. Usa una contraseña de 8 "
                    "caracteres como mínimo y al menos un número."
                if self.rol in {"profesional", "enfermeria"}
                else "Usa al menos 8 caracteres y un número. El DNI debe "
                "coincidir con el registro existente."
            ),
            font=("Arial", 9),
            fg=COLOR_GRIS,
            bg=COLOR_BLANCO,
            wraplength=390,
            justify="center",
        ).pack(pady=(3, 0))
        self._boton("Verificar y crear cuenta", self._crear_cuenta, principal=True)
        if self.rol == "paciente":
            self._enlace(
                "Soy paciente nuevo (crear mi registro)",
                lambda: self._mostrar_modo("registro_nuevo"),
            )
        else:
            self._enlace(
                "Soy personal nuevo (crear mi registro)",
                lambda: self._mostrar_modo("registro_personal_nuevo"),
            )
        self._enlace("Volver al inicio de sesión", lambda: self._mostrar_modo("login"))
        confirmacion.bind("<Return>", lambda _evento: self._crear_cuenta())

    def _iniciar_sesion(self):
        sesion = self.servicio.autenticar(
            self.campos["usuario"].get(),
            self.campos["password"].get(),
            self.rol,
        )
        if sesion is None:
            self.error.configure(text="Usuario o contraseña incorrectos para este acceso.")
            self.campos["password"].delete(0, tk.END)
            self.campos["password"].focus_set()
            return
        self._completar(sesion)

    def _crear_administrador(self):
        if not self._requiere_aceptacion():
            return
        if self.campos["password"].get() != self.campos["confirmacion"].get():
            self.error.configure(text="Las contraseñas no coinciden.")
            return
        try:
            sesion = self.servicio.registrar_primer_administrador(
                self.campos["usuario"].get(),
                self.campos["password"].get(),
                acepta_terminos=True,
            )
        except ValueError as error:
            self.error.configure(text=str(error))
            return
        self._completar(sesion)

    def _crear_cuenta(self):
        if not self._requiere_aceptacion():
            return
        if self.campos["password"].get() != self.campos["confirmacion"].get():
            self.error.configure(text="Las contraseñas no coinciden.")
            return
        try:
            sesion = self.servicio.registrar(
                self.campos["usuario"].get(),
                self.campos["password"].get(),
                self.rol,
                self.campos.get("codigo").get()
                if "codigo" in self.campos
                else None,
                self.campos["dni"].get(),
                acepta_terminos=True,
                codigo_medico=(
                    self.campos["codigo_medico"].get()
                    if "codigo_medico" in self.campos
                    else None
                ),
            )
        except ValueError as error:
            self.error.configure(text=str(error))
            return
        self._completar(sesion)

    def _crear_paciente_nuevo(self):
        if not self._requiere_aceptacion():
            return
        if self.campos["password"].get() != self.campos["confirmacion"].get():
            self.error.configure(text="Las contraseñas no coinciden.")
            return
        try:
            sesion = self.servicio.registrar_paciente_nuevo(
                self.campos["nombre"].get(),
                self.campos["edad"].get(),
                self.campos["dni"].get(),
                self.campos["usuario"].get(),
                self.campos["password"].get(),
                acepta_terminos=True,
            )
        except ValueError as error:
            self.error.configure(text=str(error))
            return
        messagebox.showinfo(
            "Cuenta creada",
            f"Tu registro quedó vinculado con el código {sesion.codigo_referencia}.",
            parent=self,
        )
        self._completar(sesion)

    def _crear_personal_nuevo(self):
        if not self._requiere_aceptacion():
            return
        if self.campos["password"].get() != self.campos["confirmacion"].get():
            self.error.configure(text="Las contraseñas no coinciden.")
            return
        try:
            sesion = self.servicio.registrar_personal_nuevo(
                self.campos["nombre"].get(),
                self.campos["edad"].get(),
                self.campos["dni"].get(),
                self.campos["usuario"].get(),
                self.campos["password"].get(),
                self.rol,
                especialidad=(
                    self.especialidad_var.get()
                    if self.rol == "profesional"
                    else "Enfermería"
                ),
                acepta_terminos=True,
                codigo_medico=self.campos["codigo_medico"].get(),
            )
        except ValueError as error:
            self.error.configure(text=str(error))
            return
        messagebox.showinfo(
            "Cuenta creada",
            f"Tu registro quedó vinculado con el código {sesion.codigo_referencia}.",
            parent=self,
        )
        self._completar(sesion)

    def _mostrar_registro(self):
        self._mostrar_modo("registro")

    def _completar(self, sesion):
        callback = self.al_autenticar
        self.destroy()
        callback(sesion)

    def destroy(self):
        if not self._cerrado:
            self._cerrado = True
            try:
                self.servicio.cerrar()
            except Exception:
                pass
        try:
            super().destroy()
        except tk.TclError:
            pass

# SistemaRural-PE

## Sistema de gestión para un establecimiento de salud rural

SistemaRural-PE es un prototipo académico de escritorio desarrollado en
Python para gestionar pacientes, profesionales de salud, citas, atenciones
médicas y reportes básicos en un contexto de salud rural.

## 1. Funcionalidades

- Registro y consulta de pacientes.
- Registro y consulta de profesionales de salud.
- Búsqueda por código o DNI.
- Registro, consulta y actualización de citas.
- Registro y consulta de atenciones médicas.
- Historial clínico y de pacientes.
- Reportes y estadísticas básicas.
- Validación de datos y manejo de errores.
- Interfaz gráfica con navegación en una sola ventana.
- Maximización y pantalla completa mediante F11.
- Protección del DNI mediante PBKDF2-HMAC-SHA256 con sal aleatoria.
- Pruebas automatizadas con pytest.

## 2. Paradigmas aplicados

- **Programación Orientada a Objetos:** entidades, herencia, encapsulamiento y lógica de dominio.
- **Programación Funcional:** `map`, `filter`, `lambda` y procesamiento de colecciones.
- **Programación Orientada a Eventos:** botones, teclado y eventos de Tkinter.

## 3. Patrones de diseño

- **Singleton:** `GestorBaseDatos` administra las conexiones SQLite.
- **Factory:** `FabricaEntidades` centraliza la creación de entidades.

## 4. Arquitectura

```text
SistemaRural-PE/
├── interfaz/
│   ├── pantalla_inicio.py
│   ├── pantalla_paciente.py
│   ├── ventana_principal.py
│   └── estilos.py
├── modelos/
│   ├── persona.py
│   ├── paciente.py
│   ├── personal_salud.py
│   ├── cita.py
│   └── atencion_medica.py
├── servicios/
│   ├── sistema_salud.py
│   ├── repositorio.py
│   ├── gestor_bd.py
│   ├── fabrica.py
│   ├── contratos.py
│   ├── seguridad.py
│   ├── validaciones.py
│   └── reportes.py
├── pruebas/
│   ├── test_sistema.py
│   └── test_patrones.py
├── datos/
│   └── salud.db
├── imagenes/
├── main.py
├── requirements.txt
└── README.md
```

## 5. Instalación

Se recomienda usar un entorno virtual.

```bash
python -m venv venv
```

### Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 6. Ejecución

```bash
python main.py
```

La aplicación se abre en una sola ventana raíz. Las pantallas internas reemplazan
el contenido anterior y utilizan el botón **← Volver** para regresar al nivel
correspondiente.

## 7. Pruebas automatizadas

Ejecutar:

```bash
python -m pytest
```

La versión revisada del proyecto contiene **32 pruebas automatizadas aprobadas**.
Las pruebas cubren registro, búsquedas, validaciones, citas, atenciones,
protección de DNI, persistencia, migración de datos y patrones Singleton/Factory.

## 8. Tratamiento de datos personales

El prototipo utiliza datos ficticios. El DNI no se almacena en texto plano:
se protege mediante una huella derivada con PBKDF2-HMAC-SHA256 y una sal aleatoria.
Las pantallas muestran el DNI enmascarado y las búsquedas verifican la huella
sin recuperar el DNI original desde SQLite.

El sistema tiene finalidad académica y no debe considerarse una solución lista
para producción. Un despliegue real requeriría, entre otros controles, gestión
de usuarios y roles, auditoría, respaldos, políticas de conservación y medidas
adicionales de seguridad.

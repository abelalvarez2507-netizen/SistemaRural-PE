# SistemaRural-PE

## Sistema de gestión para un establecimiento de salud rural

SistemaRural-PE (SaluPro) es un prototipo académico de escritorio desarrollado
en Python para gestionar pacientes, profesionales de salud, citas, atenciones
médicas e informes básicos en un establecimiento de salud rural. Utiliza
Tkinter para la interfaz gráfica y SQLite para guardar la información.

## 1. Funcionalidades

- Registro y consulta de pacientes y profesionales de salud.
- Acceso a los módulos de paciente, profesional y administración.
- Búsqueda por código o DNI en los portales de paciente y profesional.
- Búsqueda rápida administrativa por código de paciente, DNI de paciente,
  código profesional o DNI profesional.
- Resultados de búsqueda con los datos del paciente, sus citas y atenciones,
  el profesional que lo atendió y el diagnóstico registrado. El DNI se muestra
  enmascarado.
- La búsqueda rápida acepta códigos de 2 a 10 caracteres y DNI de 8 dígitos.
  Los valores de ocho dígitos se comprueban tanto como código como DNI. Si no
  hay coincidencias, muestra un aviso en el panel sin abrir la pantalla de
  resultados.
- Pantalla interna de resultados con botón **← Volver**; el panel administrativo
  queda oculto mientras se consulta el resultado.
- Registro, consulta, cancelación y reprogramación de citas.
- Registro y actualización de atenciones médicas e historiales clínicos.
- Turnos de 30 minutos entre las 08:00 y las 17:00. El sistema rechaza citas
  pasadas y evita reservar el mismo horario para un profesional.
- Cancelación automática de citas pendientes o reprogramadas que ya vencieron.
- Reportes y estadísticas básicas del establecimiento.
- Desplazamiento vertical con la barra, la rueda del mouse y el touchpad en las
  pantallas largas, incluido el panel administrativo.
- Navegación dentro de una sola ventana raíz. **Alt+←** vuelve a la pantalla
  anterior, **Alt+Inicio** regresa al inicio y **F11** alterna la pantalla
  completa.
- Validación de datos y manejo de errores.
- Protección de DNI con PBKDF2-HMAC-SHA256 y una sal aleatoria.

## 2. Paradigmas aplicados

- **Programación orientada a objetos:** modelos de dominio, herencia,
  encapsulamiento y coordinación de operaciones del sistema.
- **Programación funcional:** uso de `map`, `filter`, `lambda` y procesamiento
  de colecciones.
- **Programación orientada a eventos:** botones, teclado y eventos de Tkinter.

## 3. Patrones de diseño

- **Singleton:** `GestorBaseDatos` administra las conexiones a SQLite.
- **Factory:** `FabricaEntidades` centraliza la creación de pacientes,
  profesionales, citas y atenciones.

## 4. Arquitectura

```text
SistemaRural-PE/
├── interfaz/
│   ├── pantalla_inicio.py
│   ├── pantalla_paciente.py
│   ├── pantalla_profesional.py
│   ├── pantalla_administrativa.py
│   ├── navegacion.py
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
│   └── logo_salupro.png
├── main.py
├── requirements.txt
└── README.md
```

## 5. Instalación

Se recomienda Python 3.10 o posterior y el uso de un entorno virtual.

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 6. Ejecución

```powershell
python main.py
```

La aplicación se abre en una sola ventana. Las pantallas internas reemplazan
temporalmente la vista anterior y utilizan **← Volver** para regresar al nivel
correspondiente.

## 7. Pruebas automatizadas

Ejecuta las pruebas con:

```powershell
python -m pytest
```

La versión revisada contiene **32 pruebas automatizadas aprobadas**. Cubren
registro y búsqueda, validaciones, citas, atenciones, protección de DNI,
persistencia, migración de datos y los patrones Singleton y Factory.

## 8. Tratamiento de datos personales

El DNI no se almacena en texto plano: se protege mediante PBKDF2-HMAC-SHA256
con una sal aleatoria. La aplicación verifica la huella protegida durante la
búsqueda y muestra el DNI enmascarado.

El sistema tiene finalidad académica y no debe considerarse una solución lista
para producción. Un despliegue real requeriría controles adicionales, como
gestión de usuarios y roles, auditoría, respaldos, políticas de conservación y
medidas de seguridad adicionales.

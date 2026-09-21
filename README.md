# SistemaRural-PE - V5

## Cambios principales
- Se mantienen las validaciones de V3.
- Se corrigen los duplicados mediante claves `PRIMARY KEY` en SQLite.
- Se controlan los errores de integridad de la base de datos.
- Se incorpora `SeguridadDatos`.
- El DNI deja de almacenarse directamente en SQLite y se protege con PBKDF2-HMAC-SHA256.
- Se agrega verificación del DNI sin guardar el valor original.
- Se agrega enmascaramiento del DNI para su visualización.

## Todavía no se incorporan
- Interfaz gráfica.
- Patrones Factory y Singleton.
- Suite completa de pruebas automatizadas.
- Reportes.

## Ejecución
```bash
python main.py
```
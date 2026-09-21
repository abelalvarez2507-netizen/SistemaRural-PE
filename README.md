# SistemaRural-PE - V4 

Esta versión representa una etapa intermedia reconstruida a partir del proyecto real.

## Cambio principal
Se incorpora por primera vez persistencia mediante SQLite.

## Errores intencionales de esta etapa
- Las tablas no tienen restricciones de unicidad.
- Se pueden insertar códigos repetidos.
- Todavía no existe una comprobación centralizada de duplicados.
- El manejo de errores de base de datos es básico.

Estos problemas forman parte de la evolución didáctica y se corrigen en **V4.1**.

> Esta es una reconstrucción técnica para mostrar una progresión del proyecto; no se presenta como una copia histórica exacta de un estado anterior.

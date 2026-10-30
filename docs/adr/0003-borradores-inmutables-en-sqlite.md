# ADR 0003: conservar borradores inmutables en SQLite

- Estado: aceptada.
- Fecha de registro: 2026-10-30.

## Contexto

Un asistente puede repetir la operación de guardado o perder la respuesta
después de ejecutarla. El borrador debe persistir al cerrar el proceso y
su recuperación debe respetar al empleado propietario. El proyecto no
implementa edición, envío, aprobación ni pago de informes.

## Decisión

Persistir una instantánea del informe en SQLite, con una restricción
`UNIQUE(employee_id, trip_id)`. Guardar vuelve a evaluar las reglas y conserva
el informe completo, la versión de política, el ID y la fecha de creación.

Una transacción `BEGIN IMMEDIATE` serializa la consulta y la inserción.
Si ya existe una instantánea idéntica, devuelve el borrador original.
Si difiere, devuelve un conflicto y conserva el anterior. Se compara todo
el informe serializado, no solo sus totales. Las lecturas se filtran por
empleado e identificador.

Cada operación abre una conexión, termina su transacción y cierra el recurso.
En Docker, la base vive en `/data`, sobre un volumen persistente.

## Alternativas consideradas

- Memoria del proceso: más simple, pero pierde los borradores al terminar.
- Un servidor de base de datos externo: puede ser adecuado para otras
  necesidades de operación, pero añade instalación y administración para
  una aplicación local que solo necesita un archivo persistente.
- Sobrescribir el borrador: permitiría cambios, pero necesita un flujo de
  edición y control de versiones que la aplicación todavía no ofrece.

## Consecuencias

Los reintentos con los mismos datos conservan ID, fecha y contenido. Las
llamadas concurrentes no crean varios borradores para el mismo empleado y
viaje. Un cambio de datos o política requiere revisar el conflicto; para
ensayos independientes se usa otra base.

Las pruebas comprueban concurrencia, comparación del contenido completo,
acceso por propietario y recuperación desde un proceso nuevo. La persistencia
en Docker depende de conservar el volumen, no del contenedor.

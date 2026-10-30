# ADR 0001: separar el dominio de los adaptadores

- Estado: aceptada.
- Fecha de registro: 2026-10-30.

## Contexto

Las reglas de gastos deben producir los mismos importes al usarlas desde
un asistente, una demo programada o una prueba. El protocolo MCP, el formato
JSON de entrada y SQLite pueden cambiar sin alterar esas reglas. Concentrar
esas responsabilidades en las funciones MCP haría depender el cálculo del
transporte y del almacenamiento.

## Decisión

Aplicar Clean Architecture con un dominio encapsulado. `ExpensePolicy`
evalúa viajes y justificantes mediante objetos valor inmutables y dinero
decimal. `ExpenseService` comprueba el acceso, solicita datos, evalúa y
coordina la persistencia; no importa el SDK MCP ni Pydantic.

Los puertos `TravelData` y `DraftStore` pertenecen a la aplicación y se
expresan como `Protocol`. Sus contratos de salida usan `TypedDict`.
Los adaptadores implementan la lectura de JSON, SQLite y MCP. Pydantic
valida los datos externos en esos adaptadores; las anotaciones estáticas
no sustituyen esa validación. `bootstrap.py` compone las dependencias.

Cada clase ocupa un módulo propio, también contratos, excepciones y pruebas.
Los módulos de funciones se mantienen separados de los que declaran clases.
El perfil completo de organización y estilo se documenta en el
[README](../../README.md#estilo-y-calidad).

## Alternativas consideradas

- Ejecutar cálculo, SQL y protocolo en los manejadores MCP: menos separación
  inicial, pero mezcla reglas y operaciones externas y dificulta probarlas.
- Usar los modelos del SDK o Pydantic en todo el núcleo: reduce conversiones,
  pero acopla los casos de uso a contratos de una biblioteca externa.

## Consecuencias

Hay conversiones explícitas entre registros externos, objetos de dominio y
respuestas. Cada frontera tiene pruebas y las dependencias se comprueban
mediante AST desde precommit y CI. El dominio importa solo biblioteca
estándar; los adaptadores dependen hacia el interior. No se añaden capas ni
entidades sin una responsabilidad concreta.

Importar módulos no abre bases de datos ni transportes. Las conexiones y
subprocesos se crean en entradas explícitas y tienen un cierre definido.

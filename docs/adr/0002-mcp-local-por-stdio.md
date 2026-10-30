# ADR 0002: ofrecer las operaciones mediante MCP local por stdio

- Estado: aceptada.
- Fecha de registro: 2026-10-30.

## Contexto

Queremos que distintos asistentes compatibles descubran y soliciten las
operaciones de gastos. El caso actual utiliza datos locales de ejemplo y
no requiere atender usuarios remotos ni mantener un servicio HTTP.

## Decisión

Utilizar el SDK oficial de Python para ofrecer herramientas, un recurso de
política y un prompt mediante MCP por stdio. El cliente inicia el servidor
como subproceso y gestiona su transporte. Docker conserva esa misma forma
de comunicación, sin publicar puertos.

El servidor ejecuta las reglas deterministas de gastos. No incluye un LLM:
el asistente presenta las herramientas a su modelo y solicita las llamadas
propuestas. Las demos utilizan una secuencia programada sobre MCP real.

La identidad se configura al arrancar con `--employee` y no se admite como
argumento de herramienta. Las consultas se filtran por empleado.
`--read-only` impide registrar la herramienta de creación de borradores.
Los prompts y las anotaciones de herramientas no sustituyen ese control.

## Alternativas consideradas

- Una API convencional: suficiente para un servicio que conoce de antemano
  la operación, pero requiere otra integración para anunciar capacidades
  a los asistentes MCP que queremos utilizar.
- MCP remoto sobre HTTP: permitiría clientes de otros equipos, pero exige
  resolver identidad autenticada, autorización y operación de un servicio
  remoto que no forman parte del alcance actual.

## Consecuencias

No se instala un servicio permanente ni hay una URL para abrir en el
navegador. El cliente necesita acceso al ejecutable y a los archivos del
equipo. La configuración del proceso es de confianza; `--employee` no
autentica a una persona. Este diseño no proporciona acceso multiusuario
remoto y no debe exponerse como tal sin una decisión e implementación nuevas.

Las pruebas verifican descubrimiento, entradas, resultados, errores de
negocio, recurso, prompt, perfil de lectura y transporte entre procesos.
